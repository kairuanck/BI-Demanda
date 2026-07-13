// Hooks de dados do Dashboard Executivo (React Query), um por bloco da tela
// (DASHBOARD.md). Cada alteração de filtro recalcula a `queryKey` e dispara
// nova busca automaticamente.

import { useQuery } from "@tanstack/react-query";

import * as dashboardService from "../services/dashboardService";
import type { FiltrosDashboard } from "../types/dashboard";

export function useOpcoesFiltro() {
  return useQuery({
    queryKey: ["dashboard", "filtros"],
    queryFn: dashboardService.obterOpcoesFiltro,
    staleTime: 5 * 60 * 1000,
  });
}

export function useKpis(filtros: FiltrosDashboard) {
  return useQuery({
    queryKey: ["dashboard", "kpis", filtros],
    queryFn: () => dashboardService.obterKpis(filtros),
  });
}

export function useEvolucaoFaturamentoMensal(filtros: FiltrosDashboard) {
  return useQuery({
    queryKey: ["dashboard", "evolucao-faturamento", filtros],
    queryFn: () => dashboardService.obterEvolucaoFaturamentoMensal(filtros),
  });
}

export function useEvolucaoPositivacaoMensal(filtros: FiltrosDashboard) {
  return useQuery({
    queryKey: ["dashboard", "evolucao-positivacao", filtros],
    queryFn: () => dashboardService.obterEvolucaoPositivacaoMensal(filtros),
  });
}

export function useFaturamentoPorLaboratorio(filtros: FiltrosDashboard) {
  return useQuery({
    queryKey: ["dashboard", "faturamento-laboratorio", filtros],
    queryFn: () => dashboardService.obterFaturamentoPorLaboratorio(filtros),
  });
}

export function useTopPromotores(filtros: FiltrosDashboard, limite = 10) {
  return useQuery({
    queryKey: ["dashboard", "top-promotores", filtros, limite],
    queryFn: () => dashboardService.obterTopPromotores(filtros, limite),
  });
}

export function useTiposChecklist(filtros: FiltrosDashboard) {
  return useQuery({
    queryKey: ["dashboard", "tipos-checklist", filtros],
    queryFn: () => dashboardService.obterTiposChecklist(filtros),
  });
}

export function useDistribuicaoUf(filtros: FiltrosDashboard) {
  return useQuery({
    queryKey: ["dashboard", "distribuicao-uf", filtros],
    queryFn: () => dashboardService.obterDistribuicaoUf(filtros),
  });
}

export function usePromotores(filtros: FiltrosDashboard, pagina: number, tamanhoPagina: number) {
  return useQuery({
    queryKey: ["dashboard", "promotores", filtros, pagina, tamanhoPagina],
    queryFn: () => dashboardService.listarPromotores(filtros, pagina, tamanhoPagina),
  });
}

export function useDetalhePromotor(
  promotorId: string | undefined,
  filtros: Pick<FiltrosDashboard, "ano" | "mes">,
) {
  return useQuery({
    queryKey: ["dashboard", "promotor-detalhe", promotorId, filtros],
    queryFn: () => dashboardService.obterDetalhePromotor(promotorId as string, filtros),
    enabled: Boolean(promotorId),
  });
}

export function useUltimasImportacoes() {
  return useQuery({
    queryKey: ["dashboard", "ultimas-importacoes"],
    queryFn: dashboardService.listarUltimasImportacoes,
  });
}
