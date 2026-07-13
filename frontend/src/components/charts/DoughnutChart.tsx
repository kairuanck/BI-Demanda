// Wrapper de gráfico de rosca (GRAFICOS.md, seção 4.4).

import "./chartSetup";

import { Doughnut } from "react-chartjs-2";

import { corDaSerie } from "./paletaCores";

interface DoughnutChartProps {
  rotulos: string[];
  valores: number[];
  ariaLabel: string;
  formatarValor?: (valor: number) => string;
}

export function DoughnutChart({ rotulos, valores, ariaLabel, formatarValor }: DoughnutChartProps) {
  return (
    <div role="img" aria-label={ariaLabel} className="h-72 w-full">
      <Doughnut
        data={{
          labels: rotulos,
          datasets: [
            {
              data: valores,
              backgroundColor: rotulos.map((_, indice) => corDaSerie(indice)),
              borderWidth: 1,
              borderColor: "#FFFFFF",
            },
          ],
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "bottom" },
            tooltip: {
              callbacks: formatarValor
                ? { label: (contexto) => formatarValor(contexto.parsed) }
                : undefined,
            },
          },
        }}
      />
    </div>
  );
}
