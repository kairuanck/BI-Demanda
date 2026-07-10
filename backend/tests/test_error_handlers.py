"""Testes do tratamento global de erros (API.md, seção 13)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api.error_handlers import registrar_error_handlers
from app.domain.excecoes import (
    ArquivoDuplicadoError,
    ArquivoInvalidoError,
    PermissaoNegadaError,
    RegistroNaoEncontradoError,
    ValidacaoFalhouError,
)


class _CorpoTeste(BaseModel):
    valor: int


@pytest.fixture()
def app_teste() -> FastAPI:
    app = FastAPI()
    registrar_error_handlers(app)

    @app.get("/nao-encontrado")
    def _nao_encontrado() -> None:
        raise RegistroNaoEncontradoError("Cliente não encontrado.")

    @app.get("/negado")
    def _negado() -> None:
        raise PermissaoNegadaError("Acesso negado ao recurso.")

    @app.get("/validacao")
    def _validacao() -> None:
        raise ValidacaoFalhouError("Regra de negócio violada.")

    @app.get("/duplicado")
    def _duplicado() -> None:
        raise ArquivoDuplicadoError("Este arquivo já foi importado anteriormente.")

    @app.get("/invalido")
    def _invalido() -> None:
        raise ArquivoInvalidoError("Formato de arquivo inválido.")

    @app.post("/entrada")
    def _entrada(corpo: _CorpoTeste) -> dict[str, int]:
        return {"valor": corpo.valor}

    @app.get("/inesperado")
    def _inesperado() -> None:
        raise RuntimeError("falha proposital de teste")

    return app


@pytest.fixture()
def client_teste(app_teste: FastAPI) -> TestClient:
    return TestClient(app_teste, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("rota", "status_esperado", "codigo_esperado"),
    [
        ("/nao-encontrado", 404, "RECURSO_NAO_ENCONTRADO"),
        ("/negado", 403, "PERMISSAO_NEGADA"),
        ("/validacao", 422, "VALIDACAO_FALHOU"),
        ("/duplicado", 409, "ARQUIVO_DUPLICADO"),
        ("/invalido", 400, "ARQUIVO_INVALIDO"),
    ],
)
def test_excecoes_de_dominio_geram_resposta_padrao(
    client_teste: TestClient, rota: str, status_esperado: int, codigo_esperado: str
) -> None:
    response = client_teste.get(rota)

    assert response.status_code == status_esperado
    corpo = response.json()
    assert corpo["erro"]["codigo"] == codigo_esperado
    assert corpo["erro"]["mensagem"]


def test_erro_de_validacao_de_entrada_segue_formato_padrao(client_teste: TestClient) -> None:
    response = client_teste.post("/entrada", json={"valor": "nao-numerico"})

    assert response.status_code == 422
    corpo = response.json()
    assert corpo["erro"]["codigo"] == "VALIDACAO_FALHOU"
    assert corpo["erro"]["detalhes"]


def test_excecao_nao_mapeada_retorna_500_generico_sem_vazar_detalhes(
    client_teste: TestClient,
) -> None:
    response = client_teste.get("/inesperado")

    assert response.status_code == 500
    corpo = response.json()
    assert corpo["erro"]["codigo"] == "ERRO_INTERNO"
    # A mensagem interna da exceção nunca é exposta ao cliente.
    assert "falha proposital" not in response.text
