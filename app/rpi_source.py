from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

OFFICIAL_RPI_BASE_URL = "https://revistas.inpi.gov.br/txt"
USER_AGENT = "INPI-MCP-Community/0.2 (+https://github.com/viniciusvilaverd-22/INPI-MCP)"


@dataclass(frozen=True)
class RPIArtifact:
    rpi_number: int
    source_url: str
    zip_path: str
    xml_path: str
    zip_sha256: str
    xml_sha256: str
    zip_bytes: int
    xml_bytes: int
    reused_zip: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _validate_number(rpi_number: int) -> int:
    value = int(rpi_number)
    if value <= 0 or value > 99999:
        raise ValueError("numero de RPI invalido")
    return value


def build_rpi_url(rpi_number: int) -> str:
    number = _validate_number(rpi_number)
    return f"{OFFICIAL_RPI_BASE_URL}/RM{number}.zip"


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_rpi_xml(path: str | Path) -> dict:
    xml_path = Path(path)
    for _event, element in ET.iterparse(xml_path, events=("start",)):
        tag = element.tag.rsplit("}", 1)[-1]
        if tag != "revista":
            raise ValueError(f"raiz XML inesperada: {tag}")
        number = element.attrib.get("numero")
        return {
            "rpi_number": int(number) if number and number.isdigit() else None,
            "rpi_date": element.attrib.get("data"),
        }
    raise ValueError("XML vazio")


def extract_rpi_zip(zip_path: str | Path, rpi_number: int, output_dir: str | Path) -> Path:
    number = _validate_number(rpi_number)
    source = Path(zip_path)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"RM{number}.xml"

    if not zipfile.is_zipfile(source):
        raise ValueError(f"arquivo nao e ZIP valido: {source}")

    with zipfile.ZipFile(source) as archive:
        xml_members = [
            info for info in archive.infolist()
            if not info.is_dir() and info.filename.lower().endswith(".xml")
        ]
        preferred = [
            info for info in xml_members
            if Path(info.filename).name.lower() == f"rm{number}.xml".lower()
        ]
        if preferred:
            member = preferred[0]
        elif len(xml_members) == 1:
            member = xml_members[0]
        else:
            names = ", ".join(Path(item.filename).name for item in xml_members[:10])
            raise ValueError(f"XML da RPI {number} nao identificado univocamente: {names}")

        temp_target = target.with_suffix(".xml.download")
        with archive.open(member, "r") as src, temp_target.open("wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        os.replace(temp_target, target)

    header = inspect_rpi_xml(target)
    if header["rpi_number"] != number:
        target.unlink(missing_ok=True)
        raise ValueError(
            f"RPI do XML ({header['rpi_number']}) difere da solicitada ({number})"
        )
    return target


def prepare_rpi(
    rpi_number: int,
    raw_root: str | Path = "raw/rpi",
    *,
    timeout: int = 300,
    force_download: bool = False,
) -> RPIArtifact:
    number = _validate_number(rpi_number)
    target_dir = Path(raw_root) / str(number)
    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir / f"RM{number}.zip"
    source_url = build_rpi_url(number)

    reused_zip = zip_path.exists() and not force_download
    if not reused_zip:
        temp_zip = zip_path.with_suffix(".zip.download")
        request = urllib.request.Request(
            source_url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/zip,*/*"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response, temp_zip.open("wb") as out:
                shutil.copyfileobj(response, out, length=1024 * 1024)
            if temp_zip.stat().st_size < 100:
                raise ValueError("download da RPI produziu arquivo pequeno demais")
            os.replace(temp_zip, zip_path)
        finally:
            temp_zip.unlink(missing_ok=True)

    xml_path = extract_rpi_zip(zip_path, number, target_dir)
    artifact = RPIArtifact(
        rpi_number=number,
        source_url=source_url,
        zip_path=str(zip_path),
        xml_path=str(xml_path),
        zip_sha256=sha256_file(zip_path),
        xml_sha256=sha256_file(xml_path),
        zip_bytes=zip_path.stat().st_size,
        xml_bytes=xml_path.stat().st_size,
        reused_zip=reused_zip,
    )

    metadata = {
        **artifact.to_dict(),
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_source": True,
    }
    (target_dir / "source.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return artifact
