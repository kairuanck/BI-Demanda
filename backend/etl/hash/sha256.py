"""Cálculo de hash SHA-256 de arquivos importados (HASH.md, seção 2)."""

from __future__ import annotations

import hashlib
from pathlib import Path

_TAMANHO_BLOCO = 8192


def calcular_sha256_arquivo(caminho: Path) -> str:
    """Hash SHA-256 do conteúdo binário integral, em streaming."""

    sha256 = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(_TAMANHO_BLOCO):
            sha256.update(bloco)
    return sha256.hexdigest()


def calcular_sha256_bytes(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()
