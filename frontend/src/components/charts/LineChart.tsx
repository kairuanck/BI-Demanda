// Wrapper de gráfico de linha (GRAFICOS.md, seção 4.1).

import "./chartSetup";

import { Line } from "react-chartjs-2";

import { corComOpacidade, corDaSerie } from "./paletaCores";

export interface SerieLinha {
  rotulo: string;
  valores: number[];
}

interface LineChartProps {
  rotulos: string[];
  series: SerieLinha[];
  ariaLabel: string;
  formatarValor?: (valor: number) => string;
}

export function LineChart({ rotulos, series, ariaLabel, formatarValor }: LineChartProps) {
  return (
    <div role="img" aria-label={ariaLabel} className="h-72 w-full">
      <Line
        data={{
          labels: rotulos,
          datasets: series.map((serie, indice) => {
            const cor = corDaSerie(indice);
            return {
              label: serie.rotulo,
              data: serie.valores,
              borderColor: cor,
              backgroundColor: corComOpacidade(cor, 0.08),
              pointRadius: 3,
              tension: 0.3,
              fill: true,
            };
          }),
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: series.length > 1, position: "bottom" },
            tooltip: {
              callbacks: formatarValor
                ? {
                    label: (contexto) =>
                      `${contexto.dataset.label}: ${formatarValor(contexto.parsed.y ?? 0)}`,
                  }
                : undefined,
            },
          },
          scales: {
            y: { beginAtZero: true },
          },
        }}
      />
    </div>
  );
}
