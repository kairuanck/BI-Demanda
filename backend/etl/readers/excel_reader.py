"""Leitura de arquivos Excel (ETL.md, Etapa 2 — Extract).

Lê a primeira aba com cabeçalho na primeira linha, normaliza os nomes de
coluna e retorna as linhas brutas com seus números de linha originais
(base 1, cabeçalho = linha 1).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from etl.layouts import Layout
from etl.resultado import LINHA_ARQUIVO, ErroLinha


@dataclass
class LeituraExcel:
    """Resultado bruto da leitura: linhas com número original e erros estruturais."""

    linhas: list[tuple[int, dict[str, Any]]]
    erros_estruturais: list[ErroLinha]

    @property
    def valida(self) -> bool:
        return not self.erros_estruturais


def normalizar_nome_coluna(nome: str) -> str:
    """Maiúsculas, sem acento, espaços internos → underscore (IMPORTADOR.md, seção 2)."""

    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode("ascii")
    return "_".join(sem_acento.strip().upper().split())


def _celula_vazia(valor: Any) -> bool:
    return (
        valor is None or (isinstance(valor, float) and pd.isna(valor)) or str(valor).strip() == ""
    )


def ler_excel(caminho: Path, layout: Layout) -> LeituraExcel:
    try:
        df = pd.read_excel(caminho, sheet_name=0, dtype=object, engine="openpyxl")
    except Exception as exc:  # noqa: BLE001 - arquivo corrompido é erro estrutural, não bug
        return LeituraExcel(
            linhas=[],
            erros_estruturais=[ErroLinha(LINHA_ARQUIVO, f"Arquivo inválido ou corrompido: {exc}")],
        )

    df.columns = [normalizar_nome_coluna(str(c)) for c in df.columns]

    erros: list[ErroLinha] = []
    for coluna in layout.colunas_obrigatorias:
        if coluna not in df.columns:
            # VALIDADOR.md, EST-003
            erros.append(ErroLinha(LINHA_ARQUIVO, f"Coluna obrigatória ausente: {coluna}.", coluna))
    if erros:
        return LeituraExcel(linhas=[], erros_estruturais=erros)

    colunas_conhecidas = [c for c in df.columns if c in layout.todas]
    linhas: list[tuple[int, dict[str, Any]]] = []
    for indice, registro in enumerate(df.to_dict(orient="records")):
        numero_linha = indice + 2  # cabeçalho é a linha 1
        dados = {
            c: (None if _celula_vazia(registro.get(c)) else registro.get(c))
            for c in colunas_conhecidas
        }
        if all(v is None for v in dados.values()):
            continue  # ETL.md, Etapa 3, item 4: linha totalmente vazia é ignorada
        linhas.append((numero_linha, dados))

    if not linhas:
        # VALIDADOR.md, EST-002
        erros.append(ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados."))
        return LeituraExcel(linhas=[], erros_estruturais=erros)

    return LeituraExcel(linhas=linhas, erros_estruturais=[])
