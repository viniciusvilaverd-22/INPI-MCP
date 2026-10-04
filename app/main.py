from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from .repository import TrademarkRepository
from .services import TrademarkService
from .schemas import SearchRequest, CompareRequest, IngestResponse
from .ingest import ingest_xml

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app=FastAPI(title='INPI Trademark Intelligence MVP', version='0.1.0', lifespan=lifespan)

def get_session():
    s=SessionLocal()
    try: yield s
    finally: s.close()

@app.get('/health')
def health(): return {'status':'ok','version':'0.1.0'}

@app.post('/v1/trademarks/search')
def search(req: SearchRequest, session: Session=Depends(get_session)):
    return TrademarkService(TrademarkRepository(session)).search(req.query,req.nice_classes,req.limit)

@app.post('/v1/trademarks/compare')
def compare(req: CompareRequest):
    return TrademarkService(None).compare(req.left,req.right)

@app.get('/v1/trademarks/{process_number}')
def get_process(process_number: str, session: Session=Depends(get_session)):
    tm=TrademarkRepository(session).get(process_number)
    if not tm: raise HTTPException(404,'processo não encontrado')
    return {
        'process_number':tm.process_number,'mark_name':tm.mark_name,
        'nice_classes':[{'class':c.nice_class,'edition':c.edition,'specification':c.specification} for c in tm.classes],
        'events':[{'rpi_number':e.rpi_number,'rpi_date':str(e.rpi_date) if e.rpi_date else None,'dispatch_code':e.dispatch_code,'dispatch_name':e.dispatch_name} for e in sorted(tm.events,key=lambda e:e.rpi_number, reverse=True)],
    }

@app.post('/v1/admin/ingest/xml', response_model=IngestResponse)
def ingest(path: str, session: Session=Depends(get_session)):
    p=Path(path)
    if not p.exists() or not p.is_file(): raise HTTPException(400,'arquivo XML não encontrado')
    return ingest_xml(session,p)
