"""Testes do serviço de qualidade de dados (Sprint 3, Fase 6)."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.domain.enums import SistemaOrigem, StatusImportacao, TipoArquivoImportacao
from app.infrastructure.models import Usuario
from app.services.qualidade_dados_service import gerar_relatorio_qualidade
from etl.arquivos import FluxoArquivos
from etl.motor import MotorImportacao
from tests.etl.fixtures_reais import (
    xlsx_base_clientes,
    xlsx_faturamento_matriz,
    xlsx_painel_avert,
    xlsx_sb_supervisor,
)


def test_relatorio_qualidade_banco_vazio(sessao: Session) -> None:
    relatorio = gerar_relatorio_qualidade(sessao)

    assert relatorio.total_clientes == 0
    assert relatorio.cobertura_faturamento_pct == 0.0
    assert relatorio.cobertura_carteira_pct == 0.0
    assert relatorio.cobertura_carteira_avert_pct == 0.0
    assert relatorio.integracoes_pendentes_por_sistema == {}


def test_relatorio_qualidade_calcula_coberturas_e_pendencias(
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
    sessao: Session,
) -> None:
    motor.importar(xlsx_base_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id)
    motor.importar(
        xlsx_faturamento_matriz(fluxo), TipoArquivoImportacao.FATURAMENTO, usuario_admin.id
    )
    motor.importar(
        xlsx_sb_supervisor(fluxo),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=date(2026, 6, 1),
    )
    linhas_avert = [
        [
            "11.222.333/0001-44",
            None,
            None,
            None,
            "RS",
            "SUL",
            "REGIONAL 1",
            "DISTRIBUIDOR X",
            "COORD A",
            "PROMOTORA UM",
            "VENDEDOR Z",
            "GRUPO ALFA",
            "PET ALFA",
            "PET SHOP ALFA LTDA",
            "PET SHOP",
            None,
        ],
        [
            "00.000.000/0001-00",
            None,
            None,
            None,
            "RS",
            "SUL",
            "REGIONAL 1",
            "DISTRIBUIDOR X",
            "COORD A",
            "PROMOTORA UM",
            "VENDEDOR Z",
            None,
            "SEM CADASTRO",
            "SEM CADASTRO LTDA",
            "AGRO",
            None,
        ],
    ]
    motor.importar(
        xlsx_painel_avert(fluxo, linhas=linhas_avert),
        TipoArquivoImportacao.PAINEL_AVERT,
        usuario_admin.id,
        competencia=date(2026, 6, 1),
    )

    relatorio = gerar_relatorio_qualidade(sessao)

    assert relatorio.total_clientes == 3
    assert relatorio.clientes_com_faturamento == 3
    assert relatorio.cobertura_faturamento_pct == 100.0
    assert relatorio.clientes_com_carteira_ativa == 3
    assert relatorio.cobertura_carteira_pct == 100.0
    assert relatorio.carteira_avert_total == 2
    assert relatorio.carteira_avert_vinculada == 1
    assert relatorio.cobertura_carteira_avert_pct == 50.0
    assert relatorio.integracoes_pendentes_por_sistema == {SistemaOrigem.PAINEL_AVERT.value: 1}


def test_relatorio_qualidade_detecta_documento_compartilhado(
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
    sessao: Session,
) -> None:
    linhas = [
        [
            "10001",
            "11222333000144",
            None,
            "CLIENTE A",
            None,
            None,
            None,
            None,
            None,
            None,
            "CAMPINAS",
            "SP",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        [
            "10002",
            "11222333000144",
            None,
            "CLIENTE B (mesmo documento)",
            None,
            None,
            None,
            None,
            None,
            None,
            "CAMPINAS",
            "SP",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        [
            "10003",
            "99988877000100",
            None,
            "CLIENTE C",
            None,
            None,
            None,
            None,
            None,
            None,
            "CAMPINAS",
            "SP",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
    ]
    importacao = motor.importar(
        xlsx_base_clientes(fluxo, linhas=linhas),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    relatorio = gerar_relatorio_qualidade(sessao)

    assert relatorio.documentos_cnpj_cpf_compartilhados == 1
    assert relatorio.clientes_afetados_por_documento_compartilhado == 2
