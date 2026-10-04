from __future__ import annotations

import argparse
import json
from pathlib import Path

from .db import SessionLocal, init_db
from .ingest import ingest_xml
from .rpi_source import inspect_rpi_xml, prepare_rpi


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
    artifact = prepare_rpi(
        args.rpi_number,
        args.raw_root,
        timeout=args.timeout,
        force_download=args.force,
    )
    init_db()
    with SessionLocal() as session:
        result = ingest_xml(session, artifact.xml_path)
    if result.get("rpi_number") != args.rpi_number:
        raise SystemExit(
            f"RPI ingerida ({result.get('rpi_number')}) difere da solicitada ({args.rpi_number})"
        )
    _dump({
        "status": "ok",
        "artifact": artifact.to_dict(),
        "ingestion": result,
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inpi-mcp",
        description="Ferramentas comunitarias do INPI MCP para RPI oficial.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser("download-rpi", help="baixa e valida uma RPI oficial")
    download.add_argument("rpi_number", type=int)
    download.add_argument("--raw-root", default="raw/rpi")
    download.add_argument("--timeout", type=int, default=300)
    download.add_argument("--force", action="store_true")
    download.set_defaults(handler=_download)

    inspect = sub.add_parser("inspect-rpi", help="inspeciona o cabecalho de um XML de RPI")
    inspect.add_argument("xml")
    inspect.set_defaults(handler=_inspect)

    ingest = sub.add_parser("ingest-rpi", help="baixa/valida e ingere uma RPI oficial")
    ingest.add_argument("rpi_number", type=int)
    ingest.add_argument("--raw-root", default="raw/rpi")
    ingest.add_argument("--timeout", type=int, default=300)
    ingest.add_argument("--force", action="store_true")
    ingest.set_defaults(handler=_ingest)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
