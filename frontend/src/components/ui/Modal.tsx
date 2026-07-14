// Diálogo modal com overlay, usado em confirmações (DESIGN_SYSTEM.md, seção 6).
// Primeiro uso no projeto: confirmação antes de reprocessar uma importação
// (substitui/gera nova versão dos dados já carregados) — Sprint 6.

import { useEffect, useRef, type PropsWithChildren } from "react";

interface ModalProps extends PropsWithChildren {
  aberto: boolean;
  titulo: string;
  onFechar: () => void;
}

export function Modal({ aberto, titulo, onFechar, children }: ModalProps) {
  const referenciaTitulo = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (!aberto) return;
    referenciaTitulo.current?.focus();
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") onFechar();
    };
    document.addEventListener("keydown", aoTeclar);
    return () => document.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar]);

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-titulo"
        className="w-full max-w-md rounded-lg bg-white p-5 shadow-lg"
      >
        <div className="flex items-center justify-between">
          <h2
            id="modal-titulo"
            ref={referenciaTitulo}
            tabIndex={-1}
            className="text-base font-semibold text-slate-900 outline-none"
          >
            {titulo}
          </h2>
          <button
            type="button"
            onClick={onFechar}
            aria-label="Fechar"
            className="text-slate-400 hover:text-slate-600"
          >
            ✕
          </button>
        </div>
        <div className="mt-3">{children}</div>
      </div>
    </div>
  );
}

interface BotaoModalProps {
  texto: string;
  variante?: "primary" | "secondary" | "danger";
  onClick: () => void;
  desabilitado?: boolean;
}

const CLASSE_POR_VARIANTE: Record<NonNullable<BotaoModalProps["variante"]>, string> = {
  primary: "bg-primary text-white hover:bg-primary-hover",
  secondary: "border border-slate-200 text-slate-700 hover:bg-surface-muted",
  danger: "bg-danger text-white hover:bg-danger/90",
};

export function BotaoModal({
  texto,
  variante = "primary",
  onClick,
  desabilitado = false,
}: BotaoModalProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={desabilitado}
      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${CLASSE_POR_VARIANTE[variante]}`}
    >
      {texto}
    </button>
  );
}
