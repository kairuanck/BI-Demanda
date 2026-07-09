# DEPLOY.md — Guia de Implantação

## 1. Finalidade

Este documento especifica como executar o Promotores BI localmente (ambiente de desenvolvimento da POC) e como publicá-lo em um ambiente acessível (ambiente de demonstração/produção da POC), incluindo o caminho de evolução de SQLite para PostgreSQL. O passo a passo operacional detalhado, com comandos, está em `TUTORIAL.md`.

## 2. Ambientes

| Ambiente | Backend | Frontend | Banco |
|---|---|---|---|
| Desenvolvimento local | `uvicorn` com reload | `vite dev` | SQLite local |
| Demonstração/POC publicada | `uvicorn`/`gunicorn` atrás de proxy reverso | build estático (`vite build`) servido por CDN/hosting estático | SQLite (arquivo persistente) ou PostgreSQL gerenciado |
| Produção (pós-POC) | `gunicorn` com workers `uvicorn`, contêiner | build estático | PostgreSQL gerenciado |

## 3. Variáveis de Ambiente — Backend

| Variável | Obrigatória | Descrição | Valor padrão (dev) |
|---|---|---|---|
| `DATABASE_URL` | Não | String de conexão SQLAlchemy | `sqlite:///./promotores_bi.db` |
| `JWT_SECRET_KEY` | Sim | Chave de assinatura do access token | — (deve ser gerada, nunca commitada) |
| `JWT_REFRESH_SECRET_KEY` | Sim | Chave de assinatura do refresh token | — (deve ser gerada, nunca commitada) |
| `JWT_ACCESS_EXPIRE_MINUTES` | Não | Tempo de vida do access token | `30` |
| `JWT_REFRESH_EXPIRE_DAYS` | Não | Tempo de vida do refresh token | `7` |
| `CORS_ALLOWED_ORIGINS` | Não | Origens permitidas para o frontend | `http://localhost:5173` |
| `STORAGE_DIR` | Não | Diretório de armazenamento de arquivos importados (`importacao_arquivos`) | `./storage/importacoes` |
| `LOG_LEVEL` | Não | Nível mínimo de log técnico (`LOGS.md`) | `INFO` |
| `ENVIRONMENT` | Não | `development` / `production`, controla nível de detalhamento de erro exposto na resposta HTTP | `development` |

## 4. Variáveis de Ambiente — Frontend

| Variável | Obrigatória | Descrição | Valor padrão (dev) |
|---|---|---|---|
| `VITE_API_BASE_URL` | Sim | URL base da API consumida pelo frontend | `http://localhost:8000/api/v1` |

## 5. Execução Local — Backend

1. Ambiente virtual Python 3.11+, dependências instaladas via `pyproject.toml`/`requirements.txt` (`fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pandas`, `openpyxl`, `python-jose` ou `pyjwt`, `passlib[bcrypt]`, `pydantic-settings`, `pytest`, `pytest-cov`, `black`, `ruff`, `mypy`).
2. Aplicação das migrações: `alembic upgrade head`.
3. Execução do seed inicial (usuário Administrador, UFs — `SPRINT_01.md`, `SPRINT_02.md`).
4. Subida do servidor: `uvicorn app.main:app --reload --port 8000`.
5. Documentação interativa disponível em `http://localhost:8000/docs`.

## 6. Execução Local — Frontend

1. Dependências instaladas via `npm install` (`react`, `react-dom`, `react-router-dom`, `chart.js`, `react-chartjs-2`, `tailwindcss`, `vite`, `vitest`, `@testing-library/react`, `lucide-react`).
2. Subida do servidor de desenvolvimento: `npm run dev`, disponível em `http://localhost:5173`.
3. O frontend consome a API em `VITE_API_BASE_URL` (seção 4).

## 7. Build de Produção

1. **Backend:** nenhum passo de build é necessário além da instalação de dependências; a aplicação roda diretamente via `uvicorn`/`gunicorn` a partir do código-fonte Python.
2. **Frontend:** `npm run build`, gerando artefatos estáticos otimizados em `frontend/dist/`, servíveis por qualquer servidor de arquivos estáticos ou CDN.

## 8. Publicação da POC (Ambiente de Demonstração)

Para os fins da POC, a publicação recomendada é composta por:

1. **Backend:** contêiner Docker (`backend/Dockerfile`, criado na Sprint 12) executando `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`, publicado em uma plataforma de hospedagem de contêineres (a escolha específica de provedor de nuvem é uma decisão operacional do usuário, fora do escopo desta documentação técnica).
2. **Frontend:** artefato estático de `npm run build`, publicado em qualquer hosting estático (ex.: mesma plataforma do backend servindo arquivos estáticos, ou um serviço de hospedagem estático dedicado).
3. **Banco:** para a POC, o arquivo SQLite pode ser mantido em um volume persistente do contêiner do backend; para maior robustez, recomenda-se desde já um PostgreSQL gerenciado, seguindo a migração da seção 9, aproveitando a compatibilidade nativa da modelagem (`DATABASE.md`).
4. **Armazenamento de arquivos:** o diretório `STORAGE_DIR` (importações originais) deve residir em volume persistente, não em armazenamento efêmero do contêiner.

## 9. Migração de SQLite para PostgreSQL

1. Provisionar uma instância PostgreSQL (versão 14+).
2. Definir `DATABASE_URL` no formato `postgresql+psycopg://usuario:senha@host:porta/banco`.
3. Executar `alembic upgrade head` contra o novo banco — as mesmas migrações usadas em SQLite são aplicadas sem alteração, por força das regras de compatibilidade de `DATABASE.md`, seção 3.
4. Migração de dados existentes (de um SQLite já populado para o PostgreSQL novo) é realizada via script de exportação/importação tabela a tabela (ferramenta `pgloader` ou script Python dedicado usando Pandas, não incluído nas Sprints 00–12 por não ser necessário à POC — a POC inicia diretamente em SQLite ou diretamente em PostgreSQL, conforme decisão do ambiente de publicação).
5. Nenhuma alteração de código de aplicação é necessária — a camada de acesso a dados (`SQLAlchemy`) e o dialeto são resolvidos exclusivamente pela `DATABASE_URL`.

## 10. Backup e Recuperação (POC)

Conforme `DATABASE.md`, seção 7: cópia do arquivo SQLite antes de rollbacks em massa; em PostgreSQL, a estratégia de backup é a nativa do provedor de hospedagem escolhido.

## 11. Observabilidade Mínima

1. Endpoint de verificação de saúde: `GET /api/v1/health`, retornando `200` com `{ "status": "ok", "database": "ok" }` (verificação simples de conectividade com o banco).
2. Logs técnicos (`LOGS.md`) direcionados a `stdout`/`stderr` em ambiente de contêiner, coletáveis pela plataforma de hospedagem.

## 12. Segurança de Implantação

1. HTTPS obrigatório em qualquer ambiente publicado (terminado no proxy reverso/plataforma de hospedagem).
2. `CORS_ALLOWED_ORIGINS` restrito exclusivamente ao domínio real do frontend publicado em produção (nunca `*`).
3. Segredos (`JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`, credenciais de banco) geridos exclusivamente via variáveis de ambiente do provedor de hospedagem ou gerenciador de segredos, nunca versionados em `.env` commitado (`GITHUB.md`, `.gitignore`).

## 13. Checklist de Publicação

1. Todas as migrações aplicadas com sucesso no banco de destino.
2. Seed de UFs e usuário Administrador executado.
3. Variáveis de ambiente de produção configuradas (seções 3 e 4).
4. Build de frontend gerado com `VITE_API_BASE_URL` apontando para a URL pública do backend.
5. `CORS_ALLOWED_ORIGINS` do backend configurado com a URL pública do frontend.
6. Endpoint `/api/v1/health` respondendo `200`.
7. Login com o usuário Administrador de seed validado manualmente.
8. Checklist completo de validação funcional executado, conforme `TUTORIAL.md`, seção 12.
