from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

class Base(DeclarativeBase):
    pass

_engine_kwargs = {"pool_pre_ping": True}
if settings.database_url.startswith('sqlite'):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    if settings.database_url.endswith(':memory:'):
        _engine_kwargs["poolclass"] = StaticPool
engine = create_engine(settings.database_url, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def init_db() -> None:
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)
