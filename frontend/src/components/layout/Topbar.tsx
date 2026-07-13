import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

// DESIGN_SYSTEM.md, seção 7. O Avatar/menu de logout real é implementado
// junto da autenticação (Sprint 09) — ver docs/DECISIONS.md.
// Busca global de clientes (Sprint 5, docs/DECISIONS.md, seção 22) —
// acessível de qualquer tela por estar no Topbar do Shell.
export function Topbar() {
  const [termo, setTermo] = useState("");
  const navigate = useNavigate();

  function buscar(evento: FormEvent) {
    evento.preventDefault();
    if (termo.trim()) {
      navigate(`/clientes?q=${encodeURIComponent(termo.trim())}`);
    }
  }

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-4 border-b border-slate-200 bg-white px-6">
      <span className="shrink-0 text-sm font-medium text-slate-500">
        Plataforma de BI para Promotores
      </span>
      <form onSubmit={buscar} className="w-full max-w-sm">
        <input
          type="search"
          value={termo}
          onChange={(evento) => setTermo(evento.target.value)}
          placeholder="Buscar cliente…"
          aria-label="Buscar cliente"
          className="w-full rounded-lg border border-slate-200 bg-surface-muted px-3 py-1.5 text-sm text-slate-700 focus:border-primary focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </form>
      <div className="h-8 w-8 shrink-0 rounded-full bg-slate-200" aria-label="Usuário" />
    </header>
  );
}
