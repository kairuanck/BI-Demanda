"""Testes do serviço da Visão 360º do Cliente (Sprint 5)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import SistemaOrigem, TipoArquivoImportacao
from app.domain.excecoes import RegistroNaoEncontradoError
from app.infrastructure.models import Cliente, Laboratorio, Promotor, Usuario
from app.services.cliente_service import ClienteService, FiltrosCliente
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


def _dentro_dos_ultimos_12_meses(ano: int, mes: int) -> bool:
    """Mesma janela móvel de `ClienteService._faturamento_ultimos_12_meses`."""

    hoje = date.today()
    codigo = ano * 100 + mes
    ano_ini, mes_ini = hoje.year, hoje.month - 11
    while mes_ini <= 0:
        mes_ini += 12
        ano_ini -= 1
    codigo_ini = ano_ini * 100 + mes_ini
    codigo_fim = hoje.year * 100 + hoje.month
    return codigo_ini <= codigo <= codigo_fim


@pytest.fixture()
def cenario_basico(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    """Mesmo cenário de tests/test_dashboard_service.py, com o checklist_sb
    adicional (2 visitas REALIZADA de junho/2026: 0343→10001, 0777→10002)."""

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


def _laboratorio_id(sessao: Session, nome: str) -> str:
    laboratorio_id = sessao.scalar(select(Laboratorio.id).where(Laboratorio.nome == nome))
    assert laboratorio_id is not None
    return laboratorio_id


def _promotor_id(sessao: Session, codigo_externo: str | None, nome: str | None = None) -> str:
    """Busca por `codigo_externo` (promotores SB) ou por `nome` (promotores
    criados via CONSULTOR do Painel Avert, sem `codigo_externo`)."""

    consulta = select(Promotor.id).where(
        Promotor.codigo_externo == codigo_externo if codigo_externo else Promotor.nome == nome
    )
    promotor_id = sessao.scalar(consulta)
    assert promotor_id is not None
    return promotor_id


def test_busca_clientes_por_codigo_razao_fantasia_cnpj_cidade(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)

    assert servico.buscar_clientes("10001", 1, 10).total_itens == 1
    assert servico.buscar_clientes("PET SHOP ALFA", 1, 10).total_itens == 1
    assert servico.buscar_clientes("PET ALFA", 1, 10).total_itens == 1
    assert servico.buscar_clientes("11222333000144", 1, 10).total_itens == 1
    assert servico.buscar_clientes("CAMPINAS", 1, 10).total_itens == 1
    assert servico.buscar_clientes("nao existe nenhum cliente assim", 1, 10).total_itens == 0


def test_busca_clientes_ignora_acento_e_caixa(cenario_basico: None, sessao: Session) -> None:
    """SÃO PAULO deve ser encontrado independente de acento/caixa digitados
    (mesma limitação do LOWER() nativo do SQLite corrigida na Sprint 3 para
    nomes de promotor, docs/DECISIONS.md, seção 15.3)."""

    servico = ClienteService(sessao)

    for termo in ("são paulo", "SÃO PAULO", "São Paulo", "sao paulo"):
        assert servico.buscar_clientes(termo, 1, 10).total_itens == 1, termo


def test_busca_clientes_sem_termo_lista_todos_paginado(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)
    pagina = servico.buscar_clientes("", 1, 2)

    assert pagina.total_itens == 3
    assert len(pagina.itens) == 2


def test_busca_clientes_filtrada_por_promotor(cenario_basico: None, sessao: Session) -> None:
    """Usado pela Página do Promotor para navegar Promotor → Cliente (Carteira)."""

    servico = ClienteService(sessao)
    promotor_id = _promotor_id(sessao, "0343")

    pagina = servico.buscar_clientes("", 1, 10, promotor_id=promotor_id)

    codigos = {item.codigo_externo for item in pagina.itens}
    assert codigos == {"10001", "10002"}


def test_busca_clientes_filtrada_por_promotor_avert(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    promotor_avert_id = _promotor_id(sessao, None, nome="PROMOTORA WECHECK UM")

    pagina = servico.buscar_clientes("", 1, 10, promotor_id=promotor_avert_id)

    assert {item.codigo_externo for item in pagina.itens} == {"10001"}


def test_obter_detalhe_cliente_inexistente_levanta_erro(sessao: Session) -> None:
    servico = ClienteService(sessao)
    with pytest.raises(RegistroNaoEncontradoError):
        servico.obter_detalhe_cliente("id-inexistente", FiltrosCliente())


def test_detalhe_cliente_dados_cadastrais_e_vinculos(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    detalhe = servico.obter_detalhe_cliente(cliente_id, FiltrosCliente(ano=2026))

    assert detalhe.codigo_externo == "10001"
    assert detalhe.razao_social == "PET SHOP ALFA LTDA"
    assert detalhe.nome_fantasia == "PET ALFA"
    assert detalhe.cidade == "CAMPINAS"
    assert detalhe.uf_sigla == "SP"
    assert detalhe.ativo is True
    assert detalhe.grupo_economico == "GRUPO ALFA"
    assert detalhe.segmento == "PET SHOP"

    sistemas = {v.sistema_origem for v in detalhe.vinculos}
    assert sistemas == {SistemaOrigem.SB_PROMOTOR.value, SistemaOrigem.PAINEL_AVERT.value}
    vinculo_sb = next(
        v for v in detalhe.vinculos if v.sistema_origem == SistemaOrigem.SB_PROMOTOR.value
    )
    assert vinculo_sb.nome == "PROMOTORA UM"
    vinculo_avert = next(
        v for v in detalhe.vinculos if v.sistema_origem == SistemaOrigem.PAINEL_AVERT.value
    )
    assert vinculo_avert.nome == "PROMOTORA WECHECK UM"


def test_detalhe_cliente_sem_carteira_avert_tem_campos_nulos(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10003")

    detalhe = servico.obter_detalhe_cliente(cliente_id, FiltrosCliente())

    assert detalhe.grupo_economico is None
    assert detalhe.segmento is None
    assert [v.sistema_origem for v in detalhe.vinculos] == [SistemaOrigem.SB_PROMOTOR.value]


def test_kpis_cliente_faturamento_e_laboratorios(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    kpis = servico._kpis_cliente(cliente_id, FiltrosCliente(ano=2026))

    assert kpis.faturamento_acumulado == Decimal("406.07")
    assert kpis.quantidade_laboratorios == 2  # AVERT (396.07) e BRINDE (10.00); BBPET é None

    esperado_12_meses = Decimal("406.07") if _dentro_dos_ultimos_12_meses(2026, 1) else Decimal("0")
    assert kpis.faturamento_12_meses == esperado_12_meses


def test_kpis_cliente_filtro_laboratorio_restringe_tudo(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    filtros = FiltrosCliente(ano=2026, laboratorio_id=_laboratorio_id(sessao, "AVERT"))
    kpis = servico._kpis_cliente(cliente_id, filtros)

    assert kpis.faturamento_acumulado == Decimal("396.07")
    assert kpis.quantidade_laboratorios == 1


def test_kpis_cliente_cobertura_e_positivacao_no_ano(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    kpis = servico._kpis_cliente(cliente_id, FiltrosCliente(ano=2026))

    # janela de 12 meses (jan-dez/2026): 1 mês com visita REALIZADA (junho) e 1 mês com
    # faturamento positivo (janeiro) -> ambos 1/12.
    assert kpis.cobertura == Decimal("1") / Decimal("12")
    assert kpis.positivacao == Decimal("1") / Decimal("12")
    assert kpis.quantidade_visitas == 1
    assert kpis.dias_desde_ultima_visita == (date.today() - date(2026, 6, 5)).days


def test_kpis_cliente_sem_visita_tem_dias_desde_ultima_visita_nulo(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10003")

    kpis = servico._kpis_cliente(cliente_id, FiltrosCliente())

    assert kpis.dias_desde_ultima_visita is None
    assert kpis.quantidade_visitas == 0
    assert kpis.cobertura == Decimal("0")


def test_evolucao_faturamento_cliente(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    serie = servico.evolucao_faturamento_cliente(cliente_id, FiltrosCliente())

    assert len(serie) == 1
    assert serie[0].ano == 2026
    assert serie[0].mes == 1
    assert serie[0].valor == Decimal("406.07")


def test_laboratorios_cliente_com_participacao_percentual(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    laboratorios = servico.laboratorios_cliente(cliente_id, FiltrosCliente())
    por_nome = {linha.laboratorio: linha for linha in laboratorios}

    assert por_nome["AVERT"].valor_acumulado == Decimal("396.07")
    assert por_nome["BRINDE"].valor_acumulado == Decimal("10.00")
    assert por_nome["AVERT"].primeiro_ano == 2026
    assert por_nome["AVERT"].primeiro_mes == 1
    assert por_nome["AVERT"].ultimo_ano == 2026
    assert por_nome["AVERT"].ultimo_mes == 1

    total_participacao = sum(
        (linha.participacao_percentual for linha in laboratorios), Decimal("0")
    )
    assert total_participacao == Decimal("1")


def test_faturamento_por_laboratorio_cliente(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    serie = servico.faturamento_por_laboratorio_cliente(cliente_id, FiltrosCliente())
    valores = {p.rotulo: p.valor for p in serie}

    assert valores == {"AVERT": Decimal("396.07"), "BRINDE": Decimal("10.00")}


def test_visitas_e_checklists_por_mes_cliente(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    visitas = servico.visitas_por_mes_cliente(cliente_id, FiltrosCliente())
    checklists = servico.checklists_por_mes_cliente(cliente_id, FiltrosCliente())

    assert len(visitas) == 1
    assert visitas[0].ano == 2026
    assert visitas[0].mes == 6
    assert visitas[0].valor == Decimal("1")

    assert len(checklists) == 1
    assert checklists[0].ano == 2026
    assert checklists[0].mes == 6
    assert checklists[0].valor > 0


def test_timeline_cliente_combina_fontes_e_ordena_desc(
    cenario_basico: None, sessao: Session
) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    pagina = servico.timeline_cliente(cliente_id, pagina=1, tamanho_pagina=50)
    tipos = {evento.tipo for evento in pagina.itens}

    assert "VISITA" in tipos
    assert "CHECKLIST" in tipos
    assert "IMPORTACAO" in tipos
    assert "ALTERACAO_CADASTRAL" in tipos

    datas = [evento.data for evento in pagina.itens]
    assert datas == sorted(datas, reverse=True)


def test_timeline_cliente_paginacao(cenario_basico: None, sessao: Session) -> None:
    servico = ClienteService(sessao)
    cliente_id = _cliente_id(sessao, "10001")

    total = servico.timeline_cliente(cliente_id, pagina=1, tamanho_pagina=1000).total_itens
    assert total > 1

    primeira_pagina = servico.timeline_cliente(cliente_id, pagina=1, tamanho_pagina=1)
    assert len(primeira_pagina.itens) == 1
    assert primeira_pagina.total_itens == total
