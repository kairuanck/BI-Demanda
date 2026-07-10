import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ErrorBoundary } from "./ErrorBoundary";

function ComponenteQueQuebra(): never {
  throw new Error("falha proposital de teste");
}

describe("ErrorBoundary", () => {
  beforeEach(() => {
    // Silencia o log de erro esperado do React/JSDOM durante o teste.
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renderiza os filhos quando não há erro", () => {
    render(
      <ErrorBoundary>
        <p>conteúdo saudável</p>
      </ErrorBoundary>,
    );

    expect(screen.getByText("conteúdo saudável")).toBeInTheDocument();
  });

  it("exibe o fallback quando um componente filho lança exceção", () => {
    render(
      <ErrorBoundary>
        <ComponenteQueQuebra />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Algo deu errado")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Recarregar página" })).toBeInTheDocument();
  });
});
