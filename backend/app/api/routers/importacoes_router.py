"""Endpoints de Importação (API.md, seção 9 — sem upload nesta sprint).

Autorização por perfil (PERMISSOES.md: Administrador) será aplicada na
sprint de autenticação — ver docs/DECISIONS.md.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.schemas.importacao_schema import (
    ImportacaoArquivoResponse,
    ImportacaoErroResponse,
    ImportacaoResponse,
    PaginaErrosResponse,
    PaginaImportacoesResponse,
)
from app.core.config import get_settings
from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.repositories.importacao_repository import ImportacaoRepository
from app.services.importacao_service import ImportacaoService, montar_paginacao
from etl.arquivos import FluxoArquivos
from etl.motor import MotorImportacao

router = APIRouter(prefix="/importacoes", tags=["importacoes"])


def get_importacao_service(db: Session = Depends(get_db_session)) -> ImportacaoService:
    fluxo = FluxoArquivos(Path(get_settings().storage_dir))
    motor = MotorImportacao(session=db, fluxo=fluxo)
    return ImportacaoService(repository=ImportacaoRepository(db), motor=motor)


@router.get("", response_model=PaginaImportacoesResponse)
def listar_importacoes(
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=20, ge=1, le=100),
    tipo_arquivo: TipoArquivoImportacao | None = None,
    status_importacao: StatusImportacao | None = Query(default=None, alias="status"),
    service: ImportacaoService = Depends(get_importacao_service),
) -> PaginaImportacoesResponse:
    resultado = service.listar(pagina, tamanho_pagina, tipo_arquivo, status_importacao)
    return PaginaImportacoesResponse(
        itens=[ImportacaoResponse.model_validate(i) for i in resultado.itens],
        **montar_paginacao(resultado.total_itens, pagina, tamanho_pagina),
    )


@router.get("/{importacao_id}", response_model=ImportacaoResponse)
def obter_importacao(
    importacao_id: str,
    service: ImportacaoService = Depends(get_importacao_service),
) -> ImportacaoResponse:
    return ImportacaoResponse.model_validate(service.obter(importacao_id))


@router.get("/{importacao_id}/erros", response_model=PaginaErrosResponse)
def listar_erros_importacao(
    importacao_id: str,
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=20, ge=1, le=100),
    service: ImportacaoService = Depends(get_importacao_service),
) -> PaginaErrosResponse:
    resultado = service.listar_erros(importacao_id, pagina, tamanho_pagina)
    return PaginaErrosResponse(
        itens=[ImportacaoErroResponse.model_validate(e) for e in resultado.itens],
        **montar_paginacao(resultado.total_itens, pagina, tamanho_pagina),
    )


@router.get("/{importacao_id}/versoes", response_model=list[ImportacaoResponse])
def listar_versoes_importacao(
    importacao_id: str,
    service: ImportacaoService = Depends(get_importacao_service),
) -> list[ImportacaoResponse]:
    return [ImportacaoResponse.model_validate(i) for i in service.listar_versoes(importacao_id)]


@router.get("/{importacao_id}/arquivo", response_model=ImportacaoArquivoResponse)
def obter_arquivo_importacao(
    importacao_id: str,
    service: ImportacaoService = Depends(get_importacao_service),
) -> ImportacaoArquivoResponse:
    return ImportacaoArquivoResponse.model_validate(service.obter_arquivo(importacao_id))


@router.post("/{importacao_id}/reprocessar", response_model=ImportacaoResponse)
def reprocessar_importacao(
    importacao_id: str,
    service: ImportacaoService = Depends(get_importacao_service),
) -> ImportacaoResponse:
    return ImportacaoResponse.model_validate(service.reprocessar(importacao_id))


@router.delete("/{importacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_importacao_pendente(
    importacao_id: str,
    service: ImportacaoService = Depends(get_importacao_service),
) -> None:
    service.excluir_pendente(importacao_id)
