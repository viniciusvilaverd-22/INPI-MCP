from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, selectinload
from .models import TrademarkProcess, TrademarkNiceClass
from .normalization import normalize_mark

class TrademarkRepository:
    def __init__(self, session: Session):
        self.session=session

    def get(self, process_number: str):
        return self.session.scalar(select(TrademarkProcess).options(selectinload(TrademarkProcess.classes), selectinload(TrademarkProcess.events)).where(TrademarkProcess.process_number==process_number))

    def candidates(self, query: str, nice_classes: list[int], limit: int=100):
        qn=normalize_mark(query)
        stmt=select(TrademarkProcess).options(selectinload(TrademarkProcess.classes))
        dialect=self.session.get_bind().dialect.name
        if nice_classes:
            stmt=stmt.where(TrademarkProcess.classes.any(TrademarkNiceClass.nice_class.in_(nice_classes)))
        if dialect=='postgresql':
            sim=func.similarity(TrademarkProcess.mark_name_normalized, qn)
            stmt=stmt.where(or_(TrademarkProcess.mark_name_normalized.ilike(f'%{qn}%'), sim > 0.20)).order_by(sim.desc())
        else:
            tokens=[t for t in qn.split() if len(t)>=2][:4]
            if tokens:
                stmt=stmt.where(or_(*[TrademarkProcess.mark_name_normalized.ilike(f'%{t}%') for t in tokens]))
        stmt=stmt.limit(max(limit,20))
        return list(self.session.scalars(stmt).unique())
