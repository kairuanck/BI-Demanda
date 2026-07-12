"""Tabela `importacoes` (DICIONARIO_DE_DADOS.md, seção 17).

Sprint 3 — duas colunas novas exigidas pelos dados reais
(docs/DECISIONS.md, seções 11 e 13):
- `hash_conteudo`: hash SHA-256 do conteúdo lógico das células. Os exports
  reais chegam em dezenas de cópias byte a byte distintas (metadados
  internos do xlsx) porém idênticas em conteúdo — o hash binário sozinho
  não detecta essas duplicatas.
- `competencia`: mês de referência dos dados (1º dia do mês). Fontes
  mensais reais não trazem o período dentro do arquivo.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Importacao(Base):
    __tablename__ = "importacoes"
    __table_args__ = (
        Index("ix_importacoes_hash", "hash_sha256"),
        Index("ix_importacoes_hash_conteudo", "hash_conteudo"),
        Index("ix_importacoes_tipo_versao", "tipo_arquivo", "versao"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    tipo_arquivo: Mapped[TipoArquivoImportacao] = mapped_column(
        SAEnum(TipoArquivoImportacao, native_enum=False, length=20), nullable=False
    )
    nome_arquivo_original: Mapped[str] = mapped_column(String(255), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    hash_conteudo: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    competencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[StatusImportacao] = mapped_column(
        SAEnum(StatusImportacao, native_enum=False, length=25),
        default=StatusImportacao.PENDENTE,
        nullable=False,
    )
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    importacao_pai_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("importacoes.id", ondelete="SET NULL"), nullable=True
    )
    total_linhas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linhas_validas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linhas_invalidas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    iniciado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
