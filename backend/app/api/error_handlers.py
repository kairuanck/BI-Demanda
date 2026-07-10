"""Tratamento global de erros (BACKEND.md, seção 8; API.md, seção 13).

Traduz exceções de domínio em respostas HTTP no formato padrão
`{"erro": {"codigo", "mensagem", "detalhes"}}` e registra em nível
CRITICAL qualquer exceção não mapeada (LOGS.md, seção 5, item 4).
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.excecoes import (
    ArquivoDuplicadoError,
    ArquivoInvalidoError,
    DominioError,
    PermissaoNegadaError,
    RegistroNaoEncontradoError,
    ValidacaoFalhouError,
)

logger = logging.getLogger("promotores_bi.errors")

# Mapeamento exceção de domínio -> (status HTTP, código de erro da API.md, seção 13).
MAPEAMENTO_EXCECOES: dict[type[DominioError], tuple[int, str]] = {
    RegistroNaoEncontradoError: (404, "RECURSO_NAO_ENCONTRADO"),
    PermissaoNegadaError: (403, "PERMISSAO_NEGADA"),
    ValidacaoFalhouError: (422, "VALIDACAO_FALHOU"),
    ArquivoDuplicadoError: (409, "ARQUIVO_DUPLICADO"),
    ArquivoInvalidoError: (400, "ARQUIVO_INVALIDO"),
}


def _resposta_erro(
    status_code: int,
    codigo: str,
    mensagem: str,
    detalhes: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"erro": {"codigo": codigo, "mensagem": mensagem, "detalhes": detalhes}},
    )


def registrar_error_handlers(app: FastAPI) -> None:
    """Registra os manipuladores globais de exceção na aplicação."""

    @app.exception_handler(DominioError)
    async def tratar_erro_de_dominio(request: Request, exc: DominioError) -> JSONResponse:
        status_code, codigo = MAPEAMENTO_EXCECOES.get(type(exc), (400, "CONFLITO_DE_DADOS"))
        logger.warning(
            "Erro de domínio em %s %s: %s (%s)",
            request.method,
            request.url.path,
            exc,
            codigo,
        )
        return _resposta_erro(status_code, codigo, str(exc) or codigo)

    @app.exception_handler(RequestValidationError)
    async def tratar_erro_de_validacao_de_entrada(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _resposta_erro(
            422,
            "VALIDACAO_FALHOU",
            "Dados de entrada inválidos.",
            detalhes=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def tratar_erro_nao_mapeado(request: Request, exc: Exception) -> JSONResponse:
        # LOGS.md, seção 5, item 4: exceção não capturada é registrada em
        # CRITICAL antes de retornar um 500 genérico ao cliente.
        logger.critical(
            "Exceção não tratada em %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return _resposta_erro(500, "ERRO_INTERNO", "Ocorreu um erro interno inesperado.")
