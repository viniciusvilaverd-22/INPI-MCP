from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .db import SessionLocal, init_db
from .repository import TrademarkRepository
from .services import TrademarkService
from .schemas import SearchRequest, CompareRequest, IngestResponse
from .ingest import ingest_xml

VERSION = "0.2.1"
RELEASE = "community-v1"
DEMO_PATH = Path(__file__).parent / "static" / "demo.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="INPI Trademark Intelligence",
    version=VERSION,
    description=(
        "Pesquisa e comparacao computacional de marcas com dados estruturados do INPI. "
        "Resultados nao constituem parecer juridico."
    ),
    lifespan=lifespan,
)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/")
def root():
    return {
        "name": "INPI MCP",
        "version": VERSION,
        "release": RELEASE,
        "status": "dev",
        "demo": "/demo",
        "docs": "/docs",
        "health": "/health",
        "disclaimer": "Projeto independente e nao oficial; resultados nao constituem decisao do INPI.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION, "release": RELEASE}


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo():
    if not DEMO_PATH.exists():
        raise HTTPException(500, "demo local nao encontrada")
    return HTMLResponse(DEMO_PATH.read_text(encoding="utf-8"))


@app.post("/v1/trademarks/search")
def search(req: SearchRequest, session: Session = Depends(get_session)):
    return TrademarkService(TrademarkRepository(session)).search(
        req.query, req.nice_classes, req.limit
    )


@app.post("/v1/trademarks/compare")
def compare(req: CompareRequest):
    return TrademarkService(None).compare(req.left, req.right)


@app.get("/v1/trademarks/{process_number}")
def get_process(process_number: str, session: Session = Depends(get_session)):
    tm = TrademarkRepository(session).get(process_number)
    if not tm:
        raise HTTPException(404, "processo nao encontrado")
    return {
        "process_number": tm.process_number,
        "mark_name": tm.mark_name,
        "nice_classes": [
            {
                "class": c.nice_class,
                "edition": c.edition,
                "specification": c.specification,
            }
            for c in tm.classes
        ],
        "events": [
            {
                "rpi_number": e.rpi_number,
                "rpi_date": str(e.rpi_date) if e.rpi_date else None,
                "dispatch_code": e.dispatch_code,
                "dispatch_name": e.dispatch_name,
            }
            for e in sorted(tm.events, key=lambda e: e.rpi_number, reverse=True)
        ],
    }


@app.post("/v1/admin/ingest/xml", response_model=IngestResponse)
def ingest(path: str, session: Session = Depends(get_session)):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(400, "arquivo XML nao encontrado")
    return ingest_xml(session, p)
