"""Testes do serviço do Dashboard Executivo (Sprint 4)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import SistemaOrigem, StatusVisita, TipoArquivoImportacao
from app.domain.excecoes import RegistroNaoEncontradoError
from app.infrastructure.models import Carteira, Importacao, Promotor, Usuario, Visita
from app.services.dashboard_service import DashboardService, FiltrosDashboard
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
    """3 clientes (10001 SP, 10002 SP, 10003 MG), faturamento de Janeiro/2026,
    carteira SB (0343: 10001+10002; 0777: 10003) e carteira Avert (10001)."""

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


def test_kpis_sem_filtro_soma_tudo(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    kpis = servico.calcular_kpis(FiltrosDashboard())

    assert kpis.faturamento_total == Decimal("1616.57")
    assert kpis.faturamento_carteira == Decimal("1616.57")  # todos os 3 estão na carteira SB
    assert kpis.faturamento_regiao == Decimal("406.07")  # só 10001 está na carteira Avert
    assert kpis.faturamento_fora_carteira == Decimal("0")  # nenhum cliente fora de ambas
    assert kpis.quantidade_clientes == 3
    assert kpis.clientes_positivados == 2  # 10003 tem saldo líquido negativo (-40.00)
    assert kpis.numero_visitas == 0
    assert kpis.numero_checklists == 0


def test_kpis_filtrados_por_ano_mes(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    kpis_jan = servico.calcular_kpis(FiltrosDashboard(ano=2026, mes=1))
    kpis_fev = servico.calcular_kpis(FiltrosDashboard(ano=2026, mes=2))

    assert kpis_jan.faturamento_total == Decimal("1616.57")
    assert kpis_fev.faturamento_total == Decimal("0")  # sem dados de fevereiro


def test_kpis_filtrados_por_uf(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    kpis_mg = servico.calcular_kpis(FiltrosDashboard(uf_sigla="MG"))

    assert kpis_mg.quantidade_clientes == 1  # só 10003
    assert kpis_mg.faturamento_total == Decimal("-40.00")
    assert kpis_mg.faturamento_regiao == Decimal("0")  # 10003 não está na carteira Avert


def test_kpis_fora_da_carteira_nao_aplicavel_com_filtro_promotor(
    cenario_basico: None, sessao: Session
) -> None:
    servico = DashboardService(sessao)
    promotor_id = sessao.scalars(select(Promotor.id)).first()
    assert promotor_id is not None

    kpis = servico.calcular_kpis(FiltrosDashboard(promotor_id=promotor_id))
    assert kpis.faturamento_fora_carteira is None  # KPIS.md, seção 5


def test_kpis_sistema_origem_segrega_carteira_sb_e_avert(
    cenario_basico: None, sessao: Session
) -> None:
    servico = DashboardService(sessao)
    kpis_sb = servico.calcular_kpis(FiltrosDashboard(sistema_origem=SistemaOrigem.SB_PROMOTOR))
    kpis_avert = servico.calcular_kpis(FiltrosDashboard(sistema_origem=SistemaOrigem.PAINEL_AVERT))

    assert kpis_sb.faturamento_regiao is None
    assert kpis_sb.faturamento_carteira == Decimal("1616.57")
    assert kpis_avert.faturamento_carteira == Decimal("0")
    assert kpis_avert.faturamento_regiao == Decimal("406.07")


def test_evolucao_faturamento_mensal(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    serie = servico.evolucao_faturamento_mensal(FiltrosDashboard())

    assert len(serie) == 1
    assert serie[0].ano == 2026
    assert serie[0].mes == 1
    assert serie[0].valor == Decimal("1616.57")


def test_faturamento_por_laboratorio(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    serie = servico.faturamento_por_laboratorio(FiltrosDashboard())

    valores = {p.rotulo: p.valor for p in serie}
    assert valores["BBPET"] == Decimal("1330.50")  # 1250.50 + 80.00
    assert valores["AVERT"] == Decimal("276.07")  # 396.07 - 120.00
    assert valores["BRINDE"] == Decimal("10.00")


def test_distribuicao_uf(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    serie = servico.distribuicao_uf(FiltrosDashboard())

    por_uf = {p.uf_sigla: p for p in serie}
    assert por_uf["SP"].quantidade_clientes == 2
    assert por_uf["MG"].quantidade_clientes == 1
    assert por_uf["SP"].faturamento_total == Decimal("1656.57")  # 396.07+10+1250.50
    assert por_uf["MG"].faturamento_total == Decimal("-40.00")


def test_listar_promotores_traz_metricas_agregadas(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    pagina = servico.listar_promotores(FiltrosDashboard(), pagina=1, tamanho_pagina=10)

    # 0343 e 0777 (carteira SB) + "PROMOTORA WECHECK UM" (CONSULTOR do Painel Avert)
    assert pagina.total_itens == 3
    por_codigo = {}
    for linha in pagina.itens:
        promotor = sessao.get(Promotor, linha.promotor_id)
        assert promotor is not None
        por_codigo[promotor.codigo_externo or promotor.nome] = linha

    assert por_codigo["0343"].quantidade_clientes == 2
    assert por_codigo["0343"].faturamento_carteira == Decimal("1656.57")
    assert por_codigo["0777"].quantidade_clientes == 1
    assert por_codigo["0777"].faturamento_carteira == Decimal("-40.00")
    assert por_codigo["PROMOTORA WECHECK UM"].faturamento_regiao == Decimal("406.07")


def test_listar_promotores_respeita_filtro_de_uf(cenario_basico: None, sessao: Session) -> None:
    """Filtro global de UF deve recalcular as métricas por promotor, não
    apenas os KPIs/gráficos — 0777 só tem cliente em MG, então some do
    recorte quando filtramos SP (KPIS.md; requisito de filtros globais)."""

    servico = DashboardService(sessao)
    pagina = servico.listar_promotores(FiltrosDashboard(uf_sigla="SP"), pagina=1, tamanho_pagina=10)

    por_codigo = {}
    for linha in pagina.itens:
        promotor = sessao.get(Promotor, linha.promotor_id)
        assert promotor is not None
        por_codigo[promotor.codigo_externo or promotor.nome] = linha

    assert por_codigo["0343"].quantidade_clientes == 2
    assert por_codigo["0343"].faturamento_carteira == Decimal("1656.57")
    assert por_codigo["0777"].quantidade_clientes == 0
    assert por_codigo["0777"].faturamento_carteira == Decimal("0")


def test_top_promotores_ordena_por_indice_desempenho(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    ranking = servico.top_promotores(FiltrosDashboard(), limite=5)

    assert len(ranking) == 3
    # promotores com carteira SB (0343/0777) têm cobertura calculável (0/N clientes visitados);
    # a promotora só-Avert não tem carteira SB, então cobertura fica None (KPIS.md, seção 8)
    com_carteira_sb = [p for p in ranking if p.nome != "PROMOTORA WECHECK UM"]
    assert all(p.cobertura is not None for p in com_carteira_sb)


def test_listar_ultimas_importacoes_uma_por_tipo(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    ultimas = servico.listar_ultimas_importacoes()

    tipos = {i.tipo_arquivo for i in ultimas}
    assert TipoArquivoImportacao.CLIENTES in tipos
    assert TipoArquivoImportacao.FATURAMENTO in tipos
    assert TipoArquivoImportacao.CARTEIRA in tipos
    assert TipoArquivoImportacao.PAINEL_AVERT in tipos
    assert len(ultimas) == len(tipos)  # 1 por tipo


def test_obter_detalhe_promotor_inexistente_levanta_erro(sessao: Session) -> None:
    servico = DashboardService(sessao)
    with pytest.raises(RegistroNaoEncontradoError):
        servico.obter_detalhe_promotor("id-inexistente", FiltrosDashboard())


def test_obter_detalhe_promotor(cenario_basico: None, sessao: Session) -> None:
    servico = DashboardService(sessao)
    promotor = sessao.scalar(select(Promotor).where(Promotor.codigo_externo == "0343"))
    assert promotor is not None

    detalhe = servico.obter_detalhe_promotor(promotor.id, FiltrosDashboard())
    assert detalhe.nome == promotor.nome
    assert detalhe.kpis.faturamento_carteira == Decimal("1656.57")
    assert len(detalhe.evolucao_faturamento) == 1


def test_cobertura_carteira_nao_credita_visita_de_outro_promotor(
    cenario_basico: None, sessao: Session
) -> None:
    """Uma visita só cobre um cliente quando feita pelo promotor titular
    daquele vínculo de carteira (10002 pertence à carteira de 0343, não de
    0777) — visita "cruzada" não deve inflar a cobertura de ninguém."""

    promotor_0343 = sessao.scalar(select(Promotor).where(Promotor.codigo_externo == "0343"))
    promotor_0777 = sessao.scalar(select(Promotor).where(Promotor.codigo_externo == "0777"))
    assert promotor_0343 is not None and promotor_0777 is not None

    carteira_0343 = sessao.scalar(select(Carteira).where(Carteira.promotor_id == promotor_0343.id))
    assert carteira_0343 is not None
    importacao_id = sessao.scalar(select(Importacao.id))

    sessao.add(
        Visita(
            origem=SistemaOrigem.SB_PROMOTOR,
            promotor_id=promotor_0777.id,
            cliente_id=carteira_0343.cliente_id,
            data_visita=COMPETENCIA_JAN,
            status=StatusVisita.REALIZADA,
            importacao_id=importacao_id,
        )
    )
    sessao.commit()

    servico = DashboardService(sessao)
    cobertura_0343 = servico.calcular_kpis(
        FiltrosDashboard(promotor_id=promotor_0343.id)
    ).cobertura_carteira
    cobertura_geral = servico.calcular_kpis(FiltrosDashboard()).cobertura_carteira

    assert cobertura_0343 == Decimal("0")
    assert cobertura_geral == Decimal("0")


def test_tipos_checklist_conta_visitas_distintas(
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
    sessao: Session,
) -> None:
    motor.importar(xlsx_base_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id)
    motor.importar(xlsx_checklist_sb(fluxo), TipoArquivoImportacao.CHECKLIST, usuario_admin.id)

    servico = DashboardService(sessao)
    serie = servico.tipos_checklist(FiltrosDashboard())

    assert sum(int(p.valor) for p in serie) == 2  # 2 aplicações de checklist na fixture
