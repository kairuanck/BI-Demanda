"""Tabela `promotores` (DICIONARIO_DE_DADOS.md, seção 4).

Sprint 3 — adaptações aos dados reais (docs/DECISIONS.md, seções 12–13):
- `tipo` deixa de ser enum embutido e vira FK para `tipos_promotor`
  (cadastral, nunca inferido dos dados). Promotores criados via importação
  ficam com tipo nulo até o cadastro definir.
- `supervisor_id` passa a aceitar nulo: nenhuma fonte real informa
  supervisor.
- `area` vem do relatório Supervisor do SB Promotor.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Promotor(Base):
    __tablename__ = "promotores"
    __table_args__ = (Index("ix_promotores_tipo", "tipo_promotor_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo_externo: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    tipo_promotor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tipos_promotor.id", ondelete="RESTRICT"), nullable=True
    )
    supervisor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("supervisores.id", ondelete="RESTRICT"), nullable=True
    )
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_admissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
