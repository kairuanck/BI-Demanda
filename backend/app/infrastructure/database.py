"""Conexão de banco de dados (ver DATABASE.md).

Compatível com SQLite (POC) e PostgreSQL (produção) via `DATABASE_URL`.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Classe declarativa base de todos os modelos SQLAlchemy."""


def normalizar_para_busca(texto: str | None) -> str | None:
    """Minúsculas + sem acento, para busca textual (Sprint 5).

    O `LOWER()` nativo do SQLite não faz *case-folding* de caracteres
    acentuados — mesma limitação encontrada para nomes de promotor na
    Sprint 3 (docs/DECISIONS.md, seção 15.3). Registrada como função SQL
    (`norm_busca`) só para SQLite: o `ILIKE` do PostgreSQL já resolve isso
    nativamente na produção.
    """

    if texto is None:
        return None
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()


def _criar_engine() -> Engine:
    settings = get_settings()
    connect_args: dict[str, object] = {}

    is_sqlite = settings.database_url.startswith("sqlite")
    if is_sqlite:
        connect_args["check_same_thread"] = False
        # Sem isso, o driver sqlite3 desiste depois de 5s esperando um lock
        # liberar (padrão do Python) — pouco tempo para uma importação grande
        # (milhares de linhas) segurando o banco enquanto o Dashboard tenta
        # ler ao mesmo tempo, o que gera "database is locked" mesmo em uso
        # normal, não só sob carga pesada.
        connect_args["timeout"] = 30
        # Garante que o diretório do arquivo SQLite exista (ex.: database/).
        db_path = settings.database_url.split("sqlite:///")[-1]
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

    if is_sqlite:
        # DATABASE.md, seção 3, item 7: integridade referencial no SQLite.
        # journal_mode=WAL: no modo padrão (rollback journal), uma escrita
        # (ex.: uma importação gravando milhares de linhas) bloqueia toda
        # leitura concorrente (ex.: o Dashboard) até terminar — em WAL,
        # leituras não esperam por escritas em andamento, o que é o cenário
        # normal de uso desta aplicação (importar e consultar ao mesmo tempo).
        @event.listens_for(engine, "connect")
        def _habilitar_foreign_keys(dbapi_connection: object, _connection_record: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        @event.listens_for(engine, "connect")
        def _registrar_norm_busca(dbapi_connection: object, _connection_record: object) -> None:
            dbapi_connection.create_function(  # type: ignore[attr-defined]
                "norm_busca", 1, normalizar_para_busca
            )

    return engine


engine: Engine = _criar_engine()
SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Dependência FastAPI: sessão de banco com escopo de uma requisição."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
