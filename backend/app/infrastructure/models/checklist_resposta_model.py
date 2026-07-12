"""Tabela `checklist_respostas` (DICIONARIO_DE_DADOS.md, seção 16).

Sprint 3: `resposta_valor` vira Text — respostas reais do WeCheck incluem
descrições longas e URLs de fotos que excedem 500 caracteres.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class ChecklistResposta(Base):
    __tablename__ = "checklist_respostas"
    __table_args__ = (
        UniqueConstraint(
            "visita_id", "checklist_pergunta_id", name="uq_checklist_respostas_visita_pergunta"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    visita_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visitas.id", ondelete="CASCADE"), nullable=False
    )
    checklist_pergunta_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("checklist_perguntas.id", ondelete="RESTRICT"), nullable=False
    )
    resposta_valor: Mapped[str] = mapped_column(Text, nullable=False)
    conforme: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
