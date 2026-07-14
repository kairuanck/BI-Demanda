import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { App } from "./App";
import { ErrorBoundary } from "./components/ui/ErrorBoundary";
import { ToastProvider } from "./components/ui/Toast";
import { ApiError } from "./services/httpClient";
import "./styles/index.css";

// React Query instalado na Sprint 0 (infraestrutura).
// Sprint 5 (autoauditoria): não faz sentido tentar de novo um 404 — o
// registro não existe e nunca vai existir na próxima tentativa. Sem essa
// exceção, o estado de erro amigável (ErrorState) só aparecia depois de
// ~7s de retries automáticos, mostrando skeletons "pendurados" nesse meio
// tempo. Outros erros (rede, 5xx) continuam com o retry padrão do React
// Query — só o 404 é definitivo.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (contagem, erro) =>
        erro instanceof ApiError && erro.status === 404 ? false : contagem < 3,
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);
