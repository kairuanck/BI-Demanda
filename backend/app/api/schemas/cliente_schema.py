"""Schemas Pydantic da Visão 360º do Cliente (Sprint 5)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class KpisClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    faturamento_acumulado: Decimal
    faturamento_12_meses: Decimal
    quantidade_laboratorios: int
    quantidade_visitas: int
    quantidade_checklists: int
    dias_desde_ultima_visita: int | None
    cobertura: Decimal
    positivacao: Decimal


class VinculoPromotorClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sistema_origem: str
    promotor_id: str
    nome: str
    tipo: str | None
    supervisor: str | None
    quantidade_clientes_carteira: int
    cobertura: Decimal | None
    faturamento_carteira: Decimal


class DetalheClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    codigo_externo: str
    razao_social: str
    nome_fantasia: str | None
    cidade: str
    uf_sigla: str
    cnpj_cpf: str | None
    ativo: bool
    grupo_economico: str | None
    segmento: str | None
    vinculos: list[VinculoPromotorClienteResponse]
    kpis: KpisClienteResponse


class LinhaLaboratorioClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    laboratorio: str
    primeiro_ano: int
    primeiro_mes: int
    ultimo_ano: int
    ultimo_mes: int
    valor_acumulado: Decimal
    participacao_percentual: Decimal


class EventoTimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: str
    data: datetime
    titulo: str
    descricao: str | None


class PaginaTimelineResponse(BaseModel):
    itens: list[EventoTimelineResponse]
    pagina: int
    tamanho_pagina: int
    total_itens: int
    total_paginas: int


class LinhaClienteBuscaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    codigo_externo: str
    razao_social: str
    nome_fantasia: str | None
    cidade: str
    uf_sigla: str
    ativo: bool


class PaginaClientesBuscaResponse(BaseModel):
    itens: list[LinhaClienteBuscaResponse]
    pagina: int
    tamanho_pagina: int
    total_itens: int
    total_paginas: int
