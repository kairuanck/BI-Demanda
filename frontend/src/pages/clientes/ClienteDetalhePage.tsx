// Página da Visão 360º do Cliente (Sprint 5) — docs/DECISIONS.md, seção 22.

import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { BarChart } from "../../components/charts/BarChart";
import { LineChart } from "../../components/charts/LineChart";
import { BlocoGrafico } from "../../components/dashboard/BlocoGrafico";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { ErrorState } from "../../components/ui/ErrorState";
import { KpiCard } from "../../components/ui/KpiCard";
import { Skeleton } from "../../components/ui/Skeleton";
import { useOpcoesFiltro } from "../../hooks/useDashboardData";
import {
  useChecklistsPorMesCliente,
  useDetalheCliente,
  useEvolucaoFaturamentoCliente,
  useFaturamentoPorLaboratorioCliente,
  useLaboratoriosCliente,
  useTimelineCliente,
  useVisitasPorMesCliente,
} from "../../hooks/useClienteData";
import type { FiltrosCliente } from "../../types/cliente";
import { CLASSE_SELECT } from "../../utils/estilos";
import {
  NOMES_MES,
  formatarDataHora,
  formatarMesAno,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
} from "../../utils/formatadores";

const TAMANHO_PAGINA_TIMELINE = 15;

const NOMES_SISTEMA: Record<string, string> = {
  SB_PROMOTOR: "SB Promotor",
  WECHECK: "WeCheck",
  PAINEL_AVERT: "Painel Avert",
};

const RUBRICAS_TIMELINE: Record<string, string> = {
  VISITA: "bg-primary/10 text-primary",
  CHECKLIST: "bg-info/10 text-info",
  IMPORTACAO: "bg-slate-100 text-slate-600",
  ALTERACAO_CADASTRAL: "bg-warning/10 text-warning",
};

function formatarDias(dias: number | null): string {
  if (dias === null) return "Nunca visitado";
  if (dias === 0) return "Hoje";
  return `${dias} dia${dias !== 1 ? "s" : ""}`;
}

export function ClienteDetalhePage() {
  const { clienteId } = useParams<{ clienteId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: opcoes } = useOpcoesFiltro();

  const filtros: FiltrosCliente = {
    ano: searchParams.get("ano") ? Number(searchParams.get("ano")) : undefined,
    mes: searchParams.get("mes") ? Number(searchParams.get("mes")) : undefined,
    laboratorio_id: searchParams.get("laboratorio_id") ?? undefined,
    sistema_origem: searchParams.get("sistema_origem") ?? undefined,
  };

  function definirFiltro(chave: keyof FiltrosCliente, valor: string) {
    const proximo = new URLSearchParams(searchParams);
    if (valor) proximo.set(chave, valor);
    else proximo.delete(chave);
    setSearchParams(proximo, { replace: true });
  }

  const { data: detalhe, isLoading, isError, refetch } = useDetalheCliente(clienteId, filtros);
  const evolucaoFaturamento = useEvolucaoFaturamentoCliente(clienteId, filtros);
  const faturamentoLaboratorio = useFaturamentoPorLaboratorioCliente(clienteId, filtros);
  const visitasPorMes = useVisitasPorMesCliente(clienteId, filtros);
  const checklistsPorMes = useChecklistsPorMesCliente(clienteId, filtros);
  const laboratorios = useLaboratoriosCliente(clienteId, filtros);
  const [paginaTimeline, setPaginaTimeline] = useSearchParamPagina();
  const timeline = useTimelineCliente(clienteId, paginaTimeline, TAMANHO_PAGINA_TIMELINE);

  if (isError) {
    return <ErrorState mensagem="Não foi possível carregar o cliente." onRetry={refetch} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link
            to="/clientes"
            className="text-xs font-medium text-primary hover:text-primary-hover"
          >
            ← Voltar à busca de clientes
          </Link>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">
            {isLoading ? <Skeleton className="h-8 w-72" /> : detalhe?.razao_social}
          </h1>
          {!isLoading && detalhe && (
            <p className="mt-1 text-sm text-slate-500">
              {detalhe.nome_fantasia ?? "—"} · Código {detalhe.codigo_externo} ·{" "}
              <span
                className={
                  detalhe.ativo ? "font-medium text-success" : "font-medium text-slate-500"
                }
              >
                {detalhe.ativo ? "Ativo" : "Inativo"}
              </span>
            </p>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
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
          <select
            className={CLASSE_SELECT}
            value={filtros.laboratorio_id ?? ""}
            onChange={(evento) => definirFiltro("laboratorio_id", evento.target.value)}
          >
            <option value="">Todos os laboratórios</option>
            {(opcoes?.laboratorios ?? []).map((lab) => (
              <option key={lab.id} value={lab.id}>
                {lab.nome}
              </option>
            ))}
          </select>
          <select
            className={CLASSE_SELECT}
            value={filtros.sistema_origem ?? ""}
            onChange={(evento) => definirFiltro("sistema_origem", evento.target.value)}
          >
            <option value="">Todos os sistemas</option>
            {(opcoes?.sistemas_origem ?? []).map((sistema) => (
              <option key={sistema} value={sistema}>
                {NOMES_SISTEMA[sistema] ?? sistema}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading || !detalhe ? (
        <Skeleton className="h-24 w-full" />
      ) : (
        <Card titulo="Dados Cadastrais">
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-3 lg:grid-cols-4">
            <div>
              <dt className="text-xs uppercase text-slate-400">Código</dt>
              <dd className="text-slate-700">{detalhe.codigo_externo}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-400">Cidade/UF</dt>
              <dd className="text-slate-700">
                {detalhe.cidade}/{detalhe.uf_sigla}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-400">CNPJ/CPF</dt>
              <dd className="text-slate-700">{detalhe.cnpj_cpf ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-400">Grupo Econômico</dt>
              <dd className="text-slate-700">{detalhe.grupo_economico ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-400">Segmento</dt>
              <dd className="text-slate-700">{detalhe.segmento ?? "—"}</dd>
            </div>
          </dl>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <KpiCard
          titulo="Faturamento Acumulado"
          valor={formatarMoeda(detalhe?.kpis.faturamento_acumulado)}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Faturamento 12 Meses"
          valor={formatarMoeda(detalhe?.kpis.faturamento_12_meses)}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Laboratórios Comprados"
          valor={formatarNumero(detalhe?.kpis.quantidade_laboratorios)}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Dias Desde Última Visita"
          valor={detalhe ? formatarDias(detalhe.kpis.dias_desde_ultima_visita) : undefined}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Visitas"
          valor={formatarNumero(detalhe?.kpis.quantidade_visitas)}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Checklists"
          valor={formatarNumero(detalhe?.kpis.quantidade_checklists)}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Cobertura"
          valor={formatarPercentual(detalhe?.kpis.cobertura)}
          carregando={isLoading}
        />
        <KpiCard
          titulo="Positivação"
          valor={formatarPercentual(detalhe?.kpis.positivacao)}
          carregando={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <BlocoGrafico
          titulo="Evolução do Faturamento"
          carregando={evolucaoFaturamento.isLoading}
          comErro={evolucaoFaturamento.isError}
          vazio={(evolucaoFaturamento.data ?? []).length === 0}
          onRetry={() => evolucaoFaturamento.refetch()}
        >
          <LineChart
            ariaLabel="Evolução mensal do faturamento do cliente"
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
          titulo="Faturamento por Laboratório"
          carregando={faturamentoLaboratorio.isLoading}
          comErro={faturamentoLaboratorio.isError}
          vazio={(faturamentoLaboratorio.data ?? []).length === 0}
          onRetry={() => faturamentoLaboratorio.refetch()}
        >
          <BarChart
            ariaLabel="Faturamento do cliente por laboratório"
            rotulos={(faturamentoLaboratorio.data ?? []).map((p) => p.rotulo)}
            valores={(faturamentoLaboratorio.data ?? []).map((p) => Number(p.valor))}
            formatarValor={formatarMoeda}
          />
        </BlocoGrafico>

        <BlocoGrafico
          titulo="Visitas por Mês"
          carregando={visitasPorMes.isLoading}
          comErro={visitasPorMes.isError}
          vazio={(visitasPorMes.data ?? []).length === 0}
          onRetry={() => visitasPorMes.refetch()}
        >
          <LineChart
            ariaLabel="Quantidade de visitas por mês"
            rotulos={(visitasPorMes.data ?? []).map((p) => formatarMesAno(p.ano, p.mes))}
            series={[
              {
                rotulo: "Visitas",
                valores: (visitasPorMes.data ?? []).map((p) => Number(p.valor)),
              },
            ]}
            formatarValor={formatarNumero}
          />
        </BlocoGrafico>

        <BlocoGrafico
          titulo="Checklists por Mês"
          carregando={checklistsPorMes.isLoading}
          comErro={checklistsPorMes.isError}
          vazio={(checklistsPorMes.data ?? []).length === 0}
          onRetry={() => checklistsPorMes.refetch()}
        >
          <LineChart
            ariaLabel="Quantidade de checklists por mês"
            rotulos={(checklistsPorMes.data ?? []).map((p) => formatarMesAno(p.ano, p.mes))}
            series={[
              {
                rotulo: "Checklists",
                valores: (checklistsPorMes.data ?? []).map((p) => Number(p.valor)),
              },
            ]}
            formatarValor={formatarNumero}
          />
        </BlocoGrafico>
      </div>

      <Card titulo="Laboratórios">
        {laboratorios.isLoading ? (
          <Skeleton className="h-32 w-full" />
        ) : laboratorios.isError ? (
          <ErrorState
            mensagem="Não foi possível carregar os laboratórios."
            onRetry={() => laboratorios.refetch()}
          />
        ) : (laboratorios.data ?? []).length === 0 ? (
          <EmptyState descricao="Nenhuma compra registrada para os filtros aplicados." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                  <th className="py-2 pr-3 font-medium">Laboratório</th>
                  <th className="py-2 pr-3 font-medium">Primeira Compra</th>
                  <th className="py-2 pr-3 font-medium">Última Compra</th>
                  <th className="py-2 pr-3 text-right font-medium">Valor Acumulado</th>
                  <th className="py-2 pr-3 text-right font-medium">Participação</th>
                </tr>
              </thead>
              <tbody>
                {(laboratorios.data ?? []).map((linha) => (
                  <tr key={linha.laboratorio} className="border-b border-slate-100">
                    <td className="py-2 pr-3 font-medium text-slate-900">{linha.laboratorio}</td>
                    <td className="py-2 pr-3 text-slate-600">
                      {formatarMesAno(linha.primeiro_ano, linha.primeiro_mes)}
                    </td>
                    <td className="py-2 pr-3 text-slate-600">
                      {formatarMesAno(linha.ultimo_ano, linha.ultimo_mes)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarMoeda(linha.valor_acumulado)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarPercentual(linha.participacao_percentual)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : !detalhe || detalhe.vinculos.length === 0 ? (
          <Card titulo="Promotor">
            <EmptyState descricao="Nenhum promotor vinculado a este cliente." />
          </Card>
        ) : (
          detalhe.vinculos.map((vinculo) => (
            <Card
              key={vinculo.promotor_id}
              titulo={`Promotor · ${NOMES_SISTEMA[vinculo.sistema_origem] ?? vinculo.sistema_origem}`}
            >
              <div className="space-y-1 text-sm">
                <p className="text-base font-semibold text-slate-900">{vinculo.nome}</p>
                <p className="text-slate-500">
                  {[vinculo.tipo, vinculo.supervisor].filter(Boolean).join(" · ") ||
                    "Sem dados cadastrais adicionais"}
                </p>
                <div className="mt-3 grid grid-cols-3 gap-3 text-xs">
                  <div>
                    <p className="text-slate-400">Carteira</p>
                    <p className="font-medium text-slate-700">
                      {formatarNumero(vinculo.quantidade_clientes_carteira)}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400">Cobertura</p>
                    <p className="font-medium text-slate-700">
                      {formatarPercentual(vinculo.cobertura)}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400">Faturamento</p>
                    <p className="font-medium text-slate-700">
                      {formatarMoeda(vinculo.faturamento_carteira)}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => navigate(`/dashboard/promotores/${vinculo.promotor_id}`)}
                  className="mt-3 text-xs font-medium text-primary hover:text-primary-hover"
                >
                  Ver página do promotor →
                </button>
              </div>
            </Card>
          ))
        )}
      </div>

      <Card titulo="Histórico">
        {timeline.isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, indice) => (
              <Skeleton key={indice} className="h-12 w-full" />
            ))}
          </div>
        ) : timeline.isError ? (
          <ErrorState
            mensagem="Não foi possível carregar o histórico."
            onRetry={() => timeline.refetch()}
          />
        ) : !timeline.data || timeline.data.itens.length === 0 ? (
          <EmptyState descricao="Nenhum evento registrado para este cliente." />
        ) : (
          <>
            <ol className="space-y-3">
              {timeline.data.itens.map((evento, indice) => (
                <li
                  key={`${evento.tipo}-${evento.data}-${indice}`}
                  className="flex items-start gap-3 border-b border-slate-100 pb-3 last:border-b-0"
                >
                  <span
                    className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                      RUBRICAS_TIMELINE[evento.tipo] ?? "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {evento.tipo}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-900">{evento.titulo}</p>
                    {evento.descricao && (
                      <p className="text-xs text-slate-500">{evento.descricao}</p>
                    )}
                    <p className="text-xs text-slate-400">{formatarDataHora(evento.data)}</p>
                  </div>
                </li>
              ))}
            </ol>

            <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
              <span>
                {timeline.data.total_itens} evento{timeline.data.total_itens !== 1 ? "s" : ""} ·
                página {timeline.data.pagina} de {Math.max(timeline.data.total_paginas, 1)}
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={paginaTimeline <= 1}
                  onClick={() => setPaginaTimeline(paginaTimeline - 1)}
                  className="rounded-lg border border-slate-200 px-3 py-1 font-medium text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Anterior
                </button>
                <button
                  type="button"
                  disabled={paginaTimeline >= timeline.data.total_paginas}
                  onClick={() => setPaginaTimeline(paginaTimeline + 1)}
                  className="rounded-lg border border-slate-200 px-3 py-1 font-medium text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Próxima
                </button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}

function useSearchParamPagina(): [number, (proxima: number) => void] {
  const [searchParams, setSearchParams] = useSearchParams();
  const pagina = Number(searchParams.get("pagina_timeline") ?? "1") || 1;

  function definirPagina(proxima: number) {
    const proximo = new URLSearchParams(searchParams);
    proximo.set("pagina_timeline", String(proxima));
    setSearchParams(proximo, { replace: true });
  }

  return [pagina, definirPagina];
}
