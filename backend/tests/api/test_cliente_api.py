"""Testes dos endpoints REST da Visão 360º do Cliente (Sprint 5)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TipoArquivoImportacao
from app.infrastructure.models import Cliente, Usuario
from etl.arquivos import FluxoArquivos
from etl.motor import MotorImportacao
from tests.etl.fixtures_reais import (
    xlsx_base_clientes,
    xlsx_checklist_sb,
    xlsx_faturamento_matriz,
    xlsx_painel_avert,
    xlsx_sb_supervisor,
)

COMPETENCIA_JAN = date(2026, 1, 1)


@pytest.fixture()
def cenario_basico(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    motor.importar(xlsx_base_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id)
    motor.importar(
        xlsx_faturamento_matriz(fluxo), TipoArquivoImportacao.FATURAMENTO, usuario_admin.id
    )
    motor.importar(
        xlsx_sb_supervisor(fluxo),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=COMPETENCIA_JAN,
    )
    motor.importar(
        xlsx_painel_avert(fluxo),
        TipoArquivoImportacao.PAINEL_AVERT,
        usuario_admin.id,
        competencia=COMPETENCIA_JAN,
    )
    motor.importar(xlsx_checklist_sb(fluxo), TipoArquivoImportacao.CHECKLIST, usuario_admin.id)


def _cliente_id(sessao: Session, codigo_externo: str) -> str:
    cliente_id = sessao.scalar(select(Cliente.id).where(Cliente.codigo_externo == codigo_externo))
    assert cliente_id is not None
    return cliente_id


def test_buscar_clientes(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/clientes", params={"q": "PET SHOP ALFA"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_itens"] == 1
    assert corpo["itens"][0]["codigo_externo"] == "10001"


def test_buscar_clientes_sem_termo_lista_todos(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/clientes")

    assert resposta.status_code == 200
    assert resposta.json()["total_itens"] == 3


def test_obter_detalhe_cliente(cenario_basico: None, client: TestClient, sessao: Session) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}", params={"ano": 2026})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["razao_social"] == "PET SHOP ALFA LTDA"
    assert Decimal(corpo["kpis"]["faturamento_acumulado"]) == Decimal("406.07")
    assert len(corpo["vinculos"]) == 2


def test_obter_detalhe_cliente_inexistente_retorna_404_padrao(client: TestClient) -> None:
    resposta = client.get("/api/v1/clientes/id-inexistente")

    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_grafico_evolucao_faturamento_cliente(
    cenario_basico: None, client: TestClient, sessao: Session
) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}/graficos/faturamento-mensal")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo) == 1
    assert Decimal(corpo[0]["valor"]) == Decimal("406.07")


def test_grafico_faturamento_por_laboratorio_cliente(
    cenario_basico: None, client: TestClient, sessao: Session
) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}/graficos/faturamento-laboratorio")

    assert resposta.status_code == 200
    valores = {p["rotulo"]: Decimal(p["valor"]) for p in resposta.json()}
    assert valores == {"AVERT": Decimal("396.07"), "BRINDE": Decimal("10.00")}


def test_grafico_visitas_por_mes_cliente(
    cenario_basico: None, client: TestClient, sessao: Session
) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}/graficos/visitas-mensal")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo) == 1
    assert corpo[0]["mes"] == 6


def test_grafico_checklists_por_mes_cliente(
    cenario_basico: None, client: TestClient, sessao: Session
) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}/graficos/checklists-mensal")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_laboratorios_cliente(cenario_basico: None, client: TestClient, sessao: Session) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}/laboratorios")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo) == 2
    total_participacao = sum(Decimal(linha["participacao_percentual"]) for linha in corpo)
    assert total_participacao == Decimal("1")


def test_timeline_cliente_paginada(
    cenario_basico: None, client: TestClient, sessao: Session
) -> None:
    cliente_id = _cliente_id(sessao, "10001")

    resposta = client.get(f"/api/v1/clientes/{cliente_id}/timeline", params={"tamanho_pagina": 2})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["tamanho_pagina"] == 2
    assert len(corpo["itens"]) == 2
    assert corpo["total_itens"] > 2
    tipos_validos = {"VISITA", "CHECKLIST", "IMPORTACAO", "ALTERACAO_CADASTRAL"}
    assert all(item["tipo"] in tipos_validos for item in corpo["itens"])
