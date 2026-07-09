#!/bin/sh
# Aplica as migrações Alembic e sobe o servidor (DEPLOY.md, seção 8).
set -e

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
