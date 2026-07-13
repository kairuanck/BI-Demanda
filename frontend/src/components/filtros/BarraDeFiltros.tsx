// Barra de filtros globais do Dashboard Executivo (DESIGN_SYSTEM.md, seção 8;
// DASHBOARD.md, seção 2.3). Qualquer alteração atualiza a URL e recarrega
// todos os blocos da tela que consomem `useFiltrosDashboard`.

import { useOpcoesFiltro } from "../../hooks/useDashboardData";
import type { FiltrosDashboard } from "../../types/dashboard";
import { NOMES_MES } from "../../utils/formatadores";
import { Skeleton } from "../ui/Skeleton";

const NOMES_SISTEMA: Record<string, string> = {
  SB_PROMOTOR: "SB Promotor",
  WECHECK: "WeCheck",
  PAINEL_AVERT: "Painel Avert",
};

interface BarraDeFiltrosProps {
  filtros: FiltrosDashboard;
  definirFiltro: (chave: keyof FiltrosDashboard, valor: string) => void;
  limparFiltros: () => void;
  totalFiltrosAtivos: number;
}

const CLASSE_SELECT =
  "w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary";

export function BarraDeFiltros({
  filtros,
  definirFiltro,
  limparFiltros,
  totalFiltrosAtivos,
}: BarraDeFiltrosProps) {
  const { data: opcoes, isLoading } = useOpcoesFiltro();

  if (isLoading || !opcoes) {
    return (
      <div className="grid grid-cols-2 gap-3 rounded-lg border border-slate-200 bg-white p-4 sm:grid-cols-4 lg:grid-cols-8">
        {Array.from({ length: 8 }).map((_, indice) => (
          <Skeleton key={indice} className="h-9 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Ano
          <select
            className={CLASSE_SELECT}
            value={filtros.ano ?? ""}
            onChange={(evento) => definirFiltro("ano", evento.target.value)}
          >
            <option value="">Todos</option>
            {opcoes.anos.map((ano) => (
              <option key={ano} value={ano}>
                {ano}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Mês
          <select
            className={CLASSE_SELECT}
            value={filtros.mes ?? ""}
            onChange={(evento) => definirFiltro("mes", evento.target.value)}
          >
            <option value="">Todos</option>
            {NOMES_MES.map((nome, indice) => (
              <option key={nome} value={indice + 1}>
                {nome}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          UF
          <select
            className={CLASSE_SELECT}
            value={filtros.uf ?? ""}
            onChange={(evento) => definirFiltro("uf", evento.target.value)}
          >
            <option value="">Todas</option>
            {opcoes.ufs.map((uf) => (
              <option key={uf.sigla} value={uf.sigla}>
                {uf.sigla}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Laboratório
          <select
            className={CLASSE_SELECT}
            value={filtros.laboratorio_id ?? ""}
            onChange={(evento) => definirFiltro("laboratorio_id", evento.target.value)}
          >
            <option value="">Todos</option>
            {opcoes.laboratorios.map((lab) => (
              <option key={lab.id} value={lab.id}>
                {lab.nome}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Tipo de Promotor
          <select
            className={CLASSE_SELECT}
            value={filtros.tipo_promotor_id ?? ""}
            onChange={(evento) => definirFiltro("tipo_promotor_id", evento.target.value)}
          >
            <option value="">Todos</option>
            {opcoes.tipos_promotor.map((tipo) => (
              <option key={tipo.id} value={tipo.id}>
                {tipo.nome}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Sistema de Origem
          <select
            className={CLASSE_SELECT}
            value={filtros.sistema_origem ?? ""}
            onChange={(evento) => definirFiltro("sistema_origem", evento.target.value)}
          >
            <option value="">Todos</option>
            {opcoes.sistemas_origem.map((sistema) => (
              <option key={sistema} value={sistema}>
                {NOMES_SISTEMA[sistema] ?? sistema}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Supervisor
          <select
            className={CLASSE_SELECT}
            value={filtros.supervisor_id ?? ""}
            onChange={(evento) => definirFiltro("supervisor_id", evento.target.value)}
          >
            <option value="">Todos</option>
            {opcoes.supervisores.map((supervisor) => (
              <option key={supervisor.id} value={supervisor.id}>
                {supervisor.nome}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
          Promotor
          <select
            className={CLASSE_SELECT}
            value={filtros.promotor_id ?? ""}
            onChange={(evento) => definirFiltro("promotor_id", evento.target.value)}
          >
            <option value="">Todos</option>
            {opcoes.promotores.map((promotor) => (
              <option key={promotor.id} value={promotor.id}>
                {promotor.nome}
              </option>
            ))}
          </select>
        </label>
      </div>

      {totalFiltrosAtivos > 0 && (
        <div className="mt-3 flex items-center gap-3 border-t border-slate-100 pt-3">
          <span className="text-xs text-slate-500">
            {totalFiltrosAtivos} filtro{totalFiltrosAtivos > 1 ? "s" : ""} ativo
            {totalFiltrosAtivos > 1 ? "s" : ""}
          </span>
          <button
            type="button"
            onClick={limparFiltros}
            className="text-xs font-medium text-primary hover:text-primary-hover"
          >
            Limpar filtros
          </button>
        </div>
      )}
    </div>
  );
}
