// Container padrão de conteúdo (DESIGN_SYSTEM.md, seção 6).

import type { PropsWithChildren, ReactNode } from "react";

interface CardProps extends PropsWithChildren {
  titulo?: string;
  acoes?: ReactNode;
  className?: string;
}

export function Card({ titulo, acoes, className = "", children }: CardProps) {
  return (
    <div className={`rounded-lg border border-slate-200 bg-white p-4 shadow-sm ${className}`}>
      {(titulo || acoes) && (
        <div className="mb-3 flex items-center justify-between">
          {titulo && <h2 className="text-sm font-semibold text-slate-900">{titulo}</h2>}
          {acoes}
        </div>
      )}
      {children}
    </div>
  );
}
