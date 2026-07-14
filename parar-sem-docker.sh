#!/usr/bin/env bash
# Encerra o backend e o frontend iniciados por ./iniciar-sem-docker.sh.
# Os dados continuam salvos em database/ e imports/ — nada é apagado.
# Uso: ./parar-sem-docker.sh
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"

parar() {
  nome="$1"
  arquivo_pid="$RUN_DIR/$2"
  if [ -f "$arquivo_pid" ]; then
    pid="$(cat "$arquivo_pid")"
    # Mata também eventuais processos-filho (ex.: se o processo principal
    # tiver iniciado outro por baixo) — sem isso, o servidor pode continuar
    # ocupando a porta mesmo após "encerrar" o processo pai.
    pkill -P "$pid" >/dev/null 2>&1
    if kill "$pid" >/dev/null 2>&1; then
      echo "==> $nome encerrado (pid $pid)."
    else
      echo "==> $nome já não estava em execução."
    fi
    rm -f "$arquivo_pid"
  else
    echo "==> $nome não estava em execução (nenhum processo iniciado por ./iniciar-sem-docker.sh encontrado)."
  fi
}

parar "Backend" "backend.pid"
parar "Frontend" "frontend.pid"

echo
echo "✔ Aplicação encerrada. Seus dados continuam salvos em database/ e imports/."
echo "  Para iniciar de novo, rode: ./iniciar-sem-docker.sh"
