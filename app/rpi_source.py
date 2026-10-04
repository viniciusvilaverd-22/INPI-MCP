from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

OFFICIAL_RPI_BASE_URL = "https://revistas.inpi.gov.br/txt"
USER_AGENT = "INPI-MCP-Community/0.3 (+https://github.com/viniciusvilaverd-22/INPI-MCP)"


class RPIUnavailableError(RuntimeError):
    def __init__(self, rpi_number: int):
        super().__init__(f"RPI {rpi_number} ainda nao disponivel na fonte oficial")
        self.rpi_number = rpi_number


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


@dataclass(frozen=True)
class RPIProbe:
    rpi_number: int
    source_url: str
    available: bool
    status_code: int | None
    content_length: int | None
    last_modified: str | None

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


def _probe_request(url: str, method: str, timeout: int):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/zip,*/*"}
    if method == "GET":
        headers["Range"] = "bytes=0-0"
    request = urllib.request.Request(url, headers=headers, method=method)
    return urllib.request.urlopen(request, timeout=timeout)


def probe_rpi(rpi_number: int, *, timeout: int = 30) -> RPIProbe:
    number = _validate_number(rpi_number)
    source_url = build_rpi_url(number)
    response = None
    try:
        try:
            response = _probe_request(source_url, "HEAD", timeout)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return RPIProbe(number, source_url, False, 404, None, None)
            if exc.code not in (405, 501):
                raise
            response = _probe_request(source_url, "GET", timeout)

        status = getattr(response, "status", None) or response.getcode()
        headers = response.headers
        length = headers.get("Content-Length")
        return RPIProbe(
            rpi_number=number,
            source_url=source_url,
            available=200 <= int(status) < 400,
            status_code=int(status),
            content_length=int(length) if length and length.isdigit() else None,
            last_modified=headers.get("Last-Modified"),
        )
    finally:
        if response is not None:
            response.close()


def discover_rpis(after: int, *, max_scan: int = 4, timeout: int = 30) -> list[RPIProbe]:
    start = _validate_number(after)
    if max_scan <= 0 or max_scan > 100:
        raise ValueError("max_scan deve estar entre 1 e 100")
    probes = []
    for number in range(start + 1, start + max_scan + 1):
        probe = probe_rpi(number, timeout=timeout)
        probes.append(probe)
        if not probe.available:
            break
    return probes


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
            try:
                response = urllib.request.urlopen(request, timeout=timeout)
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    raise RPIUnavailableError(number) from exc
                raise
            with response, temp_zip.open("wb") as out:
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
