from .db import SessionLocal
from .repository import TrademarkRepository
from .services import TrademarkService
from .schemas import CompareSide

def search_trademarks(query: str, nice_classes: list[int] | None=None, limit: int=20):
    with SessionLocal() as s:
        return TrademarkService(TrademarkRepository(s)).search(query,nice_classes or [],limit)

def compare_trademarks(left_name: str, right_name: str, left_classes: list[int] | None=None, right_classes: list[int] | None=None):
    svc=TrademarkService(None)
    return svc.compare(CompareSide(name=left_name,nice_classes=left_classes or []), CompareSide(name=right_name,nice_classes=right_classes or []))

def get_trademark_process(process_number: str):
    with SessionLocal() as s:
        tm=TrademarkRepository(s).get(process_number)
        if not tm: return {'found':False,'process_number':process_number}
        return {'found':True,'process_number':tm.process_number,'mark_name':tm.mark_name,'nice_classes':[c.nice_class for c in tm.classes]}
