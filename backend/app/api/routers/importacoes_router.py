"""Endpoints de Importação (API.md, seção 9).

A partir da Sprint 6, upload multipart elimina a necessidade de terminal
para importar dados (docs/DECISIONS.md). Autorização por perfil
(PERMISSOES.md: Administrador) será aplicada na sprint de autenticação.
"""

from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import StreamingResponse
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
from app.services.usuario_service import obter_ou_criar_usuario_sistema
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


@router.post("/upload", response_model=ImportacaoResponse, status_code=status.HTTP_201_CREATED)
async def enviar_importacao(
    arquivo: UploadFile = File(...),
    ano_competencia: int | None = Form(default=None),
    mes_competencia: int | None = Form(default=None),
    db: Session = Depends(get_db_session),
    service: ImportacaoService = Depends(get_importacao_service),
) -> ImportacaoResponse:
    """Upload Web (Sprint 6) — elimina a necessidade de terminal para importar dados.

    Sem autenticação nesta fase (AUTENTICACAO.md fica para sprint futura):
    a importação é registrada sob o mesmo usuário de sistema usado pela CLI
    (`app/services/usuario_service.py`).
    """

    competencia: date | None = None
    if ano_competencia is not None and mes_competencia is not None:
        competencia = date(ano_competencia, mes_competencia, 1)

    usuario = obter_ou_criar_usuario_sistema(db)
    conteudo = await arquivo.read()
    resultado = service.importar_upload(
        conteudo, arquivo.filename or "arquivo.xlsx", usuario.id, competencia
    )
    return ImportacaoResponse.model_validate(resultado)


@router.post("/{importacao_id}/cancelar", response_model=ImportacaoResponse)
def cancelar_importacao(
    importacao_id: str,
    db: Session = Depends(get_db_session),
    service: ImportacaoService = Depends(get_importacao_service),
) -> ImportacaoResponse:
    usuario = obter_ou_criar_usuario_sistema(db)
    return ImportacaoResponse.model_validate(service.cancelar(importacao_id, usuario.id))


@router.get("/{importacao_id}/erros/relatorio")
def baixar_relatorio_erros(
    importacao_id: str,
    service: ImportacaoService = Depends(get_importacao_service),
) -> StreamingResponse:
    """CSV com todos os erros de validação da importação (Sprint 6).

    BOM UTF-8 no início do arquivo garante acentuação correta ao abrir no
    Excel (mesma classe de problema de acentuação da Sprint 5).
    """

    erros = service.listar_todos_erros(importacao_id)
    buffer = io.StringIO()
    buffer.write("﻿")
    escritor = csv.writer(buffer, delimiter=";")
    escritor.writerow(["Linha", "Coluna", "Valor Recebido", "Mensagem de Erro"])
    for erro in erros:
        escritor.writerow(
            [erro.numero_linha, erro.coluna or "", erro.valor_recebido or "", erro.mensagem_erro]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="importacao_{importacao_id}_erros.csv"'
        },
    )
