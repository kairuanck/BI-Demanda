"""Validador da Base de Clientes (VALIDADOR.md, seção 6; IMPORTADOR.md, seção 3)."""

from __future__ import annotations

import re
from typing import Any

from etl.resultado import ErroLinha, LinhaValida, ResultadoValidacao
from etl.transformers import para_texto
from etl.validators.contexto import ContextoValidacao

_CNPJ_CPF_RE = re.compile(r"^\d{11}$|^\d{14}$")


def validar_clientes(
    linhas: list[tuple[int, dict[str, Any]]], contexto: ContextoValidacao
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    codigos_vistos: set[str] = set()

    for numero, bruto in linhas:
        erros: list[ErroLinha] = []
        codigo = para_texto(bruto.get("CODIGO_CLIENTE"))
        razao = para_texto(bruto.get("RAZAO_SOCIAL"))
        uf = para_texto(bruto.get("UF"))
        cidade = para_texto(bruto.get("CIDADE"))

        if not codigo:
            erros.append(
                ErroLinha(
                    numero, "Campo obrigatório não preenchido: CODIGO_CLIENTE.", "CODIGO_CLIENTE"
                )
            )
        elif len(codigo) > 50:
            erros.append(
                ErroLinha(
                    numero,
                    "Código excede o tamanho máximo em CODIGO_CLIENTE.",
                    "CODIGO_CLIENTE",
                    codigo,
                )
            )
        elif codigo in codigos_vistos:
            # CLI-001
            erros.append(
                ErroLinha(
                    numero,
                    f"Código de cliente duplicado no arquivo: {codigo}.",
                    "CODIGO_CLIENTE",
                    codigo,
                )
            )
        else:
            codigos_vistos.add(codigo)

        if not razao:
            erros.append(
                ErroLinha(numero, "Campo obrigatório não preenchido: RAZAO_SOCIAL.", "RAZAO_SOCIAL")
            )
        if not cidade:
            erros.append(ErroLinha(numero, "Campo obrigatório não preenchido: CIDADE.", "CIDADE"))

        uf_normalizada = uf.upper() if uf else None
        if not uf_normalizada:
            erros.append(ErroLinha(numero, "Campo obrigatório não preenchido: UF.", "UF"))
        elif not contexto.uf_existe(uf_normalizada):
            # REF-001
            erros.append(
                ErroLinha(numero, f"UF inexistente: {uf_normalizada}.", "UF", uf_normalizada)
            )

        cnpj_cpf = para_texto(bruto.get("CNPJ_CPF"))
        if cnpj_cpf:
            apenas_digitos = re.sub(r"\D", "", cnpj_cpf)
            if not _CNPJ_CPF_RE.match(apenas_digitos):
                # CLI-002
                erros.append(
                    ErroLinha(numero, f"CNPJ/CPF inválido: {cnpj_cpf}.", "CNPJ_CPF", cnpj_cpf)
                )
            else:
                cnpj_cpf = apenas_digitos

        if erros:
            resultado.erros.extend(erros)
            continue

        resultado.linhas_validas.append(
            LinhaValida(
                numero_linha=numero,
                dados={
                    "codigo_externo": codigo,
                    "razao_social": razao,
                    "nome_fantasia": para_texto(bruto.get("NOME_FANTASIA")),
                    "cnpj_cpf": cnpj_cpf,
                    "uf_sigla": uf_normalizada,
                    "cidade_nome": cidade,
                    "endereco": para_texto(bruto.get("ENDERECO")),
                    "canal": para_texto(bruto.get("CANAL")),
                },
            )
        )

    return resultado
