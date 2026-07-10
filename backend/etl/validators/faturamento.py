"""Validador do Faturamento Mensal (VALIDADOR.md, seção 8; IMPORTADOR.md, seção 5)."""

from __future__ import annotations

from datetime import date
from typing import Any

from etl.resultado import ErroLinha, LinhaValida, ResultadoValidacao
from etl.transformers import para_decimal, para_inteiro, para_texto
from etl.validators.contexto import ContextoValidacao


def validar_faturamento(
    linhas: list[tuple[int, dict[str, Any]]], contexto: ContextoValidacao
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    ano_maximo = date.today().year + 1

    for numero, bruto in linhas:
        erros: list[ErroLinha] = []
        codigo_cliente = para_texto(bruto.get("CODIGO_CLIENTE"))
        codigo_laboratorio = para_texto(bruto.get("CODIGO_LABORATORIO"))
        codigo_departamento = para_texto(bruto.get("CODIGO_DEPARTAMENTO"))
        ano = para_inteiro(bruto.get("ANO"))
        mes = para_inteiro(bruto.get("MES"))
        valor = para_decimal(bruto.get("VALOR_FATURADO"))
        quantidade = para_decimal(bruto.get("QUANTIDADE"))

        if not codigo_cliente:
            erros.append(
                ErroLinha(
                    numero, "Campo obrigatório não preenchido: CODIGO_CLIENTE.", "CODIGO_CLIENTE"
                )
            )
        elif contexto.cliente_id_por_codigo(codigo_cliente) is None:
            # REF-002
            erros.append(
                ErroLinha(
                    numero,
                    f"Cliente não encontrado: {codigo_cliente}.",
                    "CODIGO_CLIENTE",
                    codigo_cliente,
                )
            )

        if not codigo_laboratorio:
            erros.append(
                ErroLinha(
                    numero,
                    "Campo obrigatório não preenchido: CODIGO_LABORATORIO.",
                    "CODIGO_LABORATORIO",
                )
            )
        if not codigo_departamento:
            erros.append(
                ErroLinha(
                    numero,
                    "Campo obrigatório não preenchido: CODIGO_DEPARTAMENTO.",
                    "CODIGO_DEPARTAMENTO",
                )
            )

        if ano is None or not (2000 <= ano <= ano_maximo):
            # FAT-001
            valor_ano = para_texto(bruto.get("ANO"))
            erros.append(
                ErroLinha(
                    numero, f"Ano fora do intervalo permitido: {valor_ano}.", "ANO", valor_ano
                )
            )
        if mes is None or not (1 <= mes <= 12):
            # FAT-002
            valor_mes = para_texto(bruto.get("MES"))
            erros.append(ErroLinha(numero, f"Mês inválido: {valor_mes}.", "MES", valor_mes))
        if valor is None:
            # FAT-003 (negativo é permitido — estorno)
            valor_bruto = para_texto(bruto.get("VALOR_FATURADO"))
            erros.append(
                ErroLinha(
                    numero,
                    f"Valor faturado inválido: {valor_bruto}.",
                    "VALOR_FATURADO",
                    valor_bruto,
                )
            )
        if bruto.get("QUANTIDADE") is not None and (quantidade is None or quantidade < 0):
            # FAT-004
            valor_qtd = para_texto(bruto.get("QUANTIDADE"))
            erros.append(
                ErroLinha(numero, f"Quantidade inválida: {valor_qtd}.", "QUANTIDADE", valor_qtd)
            )

        if erros:
            resultado.erros.extend(erros)
            continue

        resultado.linhas_validas.append(
            LinhaValida(
                numero_linha=numero,
                dados={
                    "codigo_cliente": codigo_cliente,
                    "codigo_laboratorio": codigo_laboratorio,
                    "nome_laboratorio": para_texto(bruto.get("NOME_LABORATORIO")),
                    "codigo_departamento": codigo_departamento,
                    "nome_departamento": para_texto(bruto.get("NOME_DEPARTAMENTO")),
                    "codigo_vendedor": para_texto(bruto.get("CODIGO_VENDEDOR")),
                    "nome_vendedor": para_texto(bruto.get("NOME_VENDEDOR")),
                    "ano": ano,
                    "mes": mes,
                    "valor_faturado": valor,
                    "quantidade": quantidade,
                },
            )
        )

    return resultado
