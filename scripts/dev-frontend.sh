#!/usr/bin/env bash
# Sobe o frontend em modo desenvolvimento.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/frontend"
npm run dev
