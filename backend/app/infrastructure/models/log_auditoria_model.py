"""Tabela `logs_auditoria` (DICIONARIO_DE_DADOS.md, seção 20).

Sprint 3: `entidade_id` vira String(36) — as entidades passam a ter
identidade UUID interna (docs/DECISIONS.md, seção 13).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import AcaoAuditoria
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    __table_args__ = (
        Index("ix_logs_auditoria_entidade", "entidade", "entidade_id"),
        Index("ix_logs_auditoria_usuario", "usuario_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    acao: Mapped[AcaoAuditoria] = mapped_column(
        SAEnum(AcaoAuditoria, native_enum=False, length=20), nullable=False
    )
    usuario_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    dados_antes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    dados_depois: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ip_origem: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
