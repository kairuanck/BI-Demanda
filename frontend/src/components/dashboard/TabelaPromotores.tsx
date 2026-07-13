// Tabela de Promotores do Dashboard Executivo — clique na linha abre o
// detalhe do promotor (DESIGN_SYSTEM.md, seção 6: `Table`).

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { usePromotores } from "../../hooks/useDashboardData";
import type { FiltrosDashboard } from "../../types/dashboard";
import { formatarMoeda, formatarNumero, formatarPercentual } from "../../utils/formatadores";
import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { ErrorState } from "../ui/ErrorState";
import { Skeleton } from "../ui/Skeleton";

const TAMANHO_PAGINA = 10;

const NOMES_SISTEMA: Record<string, string> = {
  SB_PROMOTOR: "SB Promotor",
  WECHECK: "WeCheck",
  PAINEL_AVERT: "Painel Avert",
  AMBOS: "Ambos",
};

interface TabelaPromotoresProps {
  filtros: FiltrosDashboard;
}

export function TabelaPromotores({ filtros }: TabelaPromotoresProps) {
  const [pagina, setPagina] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    setPagina(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(filtros)]);

  const { data, isLoading, isError, refetch } = usePromotores(filtros, pagina, TAMANHO_PAGINA);

  return (
    <Card titulo="Promotores">
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, indice) => (
            <Skeleton key={indice} className="h-10 w-full" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState mensagem="Não foi possível carregar os promotores." onRetry={refetch} />
      ) : !data || data.itens.length === 0 ? (
        <EmptyState descricao="Nenhum promotor encontrado para os filtros aplicados." />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                  <th className="py-2 pr-3 font-medium">Nome</th>
                  <th className="py-2 pr-3 font-medium">Tipo</th>
                  <th className="py-2 pr-3 font-medium">Supervisor</th>
                  <th className="py-2 pr-3 font-medium">Sistema</th>
                  <th className="py-2 pr-3 text-right font-medium">Clientes</th>
                  <th className="py-2 pr-3 text-right font-medium">Visitas</th>
                  <th className="py-2 pr-3 text-right font-medium">Checklists</th>
                  <th className="py-2 pr-3 text-right font-medium">Cobertura</th>
                  <th className="py-2 pr-3 text-right font-medium">Fat. Carteira</th>
                  <th className="py-2 pr-3 text-right font-medium">Fat. Região</th>
                </tr>
              </thead>
              <tbody>
                {data.itens.map((promotor) => (
                  <tr
                    key={promotor.promotor_id}
                    onClick={() => {
                      const busca = new URLSearchParams();
                      if (filtros.ano) busca.set("ano", String(filtros.ano));
                      if (filtros.mes) busca.set("mes", String(filtros.mes));
                      const query = busca.toString();
                      navigate(
                        `/dashboard/promotores/${promotor.promotor_id}${query ? `?${query}` : ""}`,
                      );
                    }}
                    className="cursor-pointer border-b border-slate-100 transition-colors hover:bg-surface-muted"
                  >
                    <td className="py-2 pr-3 font-medium text-slate-900">{promotor.nome}</td>
                    <td className="py-2 pr-3 text-slate-600">{promotor.tipo ?? "—"}</td>
                    <td className="py-2 pr-3 text-slate-600">{promotor.supervisor ?? "—"}</td>
                    <td className="py-2 pr-3 text-slate-600">
                      {promotor.sistema_origem
                        ? (NOMES_SISTEMA[promotor.sistema_origem] ?? promotor.sistema_origem)
                        : "—"}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarNumero(promotor.quantidade_clientes)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarNumero(promotor.numero_visitas)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarNumero(promotor.numero_checklists)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarPercentual(promotor.cobertura_carteira)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarMoeda(promotor.faturamento_carteira)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarMoeda(promotor.faturamento_regiao)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
            <span>
              {data.total_itens} promotor{data.total_itens !== 1 ? "es" : ""} · página {data.pagina}{" "}
              de {Math.max(data.total_paginas, 1)}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={pagina <= 1}
                onClick={() => setPagina((atual) => atual - 1)}
                className="rounded-lg border border-slate-200 px-3 py-1 font-medium text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Anterior
              </button>
              <button
                type="button"
                disabled={pagina >= data.total_paginas}
                onClick={() => setPagina((atual) => atual + 1)}
                className="rounded-lg border border-slate-200 px-3 py-1 font-medium text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Próxima
              </button>
            </div>
          </div>
        </>
      )}
    </Card>
  );
}
