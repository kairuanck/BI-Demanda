import { Component, type ErrorInfo, type PropsWithChildren } from "react";

interface ErrorBoundaryState {
  temErro: boolean;
}

// Tratamento global de erros de renderização do React (Sprint 1).
// Qualquer exceção não capturada na árvore de componentes exibe um
// fallback amigável em vez de uma tela em branco.
export class ErrorBoundary extends Component<PropsWithChildren, ErrorBoundaryState> {
  state: ErrorBoundaryState = { temErro: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { temErro: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Erro não tratado na interface:", error, info.componentStack);
  }

  render() {
    if (this.state.temErro) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-surface-muted p-8 text-center">
          <h1 className="text-xl font-semibold text-slate-900">Algo deu errado</h1>
          <p className="mt-2 max-w-md text-sm text-slate-500">
            Ocorreu um erro inesperado na interface. Recarregue a página para continuar.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-6 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover"
          >
            Recarregar página
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
