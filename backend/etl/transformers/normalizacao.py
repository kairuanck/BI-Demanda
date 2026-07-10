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
