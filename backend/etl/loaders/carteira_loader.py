"""Loader da Carteira — versionamento de vigência (REGRAS_DE_NEGOCIO.md, seção 5.2).

Nunca sobrescreve vínculos: encerra a vigência anterior e cria um novo
registro quando o promotor de um cliente muda; encerra vínculos vigentes
de clientes ausentes no novo arquivo.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import StatusCarteira
from app.infrastructure.models import Carteira, Cliente
from etl.loaders.apoio import obter_ou_criar_promotor, obter_ou_criar_supervisor
from etl.resultado import LinhaValida


def _vinculo_vigente(session: Session, cliente_id: int) -> Carteira | None:
    return session.scalar(
        select(Carteira).where(
            Carteira.cliente_id == cliente_id,
            Carteira.data_fim_vigencia.is_(None),
            Carteira.status == StatusCarteira.ATIVA,
        )
    )


def carregar_carteira(
    session: Session, linhas: list[LinhaValida], importacao_id: int, usuario_id: int
) -> int:
    persistidas = 0
    clientes_no_arquivo: set[int] = set()
    data_referencia_arquivo = None

    for linha in linhas:
        dados = linha.dados
        data_referencia = dados["data_referencia"]
        data_referencia_arquivo = data_referencia_arquivo or data_referencia

        cliente_id = session.scalar(
            select(Cliente.id).where(Cliente.codigo_externo == dados["codigo_cliente"])
        )
        if cliente_id is None:  # garantido pelo validador; defesa extra
            continue
        clientes_no_arquivo.add(cliente_id)

        supervisor = obter_ou_criar_supervisor(
            session, dados["codigo_supervisor"], dados["nome_supervisor"]
        )
        promotor = obter_ou_criar_promotor(
            session,
            dados["codigo_promotor"],
            dados["nome_promotor"],
            dados["tipo_promotor"],
            supervisor.id,
        )

        vigente = _vinculo_vigente(session, cliente_id)
        if vigente is not None and vigente.promotor_id == promotor.id:
            # Idempotência: mesmo promotor, nenhuma alteração (5.2, item 2)
            persistidas += 1
            continue
        if vigente is not None:
            vigente.data_fim_vigencia = data_referencia
            vigente.status = StatusCarteira.ENCERRADA

        session.add(
            Carteira(
                promotor_id=promotor.id,
                cliente_id=cliente_id,
                importacao_id=importacao_id,
                data_inicio_vigencia=data_referencia,
                status=StatusCarteira.ATIVA,
            )
        )
        persistidas += 1

    # 5.2, item 3: clientes com vínculo vigente ausentes no arquivo são encerrados
    if data_referencia_arquivo is not None:
        vigentes = session.scalars(
            select(Carteira).where(
                Carteira.data_fim_vigencia.is_(None),
                Carteira.status == StatusCarteira.ATIVA,
            )
        ).all()
        for vinculo in vigentes:
            if vinculo.cliente_id not in clientes_no_arquivo:
                vinculo.data_fim_vigencia = data_referencia_arquivo
                vinculo.status = StatusCarteira.ENCERRADA

    return persistidas
