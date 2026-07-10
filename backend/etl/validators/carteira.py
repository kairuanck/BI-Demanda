"""Validador da Carteira dos Promotores (VALIDADOR.md, seção 7; IMPORTADOR.md, seção 4)."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.domain.enums import TipoPromotor
from etl.resultado import ErroLinha, LinhaValida, ResultadoValidacao
from etl.transformers import para_data, para_texto
from etl.validators.contexto import ContextoValidacao


def validar_carteira(
    linhas: list[tuple[int, dict[str, Any]]], contexto: ContextoValidacao
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    clientes_vistos: set[str] = set()

    for numero, bruto in linhas:
        erros: list[ErroLinha] = []
        codigo_cliente = para_texto(bruto.get("CODIGO_CLIENTE"))
        codigo_promotor = para_texto(bruto.get("CODIGO_PROMOTOR"))
        codigo_supervisor = para_texto(bruto.get("CODIGO_SUPERVISOR"))
        data_referencia = para_data(bruto.get("DATA_REFERENCIA"))

        if not codigo_cliente:
            erros.append(
                ErroLinha(
                    numero, "Campo obrigatório não preenchido: CODIGO_CLIENTE.", "CODIGO_CLIENTE"
                )
            )
        elif codigo_cliente in clientes_vistos:
            # CAR-003: um cliente não pode ter dois promotores no mesmo arquivo
            erros.append(
                ErroLinha(
                    numero,
                    f"Cliente informado mais de uma vez no arquivo: {codigo_cliente}.",
                    "CODIGO_CLIENTE",
                    codigo_cliente,
                )
            )
        elif contexto.cliente_id_por_codigo(codigo_cliente) is None:
            # REF-002: a Carteira não cria clientes
            erros.append(
                ErroLinha(
                    numero,
                    f"Cliente não encontrado: {codigo_cliente}.",
                    "CODIGO_CLIENTE",
                    codigo_cliente,
                )
            )
        else:
            clientes_vistos.add(codigo_cliente)

        if not codigo_promotor:
            erros.append(
                ErroLinha(
                    numero, "Campo obrigatório não preenchido: CODIGO_PROMOTOR.", "CODIGO_PROMOTOR"
                )
            )
        if not codigo_supervisor:
            erros.append(
                ErroLinha(
                    numero,
                    "Campo obrigatório não preenchido: CODIGO_SUPERVISOR.",
                    "CODIGO_SUPERVISOR",
                )
            )

        if data_referencia is None:
            valor = para_texto(bruto.get("DATA_REFERENCIA"))
            erros.append(
                ErroLinha(
                    numero, f"Data inválida em DATA_REFERENCIA: {valor}.", "DATA_REFERENCIA", valor
                )
            )
        elif data_referencia > date.today():
            # CAR-002
            erros.append(
                ErroLinha(
                    numero,
                    "Data de referência não pode ser futura.",
                    "DATA_REFERENCIA",
                    str(data_referencia),
                )
            )

        tipo_promotor_texto = para_texto(bruto.get("TIPO_PROMOTOR"))
        tipo_promotor: TipoPromotor | None = None
        if tipo_promotor_texto:
            normalizado = tipo_promotor_texto.upper()
            if normalizado not in (TipoPromotor.TECNICO.value, TipoPromotor.TRADE.value):
                # CAR-001
                erros.append(
                    ErroLinha(
                        numero,
                        f"Tipo de promotor inválido: {tipo_promotor_texto}.",
                        "TIPO_PROMOTOR",
                        tipo_promotor_texto,
                    )
                )
            else:
                tipo_promotor = TipoPromotor(normalizado)

        # Promotor inédito exige NOME_PROMOTOR e TIPO_PROMOTOR (IMPORTADOR.md, seção 4.1)
        if codigo_promotor and contexto.promotor_id_por_codigo(codigo_promotor) is None:
            if not para_texto(bruto.get("NOME_PROMOTOR")):
                erros.append(
                    ErroLinha(
                        numero,
                        "Campo obrigatório não preenchido: NOME_PROMOTOR (promotor inédito).",
                        "NOME_PROMOTOR",
                    )
                )
            if tipo_promotor is None:
                erros.append(
                    ErroLinha(
                        numero,
                        "Campo obrigatório não preenchido: TIPO_PROMOTOR (promotor inédito).",
                        "TIPO_PROMOTOR",
                    )
                )

        if erros:
            resultado.erros.extend(erros)
            continue

        resultado.linhas_validas.append(
            LinhaValida(
                numero_linha=numero,
                dados={
                    "codigo_cliente": codigo_cliente,
                    "codigo_promotor": codigo_promotor,
                    "nome_promotor": para_texto(bruto.get("NOME_PROMOTOR")),
                    "tipo_promotor": tipo_promotor,
                    "codigo_supervisor": codigo_supervisor,
                    "nome_supervisor": para_texto(bruto.get("NOME_SUPERVISOR")),
                    "data_referencia": data_referencia,
                },
            )
        )

    return resultado
