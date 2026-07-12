"""Tabela `vendedores` (DICIONARIO_DE_DADOS.md, seção 5)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Vendedor(Base):
    __tablename__ = "vendedores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo_externo: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
