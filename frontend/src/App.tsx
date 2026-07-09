import { Navigate, Route, Routes } from "react-router-dom";

import { Shell } from "./components/layout/Shell";
import { ConfiguracoesPage } from "./pages/configuracoes/ConfiguracoesPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { HomePage } from "./pages/home/HomePage";
import { ImportacoesPage } from "./pages/importacoes/ImportacoesPage";

// Rotas da Sprint 0 (SPRINT_00.md): apenas placeholders de navegação.
// Autenticação, dashboards reais e importação são implementados nas
// Sprints 02, 08/10 e 03-07/11, respectivamente — ver docs/DECISIONS.md.
export function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/importacoes" element={<ImportacoesPage />} />
        <Route path="/configuracoes" element={<ConfiguracoesPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
