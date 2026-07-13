"""Tabela `carteiras` (DICIONARIO_DE_DADOS.md, seção 11).

Sprint 3: a carteira mensal oficial vem do relatório Supervisor do SB
Promotor (docs/DECISIONS.md, seção 12); `competencia` registra o mês de
referência informado na importação.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import StatusCarteira
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Carteira(Base):
    __tablename__ = "carteiras"
    __table_args__ = (
        Index("ix_carteiras_cliente_vigencia", "cliente_id", "data_fim_vigencia"),
        Index("ix_carteiras_promotor", "promotor_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    promotor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("promotores.id", ondelete="RESTRICT"), nullable=False
    )
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    data_inicio_vigencia: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim_vigencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    competencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[StatusCarteira] = mapped_column(
        SAEnum(StatusCarteira, native_enum=False, length=15),
        default=StatusCarteira.ATIVA,
        nullable=False,
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
