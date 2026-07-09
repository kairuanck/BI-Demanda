"""Testes de estrutura do banco de dados (DICIONARIO_DE_DADOS.md)."""

from __future__ import annotations

from sqlalchemy import inspect

from app.infrastructure.database import engine

TABELAS_ESPERADAS = {
    "usuarios",
    "supervisores",
    "promotores",
    "vendedores",
    "laboratorios",
    "departamentos",
    "ufs",
    "cidades",
    "clientes",
    "carteiras",
    "faturamentos",
    "visitas",
    "checklists",
    "checklist_perguntas",
    "checklist_respostas",
    "importacoes",
    "importacao_erros",
    "importacao_arquivos",
    "logs_auditoria",
}


def test_todas_as_19_tabelas_existem_apos_migracao() -> None:
    inspetor = inspect(engine)
    tabelas_existentes = set(inspetor.get_table_names())

    faltando = TABELAS_ESPERADAS - tabelas_existentes
    assert not faltando, f"Tabelas ausentes após a migração: {faltando}"


def test_chave_estrangeira_promotor_supervisor_configurada() -> None:
    inspetor = inspect(engine)
    fks = inspetor.get_foreign_keys("promotores")
    colunas_fk = {fk["constrained_columns"][0] for fk in fks}

    assert "supervisor_id" in colunas_fk
