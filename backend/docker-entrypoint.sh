#!/bin/sh
# Aplica as migrações Alembic, garante os dados de referência (UFs e tipos
# de promotor) e sobe o servidor (DEPLOY.md, seção 8).
#
# Os seeds são idempotentes (não alteram registros já existentes) e por
# isso rodam em toda inicialização, não só na primeira — garante que um
# banco novo (`database/app.db` inexistente) já nasça utilizável, sem
# depender de um passo manual separado.
set -e

alembic upgrade head
python -m app.infrastructure.seeds.seed_ufs
python -m app.infrastructure.seeds.seed_tipos_promotor
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
