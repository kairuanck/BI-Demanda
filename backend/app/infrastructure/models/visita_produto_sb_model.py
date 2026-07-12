"""Tabela `visitas_produtos_sb` (Sprint 3, docs/DECISIONS.md, seção 13).

Detalhe de produtos verificados em visita, do arquivo de detalhe do SB
Promotor (aba `Produtos`): 1 linha = 1 produto verificado em 1 visita.
`codigo_visita_externa` referencia o id VISITA do SB — mesmo espaço de
códigos usado pelas aplicações de checklist (`visitas.codigo_externo`).
Todas as colunas do arquivo real são preservadas.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class VisitaProdutoSb(Base):
    __tablename__ = "visitas_produtos_sb"
    __table_args__ = (Index("ix_visitas_produtos_sb_visita", "codigo_visita_externa"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    codigo_visita_externa: Mapped[str] = mapped_column(String(50), nullable=False)
    promotor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("promotores.id", ondelete="RESTRICT"), nullable=False
    )
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    uf_sigla: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("ufs.sigla", ondelete="RESTRICT"), nullable=True
    )
    data_inicial: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_final: Mapped[date | None] = mapped_column(Date, nullable=True)
    operacao: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grupo_marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    codigo_produto: Mapped[str | None] = mapped_column(String(50), nullable=True)
    produto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    validade: Mapped[date | None] = mapped_column(Date, nullable=True)
    lote: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estoque: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    preco: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
