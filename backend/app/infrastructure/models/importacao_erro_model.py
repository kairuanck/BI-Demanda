"""Tabela `importacao_erros` (DICIONARIO_DE_DADOS.md, seção 18)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class ImportacaoErro(Base):
    __tablename__ = "importacao_erros"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="CASCADE"), nullable=False
    )
    numero_linha: Mapped[int] = mapped_column(Integer, nullable=False)
    coluna: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_recebido: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mensagem_erro: Mapped[str] = mapped_column(String(500), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
