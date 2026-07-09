"""Tabela `checklist_perguntas` (DICIONARIO_DE_DADOS.md, seção 15)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import TipoRespostaChecklist
from app.infrastructure.database import Base


class ChecklistPergunta(Base):
    __tablename__ = "checklist_perguntas"
    __table_args__ = (
        UniqueConstraint("checklist_id", "ordem", name="uq_checklist_perguntas_checklist_ordem"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("checklists.id", ondelete="CASCADE"), nullable=False
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    enunciado: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_resposta: Mapped[TipoRespostaChecklist] = mapped_column(
        SAEnum(TipoRespostaChecklist, native_enum=False, length=20), nullable=False
    )
    obrigatoria: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    peso: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=1, nullable=False)
