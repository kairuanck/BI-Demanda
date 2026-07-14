// Campo de upload de arquivo .xlsx com drag-and-drop e seleção múltipla
// (DESIGN_SYSTEM.md, seção 6). Primeiro uso: Central de Importações
// (Sprint 6) — elimina a necessidade de terminal para importar dados.

import { useRef, useState, type DragEvent } from "react";

interface FileUploadProps {
  onArquivosSelecionados: (arquivos: File[]) => void;
  desabilitado?: boolean;
}

const EXTENSAO_ACEITA = ".xlsx";

function filtrarXlsx(lista: FileList | null): File[] {
  if (!lista) return [];
  return Array.from(lista).filter((arquivo) =>
    arquivo.name.toLowerCase().endsWith(EXTENSAO_ACEITA),
  );
}

export function FileUpload({ onArquivosSelecionados, desabilitado = false }: FileUploadProps) {
  const [arrastando, setArrastando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const aoSoltar = (evento: DragEvent<HTMLDivElement>) => {
    evento.preventDefault();
    setArrastando(false);
    if (desabilitado) return;
    const arquivos = filtrarXlsx(evento.dataTransfer.files);
    if (arquivos.length > 0) onArquivosSelecionados(arquivos);
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-disabled={desabilitado}
      onClick={() => !desabilitado && inputRef.current?.click()}
      onKeyDown={(evento) => {
        if (!desabilitado && (evento.key === "Enter" || evento.key === " ")) {
          evento.preventDefault();
          inputRef.current?.click();
        }
      }}
      onDragOver={(evento) => {
        evento.preventDefault();
        if (!desabilitado) setArrastando(true);
      }}
      onDragLeave={() => setArrastando(false)}
      onDrop={aoSoltar}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
        desabilitado
          ? "cursor-not-allowed border-slate-200 bg-slate-50 opacity-60"
          : arrastando
            ? "border-primary bg-primary/5"
            : "border-slate-300 hover:border-primary/50 hover:bg-surface-muted"
      }`}
    >
      <p className="text-sm font-medium text-slate-700">
        Arraste arquivos .xlsx aqui ou clique para selecionar
      </p>
      <p className="mt-1 text-xs text-slate-500">
        Aceita múltiplos arquivos — o tipo de cada um é identificado automaticamente.
      </p>
      <input
        ref={inputRef}
        type="file"
        accept={EXTENSAO_ACEITA}
        multiple
        disabled={desabilitado}
        className="sr-only"
        aria-label="Selecionar arquivos .xlsx para importação"
        onChange={(evento) => {
          const arquivos = filtrarXlsx(evento.target.files);
          if (arquivos.length > 0) onArquivosSelecionados(arquivos);
          evento.target.value = "";
        }}
      />
    </div>
  );
}
