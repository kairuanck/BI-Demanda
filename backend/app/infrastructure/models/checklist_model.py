"""Tabela `checklists` (DICIONARIO_DE_DADOS.md, seção 14)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import TipoPromotorAlvo
from app.infrastructure.database import Base


class Checklist(Base):
    __tablename__ = "checklists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo_promotor_alvo: Mapped[TipoPromotorAlvo] = mapped_column(
        SAEnum(TipoPromotorAlvo, native_enum=False, length=20), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
