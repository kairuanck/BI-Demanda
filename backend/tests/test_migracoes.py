"""Teste do ciclo completo de migrações Alembic (TESTES.md; DATABASE.md, seção 4)."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command

ALEMBIC_INI_PATH = Path(__file__).resolve().parents[1] / "alembic.ini"


def test_upgrade_e_downgrade_completos_em_banco_isolado(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path}/migracao_teste.db"
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option("sqlalchemy.url", url)

    command.upgrade(alembic_cfg, "head")
    engine = create_engine(url)
    tabelas = set(inspect(engine).get_table_names())
    assert "importacoes" in tabelas
    assert "empresas" in tabelas
    assert len(tabelas) >= 21  # 20 de negócio + alembic_version

    command.downgrade(alembic_cfg, "base")
    tabelas_apos_downgrade = set(inspect(engine).get_table_names())
    assert tabelas_apos_downgrade <= {"alembic_version"}

    command.upgrade(alembic_cfg, "head")
    assert "empresas" in set(inspect(engine).get_table_names())
    engine.dispose()
