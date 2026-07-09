"""Tabela `clientes` (DICIONARIO_DE_DADOS.md, seção 10)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_externo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    razao_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cnpj_cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    uf_sigla: Mapped[str] = mapped_column(
        String(2), ForeignKey("ufs.sigla", ondelete="RESTRICT"), nullable=False
    )
    cidade_id: Mapped[int] = mapped_column(
        ForeignKey("cidades.id", ondelete="RESTRICT"), nullable=False
    )
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
