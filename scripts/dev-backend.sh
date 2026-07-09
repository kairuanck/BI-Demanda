#!/usr/bin/env bash
# Sobe o backend em modo desenvolvimento (reload automático).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"
# shellcheck source=/dev/null
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
