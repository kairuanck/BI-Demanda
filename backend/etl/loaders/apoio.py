"""Resoluções get-or-create de dimensões usadas pelos loaders (IMPORTADOR.md)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.enums import CategoriaComercial, SistemaOrigem, StatusConciliacao, TipoPromotor
from app.infrastructure.models import (
    Cidade,
    ClienteIntegracao,
    Departamento,
    Laboratorio,
    Promotor,
    Supervisor,
    TipoPromotorCadastro,
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


def resolver_tipo_promotor_id(session: Session, tipo: TipoPromotor | str | None) -> str | None:
    """Resolve o código cadastral em `tipos_promotor.id` (docs/DECISIONS.md, seção 13)."""

    if tipo is None:
        return None
    codigo = tipo.value if isinstance(tipo, TipoPromotor) else str(tipo)
    return session.scalar(
        select(TipoPromotorCadastro.id).where(TipoPromotorCadastro.codigo == codigo)
    )


def obter_ou_criar_promotor(
    session: Session,
    codigo: str,
    nome: str | None,
    tipo: TipoPromotor | None,
    supervisor_id: str | None,
) -> Promotor:
    promotor = session.scalar(select(Promotor).where(Promotor.codigo_externo == codigo))
    if promotor is None:
        # O tipo é cadastral e nunca inferido (docs/DECISIONS.md, seção 12):
        # sem tipo informado pela fonte, o promotor nasce com tipo pendente.
        promotor = Promotor(
            codigo_externo=codigo,
            nome=nome or codigo,
            tipo_promotor_id=resolver_tipo_promotor_id(session, tipo),
            supervisor_id=supervisor_id,
        )
        session.add(promotor)
        session.flush()
    elif supervisor_id is not None and promotor.supervisor_id != supervisor_id:
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


def obter_ou_criar_laboratorio_por_nome(
    session: Session, nome: str, categoria: CategoriaComercial = CategoriaComercial.LABORATORIO
) -> Laboratorio:
    """Marcas da matriz real de faturamento não têm código — identidade por nome."""

    laboratorio = session.scalar(select(Laboratorio).where(Laboratorio.nome == nome))
    if laboratorio is None:
        laboratorio = Laboratorio(nome=nome, categoria=categoria)
        session.add(laboratorio)
        session.flush()
    return laboratorio


def obter_ou_criar_promotor_por_nome(
    session: Session, nome: str, tipo: TipoPromotor | None
) -> Promotor:
    """WeCheck/Painel Avert identificam a promotora apenas pelo nome.

    Busca exata case-insensitive (normalização determinística — casamento
    fuzzy é proibido, docs/DECISIONS.md, 12.4). O tipo só é aplicado na
    criação: é definição cadastral do PO (12.6), nunca sobrescreve cadastro.
    """

    nome_normalizado = " ".join(nome.split())
    promotor = session.scalar(
        select(Promotor).where(func.lower(Promotor.nome) == nome_normalizado.lower())
    )
    if promotor is None:
        promotor = Promotor(
            nome=nome_normalizado,
            tipo_promotor_id=resolver_tipo_promotor_id(session, tipo),
        )
        session.add(promotor)
        session.flush()
    return promotor


def registrar_integracao_cliente(
    session: Session,
    sistema: SistemaOrigem,
    codigo_origem: str,
    nome_origem: str | None,
    importacao_id: str,
    cliente_id: str | None = None,
) -> ClienteIntegracao:
    """Get-or-create do vínculo de identidade externa (docs/DECISIONS.md, 13.4).

    Sem correspondência interna o registro fica PENDENTE — clientes nunca
    são criados automaticamente (12.4/12.5). Se um vínculo é fornecido e o
    registro ainda está pendente, ele é promovido a VINCULADO.
    """

    integracao = session.scalar(
        select(ClienteIntegracao).where(
            ClienteIntegracao.sistema_origem == sistema,
            ClienteIntegracao.codigo_origem == codigo_origem,
        )
    )
    if integracao is None:
        integracao = ClienteIntegracao(
            sistema_origem=sistema,
            codigo_origem=codigo_origem,
            nome_origem=nome_origem,
            cliente_id=cliente_id,
            status=(StatusConciliacao.VINCULADO if cliente_id else StatusConciliacao.PENDENTE),
            importacao_id=importacao_id,
        )
        session.add(integracao)
        session.flush()
    elif cliente_id is not None and integracao.status == StatusConciliacao.PENDENTE:
        integracao.cliente_id = cliente_id
        integracao.status = StatusConciliacao.VINCULADO
        integracao.importacao_id = importacao_id
        session.flush()
    return integracao
