"""Tabela `promotores` (DICIONARIO_DE_DADOS.md, seção 4)."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import TipoPromotor
from app.infrastructure.database import Base


class Promotor(Base):
    __tablename__ = "promotores"
    __table_args__ = (Index("ix_promotores_tipo", "tipo"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo_externo: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    tipo: Mapped[TipoPromotor] = mapped_column(
        SAEnum(TipoPromotor, native_enum=False, length=20), nullable=False
    )
    supervisor_id: Mapped[int] = mapped_column(
        ForeignKey("supervisores.id", ondelete="RESTRICT"), nullable=False
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_admissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
