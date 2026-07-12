"""Tabela `visitas_resumo_sb` (Sprint 3, docs/DECISIONS.md, seção 13).

Espelho normalizado do relatório "Supervisor" do SB Promotor: 1 linha =
1 par promotor×cliente com contagens agregadas de visitas do mês de
competência. É a fotografia mensal oficial da carteira (definição de
negócio, seção 12) — o loader deriva as vigências de `carteiras` daqui.
Todos os campos do relatório real são preservados, inclusive os três
percentuais do bloco cliente.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class VisitaResumoSb(Base):
    __tablename__ = "visitas_resumo_sb"
    __table_args__ = (
        UniqueConstraint(
            "promotor_id",
            "cliente_id",
            "competencia",
            name="uq_visitas_resumo_sb_promotor_cliente_competencia",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    promotor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("promotores.id", ondelete="RESTRICT"), nullable=False
    )
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    competencia: Mapped[date] = mapped_column(Date, nullable=False)
    # Bloco promotor do relatório real (contagens do promotor no mês)
    visitas_previstas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    previstas_realizadas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    previstas_nao_realizadas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nao_previstas_realizadas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Bloco cliente do relatório real (contagens do par promotor×cliente)
    cliente_visitas_previstas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cliente_visitas_realizadas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cliente_nao_visitas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    perc_visitas_realizadas: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    perc_nao_visitas: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    perc_cobertura: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
