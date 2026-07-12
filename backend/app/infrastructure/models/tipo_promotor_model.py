"""Tabela `tipos_promotor` (Sprint 3, docs/DECISIONS.md, seção 13).

O tipo do promotor (Técnico/Trade) é informação cadastral — nunca inferida
dos dados importados (definição de negócio, seção 12). Uma tabela em vez de
enum embutido permite gerir tipos sem alteração de código; os códigos
canônicos atuais estão no enum `TipoPromotor` (seed da migração).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class TipoPromotorCadastro(Base):
    __tablename__ = "tipos_promotor"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
