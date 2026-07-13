// Página de Detalhe do Promotor (Sprint 4) — DASHBOARD.md, seção 3,
// adaptada à realidade do schema real (docs/DECISIONS.md, seções 16-19).

import { Link, useNavigate, useParams } from "react-router-dom";

import { BarChart } from "../../components/charts/BarChart";
import { LineChart } from "../../components/charts/LineChart";
import { BlocoGrafico } from "../../components/dashboard/BlocoGrafico";
import { Card } from "../../components/ui/Card";
import { ErrorState } from "../../components/ui/ErrorState";
import { KpiCard } from "../../components/ui/KpiCard";
import { Skeleton } from "../../components/ui/Skeleton";
import { useDetalhePromotor, useOpcoesFiltro } from "../../hooks/useDashboardData";
import { useFiltrosDashboard } from "../../hooks/useFiltrosDashboard";
import {
  formatarMesAno,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
} from "../../utils/formatadores";

const NOMES_MES = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];

const CLASSE_SELECT =
  "rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary";

export function PromotorDetalhePage() {
  const { promotorId } = useParams<{ promotorId: string }>();
  const navigate = useNavigate();
  const { filtros, definirFiltro } = useFiltrosDashboard();
  const { data: opcoes } = useOpcoesFiltro();
  const periodo = { ano: filtros.ano, mes: filtros.mes };
  const { data: detalhe, isLoading, isError, refetch } = useDetalhePromotor(promotorId, periodo);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            to="/dashboard"
            className="text-xs font-medium text-primary hover:text-primary-hover"
          >
            ← Voltar ao Dashboard
          </Link>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">
            {isLoading ? <Skeleton className="h-8 w-64" /> : (detalhe?.nome ?? "Promotor")}
          </h1>
          {!isLoading && detalhe && (
            <p className="mt-1 text-sm text-slate-500">
              {[detalhe.tipo, detalhe.supervisor, detalhe.area].filter(Boolean).join(" · ") ||
                "Sem dados cadastrais adicionais"}
            </p>
          )}
        </div>

        <div className="flex gap-2">
          <select
            className={CLASSE_SELECT}
            value={filtros.ano ?? ""}
            onChange={(evento) => definirFiltro("ano", evento.target.value)}
          >
            <option value="">Todos os anos</option>
            {(opcoes?.anos ?? []).map((ano) => (
              <option key={ano} value={ano}>
                {ano}
              </option>
            ))}
          </select>
          <select
            className={CLASSE_SELECT}
            value={filtros.mes ?? ""}
            onChange={(evento) => definirFiltro("mes", evento.target.value)}
          >
            <option value="">Todos os meses</option>
            {NOMES_MES.map((nome, indice) => (
              <option key={nome} value={indice + 1}>
                {nome}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isError ? (
        <ErrorState mensagem="Não foi possível carregar o detalhe do promotor." onRetry={refetch} />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <KpiCard
              titulo="Clientes"
              valor={formatarNumero(detalhe?.kpis.quantidade_clientes)}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Cobertura"
              valor={formatarPercentual(detalhe?.kpis.cobertura_carteira)}
              naoAplicavel={detalhe?.kpis.cobertura_carteira === null}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Visitas"
              valor={formatarNumero(detalhe?.kpis.numero_visitas)}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Checklists"
              valor={formatarNumero(detalhe?.kpis.numero_checklists)}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Conformidade de Checklist"
              valor={formatarPercentual(detalhe?.conformidade_checklist)}
              naoAplicavel={detalhe?.conformidade_checklist === null}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Índice de Desempenho"
              valor={formatarPercentual(detalhe?.indice_desempenho)}
              naoAplicavel={detalhe?.indice_desempenho === null}
              carregando={isLoading}
            />
          </div>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <KpiCard
              titulo="Faturamento Carteira"
              valor={formatarMoeda(detalhe?.kpis.faturamento_carteira)}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Faturamento Região"
              valor={formatarMoeda(detalhe?.kpis.faturamento_regiao)}
              naoAplicavel={detalhe?.kpis.faturamento_regiao === null}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Clientes Positivados"
              valor={formatarNumero(detalhe?.kpis.clientes_positivados)}
              carregando={isLoading}
            />
            <KpiCard
              titulo="Código Externo"
              valor={detalhe?.codigo_externo ?? "—"}
              carregando={isLoading}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <BlocoGrafico
              titulo="Evolução do Faturamento"
              carregando={isLoading}
              comErro={false}
              vazio={(detalhe?.evolucao_faturamento ?? []).length === 0}
            >
              <LineChart
                ariaLabel="Evolução mensal do faturamento do promotor"
                rotulos={(detalhe?.evolucao_faturamento ?? []).map((p) =>
                  formatarMesAno(p.ano, p.mes),
                )}
                series={[
                  {
                    rotulo: "Faturamento",
                    valores: (detalhe?.evolucao_faturamento ?? []).map((p) => Number(p.valor)),
                  },
                ]}
                formatarValor={formatarMoeda}
              />
            </BlocoGrafico>

            <BlocoGrafico
              titulo="Faturamento por Laboratório"
              carregando={isLoading}
              comErro={false}
              vazio={(detalhe?.faturamento_por_laboratorio ?? []).length === 0}
            >
              <BarChart
                ariaLabel="Faturamento do promotor por laboratório"
                rotulos={(detalhe?.faturamento_por_laboratorio ?? []).map((p) => p.rotulo)}
                valores={(detalhe?.faturamento_por_laboratorio ?? []).map((p) => Number(p.valor))}
                formatarValor={formatarMoeda}
              />
            </BlocoGrafico>
          </div>

          {!isLoading && !detalhe && (
            <Card>
              <p className="text-sm text-slate-500">Promotor não encontrado.</p>
              <button
                type="button"
                onClick={() => navigate("/dashboard")}
                className="mt-3 text-sm font-medium text-primary hover:text-primary-hover"
              >
                Voltar ao Dashboard
              </button>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
