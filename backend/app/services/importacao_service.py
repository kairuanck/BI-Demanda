"""Serviço de Importações (BACKEND.md, camada services).

A partir da Sprint 6 a API também recebe upload multipart, elimina a
necessidade de terminal para importar dados e permite cancelar uma
importação ainda não iniciada — reaproveitando integralmente o pipeline
ETL (`etl/motor.py`, `etl/inferencia.py`) já usado pela CLI.
"""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.domain.excecoes import RegistroNaoEncontradoError, ValidacaoFalhouError
from app.infrastructure.models import Importacao, ImportacaoArquivo, ImportacaoErro
from app.repositories.importacao_repository import (
    ImportacaoRepository,
    PaginaErros,
    PaginaImportacoes,
)
from etl.inferencia import inferir_tipo_arquivo
from etl.motor import MotorImportacao


class ImportacaoService:
    def __init__(self, repository: ImportacaoRepository, motor: MotorImportacao) -> None:
        self.repository = repository
        self.motor = motor

    def listar(
        self,
        pagina: int,
        tamanho_pagina: int,
        tipo_arquivo: TipoArquivoImportacao | None,
        status: StatusImportacao | None,
    ) -> PaginaImportacoes:
        return self.repository.listar(pagina, tamanho_pagina, tipo_arquivo, status)

    def obter(self, importacao_id: str) -> Importacao:
        importacao = self.repository.obter(importacao_id)
        if importacao is None:
            raise RegistroNaoEncontradoError(f"Importação {importacao_id} não encontrada.")
        return importacao

    def listar_erros(self, importacao_id: str, pagina: int, tamanho_pagina: int) -> PaginaErros:
        self.obter(importacao_id)
        return self.repository.listar_erros(importacao_id, pagina, tamanho_pagina)

    def listar_versoes(self, importacao_id: str) -> list[Importacao]:
        importacao = self.obter(importacao_id)
        return [
            self.repository.anexar_usuario_nome(i)
            for i in self.repository.listar_versoes(importacao.tipo_arquivo)
        ]

    def obter_arquivo(self, importacao_id: str) -> ImportacaoArquivo:
        self.obter(importacao_id)
        arquivo = self.repository.obter_arquivo(importacao_id)
        if arquivo is None:
            raise RegistroNaoEncontradoError(
                f"A importação {importacao_id} não possui arquivo armazenado."
            )
        return arquivo

    def reprocessar(self, importacao_id: str) -> Importacao:
        """Reexecuta o pipeline a partir da cópia em archive/ (Sprint 2).

        A nova execução é uma importação independente: o controle de
        duplicidade continua valendo — reprocessar uma importação
        CONCLUIDA idêntica será recusado como duplicado (HASH.md).
        """

        original = self.obter(importacao_id)
        arquivo = self.repository.obter_arquivo(importacao_id)
        if arquivo is None:
            raise ValidacaoFalhouError(
                "Importação sem arquivo armazenado não pode ser reprocessada."
            )
        origem = self.motor.fluxo.base / arquivo.caminho_armazenamento
        if not origem.exists():
            raise RegistroNaoEncontradoError(
                f"Arquivo físico não encontrado em archive: {arquivo.caminho_armazenamento}."
            )
        destino = self.motor.fluxo.caminho_disponivel(
            self.motor.fluxo.incoming, original.nome_arquivo_original
        )
        shutil.copy2(str(origem), str(destino))
        resultado = self.motor.importar(
            destino, original.tipo_arquivo, original.usuario_id, competencia=original.competencia
        )
        return self.repository.anexar_usuario_nome(resultado)

    def excluir_pendente(self, importacao_id: str) -> None:
        """Exclui apenas importações com status PENDENTE (Sprint 2)."""

        importacao = self.obter(importacao_id)
        if importacao.status != StatusImportacao.PENDENTE:
            raise ValidacaoFalhouError(
                "Apenas importações com status PENDENTE podem ser excluídas."
            )
        self.repository.excluir(importacao)

    def importar_upload(
        self,
        conteudo: bytes,
        nome_arquivo: str,
        usuario_id: str,
        competencia: date | None,
    ) -> Importacao:
        """Recebe um arquivo enviado pela Web e executa o mesmo pipeline da CLI (Sprint 6).

        `nome_arquivo` é saneado com `Path(...).name` para descartar
        qualquer componente de diretório recebido do cliente antes de
        gravar em `incoming/`. O tipo é inferido pela estrutura do arquivo
        (`etl/inferencia.py`) — arquivo sem assinatura reconhecida é
        recusado sem criar registro de importação, igual à CLI.
        """

        nome_seguro = Path(nome_arquivo).name
        destino = self.motor.fluxo.caminho_disponivel(self.motor.fluxo.incoming, nome_seguro)
        destino.write_bytes(conteudo)

        tipo = inferir_tipo_arquivo(destino)
        if tipo is None:
            destino.unlink(missing_ok=True)
            raise ValidacaoFalhouError(
                f"Estrutura de '{nome_arquivo}' não foi reconhecida como nenhum tipo de "
                "importação suportado."
            )
        resultado = self.motor.importar(destino, tipo, usuario_id, competencia=competencia)
        return self.repository.anexar_usuario_nome(resultado)

    def cancelar(self, importacao_id: str, usuario_id: str) -> Importacao:
        """Cancela uma importação `PENDENTE`, antes de iniciar o processamento (Sprint 6).

        Processamento nesta arquitetura é síncrono (sem fila em segundo
        plano) — não há execução "em andamento" para interromper, por isso
        o cancelamento se aplica apenas ao estado anterior ao início.
        """

        importacao = self.obter(importacao_id)
        if importacao.status != StatusImportacao.PENDENTE:
            raise ValidacaoFalhouError(
                "Apenas importações com status PENDENTE podem ser canceladas."
            )
        return self.motor.cancelar(importacao, usuario_id)

    def listar_todos_erros(self, importacao_id: str) -> list[ImportacaoErro]:
        """Todos os erros de uma importação, sem paginação — para o relatório baixável."""

        self.obter(importacao_id)
        return self.repository.listar_todos_erros(importacao_id)


def montar_paginacao(total_itens: int, pagina: int, tamanho_pagina: int) -> dict[str, int]:
    """Campos de paginação no formato da API.md, seção 2, item 4."""

    total_paginas = (total_itens + tamanho_pagina - 1) // tamanho_pagina if total_itens else 0
    return {
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total_itens": total_itens,
        "total_paginas": total_paginas,
    }


__all__ = ["ImportacaoService", "montar_paginacao", "ImportacaoErro"]
