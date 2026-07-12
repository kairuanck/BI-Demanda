"""Tabela `visitas` (DICIONARIO_DE_DADOS.md, seção 13).

Sprint 3 — a visita é a entidade unificada das duas origens reais
(Strategy Pattern, docs/DECISIONS.md, seções 11–13):
- SB Promotor/Checklist: 1 aplicação de checklist = 1 visita
  (`codigo_externo` = id VISITA do export, `origem` = SB_PROMOTOR).
- WeCheck: 1 resposta de formulário = 1 visita (`origem` = WECHECK);
  não há código de cliente — `cliente_id` fica nulo e o vínculo pendente
  vive em `clientes_integracao` (`cliente_integracao_id`).
Campos `*_texto` preservam a localização textual do WeCheck e
`dados_brutos` guarda o contexto integral da linha de origem
(regra "nunca descartar colunas").
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import SistemaOrigem, StatusVisita
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Visita(Base):
    __tablename__ = "visitas"
    __table_args__ = (
        Index("ix_visitas_promotor_data", "promotor_id", "data_visita"),
        UniqueConstraint("origem", "codigo_externo", name="uq_visitas_origem_codigo"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    origem: Mapped[SistemaOrigem] = mapped_column(
        SAEnum(SistemaOrigem, native_enum=False, length=20),
        default=SistemaOrigem.SB_PROMOTOR,
        server_default=SistemaOrigem.SB_PROMOTOR.value,
        nullable=False,
    )
    codigo_externo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    promotor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("promotores.id", ondelete="RESTRICT"), nullable=False
    )
    cliente_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=True
    )
    cliente_integracao_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clientes_integracao.id", ondelete="SET NULL"), nullable=True
    )
    data_visita: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_fim: Mapped[time | None] = mapped_column(Time, nullable=True)
    tipo_visita: Mapped[str | None] = mapped_column(String(50), nullable=True)
    local_texto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco_texto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cidade_texto: Mapped[str | None] = mapped_column(String(150), nullable=True)
    estado_texto: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_brutos: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[StatusVisita] = mapped_column(
        SAEnum(StatusVisita, native_enum=False, length=15),
        default=StatusVisita.REALIZADA,
        nullable=False,
    )
    importacao_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="RESTRICT"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
