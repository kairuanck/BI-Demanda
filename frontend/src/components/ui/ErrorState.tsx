// Estado de erro padronizado, com nova tentativa (DESIGN_SYSTEM.md, seção 10).

interface ErrorStateProps {
  mensagem?: string;
  onRetry?: () => void;
}

export function ErrorState({
  mensagem = "Não foi possível carregar os dados.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex h-full min-h-[160px] flex-col items-center justify-center rounded-lg border border-dashed border-danger/40 bg-danger/5 p-6 text-center">
      <p className="text-sm font-medium text-danger">{mensagem}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded-lg border border-danger/30 px-3 py-1.5 text-xs font-medium text-danger transition-colors hover:bg-danger/10"
        >
          Tentar novamente
        </button>
      )}
    </div>
  );
}
