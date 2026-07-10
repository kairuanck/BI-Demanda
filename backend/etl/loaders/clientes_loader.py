"""Loader da Base de Clientes — upsert por codigo_externo (REGRAS_DE_NEGOCIO.md, seção 5.1)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import AcaoAuditoria
from app.infrastructure.models import Cliente, LogAuditoria
from etl.loaders.apoio import obter_ou_criar_cidade
from etl.resultado import LinhaValida

_CAMPOS_CADASTRAIS = ("razao_social", "nome_fantasia", "cnpj_cpf", "uf_sigla", "endereco", "canal")


def carregar_clientes(
    session: Session, linhas: list[LinhaValida], importacao_id: int, usuario_id: int
) -> int:
    persistidas = 0
    for linha in linhas:
        dados = linha.dados
        cidade = obter_ou_criar_cidade(session, dados["cidade_nome"], dados["uf_sigla"])
        cliente = session.scalar(
            select(Cliente).where(Cliente.codigo_externo == dados["codigo_externo"])
        )

        if cliente is None:
            cliente = Cliente(
                codigo_externo=dados["codigo_externo"],
                razao_social=dados["razao_social"],
                nome_fantasia=dados["nome_fantasia"],
                cnpj_cpf=dados["cnpj_cpf"],
                uf_sigla=dados["uf_sigla"],
                cidade_id=cidade.id,
                endereco=dados["endereco"],
                canal=dados["canal"],
            )
            session.add(cliente)
            session.flush()
            session.add(
                LogAuditoria(
                    entidade="clientes",
                    entidade_id=cliente.id,
                    acao=AcaoAuditoria.CRIACAO,
                    usuario_id=usuario_id,
                    dados_depois={
                        "codigo_externo": cliente.codigo_externo,
                        "importacao_id": importacao_id,
                    },
                )
            )
        else:
            antes: dict[str, Any] = {}
            depois: dict[str, Any] = {}
            novos_valores = {campo: dados[campo] for campo in _CAMPOS_CADASTRAIS}
            novos_valores["cidade_id"] = cidade.id
            for campo, novo_valor in novos_valores.items():
                valor_atual = getattr(cliente, campo)
                if valor_atual != novo_valor:
                    antes[campo] = valor_atual
                    depois[campo] = novo_valor
                    setattr(cliente, campo, novo_valor)
            if depois:
                depois["importacao_id"] = importacao_id
                session.add(
                    LogAuditoria(
                        entidade="clientes",
                        entidade_id=cliente.id,
                        acao=AcaoAuditoria.ATUALIZACAO,
                        usuario_id=usuario_id,
                        dados_antes=antes,
                        dados_depois=depois,
                    )
                )
        persistidas += 1
    return persistidas
