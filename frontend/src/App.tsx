import { Navigate, Route, Routes } from "react-router-dom";

import { Shell } from "./components/layout/Shell";
import { ClienteDetalhePage } from "./pages/clientes/ClienteDetalhePage";
import { ClientesPage } from "./pages/clientes/ClientesPage";
import { ConfiguracoesPage } from "./pages/configuracoes/ConfiguracoesPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { HomePage } from "./pages/home/HomePage";
import { ImportacaoDetalhePage } from "./pages/importacoes/ImportacaoDetalhePage";
import { ImportacoesPage } from "./pages/importacoes/ImportacoesPage";
import { PromotorDetalhePage } from "./pages/promotor/PromotorDetalhePage";

// Dashboard Executivo (Sprint 4), Visão 360º do Cliente (Sprint 5) e
// Central de Importações (Sprint 6, docs/DECISIONS.md) implementados.
// Autenticação permanece placeholder até a sprint correspondente.
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
        <Route path="/importacoes/:importacaoId" element={<ImportacaoDetalhePage />} />
        <Route path="/configuracoes" element={<ConfiguracoesPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
