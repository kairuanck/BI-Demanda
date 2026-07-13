// Cartão de KPI (DESIGN_SYSTEM.md, seções 4 e 6).

import type { ReactNode } from "react";

import { Skeleton } from "./Skeleton";

type TomKpi = "default" | "success" | "warning" | "danger";

interface KpiCardProps {
  titulo: string;
  valor?: ReactNode;
  descricao?: string;
  tom?: TomKpi;
  carregando?: boolean;
  naoAplicavel?: boolean;
  onClick?: () => void;
}

const CORES_TOM: Record<TomKpi, string> = {
  default: "text-slate-900",
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger",
};

export function KpiCard({
  titulo,
  valor,
  descricao,
  tom = "default",
  carregando = false,
  naoAplicavel = false,
  onClick,
}: KpiCardProps) {
  const interativo = Boolean(onClick);

  return (
    <div
      role={interativo ? "button" : undefined}
      tabIndex={interativo ? 0 : undefined}
      onClick={onClick}
      onKeyDown={(evento) => {
        if (interativo && (evento.key === "Enter" || evento.key === " ")) onClick?.();
      }}
      className={`rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow ${
        interativo ? "cursor-pointer hover:shadow-md" : ""
      }`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{titulo}</p>
      {carregando ? (
        <Skeleton className="mt-2 h-8 w-24" />
      ) : naoAplicavel ? (
        <p className="mt-1 text-2xl font-bold text-slate-300">N/A</p>
      ) : (
        <p className={`mt-1 text-2xl font-bold tabular-nums ${CORES_TOM[tom]}`}>{valor}</p>
      )}
      {descricao && !carregando && <p className="mt-1 text-xs text-slate-400">{descricao}</p>}
    </div>
  );
}
