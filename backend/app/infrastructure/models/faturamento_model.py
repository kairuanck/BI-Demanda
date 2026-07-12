"""Tabela `faturamentos` (DICIONARIO_DE_DADOS.md, seção 12).

Sprint 3: a matriz real Cliente×Marca não traz departamento, vendedor nem
quantidade — `departamento_id` passa a aceitar nulo e o valor mensal por
marca entra como uma linha por cliente×laboratório×competência
(docs/DECISIONS.md, seção 13). Valores negativos são devoluções líquidas.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Faturamento(Base):
    __tablename__ = "faturamentos"
    __table_args__ = (
        Index("ix_faturamentos_periodo", "ano", "mes"),
        Index("ix_faturamentos_cliente_periodo", "cliente_id", "ano", "mes"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    laboratorio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("laboratorios.id", ondelete="RESTRICT"), nullable=False
    )
    departamento_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departamentos.id", ondelete="RESTRICT"), nullable=True
    )
    vendedor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("vendedores.id", ondelete="SET NULL"), nullable=True
    )
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_faturado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
