"""Contrato dos conectores de origem (Strategy Pattern, Sprint 3).

O motor de importação executa as etapas comuns a qualquer arquivo
(hash binário + hash de conteúdo, duplicidade, versionamento, transação,
registro de erros, auditoria, fluxo físico). O que varia por sistema de
origem — estrutura do arquivo, transformação wide→long, validação e
carga — fica confinado ao conector correspondente.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

from app.infrastructure.models import Importacao
from etl.resultado import ErroLinha


@dataclass
class ExecucaoImportacao:
    """Contexto que o motor entrega ao conector para uma importação."""

    session: Session
    importacao: Importacao

    @property
    def importacao_id(self) -> str:
        return self.importacao.id

    @property
    def usuario_id(self) -> str:
        return self.importacao.usuario_id


@dataclass
class ResultadoConector:
    """Contagens e erros produzidos pelo conector.

    `total_linhas` conta as linhas lógicas da origem (após a transformação
    wide→long quando houver — o significado exato por fonte está em
    IMPORT_MAPPING.md). `estrutural_invalido` indica que o arquivo não tem
    a estrutura esperada e nada foi processado.
    """

    total_linhas: int = 0
    persistidas: int = 0
    erros: list[ErroLinha] = field(default_factory=list)
    estrutural_invalido: bool = False


class ConectorOrigem(ABC):
    """Strategy de importação por origem/estrutura de arquivo."""

    @abstractmethod
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        """Lê, transforma, valida e carrega o arquivo dentro da transação
        aberta pelo motor (que garante rollback em caso de exceção)."""
