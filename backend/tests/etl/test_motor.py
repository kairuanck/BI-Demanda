"""Testes do motor de importação: hash, duplicidade, versionamento e rollback."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.infrastructure.models import Cliente, ImportacaoErro, LogAuditoria, Usuario
from etl.arquivos import FluxoArquivos
from etl.motor import IMPORTADORES, MotorImportacao
from etl.validators.clientes import validar_clientes
from tests.etl.fixtures_xlsx import criar_xlsx, duplicar_arquivo, xlsx_clientes


def test_importacao_em_banco_vazio_recebe_versao_1(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    arquivo = xlsx_clientes(fluxo)
    importacao = motor.importar(arquivo, TipoArquivoImportacao.CLIENTES, usuario_admin.id)

    assert importacao.status == StatusImportacao.CONCLUIDA
    assert importacao.versao == 1
    assert importacao.importacao_pai_id is None
    assert importacao.total_linhas == 3
    assert importacao.linhas_validas == 3
    assert importacao.linhas_invalidas == 0
    # arquivo movido para processed e cópia em archive
    assert not arquivo.exists()
    assert len(list(fluxo.processed.iterdir())) == 1
    assert len(list(fluxo.archive.iterdir())) == 1


def test_arquivo_identico_e_recusado_como_duplicado(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    # duplicar_arquivo garante bytes idênticos (e portanto hash idêntico),
    # diferente de gerar duas planilhas equivalentes via OpenPyXL (ver
    # fixtures_xlsx.py — o writer sempre varia o `modified` interno).
    arquivo_a = xlsx_clientes(fluxo, "a.xlsx")
    arquivo_b = duplicar_arquivo(arquivo_a, "b.xlsx")

    primeira = motor.importar(arquivo_a, TipoArquivoImportacao.CLIENTES, usuario_admin.id)
    segunda = motor.importar(arquivo_b, TipoArquivoImportacao.CLIENTES, usuario_admin.id)

    assert primeira.status == StatusImportacao.CONCLUIDA
    assert segunda.status == StatusImportacao.FALHOU
    assert segunda.versao == 0  # tentativa fora da cadeia de versões (docs/DECISIONS.md)
    erros = list(
        sessao.scalars(select(ImportacaoErro).where(ImportacaoErro.importacao_id == segunda.id))
    )
    assert len(erros) == 1
    assert "duplicado" in erros[0].mensagem_erro.lower()
    assert len(list(fluxo.rejected.iterdir())) == 1
    # clientes não foram duplicados
    total_clientes = len(list(sessao.scalars(select(Cliente))))
    assert total_clientes == 3


def test_arquivo_alterado_gera_nova_versao_encadeada(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    primeira = motor.importar(
        xlsx_clientes(fluxo, "v1.xlsx"), TipoArquivoImportacao.CLIENTES, usuario_admin.id
    )
    linhas_alteradas = [
        ["C001", "Pet Shop Alfa Ltda ME", "Pet Alfa", None, "SP", "Campinas", None, "Pet Shop"],
    ]
    segunda = motor.importar(
        xlsx_clientes(fluxo, "v2.xlsx", linhas=linhas_alteradas),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )

    assert segunda.status == StatusImportacao.CONCLUIDA
    assert segunda.versao == primeira.versao + 1
    assert segunda.importacao_pai_id == primeira.id


def test_sequencias_de_versao_sao_independentes_por_tipo(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    clientes = motor.importar(
        xlsx_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id
    )
    assert clientes.versao == 1

    # um arquivo de carteira (mesmo sendo o primeiro) também recebe versão 1
    from tests.etl.fixtures_xlsx import xlsx_carteira

    carteira = motor.importar(
        xlsx_carteira(fluxo), TipoArquivoImportacao.CARTEIRA, usuario_admin.id
    )
    assert carteira.versao == 1


def test_extensao_invalida_e_recusada(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario
) -> None:
    arquivo = fluxo.incoming / "dados.csv"
    arquivo.write_bytes(b"a;b;c")
    importacao = motor.importar(arquivo, TipoArquivoImportacao.CLIENTES, usuario_admin.id)

    assert importacao.status == StatusImportacao.FALHOU
    assert len(list(fluxo.rejected.iterdir())) == 1


def test_coluna_obrigatoria_ausente_falha_importacao_inteira(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, sessao: Session
) -> None:
    arquivo = criar_xlsx(
        fluxo.incoming / "sem_coluna.xlsx",
        ["CODIGO_CLIENTE", "RAZAO_SOCIAL"],  # faltam UF e CIDADE
        [["C001", "Cliente Sem UF"]],
    )
    importacao = motor.importar(arquivo, TipoArquivoImportacao.CLIENTES, usuario_admin.id)

    assert importacao.status == StatusImportacao.FALHOU
    mensagens = [
        e.mensagem_erro
        for e in sessao.scalars(
            select(ImportacaoErro).where(ImportacaoErro.importacao_id == importacao.id)
        )
    ]
    assert any("Coluna obrigatória ausente" in m for m in mensagens)


def test_falha_no_loader_faz_rollback_completo_da_carga(
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
    sessao: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regra "rollback": falha no meio da carga não persiste nenhuma linha."""

    def loader_que_falha(session: Session, linhas, importacao_id: str, usuario_id: str) -> int:
        from etl.loaders import carregar_clientes

        carregar_clientes(session, linhas[:1], importacao_id, usuario_id)  # persiste 1 e...
        raise RuntimeError("falha proposital no meio da carga")

    monkeypatch.setitem(
        IMPORTADORES, TipoArquivoImportacao.CLIENTES, (validar_clientes, loader_que_falha)
    )

    importacao = motor.importar(
        xlsx_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.FALHOU
    # nada foi persistido, nem mesmo a linha carregada antes da falha
    assert list(sessao.scalars(select(Cliente))) == []
    assert len(list(fluxo.rejected.iterdir())) == 1


def test_toda_importacao_gera_registro_de_auditoria(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    importacao = motor.importar(
        xlsx_clientes(fluxo), TipoArquivoImportacao.CLIENTES, usuario_admin.id
    )
    registros = list(
        sessao.scalars(
            select(LogAuditoria).where(
                LogAuditoria.entidade == "importacoes",
                LogAuditoria.entidade_id == importacao.id,
            )
        )
    )
    assert len(registros) == 1
    dados = registros[0].dados_depois
    assert dados is not None
    assert dados["status"] == "CONCLUIDA"
    assert dados["hash_sha256"] == importacao.hash_sha256
    assert dados["duracao_segundos"] is not None
