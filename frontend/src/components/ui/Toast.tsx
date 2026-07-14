// Notificação temporária não bloqueante (DESIGN_SYSTEM.md, seção 6).
// Primeiro uso no projeto: a Central de Importações (Sprint 6) é a
// primeira tela a precisar de feedback assíncrono de sucesso/erro que não
// bloqueia a navegação (upload, cancelamento, reprocessamento).

import { useCallback, useMemo, useRef, useState, type PropsWithChildren } from "react";

import { ToastContext, type TipoToast } from "../../hooks/useToast";

interface Toast {
  id: number;
  tipo: TipoToast;
  mensagem: string;
}

const DURACAO_MS = 6000;

const ESTILO_POR_TIPO: Record<TipoToast, string> = {
  sucesso: "border-success/30 bg-white text-success",
  erro: "border-danger/30 bg-white text-danger",
  aviso: "border-warning/30 bg-white text-warning",
};

const ICONE_POR_TIPO: Record<TipoToast, string> = {
  sucesso: "✓",
  erro: "✕",
  aviso: "!",
};

export function ToastProvider({ children }: PropsWithChildren) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const proximoId = useRef(0);

  const removerToast = useCallback((id: number) => {
    setToasts((atual) => atual.filter((toast) => toast.id !== id));
  }, []);

  const mostrarToast = useCallback(
    (tipo: TipoToast, mensagem: string) => {
      const id = proximoId.current++;
      setToasts((atual) => [...atual, { id, tipo, mensagem }]);
      window.setTimeout(() => removerToast(id), DURACAO_MS);
    },
    [removerToast],
  );

  const valor = useMemo(() => ({ mostrarToast }), [mostrarToast]);

  return (
    <ToastContext.Provider value={valor}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-sm flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role={toast.tipo === "erro" ? "alert" : "status"}
            aria-live={toast.tipo === "erro" ? "assertive" : "polite"}
            className={`pointer-events-auto flex items-start gap-2 rounded-lg border px-4 py-3 text-sm font-medium shadow-md ${ESTILO_POR_TIPO[toast.tipo]}`}
          >
            <span aria-hidden="true">{ICONE_POR_TIPO[toast.tipo]}</span>
            <p className="flex-1 text-slate-700">{toast.mensagem}</p>
            <button
              type="button"
              onClick={() => removerToast(toast.id)}
              aria-label="Fechar notificação"
              className="text-slate-400 hover:text-slate-600"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
