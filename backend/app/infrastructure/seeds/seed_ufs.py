"""Seed das 27 UFs brasileiras (SPRINT_01.md, seção 4.6).

Execução: `python -m app.infrastructure.seeds.seed_ufs`
Idempotente: UFs já existentes não são alteradas.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Uf

UFS_BRASIL: list[tuple[str, str, str]] = [
    ("AC", "Acre", "Norte"),
    ("AL", "Alagoas", "Nordeste"),
    ("AP", "Amapá", "Norte"),
    ("AM", "Amazonas", "Norte"),
    ("BA", "Bahia", "Nordeste"),
    ("CE", "Ceará", "Nordeste"),
    ("DF", "Distrito Federal", "Centro-Oeste"),
    ("ES", "Espírito Santo", "Sudeste"),
    ("GO", "Goiás", "Centro-Oeste"),
    ("MA", "Maranhão", "Nordeste"),
    ("MT", "Mato Grosso", "Centro-Oeste"),
    ("MS", "Mato Grosso do Sul", "Centro-Oeste"),
    ("MG", "Minas Gerais", "Sudeste"),
    ("PA", "Pará", "Norte"),
    ("PB", "Paraíba", "Nordeste"),
    ("PR", "Paraná", "Sul"),
    ("PE", "Pernambuco", "Nordeste"),
    ("PI", "Piauí", "Nordeste"),
    ("RJ", "Rio de Janeiro", "Sudeste"),
    ("RN", "Rio Grande do Norte", "Nordeste"),
    ("RS", "Rio Grande do Sul", "Sul"),
    ("RO", "Rondônia", "Norte"),
    ("RR", "Roraima", "Norte"),
    ("SC", "Santa Catarina", "Sul"),
    ("SP", "São Paulo", "Sudeste"),
    ("SE", "Sergipe", "Nordeste"),
    ("TO", "Tocantins", "Norte"),
]


def executar_seed_ufs(session: Session) -> int:
    """Insere as UFs ausentes; retorna a quantidade inserida."""

    existentes = set(session.scalars(select(Uf.sigla)).all())
    inseridas = 0
    for sigla, nome, regiao in UFS_BRASIL:
        if sigla not in existentes:
            session.add(Uf(sigla=sigla, nome=nome, regiao=regiao))
            inseridas += 1
    session.commit()
    return inseridas


def main() -> None:
    session = SessionLocal()
    try:
        inseridas = executar_seed_ufs(session)
        print(f"Seed de UFs concluído: {inseridas} inseridas, {27 - inseridas} já existentes.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
