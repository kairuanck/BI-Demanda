// Controles de paginação (Anterior/Próxima), compartilhados pelas duas
// tabelas paginadas da Central de Importações (Sprint 6) — histórico e
// erros de validação. Páginas de sprints anteriores (Clientes, Promotor)
// repetem esta mesma marcação; ver docs/DECISIONS.md para a decisão de
// não migrá-las nesta sprint.

interface PaginacaoProps {
  pagina: number;
  totalPaginas: number;
  legenda: string;
  onAnterior: () => void;
  onProxima: () => void;
}

export function Paginacao({
  pagina,
  totalPaginas,
  legenda,
  onAnterior,
  onProxima,
}: PaginacaoProps) {
  return (
    <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
      <span>{legenda}</span>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={pagina <= 1}
          onClick={onAnterior}
          className="rounded-lg border border-slate-200 px-3 py-1 font-medium text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Anterior
        </button>
        <button
          type="button"
          disabled={pagina >= totalPaginas}
          onClick={onProxima}
          className="rounded-lg border border-slate-200 px-3 py-1 font-medium text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Próxima
        </button>
      </div>
    </div>
  );
}
