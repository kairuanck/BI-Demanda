import { Link } from "react-router-dom";

import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { ErrorState } from "../../components/ui/ErrorState";
import { Skeleton } from "../../components/ui/Skeleton";
import { useUltimasImportacoes } from "../../hooks/useDashboardData";
import { useHealthCheck } from "../../hooks/useHealthCheck";
import { formatarDataHora, formatarDuracao, formatarNumero } from "../../utils/formatadores";

const NOMES_TIPO: Record<string, string> = {
  CLIENTES: "Clientes",
  CARTEIRA: "Carteira",
  FATURAMENTO: "Faturamento",
  CHECKLIST: "Checklist",
  PAINEL_AVERT: "Painel Avert",
  WECHECK: "WeCheck",
};

const CORES_STATUS: Record<string, string> = {
  CONCLUIDA: "text-success",
  CONCLUIDA_COM_ERROS: "text-warning",
  FALHOU: "text-danger",
  PENDENTE: "text-slate-500",
  REVERTIDA: "text-slate-500",
};

export function HomePage() {
  const { data, isLoading, isError } = useHealthCheck();
  const importacoes = useUltimasImportacoes();

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-8">
        <h1 className="text-2xl font-semibold text-slate-900">Bem-vindo ao Promotores BI</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-500">
          Plataforma de Business Intelligence para gestão de Promotores Técnicos e Promotores Trade
          do mercado pet.{" "}
          <Link to="/dashboard" className="font-medium text-primary hover:text-primary-hover">
            Ver Dashboard Executivo →
          </Link>
        </p>

        <div className="mt-6 flex items-center gap-2 text-sm">
          <span className="font-medium text-slate-700">Status da API:</span>
          {isLoading && <span className="text-slate-400">verificando...</span>}
          {isError && <span className="text-danger">indisponível</span>}
          {data && (
            <span className="inline-flex items-center gap-1 text-success">
              <span className="h-2 w-2 rounded-full bg-success" />
              {data.status} · banco {data.database}
            </span>
          )}
        </div>
      </div>

      <Card titulo="Últimas Importações">
        {importacoes.isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, indice) => (
              <Skeleton key={indice} className="h-10 w-full" />
            ))}
          </div>
        ) : importacoes.isError ? (
          <ErrorState
            mensagem="Não foi possível carregar as últimas importações."
            onRetry={() => importacoes.refetch()}
          />
        ) : !importacoes.data || importacoes.data.length === 0 ? (
          <EmptyState descricao="Nenhuma importação realizada ainda." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                  <th className="py-2 pr-3 font-medium">Tipo</th>
                  <th className="py-2 pr-3 font-medium">Arquivo</th>
                  <th className="py-2 pr-3 font-medium">Status</th>
                  <th className="py-2 pr-3 text-right font-medium">Linhas Válidas</th>
                  <th className="py-2 pr-3 text-right font-medium">Linhas Inválidas</th>
                  <th className="py-2 pr-3 font-medium">Data</th>
                  <th className="py-2 pr-3 text-right font-medium">Duração</th>
                </tr>
              </thead>
              <tbody>
                {importacoes.data.map((importacao) => (
                  <tr key={importacao.id} className="border-b border-slate-100">
                    <td className="py-2 pr-3 font-medium text-slate-900">
                      {NOMES_TIPO[importacao.tipo_arquivo] ?? importacao.tipo_arquivo}
                    </td>
                    <td className="py-2 pr-3 text-slate-600">{importacao.nome_arquivo_original}</td>
                    <td
                      className={`py-2 pr-3 font-medium ${CORES_STATUS[importacao.status] ?? "text-slate-600"}`}
                    >
                      {importacao.status}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarNumero(importacao.linhas_validas)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums">
                      {formatarNumero(importacao.linhas_invalidas)}
                    </td>
                    <td className="py-2 pr-3 text-slate-600">
                      {formatarDataHora(importacao.criado_em)}
                    </td>
                    <td className="py-2 pr-3 text-right tabular-nums text-slate-600">
                      {formatarDuracao(importacao.duracao_segundos)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
