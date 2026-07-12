"""Tabela `empresas` — entidade criada na Sprint 2 (ver docs/DECISIONS.md).

Representa a empresa/organização operadora, preparando o caminho de
evolução multi-tenant descrito em TUTORIAL.md, seção 15, sem ainda ser
referenciada pelas demais tabelas (single-tenant na POC).

Sprint 3: com a identidade UUID generalizada (docs/DECISIONS.md, seção 13),
a coluna `uuid` separada foi consolidada no próprio `id`.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deletado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    atualizado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
