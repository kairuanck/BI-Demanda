"""Endpoints do Dashboard Executivo (Sprint 4, ver docs/DECISIONS.md, seções 16-19).

Autorização por perfil (PERMISSOES.md) é aplicada na sprint de
autenticação — ver docs/DECISIONS.md.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.schemas.dashboard_schema import (
    DetalhePromotorResponse,
    KpisDashboardResponse,
    LinhaPromotorResponse,
    OpcoesFiltroResponse,
    PaginaPromotoresResponse,
    PontoCategoriaResponse,
    PontoPositivacaoMensalResponse,
    PontoRankingPromotorResponse,
    PontoSerieMensalResponse,
    PontoUfResponse,
    UltimaImportacaoResponse,
)
from app.domain.enums import SistemaOrigem
from app.services.dashboard_service import DashboardService, FiltrosDashboard
from app.services.importacao_service import montar_paginacao

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_service(db: Session = Depends(get_db_session)) -> DashboardService:
    return DashboardService(session=db)


def obter_filtros(
    ano: int | None = None,
    mes: int | None = Query(default=None, ge=1, le=12),
    uf: str | None = None,
    laboratorio_id: str | None = None,
    tipo_promotor_id: str | None = None,
    sistema_origem: SistemaOrigem | None = None,
    supervisor_id: str | None = None,
    promotor_id: str | None = None,
) -> FiltrosDashboard:
    """Filtros globais compartilhados por todos os endpoints (Sprint 4)."""

    return FiltrosDashboard(
        ano=ano,
        mes=mes,
        uf_sigla=uf.upper() if uf else None,
        laboratorio_id=laboratorio_id,
        tipo_promotor_id=tipo_promotor_id,
        sistema_origem=sistema_origem,
        supervisor_id=supervisor_id,
        promotor_id=promotor_id,
    )


@router.get("/filtros", response_model=OpcoesFiltroResponse)
def obter_opcoes_filtro(
    service: DashboardService = Depends(get_dashboard_service),
) -> OpcoesFiltroResponse:
    return OpcoesFiltroResponse.model_validate(service.obter_opcoes_filtro())


@router.get("/kpis", response_model=KpisDashboardResponse)
def obter_kpis(
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> KpisDashboardResponse:
    return KpisDashboardResponse.model_validate(service.calcular_kpis(filtros))


@router.get("/graficos/faturamento-mensal", response_model=list[PontoSerieMensalResponse])
def obter_evolucao_faturamento_mensal(
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> list[PontoSerieMensalResponse]:
    return [
        PontoSerieMensalResponse.model_validate(p)
        for p in service.evolucao_faturamento_mensal(filtros)
    ]


@router.get("/graficos/positivacao-mensal", response_model=list[PontoPositivacaoMensalResponse])
def obter_evolucao_positivacao_mensal(
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> list[PontoPositivacaoMensalResponse]:
    return [
        PontoPositivacaoMensalResponse.model_validate(p)
        for p in service.evolucao_positivacao_mensal(filtros)
    ]


@router.get("/graficos/faturamento-laboratorio", response_model=list[PontoCategoriaResponse])
def obter_faturamento_por_laboratorio(
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> list[PontoCategoriaResponse]:
    return [
        PontoCategoriaResponse.model_validate(p)
        for p in service.faturamento_por_laboratorio(filtros)
    ]


@router.get("/graficos/top-promotores", response_model=list[PontoRankingPromotorResponse])
def obter_top_promotores(
    limite: int = Query(default=10, ge=1, le=50),
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> list[PontoRankingPromotorResponse]:
    return [
        PontoRankingPromotorResponse.model_validate(p)
        for p in service.top_promotores(filtros, limite=limite)
    ]


@router.get("/graficos/tipos-checklist", response_model=list[PontoCategoriaResponse])
def obter_tipos_checklist(
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> list[PontoCategoriaResponse]:
    return [PontoCategoriaResponse.model_validate(p) for p in service.tipos_checklist(filtros)]


@router.get("/graficos/distribuicao-uf", response_model=list[PontoUfResponse])
def obter_distribuicao_uf(
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> list[PontoUfResponse]:
    return [PontoUfResponse.model_validate(p) for p in service.distribuicao_uf(filtros)]


@router.get("/promotores", response_model=PaginaPromotoresResponse)
def listar_promotores(
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=20, ge=1, le=100),
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> PaginaPromotoresResponse:
    resultado = service.listar_promotores(filtros, pagina, tamanho_pagina)
    return PaginaPromotoresResponse(
        itens=[LinhaPromotorResponse.model_validate(p) for p in resultado.itens],
        **montar_paginacao(resultado.total_itens, pagina, tamanho_pagina),
    )


@router.get("/promotores/{promotor_id}", response_model=DetalhePromotorResponse)
def obter_detalhe_promotor(
    promotor_id: str,
    filtros: FiltrosDashboard = Depends(obter_filtros),
    service: DashboardService = Depends(get_dashboard_service),
) -> DetalhePromotorResponse:
    filtros_periodo = FiltrosDashboard(ano=filtros.ano, mes=filtros.mes)
    return DetalhePromotorResponse.model_validate(
        service.obter_detalhe_promotor(promotor_id, filtros_periodo)
    )


@router.get("/importacoes/ultimas", response_model=list[UltimaImportacaoResponse])
def listar_ultimas_importacoes(
    service: DashboardService = Depends(get_dashboard_service),
) -> list[UltimaImportacaoResponse]:
    return [
        UltimaImportacaoResponse.model_validate(i) for i in service.listar_ultimas_importacoes()
    ]
