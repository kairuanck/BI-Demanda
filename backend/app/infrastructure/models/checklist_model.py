"""Tabela `checklists` (DICIONARIO_DE_DADOS.md, seção 14).

Sprint 3: templates passam a ser criados também por importação —
`codigo_externo` guarda o CK_ID do export de checklists e `origem`
identifica o sistema que definiu o template (formulários WeCheck também
são templates). `tipo_promotor_alvo` aceita nulo: as fontes reais não
informam o público-alvo e ele não pode ser inferido (docs/DECISIONS.md,
seção 12).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import SistemaOrigem, TipoPromotorAlvo
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Checklist(Base):
    __tablename__ = "checklists"
    __table_args__ = (
        UniqueConstraint("origem", "codigo_externo", name="uq_checklists_origem_codigo"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo_externo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    origem: Mapped[SistemaOrigem | None] = mapped_column(
        SAEnum(SistemaOrigem, native_enum=False, length=20), nullable=True
    )
    tipo_promotor_alvo: Mapped[TipoPromotorAlvo | None] = mapped_column(
        SAEnum(TipoPromotorAlvo, native_enum=False, length=20), nullable=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
