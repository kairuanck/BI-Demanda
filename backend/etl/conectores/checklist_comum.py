"""Lógica comum de templates/perguntas/respostas dos conectores de checklist.

Compartilhada por `ConectorChecklistSb` e `ConectorWeCheck` — ambos
transformam colunas wide em perguntas e células preenchidas em respostas,
alimentando o MESMO modelo de domínio (Strategy, docs/DECISIONS.md, 11.6).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TipoRespostaChecklist
from app.infrastructure.models import Checklist, ChecklistPergunta, ChecklistResposta, Visita
from etl.conectores.leitura import celula
from etl.resultado import ErroLinha
from etl.transformers import para_texto


def desambiguar_enunciados(colunas: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Colunas com o mesmo enunciado no mesmo formulário recebem sufixo (n).

    Sem isso, duas colunas idênticas colidiriam na mesma pergunta e a
    segunda resposta seria tratada como conflito.
    """

    vistos: dict[str, int] = {}
    resultado: list[tuple[int, str]] = []
    for posicao, enunciado in colunas:
        ocorrencias = vistos.get(enunciado, 0)
        vistos[enunciado] = ocorrencias + 1
        rotulo = enunciado if ocorrencias == 0 else f"{enunciado} ({ocorrencias + 1})"
        resultado.append((posicao, rotulo))
    return resultado


def obter_ou_criar_perguntas(
    session: Session,
    template: Checklist,
    perguntas_posicoes: list[tuple[int, str]],
) -> dict[int, ChecklistPergunta]:
    """Get-or-create por enunciado; perguntas novas entram no fim da ordem.

    Tolera schema drift real: meses novos trazem colunas novas, que viram
    perguntas adicionais do mesmo template (docs/DECISIONS.md, 11.3).
    `obrigatoria=False` e tipo TEXTO porque a origem não informa nem um nem
    outro — e inferir é proibido.
    """

    existentes = {
        pergunta.enunciado: pergunta
        for pergunta in session.scalars(
            select(ChecklistPergunta).where(ChecklistPergunta.checklist_id == template.id)
        )
    }
    proxima_ordem = max((p.ordem for p in existentes.values()), default=0) + 1
    por_posicao: dict[int, ChecklistPergunta] = {}
    for posicao, enunciado in desambiguar_enunciados(perguntas_posicoes):
        enunciado = enunciado[:500]
        pergunta = existentes.get(enunciado)
        if pergunta is None:
            pergunta = ChecklistPergunta(
                checklist_id=template.id,
                ordem=proxima_ordem,
                enunciado=enunciado,
                tipo_resposta=TipoRespostaChecklist.TEXTO,
                obrigatoria=False,
            )
            session.add(pergunta)
            session.flush()
            existentes[enunciado] = pergunta
            proxima_ordem += 1
        por_posicao[posicao] = pergunta
    return por_posicao


def gravar_respostas(
    session: Session,
    aba_titulo: str,
    numero: int,
    linha: tuple[Any, ...],
    visita: Visita,
    perguntas_por_posicao: dict[int, ChecklistPergunta],
    importacao_id: str,
) -> list[ErroLinha]:
    """Células preenchidas → respostas (wide→long). Nunca sobrescreve:
    resposta idêntica é idempotente; divergente vira erro de linha."""

    existentes = {
        resposta.checklist_pergunta_id: resposta
        for resposta in session.scalars(
            select(ChecklistResposta).where(ChecklistResposta.visita_id == visita.id)
        )
    }
    conflitos: list[ErroLinha] = []
    for posicao, pergunta in perguntas_por_posicao.items():
        valor = para_texto(celula(linha, posicao))
        if valor is None:
            continue  # célula vazia: o template não usa esta pergunta nesta linha
        existente = existentes.get(pergunta.id)
        if existente is not None:
            if existente.resposta_valor != valor:
                conflitos.append(
                    ErroLinha(
                        numero,
                        f"Aba '{aba_titulo}': resposta já registrada com valor diferente "
                        f"para a visita {visita.codigo_externo} — dados nunca são "
                        "sobrescritos.",
                        pergunta.enunciado[:100],
                        valor[:100],
                    )
                )
            continue
        session.add(
            ChecklistResposta(
                visita_id=visita.id,
                checklist_pergunta_id=pergunta.id,
                resposta_valor=valor,
                importacao_id=importacao_id,
            )
        )
    return conflitos
