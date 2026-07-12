"""Seed cadastral dos tipos de promotor (Sprint 3, docs/DECISIONS.md, seção 13).

Execução: `python -m app.infrastructure.seeds.seed_tipos_promotor`
Idempotente: tipos já existentes não são alterados. A migração da Sprint 3
aplica o mesmo seed; este módulo permite restaurá-lo (ex.: testes, novos
ambientes).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TipoPromotor
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import TipoPromotorCadastro

TIPOS_PROMOTOR: list[tuple[str, str]] = [
    (TipoPromotor.TECNICO.value, "Promotor Técnico"),
    (TipoPromotor.TRADE.value, "Promotor Trade"),
]


def executar_seed_tipos_promotor(session: Session) -> int:
    """Insere os tipos ausentes; retorna quantos foram criados."""

    existentes = set(session.scalars(select(TipoPromotorCadastro.codigo)))
    criados = 0
    for codigo, nome in TIPOS_PROMOTOR:
        if codigo not in existentes:
            session.add(TipoPromotorCadastro(codigo=codigo, nome=nome))
            criados += 1
    session.commit()
    return criados


def main() -> None:
    session = SessionLocal()
    try:
        criados = executar_seed_tipos_promotor(session)
        print(f"Seed de tipos de promotor concluído: {criados} criado(s).")
    finally:
        session.close()


if __name__ == "__main__":
    main()
