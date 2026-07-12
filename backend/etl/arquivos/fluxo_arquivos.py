"""Fluxo físico de arquivos de importação (Sprint 2).

Estrutura criada automaticamente sob o diretório base (`STORAGE_DIR`):

    imports/
    ├── incoming/    # arquivos aguardando processamento
    ├── processed/   # processados com sucesso (movidos de incoming)
    ├── rejected/    # recusados (duplicados/estruturalmente inválidos)
    └── archive/     # cópia imutável de todo arquivo aceito (HASH.md, seção 8)

Arquivos nunca são excluídos — apenas movidos ou copiados.
"""

from __future__ import annotations

import shutil
from pathlib import Path


class FluxoArquivos:
    """Gerencia o ciclo de vida físico dos arquivos de importação."""

    def __init__(self, diretorio_base: Path) -> None:
        self.base = diretorio_base
        self.incoming = diretorio_base / "incoming"
        self.processed = diretorio_base / "processed"
        self.rejected = diretorio_base / "rejected"
        self.archive = diretorio_base / "archive"
        self.garantir_estrutura()

    def garantir_estrutura(self) -> None:
        for diretorio in (self.incoming, self.processed, self.rejected, self.archive):
            diretorio.mkdir(parents=True, exist_ok=True)

    def _mover_sem_sobrescrever(self, origem: Path, destino_dir: Path) -> Path:
        destino = destino_dir / origem.name
        contador = 1
        while destino.exists():
            destino = destino_dir / f"{origem.stem}_{contador}{origem.suffix}"
            contador += 1
        shutil.move(str(origem), str(destino))
        return destino

    def mover_para_processed(self, arquivo: Path) -> Path:
        return self._mover_sem_sobrescrever(arquivo, self.processed)

    def mover_para_rejected(self, arquivo: Path) -> Path:
        return self._mover_sem_sobrescrever(arquivo, self.rejected)

    def arquivar(
        self, arquivo: Path, tipo_arquivo: str, importacao_id: str, hash_sha256: str
    ) -> Path:
        """Copia o arquivo para `archive/` com nome rastreável (HASH.md, seção 8)."""

        nome = f"{tipo_arquivo}_{importacao_id}_{hash_sha256[:12]}{arquivo.suffix}"
        destino = self.archive / nome
        shutil.copy2(str(arquivo), str(destino))
        return destino
