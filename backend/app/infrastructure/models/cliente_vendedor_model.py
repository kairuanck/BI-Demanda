"""Tabela `clientes_vendedores` (Sprint 3, docs/DECISIONS.md, seção 13).

Vínculo cliente×vendedor (RCA) da Base de Clientes real: as colunas
`RCA 1..4` viram até 4 linhas por cliente, com `ordem` preservando a
posição original (regra "nunca descartar colunas").
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class ClienteVendedor(Base):
    __tablename__ = "clientes_vendedores"
    __table_args__ = (
        UniqueConstraint("cliente_id", "ordem", name="uq_clientes_vendedores_cliente_ordem"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False
    )
    vendedor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendedores.id", ondelete="RESTRICT"), nullable=False
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
