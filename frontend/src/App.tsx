import { Navigate, Route, Routes } from "react-router-dom";

import { Shell } from "./components/layout/Shell";
import { ClienteDetalhePage } from "./pages/clientes/ClienteDetalhePage";
import { ClientesPage } from "./pages/clientes/ClientesPage";
import { ConfiguracoesPage } from "./pages/configuracoes/ConfiguracoesPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { HomePage } from "./pages/home/HomePage";
import { ImportacoesPage } from "./pages/importacoes/ImportacoesPage";
import { PromotorDetalhePage } from "./pages/promotor/PromotorDetalhePage";

// Dashboard Executivo (Sprint 4) e Visão 360º do Cliente (Sprint 5,
// docs/DECISIONS.md, seção 22) implementados. Autenticação e o fluxo de
// upload de importações permanecem placeholders até as sprints
// correspondentes.
export function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/dashboard/promotores/:promotorId" element={<PromotorDetalhePage />} />
        <Route path="/clientes" element={<ClientesPage />} />
        <Route path="/clientes/:clienteId" element={<ClienteDetalhePage />} />
        <Route path="/importacoes" element={<ImportacoesPage />} />
        <Route path="/configuracoes" element={<ConfiguracoesPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
