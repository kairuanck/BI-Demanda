"""Tabela `faturamentos` (DICIONARIO_DE_DADOS.md, seção 12)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Faturamento(Base):
    __tablename__ = "faturamentos"
    __table_args__ = (
        Index("ix_faturamentos_periodo", "ano", "mes"),
        Index("ix_faturamentos_cliente_periodo", "cliente_id", "ano", "mes"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    laboratorio_id: Mapped[int] = mapped_column(
        ForeignKey("laboratorios.id", ondelete="RESTRICT"), nullable=False
    )
    departamento_id: Mapped[int] = mapped_column(
        ForeignKey("departamentos.id", ondelete="RESTRICT"), nullable=False
    )
    vendedor_id: Mapped[int | None] = mapped_column(
        ForeignKey("vendedores.id", ondelete="SET NULL"), nullable=True
    )
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_faturado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    importacao_id: Mapped[int] = mapped_column(
        ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
