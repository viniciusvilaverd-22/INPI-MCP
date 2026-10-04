import zipfile

import pytest

from app.rpi_source import build_rpi_url, extract_rpi_zip, inspect_rpi_xml, sha256_file


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
