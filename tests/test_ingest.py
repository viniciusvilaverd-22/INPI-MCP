from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import TrademarkProcess, TrademarkEvent
from app.ingest import ingest_xml

def test_ingest_is_idempotent(tmp_path):
    engine=create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    S=sessionmaker(bind=engine,expire_on_commit=False)
    fixture='fixtures/rpi-layout-sample.xml'
    with S() as s:
        a=ingest_xml(s,fixture)
        b=ingest_xml(s,fixture)
        assert a['process_count']==2
        assert a['event_count']==2
        assert b['event_count']==0
        assert len(list(s.scalars(select(TrademarkProcess))))==2
        assert len(list(s.scalars(select(TrademarkEvent))))==2
