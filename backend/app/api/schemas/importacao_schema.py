"""Schemas Pydantic dos endpoints de Importação (API.md, seção 9)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import StatusImportacao, TipoArquivoImportacao


class ImportacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_arquivo: TipoArquivoImportacao
    nome_arquivo_original: str
    hash_sha256: str
    tamanho_bytes: int
    usuario_id: int
    status: StatusImportacao
    versao: int
    importacao_pai_id: int | None
    total_linhas: int
    linhas_validas: int
    linhas_invalidas: int
    iniciado_em: datetime | None
    concluido_em: datetime | None
    criado_em: datetime

    @property
    def duracao_segundos(self) -> float | None:
        if self.iniciado_em and self.concluido_em:
            return (self.concluido_em - self.iniciado_em).total_seconds()
        return None


class ImportacaoErroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_linha: int
    coluna: str | None
    valor_recebido: str | None
    mensagem_erro: str


class ImportacaoArquivoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    importacao_id: int
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
