"""Loader de respostas de Checklist (REGRAS_DE_NEGOCIO.md, seção 5.4).

O campo `conforme` já chega calculado pelo validador; duplicidades
(no arquivo e contra o banco) foram rejeitadas na validação, respeitando
a restrição UQ (visita_id, checklist_pergunta_id) — ver docs/DECISIONS.md.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.infrastructure.models import ChecklistResposta
from etl.resultado import LinhaValida


def carregar_checklist(
    session: Session, linhas: list[LinhaValida], importacao_id: int, usuario_id: int
) -> int:
    persistidas = 0
    for linha in linhas:
        dados = linha.dados
        session.add(
            ChecklistResposta(
                visita_id=dados["visita_id"],
                checklist_pergunta_id=dados["checklist_pergunta_id"],
                resposta_valor=dados["resposta_valor"],
                conforme=dados["conforme"],
                importacao_id=importacao_id,
            )
        )
        persistidas += 1
    return persistidas
