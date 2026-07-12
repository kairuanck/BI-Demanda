"""Fixtures de teste (ver TESTES.md, seção 3).

Cria um banco SQLite efêmero por sessão de teste, aplica todas as
migrações Alembic antes da suíte e limpa os dados entre testes.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

_TMP_DIR = tempfile.mkdtemp(prefix="promotores_bi_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["STORAGE_DIR"] = f"{_TMP_DIR}/imports"

from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from alembic import command  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.domain.enums import PerfilUsuario  # noqa: E402
from app.infrastructure.database import Base, SessionLocal, engine  # noqa: E402
from app.infrastructure.models import Usuario  # noqa: E402
from app.infrastructure.seeds.seed_tipos_promotor import (  # noqa: E402
    executar_seed_tipos_promotor,
)
from app.infrastructure.seeds.seed_ufs import executar_seed_ufs  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from etl.arquivos import FluxoArquivos  # noqa: E402
from etl.motor import MotorImportacao  # noqa: E402

ALEMBIC_INI_PATH = Path(__file__).resolve().parents[1] / "alembic.ini"


@pytest.fixture(scope="session", autouse=True)
def _aplicar_migracoes() -> Generator[None, None, None]:
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option("sqlalchemy.url", get_settings().database_url)
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture(autouse=True)
def _limpar_banco() -> Generator[None, None, None]:
    """Isola os testes: apaga todos os dados e restaura seeds de migração.

    A limpeza remove também o seed cadastral de `tipos_promotor` aplicado
    pela migração da Sprint 3; ele é reaplicado para que cada teste veja o
    banco como uma migração recém-executada.
    """

    _garantir_seed_tipos_promotor()
    yield
    with engine.begin() as conexao:
        for tabela in reversed(Base.metadata.sorted_tables):
            conexao.execute(tabela.delete())
    _garantir_seed_tipos_promotor()


def _garantir_seed_tipos_promotor() -> None:
    sessao_seed = SessionLocal()
    try:
        executar_seed_tipos_promotor(sessao_seed)
    finally:
        sessao_seed.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture()
def sessao() -> Generator[Session, None, None]:
    sessao_db = SessionLocal()
    try:
        yield sessao_db
    finally:
        sessao_db.close()


@pytest.fixture()
def usuario_admin(sessao: Session) -> Usuario:
    usuario = Usuario(
        nome="Admin de Teste",
        email="admin.teste@promotoresbi.local",
        senha_hash="$2b$12$hash-ficticio-para-testes-sem-autenticacao",
        perfil=PerfilUsuario.ADMINISTRADOR,
    )
    sessao.add(usuario)
    sessao.commit()
    return usuario


@pytest.fixture()
def ufs(sessao: Session) -> None:
    executar_seed_ufs(sessao)


@pytest.fixture()
def fluxo(tmp_path: Path) -> FluxoArquivos:
    return FluxoArquivos(tmp_path / "imports")


@pytest.fixture()
def motor(sessao: Session, fluxo: FluxoArquivos) -> MotorImportacao:
    return MotorImportacao(session=sessao, fluxo=fluxo)
