"""Tabela `clientes_integracao` (Sprint 3, docs/DECISIONS.md, seções 12–13).

Tabela de conciliação de identidades externas: cada sistema de origem
identifica o cliente à sua maneira (código, CNPJ ou apenas texto livre no
WeCheck). O vínculo com o cliente interno é manual/futuro — registros sem
correspondência ficam PENDENTES e **nunca** geram cliente automaticamente
(definição de negócio, seção 12).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import SistemaOrigem, StatusConciliacao
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class ClienteIntegracao(Base):
    __tablename__ = "clientes_integracao"
    __table_args__ = (
        UniqueConstraint(
            "sistema_origem", "codigo_origem", name="uq_clientes_integracao_origem_codigo"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    sistema_origem: Mapped[SistemaOrigem] = mapped_column(
        SAEnum(SistemaOrigem, native_enum=False, length=20), nullable=False
    )
    codigo_origem: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_origem: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cliente_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[StatusConciliacao] = mapped_column(
        SAEnum(StatusConciliacao, native_enum=False, length=15),
        default=StatusConciliacao.PENDENTE,
        nullable=False,
    )
    observacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    importacao_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="SET NULL"), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
