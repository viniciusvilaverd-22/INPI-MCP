import urllib.error
import zipfile

import pytest

import app.rpi_source as rpi_source
from app.rpi_source import (
    RPIProbe,
    build_rpi_url,
    discover_rpis,
    extract_rpi_zip,
    inspect_rpi_xml,
    probe_rpi,
    sha256_file,
)


def _make_zip(tmp_path, xml_text: str, member: str = "RM2908.xml"):
    path = tmp_path / "RM2908.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, xml_text)
    return path


def test_build_official_rpi_url():
    assert build_rpi_url(2908) == "https://revistas.inpi.gov.br/txt/RM2908.zip"


def test_extract_rpi_zip_and_inspect_header(tmp_path):
    zip_path = _make_zip(
        tmp_path,
        '<?xml version="1.0"?><revista numero="2908" data="29/09/2026"></revista>',
    )
    xml_path = extract_rpi_zip(zip_path, 2908, tmp_path / "out")
    assert xml_path.name == "RM2908.xml"
    assert inspect_rpi_xml(xml_path)["rpi_number"] == 2908
    assert len(sha256_file(xml_path)) == 64


def test_extractor_does_not_trust_archive_path(tmp_path):
    zip_path = _make_zip(
        tmp_path,
        '<revista numero="2908" data="29/09/2026"></revista>',
        member="../../RM2908.xml",
    )
    out = tmp_path / "safe"
    xml_path = extract_rpi_zip(zip_path, 2908, out)
    assert xml_path.parent == out
    assert not (tmp_path.parent / "RM2908.xml").exists()


def test_rejects_mismatched_rpi(tmp_path):
    zip_path = _make_zip(
        tmp_path,
        '<revista numero="9999" data="29/09/2026"></revista>',
    )
    with pytest.raises(ValueError, match="difere"):
        extract_rpi_zip(zip_path, 2908, tmp_path / "out")


class _FakeResponse:
    def __init__(self, status=200, headers=None):
        self.status = status
        self.headers = headers or {}
        self.closed = False

    def getcode(self):
        return self.status

    def close(self):
        self.closed = True


def test_probe_rpi_available(monkeypatch):
    response = _FakeResponse(
        status=200,
        headers={"Content-Length": "12345", "Last-Modified": "Tue, 06 Oct 2026 10:00:00 GMT"},
    )
    monkeypatch.setattr(rpi_source.urllib.request, "urlopen", lambda request, timeout: response)
    probe = probe_rpi(2909)
    assert probe.available is True
    assert probe.status_code == 200
    assert probe.content_length == 12345


def test_probe_rpi_404_is_not_available(monkeypatch):
    def missing(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

    monkeypatch.setattr(rpi_source.urllib.request, "urlopen", missing)
    probe = probe_rpi(2909)
    assert probe.available is False
    assert probe.status_code == 404


def test_discovery_stops_at_first_missing(monkeypatch):
    def fake_probe(number, timeout=30):
        return RPIProbe(
            rpi_number=number,
            source_url=build_rpi_url(number),
            available=number < 2910,
            status_code=200 if number < 2910 else 404,
            content_length=None,
            last_modified=None,
        )

    monkeypatch.setattr(rpi_source, "probe_rpi", fake_probe)
    probes = discover_rpis(2908, max_scan=4)
    assert [item.rpi_number for item in probes] == [2909, 2910]
    assert [item.available for item in probes] == [True, False]


def test_probe_rpi_falls_back_to_ranged_get_on_head_403(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.get_method())
        if request.get_method() == "HEAD":
            raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, None)
        assert request.headers.get("Range") == "bytes=0-0"
        return _FakeResponse(status=206, headers={"Content-Length": "1"})

    monkeypatch.setattr(rpi_source.urllib.request, "urlopen", fake_urlopen)
    probe = probe_rpi(2909)

    assert calls == ["HEAD", "GET"]
    assert probe.available is True
    assert probe.status_code == 206
