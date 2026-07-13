// Dashboard Executivo (Sprint 4) — DASHBOARD.md, KPIS.md, GRAFICOS.md,
// adaptados à realidade do schema real (docs/DECISIONS.md, seções 16-19).

import { BlocoGrafico } from "../../components/dashboard/BlocoGrafico";
import { TabelaPromotores } from "../../components/dashboard/TabelaPromotores";
import { BarChart } from "../../components/charts/BarChart";
import { DoughnutChart } from "../../components/charts/DoughnutChart";
import { LineChart } from "../../components/charts/LineChart";
import { BarraDeFiltros } from "../../components/filtros/BarraDeFiltros";
import { Card } from "../../components/ui/Card";
import { KpiCard } from "../../components/ui/KpiCard";
import {
  useDistribuicaoUf,
  useEvolucaoFaturamentoMensal,
  useEvolucaoPositivacaoMensal,
  useFaturamentoPorLaboratorio,
  useKpis,
  useTiposChecklist,
  useTopPromotores,
  useUltimasImportacoes,
} from "../../hooks/useDashboardData";
import { useFiltrosDashboard } from "../../hooks/useFiltrosDashboard";
import {
  formatarDataHora,
  formatarMesAno,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
} from "../../utils/formatadores";

function tomCobertura(cobertura: string | null): "default" | "success" | "warning" | "danger" {
  if (cobertura === null) return "default";
  const valor = Number(cobertura);
  if (valor >= 0.85) return "success";
  if (valor >= 0.7) return "warning";
  return "danger";
}

export function DashboardPage() {
  const { filtros, definirFiltro, limparFiltros, totalFiltrosAtivos } = useFiltrosDashboard();

  const kpis = useKpis(filtros);
  const evolucaoFaturamento = useEvolucaoFaturamentoMensal(filtros);
  const evolucaoPositivacao = useEvolucaoPositivacaoMensal(filtros);
  const faturamentoLaboratorio = useFaturamentoPorLaboratorio(filtros);
  const topPromotores = useTopPromotores(filtros, 10);
  const tiposChecklist = useTiposChecklist(filtros);
  const distribuicaoUf = useDistribuicaoUf(filtros);
  const ultimasImportacoes = useUltimasImportacoes();

  const ultimaImportacaoGeral = ultimasImportacoes.data?.reduce<
    (typeof ultimasImportacoes.data)[number] | undefined
  >((maisRecente, atual) => {
    if (!maisRecente) return atual;
    return new Date(atual.criado_em) > new Date(maisRecente.criado_em) ? atual : maisRecente;
  }, undefined);

  const promotoresComIndice = (topPromotores.data ?? []).filter(
    (promotor) => promotor.indice_desempenho !== null,
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard Executivo</h1>
        <p className="mt-1 text-sm text-slate-500">
          Visão consolidada da operação — Faturamento, Cobertura, Positivação e Visitas.
        </p>
      </div>

      <BarraDeFiltros
        filtros={filtros}
        definirFiltro={definirFiltro}
        limparFiltros={limparFiltros}
        totalFiltrosAtivos={totalFiltrosAtivos}
      />

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <KpiCard
          titulo="Faturamento Total"
          valor={formatarMoeda(kpis.data?.faturamento_total)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Faturamento da Carteira"
          valor={formatarMoeda(kpis.data?.faturamento_carteira)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Faturamento da Região"
          valor={formatarMoeda(kpis.data?.faturamento_regiao)}
          naoAplicavel={kpis.data?.faturamento_regiao === null}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Faturamento Fora da Carteira"
          valor={formatarMoeda(kpis.data?.faturamento_fora_carteira)}
          naoAplicavel={kpis.data?.faturamento_fora_carteira === null}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Quantidade de Clientes"
          valor={formatarNumero(kpis.data?.quantidade_clientes)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Clientes Positivados"
          valor={formatarNumero(kpis.data?.clientes_positivados)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Cobertura da Carteira"
          valor={formatarPercentual(kpis.data?.cobertura_carteira)}
          naoAplicavel={kpis.data?.cobertura_carteira === null}
          tom={tomCobertura(kpis.data?.cobertura_carteira ?? null)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Número de Visitas"
          valor={formatarNumero(kpis.data?.numero_visitas)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Número de Checklists"
          valor={formatarNumero(kpis.data?.numero_checklists)}
          carregando={kpis.isLoading}
        />
        <KpiCard
          titulo="Última Importação"
          valor={formatarDataHora(ultimaImportacaoGeral?.criado_em)}
          descricao={ultimaImportacaoGeral?.tipo_arquivo}
          carregando={ultimasImportacoes.isLoading}
          naoAplicavel={!ultimasImportacoes.isLoading && !ultimaImportacaoGeral}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <BlocoGrafico
          titulo="Evolução Mensal do Faturamento"
          carregando={evolucaoFaturamento.isLoading}
          comErro={evolucaoFaturamento.isError}
          vazio={(evolucaoFaturamento.data ?? []).length === 0}
          onRetry={() => evolucaoFaturamento.refetch()}
        >
          <LineChart
            ariaLabel="Evolução mensal do faturamento"
            rotulos={(evolucaoFaturamento.data ?? []).map((p) => formatarMesAno(p.ano, p.mes))}
            series={[
              {
                rotulo: "Faturamento",
                valores: (evolucaoFaturamento.data ?? []).map((p) => Number(p.valor)),
              },
            ]}
            formatarValor={formatarMoeda}
          />
        </BlocoGrafico>

        <BlocoGrafico
          titulo="Evolução da Positivação"
          carregando={evolucaoPositivacao.isLoading}
          comErro={evolucaoPositivacao.isError}
          vazio={(evolucaoPositivacao.data ?? []).length === 0}
          onRetry={() => evolucaoPositivacao.refetch()}
        >
          <LineChart
            ariaLabel="Evolução mensal de clientes positivados por carteira, região e fora da carteira"
            rotulos={(evolucaoPositivacao.data ?? []).map((p) => formatarMesAno(p.ano, p.mes))}
            series={[
              {
                rotulo: "Carteira",
                valores: (evolucaoPositivacao.data ?? []).map(
                  (p) => p.clientes_positivados_carteira,
                ),
              },
              {
                rotulo: "Região",
                valores: (evolucaoPositivacao.data ?? []).map((p) => p.clientes_positivados_regiao),
              },
              {
                rotulo: "Fora da Carteira",
                valores: (evolucaoPositivacao.data ?? []).map(
                  (p) => p.clientes_positivados_fora_carteira,
                ),
              },
            ]}
            formatarValor={formatarNumero}
          />
        </BlocoGrafico>

        <BlocoGrafico
          titulo="Faturamento por Laboratório"
          carregando={faturamentoLaboratorio.isLoading}
          comErro={faturamentoLaboratorio.isError}
          vazio={(faturamentoLaboratorio.data ?? []).length === 0}
          onRetry={() => faturamentoLaboratorio.refetch()}
        >
          <BarChart
            ariaLabel="Faturamento total por laboratório"
            rotulos={(faturamentoLaboratorio.data ?? []).map((p) => p.rotulo)}
            valores={(faturamentoLaboratorio.data ?? []).map((p) => Number(p.valor))}
            formatarValor={formatarMoeda}
          />
        </BlocoGrafico>

        <BlocoGrafico
          titulo="Top Promotores (Índice de Desempenho)"
          carregando={topPromotores.isLoading}
          comErro={topPromotores.isError}
          vazio={promotoresComIndice.length === 0}
          onRetry={() => topPromotores.refetch()}
        >
          <BarChart
            ariaLabel="Top promotores por índice de desempenho"
            rotulos={promotoresComIndice.map((p) => p.nome)}
            valores={promotoresComIndice.map((p) => Number(p.indice_desempenho))}
            formatarValor={formatarPercentual}
            horizontal
          />
        </BlocoGrafico>

        <BlocoGrafico
          titulo="Tipos de Checklist"
          carregando={tiposChecklist.isLoading}
          comErro={tiposChecklist.isError}
          vazio={(tiposChecklist.data ?? []).length === 0}
          onRetry={() => tiposChecklist.refetch()}
        >
          <DoughnutChart
            ariaLabel="Distribuição de aplicações por tipo de checklist"
            rotulos={(tiposChecklist.data ?? []).map((p) => p.rotulo)}
            valores={(tiposChecklist.data ?? []).map((p) => Number(p.valor))}
            formatarValor={formatarNumero}
          />
        </BlocoGrafico>

        <Card titulo="Distribuição por UF">
          {distribuicaoUf.isLoading ? (
            <div className="h-72 animate-pulse rounded-md bg-slate-200" />
          ) : distribuicaoUf.isError ? (
            <div className="flex h-72 items-center justify-center text-sm text-danger">
              Não foi possível carregar a distribuição por UF.
            </div>
          ) : (distribuicaoUf.data ?? []).length === 0 ? (
            <div className="flex h-72 items-center justify-center text-sm text-slate-500">
              Nenhum dado para os filtros aplicados.
            </div>
          ) : (
            <div className="max-h-72 overflow-y-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-white">
                  <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                    <th className="py-2 pr-3 font-medium">UF</th>
                    <th className="py-2 pr-3 text-right font-medium">Clientes</th>
                    <th className="py-2 pr-3 text-right font-medium">Faturamento</th>
                  </tr>
                </thead>
                <tbody>
                  {(distribuicaoUf.data ?? []).map((linha) => (
                    <tr key={linha.uf_sigla} className="border-b border-slate-100">
                      <td className="py-2 pr-3 font-medium text-slate-900">{linha.uf_sigla}</td>
                      <td className="py-2 pr-3 text-right tabular-nums">
                        {formatarNumero(linha.quantidade_clientes)}
                      </td>
                      <td className="py-2 pr-3 text-right tabular-nums">
                        {formatarMoeda(linha.faturamento_total)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      <TabelaPromotores filtros={filtros} />
    </div>
  );
}
