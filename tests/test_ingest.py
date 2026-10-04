import hashlib
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import TrademarkProcess, TrademarkEvent, TrademarkNiceClass
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

def test_ingest_accepts_official_nested_nice_class_layout(tmp_path):
    long_spec='Item de classe; ' * 700
    xml=tmp_path/'nested-rpi.xml'
    xml.write_text(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<revista numero="2908" data="29/09/2026">
  <processo numero="937661422" data-deposito="15/01/2025">
    <despachos><despacho codigo="IPAS158" nome="Concessão de registro"/></despachos>
    <marca apresentacao="Mista" natureza="Produtos e/ou Serviço"><nome>MARCA REALISTA</nome></marca>
    <lista-classe-nice>
      <classe-nice codigo="18"><especificacao>{long_spec}</especificacao><status>Ativa</status></classe-nice>
    </lista-classe-nice>
  </processo>
</revista>''',
        encoding='utf-8',
    )
    engine=create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    S=sessionmaker(bind=engine,expire_on_commit=False)
    with S() as s:
        result=ingest_xml(s,xml)
        tm=s.scalar(select(TrademarkProcess).where(TrademarkProcess.process_number=='937661422'))
        classes=list(s.scalars(select(TrademarkNiceClass)))
        normalized_spec=long_spec.strip()
        assert result['parser_version']=='rpi-marcas-xml-0.2.1'
        assert tm is not None
        assert tm.mark_name=='MARCA REALISTA'
        assert len(classes)==1
        assert classes[0].nice_class==18
        assert classes[0].specification==normalized_spec
        assert classes[0].specification_hash==hashlib.sha256(normalized_spec.encode('utf-8')).hexdigest()
