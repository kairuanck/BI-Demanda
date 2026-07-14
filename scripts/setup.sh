#!/usr/bin/env bash
# Bootstrap completo do ambiente de desenvolvimento local (sem Docker).
# Ver TUTORIAL.md e README.md para o passo a passo detalhado.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Backend: criando ambiente virtual e instalando dependências..."
cd "$ROOT_DIR/backend"
python3.12 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
[ -f .env ] || cp .env.example .env

echo "==> Backend: aplicando migrações..."
alembic upgrade head

echo "==> Backend: aplicando dados de referência (UFs e tipos de promotor)..."
python -m app.infrastructure.seeds.seed_ufs
python -m app.infrastructure.seeds.seed_tipos_promotor

echo "==> Frontend: instalando dependências..."
cd "$ROOT_DIR/frontend"
npm install
[ -f .env ] || cp .env.example .env

echo "==> Pronto. Use scripts/dev-backend.sh e scripts/dev-frontend.sh para subir cada serviço."
