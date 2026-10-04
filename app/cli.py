from __future__ import annotations

import argparse
import json
from pathlib import Path

from .db import SessionLocal, init_db
from .rpi_incremental import (
    get_ingestion_status,
    ingest_next_rpis,
    ingest_one_rpi,
    ingest_rpi_range,
)
from .rpi_source import discover_rpis, inspect_rpi_xml, prepare_rpi


def _dump(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _download(args: argparse.Namespace) -> int:
    artifact = prepare_rpi(
        args.rpi_number,
        args.raw_root,
        timeout=args.timeout,
        force_download=args.force,
    )
    _dump({"status": "ok", "artifact": artifact.to_dict()})
    return 0


def _inspect(args: argparse.Namespace) -> int:
    path = Path(args.xml)
    payload = inspect_rpi_xml(path)
    payload.update({
        "xml_path": str(path),
        "xml_bytes": path.stat().st_size,
    })
    _dump(payload)
    return 0


def _ingest(args: argparse.Namespace) -> int:
    init_db()
    with SessionLocal() as session:
        result = ingest_one_rpi(
            session,
            args.rpi_number,
            raw_root=args.raw_root,
            timeout=args.timeout,
            force_download=args.force,
        )
    _dump({"status": "ok", "result": result})
    return 0


def _ingest_range(args: argparse.Namespace) -> int:
    init_db()
    with SessionLocal() as session:
        result = ingest_rpi_range(
            session,
            args.start,
            args.end,
            raw_root=args.raw_root,
            timeout=args.timeout,
            force_download=args.force,
        )
    _dump(result)
    return 0


def _ingest_next(args: argparse.Namespace) -> int:
    init_db()
    with SessionLocal() as session:
        result = ingest_next_rpis(
            session,
            max_count=args.max_count,
            raw_root=args.raw_root,
            timeout=args.timeout,
            force_download=args.force,
        )
    _dump(result)
    return 0


def _status(args: argparse.Namespace) -> int:
    init_db()
    with SessionLocal() as session:
        result = get_ingestion_status(session, recent_limit=args.limit)
    _dump({"status": "ok", **result})
    return 0


def _discover(args: argparse.Namespace) -> int:
    probes = discover_rpis(args.after, max_scan=args.max_scan, timeout=args.timeout)
    available = [item.rpi_number for item in probes if item.available]
    first_missing = next((item.rpi_number for item in probes if not item.available), None)
    _dump({
        "status": "ok",
        "after": args.after,
        "available_rpis": available,
        "latest_available_rpi": max(available) if available else args.after,
        "first_missing_rpi": first_missing,
        "probes": [item.to_dict() for item in probes],
    })
    return 0


def _add_source_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--raw-root", default="raw/rpi")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--force", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inpi-mcp",
        description="Ferramentas comunitarias do INPI MCP para RPI oficial.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser("download-rpi", help="baixa e valida uma RPI oficial")
    download.add_argument("rpi_number", type=int)
    _add_source_options(download)
    download.set_defaults(handler=_download)

    inspect = sub.add_parser("inspect-rpi", help="inspeciona o cabecalho de um XML de RPI")
    inspect.add_argument("xml")
    inspect.set_defaults(handler=_inspect)

    ingest = sub.add_parser("ingest-rpi", help="baixa/valida e ingere uma RPI oficial")
    ingest.add_argument("rpi_number", type=int)
    _add_source_options(ingest)
    ingest.set_defaults(handler=_ingest)

    ingest_range = sub.add_parser(
        "ingest-range",
        help="ingere uma sequencia inclusiva de RPIs e para na primeira ainda indisponivel",
    )
    ingest_range.add_argument("start", type=int)
    ingest_range.add_argument("end", type=int)
    _add_source_options(ingest_range)
    ingest_range.set_defaults(handler=_ingest_range)

    ingest_next = sub.add_parser(
        "ingest-next",
        help="retoma automaticamente a partir de last_ingested_rpi + 1",
    )
    ingest_next.add_argument("--max-count", type=int, default=1)
    _add_source_options(ingest_next)
    ingest_next.set_defaults(handler=_ingest_next)

    status = sub.add_parser(
        "rpi-status",
        help="mostra last_ingested_rpi, last_checked_rpi e execucoes recentes",
    )
    status.add_argument("--limit", type=int, default=10)
    status.set_defaults(handler=_status)

    discover = sub.add_parser(
        "discover-rpi",
        help="consulta de forma leve quais RPIs sequenciais ja existem na fonte oficial",
    )
    discover.add_argument("--after", type=int, required=True)
    discover.add_argument("--max-scan", type=int, default=4)
    discover.add_argument("--timeout", type=int, default=30)
    discover.set_defaults(handler=_discover)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
