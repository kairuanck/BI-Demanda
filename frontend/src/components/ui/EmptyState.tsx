// Estado vazio padronizado (DESIGN_SYSTEM.md, seção 10).

interface EmptyStateProps {
  titulo?: string;
  descricao?: string;
}

export function EmptyState({
  titulo = "Nenhum dado encontrado",
  descricao = "Não há dados para os filtros aplicados.",
}: EmptyStateProps) {
  return (
    <div className="flex h-full min-h-[160px] flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 p-6 text-center">
      <p className="text-sm font-medium text-slate-700">{titulo}</p>
      <p className="mt-1 text-xs text-slate-500">{descricao}</p>
    </div>
  );
}
