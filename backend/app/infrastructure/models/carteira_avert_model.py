"""Tabela `carteiras_avert` (Sprint 3, docs/DECISIONS.md, seção 13).

Espelho do Painel Trade Avert — a carteira oficial da operação Avert
(definição de negócio, seção 12): 1 linha = 1 cliente da carteira,
identificado por CNPJ. CONSULTOR é a promotora (WeCheck). CNPJs sem
correspondência na base interna ficam com `cliente_id` nulo e viram
pendência em `clientes_integracao` — nunca criam cliente automaticamente.
Todas as colunas do painel real são preservadas, inclusive as de compra
que chegaram vazias.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class CarteiraAvert(Base):
    __tablename__ = "carteiras_avert"
    __table_args__ = (
        Index("ix_carteiras_avert_cnpj", "cnpj"),
        Index("ix_carteiras_avert_promotor", "promotor_id"),
        Index("ix_carteiras_avert_cliente", "cliente_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    cnpj: Mapped[str] = mapped_column(String(20), nullable=False)
    cliente_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True
    )
    promotor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("promotores.id", ondelete="SET NULL"), nullable=True
    )
    competencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    uf_sigla: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("ufs.sigla", ondelete="RESTRICT"), nullable=True
    )
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    regional: Mapped[str | None] = mapped_column(String(100), nullable=True)
    distribuidor: Mapped[str | None] = mapped_column(String(150), nullable=True)
    coordenador: Mapped[str | None] = mapped_column(String(150), nullable=True)
    consultor: Mapped[str | None] = mapped_column(String(150), nullable=True)
    vendedor: Mapped[str | None] = mapped_column(String(150), nullable=True)
    grupo_economico: Mapped[str | None] = mapped_column(String(150), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    razao_social: Mapped[str | None] = mapped_column(String(200), nullable=True)
    segmento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    compra_2025: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    compra_2026: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    crescimento: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
