"""Tabela `laboratorios` (DICIONARIO_DE_DADOS.md, seção 6).

Sprint 3: as colunas de marca da matriz real de faturamento viram linhas
desta tabela. `categoria` distingue laboratórios de BRINDE, que por
definição de negócio é categoria comercial à parte, não um laboratório
(docs/DECISIONS.md, seção 12).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import CategoriaComercial
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Laboratorio(Base):
    __tablename__ = "laboratorios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    codigo_externo: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    categoria: Mapped[CategoriaComercial] = mapped_column(
        SAEnum(CategoriaComercial, native_enum=False, length=20),
        default=CategoriaComercial.LABORATORIO,
        server_default=CategoriaComercial.LABORATORIO.value,
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
