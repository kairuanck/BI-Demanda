// Composição padrão de um bloco de gráfico do Dashboard: título + os três
// estados de interface (carregando/vazio/erro) — DESIGN_SYSTEM.md, seção 10;
// GRAFICOS.md, seção 7.

import type { PropsWithChildren, ReactNode } from "react";

import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { ErrorState } from "../ui/ErrorState";
import { Skeleton } from "../ui/Skeleton";

interface BlocoGraficoProps extends PropsWithChildren {
  titulo: string;
  carregando: boolean;
  comErro: boolean;
  vazio: boolean;
  onRetry?: () => void;
  acoes?: ReactNode;
  className?: string;
}

export function BlocoGrafico({
  titulo,
  carregando,
  comErro,
  vazio,
  onRetry,
  acoes,
  className,
  children,
}: BlocoGraficoProps) {
  return (
    <Card titulo={titulo} acoes={acoes} className={className}>
      {carregando ? (
        <Skeleton className="h-72 w-full" />
      ) : comErro ? (
        <ErrorState mensagem="Não foi possível carregar este gráfico." onRetry={onRetry} />
      ) : vazio ? (
        <EmptyState />
      ) : (
        children
      )}
    </Card>
  );
}
