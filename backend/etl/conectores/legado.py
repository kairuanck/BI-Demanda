"""Adaptador dos importadores documentais da Sprint 2 ao contrato de conector.

Mantém vivos os layouts long documentados (IMPORTADOR.md) que não têm
fonte real correspondente (ex.: VISITAS), sem duplicar o pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from sqlalchemy.orm import Session

from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.layouts import Layout
from etl.readers import ler_excel
from etl.resultado import LinhaValida, ResultadoValidacao
from etl.validators import criar_contexto_validacao
from etl.validators.contexto import ContextoValidacao


class FuncaoValidacao(Protocol):
    def __call__(
        self, linhas: list[tuple[int, dict[str, Any]]], contexto: ContextoValidacao
    ) -> ResultadoValidacao: ...


class FuncaoCarga(Protocol):
    def __call__(
        self, session: Session, linhas: list[LinhaValida], importacao_id: str, usuario_id: str
    ) -> int: ...


class ConectorLegado(ConectorOrigem):
    """Pipeline documental: ler_excel(layout) → validador → loader."""

    def __init__(self, layout: Layout, validar: FuncaoValidacao, carregar: FuncaoCarga) -> None:
        self._layout = layout
        self._validar = validar
        self._carregar = carregar

    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        leitura = ler_excel(caminho, self._layout)
        if not leitura.valida:
            return ResultadoConector(erros=leitura.erros_estruturais, estrutural_invalido=True)

        contexto = criar_contexto_validacao(execucao.session)
        resultado = self._validar(leitura.linhas, contexto)

        persistidas = 0
        if resultado.linhas_validas:
            persistidas = self._carregar(
                execucao.session,
                resultado.linhas_validas,
                execucao.importacao_id,
                execucao.usuario_id,
            )
        return ResultadoConector(
            total_linhas=len(leitura.linhas), persistidas=persistidas, erros=resultado.erros
        )
