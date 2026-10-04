from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db, SessionLocal
from app.ingest import ingest_xml

def test_health_and_search():
    init_db()
    with SessionLocal() as s:
        ingest_xml(s,'fixtures/rpi-layout-sample.xml')
    client=TestClient(app)
    assert client.get('/health').status_code==200
    r=client.post('/v1/trademarks/search',json={'query':'MARCA EXEMPLO','nice_classes':[39],'limit':10})
    assert r.status_code==200
    data=r.json()
    assert data['results']
    assert data['results'][0]['process_number']=='123456789'
