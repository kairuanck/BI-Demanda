"""Construtores de planilhas .xlsx de teste (TESTES.md, seção 8).

Gerados em tempo de teste via OpenPyXL — determinísticos, sem binários no
repositório. Os arquivos são gravados diretamente em `fluxo.incoming`.
"""

from __future__ import annotations

import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from etl.arquivos import FluxoArquivos

# O OpenPyXL grava `created`/`modified` em docProps/core.xml. `created` pode
# ser fixado, mas `modified` é sobrescrito com datetime.now() dentro do
# próprio writer (openpyxl/writer/excel.py), independentemente do valor
# atribuído antes de workbook.save(). Ou seja: dois arquivos com conteúdo
# idêntico gerados via criar_xlsx() em segundos diferentes SEMPRE produzem
# bytes (e hash SHA-256) diferentes — não há como neutralizar isso pela
# API pública do openpyxl. Fixar `created` aqui é só uma redução parcial de
# ruído; testes que precisem de hash idêntico devem usar duplicar_arquivo().
_TIMESTAMP_DETERMINISTICO = datetime(2026, 1, 1, 0, 0, 0)


def criar_xlsx(destino: Path, colunas: list[str], linhas: list[list[Any]]) -> Path:
    workbook = Workbook()
    workbook.properties.created = _TIMESTAMP_DETERMINISTICO
    aba = workbook.active
    aba.append(colunas)
    for linha in linhas:
        aba.append(linha)
    workbook.save(destino)
    return destino


def duplicar_arquivo(origem: Path, novo_nome: str) -> Path:
    """Copia um arquivo já gerado byte a byte, com outro nome.

    Usado para simular o cenário real de "o mesmo arquivo reenviado sob
    outro nome" (HASH.md, seção 3), garantindo hash SHA-256 idêntico —
    diferente de gerar duas planilhas equivalentes via OpenPyXL, cujo
    `modified` interno as torna sempre distintas em bytes.
    """

    destino = origem.parent / novo_nome
    shutil.copy2(origem, destino)
    return destino


def xlsx_clientes(
    fluxo: FluxoArquivos, nome: str = "clientes.xlsx", linhas: list[list[Any]] | None = None
) -> Path:
    colunas = [
        "CODIGO_CLIENTE",
        "RAZAO_SOCIAL",
        "NOME_FANTASIA",
        "CNPJ_CPF",
        "UF",
        "CIDADE",
        "ENDERECO",
        "CANAL",
    ]
    if linhas is None:
        linhas = [
            [
                "C001",
                "Pet Shop Alfa Ltda",
                "Pet Alfa",
                "11222333000144",
                "SP",
                "Campinas",
                "Rua A, 100",
                "Pet Shop",
            ],
            [
                "C002",
                "Clínica Vet Beta",
                None,
                "22333444000155",
                "SP",
                "São Paulo",
                None,
                "Clínica Veterinária",
            ],
            [
                "C003",
                "Distribuidora Gama",
                "Gama Dist",
                None,
                "MG",
                "Belo Horizonte",
                None,
                "Distribuidor",
            ],
        ]
    return criar_xlsx(fluxo.incoming / nome, colunas, linhas)


def xlsx_carteira(
    fluxo: FluxoArquivos,
    nome: str = "carteira.xlsx",
    linhas: list[list[Any]] | None = None,
    data_referencia: date | None = None,
) -> Path:
    colunas = [
        "CODIGO_CLIENTE",
        "CODIGO_PROMOTOR",
        "NOME_PROMOTOR",
        "TIPO_PROMOTOR",
        "CODIGO_SUPERVISOR",
        "NOME_SUPERVISOR",
        "DATA_REFERENCIA",
    ]
    referencia = data_referencia or date(2026, 6, 1)
    if linhas is None:
        linhas = [
            ["C001", "P001", "Promotor Um", "TECNICO", "S001", "Supervisor Um", referencia],
            ["C002", "P001", "Promotor Um", "TECNICO", "S001", "Supervisor Um", referencia],
            ["C003", "P002", "Promotor Dois", "TRADE", "S001", "Supervisor Um", referencia],
        ]
    return criar_xlsx(fluxo.incoming / nome, colunas, linhas)


def xlsx_faturamento(
    fluxo: FluxoArquivos, nome: str = "faturamento.xlsx", linhas: list[list[Any]] | None = None
) -> Path:
    colunas = [
        "CODIGO_CLIENTE",
        "CODIGO_LABORATORIO",
        "NOME_LABORATORIO",
        "CODIGO_DEPARTAMENTO",
        "NOME_DEPARTAMENTO",
        "CODIGO_VENDEDOR",
        "NOME_VENDEDOR",
        "ANO",
        "MES",
        "VALOR_FATURADO",
        "QUANTIDADE",
    ]
    if linhas is None:
        linhas = [
            [
                "C001",
                "L01",
                "Lab Um",
                "D01",
                "Nutrição",
                "V01",
                "Vendedor Um",
                2026,
                5,
                "1500,50",
                10,
            ],
            ["C002", "L01", "Lab Um", "D02", "Saúde Animal", None, None, 2026, 5, 2300.75, None],
            [
                "C001",
                "L02",
                "Lab Dois",
                "D01",
                "Nutrição",
                "V01",
                "Vendedor Um",
                2026,
                5,
                "-120,00",
                1,
            ],
        ]
    return criar_xlsx(fluxo.incoming / nome, colunas, linhas)


def xlsx_visitas(
    fluxo: FluxoArquivos, nome: str = "visitas.xlsx", linhas: list[list[Any]] | None = None
) -> Path:
    colunas = [
        "CODIGO_PROMOTOR",
        "CODIGO_CLIENTE",
        "DATA_VISITA",
        "HORA_INICIO",
        "HORA_FIM",
        "TIPO_VISITA",
        "STATUS",
    ]
    if linhas is None:
        linhas = [
            ["P001", "C001", date(2026, 6, 10), "09:00", "10:00", "Rotina", "REALIZADA"],
            ["P001", "C002", date(2026, 6, 11), None, None, "Rotina", None],
        ]
    return criar_xlsx(fluxo.incoming / nome, colunas, linhas)


def xlsx_checklist(
    fluxo: FluxoArquivos, nome: str = "checklist.xlsx", linhas: list[list[Any]] | None = None
) -> Path:
    colunas = ["ID_VISITA", "ORDEM_PERGUNTA", "RESPOSTA"]
    if linhas is None:
        linhas = [[1, 1, "SIM"], [1, 2, "Gôndola organizada"]]
    return criar_xlsx(fluxo.incoming / nome, colunas, linhas)
