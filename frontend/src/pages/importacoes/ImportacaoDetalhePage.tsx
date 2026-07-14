// Detalhe de Importação (Sprint 6) — metadados, logs de erro e ações
// (reprocessar, cancelar, baixar relatório de inconsistências).

import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { StatusBadge } from "../../components/importacoes/StatusBadge";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { ErrorState } from "../../components/ui/ErrorState";
import { BotaoModal, Modal } from "../../components/ui/Modal";
import { Paginacao } from "../../components/ui/Paginacao";
import { Skeleton } from "../../components/ui/Skeleton";
import {
  useCancelarImportacao,
  useDetalheImportacao,
  useErrosImportacao,
  useReprocessarImportacao,
} from "../../hooks/useImportacaoData";
import { useToast } from "../../hooks/useToast";
import { ApiError } from "../../services/httpClient";
import { urlRelatorioErros } from "../../services/importacaoService";
import { formatarDataHora, formatarDuracao, formatarNumero } from "../../utils/formatadores";

const TAMANHO_PAGINA_ERROS = 20;

function mensagemDeErro(erro: unknown): string {
  return erro instanceof ApiError ? erro.message : "Falha inesperada.";
}

export function ImportacaoDetalhePage() {
  const { importacaoId } = useParams<{ importacaoId: string }>();
  const navigate = useNavigate();
  const { mostrarToast } = useToast();
  const [paginaErros, setPaginaErros] = useState(1);
  const [modalReprocessar, setModalReprocessar] = useState(false);
  const [modalCancelar, setModalCancelar] = useState(false);

  const { data: importacao, isLoading, isError, refetch } = useDetalheImportacao(importacaoId);
  const erros = useErrosImportacao(importacaoId, paginaErros, TAMANHO_PAGINA_ERROS);
  const reprocessar = useReprocessarImportacao();
  const cancelar = useCancelarImportacao();

  const confirmarReprocessar = () => {
    if (!importacaoId) return;
    reprocessar.mutate(importacaoId, {
      onSuccess: (resultado) => {
        setModalReprocessar(false);
        mostrarToast(
          resultado.status === "FALHOU" ? "erro" : "sucesso",
          resultado.status === "FALHOU"
            ? "Reprocessamento recusado — provavelmente duplicado."
            : "Reprocessamento concluído.",
        );
        navigate(`/importacoes/${resultado.id}`);
      },
      onError: (erro) => {
        setModalReprocessar(false);
        mostrarToast("erro", mensagemDeErro(erro));
      },
    });
  };

  const confirmarCancelar = () => {
    if (!importacaoId) return;
    cancelar.mutate(importacaoId, {
      onSuccess: () => {
        setModalCancelar(false);
        mostrarToast("sucesso", "Importação cancelada.");
      },
      onError: (erro) => {
        setModalCancelar(false);
        mostrarToast("erro", mensagemDeErro(erro));
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <Link
          to="/importacoes"
          className="text-xs font-medium text-primary hover:text-primary-hover"
        >
          ← Voltar às Importações
        </Link>
        <h1 className="mt-1 text-2xl font-semibold text-slate-900">
          {isLoading ? (
            <Skeleton className="h-8 w-64" />
          ) : (
            (importacao?.nome_arquivo_original ?? "Importação")
          )}
        </h1>
      </div>

      {isError ? (
        <ErrorState mensagem="Não foi possível carregar a importação." onRetry={() => refetch()} />
      ) : isLoading || !importacao ? (
        <Card>
          <Skeleton className="h-40 w-full" />
        </Card>
      ) : (
        <>
          <Card
            titulo="Detalhes"
            acoes={
              <div className="flex gap-2">
                {importacao.status === "PENDENTE" && (
                  <button
                    type="button"
                    onClick={() => setModalCancelar(true)}
                    className="rounded-lg border border-danger/30 px-3 py-1.5 text-xs font-medium text-danger hover:bg-danger/10"
                  >
                    Cancelar
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setModalReprocessar(true)}
                  className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-surface-muted"
                >
                  Reprocessar
                </button>
              </div>
            }
          >
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm sm:grid-cols-3 lg:grid-cols-4">
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Status</dt>
                <dd className="mt-1">
                  <StatusBadge status={importacao.status} />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Tipo</dt>
                <dd className="mt-1 font-medium text-slate-900">{importacao.tipo_arquivo}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Versão</dt>
                <dd className="mt-1 font-medium text-slate-900">{importacao.versao}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">
                  Usuário responsável
                </dt>
                <dd className="mt-1 font-medium text-slate-900">{importacao.usuario_nome}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Competência</dt>
                <dd className="mt-1 text-slate-700">
                  {importacao.competencia
                    ? formatarDataHora(importacao.competencia).split(" ")[0]
                    : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">
                  Tempo de processamento
                </dt>
                <dd className="mt-1 text-slate-700">
                  {formatarDuracao(importacao.duracao_segundos)}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Linhas válidas</dt>
                <dd className="mt-1 text-success">{formatarNumero(importacao.linhas_validas)}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">
                  Linhas rejeitadas
                </dt>
                <dd className="mt-1 text-danger">{formatarNumero(importacao.linhas_invalidas)}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Enviado em</dt>
                <dd className="mt-1 text-slate-700">{formatarDataHora(importacao.criado_em)}</dd>
              </div>
              <div className="col-span-2 sm:col-span-3 lg:col-span-4">
                <dt className="text-xs uppercase tracking-wide text-slate-500">Hash SHA-256</dt>
                <dd className="mt-1 break-all font-mono text-xs text-slate-500">
                  {importacao.hash_sha256}
                </dd>
              </div>
            </dl>
          </Card>

          <Card
            titulo="Erros de Validação"
            acoes={
              (erros.data?.total_itens ?? 0) > 0 && (
                <a
                  href={urlRelatorioErros(importacao.id)}
                  className="text-xs font-medium text-primary hover:text-primary-hover"
                >
                  Baixar relatório (.csv)
                </a>
              )
            }
          >
            {erros.isLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : erros.isError ? (
              <ErrorState
                mensagem="Não foi possível carregar os erros."
                onRetry={() => erros.refetch()}
              />
            ) : !erros.data || erros.data.itens.length === 0 ? (
              <EmptyState
                titulo="Sem erros"
                descricao="Nenhuma linha foi rejeitada nesta importação."
              />
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                        <th className="py-2 pr-3 font-medium">Linha</th>
                        <th className="py-2 pr-3 font-medium">Coluna</th>
                        <th className="py-2 pr-3 font-medium">Valor Recebido</th>
                        <th className="py-2 pr-3 font-medium">Mensagem</th>
                      </tr>
                    </thead>
                    <tbody>
                      {erros.data.itens.map((erro) => (
                        <tr key={erro.id} className="border-b border-slate-100">
                          <td className="py-2 pr-3 text-slate-600">{erro.numero_linha}</td>
                          <td className="py-2 pr-3 text-slate-600">{erro.coluna ?? "—"}</td>
                          <td className="py-2 pr-3 text-slate-600">{erro.valor_recebido ?? "—"}</td>
                          <td className="py-2 pr-3 text-slate-700">{erro.mensagem_erro}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <Paginacao
                  pagina={paginaErros}
                  totalPaginas={Math.max(erros.data.total_paginas, 1)}
                  legenda={`${erros.data.total_itens} erro${erros.data.total_itens !== 1 ? "s" : ""} · página ${erros.data.pagina} de ${Math.max(erros.data.total_paginas, 1)}`}
                  onAnterior={() => setPaginaErros((atual) => atual - 1)}
                  onProxima={() => setPaginaErros((atual) => atual + 1)}
                />
              </>
            )}
          </Card>
        </>
      )}

      <Modal
        aberto={modalReprocessar}
        titulo="Reprocessar importação"
        onFechar={() => setModalReprocessar(false)}
      >
        <p className="text-sm text-slate-600">
          Isso executa uma nova importação a partir do mesmo arquivo, gerando uma nova versão dos
          dados. Se nada mudou no arquivo original, a tentativa será recusada como duplicada. Deseja
          continuar?
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <BotaoModal
            texto="Cancelar"
            variante="secondary"
            onClick={() => setModalReprocessar(false)}
          />
          <BotaoModal
            texto="Reprocessar"
            onClick={confirmarReprocessar}
            desabilitado={reprocessar.isPending}
          />
        </div>
      </Modal>

      <Modal
        aberto={modalCancelar}
        titulo="Cancelar importação"
        onFechar={() => setModalCancelar(false)}
      >
        <p className="text-sm text-slate-600">
          Esta importação ainda não foi processada. Deseja cancelá-la?
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <BotaoModal texto="Voltar" variante="secondary" onClick={() => setModalCancelar(false)} />
          <BotaoModal
            texto="Confirmar cancelamento"
            variante="danger"
            onClick={confirmarCancelar}
            desabilitado={cancelar.isPending}
          />
        </div>
      </Modal>
    </div>
  );
}
