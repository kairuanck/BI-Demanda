// Cliente HTTP centralizado (FRONTEND.md, seção 6). Nesta Sprint expõe
// apenas a base da API; injeção de token/tratamento de erro padronizado
// (API.md, seção 13) são implementados na Sprint 09 — ver docs/DECISIONS.md.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function httpGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Falha na requisição: ${response.status}`);
  }
  return response.json() as Promise<T>;
}
