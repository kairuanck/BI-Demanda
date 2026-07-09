"""Tabela `importacoes` (DICIONARIO_DE_DADOS.md, seção 17)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.infrastructure.database import Base


class Importacao(Base):
    __tablename__ = "importacoes"
    __table_args__ = (
        Index("ix_importacoes_hash", "hash_sha256"),
        Index("ix_importacoes_tipo_versao", "tipo_arquivo", "versao"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_arquivo: Mapped[TipoArquivoImportacao] = mapped_column(
        SAEnum(TipoArquivoImportacao, native_enum=False, length=20), nullable=False
    )
    nome_arquivo_original: Mapped[str] = mapped_column(String(255), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[StatusImportacao] = mapped_column(
        SAEnum(StatusImportacao, native_enum=False, length=25),
        default=StatusImportacao.PENDENTE,
        nullable=False,
    )
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    importacao_pai_id: Mapped[int | None] = mapped_column(
        ForeignKey("importacoes.id", ondelete="SET NULL"), nullable=True
    )
    total_linhas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linhas_validas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linhas_invalidas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    iniciado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
