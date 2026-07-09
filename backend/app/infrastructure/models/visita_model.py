"""Tabela `visitas` (DICIONARIO_DE_DADOS.md, seção 13)."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text, Time, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import StatusVisita
from app.infrastructure.database import Base


class Visita(Base):
    __tablename__ = "visitas"
    __table_args__ = (Index("ix_visitas_promotor_data", "promotor_id", "data_visita"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    promotor_id: Mapped[int] = mapped_column(
        ForeignKey("promotores.id", ondelete="RESTRICT"), nullable=False
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    data_visita: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_fim: Mapped[time | None] = mapped_column(Time, nullable=True)
    tipo_visita: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusVisita] = mapped_column(
        SAEnum(StatusVisita, native_enum=False, length=15),
        default=StatusVisita.REALIZADA,
        nullable=False,
    )
    importacao_id: Mapped[int] = mapped_column(
        ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
