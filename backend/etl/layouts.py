"""Layouts de colunas esperados por tipo de arquivo (IMPORTADOR.md).

Nomes de coluna são comparados de forma normalizada (maiúsculas, sem
acento, espaços → underscore) — IMPORTADOR.md, seção 2, item 2.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import TipoArquivoImportacao


@dataclass(frozen=True)
class Layout:
    colunas_obrigatorias: tuple[str, ...]
    colunas_opcionais: tuple[str, ...] = ()

    @property
    def todas(self) -> tuple[str, ...]:
        return self.colunas_obrigatorias + self.colunas_opcionais


LAYOUTS: dict[TipoArquivoImportacao, Layout] = {
    # IMPORTADOR.md, seção 3.1
    TipoArquivoImportacao.CLIENTES: Layout(
        colunas_obrigatorias=("CODIGO_CLIENTE", "RAZAO_SOCIAL", "UF", "CIDADE"),
        colunas_opcionais=("NOME_FANTASIA", "CNPJ_CPF", "ENDERECO", "CANAL"),
    ),
    # IMPORTADOR.md, seção 4.1 — NOME/TIPO/SUPERVISOR são condicionais
    # (obrigatórios apenas quando o promotor/supervisor é inédito), por
    # isso entram como opcionais no layout e são exigidos pelo validador.
    TipoArquivoImportacao.CARTEIRA: Layout(
        colunas_obrigatorias=(
            "CODIGO_CLIENTE",
            "CODIGO_PROMOTOR",
            "CODIGO_SUPERVISOR",
            "DATA_REFERENCIA",
        ),
        colunas_opcionais=("NOME_PROMOTOR", "TIPO_PROMOTOR", "NOME_SUPERVISOR"),
    ),
    # IMPORTADOR.md, seção 5.1
    TipoArquivoImportacao.FATURAMENTO: Layout(
        colunas_obrigatorias=(
            "CODIGO_CLIENTE",
            "CODIGO_LABORATORIO",
            "CODIGO_DEPARTAMENTO",
            "ANO",
            "MES",
            "VALOR_FATURADO",
        ),
        colunas_opcionais=(
            "NOME_LABORATORIO",
            "NOME_DEPARTAMENTO",
            "CODIGO_VENDEDOR",
            "NOME_VENDEDOR",
            "QUANTIDADE",
        ),
    ),
    # IMPORTADOR.md, seção 6.1
    TipoArquivoImportacao.CHECKLIST: Layout(
        colunas_obrigatorias=("ID_VISITA", "ORDEM_PERGUNTA", "RESPOSTA"),
    ),
    # IMPORTADOR.md, seção 7.1
    TipoArquivoImportacao.VISITAS: Layout(
        colunas_obrigatorias=("CODIGO_PROMOTOR", "CODIGO_CLIENTE", "DATA_VISITA"),
        colunas_opcionais=(
            "HORA_INICIO",
            "HORA_FIM",
            "TIPO_VISITA",
            "LATITUDE",
            "LONGITUDE",
            "OBSERVACOES",
            "STATUS",
        ),
    ),
}
