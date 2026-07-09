// DESIGN_SYSTEM.md, seção 7. O Avatar/menu de logout real é implementado
// junto da autenticação (Sprint 09) — ver docs/DECISIONS.md.
export function Topbar() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
      <span className="text-sm font-medium text-slate-500">Plataforma de BI para Promotores</span>
      <div className="h-8 w-8 rounded-full bg-slate-200" aria-label="Usuário" />
    </header>
  );
}
