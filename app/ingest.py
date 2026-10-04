from __future__ import annotations
import hashlib, json, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import TrademarkProcess, TrademarkNiceClass, TrademarkEvent
from .normalization import normalize_mark

PARSER_VERSION='rpi-marcas-xml-0.2.1'

def _date(v):
    if not v: return None
    for fmt in ('%d/%m/%Y','%Y-%m-%d'):
        try: return datetime.strptime(v,fmt).date()
        except ValueError: pass
    return None

def _sha_file(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def _text(el, path):
    x=el.find(path)
    return (x.text or '').strip() if x is not None and x.text else None

def _stable_hash(payload):
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()

def _specification_hash(value):
    return hashlib.sha256((value or '').encode('utf-8')).hexdigest()

def _nice_class_nodes(process):
    return [
        *process.findall('classe-nice'),
        *process.findall('./lista-classe-nice/classe-nice'),
    ]

def ingest_xml(session: Session, path: str | Path):
    path=Path(path); source_sha=_sha_file(path)
    rpi_number=None; rpi_date=None; pc=0; ec=0
    for ev, elem in ET.iterparse(path, events=('start','end')):
        if ev=='start' and elem.tag=='revista' and rpi_number is None:
            rpi_number=int(elem.attrib['numero']) if elem.attrib.get('numero') else None
            rpi_date=_date(elem.attrib.get('data'))
        elif ev=='end' and elem.tag=='processo':
            number=elem.attrib.get('numero')
            if not number:
                elem.clear(); continue
            tm=session.scalar(select(TrademarkProcess).where(TrademarkProcess.process_number==number))
            if tm is None:
                tm=TrademarkProcess(process_number=number)
                session.add(tm); session.flush()
            tm.filing_date=_date(elem.attrib.get('data-deposito')) or tm.filing_date
            tm.grant_date=_date(elem.attrib.get('data-concessao')) or tm.grant_date
            tm.expiry_date=_date(elem.attrib.get('data-vigencia')) or tm.expiry_date
            tm.last_rpi_number=rpi_number
            mark=elem.find('marca')
            if mark is not None:
                tm.mark_name=_text(mark,'nome') or tm.mark_name
                if tm.mark_name:
                    tm.mark_name_normalized=normalize_mark(tm.mark_name)
                tm.presentation_type=mark.attrib.get('apresentacao') or tm.presentation_type
                tm.nature=mark.attrib.get('natureza') or tm.nature
                tm.translation=_text(mark,'traducao') or tm.translation
            tm.attorney_name=_text(elem,'procurador') or tm.attorney_name
            for nc in _nice_class_nodes(elem):
                code=nc.attrib.get('codigo')
                if not code or not code.isdigit(): continue
                spec=_text(nc,'especificacao')
                spec_hash=_specification_hash(spec)
                exists=any(
                    c.nice_class==int(code) and c.specification_hash==spec_hash
                    for c in tm.classes
                )
                if not exists:
                    tm.classes.append(TrademarkNiceClass(
                        nice_class=int(code),
                        edition=nc.attrib.get('edicao'),
                        specification=spec,
                        specification_hash=spec_hash,
                    ))
            ds=elem.find('despachos')
            if ds is not None:
                for d in ds.findall('despacho'):
                    proto=d.find('protocolo')
                    pnum=proto.attrib.get('numero') if proto is not None else None
                    payload={'rpi':rpi_number,'process':number,'code':d.attrib.get('codigo'),'name':d.attrib.get('nome'),'text':_text(d,'texto-complementar'),'protocol':pnum}
                    rh=_stable_hash(payload)
                    existing=session.scalar(select(TrademarkEvent).where(
                        TrademarkEvent.rpi_number==rpi_number,
                        TrademarkEvent.trademark_id==tm.id,
                        TrademarkEvent.dispatch_code==d.attrib.get('codigo'),
                        TrademarkEvent.protocol_number==pnum,
                        TrademarkEvent.raw_payload_hash==rh,
                    ))
                    if existing is None:
                        tm.events.append(TrademarkEvent(
                            rpi_number=rpi_number or 0, rpi_date=rpi_date,
                            dispatch_code=d.attrib.get('codigo'), dispatch_name=d.attrib.get('nome'),
                            complementary_text=_text(d,'texto-complementar'), protocol_number=pnum,
                            raw_payload_hash=rh, parser_version=PARSER_VERSION))
                        ec += 1
            pc += 1
            session.flush(); elem.clear()
    session.commit()
    return {'rpi_number':rpi_number,'rpi_date':rpi_date.isoformat() if rpi_date else None,'process_count':pc,'event_count':ec,'source_sha256':source_sha,'parser_version':PARSER_VERSION}
