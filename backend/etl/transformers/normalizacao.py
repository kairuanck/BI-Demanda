"""Conversores de normalização de valores (ETL.md, Etapa 3 — Transform).

Cada função converte um valor bruto de célula Excel para o tipo de
destino, retornando `None` quando o valor é inconversível — cabe ao
validador transformar isso no erro de linha apropriado (VALIDADOR.md).
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from typing import Any


def para_texto(valor: Any) -> str | None:
    """Texto normalizado: trim e colapso de espaços internos duplicados."""

    if valor is None:
        return None
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)  # 123.0 lido pelo Excel vira "123", preservando códigos
    texto = " ".join(str(valor).split())
    return texto or None


def para_inteiro(valor: Any) -> int | None:
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        return int(valor) if valor.is_integer() else None
    try:
        return int(str(valor).strip())
    except ValueError:
        return None


def para_decimal(valor: Any) -> Decimal | None:
    """Aceita separador decimal ',' ou '.' (IMPORTADOR.md, seção 2, item 4)."""

    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, int | float):
        return Decimal(str(valor))
    texto = str(valor).strip().replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def para_data(valor: Any) -> date | None:
    """Aceita data nativa do Excel ou texto DD/MM/AAAA (IMPORTADOR.md, seção 2, item 3)."""

    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def para_hora(valor: Any) -> time | None:
    if valor is None:
        return None
    if isinstance(valor, time):
        return valor
    if isinstance(valor, datetime):
        return valor.time()
    texto = str(valor).strip()
    for formato in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(texto, formato).time()
        except ValueError:
            continue
    return None


def para_data_hora(valor: Any) -> datetime | None:
    """Aceita datetime nativo do Excel ou texto DD/MM/AAAA HH:MM(:SS)."""

    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day)
    texto = str(valor).strip()
    for formato in (
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


def para_percentual(valor: Any) -> Decimal | None:
    """Converte "100%", "12,5%" ou número em Decimal (valor percentual)."""

    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.strip().rstrip("%").strip()
        if not valor:
            return None
    return para_decimal(valor)
