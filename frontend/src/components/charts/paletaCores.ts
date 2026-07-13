// Paleta categórica única para gráficos com múltiplas séries (GRAFICOS.md, seção 3).
// A mesma posição de série sempre recebe a mesma cor em qualquer gráfico da aplicação.

export const PALETA_CORES = [
  "#1D4ED8", // primary
  "#15803D", // success
  "#B45309", // warning
  "#B91C1C", // danger
  "#0369A1", // info
  "#7C3AED", // violet-600
  "#0D9488", // teal-600
  "#C2410C", // orange-600
] as const;

export function corDaSerie(indice: number): string {
  return PALETA_CORES[indice % PALETA_CORES.length];
}

export function corComOpacidade(cor: string, opacidade: number): string {
  const alfa = Math.round(opacidade * 255)
    .toString(16)
    .padStart(2, "0");
  return `${cor}${alfa}`;
}
