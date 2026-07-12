"""Serviço de Importações (BACKEND.md, camada services).

Sem upload nesta sprint — a API apenas consulta o histórico, reprocessa
a partir do arquivo arquivado e exclui importações pendentes.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.domain.excecoes import RegistroNaoEncontradoError, ValidacaoFalhouError
from app.infrastructure.models import Importacao, ImportacaoArquivo, ImportacaoErro
from app.repositories.importacao_repository import (
    ImportacaoRepository,
    PaginaErros,
    PaginaImportacoes,
)
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
        return self.repository.listar_versoes(importacao.tipo_arquivo)

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
        destino = self.motor.fluxo.incoming / original.nome_arquivo_original
        contador = 1
        while destino.exists():
            destino = self.motor.fluxo.incoming / (
                f"{Path(original.nome_arquivo_original).stem}_{contador}"
                f"{Path(original.nome_arquivo_original).suffix}"
            )
            contador += 1
        shutil.copy2(str(origem), str(destino))
        return self.motor.importar(destino, original.tipo_arquivo, original.usuario_id)

    def excluir_pendente(self, importacao_id: str) -> None:
        """Exclui apenas importações com status PENDENTE (Sprint 2)."""

        importacao = self.obter(importacao_id)
        if importacao.status != StatusImportacao.PENDENTE:
            raise ValidacaoFalhouError(
                "Apenas importações com status PENDENTE podem ser excluídas."
            )
        self.repository.excluir(importacao)


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
