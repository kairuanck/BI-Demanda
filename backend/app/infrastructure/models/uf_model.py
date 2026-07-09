"""Tabela `ufs` (DICIONARIO_DE_DADOS.md, seção 8)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Uf(Base):
    __tablename__ = "ufs"

    sigla: Mapped[str] = mapped_column(String(2), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    regiao: Mapped[str] = mapped_column(String(20), nullable=False)
