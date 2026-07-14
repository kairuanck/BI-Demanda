// Central de Importações (Sprint 6) — elimina a necessidade de terminal
// para importar dados: upload via drag & drop com progresso real, fila de
// múltiplos arquivos e histórico completo (docs/DECISIONS.md).

import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { StatusBadge } from "../../components/importacoes/StatusBadge";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { ErrorState } from "../../components/ui/ErrorState";
import { FileUpload } from "../../components/ui/FileUpload";
import { Paginacao } from "../../components/ui/Paginacao";
import { ProgressBar } from "../../components/ui/ProgressBar";
import { Skeleton } from "../../components/ui/Skeleton";
import { useHistoricoImportacoes, useInvalidarAposImportacao } from "../../hooks/useImportacaoData";
import { useToast } from "../../hooks/useToast";
import { enviarImportacao } from "../../services/importacaoService";
import type {
  ArquivoNaFila,
  FiltrosHistoricoImportacoes,
  StatusImportacao,
  TipoArquivoImportacao,
} from "../../types/importacao";
import { CLASSE_SELECT } from "../../utils/estilos";
import { NOMES_MES, formatarDataHora, formatarNumero } from "../../utils/formatadores";

const TAMANHO_PAGINA = 20;

const TIPOS_ARQUIVO: TipoArquivoImportacao[] = [
  "CLIENTES",
  "CARTEIRA",
  "FATURAMENTO",
  "CHECKLIST",
  "VISITAS",
  "WECHECK",
  "PAINEL_AVERT",
  "SB_PRODUTOS",
];

const STATUS_LISTA: StatusImportacao[] = [
  "PENDENTE",
  "PROCESSANDO",
  "CONCLUIDA",
  "CONCLUIDA_COM_ERROS",
  "FALHOU",
  "REVERTIDA",
];

function novoIdLocal(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function ImportacoesPage() {
  const navigate = useNavigate();
  const { mostrarToast } = useToast();
  const invalidarAposImportacao = useInvalidarAposImportacao();

  const anoAtual = new Date().getFullYear();
  const [anoCompetencia, setAnoCompetencia] = useState("");
  const [mesCompetencia, setMesCompetencia] = useState("");

  const [fila, setFila] = useState<ArquivoNaFila[]>([]);
  const cancelamentos = useRef(new Map<string, () => void>());

  const [filtros, setFiltros] = useState<FiltrosHistoricoImportacoes>({});
  const [pagina, setPagina] = useState(1);
  const historico = useHistoricoImportacoes(pagina, TAMANHO_PAGINA, filtros);

  const atualizarItemFila = useCallback((idLocal: string, alteracao: Partial<ArquivoNaFila>) => {
    setFila((atual) =>
      atual.map((item) => (item.idLocal === idLocal ? { ...item, ...alteracao } : item)),
    );
  }, []);

  const enviarArquivos = useCallback(
    (arquivos: File[]) => {
      const competencia =
        anoCompetencia && mesCompetencia
          ? { ano: Number(anoCompetencia), mes: Number(mesCompetencia) }
          : undefined;

      const novosItens: ArquivoNaFila[] = arquivos.map((arquivo) => ({
        idLocal: novoIdLocal(),
        arquivo,
        estado: "enviando",
        progresso: 0,
      }));
      setFila((atual) => [...novosItens, ...atual]);

      for (const item of novosItens) {
        const { promessa, cancelar } = enviarImportacao(item.arquivo, competencia, (percentual) =>
          atualizarItemFila(item.idLocal, { progresso: percentual, estado: "enviando" }),
        );
        cancelamentos.current.set(item.idLocal, cancelar);

        promessa
          .then((resultado) => {
            atualizarItemFila(item.idLocal, {
              estado: resultado.status === "FALHOU" ? "erro" : "concluido",
              progresso: 100,
              resultado,
              mensagemErro:
                resultado.status === "FALHOU"
                  ? "Importação recusada — veja os detalhes."
                  : undefined,
            });
            if (resultado.status === "FALHOU") {
              mostrarToast("erro", `${item.arquivo.name}: importação recusada.`);
            } else {
              mostrarToast("sucesso", `${item.arquivo.name}: importação concluída.`);
            }
            invalidarAposImportacao(resultado);
          })
          .catch((erro: unknown) => {
            if (erro instanceof DOMException && erro.name === "AbortError") {
              atualizarItemFila(item.idLocal, { estado: "cancelado" });
              return;
            }
            const mensagem = erro instanceof Error ? erro.message : "Falha desconhecida no envio.";
            atualizarItemFila(item.idLocal, { estado: "erro", mensagemErro: mensagem });
            mostrarToast("erro", `${item.arquivo.name}: ${mensagem}`);
          })
          .finally(() => cancelamentos.current.delete(item.idLocal));
      }
    },
    [anoCompetencia, mesCompetencia, atualizarItemFila, mostrarToast, invalidarAposImportacao],
  );

  const cancelarEnvio = (idLocal: string) => cancelamentos.current.get(idLocal)?.();
  const removerDaFila = (idLocal: string) =>
    setFila((atual) => atual.filter((item) => item.idLocal !== idLocal));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Importações</h1>
        <p className="mt-1 text-sm text-slate-500">
          Envie planilhas .xlsx diretamente pelo navegador — o tipo de cada arquivo é identificado
          automaticamente pela estrutura, sem necessidade de terminal.
        </p>
      </div>

      <Card titulo="Nova Importação">
        <div className="mb-3 flex flex-wrap items-center gap-2 text-sm text-slate-600">
          <span>Competência (obrigatória para Carteira e Painel Avert):</span>
          <select
            className={CLASSE_SELECT}
            value={anoCompetencia}
            onChange={(evento) => setAnoCompetencia(evento.target.value)}
          >
            <option value="">Ano</option>
            {Array.from({ length: 5 }, (_, indice) => anoAtual - 3 + indice).map((ano) => (
              <option key={ano} value={ano}>
                {ano}
              </option>
            ))}
          </select>
          <select
            className={CLASSE_SELECT}
            value={mesCompetencia}
            onChange={(evento) => setMesCompetencia(evento.target.value)}
          >
            <option value="">Mês</option>
            {NOMES_MES.map((nome, indice) => (
              <option key={nome} value={indice + 1}>
                {nome}
              </option>
            ))}
          </select>
        </div>

        <FileUpload onArquivosSelecionados={enviarArquivos} />

        {fila.length > 0 && (
          <ul className="mt-4 space-y-2">
            {fila.map((item) => (
              <li key={item.idLocal} className="rounded-lg border border-slate-200 p-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-slate-900">{item.arquivo.name}</p>
                    <p className="text-xs text-slate-500">
                      {item.estado === "enviando" && `Enviando… ${item.progresso}%`}
                      {item.estado === "concluido" &&
                        `${item.resultado?.tipo_arquivo} — ${item.resultado?.status === "CONCLUIDA_COM_ERROS" ? "concluída com erros" : "concluída"}`}
                      {item.estado === "erro" && (item.mensagemErro ?? "Falha no envio.")}
                      {item.estado === "cancelado" && "Envio cancelado."}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    {item.estado === "concluido" && item.resultado && (
                      <button
                        type="button"
                        onClick={() => navigate(`/importacoes/${item.resultado!.id}`)}
                        className="text-xs font-medium text-primary hover:text-primary-hover"
                      >
                        Ver detalhes
                      </button>
                    )}
                    {item.estado === "enviando" && (
                      <button
                        type="button"
                        onClick={() => cancelarEnvio(item.idLocal)}
                        className="text-xs font-medium text-slate-500 hover:text-danger"
                      >
                        Cancelar
                      </button>
                    )}
                    {item.estado !== "enviando" && (
                      <button
                        type="button"
                        onClick={() => removerDaFila(item.idLocal)}
                        aria-label={`Remover ${item.arquivo.name} da fila`}
                        className="text-slate-400 hover:text-slate-600"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
                {item.estado === "enviando" && (
                  <div className="mt-2">
                    <ProgressBar percentual={item.progresso} />
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card titulo="Histórico de Importações">
        <div className="mb-3 flex flex-wrap gap-2">
          <select
            className={CLASSE_SELECT}
            value={filtros.tipo_arquivo ?? ""}
            onChange={(evento) => {
              setFiltros((atual) => ({
                ...atual,
                tipo_arquivo: (evento.target.value || undefined) as
                  TipoArquivoImportacao | undefined,
              }));
              setPagina(1);
            }}
          >
            <option value="">Todos os tipos</option>
            {TIPOS_ARQUIVO.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
          <select
            className={CLASSE_SELECT}
            value={filtros.status ?? ""}
            onChange={(evento) => {
              setFiltros((atual) => ({
                ...atual,
                status: (evento.target.value || undefined) as StatusImportacao | undefined,
              }));
              setPagina(1);
            }}
          >
            <option value="">Todos os status</option>
            {STATUS_LISTA.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {historico.isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, indice) => (
              <Skeleton key={indice} className="h-10 w-full" />
            ))}
          </div>
        ) : historico.isError ? (
          <ErrorState
            mensagem="Não foi possível carregar o histórico de importações."
            onRetry={() => historico.refetch()}
          />
        ) : !historico.data || historico.data.itens.length === 0 ? (
          <EmptyState
            titulo="Nenhuma importação encontrada"
            descricao="Envie um arquivo acima ou ajuste os filtros."
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                    <th className="py-2 pr-3 font-medium">Tipo</th>
                    <th className="py-2 pr-3 font-medium">Arquivo</th>
                    <th className="py-2 pr-3 font-medium">Versão</th>
                    <th className="py-2 pr-3 font-medium">Status</th>
                    <th className="py-2 pr-3 font-medium">Usuário</th>
                    <th className="py-2 pr-3 font-medium">Linhas</th>
                    <th className="py-2 pr-3 font-medium">Data</th>
                  </tr>
                </thead>
                <tbody>
                  {historico.data.itens.map((importacao) => (
                    <tr
                      key={importacao.id}
                      role="button"
                      tabIndex={0}
                      onClick={() => navigate(`/importacoes/${importacao.id}`)}
                      onKeyDown={(evento) => {
                        if (evento.key === "Enter" || evento.key === " ") {
                          evento.preventDefault();
                          navigate(`/importacoes/${importacao.id}`);
                        }
                      }}
                      className="cursor-pointer border-b border-slate-100 transition-colors hover:bg-surface-muted focus:outline-none focus:ring-2 focus:ring-primary/40"
                    >
                      <td className="py-2 pr-3 font-medium text-slate-900">
                        {importacao.tipo_arquivo}
                      </td>
                      <td className="max-w-[220px] truncate py-2 pr-3 text-slate-600">
                        {importacao.nome_arquivo_original}
                      </td>
                      <td className="py-2 pr-3 text-slate-600">{importacao.versao}</td>
                      <td className="py-2 pr-3">
                        <StatusBadge status={importacao.status} />
                      </td>
                      <td className="py-2 pr-3 text-slate-600">{importacao.usuario_nome}</td>
                      <td className="py-2 pr-3 text-slate-600">
                        {formatarNumero(importacao.linhas_validas)}/
                        {formatarNumero(importacao.linhas_invalidas)}
                      </td>
                      <td className="py-2 pr-3 text-slate-600">
                        {formatarDataHora(importacao.criado_em)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Paginacao
              pagina={pagina}
              totalPaginas={Math.max(historico.data.total_paginas, 1)}
              legenda={`${historico.data.total_itens} importaç${historico.data.total_itens !== 1 ? "ões" : "ão"} · página ${historico.data.pagina} de ${Math.max(historico.data.total_paginas, 1)}`}
              onAnterior={() => setPagina((atual) => atual - 1)}
              onProxima={() => setPagina((atual) => atual + 1)}
            />
          </>
        )}
      </Card>
    </div>
  );
}
