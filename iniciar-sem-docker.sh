#!/usr/bin/env bash
# Alternativa a ./iniciar.sh para quem não consegue instalar/rodar o Docker.
# Sobe backend e frontend diretamente na máquina (sem containers), com um
# único comando. Exige Python 3.12 e Node.js 20+ já instalados.
# Uso: ./iniciar-sem-docker.sh   (ver PRIMEIRO_USO.md).
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
RUN_DIR="$ROOT_DIR/.run"
mkdir -p "$RUN_DIR"

azul() { printf "\033[1;34m%s\033[0m\n" "$1"; }
verde() { printf "\033[1;32m%s\033[0m\n" "$1"; }
vermelho() { printf "\033[1;31m%s\033[0m\n" "$1"; }

# ------------------------------------------------------------------ checagens

azul "==> Verificando se o Python está instalado..."
PYTHON_BIN=""
for candidato in python3.12 python3 python; do
  if command -v "$candidato" >/dev/null 2>&1; then
    # Aceita 3.12 ou mais novo (o projeto não tem limite superior: pyproject.toml
    # declara "requires-python = >=3.12") — versões futuras do Python (3.13, 3.14...)
    # não devem ser recusadas só por não serem exatamente "3.12".
    versao_ok="$("$candidato" -c 'import sys; print(1 if sys.version_info[:2] >= (3, 12) else 0)' 2>/dev/null)"
    if [ "$versao_ok" = "1" ]; then
      PYTHON_BIN="$candidato"
      break
    fi
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  vermelho "Não encontrei o Python 3.12 (ou mais novo) instalado."
  echo "Baixe em https://www.python.org/downloads/ (escolha a versão 3.12 ou mais recente)."
  echo "Windows: marque a caixa 'Add python.exe to PATH' durante a instalação — é o erro mais comum."
  exit 1
fi

azul "==> Verificando se o Node.js está instalado..."
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  vermelho "Não encontrei o Node.js instalado."
  echo "Baixe em https://nodejs.org/ (escolha a versão 'LTS')."
  exit 1
fi

# ------------------------------------------------------------------ backend

azul "==> Preparando o backend (pode levar alguns minutos na primeira vez)..."
cd "$ROOT_DIR/backend"
if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip -q
pip install -e ".[dev]" -q
[ -f .env ] || cp .env.example .env

azul "==> Aplicando migrações e dados de referência..."
alembic upgrade head
python -m app.infrastructure.seeds.seed_ufs
python -m app.infrastructure.seeds.seed_tipos_promotor

azul "==> Iniciando o backend em segundo plano..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$RUN_DIR/backend.log" 2>&1 &
echo $! > "$RUN_DIR/backend.pid"
deactivate

BACKEND_OK=0
for _ in $(seq 1 60); do
  if curl -sf http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    BACKEND_OK=1
    break
  fi
  sleep 2
done
if [ "$BACKEND_OK" -ne 1 ]; then
  vermelho "O backend demorou demais para responder."
  echo "Últimas linhas de log, para diagnóstico:"
  tail -n 50 "$RUN_DIR/backend.log"
  exit 1
fi

# ------------------------------------------------------------------ frontend

azul "==> Preparando o frontend (pode levar alguns minutos na primeira vez)..."
cd "$ROOT_DIR/frontend"
[ -f .env ] || cp .env.example .env
if [ ! -d node_modules ]; then
  npm install
fi

azul "==> Iniciando o frontend em segundo plano..."
# Chama o binário do vite diretamente (não "npm run dev"): "npm run" cria um
# processo intermediário cujo PID não corresponde ao processo real do
# servidor — matar só o PID do npm deixaria o vite órfão, ainda ocupando a
# porta 5173 depois de ./parar-sem-docker.sh.
nohup ./node_modules/.bin/vite --host 0.0.0.0 --port 5173 > "$RUN_DIR/frontend.log" 2>&1 &
echo $! > "$RUN_DIR/frontend.pid"

FRONTEND_OK=0
for _ in $(seq 1 30); do
  if curl -sf http://localhost:5173 >/dev/null 2>&1; then
    FRONTEND_OK=1
    break
  fi
  sleep 2
done
if [ "$FRONTEND_OK" -ne 1 ]; then
  vermelho "O frontend demorou demais para responder."
  echo "Últimas linhas de log, para diagnóstico:"
  tail -n 50 "$RUN_DIR/frontend.log"
  exit 1
fi

echo
verde "✔ Promotores BI está no ar (sem Docker)!"
echo
echo "  Acesse no navegador: http://localhost:5173"
echo
echo "  Para importar planilhas, entre no menu 'Importações'."
echo "  Para encerrar a aplicação, rode: ./parar-sem-docker.sh"
echo
echo "  Guia completo para quem nunca usou o sistema: PRIMEIRO_USO.md"
