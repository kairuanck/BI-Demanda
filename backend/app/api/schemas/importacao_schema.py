"""Schemas Pydantic dos endpoints de Importação (API.md, seção 9)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.domain.enums import StatusImportacao, TipoArquivoImportacao


class ImportacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo_arquivo: TipoArquivoImportacao
    nome_arquivo_original: str
    hash_sha256: str
    hash_conteudo: str | None
    tamanho_bytes: int
    competencia: date | None
    usuario_id: str
    status: StatusImportacao
    versao: int
    importacao_pai_id: str | None
    usuario_nome: str
    total_linhas: int
    linhas_validas: int
    linhas_invalidas: int
    iniciado_em: datetime | None
    concluido_em: datetime | None
    criado_em: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duracao_segundos(self) -> float | None:
        """Tempo de processamento (Sprint 6, Tela de Importações).

        Era uma `@property` simples (não serializada pelo Pydantic v2 sem
        `@computed_field`) — nunca aparecia na resposta da API; corrigido
        aqui porque a Central de Importações depende deste campo.
        """

        if self.iniciado_em and self.concluido_em:
            return (self.concluido_em - self.iniciado_em).total_seconds()
        return None


class ImportacaoErroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    numero_linha: int
    coluna: str | None
    valor_recebido: str | None
    mensagem_erro: str


class ImportacaoArquivoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    importacao_id: str
    caminho_armazenamento: str
    nome_arquivo: str
    criado_em: datetime


class PaginaImportacoesResponse(BaseModel):
    itens: list[ImportacaoResponse]
    pagina: int
    tamanho_pagina: int
    total_itens: int
    total_paginas: int


class PaginaErrosResponse(BaseModel):
    itens: list[ImportacaoErroResponse]
    pagina: int
    tamanho_pagina: int
    total_itens: int
    total_paginas: int
