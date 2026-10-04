import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def utcnow():
    return datetime.now(timezone.utc)

class TrademarkProcess(Base):
    __tablename__ = 'trademark_process'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    process_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    filing_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    grant_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    mark_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    mark_name_normalized: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    presentation_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    nature: Mapped[str | None] = mapped_column(Text, nullable=True)
    translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    attorney_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_rpi_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    classes: Mapped[list['TrademarkNiceClass']] = relationship(cascade='all, delete-orphan', back_populates='trademark')
    events: Mapped[list['TrademarkEvent']] = relationship(cascade='all, delete-orphan', back_populates='trademark')

class TrademarkNiceClass(Base):
    __tablename__ = 'trademark_nice_class'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trademark_id: Mapped[str] = mapped_column(ForeignKey('trademark_process.id', ondelete='CASCADE'), index=True)
    nice_class: Mapped[int] = mapped_column(Integer, index=True)
    edition: Mapped[str | None] = mapped_column(String(16), nullable=True)
    specification: Mapped[str | None] = mapped_column(Text, nullable=True)
    specification_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    trademark: Mapped['TrademarkProcess'] = relationship(back_populates='classes')
    __table_args__ = (
        UniqueConstraint('trademark_id','nice_class','specification_hash', name='uq_tm_class_spec_hash'),
    )

class TrademarkEvent(Base):
    __tablename__ = 'trademark_event'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trademark_id: Mapped[str] = mapped_column(ForeignKey('trademark_process.id', ondelete='CASCADE'), index=True)
    rpi_number: Mapped[int] = mapped_column(Integer, index=True)
    rpi_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    dispatch_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dispatch_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    complementary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    protocol_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_payload_hash: Mapped[str] = mapped_column(String(64))
    parser_version: Mapped[str] = mapped_column(String(64))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    trademark: Mapped['TrademarkProcess'] = relationship(back_populates='events')
    __table_args__ = (
        UniqueConstraint('rpi_number','trademark_id','dispatch_code','protocol_number','raw_payload_hash', name='uq_event_idempotency'),
        Index('ix_event_tm_rpi', 'trademark_id', 'rpi_number'),
    )

class RPIIngestionState(Base):
    __tablename__ = 'rpi_ingestion_state'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    last_ingested_rpi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_checked_rpi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class RPIIngestionRun(Base):
    __tablename__ = 'rpi_ingestion_run'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rpi_number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), index=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    zip_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    xml_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    process_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
