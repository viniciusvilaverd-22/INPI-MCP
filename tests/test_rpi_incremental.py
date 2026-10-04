from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.rpi_incremental as incremental
from app.db import Base
from app.models import RPIIngestionRun, RPIIngestionState
from app.rpi_source import RPIUnavailableError


def _session_factory():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def _artifact(number: int):
    return SimpleNamespace(
        rpi_number=number,
        source_url=f"https://example.test/RM{number}.zip",
        zip_sha256=f"{number:064d}"[-64:],
        xml_sha256=f"{number + 1:064d}"[-64:],
        xml_path=f"/tmp/RM{number}.xml",
        to_dict=lambda: {
            "rpi_number": number,
            "source_url": f"https://example.test/RM{number}.zip",
        },
    )


def test_range_advances_last_ingested_only_after_success(monkeypatch):
    S = _session_factory()
    monkeypatch.setattr(incremental, "prepare_rpi", lambda number, *a, **k: _artifact(number))
    monkeypatch.setattr(
        incremental,
        "ingest_xml",
        lambda session, path: {
            "rpi_number": int(path.split("RM")[-1].split(".xml")[0]),
            "process_count": 10,
            "event_count": 11,
            "parser_version": "test-parser",
        },
    )

    with S() as session:
        result = incremental.ingest_rpi_range(session, 2908, 2909)
        state = session.get(RPIIngestionState, 1)
        runs = list(session.scalars(select(RPIIngestionRun).order_by(RPIIngestionRun.rpi_number)))

        assert result["last_ingested_rpi"] == 2909
        assert state.last_ingested_rpi == 2909
        assert state.last_checked_rpi == 2909
        assert [run.status for run in runs] == ["completed", "completed"]


def test_unavailable_rpi_does_not_advance_last_ingested(monkeypatch):
    S = _session_factory()

    def prepare(number, *args, **kwargs):
        if number == 2909:
            raise RPIUnavailableError(number)
        return _artifact(number)

    monkeypatch.setattr(incremental, "prepare_rpi", prepare)
    monkeypatch.setattr(
        incremental,
        "ingest_xml",
        lambda session, path: {
            "rpi_number": 2908,
            "process_count": 10,
            "event_count": 11,
            "parser_version": "test-parser",
        },
    )

    with S() as session:
        result = incremental.ingest_rpi_range(session, 2908, 2910)
        state = session.get(RPIIngestionState, 1)
        unavailable = session.scalar(
            select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == 2909)
        )

        assert result["last_ingested_rpi"] == 2908
        assert result["last_checked_rpi"] == 2909
        assert state.last_ingested_rpi == 2908
        assert unavailable.status == "unavailable"
        assert all(item["rpi_number"] != 2910 for item in result["results"])


def test_ingest_next_resumes_from_last_completed(monkeypatch):
    S = _session_factory()
    seen = []

    def prepare(number, *args, **kwargs):
        seen.append(number)
        return _artifact(number)

    monkeypatch.setattr(incremental, "prepare_rpi", prepare)
    monkeypatch.setattr(
        incremental,
        "ingest_xml",
        lambda session, path: {
            "rpi_number": int(path.split("RM")[-1].split(".xml")[0]),
            "process_count": 1,
            "event_count": 1,
            "parser_version": "test-parser",
        },
    )

    with S() as session:
        session.add(RPIIngestionState(id=1, last_ingested_rpi=2908, last_checked_rpi=2908))
        session.commit()
        result = incremental.ingest_next_rpis(session, max_count=2)

        assert seen == [2909, 2910]
        assert result["last_ingested_rpi"] == 2910


def test_completed_run_is_skipped_without_network(monkeypatch):
    S = _session_factory()

    def should_not_run(*args, **kwargs):
        raise AssertionError("network should not be called for a completed RPI")

    monkeypatch.setattr(incremental, "prepare_rpi", should_not_run)

    with S() as session:
        session.add(RPIIngestionState(id=1, last_ingested_rpi=2908, last_checked_rpi=2908))
        session.add(
            RPIIngestionRun(
                rpi_number=2908,
                status="completed",
                process_count=39858,
                event_count=40201,
                xml_sha256="a" * 64,
            )
        )
        session.commit()

        result = incremental.ingest_one_rpi(session, 2908)
        assert result["status"] == "skipped_completed"
        assert result["process_count"] == 39858


def test_failed_ingestion_does_not_advance_last_ingested(monkeypatch):
    S = _session_factory()
    monkeypatch.setattr(incremental, "prepare_rpi", lambda number, *a, **k: _artifact(number))

    def fail(session, path):
        raise RuntimeError("parser failure")

    monkeypatch.setattr(incremental, "ingest_xml", fail)

    with S() as session:
        session.add(RPIIngestionState(id=1, last_ingested_rpi=2908, last_checked_rpi=2908))
        session.commit()

        with pytest.raises(RuntimeError, match="parser failure"):
            incremental.ingest_one_rpi(session, 2909)

        state = session.get(RPIIngestionState, 1)
        run = session.scalar(
            select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == 2909)
        )
        assert state.last_ingested_rpi == 2908
        assert run.status == "failed"
