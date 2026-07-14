// Badge de status de importação (DESIGN_SYSTEM.md, seção 6 — `Badge`),
// compartilhado entre o Histórico e o Detalhe de Importação (Sprint 6).

import type { StatusImportacao } from "../../types/importacao";

const RUBRICA: Record<StatusImportacao, { rotulo: string; classe: string }> = {
  PENDENTE: { rotulo: "Pendente", classe: "bg-slate-100 text-slate-600" },
  PROCESSANDO: { rotulo: "Processando", classe: "bg-primary/10 text-primary" },
  CONCLUIDA: { rotulo: "Concluída", classe: "bg-success/10 text-success" },
  CONCLUIDA_COM_ERROS: { rotulo: "Concluída com erros", classe: "bg-warning/10 text-warning" },
  FALHOU: { rotulo: "Falhou", classe: "bg-danger/10 text-danger" },
  REVERTIDA: { rotulo: "Revertida", classe: "bg-slate-100 text-slate-500" },
};

export function StatusBadge({ status }: { status: StatusImportacao }) {
  const { rotulo, classe } = RUBRICA[status];
  return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${classe}`}>{rotulo}</span>;
}
