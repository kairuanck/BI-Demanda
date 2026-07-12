"""Loader de Visitas — inserção pura por linha (REGRAS_DE_NEGOCIO.md, seção 5.5)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import Cliente, Promotor, Visita
from etl.resultado import LinhaValida


def carregar_visitas(
    session: Session, linhas: list[LinhaValida], importacao_id: str, usuario_id: str
) -> int:
    persistidas = 0
    for linha in linhas:
        dados = linha.dados
        promotor_id = session.scalar(
            select(Promotor.id).where(Promotor.codigo_externo == dados["codigo_promotor"])
        )
        cliente_id = session.scalar(
            select(Cliente.id).where(Cliente.codigo_externo == dados["codigo_cliente"])
        )
        if promotor_id is None or cliente_id is None:  # garantido pelo validador
            continue

        session.add(
            Visita(
                promotor_id=promotor_id,
                cliente_id=cliente_id,
                data_visita=dados["data_visita"],
                hora_inicio=dados["hora_inicio"],
                hora_fim=dados["hora_fim"],
                tipo_visita=dados["tipo_visita"],
                latitude=dados["latitude"],
                longitude=dados["longitude"],
                observacoes=dados["observacoes"],
                status=dados["status"],
                importacao_id=importacao_id,
            )
        )
        persistidas += 1
    return persistidas
