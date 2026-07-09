# SPRINT_00.md — Fundação do Projeto

## 1. Objetivo

Estabelecer a estrutura inicial do repositório, o esqueleto do backend (FastAPI) e do frontend (React/Vite/Tailwind), o tooling de qualidade (lint, formatação, checagem de tipos) e o pipeline básico de CI, sem ainda implementar nenhuma funcionalidade de negócio.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `BACKEND.md`, `FRONTEND.md`, `GITHUB.md`, `DEPLOY.md`.

## 3. Pré-condições

Nenhuma — esta é a primeira Sprint de implementação, executada sobre o repositório já contendo toda a documentação (`SPEC_INDEX.md`).

## 4. Escopo (Backlog Detalhado)

### 4.1 Estrutura de Repositório
1. Criar a estrutura de diretórios `backend/` conforme `BACKEND.md`, seção 4 (pastas vazias com arquivos `__init__.py` onde aplicável).
2. Criar a estrutura de diretórios `frontend/` conforme `FRONTEND.md`, seção 3 (scaffold inicial via `npm create vite@latest -- --template react`).
3. Criar `.gitignore` na raiz conforme `GITHUB.md`, seção 8.
4. Criar `.github/PULL_REQUEST_TEMPLATE.md` conforme `GITHUB.md`, seção 4.
5. Criar `.github/workflows/ci.yml` com as etapas aplicáveis à Sprint 00 (`GITHUB.md`, seção 6: lint Python, formatação, mypy, pytest — mesmo com suíte inicialmente vazia/mínima).

### 4.2 Backend — Esqueleto
1. Configurar `pyproject.toml` com as dependências listadas em `DEPLOY.md`, seção 5.
2. Implementar `app/main.py` com instância FastAPI mínima, incluindo o endpoint `GET /api/v1/health` (`DEPLOY.md`, seção 11).
3. Implementar `app/core/config.py` com leitura de variáveis de ambiente via Pydantic Settings, conforme `DEPLOY.md`, seções 3–4.
4. Implementar `app/core/logging.py` com configuração inicial do logging técnico estruturado (`LOGS.md`, seções 3–4), aplicado ao menos ao middleware de requisição.
5. Implementar `app/api/middlewares/logging_middleware.py` (`LOGS.md`, seção 5, item 1).
6. Criar `backend/.env.example` com todas as variáveis de `DEPLOY.md`, seções 3–4 (apenas nomes/exemplos, sem segredos reais).
7. Configurar `ruff`, `black` e `mypy` com arquivos de configuração no `pyproject.toml`.

### 4.3 Frontend — Esqueleto
1. Inicializar o projeto Vite + React conforme `FRONTEND.md`, seção 3.
2. Instalar e configurar TailwindCSS (`tailwind.config.js`, `postcss.config.js`, diretivas em `src/styles/index.css`) conforme tokens de `DESIGN_SYSTEM.md`, seção 3–4 (tokens registrados como extensão do tema Tailwind).
3. Criar `frontend/.env.example` com `VITE_API_BASE_URL` (`DEPLOY.md`, seção 4).
4. Implementar uma página inicial mínima (`App.jsx`) que consulta `GET /api/v1/health` do backend e exibe o status, validando a comunicação entre frontend e backend do zero.
5. Configurar ESLint com regras compatíveis com React/JSX.

### 4.4 Documentação Operacional Mínima
1. Adicionar ao `README.md` (já existente) uma seção "Como Executar Localmente" com os comandos básicos de subida de backend e frontend, referenciando `DEPLOY.md`.

## 5. Fora de Escopo desta Sprint

1. Qualquer modelo de dados (`domain/entidades`, `infrastructure/models`) — Sprint 01.
2. Qualquer autenticação — Sprint 02.
3. Qualquer importador — Sprint 03 em diante.
4. Qualquer tela de negócio além da página de verificação de saúde — Sprint 09 em diante.

## 6. Entregáveis

1. Repositório com estrutura de pastas de `backend/` e `frontend/` completa (vazia onde ainda não há código de negócio).
2. Backend executável localmente, respondendo `GET /api/v1/health` com `200`.
3. Frontend executável localmente, exibindo o status de saúde do backend.
4. Pipeline de CI configurado e verde.
5. Tooling de qualidade (lint, formatação, tipos) configurado e sem erros sobre o código existente.

## 7. Critérios de Aceite

1. `uvicorn app.main:app --reload` sobe sem erros e `GET /api/v1/health` retorna `{"status": "ok", "database": "ok"}` com código `200`.
2. `npm run dev` sobe o frontend sem erros e a página inicial exibe o status retornado pelo backend.
3. `ruff check .`, `black --check .` e `mypy .` executam sem erro sobre o código do backend.
4. `npm run lint` executa sem erro sobre o código do frontend.
5. O workflow de CI (`.github/workflows/ci.yml`) executa com sucesso em um Pull Request de teste.
6. Estrutura de diretórios corresponde exatamente à descrita em `BACKEND.md`, seção 4, e `FRONTEND.md`, seção 3.

## 8. Riscos e Observações

1. Esta Sprint não possui banco de dados configurado ainda — o campo `"database": "ok"` do endpoint de saúde pode, nesta Sprint, refletir apenas a ausência de erro de inicialização da configuração de conexão (a verificação efetiva de conectividade com banco real passa a ser significativa a partir da Sprint 01, quando `infrastructure/database.py` é implementado com um `Engine` real).
