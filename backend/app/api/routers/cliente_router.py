"""Endpoints da Visão 360º do Cliente (Sprint 5, ver docs/DECISIONS.md, seção 22).

Autorização por perfil (PERMISSOES.md) é aplicada na sprint de
autenticação — ver docs/DECISIONS.md.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.schemas.cliente_schema import (
    DetalheClienteResponse,
    EventoTimelineResponse,
    LinhaClienteBuscaResponse,
    LinhaLaboratorioClienteResponse,
    PaginaClientesBuscaResponse,
    PaginaTimelineResponse,
)
from app.api.schemas.dashboard_schema import PontoCategoriaResponse, PontoSerieMensalResponse
from app.domain.enums import SistemaOrigem
from app.services.cliente_service import ClienteService, FiltrosCliente
from app.services.importacao_service import montar_paginacao

router = APIRouter(prefix="/clientes", tags=["clientes"])


def get_cliente_service(db: Session = Depends(get_db_session)) -> ClienteService:
    return ClienteService(session=db)


def obter_filtros_cliente(
    ano: int | None = None,
    mes: int | None = Query(default=None, ge=1, le=12),
    laboratorio_id: str | None = None,
    sistema_origem: SistemaOrigem | None = None,
) -> FiltrosCliente:
    """Filtros da Visão 360 compartilhados pelos endpoints de um cliente (Sprint 5)."""

    return FiltrosCliente(
        ano=ano, mes=mes, laboratorio_id=laboratorio_id, sistema_origem=sistema_origem
    )


@router.get("", response_model=PaginaClientesBuscaResponse)
def buscar_clientes(
    q: str = "",
    promotor_id: str | None = None,
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=20, ge=1, le=100),
    service: ClienteService = Depends(get_cliente_service),
) -> PaginaClientesBuscaResponse:
    resultado = service.buscar_clientes(q, pagina, tamanho_pagina, promotor_id=promotor_id)
    return PaginaClientesBuscaResponse(
        itens=[LinhaClienteBuscaResponse.model_validate(item) for item in resultado.itens],
        **montar_paginacao(resultado.total_itens, pagina, tamanho_pagina),
    )


@router.get("/{cliente_id}", response_model=DetalheClienteResponse)
def obter_detalhe_cliente(
    cliente_id: str,
    filtros: FiltrosCliente = Depends(obter_filtros_cliente),
    service: ClienteService = Depends(get_cliente_service),
) -> DetalheClienteResponse:
    return DetalheClienteResponse.model_validate(service.obter_detalhe_cliente(cliente_id, filtros))


@router.get(
    "/{cliente_id}/graficos/faturamento-mensal", response_model=list[PontoSerieMensalResponse]
)
def obter_evolucao_faturamento_cliente(
    cliente_id: str,
    filtros: FiltrosCliente = Depends(obter_filtros_cliente),
    service: ClienteService = Depends(get_cliente_service),
) -> list[PontoSerieMensalResponse]:
    return [
        PontoSerieMensalResponse.model_validate(p)
        for p in service.evolucao_faturamento_cliente(cliente_id, filtros)
    ]


@router.get(
    "/{cliente_id}/graficos/faturamento-laboratorio", response_model=list[PontoCategoriaResponse]
)
def obter_faturamento_por_laboratorio_cliente(
    cliente_id: str,
    filtros: FiltrosCliente = Depends(obter_filtros_cliente),
    service: ClienteService = Depends(get_cliente_service),
) -> list[PontoCategoriaResponse]:
    return [
        PontoCategoriaResponse.model_validate(p)
        for p in service.faturamento_por_laboratorio_cliente(cliente_id, filtros)
    ]


@router.get("/{cliente_id}/graficos/visitas-mensal", response_model=list[PontoSerieMensalResponse])
def obter_visitas_por_mes_cliente(
    cliente_id: str,
    filtros: FiltrosCliente = Depends(obter_filtros_cliente),
    service: ClienteService = Depends(get_cliente_service),
) -> list[PontoSerieMensalResponse]:
    return [
        PontoSerieMensalResponse.model_validate(p)
        for p in service.visitas_por_mes_cliente(cliente_id, filtros)
    ]


@router.get(
    "/{cliente_id}/graficos/checklists-mensal", response_model=list[PontoSerieMensalResponse]
)
def obter_checklists_por_mes_cliente(
    cliente_id: str,
    filtros: FiltrosCliente = Depends(obter_filtros_cliente),
    service: ClienteService = Depends(get_cliente_service),
) -> list[PontoSerieMensalResponse]:
    return [
        PontoSerieMensalResponse.model_validate(p)
        for p in service.checklists_por_mes_cliente(cliente_id, filtros)
    ]


@router.get("/{cliente_id}/laboratorios", response_model=list[LinhaLaboratorioClienteResponse])
def obter_laboratorios_cliente(
    cliente_id: str,
    filtros: FiltrosCliente = Depends(obter_filtros_cliente),
    service: ClienteService = Depends(get_cliente_service),
) -> list[LinhaLaboratorioClienteResponse]:
    return [
        LinhaLaboratorioClienteResponse.model_validate(p)
        for p in service.laboratorios_cliente(cliente_id, filtros)
    ]


@router.get("/{cliente_id}/timeline", response_model=PaginaTimelineResponse)
def obter_timeline_cliente(
    cliente_id: str,
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=20, ge=1, le=100),
    service: ClienteService = Depends(get_cliente_service),
) -> PaginaTimelineResponse:
    resultado = service.timeline_cliente(cliente_id, pagina, tamanho_pagina)
    return PaginaTimelineResponse(
        itens=[EventoTimelineResponse.model_validate(item) for item in resultado.itens],
        **montar_paginacao(resultado.total_itens, pagina, tamanho_pagina),
    )
