// Estado dos filtros globais do Dashboard, refletido na query string da URL
// (UX.md, seção 11, item 3: estado preservado via query string).

import { useSearchParams } from "react-router-dom";

import type { FiltrosDashboard } from "../types/dashboard";

const CHAVES = [
  "ano",
  "mes",
  "uf",
  "laboratorio_id",
  "tipo_promotor_id",
  "sistema_origem",
  "supervisor_id",
  "promotor_id",
] as const;

export function useFiltrosDashboard(): {
  filtros: FiltrosDashboard;
  definirFiltro: (chave: (typeof CHAVES)[number], valor: string) => void;
  limparFiltros: () => void;
  totalFiltrosAtivos: number;
} {
  const [searchParams, setSearchParams] = useSearchParams();

  const filtros: FiltrosDashboard = {
    ano: searchParams.get("ano") ? Number(searchParams.get("ano")) : undefined,
    mes: searchParams.get("mes") ? Number(searchParams.get("mes")) : undefined,
    uf: searchParams.get("uf") ?? undefined,
    laboratorio_id: searchParams.get("laboratorio_id") ?? undefined,
    tipo_promotor_id: searchParams.get("tipo_promotor_id") ?? undefined,
    sistema_origem: searchParams.get("sistema_origem") ?? undefined,
    supervisor_id: searchParams.get("supervisor_id") ?? undefined,
    promotor_id: searchParams.get("promotor_id") ?? undefined,
  };

  function definirFiltro(chave: (typeof CHAVES)[number], valor: string) {
    const proximo = new URLSearchParams(searchParams);
    if (valor) {
      proximo.set(chave, valor);
    } else {
      proximo.delete(chave);
    }
    setSearchParams(proximo, { replace: true });
  }

  function limparFiltros() {
    const proximo = new URLSearchParams(searchParams);
    for (const chave of CHAVES) proximo.delete(chave);
    setSearchParams(proximo, { replace: true });
  }

  const totalFiltrosAtivos = CHAVES.filter((chave) => searchParams.get(chave)).length;

  return { filtros, definirFiltro, limparFiltros, totalFiltrosAtivos };
}
