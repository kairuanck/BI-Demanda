// Camada de serviço do Dashboard Executivo (FRONTEND.md, seção 6).
// Toda chamada HTTP ao domínio de dashboard passa exclusivamente por aqui.

import { httpGet } from "./httpClient";
import type {
  DetalhePromotor,
  FiltrosDashboard,
  KpisDashboard,
  OpcoesFiltro,
  PaginaPromotores,
  PontoCategoria,
  PontoPositivacaoMensal,
  PontoRankingPromotor,
  PontoSerieMensal,
  PontoUf,
  UltimaImportacao,
} from "../types/dashboard";

function paramsDeFiltros(filtros: FiltrosDashboard): Record<string, string | number | undefined> {
  return {
    ano: filtros.ano,
    mes: filtros.mes,
    uf: filtros.uf,
    laboratorio_id: filtros.laboratorio_id,
    tipo_promotor_id: filtros.tipo_promotor_id,
    sistema_origem: filtros.sistema_origem,
    supervisor_id: filtros.supervisor_id,
    promotor_id: filtros.promotor_id,
  };
}

export function obterOpcoesFiltro(): Promise<OpcoesFiltro> {
  return httpGet<OpcoesFiltro>("/dashboard/filtros");
}

export function obterKpis(filtros: FiltrosDashboard): Promise<KpisDashboard> {
  return httpGet<KpisDashboard>("/dashboard/kpis", paramsDeFiltros(filtros));
}

export function obterEvolucaoFaturamentoMensal(
  filtros: FiltrosDashboard,
): Promise<PontoSerieMensal[]> {
  return httpGet<PontoSerieMensal[]>(
    "/dashboard/graficos/faturamento-mensal",
    paramsDeFiltros(filtros),
  );
}

export function obterEvolucaoPositivacaoMensal(
  filtros: FiltrosDashboard,
): Promise<PontoPositivacaoMensal[]> {
  return httpGet<PontoPositivacaoMensal[]>(
    "/dashboard/graficos/positivacao-mensal",
    paramsDeFiltros(filtros),
  );
}

export function obterFaturamentoPorLaboratorio(
  filtros: FiltrosDashboard,
): Promise<PontoCategoria[]> {
  return httpGet<PontoCategoria[]>(
    "/dashboard/graficos/faturamento-laboratorio",
    paramsDeFiltros(filtros),
  );
}

export function obterTopPromotores(
  filtros: FiltrosDashboard,
  limite = 10,
): Promise<PontoRankingPromotor[]> {
  return httpGet<PontoRankingPromotor[]>("/dashboard/graficos/top-promotores", {
    ...paramsDeFiltros(filtros),
    limite,
  });
}

export function obterTiposChecklist(filtros: FiltrosDashboard): Promise<PontoCategoria[]> {
  return httpGet<PontoCategoria[]>("/dashboard/graficos/tipos-checklist", paramsDeFiltros(filtros));
}

export function obterDistribuicaoUf(filtros: FiltrosDashboard): Promise<PontoUf[]> {
  return httpGet<PontoUf[]>("/dashboard/graficos/distribuicao-uf", paramsDeFiltros(filtros));
}

export function listarPromotores(
  filtros: FiltrosDashboard,
  pagina: number,
  tamanhoPagina: number,
): Promise<PaginaPromotores> {
  return httpGet<PaginaPromotores>("/dashboard/promotores", {
    ...paramsDeFiltros(filtros),
    pagina,
    tamanho_pagina: tamanhoPagina,
  });
}

export function obterDetalhePromotor(
  promotorId: string,
  filtros: Pick<FiltrosDashboard, "ano" | "mes">,
): Promise<DetalhePromotor> {
  return httpGet<DetalhePromotor>(`/dashboard/promotores/${promotorId}`, {
    ano: filtros.ano,
    mes: filtros.mes,
  });
}

export function listarUltimasImportacoes(): Promise<UltimaImportacao[]> {
  return httpGet<UltimaImportacao[]>("/dashboard/importacoes/ultimas");
}
