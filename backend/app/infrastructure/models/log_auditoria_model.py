"""Tabela `logs_auditoria` (DICIONARIO_DE_DADOS.md, seção 20)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import AcaoAuditoria
from app.infrastructure.database import Base


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    __table_args__ = (
        Index("ix_logs_auditoria_entidade", "entidade", "entidade_id"),
        Index("ix_logs_auditoria_usuario", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acao: Mapped[AcaoAuditoria] = mapped_column(
        SAEnum(AcaoAuditoria, native_enum=False, length=20), nullable=False
    )
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    dados_antes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    dados_depois: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ip_origem: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
