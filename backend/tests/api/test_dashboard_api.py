"""Testes dos endpoints REST do Dashboard Executivo (Sprint 4)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TipoArquivoImportacao
from app.infrastructure.models import Promotor, Usuario
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
    """Mesmo cenário de tests/test_dashboard_service.py: 3 clientes (SP, SP, MG),
    faturamento de Janeiro/2026, carteira SB e carteira Avert."""

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


def test_obter_opcoes_filtro(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/filtros")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert 2026 in corpo["anos"]
    assert {uf["sigla"] for uf in corpo["ufs"]} >= {"SP", "MG"}
    assert len(corpo["laboratorios"]) >= 1
    assert len(corpo["promotores"]) == 3


def test_obter_kpis_sem_filtro(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/kpis")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert Decimal(corpo["faturamento_total"]) == Decimal("1616.57")
    assert Decimal(corpo["faturamento_regiao"]) == Decimal("406.07")
    assert corpo["quantidade_clientes"] == 3
    assert corpo["clientes_positivados"] == 2


def test_obter_kpis_filtrados_por_ano_mes_e_uf(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/kpis", params={"ano": 2026, "mes": 2})
    assert Decimal(resposta.json()["faturamento_total"]) == Decimal("0")

    resposta_mg = client.get("/api/v1/dashboard/kpis", params={"uf": "mg"})
    assert resposta_mg.json()["quantidade_clientes"] == 1


def test_graficos_faturamento_mensal(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/graficos/faturamento-mensal")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo) == 1
    assert corpo[0]["ano"] == 2026
    assert corpo[0]["mes"] == 1


def test_graficos_positivacao_mensal(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/graficos/positivacao-mensal")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_graficos_faturamento_por_laboratorio(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/graficos/faturamento-laboratorio")

    assert resposta.status_code == 200
    valores = {p["rotulo"]: Decimal(p["valor"]) for p in resposta.json()}
    assert valores["BBPET"] == Decimal("1330.50")


def test_graficos_top_promotores_respeita_limite(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/graficos/top-promotores", params={"limite": 2})

    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_graficos_tipos_checklist(
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
    client: TestClient,
) -> None:
    motor.importar(xlsx_base_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id)
    motor.importar(xlsx_checklist_sb(fluxo), TipoArquivoImportacao.CHECKLIST, usuario_admin.id)

    resposta = client.get("/api/v1/dashboard/graficos/tipos-checklist")

    assert resposta.status_code == 200
    assert sum(int(Decimal(p["valor"])) for p in resposta.json()) == 2


def test_graficos_distribuicao_uf(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/graficos/distribuicao-uf")

    assert resposta.status_code == 200
    por_uf = {p["uf_sigla"]: p for p in resposta.json()}
    assert por_uf["SP"]["quantidade_clientes"] == 2
    assert por_uf["MG"]["quantidade_clientes"] == 1


def test_listar_promotores_paginado(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/promotores", params={"pagina": 1, "tamanho_pagina": 2})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_itens"] == 3
    assert corpo["pagina"] == 1
    assert corpo["tamanho_pagina"] == 2
    assert len(corpo["itens"]) == 2
    primeiro = corpo["itens"][0]
    assert {"promotor_id", "nome", "faturamento_carteira", "faturamento_regiao"} <= set(
        primeiro.keys()
    )


def test_obter_detalhe_promotor(cenario_basico: None, client: TestClient, sessao: Session) -> None:
    promotor = sessao.scalar(select(Promotor).where(Promotor.codigo_externo == "0343"))
    assert promotor is not None

    resposta = client.get(f"/api/v1/dashboard/promotores/{promotor.id}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome"] == promotor.nome
    assert Decimal(corpo["kpis"]["faturamento_carteira"]) == Decimal("1656.57")


def test_obter_detalhe_promotor_inexistente_retorna_404_padrao(client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/promotores/id-inexistente")

    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_listar_ultimas_importacoes(cenario_basico: None, client: TestClient) -> None:
    resposta = client.get("/api/v1/dashboard/importacoes/ultimas")

    assert resposta.status_code == 200
    tipos = {i["tipo_arquivo"] for i in resposta.json()}
    assert TipoArquivoImportacao.CLIENTES.value in tipos
    assert TipoArquivoImportacao.FATURAMENTO.value in tipos
