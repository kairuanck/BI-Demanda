"""Validador de respostas de Checklist (VALIDADOR.md, seção 10; IMPORTADOR.md, seção 6)."""

from __future__ import annotations

from typing import Any

from app.domain.enums import TipoRespostaChecklist
from etl.resultado import ErroLinha, LinhaValida, ResultadoValidacao
from etl.transformers import para_decimal, para_inteiro, para_texto
from etl.validators.contexto import ContextoValidacao

_RESPOSTAS_SIM_NAO = {"SIM", "NAO", "NÃO"}


def validar_checklist(
    linhas: list[tuple[int, dict[str, Any]]], contexto: ContextoValidacao
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    pares_vistos: set[tuple[int, int]] = set()

    for numero, bruto in linhas:
        erros: list[ErroLinha] = []
        id_visita = para_inteiro(bruto.get("ID_VISITA"))
        ordem = para_inteiro(bruto.get("ORDEM_PERGUNTA"))
        resposta = para_texto(bruto.get("RESPOSTA"))

        if id_visita is None:
            valor = para_texto(bruto.get("ID_VISITA"))
            erros.append(
                ErroLinha(
                    numero, f"Valor numérico inválido em ID_VISITA: {valor}.", "ID_VISITA", valor
                )
            )
        elif not contexto.visita_existe(id_visita):
            # REF-004
            erros.append(
                ErroLinha(
                    numero, f"Visita não encontrada: {id_visita}.", "ID_VISITA", str(id_visita)
                )
            )

        if ordem is None:
            valor = para_texto(bruto.get("ORDEM_PERGUNTA"))
            erros.append(
                ErroLinha(
                    numero,
                    f"Valor numérico inválido em ORDEM_PERGUNTA: {valor}.",
                    "ORDEM_PERGUNTA",
                    valor,
                )
            )

        pergunta = None
        if id_visita is not None and ordem is not None and not erros:
            pergunta = contexto.resolver_pergunta(id_visita, ordem)
            if pergunta is None:
                # REF-005
                erros.append(
                    ErroLinha(
                        numero,
                        f"Pergunta de checklist não encontrada para a ordem informada: {ordem}.",
                        "ORDEM_PERGUNTA",
                        str(ordem),
                    )
                )

        if pergunta is not None and id_visita is not None and ordem is not None:
            par = (id_visita, pergunta.id)
            if par in pares_vistos:
                # CHK-004
                erros.append(
                    ErroLinha(
                        numero,
                        f"Resposta duplicada no arquivo para visita {id_visita} "
                        f"e pergunta {ordem}.",
                        "ORDEM_PERGUNTA",
                    )
                )
            elif contexto.resposta_existe(id_visita, pergunta.id):
                # UQ (visita, pergunta) do DICIONARIO_DE_DADOS.md — ver docs/DECISIONS.md
                erros.append(
                    ErroLinha(
                        numero,
                        f"Resposta já existente no sistema para visita {id_visita} "
                        f"e pergunta {ordem}.",
                        "ORDEM_PERGUNTA",
                    )
                )
            else:
                pares_vistos.add(par)

        if pergunta is not None:
            if not resposta:
                # CHK-003
                erros.append(
                    ErroLinha(
                        numero,
                        f"Resposta obrigatória não preenchida para a pergunta de ordem {ordem}.",
                        "RESPOSTA",
                    )
                )
            elif pergunta.tipo_resposta == TipoRespostaChecklist.SIM_NAO:
                if resposta.upper() not in _RESPOSTAS_SIM_NAO:
                    # CHK-001
                    erros.append(
                        ErroLinha(
                            numero,
                            f"Resposta inválida para pergunta Sim/Não: {resposta}.",
                            "RESPOSTA",
                            resposta,
                        )
                    )
            elif (
                pergunta.tipo_resposta == TipoRespostaChecklist.NUMERICO
                and para_decimal(resposta) is None
            ):
                # CHK-002
                erros.append(
                    ErroLinha(
                        numero, f"Resposta numérica inválida: {resposta}.", "RESPOSTA", resposta
                    )
                )

        if erros:
            resultado.erros.extend(erros)
            continue

        assert pergunta is not None and id_visita is not None  # garantido pelos ramos acima
        conforme: bool | None = None
        if pergunta.tipo_resposta == TipoRespostaChecklist.SIM_NAO and resposta is not None:
            conforme = resposta.upper() == "SIM"

        resultado.linhas_validas.append(
            LinhaValida(
                numero_linha=numero,
                dados={
                    "visita_id": id_visita,
                    "checklist_pergunta_id": pergunta.id,
                    "resposta_valor": resposta,
                    "conforme": conforme,
                },
            )
        )

    return resultado
