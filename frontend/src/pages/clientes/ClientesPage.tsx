// Página de Busca de Clientes (Sprint 5) — "Resultados de pesquisa" e ponto
// de navegação para a Visão 360º do Cliente a partir de qualquer tela.

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { ErrorState } from "../../components/ui/ErrorState";
import { Skeleton } from "../../components/ui/Skeleton";
import { useBuscarClientes } from "../../hooks/useClienteData";

const TAMANHO_PAGINA = 20;

export function ClientesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const termoUrl = searchParams.get("q") ?? "";
  const [termo, setTermo] = useState(termoUrl);
  const [pagina, setPagina] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    setTermo(termoUrl);
  }, [termoUrl]);

  useEffect(() => {
    const temporizador = setTimeout(() => {
      if (termo !== termoUrl) {
        const proximo = new URLSearchParams(searchParams);
        if (termo) proximo.set("q", termo);
        else proximo.delete("q");
        setSearchParams(proximo, { replace: true });
        setPagina(1);
      }
    }, 300);
    return () => clearTimeout(temporizador);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [termo]);

  const { data, isLoading, isError, refetch } = useBuscarClientes(termoUrl, pagina, TAMANHO_PAGINA);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Clientes</h1>
        <p className="mt-1 text-sm text-slate-500">
          Pesquise por código, razão social, nome fantasia, CNPJ ou cidade.
        </p>
      </div>

      <input
        type="search"
        value={termo}
        onChange={(evento) => setTermo(evento.target.value)}
        placeholder="Buscar cliente…"
        className="w-full max-w-xl rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-700 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
      />

      <Card>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, indice) => (
              <Skeleton key={indice} className="h-10 w-full" />
            ))}
          </div>
        ) : isError ? (
          <ErrorState mensagem="Não foi possível buscar clientes." onRetry={() => refetch()} />
        ) : !data || data.itens.length === 0 ? (
          <EmptyState
            titulo="Nenhum cliente encontrado"
            descricao={
              termoUrl
                ? `Nenhum resultado para "${termoUrl}".`
                : "Não há clientes cadastrados ainda."
            }
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                    <th className="py-2 pr-3 font-medium">Código</th>
                    <th className="py-2 pr-3 font-medium">Razão Social</th>
                    <th className="py-2 pr-3 font-medium">Nome Fantasia</th>
                    <th className="py-2 pr-3 font-medium">Cidade/UF</th>
                    <th className="py-2 pr-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.itens.map((cliente) => (
                    <tr
                      key={cliente.id}
                      onClick={() => navigate(`/clientes/${cliente.id}`)}
                      className="cursor-pointer border-b border-slate-100 transition-colors hover:bg-surface-muted"
                    >
                      <td className="py-2 pr-3 text-slate-600">{cliente.codigo_externo}</td>
                      <td className="py-2 pr-3 font-medium text-slate-900">
                        {cliente.razao_social}
                      </td>
                      <td className="py-2 pr-3 text-slate-600">{cliente.nome_fantasia ?? "—"}</td>
                      <td className="py-2 pr-3 text-slate-600">
                        {cliente.cidade}/{cliente.uf_sigla}
                      </td>
                      <td className="py-2 pr-3">
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            cliente.ativo
                              ? "bg-success/10 text-success"
                              : "bg-slate-100 text-slate-500"
                          }`}
                        >
                          {cliente.ativo ? "Ativo" : "Inativo"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
              <span>
                {data.total_itens} cliente{data.total_itens !== 1 ? "s" : ""} · página {data.pagina}{" "}
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
    </div>
  );
}
