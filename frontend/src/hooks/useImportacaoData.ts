// Hooks de dados da Central de Importações (React Query), Sprint 6.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as importacaoService from "../services/importacaoService";
import type {
  FiltrosHistoricoImportacoes,
  Importacao,
  StatusImportacao,
} from "../types/importacao";

const STATUS_COM_DADOS_ALTERADOS: StatusImportacao[] = ["CONCLUIDA", "CONCLUIDA_COM_ERROS"];

export function useHistoricoImportacoes(
  pagina: number,
  tamanhoPagina: number,
  filtros: FiltrosHistoricoImportacoes = {},
) {
  return useQuery({
    queryKey: ["importacoes", "historico", pagina, tamanhoPagina, filtros],
    queryFn: () => importacaoService.listarImportacoes(pagina, tamanhoPagina, filtros),
  });
}

export function useDetalheImportacao(importacaoId: string | undefined) {
  return useQuery({
    queryKey: ["importacoes", "detalhe", importacaoId],
    queryFn: () => importacaoService.obterImportacao(importacaoId as string),
    enabled: Boolean(importacaoId),
  });
}

export function useErrosImportacao(
  importacaoId: string | undefined,
  pagina: number,
  tamanhoPagina: number,
) {
  return useQuery({
    queryKey: ["importacoes", "erros", importacaoId, pagina, tamanhoPagina],
    queryFn: () =>
      importacaoService.listarErrosImportacao(importacaoId as string, pagina, tamanhoPagina),
    enabled: Boolean(importacaoId),
  });
}

// O upload propriamente dito usa `importacaoService.enviarImportacao`
// diretamente (fora do React Query — precisa de progresso por arquivo em
// uma fila com múltiplos arquivos simultâneos, o que não mapeia bem para
// uma única `useMutation`). Este hook só cobre a invalidação de cache
// comum a upload e reprocessamento, reaproveitada pelos dois.
export function useInvalidarAposImportacao() {
  const queryClient = useQueryClient();
  return (resultado: Importacao) => {
    queryClient.invalidateQueries({ queryKey: ["importacoes"] });
    if (STATUS_COM_DADOS_ALTERADOS.includes(resultado.status)) {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["clientes"] });
    }
  };
}

export function useReprocessarImportacao() {
  const invalidarAposImportacao = useInvalidarAposImportacao();
  return useMutation({
    mutationFn: importacaoService.reprocessarImportacao,
    onSuccess: invalidarAposImportacao,
  });
}

export function useCancelarImportacao() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: importacaoService.cancelarImportacao,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["importacoes"] }),
  });
}
