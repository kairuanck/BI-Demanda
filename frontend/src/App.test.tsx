import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

function renderApp(rota: string) {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[rota]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok", database: "ok" }),
      }),
    );
  });

  it("renderiza a Sidebar com os itens de navegação", () => {
    renderApp("/");

    expect(screen.getByRole("link", { name: "Home" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Clientes" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Importações" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Configurações" })).toBeInTheDocument();
  });

  it("renderiza a HomePage na rota raiz", () => {
    renderApp("/");

    expect(screen.getByText("Bem-vindo ao Promotores BI")).toBeInTheDocument();
  });

  it("renderiza o Dashboard Executivo na rota de Dashboard", () => {
    renderApp("/dashboard");

    expect(screen.getByRole("heading", { name: "Dashboard Executivo" })).toBeInTheDocument();
  });

  it("redireciona rotas desconhecidas para a Home", () => {
    renderApp("/rota-inexistente");

    expect(screen.getByText("Bem-vindo ao Promotores BI")).toBeInTheDocument();
  });
});
