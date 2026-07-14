"""Repositório de Importações (BACKEND.md, camada repositories)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.infrastructure.models import Importacao, ImportacaoArquivo, ImportacaoErro, Usuario


@dataclass
class PaginaImportacoes:
    itens: list[Importacao]
    total_itens: int


@dataclass
class PaginaErros:
    itens: list[ImportacaoErro]
    total_itens: int


class ImportacaoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(
        self,
        pagina: int,
        tamanho_pagina: int,
        tipo_arquivo: TipoArquivoImportacao | None = None,
        status: StatusImportacao | None = None,
    ) -> PaginaImportacoes:
        consulta = select(Importacao, Usuario.nome).join(
            Usuario, Usuario.id == Importacao.usuario_id
        )
        if tipo_arquivo is not None:
            consulta = consulta.where(Importacao.tipo_arquivo == tipo_arquivo)
        if status is not None:
            consulta = consulta.where(Importacao.status == status)

        total = self.session.scalar(select(func.count()).select_from(consulta.subquery())) or 0
        pagina_consulta = (
            consulta.order_by(Importacao.criado_em.desc())
            .offset((pagina - 1) * tamanho_pagina)
            .limit(tamanho_pagina)
        )
        itens = [
            self._com_usuario_nome(importacao, nome)
            for importacao, nome in self.session.execute(pagina_consulta)
        ]
        return PaginaImportacoes(itens=itens, total_itens=total)

    def obter(self, importacao_id: str) -> Importacao | None:
        linha = self.session.execute(
            select(Importacao, Usuario.nome)
            .join(Usuario, Usuario.id == Importacao.usuario_id)
            .where(Importacao.id == importacao_id)
        ).first()
        if linha is None:
            return None
        return self._com_usuario_nome(*linha)

    @staticmethod
    def _com_usuario_nome(importacao: Importacao, usuario_nome: str) -> Importacao:
        """Anexa `usuario_nome` — atributo não mapeado, só em memória, para
        `ImportacaoResponse.usuario_nome` (Sprint 6); não é persistido pelo ORM.
        """

        importacao.usuario_nome = usuario_nome  # type: ignore[attr-defined]
        return importacao

    def anexar_usuario_nome(self, importacao: Importacao) -> Importacao:
        """Mesmo propósito de `_com_usuario_nome`, para uma `Importacao` já em mãos
        (ex.: resultado de `motor.importar`) — usada fora do fluxo paginado de
        `listar`/`obter`, onde uma segunda consulta pontual não é N+1 (Sprint 6).
        """

        nome = self.session.scalar(select(Usuario.nome).where(Usuario.id == importacao.usuario_id))
        return self._com_usuario_nome(importacao, nome or "—")

    def listar_erros(self, importacao_id: str, pagina: int, tamanho_pagina: int) -> PaginaErros:
        consulta = select(ImportacaoErro).where(ImportacaoErro.importacao_id == importacao_id)
        total = self.session.scalar(select(func.count()).select_from(consulta.subquery())) or 0
        itens = list(
            self.session.scalars(
                consulta.order_by(ImportacaoErro.numero_linha.asc())
                .offset((pagina - 1) * tamanho_pagina)
                .limit(tamanho_pagina)
            )
        )
        return PaginaErros(itens=itens, total_itens=total)

    def listar_todos_erros(self, importacao_id: str) -> list[ImportacaoErro]:
        """Todos os erros de uma importação, sem paginação — relatório baixável (Sprint 6)."""

        return list(
            self.session.scalars(
                select(ImportacaoErro)
                .where(ImportacaoErro.importacao_id == importacao_id)
                .order_by(ImportacaoErro.numero_linha.asc())
            )
        )

    def listar_versoes(self, tipo_arquivo: TipoArquivoImportacao) -> list[Importacao]:
        """Cadeia completa de versões de um tipo de arquivo (HASH.md, seção 5)."""

        return list(
            self.session.scalars(
                select(Importacao)
                .where(Importacao.tipo_arquivo == tipo_arquivo, Importacao.versao > 0)
                .order_by(Importacao.versao.asc(), Importacao.id.asc())
            )
        )

    def obter_arquivo(self, importacao_id: str) -> ImportacaoArquivo | None:
        return self.session.scalar(
            select(ImportacaoArquivo).where(ImportacaoArquivo.importacao_id == importacao_id)
        )

    def excluir(self, importacao: Importacao) -> None:
        self.session.delete(importacao)
        self.session.commit()
