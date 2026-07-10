// Cliente HTTP centralizado (FRONTEND.md, seção 6). Nesta fase expõe a
// base da API e o erro tipado padrão; injeção de token e renovação de
// sessão (API.md, seção 13 completa) chegam na Sprint 09 — ver
// docs/DECISIONS.md.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

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

export async function httpGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw await extrairErro(response);
  }
  return response.json() as Promise<T>;
}
