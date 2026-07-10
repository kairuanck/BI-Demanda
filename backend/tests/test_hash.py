"""Testes do cálculo de hash SHA-256 (HASH.md, seção 2)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from etl.hash import calcular_sha256_arquivo, calcular_sha256_bytes


def test_hash_streaming_equivale_ao_hash_direto(tmp_path: Path) -> None:
    conteudo = b"conteudo binario de teste " * 10_000  # maior que um bloco de 8192 bytes
    arquivo = tmp_path / "arquivo.bin"
    arquivo.write_bytes(conteudo)

    assert calcular_sha256_arquivo(arquivo) == hashlib.sha256(conteudo).hexdigest()


def test_hash_bytes_e_deterministico() -> None:
    assert calcular_sha256_bytes(b"abc") == calcular_sha256_bytes(b"abc")
    assert calcular_sha256_bytes(b"abc") != calcular_sha256_bytes(b"abd")


def test_hash_detecta_qualquer_alteracao_de_conteudo(tmp_path: Path) -> None:
    original = tmp_path / "a.xlsx"
    alterado = tmp_path / "b.xlsx"
    original.write_bytes(b"planilha original")
    alterado.write_bytes(b"planilha originaU")  # um único byte diferente

    assert calcular_sha256_arquivo(original) != calcular_sha256_arquivo(alterado)
