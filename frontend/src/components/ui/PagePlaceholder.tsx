interface PagePlaceholderProps {
  titulo: string;
  descricao: string;
}

// Estado "em construção" (SPRINT_09.md, seção 8, riscos): usado pelas
// rotas cujo conteúdo de negócio ainda não foi implementado nesta Sprint.
export function PagePlaceholder({ titulo, descricao }: PagePlaceholderProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
      <h1 className="text-xl font-semibold text-slate-900">{titulo}</h1>
      <p className="mt-2 max-w-md text-sm text-slate-500">{descricao}</p>
      <span className="mt-4 rounded-full bg-surface-muted px-3 py-1 text-xs font-medium text-slate-500">
        Em construção — infraestrutura da Sprint 0
      </span>
    </div>
  );
}
