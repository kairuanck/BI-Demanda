#!/usr/bin/env bash
# Único comando para colocar o Promotores BI no ar (backend + frontend + banco).
# Uso: ./iniciar.sh   (ver PRIMEIRO_USO.md para o passo a passo completo).
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

azul() { printf "\033[1;34m%s\033[0m\n" "$1"; }
verde() { printf "\033[1;32m%s\033[0m\n" "$1"; }
vermelho() { printf "\033[1;31m%s\033[0m\n" "$1"; }

azul "==> Verificando se o Docker está instalado..."
if ! command -v docker >/dev/null 2>&1; then
  vermelho "O Docker não foi encontrado neste computador."
  echo "Instale o Docker Desktop (gratuito) em https://www.docker.com/products/docker-desktop/"
  echo "e execute este comando novamente depois de instalar."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  vermelho "O Docker foi encontrado, mas o 'docker compose' não está disponível."
  echo "Atualize o Docker Desktop para uma versão recente e tente novamente."
  exit 1
fi

azul "==> Verificando se o Docker está em execução..."
if ! docker info >/dev/null 2>&1; then
  vermelho "O Docker está instalado, mas não está em execução."
  echo "Abra o aplicativo Docker Desktop, espere o ícone parar de animar e rode ./iniciar.sh de novo."
  exit 1
fi

azul "==> Construindo e iniciando backend, frontend e banco de dados..."
echo "    (na primeira vez isso pode levar alguns minutos — as próximas serão bem mais rápidas)"
if ! docker compose up --build -d; then
  vermelho "Não foi possível iniciar a aplicação."
  echo "Últimas linhas de log, para diagnóstico:"
  docker compose logs --tail=50
  exit 1
fi

azul "==> Aguardando o backend ficar pronto..."
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
  docker compose logs --tail=80 backend
  exit 1
fi

echo
verde "✔ Promotores BI está no ar!"
echo
echo "  Acesse no navegador: http://localhost:5173"
echo
echo "  Para importar planilhas, entre no menu 'Importações'."
echo "  Para encerrar a aplicação, rode: ./parar.sh"
echo
echo "  Guia completo para quem nunca usou o sistema: PRIMEIRO_USO.md"
