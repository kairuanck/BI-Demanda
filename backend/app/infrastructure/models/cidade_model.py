"""Tabela `cidades` (DICIONARIO_DE_DADOS.md, seção 9)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Cidade(Base):
    __tablename__ = "cidades"
    __table_args__ = (UniqueConstraint("nome", "uf_sigla", name="uq_cidades_nome_uf"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    uf_sigla: Mapped[str] = mapped_column(
        String(2), ForeignKey("ufs.sigla", ondelete="RESTRICT"), nullable=False
    )
    codigo_ibge: Mapped[str | None] = mapped_column(String(10), unique=True, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
