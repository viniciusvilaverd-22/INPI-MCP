from fastapi.testclient import TestClient

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
