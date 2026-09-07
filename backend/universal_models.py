"""Indexed universal aggregates, separate from preserved drawing records."""
from sqlalchemy import String, JSON, Integer, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base, uid, now


class ControlledChange(Base):
    __tablename__ = 'controlled_changes'
    __table_args__ = (Index('ix_controlled_tenant_domain_status', 'tenant', 'domain', 'status'),)
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32), nullable=False)
    domain: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default='DRAFT')
    classification: Mapped[str] = mapped_column(String(30), default='INTERNAL')
    data: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created: Mapped[object] = mapped_column(DateTime(timezone=True), default=now)
    updated: Mapped[object] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    __mapper_args__ = {'version_id_col': version}


class Dependency(Base):
    __tablename__ = 'change_dependencies'
    __table_args__ = (UniqueConstraint('tenant', 'change_id', 'source', 'target', 'relation', name='uq_change_dependency'),
                      Index('ix_dependency_traversal', 'tenant', 'change_id', 'source'))
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(32))
    change_id: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(100))
    target: Mapped[str] = mapped_column(String(100))
    relation: Mapped[str] = mapped_column(String(80))
    evidence: Mapped[dict] = mapped_column(JSON)
