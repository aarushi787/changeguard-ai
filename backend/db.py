import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, JSON, DateTime, Text, event, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

def now():
    return datetime.now(timezone.utc)

def uid():
    return uuid.uuid4().hex

from backend.database_config import database_settings, configured_engine
DATABASE_URL, DATABASE_CONNECT_ARGS, SUPABASE = database_settings()
os.makedirs('data', exist_ok=True)
engine = configured_engine(DATABASE_URL, DATABASE_CONNECT_ARGS, SUPABASE, pool_pre_ping=True)
Session = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Organization(Base):
    __tablename__ = 'organizations'
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(160))
    pack: Mapped[str] = mapped_column(String(60), default='precision_engineering')

class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32), index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(40))

class AuthSession(Base):
    __tablename__ = 'sessions'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Record(Base):
    """Tenant-scoped aggregate store. Type and JSON schemas enforced at the API boundary."""
    __tablename__ = 'records'
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32), index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    data: Mapped[dict] = mapped_column(JSON)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    __mapper_args__ = {'version_id_col': version}

class KnowledgeEdge(Base):
    __tablename__ = 'knowledge_edges'
    __table_args__ = (UniqueConstraint('tenant','project_id','source','target','relation',name='uq_knowledge_edge'),)
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(100))
    target: Mapped[str] = mapped_column(String(100))
    relation: Mapped[str] = mapped_column(String(80))
    evidence: Mapped[dict] = mapped_column(JSON)

class EvidenceSnapshot(Base):
    __tablename__ = 'evidence_snapshots'
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32), index=True)
    entity: Mapped[str] = mapped_column(String(32), index=True)
    stage: Mapped[str] = mapped_column(String(40))
    digest: Mapped[str] = mapped_column(String(64))
    data: Mapped[dict] = mapped_column(JSON)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Audit(Base):
    __tablename__ = 'audit_events'
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32), index=True)
    actor: Mapped[str] = mapped_column(String(200))
    entity: Mapped[str] = mapped_column(String(32), index=True)
    operation: Mapped[str] = mapped_column(String(80))
    details: Mapped[dict] = mapped_column(JSON)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

@event.listens_for(Audit, 'before_update')
@event.listens_for(Audit, 'before_delete')
@event.listens_for(EvidenceSnapshot, 'before_update')
@event.listens_for(EvidenceSnapshot, 'before_delete')
def immutable(*args):
    raise ValueError('Audit events are append-only')
