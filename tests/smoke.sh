#!/usr/bin/env bash
# Verificação manual rápida de que backend e frontend estão de pé
# (uso: após `docker compose up`, ou com os dois `npm run dev`/`uvicorn`
# locais rodando). Não faz parte da suíte automatizada (ver tests/README.md).
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5173}"

echo "Verificando backend em ${BACKEND_URL}/api/v1/health ..."
curl -fsS "${BACKEND_URL}/api/v1/health"
echo

echo "Verificando frontend em ${FRONTEND_URL} ..."
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" "${FRONTEND_URL}"

echo "OK: backend e frontend responderam."
