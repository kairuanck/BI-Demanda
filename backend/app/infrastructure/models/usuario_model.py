"""Tabela `usuarios` (DICIONARIO_DE_DADOS.md, seção 2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import PerfilUsuario
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(
        SAEnum(PerfilUsuario, native_enum=False, length=20), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    promotor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("promotores.id", ondelete="SET NULL"), unique=True, nullable=True
    )
    supervisor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("supervisores.id", ondelete="SET NULL"), unique=True, nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    ultimo_login_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
