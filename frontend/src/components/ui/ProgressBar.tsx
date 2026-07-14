// Barra de progresso (DESIGN_SYSTEM.md, seção 6). Primeiro uso: progresso
// de envio de arquivo na Central de Importações (Sprint 6).

interface ProgressBarProps {
  percentual: number;
  tom?: "default" | "success" | "danger";
}

const COR_POR_TOM: Record<NonNullable<ProgressBarProps["tom"]>, string> = {
  default: "bg-primary",
  success: "bg-success",
  danger: "bg-danger",
};

export function ProgressBar({ percentual, tom = "default" }: ProgressBarProps) {
  const valor = Math.min(100, Math.max(0, percentual));
  return (
    <div
      role="progressbar"
      aria-valuenow={valor}
      aria-valuemin={0}
      aria-valuemax={100}
      className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200"
    >
      <div
        className={`h-full rounded-full transition-all ${COR_POR_TOM[tom]}`}
        style={{ width: `${valor}%` }}
      />
    </div>
  );
}
