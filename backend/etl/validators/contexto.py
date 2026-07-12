"""Contexto de validação: consultas referenciais usadas pelos validadores.

Isola o acesso a banco em funções injetáveis, mantendo os validadores
testáveis sem sessão real (VALIDADOR.md, seção 5 — validações REF).
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TipoPromotorAlvo, TipoRespostaChecklist
from app.infrastructure.models import (
    Checklist,
    ChecklistPergunta,
    ChecklistResposta,
    Cliente,
    Promotor,
    TipoPromotorCadastro,
    Uf,
    Visita,
)


@dataclass(frozen=True)
class PerguntaInfo:
    id: str
    tipo_resposta: TipoRespostaChecklist
    obrigatoria: bool


@dataclass
class ContextoValidacao:
    session: Session

    def uf_existe(self, sigla: str) -> bool:
        return self.session.get(Uf, sigla.upper()) is not None

    def cliente_id_por_codigo(self, codigo: str) -> str | None:
        return self.session.scalar(select(Cliente.id).where(Cliente.codigo_externo == codigo))

    def promotor_id_por_codigo(self, codigo: str) -> str | None:
        return self.session.scalar(select(Promotor.id).where(Promotor.codigo_externo == codigo))

    def visita_existe(self, visita_id: str) -> bool:
        return self.session.get(Visita, visita_id) is not None

    def resposta_existe(self, visita_id: str, pergunta_id: str) -> bool:
        return (
            self.session.scalar(
                select(ChecklistResposta.id).where(
                    ChecklistResposta.visita_id == visita_id,
                    ChecklistResposta.checklist_pergunta_id == pergunta_id,
                )
            )
            is not None
        )

    def resolver_pergunta(self, visita_id: str, ordem: int) -> PerguntaInfo | None:
        """Localiza a pergunta pela ordem no template ativo do tipo do promotor
        da visita (IMPORTADOR.md, seção 6.2)."""

        visita = self.session.get(Visita, visita_id)
        if visita is None:
            return None
        promotor = self.session.get(Promotor, visita.promotor_id)
        if promotor is None:
            return None
        # Tipo agora é cadastral (tabela tipos_promotor); sem tipo definido,
        # apenas templates AMBOS são elegíveis.
        alvos = [TipoPromotorAlvo.AMBOS]
        if promotor.tipo_promotor_id is not None:
            tipo = self.session.get(TipoPromotorCadastro, promotor.tipo_promotor_id)
            if tipo is not None and tipo.codigo in TipoPromotorAlvo.__members__:
                alvos.insert(0, TipoPromotorAlvo(tipo.codigo))
        checklist_id = self.session.scalar(
            select(Checklist.id)
            .where(Checklist.ativo.is_(True), Checklist.tipo_promotor_alvo.in_(alvos))
            .order_by(Checklist.versao.desc(), Checklist.id.desc())
            .limit(1)
        )
        if checklist_id is None:
            return None
        pergunta = self.session.scalar(
            select(ChecklistPergunta).where(
                ChecklistPergunta.checklist_id == checklist_id,
                ChecklistPergunta.ordem == ordem,
            )
        )
        if pergunta is None:
            return None
        return PerguntaInfo(
            id=pergunta.id,
            tipo_resposta=pergunta.tipo_resposta,
            obrigatoria=pergunta.obrigatoria,
        )


def criar_contexto_validacao(session: Session) -> ContextoValidacao:
    return ContextoValidacao(session=session)
