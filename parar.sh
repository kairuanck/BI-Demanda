#!/usr/bin/env bash
# Encerra o Promotores BI (backend + frontend). Os dados continuam salvos
# nas pastas database/ e imports/ — nada é apagado.
# Uso: ./parar.sh
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "==> Encerrando o Promotores BI..."
docker compose down

echo
echo "✔ Aplicação encerrada. Seus dados continuam salvos em database/ e imports/."
echo "  Para iniciar de novo, rode: ./iniciar.sh"
