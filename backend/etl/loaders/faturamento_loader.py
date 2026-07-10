"""Loader do Faturamento — inserção pura, nunca atualiza (REGRAS_DE_NEGOCIO.md, seção 5.3)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import Cliente, Faturamento
from etl.loaders.apoio import (
    obter_ou_criar_departamento,
    obter_ou_criar_laboratorio,
    obter_ou_criar_vendedor,
)
from etl.resultado import LinhaValida


def carregar_faturamento(
    session: Session, linhas: list[LinhaValida], importacao_id: int, usuario_id: int
) -> int:
    persistidas = 0
    for linha in linhas:
        dados = linha.dados
        cliente_id = session.scalar(
            select(Cliente.id).where(Cliente.codigo_externo == dados["codigo_cliente"])
        )
        if cliente_id is None:  # garantido pelo validador; defesa extra
            continue

        laboratorio = obter_ou_criar_laboratorio(
            session, dados["codigo_laboratorio"], dados["nome_laboratorio"]
        )
        departamento = obter_ou_criar_departamento(
            session, dados["codigo_departamento"], dados["nome_departamento"]
        )
        vendedor_id = None
        if dados["codigo_vendedor"]:
            vendedor_id = obter_ou_criar_vendedor(
                session, dados["codigo_vendedor"], dados["nome_vendedor"]
            ).id

        session.add(
            Faturamento(
                cliente_id=cliente_id,
                laboratorio_id=laboratorio.id,
                departamento_id=departamento.id,
                vendedor_id=vendedor_id,
                ano=dados["ano"],
                mes=dados["mes"],
                valor_faturado=dados["valor_faturado"],
                quantidade=dados["quantidade"],
                importacao_id=importacao_id,
            )
        )
        persistidas += 1
    return persistidas
