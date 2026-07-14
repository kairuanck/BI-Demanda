"""Inferência estrutural do tipo de arquivo (Sprint 3, Fase 5).

Extraído de `etl/cli.py` na Sprint 6 para ser reutilizado também pelo
endpoint HTTP de upload (`app/api/routers/importacoes_router.py`) — a CLI
segue reexportando `inferir_tipo_arquivo` para não quebrar os chamadores
existentes (docs/DECISIONS.md).

Inferência sempre pela estrutura (nome de aba conhecido, ou conjunto de
colunas do cabeçalho da primeira aba) — nunca pelo nome do arquivo, que é
livre nos exports reais. Arquivo que não casa com nenhuma assinatura é
reportado como não reconhecido, nunca importado às cegas.
"""

from __future__ import annotations

from pathlib import Path

from app.domain.enums import TipoArquivoImportacao
from etl.conectores.leitura import ler_abas

_ABAS_BASE_CLIENTES = {"CÓDIGO", "CNPJ/CPF", "CLIENTE", "ESTADO"}
_ABAS_SB_PRODUTOS = {"PRODUTOS", "GONDOLA", "PRODUTOSIMILAR", "TAREFAS"}
_COLUNAS_SB_SUPERVISOR = {
    "ÁREA",
    "VISITAS PREVISTAS",
    "PREVISTAS REALIZADAS",
    "NÃO VISITAS",
}
_COLUNAS_PAINEL_AVERT = {"CNPJ", "CONSULTOR", "GRUPO ECONÔMICO", "SEGMENTO"}
_COLUNAS_WECHECK = {"FORMULÁRIO", "AUTOR", "DATA / HORA DO ITEM"}
_COLUNAS_CHECKLIST = {"VISITA", "CK_ID", "APLICAÇÃO"}
_COLUNAS_FATURAMENTO = {"DEPARTAMENTO"}


def inferir_tipo_arquivo(caminho: Path) -> TipoArquivoImportacao | None:
    """Estrutura do arquivo → tipo, nunca o nome (docs/DECISIONS.md, 11.3)."""

    try:
        abas = ler_abas(caminho)
    except Exception:  # noqa: BLE001 - arquivo ilegível: deixa o motor recusar
        return None
    if not abas:
        return None

    titulos = {aba.titulo.strip().upper() for aba in abas}
    if titulos & _ABAS_SB_PRODUTOS:
        return TipoArquivoImportacao.SB_PRODUTOS

    primeira = abas[0]
    cabecalho = {c.strip().upper() for c in primeira.cabecalho() if c}
    if _COLUNAS_CHECKLIST <= cabecalho:
        return TipoArquivoImportacao.CHECKLIST
    if _COLUNAS_SB_SUPERVISOR <= cabecalho:
        return TipoArquivoImportacao.CARTEIRA
    if _COLUNAS_PAINEL_AVERT <= cabecalho:
        return TipoArquivoImportacao.PAINEL_AVERT
    if _COLUNAS_WECHECK <= cabecalho:
        return TipoArquivoImportacao.WECHECK
    if _COLUNAS_FATURAMENTO <= cabecalho:
        return TipoArquivoImportacao.FATURAMENTO
    if _ABAS_BASE_CLIENTES <= cabecalho:
        return TipoArquivoImportacao.CLIENTES
    return None
