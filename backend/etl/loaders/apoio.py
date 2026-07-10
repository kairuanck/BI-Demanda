"""Resoluções get-or-create de dimensões usadas pelos loaders (IMPORTADOR.md)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TipoPromotor
from app.infrastructure.models import (
    Cidade,
    Departamento,
    Laboratorio,
    Promotor,
    Supervisor,
    Vendedor,
)


def obter_ou_criar_cidade(session: Session, nome: str, uf_sigla: str) -> Cidade:
    cidade = session.scalar(select(Cidade).where(Cidade.nome == nome, Cidade.uf_sigla == uf_sigla))
    if cidade is None:
        cidade = Cidade(nome=nome, uf_sigla=uf_sigla)
        session.add(cidade)
        session.flush()
    return cidade


def obter_ou_criar_supervisor(session: Session, codigo: str, nome: str | None) -> Supervisor:
    supervisor = session.scalar(select(Supervisor).where(Supervisor.codigo_externo == codigo))
    if supervisor is None:
        supervisor = Supervisor(codigo_externo=codigo, nome=nome or codigo)
        session.add(supervisor)
        session.flush()
    return supervisor


def obter_ou_criar_promotor(
    session: Session,
    codigo: str,
    nome: str | None,
    tipo: TipoPromotor | None,
    supervisor_id: int,
) -> Promotor:
    promotor = session.scalar(select(Promotor).where(Promotor.codigo_externo == codigo))
    if promotor is None:
        # nome/tipo garantidos pelo validador quando o promotor é inédito
        promotor = Promotor(
            codigo_externo=codigo,
            nome=nome or codigo,
            tipo=tipo or TipoPromotor.TRADE,
            supervisor_id=supervisor_id,
        )
        session.add(promotor)
        session.flush()
    elif promotor.supervisor_id != supervisor_id:
        # Mudança de supervisão é atualização cadastral direta
        # (IMPORTADOR.md, seção 4.2, item 3)
        promotor.supervisor_id = supervisor_id
        session.flush()
    return promotor


def obter_ou_criar_laboratorio(session: Session, codigo: str, nome: str | None) -> Laboratorio:
    laboratorio = session.scalar(select(Laboratorio).where(Laboratorio.codigo_externo == codigo))
    if laboratorio is None:
        laboratorio = Laboratorio(codigo_externo=codigo, nome=nome or codigo)
        session.add(laboratorio)
        session.flush()
    return laboratorio


def obter_ou_criar_departamento(session: Session, codigo: str, nome: str | None) -> Departamento:
    departamento = session.scalar(select(Departamento).where(Departamento.codigo_externo == codigo))
    if departamento is None:
        departamento = Departamento(codigo_externo=codigo, nome=nome or codigo)
        session.add(departamento)
        session.flush()
    return departamento


def obter_ou_criar_vendedor(session: Session, codigo: str, nome: str | None) -> Vendedor:
    vendedor = session.scalar(select(Vendedor).where(Vendedor.codigo_externo == codigo))
    if vendedor is None:
        vendedor = Vendedor(codigo_externo=codigo, nome=nome or codigo)
        session.add(vendedor)
        session.flush()
    return vendedor
