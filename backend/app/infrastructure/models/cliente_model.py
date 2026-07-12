"""Tabela `clientes` (DICIONARIO_DE_DADOS.md, seção 10).

Sprint 3 — colunas adicionadas para cobrir integralmente as 22 colunas da
Base de Clientes real (regra "nunca descartar colunas"; os RCAs 1..4 vão
para `clientes_vendedores`). `codigo_externo` é identificador de
integração, nunca identidade global (docs/DECISIONS.md, seção 12).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.infrastructure.models.identidade import novo_uuid


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_uuid)
    codigo_externo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    razao_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cnpj_cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    inscricao_estadual: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tipo_pessoa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ramo_atividade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uf_sigla: Mapped[str] = mapped_column(
        String(2), ForeignKey("ufs.sigla", ondelete="RESTRICT"), nullable=False
    )
    cidade_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cidades.id", ondelete="RESTRICT"), nullable=False
    )
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(15), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    canal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_ultima_compra: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
