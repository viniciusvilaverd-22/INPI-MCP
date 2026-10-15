from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.db import init_db, SessionLocal
from app.ingest import ingest_xml


def test_health_and_search():
    init_db()
    with SessionLocal() as session:
        ingest_xml(session, "fixtures/rpi-layout-sample.xml")
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["release"] == "community-v1"
    assert health.json()["version"] == "0.3.1"
    assert health.json()["environment"] == settings.app_env

    response = client.post(
        "/v1/trademarks/search",
        json={"query": "MARCA EXEMPLO", "nice_classes": [39], "limit": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["results"]
    assert data["results"][0]["process_number"] == "123456789"


def test_root_and_demo_are_available():
    client = TestClient(app)
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["demo"] == "/demo"

    demo = client.get("/demo")
    assert demo.status_code == 200
    assert "INPI MCP" in demo.text
    assert "parecer juridico" in demo.text


def test_rpi_status_endpoint_is_read_only_and_available():
    init_db()
    client = TestClient(app)
    response = client.get("/v1/rpi/status")
    assert response.status_code == 200
    data = response.json()
    assert "last_ingested_rpi" in data
    assert "last_checked_rpi" in data
    assert "operational" in data
    assert "status_counts" in data["operational"]
    assert isinstance(data["recent_runs"], list)


def test_admin_ingest_is_closed_by_default():
    client = TestClient(app)
    response = client.post(
        "/v1/admin/ingest/xml",
        params={"path": "fixtures/rpi-layout-sample.xml"},
    )
    assert response.status_code == 404


def test_admin_ingest_requires_dev_and_explicit_opt_in(monkeypatch):
    monkeypatch.setattr(settings, "enable_dev_admin_ingest", True)
    monkeypatch.setattr(settings, "app_env", "dev")

    client = TestClient(app)
    response = client.post(
        "/v1/admin/ingest/xml",
        params={"path": "fixtures/rpi-layout-sample.xml"},
    )
    assert response.status_code == 200

    monkeypatch.setattr(settings, "app_env", "production")
    response = client.post(
        "/v1/admin/ingest/xml",
        params={"path": "fixtures/rpi-layout-sample.xml"},
    )
    assert response.status_code == 404
