from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .ingest import ingest_xml
from .models import RPIIngestionRun, RPIIngestionState
from .rpi_source import RPIUnavailableError, prepare_rpi

STATE_ID = 1

# ASCII-ish stable key for "INPI MCP" kept below PostgreSQL signed BIGINT limit.
INGESTION_ADVISORY_LOCK_KEY = 0x494E50494D4350


class RPIIngestionBusyError(RuntimeError):
    pass


def _utcnow():
    return datetime.now(timezone.utc)


@contextmanager
def rpi_ingestion_lock(session: Session):
    """Serialize RPI mutation flows on PostgreSQL.

    SQLite and other non-PostgreSQL engines are intentionally a no-op so
    unit tests and lightweight local development remain portable.
    """
    bind = session.get_bind()
    if bind.dialect.name != "postgresql":
        yield
        return

    engine = getattr(bind, "engine", bind)
    connection = engine.connect()
    acquired = False
    try:
        acquired = bool(
            connection.scalar(
                text("SELECT pg_try_advisory_lock(:lock_key)"),
                {"lock_key": INGESTION_ADVISORY_LOCK_KEY},
            )
        )
        if not acquired:
            raise RPIIngestionBusyError(
                "outra ingestao de RPI ja esta em execucao neste banco"
            )
        yield
    finally:
        if acquired:
            connection.execute(
                text("SELECT pg_advisory_unlock(:lock_key)"),
                {"lock_key": INGESTION_ADVISORY_LOCK_KEY},
            )
            connection.commit()
        connection.close()


def get_ingestion_state(
    session: Session,
    *,
    create: bool = True,
) -> RPIIngestionState | None:
    state = session.get(RPIIngestionState, STATE_ID)
    if state is None and create:
        state = RPIIngestionState(id=STATE_ID)
        session.add(state)
        session.flush()
    return state


def _max_value(current: int | None, candidate: int) -> int:
    return candidate if current is None else max(current, candidate)


def _duration_seconds(run: RPIIngestionRun | None) -> float | None:
    if not run or not run.started_at or not run.finished_at:
        return None
    started = run.started_at
    finished = run.finished_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    if finished.tzinfo is None:
        finished = finished.replace(tzinfo=timezone.utc)
    return round(max(0.0, (finished - started).total_seconds()), 3)


def get_ingestion_status(session: Session, *, recent_limit: int = 10) -> dict:
    state = get_ingestion_state(session, create=False)
    runs = list(
        session.scalars(
            select(RPIIngestionRun)
            .order_by(RPIIngestionRun.rpi_number.desc())
            .limit(recent_limit)
        )
    )
    status_counts = {
        status: int(count)
        for status, count in session.execute(
            select(RPIIngestionRun.status, func.count())
            .group_by(RPIIngestionRun.status)
        ).all()
    }
    last_run = session.scalar(
        select(RPIIngestionRun)
        .order_by(RPIIngestionRun.started_at.desc())
        .limit(1)
    )
    last_failure = session.scalar(
        select(RPIIngestionRun)
        .where(RPIIngestionRun.status == "failed")
        .order_by(RPIIngestionRun.finished_at.desc())
        .limit(1)
    )

    last_ingested = state.last_ingested_rpi if state else None
    last_checked = state.last_checked_rpi if state else None
    cursor_gap = None
    if last_ingested is not None and last_checked is not None:
        cursor_gap = max(0, last_checked - last_ingested)

    return {
        "last_ingested_rpi": last_ingested,
        "last_checked_rpi": last_checked,
        "operational": {
            "state": "running" if status_counts.get("running", 0) else "idle",
            "cursor_gap": cursor_gap,
            "status_counts": status_counts,
            "last_run_rpi": last_run.rpi_number if last_run else None,
            "last_run_status": last_run.status if last_run else None,
            "last_run_duration_seconds": _duration_seconds(last_run),
            "last_failure": (
                {
                    "rpi_number": last_failure.rpi_number,
                    "error": last_failure.error,
                    "finished_at": (
                        last_failure.finished_at.isoformat()
                        if last_failure.finished_at
                        else None
                    ),
                }
                if last_failure
                else None
            ),
        },
        "recent_runs": [
            {
                "rpi_number": run.rpi_number,
                "status": run.status,
                "process_count": run.process_count,
                "event_count": run.event_count,
                "xml_sha256": run.xml_sha256,
                "parser_version": run.parser_version,
                "duration_seconds": _duration_seconds(run),
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                "error": run.error,
            }
            for run in runs
        ],
    }


def _ingest_one_rpi_unlocked(
    session: Session,
    rpi_number: int,
    *,
    raw_root: str = "raw/rpi",
    timeout: int = 300,
    force_download: bool = False,
) -> dict:
    number = int(rpi_number)
    state = get_ingestion_state(session)

    run = session.scalar(
        select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == number)
    )
    if run is not None and run.status == "completed" and not force_download:
        state.last_ingested_rpi = _max_value(state.last_ingested_rpi, number)
        state.last_checked_rpi = _max_value(state.last_checked_rpi, number)
        session.commit()
        return {
            "rpi_number": number,
            "status": "skipped_completed",
            "process_count": run.process_count,
            "event_count": run.event_count,
            "xml_sha256": run.xml_sha256,
        }

    if run is None:
        run = RPIIngestionRun(rpi_number=number, status="running")
        session.add(run)
    else:
        run.status = "running"
        run.error = None
        run.finished_at = None
        run.started_at = _utcnow()

    state.last_checked_rpi = _max_value(state.last_checked_rpi, number)
    session.commit()

    try:
        artifact = prepare_rpi(
            number,
            raw_root,
            timeout=timeout,
            force_download=force_download,
        )
    except RPIUnavailableError as exc:
        run = session.scalar(
            select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == number)
        )
        state = get_ingestion_state(session)
        run.status = "unavailable"
        run.error = str(exc)
        run.finished_at = _utcnow()
        state.last_checked_rpi = _max_value(state.last_checked_rpi, number)
        session.commit()
        return {
            "rpi_number": number,
            "status": "unavailable",
            "error": str(exc),
        }
    except Exception as exc:
        session.rollback()
        run = session.scalar(
            select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == number)
        )
        state = get_ingestion_state(session)
        run.status = "failed"
        run.error = f"{type(exc).__name__}: {exc}"
        run.finished_at = _utcnow()
        state.last_checked_rpi = _max_value(state.last_checked_rpi, number)
        session.commit()
        raise

    run = session.scalar(
        select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == number)
    )
    run.source_url = artifact.source_url
    run.zip_sha256 = artifact.zip_sha256
    run.xml_sha256 = artifact.xml_sha256
    session.commit()

    try:
        result = ingest_xml(session, artifact.xml_path)
        if result.get("rpi_number") != number:
            raise ValueError(
                f"RPI ingerida ({result.get('rpi_number')}) difere da solicitada ({number})"
            )
    except Exception as exc:
        session.rollback()
        run = session.scalar(
            select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == number)
        )
        run.status = "failed"
        run.error = f"{type(exc).__name__}: {exc}"
        run.finished_at = _utcnow()
        session.commit()
        raise

    run = session.scalar(
        select(RPIIngestionRun).where(RPIIngestionRun.rpi_number == number)
    )
    state = get_ingestion_state(session)
    run.status = "completed"
    run.process_count = result.get("process_count")
    run.event_count = result.get("event_count")
    run.parser_version = result.get("parser_version")
    run.error = None
    run.finished_at = _utcnow()
    state.last_ingested_rpi = _max_value(state.last_ingested_rpi, number)
    state.last_checked_rpi = _max_value(state.last_checked_rpi, number)
    session.commit()

    return {
        "rpi_number": number,
        "status": "completed",
        "artifact": artifact.to_dict(),
        "ingestion": result,
    }


def ingest_one_rpi(
    session: Session,
    rpi_number: int,
    *,
    raw_root: str = "raw/rpi",
    timeout: int = 300,
    force_download: bool = False,
) -> dict:
    with rpi_ingestion_lock(session):
        return _ingest_one_rpi_unlocked(
            session,
            rpi_number,
            raw_root=raw_root,
            timeout=timeout,
            force_download=force_download,
        )


def _ingest_rpi_range_unlocked(
    session: Session,
    start: int,
    end: int,
    *,
    raw_root: str = "raw/rpi",
    timeout: int = 300,
    force_download: bool = False,
) -> dict:
    start_number = int(start)
    end_number = int(end)
    if start_number <= 0 or end_number < start_number:
        raise ValueError("intervalo de RPI invalido")
    if end_number - start_number > 100:
        raise ValueError("intervalo limitado a 101 RPIs por execucao")

    results = []
    for number in range(start_number, end_number + 1):
        item = _ingest_one_rpi_unlocked(
            session,
            number,
            raw_root=raw_root,
            timeout=timeout,
            force_download=force_download,
        )
        results.append(item)
        if item["status"] == "unavailable":
            break

    state = get_ingestion_state(session, create=False)
    return {
        "status": "ok",
        "requested_start": start_number,
        "requested_end": end_number,
        "last_ingested_rpi": state.last_ingested_rpi if state else None,
        "last_checked_rpi": state.last_checked_rpi if state else None,
        "results": results,
    }


def ingest_rpi_range(
    session: Session,
    start: int,
    end: int,
    *,
    raw_root: str = "raw/rpi",
    timeout: int = 300,
    force_download: bool = False,
) -> dict:
    with rpi_ingestion_lock(session):
        return _ingest_rpi_range_unlocked(
            session,
            start,
            end,
            raw_root=raw_root,
            timeout=timeout,
            force_download=force_download,
        )


def ingest_next_rpis(
    session: Session,
    *,
    max_count: int = 1,
    raw_root: str = "raw/rpi",
    timeout: int = 300,
    force_download: bool = False,
) -> dict:
    if max_count <= 0 or max_count > 20:
        raise ValueError("max_count deve estar entre 1 e 20")

    with rpi_ingestion_lock(session):
        session.expire_all()
        state = get_ingestion_state(session, create=False)
        if state is None or state.last_ingested_rpi is None:
            raise ValueError(
                "last_ingested_rpi ainda nao definido; use ingest-range para estabelecer o baseline"
            )
        start = state.last_ingested_rpi + 1
        end = start + max_count - 1
        return _ingest_rpi_range_unlocked(
            session,
            start,
            end,
            raw_root=raw_root,
            timeout=timeout,
            force_download=force_download,
        )
