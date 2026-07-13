// Camada de serviço da Visão 360º do Cliente (FRONTEND.md, seção 6).

import { httpGet } from "./httpClient";
import type {
  DetalheCliente,
  FiltrosCliente,
  LinhaLaboratorioCliente,
  PaginaClientesBusca,
  PaginaTimeline,
} from "../types/cliente";
import type { PontoCategoria, PontoSerieMensal } from "../types/dashboard";

function paramsDeFiltros(filtros: FiltrosCliente): Record<string, string | number | undefined> {
  return {
    ano: filtros.ano,
    mes: filtros.mes,
    laboratorio_id: filtros.laboratorio_id,
    sistema_origem: filtros.sistema_origem,
  };
}

export function buscarClientes(
  termo: string,
  pagina: number,
  tamanhoPagina: number,
  promotorId?: string,
): Promise<PaginaClientesBusca> {
  return httpGet<PaginaClientesBusca>("/clientes", {
    q: termo,
    promotor_id: promotorId,
    pagina,
    tamanho_pagina: tamanhoPagina,
  });
}

export function obterDetalheCliente(
  clienteId: string,
  filtros: FiltrosCliente,
): Promise<DetalheCliente> {
  return httpGet<DetalheCliente>(`/clientes/${clienteId}`, paramsDeFiltros(filtros));
}

export function obterEvolucaoFaturamentoCliente(
  clienteId: string,
  filtros: FiltrosCliente,
): Promise<PontoSerieMensal[]> {
  return httpGet<PontoSerieMensal[]>(
    `/clientes/${clienteId}/graficos/faturamento-mensal`,
    paramsDeFiltros(filtros),
  );
}

export function obterFaturamentoPorLaboratorioCliente(
  clienteId: string,
  filtros: FiltrosCliente,
): Promise<PontoCategoria[]> {
  return httpGet<PontoCategoria[]>(
    `/clientes/${clienteId}/graficos/faturamento-laboratorio`,
    paramsDeFiltros(filtros),
  );
}

export function obterVisitasPorMesCliente(
  clienteId: string,
  filtros: FiltrosCliente,
): Promise<PontoSerieMensal[]> {
  return httpGet<PontoSerieMensal[]>(
    `/clientes/${clienteId}/graficos/visitas-mensal`,
    paramsDeFiltros(filtros),
  );
}

export function obterChecklistsPorMesCliente(
  clienteId: string,
  filtros: FiltrosCliente,
): Promise<PontoSerieMensal[]> {
  return httpGet<PontoSerieMensal[]>(
    `/clientes/${clienteId}/graficos/checklists-mensal`,
    paramsDeFiltros(filtros),
  );
}

export function obterLaboratoriosCliente(
  clienteId: string,
  filtros: FiltrosCliente,
): Promise<LinhaLaboratorioCliente[]> {
  return httpGet<LinhaLaboratorioCliente[]>(
    `/clientes/${clienteId}/laboratorios`,
    paramsDeFiltros(filtros),
  );
}

export function obterTimelineCliente(
  clienteId: string,
  pagina: number,
  tamanhoPagina: number,
): Promise<PaginaTimeline> {
  return httpGet<PaginaTimeline>(`/clientes/${clienteId}/timeline`, {
    pagina,
    tamanho_pagina: tamanhoPagina,
  });
}
