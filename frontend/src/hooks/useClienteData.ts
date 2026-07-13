// Hooks de dados da Visão 360º do Cliente (React Query), Sprint 5.

import { useQuery } from "@tanstack/react-query";

import * as clienteService from "../services/clienteService";
import type { FiltrosCliente } from "../types/cliente";

export function useBuscarClientes(
  termo: string,
  pagina: number,
  tamanhoPagina: number,
  promotorId?: string,
  enabled = true,
) {
  return useQuery({
    queryKey: ["clientes", "busca", termo, pagina, tamanhoPagina, promotorId],
    queryFn: () => clienteService.buscarClientes(termo, pagina, tamanhoPagina, promotorId),
    enabled,
  });
}

export function useDetalheCliente(clienteId: string | undefined, filtros: FiltrosCliente) {
  return useQuery({
    queryKey: ["clientes", "detalhe", clienteId, filtros],
    queryFn: () => clienteService.obterDetalheCliente(clienteId as string, filtros),
    enabled: Boolean(clienteId),
  });
}

export function useEvolucaoFaturamentoCliente(
  clienteId: string | undefined,
  filtros: FiltrosCliente,
) {
  return useQuery({
    queryKey: ["clientes", "evolucao-faturamento", clienteId, filtros],
    queryFn: () => clienteService.obterEvolucaoFaturamentoCliente(clienteId as string, filtros),
    enabled: Boolean(clienteId),
  });
}

export function useFaturamentoPorLaboratorioCliente(
  clienteId: string | undefined,
  filtros: FiltrosCliente,
) {
  return useQuery({
    queryKey: ["clientes", "faturamento-laboratorio", clienteId, filtros],
    queryFn: () =>
      clienteService.obterFaturamentoPorLaboratorioCliente(clienteId as string, filtros),
    enabled: Boolean(clienteId),
  });
}

export function useVisitasPorMesCliente(clienteId: string | undefined, filtros: FiltrosCliente) {
  return useQuery({
    queryKey: ["clientes", "visitas-mensal", clienteId, filtros],
    queryFn: () => clienteService.obterVisitasPorMesCliente(clienteId as string, filtros),
    enabled: Boolean(clienteId),
  });
}

export function useChecklistsPorMesCliente(clienteId: string | undefined, filtros: FiltrosCliente) {
  return useQuery({
    queryKey: ["clientes", "checklists-mensal", clienteId, filtros],
    queryFn: () => clienteService.obterChecklistsPorMesCliente(clienteId as string, filtros),
    enabled: Boolean(clienteId),
  });
}

export function useLaboratoriosCliente(clienteId: string | undefined, filtros: FiltrosCliente) {
  return useQuery({
    queryKey: ["clientes", "laboratorios", clienteId, filtros],
    queryFn: () => clienteService.obterLaboratoriosCliente(clienteId as string, filtros),
    enabled: Boolean(clienteId),
  });
}

export function useTimelineCliente(
  clienteId: string | undefined,
  pagina: number,
  tamanhoPagina: number,
) {
  return useQuery({
    queryKey: ["clientes", "timeline", clienteId, pagina, tamanhoPagina],
    queryFn: () => clienteService.obterTimelineCliente(clienteId as string, pagina, tamanhoPagina),
    enabled: Boolean(clienteId),
  });
}
