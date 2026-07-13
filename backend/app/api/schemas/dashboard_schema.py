"""Schemas Pydantic do Dashboard Executivo (Sprint 4)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, computed_field

from app.domain.enums import StatusImportacao, TipoArquivoImportacao


class OpcaoFiltroResponse(BaseModel):
    id: str
    nome: str


class OpcaoUfResponse(BaseModel):
    sigla: str
    nome: str


class OpcoesFiltroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    anos: list[int]
    ufs: list[OpcaoUfResponse]
    laboratorios: list[OpcaoFiltroResponse]
    tipos_promotor: list[OpcaoFiltroResponse]
    sistemas_origem: list[str]
    supervisores: list[OpcaoFiltroResponse]
    promotores: list[OpcaoFiltroResponse]


class KpisDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    faturamento_total: Decimal
    faturamento_carteira: Decimal
    faturamento_regiao: Decimal | None
    faturamento_fora_carteira: Decimal | None
    quantidade_clientes: int
    clientes_positivados: int
    cobertura_carteira: Decimal | None
    numero_visitas: int
    numero_checklists: int


class PontoSerieMensalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ano: int
    mes: int
    valor: Decimal


class PontoPositivacaoMensalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ano: int
    mes: int
    clientes_positivados_carteira: int
    clientes_positivados_regiao: int
    clientes_positivados_fora_carteira: int


class PontoCategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rotulo: str
    valor: Decimal


class PontoRankingPromotorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    promotor_id: str
    nome: str
    indice_desempenho: Decimal | None
    cobertura: Decimal | None
    positivacao: Decimal | None


class PontoUfResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uf_sigla: str
    faturamento_total: Decimal
    quantidade_clientes: int


class LinhaPromotorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    promotor_id: str
    nome: str
    tipo: str | None
    supervisor: str | None
    sistema_origem: str | None
    quantidade_clientes: int
    numero_visitas: int
    numero_checklists: int
    cobertura_carteira: Decimal | None
    faturamento_carteira: Decimal
    faturamento_regiao: Decimal


class PaginaPromotoresResponse(BaseModel):
    itens: list[LinhaPromotorResponse]
    pagina: int
    tamanho_pagina: int
    total_itens: int
    total_paginas: int


class DetalhePromotorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    promotor_id: str
    nome: str
    tipo: str | None
    supervisor: str | None
    codigo_externo: str | None
    area: str | None
    kpis: KpisDashboardResponse
    conformidade_checklist: Decimal | None
    indice_desempenho: Decimal | None
    evolucao_faturamento: list[PontoSerieMensalResponse]
    faturamento_por_laboratorio: list[PontoCategoriaResponse]


class UltimaImportacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo_arquivo: TipoArquivoImportacao
    nome_arquivo_original: str
    status: StatusImportacao
    total_linhas: int
    linhas_validas: int
    linhas_invalidas: int
    iniciado_em: datetime | None
    concluido_em: datetime | None
    criado_em: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duracao_segundos(self) -> float | None:
        if self.iniciado_em and self.concluido_em:
            return (self.concluido_em - self.iniciado_em).total_seconds()
        return None
