import { NavLink } from "react-router-dom";

const ITENS_MENU = [
  { rota: "/", rotulo: "Home" },
  { rota: "/dashboard", rotulo: "Dashboard" },
  { rota: "/importacoes", rotulo: "Importações" },
  { rota: "/configuracoes", rotulo: "Configurações" },
];

// DESIGN_SYSTEM.md, seção 7. Nesta Sprint, todos os itens são exibidos
// incondicionalmente; a filtragem por perfil (PERMISSOES.md) é
// implementada na Sprint 09 — ver docs/DECISIONS.md.
export function Sidebar() {
  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="px-6 py-5 text-lg font-semibold text-slate-900">Promotores BI</div>
      <nav className="flex flex-col gap-1 px-3">
        {ITENS_MENU.map((item) => (
          <NavLink
            key={item.rota}
            to={item.rota}
            end={item.rota === "/"}
            className={({ isActive }) =>
              `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-slate-600 hover:bg-surface-muted hover:text-slate-900"
              }`
            }
          >
            {item.rotulo}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
