// Cliente HTTP centralizado (FRONTEND.md, seção 6). Nesta fase expõe a
// base da API e o erro tipado padrão; injeção de token e renovação de
// sessão (API.md, seção 13 completa) chegam na Sprint 09 — ver
// docs/DECISIONS.md.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

interface ErroApi {
  codigo: string;
  mensagem: string;
  detalhes?: unknown;
}

// Erro tipado no formato padrão do backend ({"erro": {codigo, mensagem, detalhes}}).
export class ApiError extends Error {
  readonly codigo: string;
  readonly status: number;
  readonly detalhes?: unknown;

  constructor(status: number, erro: ErroApi) {
    super(erro.mensagem);
    this.name = "ApiError";
    this.status = status;
    this.codigo = erro.codigo;
    this.detalhes = erro.detalhes;
  }
}

async function extrairErro(response: Response): Promise<ApiError> {
  try {
    const corpo = (await response.json()) as { erro?: ErroApi };
    if (corpo.erro?.codigo) {
      return new ApiError(response.status, corpo.erro);
    }
  } catch {
    // Corpo não-JSON (ex.: HTML de um proxy) — cai no erro genérico abaixo.
  }
  return new ApiError(response.status, {
    codigo: "ERRO_INTERNO",
    mensagem: `Falha na requisição: ${response.status}`,
  });
}

// Mesma extração de erro padrão da API, a partir do texto de uma resposta
// XHR (upload com progresso não usa `fetch` — ver `importacaoService.ts`).
export function erroApiDeTextoXhr(status: number, corpoTexto: string): ApiError {
  try {
    const corpo = JSON.parse(corpoTexto) as { erro?: ErroApi };
    if (corpo.erro?.codigo) {
      return new ApiError(status, corpo.erro);
    }
  } catch {
    // Corpo não-JSON — cai no erro genérico abaixo.
  }
  return new ApiError(status, {
    codigo: "ERRO_INTERNO",
    mensagem: `Falha na requisição: ${status}`,
  });
}

export type QueryParams = Record<string, string | number | null | undefined>;

function montarQueryString(params?: QueryParams): string {
  if (!params) return "";
  const busca = new URLSearchParams();
  for (const [chave, valor] of Object.entries(params)) {
    if (valor !== null && valor !== undefined && valor !== "") {
      busca.append(chave, String(valor));
    }
  }
  const texto = busca.toString();
  return texto ? `?${texto}` : "";
}

export async function httpGet<T>(path: string, params?: QueryParams): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}${montarQueryString(params)}`);
  if (!response.ok) {
    throw await extrairErro(response);
  }
  return response.json() as Promise<T>;
}

export async function httpPost<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { method: "POST" });
  if (!response.ok) {
    throw await extrairErro(response);
  }
  return response.json() as Promise<T>;
}
