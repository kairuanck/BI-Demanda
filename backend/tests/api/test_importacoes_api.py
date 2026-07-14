"""Testes dos endpoints REST de Importação (API.md, seção 9)."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import httpx
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.routers.importacoes_router import get_importacao_service
from app.domain.enums import StatusImportacao, TipoArquivoImportacao
from app.infrastructure.models import Importacao, Usuario
from app.main import app as fastapi_app
from app.repositories.importacao_repository import ImportacaoRepository
from app.services.importacao_service import ImportacaoService
from app.services.usuario_service import obter_ou_criar_usuario_sistema
from etl.arquivos import FluxoArquivos
from etl.motor import MotorImportacao
from tests.etl.fixtures_reais import xlsx_base_clientes, xlsx_sb_supervisor
from tests.etl.fixtures_xlsx import xlsx_clientes


@pytest.fixture(autouse=True)
def _api_usa_fluxo_do_teste(fluxo: FluxoArquivos) -> Generator[None, None, None]:
    """A API passa a usar o mesmo diretório de arquivos do teste corrente."""

    def _override(db: Session = Depends(get_db_session)) -> ImportacaoService:
        motor = MotorImportacao(session=db, fluxo=fluxo)
        return ImportacaoService(repository=ImportacaoRepository(db), motor=motor)

    fastapi_app.dependency_overrides[get_importacao_service] = _override
    yield
    fastapi_app.dependency_overrides.pop(get_importacao_service, None)


def _importar_arquivo_valido(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario: Usuario, nome: str = "clientes.xlsx"
) -> Importacao:
    return motor.importar(xlsx_clientes(fluxo, nome), TipoArquivoImportacao.CLIENTES, usuario.id)


def _criar_pendente(sessao: Session, usuario: Usuario) -> Importacao:
    pendente = Importacao(
        tipo_arquivo=TipoArquivoImportacao.CLIENTES,
        nome_arquivo_original="pendente.xlsx",
        hash_sha256="f" * 64,
        tamanho_bytes=100,
        usuario_id=usuario.id,
        status=StatusImportacao.PENDENTE,
    )
    sessao.add(pendente)
    sessao.commit()
    return pendente


def test_listar_importacoes_paginado_e_filtravel(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    _importar_arquivo_valido(motor, fluxo, usuario_admin)

    resposta = client.get("/api/v1/importacoes", params={"tipo_arquivo": "CLIENTES"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_itens"] == 1
    assert corpo["itens"][0]["status"] == "CONCLUIDA"
    assert corpo["itens"][0]["versao"] == 1

    vazia = client.get("/api/v1/importacoes", params={"tipo_arquivo": "FATURAMENTO"})
    assert vazia.json()["total_itens"] == 0


def test_consultar_detalhe_e_historico_de_erros(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    linhas_mistas = [
        ["C001", "Válido", None, None, "SP", "Campinas", None, None],
        ["C002", "UF Errada", None, None, "XX", "Cidade", None, None],
    ]
    importacao = motor.importar(
        xlsx_clientes(fluxo, linhas=linhas_mistas),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )

    detalhe = client.get(f"/api/v1/importacoes/{importacao.id}")
    assert detalhe.status_code == 200
    assert detalhe.json()["status"] == "CONCLUIDA_COM_ERROS"
    assert detalhe.json()["linhas_invalidas"] == 1

    erros = client.get(f"/api/v1/importacoes/{importacao.id}/erros")
    assert erros.status_code == 200
    assert erros.json()["total_itens"] == 1
    assert "UF inválida" in erros.json()["itens"][0]["mensagem_erro"]


def test_consultar_importacao_inexistente_retorna_404_padrao(client: TestClient) -> None:
    resposta = client.get("/api/v1/importacoes/99999")

    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_consultar_versoes_e_arquivo(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    v1 = _importar_arquivo_valido(motor, fluxo, usuario_admin, "v1.xlsx")
    linhas_v2 = [["C010", "Outro Cliente", None, None, "SP", "Sorocaba", None, None]]
    v2 = motor.importar(
        xlsx_clientes(fluxo, "v2.xlsx", linhas=linhas_v2),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )

    versoes = client.get(f"/api/v1/importacoes/{v2.id}/versoes")
    assert versoes.status_code == 200
    cadeia = versoes.json()
    assert [item["versao"] for item in cadeia] == [1, 2]
    assert cadeia[1]["importacao_pai_id"] == v1.id

    arquivo = client.get(f"/api/v1/importacoes/{v1.id}/arquivo")
    assert arquivo.status_code == 200
    assert arquivo.json()["caminho_armazenamento"].startswith("archive/")


def test_reprocessar_importacao_concluida_e_recusado_como_duplicado(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    """Reprocessar arquivo idêntico já concluído cai no controle de duplicidade."""

    importacao = _importar_arquivo_valido(motor, fluxo, usuario_admin)

    resposta = client.post(f"/api/v1/importacoes/{importacao.id}/reprocessar")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "FALHOU"
    assert corpo["versao"] == 0  # tentativa recusada, fora da cadeia


def test_excluir_importacao_pendente(
    client: TestClient, sessao: Session, usuario_admin: Usuario
) -> None:
    pendente = _criar_pendente(sessao, usuario_admin)

    resposta = client.delete(f"/api/v1/importacoes/{pendente.id}")

    assert resposta.status_code == 204
    assert client.get(f"/api/v1/importacoes/{pendente.id}").status_code == 404


def test_excluir_importacao_nao_pendente_e_rejeitado(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    concluida = _importar_arquivo_valido(motor, fluxo, usuario_admin)

    resposta = client.delete(f"/api/v1/importacoes/{concluida.id}")

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "VALIDACAO_FALHOU"
    assert client.get(f"/api/v1/importacoes/{concluida.id}").status_code == 200


def _postar_upload(
    client: TestClient, caminho: Path, **campos_de_formulario: str
) -> httpx.Response:
    with caminho.open("rb") as arquivo:
        return client.post(
            "/api/v1/importacoes/upload",
            files={"arquivo": (caminho.name, arquivo, "application/vnd.ms-excel")},
            data=campos_de_formulario,
        )


def test_upload_reconhece_estrutura_e_importa_sem_selecao_manual_de_tipo(
    client: TestClient, fluxo: FluxoArquivos, ufs: None
) -> None:
    """Sprint 6: upload Web infere o tipo pela estrutura, igual à CLI — sem
    exigir que o usuário escolha o tipo do arquivo."""

    arquivo = xlsx_base_clientes(fluxo)

    resposta = _postar_upload(client, arquivo)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["tipo_arquivo"] == "CLIENTES"
    assert corpo["status"] == "CONCLUIDA"
    assert corpo["versao"] == 1
    assert corpo["usuario_nome"]  # resolvido via join, nunca vazio
    assert corpo["duracao_segundos"] is not None  # tempo de processamento (Tela de Importações)


def test_upload_arquivo_com_estrutura_nao_reconhecida_e_recusado_sem_criar_historico(
    client: TestClient, fluxo: FluxoArquivos
) -> None:
    arquivo = fluxo.incoming / "desconhecido.xlsx"
    arquivo.write_bytes(b"nao e um xlsx valido")

    resposta = _postar_upload(client, arquivo)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "VALIDACAO_FALHOU"
    assert client.get("/api/v1/importacoes").json()["total_itens"] == 0


def test_upload_do_mesmo_arquivo_duas_vezes_e_recusado_como_duplicado(
    client: TestClient, fluxo: FluxoArquivos, ufs: None
) -> None:
    arquivo = xlsx_base_clientes(fluxo)
    conteudo = arquivo.read_bytes()

    primeira = client.post(
        "/api/v1/importacoes/upload",
        files={"arquivo": ("clientes.xlsx", conteudo, "application/vnd.ms-excel")},
    )
    segunda = client.post(
        "/api/v1/importacoes/upload",
        files={"arquivo": ("clientes_copia.xlsx", conteudo, "application/vnd.ms-excel")},
    )

    assert primeira.status_code == 201
    assert primeira.json()["status"] == "CONCLUIDA"
    assert segunda.status_code == 201
    corpo_segunda = segunda.json()
    assert corpo_segunda["status"] == "FALHOU"
    assert corpo_segunda["versao"] == 0


def test_upload_repassa_competencia_informada(
    client: TestClient, fluxo: FluxoArquivos, ufs: None
) -> None:
    arquivo = xlsx_sb_supervisor(fluxo)

    resposta = _postar_upload(client, arquivo, ano_competencia="2026", mes_competencia="3")

    assert resposta.status_code == 201
    assert resposta.json()["competencia"] == "2026-03-01"


def test_cancelar_importacao_pendente(
    client: TestClient, sessao: Session, usuario_admin: Usuario
) -> None:
    pendente = _criar_pendente(sessao, usuario_admin)

    resposta = client.post(f"/api/v1/importacoes/{pendente.id}/cancelar")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "FALHOU"
    assert corpo["versao"] == 0

    erros = client.get(f"/api/v1/importacoes/{pendente.id}/erros")
    assert "cancelada" in erros.json()["itens"][0]["mensagem_erro"].lower()


def test_cancelar_importacao_nao_pendente_e_rejeitado(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    concluida = _importar_arquivo_valido(motor, fluxo, usuario_admin)

    resposta = client.post(f"/api/v1/importacoes/{concluida.id}/cancelar")

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "VALIDACAO_FALHOU"


def test_baixar_relatorio_de_erros_em_csv(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    linhas_mistas = [
        ["C001", "Válido", None, None, "SP", "Campinas", None, None],
        ["C002", "UF Errada", None, None, "XX", "Cidade", None, None],
    ]
    importacao = motor.importar(
        xlsx_clientes(fluxo, linhas=linhas_mistas), TipoArquivoImportacao.CLIENTES, usuario_admin.id
    )

    resposta = client.get(f"/api/v1/importacoes/{importacao.id}/erros/relatorio")

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/csv")
    assert "attachment" in resposta.headers["content-disposition"]
    corpo = resposta.content.decode("utf-8-sig")
    assert "UF inválida" in corpo
    assert corpo.count("\r\n") >= 2  # cabeçalho + 1 linha de erro


def test_listar_e_obter_importacao_incluem_usuario_nome(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    importacao = _importar_arquivo_valido(motor, fluxo, usuario_admin)

    listagem = client.get("/api/v1/importacoes")
    detalhe = client.get(f"/api/v1/importacoes/{importacao.id}")

    assert listagem.json()["itens"][0]["usuario_nome"] == usuario_admin.nome
    assert detalhe.json()["usuario_nome"] == usuario_admin.nome


def test_reprocessar_retem_usuario_nome_do_original(
    client: TestClient,
    motor: MotorImportacao,
    fluxo: FluxoArquivos,
    usuario_admin: Usuario,
    ufs: None,
) -> None:
    importacao = _importar_arquivo_valido(motor, fluxo, usuario_admin)

    resposta = client.post(f"/api/v1/importacoes/{importacao.id}/reprocessar")

    assert resposta.json()["usuario_nome"] == usuario_admin.nome


def test_upload_usa_usuario_de_sistema_compartilhado_com_a_cli(
    client: TestClient, sessao: Session, fluxo: FluxoArquivos, ufs: None
) -> None:
    """Sem autenticação nesta fase: upload Web e CLI registram sob o
    mesmo usuário de sistema (`app/services/usuario_service.py`)."""

    arquivo = xlsx_base_clientes(fluxo)

    resposta = _postar_upload(client, arquivo)

    usuario_sistema = obter_ou_criar_usuario_sistema(sessao)
    assert resposta.json()["usuario_nome"] == usuario_sistema.nome
