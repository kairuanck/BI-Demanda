// Wrapper de gráfico de barras (GRAFICOS.md, seção 4.2).

import "./chartSetup";

import { Bar } from "react-chartjs-2";

import { corDaSerie } from "./paletaCores";

interface BarChartProps {
  rotulos: string[];
  valores: number[];
  ariaLabel: string;
  formatarValor?: (valor: number) => string;
  horizontal?: boolean;
}

export function BarChart({
  rotulos,
  valores,
  ariaLabel,
  formatarValor,
  horizontal = false,
}: BarChartProps) {
  return (
    <div role="img" aria-label={ariaLabel} className="h-72 w-full">
      <Bar
        data={{
          labels: rotulos,
          datasets: [
            {
              data: valores,
              backgroundColor: rotulos.map((_, indice) => corDaSerie(indice)),
              borderRadius: 4,
            },
          ],
        }}
        options={{
          indexAxis: horizontal ? "y" : "x",
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: formatarValor
                ? {
                    label: (contexto) =>
                      formatarValor((horizontal ? contexto.parsed.x : contexto.parsed.y) ?? 0),
                  }
                : undefined,
            },
          },
          scales: {
            [horizontal ? "x" : "y"]: { beginAtZero: true },
          },
        }}
      />
    </div>
  );
}
