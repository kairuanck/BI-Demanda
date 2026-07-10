"""Tabela `empresas` — entidade nova da Sprint 2 (ver docs/DECISIONS.md).

Representa a empresa/organização operadora, preparando o caminho de
evolução multi-tenant descrito em TUTORIAL.md, seção 15, sem ainda ser
referenciada pelas demais tabelas (single-tenant na POC).

Por ser tabela nova, aplica o padrão completo de colunas pedido na
Sprint 2: UUID, criado_em, atualizado_em, deletado_em (soft delete),
criado_por e atualizado_por.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


def _novo_uuid() -> str:
    return str(uuid.uuid4())


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=_novo_uuid)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deletado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    atualizado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
