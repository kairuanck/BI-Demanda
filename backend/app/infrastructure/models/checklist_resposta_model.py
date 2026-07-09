"""Tabela `checklist_respostas` (DICIONARIO_DE_DADOS.md, seção 16)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ChecklistResposta(Base):
    __tablename__ = "checklist_respostas"
    __table_args__ = (
        UniqueConstraint(
            "visita_id", "checklist_pergunta_id", name="uq_checklist_respostas_visita_pergunta"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visita_id: Mapped[int] = mapped_column(
        ForeignKey("visitas.id", ondelete="CASCADE"), nullable=False
    )
    checklist_pergunta_id: Mapped[int] = mapped_column(
        ForeignKey("checklist_perguntas.id", ondelete="RESTRICT"), nullable=False
    )
    resposta_valor: Mapped[str] = mapped_column(String(500), nullable=False)
    conforme: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    importacao_id: Mapped[int] = mapped_column(
        ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
