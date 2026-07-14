// Camada de serviço da Central de Importações (Sprint 6). Upload usa
// `XMLHttpRequest` diretamente (não `fetch`) porque só o XHR expõe evento
// de progresso do corpo da requisição (`upload.onprogress`), necessário
// para a barra de progresso real da tela de Nova Importação.

import { API_BASE_URL, erroApiDeTextoXhr, httpGet, httpPost } from "./httpClient";
import type {
  FiltrosHistoricoImportacoes,
  Importacao,
  PaginaErrosImportacao,
  PaginaImportacoes,
} from "../types/importacao";

export function listarImportacoes(
  pagina: number,
  tamanhoPagina: number,
  filtros: FiltrosHistoricoImportacoes = {},
): Promise<PaginaImportacoes> {
  return httpGet<PaginaImportacoes>("/importacoes", {
    pagina,
    tamanho_pagina: tamanhoPagina,
    tipo_arquivo: filtros.tipo_arquivo,
    status: filtros.status,
  });
}

export function obterImportacao(importacaoId: string): Promise<Importacao> {
  return httpGet<Importacao>(`/importacoes/${importacaoId}`);
}

export function listarErrosImportacao(
  importacaoId: string,
  pagina: number,
  tamanhoPagina: number,
): Promise<PaginaErrosImportacao> {
  return httpGet<PaginaErrosImportacao>(`/importacoes/${importacaoId}/erros`, {
    pagina,
    tamanho_pagina: tamanhoPagina,
  });
}

export function reprocessarImportacao(importacaoId: string): Promise<Importacao> {
  return httpPost<Importacao>(`/importacoes/${importacaoId}/reprocessar`);
}

export function cancelarImportacao(importacaoId: string): Promise<Importacao> {
  return httpPost<Importacao>(`/importacoes/${importacaoId}/cancelar`);
}

export function urlRelatorioErros(importacaoId: string): string {
  return `${API_BASE_URL}/importacoes/${importacaoId}/erros/relatorio`;
}

export interface Competencia {
  ano: number;
  mes: number;
}

export interface EnvioImportacao {
  promessa: Promise<Importacao>;
  cancelar: () => void;
}

export function enviarImportacao(
  arquivo: File,
  competencia: Competencia | undefined,
  aoProgredir: (percentual: number) => void,
): EnvioImportacao {
  const xhr = new XMLHttpRequest();
  const formData = new FormData();
  formData.append("arquivo", arquivo);
  if (competencia) {
    formData.append("ano_competencia", String(competencia.ano));
    formData.append("mes_competencia", String(competencia.mes));
  }

  const promessa = new Promise<Importacao>((resolve, reject) => {
    xhr.open("POST", `${API_BASE_URL}/importacoes/upload`);
    xhr.upload.onprogress = (evento) => {
      if (evento.lengthComputable) {
        aoProgredir(Math.round((evento.loaded / evento.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText) as Importacao);
      } else {
        reject(erroApiDeTextoXhr(xhr.status, xhr.responseText));
      }
    };
    xhr.onerror = () => reject(new Error("Falha de rede durante o envio do arquivo."));
    xhr.onabort = () => reject(new DOMException("Envio cancelado.", "AbortError"));
    xhr.send(formData);
  });

  return { promessa, cancelar: () => xhr.abort() };
}
