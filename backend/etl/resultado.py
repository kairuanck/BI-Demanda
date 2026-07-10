"""Estruturas de resultado compartilhadas pelo pipeline ETL."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Linha "0" identifica erros de arquivo (estruturais/duplicidade),
# distinguindo-os dos erros de linha de dados (>= 2, pois 1 é o cabeçalho).
LINHA_ARQUIVO = 0


@dataclass(frozen=True)
class ErroLinha:
    """Um erro de validação associado a uma linha do arquivo."""

    numero_linha: int
    mensagem: str
    coluna: str | None = None
    valor_recebido: str | None = None


@dataclass
class LinhaValida:
    """Linha aprovada na validação, com valores já convertidos/tipados."""

    numero_linha: int
    dados: dict[str, Any]


@dataclass
class ResultadoValidacao:
    """Saída da etapa de validação de um arquivo."""

    linhas_validas: list[LinhaValida] = field(default_factory=list)
    erros: list[ErroLinha] = field(default_factory=list)

    @property
    def total_linhas(self) -> int:
        linhas_com_erro = {e.numero_linha for e in self.erros if e.numero_linha != LINHA_ARQUIVO}
        linhas_ok = {linha.numero_linha for linha in self.linhas_validas}
        return len(linhas_com_erro | linhas_ok)
