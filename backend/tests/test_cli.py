"""Testes da CLI de importação (Sprint 3, Fase 5)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select

from app.domain.enums import TipoArquivoImportacao
from app.infrastructure.models import Cliente, Usuario
from etl.arquivos import FluxoArquivos
from etl.cli import inferir_tipo_arquivo, main
from tests.etl.fixtures_reais import (
    xlsx_base_clientes,
    xlsx_checklist_sb,
    xlsx_faturamento_matriz,
    xlsx_painel_avert,
    xlsx_sb_produtos,
    xlsx_sb_supervisor,
    xlsx_wecheck,
)


@pytest.fixture()
def origem(tmp_path: Path) -> FluxoArquivos:
    """Diretório de origem só para gerar as planilhas de teste."""

    return FluxoArquivos(tmp_path / "origem")


def test_inferir_tipo_arquivo_reconhece_todas_as_fontes_reais(origem: FluxoArquivos) -> None:
    casos = [
        (xlsx_base_clientes(origem), TipoArquivoImportacao.CLIENTES),
        (xlsx_faturamento_matriz(origem), TipoArquivoImportacao.FATURAMENTO),
        (xlsx_sb_supervisor(origem), TipoArquivoImportacao.CARTEIRA),
        (xlsx_sb_produtos(origem), TipoArquivoImportacao.SB_PRODUTOS),
        (xlsx_checklist_sb(origem), TipoArquivoImportacao.CHECKLIST),
        (xlsx_wecheck(origem), TipoArquivoImportacao.WECHECK),
        (xlsx_painel_avert(origem), TipoArquivoImportacao.PAINEL_AVERT),
    ]
    for caminho, tipo_esperado in casos:
        assert inferir_tipo_arquivo(caminho) == tipo_esperado, caminho.name


def test_inferir_tipo_arquivo_estrutura_desconhecida_retorna_none(
    origem: FluxoArquivos, tmp_path: Path
) -> None:
    arquivo_texto = tmp_path / "nao_e_xlsx.xlsx"
    arquivo_texto.write_bytes(b"isto nao e um xlsx valido")

    assert inferir_tipo_arquivo(arquivo_texto) is None


def test_cli_main_importa_arquivo_reconhecido_e_cria_usuario_sistema(
    origem: FluxoArquivos, tmp_path: Path, ufs: None, capsys: pytest.CaptureFixture[str]
) -> None:
    arquivo = xlsx_base_clientes(origem)
    storage_dir = tmp_path / "storage"

    codigo_saida = main([str(arquivo), "--storage-dir", str(storage_dir)])

    assert codigo_saida == 0
    saida = capsys.readouterr().out
    assert "CLIENTES" in saida
    assert "CONCLUIDA" in saida

    from app.infrastructure.database import SessionLocal

    sessao = SessionLocal()
    try:
        usuario = sessao.scalar(
            select(Usuario).where(Usuario.email == "sistema@promotoresbi.local")
        )
        assert usuario is not None
        assert sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "10001")) is not None
    finally:
        sessao.close()


def test_cli_main_arquivo_nao_reconhecido_retorna_codigo_de_erro(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    arquivo_invalido = tmp_path / "desconhecido.xlsx"
    arquivo_invalido.write_bytes(b"conteudo qualquer")
    storage_dir = tmp_path / "storage"

    codigo_saida = main([str(arquivo_invalido), "--storage-dir", str(storage_dir)])

    assert codigo_saida == 1
    assert "NAO_RECONHECIDO" in capsys.readouterr().out


def test_cli_main_competencia_e_repassada_ao_motor(
    origem: FluxoArquivos, tmp_path: Path, ufs: None, capsys: pytest.CaptureFixture[str]
) -> None:
    motor_clientes = main(
        [str(xlsx_base_clientes(origem)), "--storage-dir", str(tmp_path / "storage")]
    )
    assert motor_clientes == 0

    codigo_saida = main(
        [
            str(xlsx_sb_supervisor(origem)),
            "--competencia",
            "2026-06",
            "--storage-dir",
            str(tmp_path / "storage"),
        ]
    )
    assert codigo_saida == 0
    assert "CARTEIRA" in capsys.readouterr().out
