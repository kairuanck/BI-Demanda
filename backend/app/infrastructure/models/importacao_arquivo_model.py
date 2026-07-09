"""Tabela `importacao_arquivos` (DICIONARIO_DE_DADOS.md, seção 19)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ImportacaoArquivo(Base):
    __tablename__ = "importacao_arquivos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    importacao_id: Mapped[int] = mapped_column(
        ForeignKey("importacoes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    caminho_armazenamento: Mapped[str] = mapped_column(String(500), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
