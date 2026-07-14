// Contexto e hook do Toast (DESIGN_SYSTEM.md, seção 6) — separados do
// componente `ToastProvider` (`components/ui/Toast.tsx`) para não misturar
// exports de componente e de hook no mesmo arquivo (react-refresh/only-export-components).

import { createContext, useContext } from "react";

export type TipoToast = "sucesso" | "erro" | "aviso";

export interface ToastContextValue {
  mostrarToast: (tipo: TipoToast, mensagem: string) => void;
}

export const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const contexto = useContext(ToastContext);
  if (!contexto) {
    throw new Error("useToast deve ser usado dentro de <ToastProvider>.");
  }
  return contexto;
}
