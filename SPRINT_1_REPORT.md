# SPRINT_1_REPORT.md — Relatório da Sprint 1 (Fundação do Produto)

## 1. Contexto e Análise de Lacunas

O prompt da Sprint 1 solicita, em sua quase totalidade, o escopo já entregue e validado na Sprint 0 (commit `feat: bootstrap da Sprint 0`). Conforme registrado em `docs/DECISIONS.md`, seção 5, nenhum item já entregue foi reimplementado. A tabela abaixo mapeia cada requisito da Sprint 1 ao seu estado:

| Requisito da Sprint 1 | Estado | Onde |
|---|---|---|
| Estrutura completa do backend em FastAPI | Entregue na Sprint 0 | `backend/app/` (camadas api/core/domain/infrastructure/services/repositories) |
| Estrutura completa do frontend (React + Vite + TypeScript) | Entregue na Sprint 0 | `frontend/src/` |
| SQLite via SQLAlchemy | Entregue na Sprint 0 | `backend/app/infrastructure/database.py` |
| Alembic configurado | Entregue na Sprint 0 | `backend/alembic/` + migração inicial das 19 tabelas |
| Docker e Docker Compose | Entregue na Sprint 0 (ver Pendências) | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` |
| GitHub Actions (build e testes) | Entregue na Sprint 0 | `.github/workflows/ci.yml` |
| Estrutura de pastas definitiva | Entregue na Sprint 0 | raiz + `docs/DECISIONS.md`, seção 2.4 |
| Configuração por ambiente (.env) | Entregue na Sprint 0 | `backend/app/core/config.py` + 3 `.env.example` |
| Endpoint `/health` | Entregue na Sprint 0 | `GET /api/v1/health` (verifica conexão real com o banco) |
| Página inicial da aplicação | Entregue na Sprint 0 | `frontend/src/pages/home/HomePage.tsx` (com status da API ao vivo) |
| Layout base (menu lateral, cabeçalho, conteúdo) | Entregue na Sprint 0 | `Shell`, `Sidebar`, `Topbar` |
| Logging | Entregue na Sprint 0 | JSON estruturado + middleware de requisição (`LOGS.md`) |
| **Tratamento global de erros** | **Entregue nesta Sprint 1** | ver seção 2 |
| Testes básicos de inicialização | Entregue na Sprint 0, ampliados nesta Sprint | 10 testes backend / 9 testes frontend |

## 2. Arquivos Criados/Alterados nesta Sprint

### Criados
| Arquivo | Conteúdo |
|---|---|
| `backend/app/api/error_handlers.py` | Manipuladores globais de exceção: exceções de domínio → envelope padrão `{"erro": {"codigo", "mensagem", "detalhes"}}` (API.md, seção 13); `RequestValidationError` → `422 VALIDACAO_FALHOU`; catch-all → `500 ERRO_INTERNO` com log `CRITICAL` (LOGS.md, seção 5, item 4). |
| `backend/tests/test_error_handlers.py` | 7 testes: os 5 mapeamentos de exceção de domínio, validação de entrada e exceção não mapeada (incluindo verificação de que detalhes internos não vazam ao cliente). |
| `frontend/src/components/ui/ErrorBoundary.tsx` | Boundary global de erros de renderização React, com fallback amigável e botão de recarga. |
| `frontend/src/components/ui/ErrorBoundary.test.tsx` | 2 testes (renderização normal e fallback em exceção). |
| `frontend/src/services/httpClient.test.ts` | 3 testes do cliente HTTP (sucesso, erro no envelope padrão, erro não-JSON). |
| `SPRINT_1_REPORT.md` | Este relatório. |

### Alterados
| Arquivo | Alteração |
|---|---|
| `backend/app/main.py` | Registro dos error handlers globais (`registrar_error_handlers(app)`). |
| `frontend/src/main.tsx` | Aplicação envolvida pelo `ErrorBoundary`. |
| `frontend/src/services/httpClient.ts` | Introdução da classe `ApiError` tipada (status, código, mensagem, detalhes), interpretando o envelope de erro padrão do backend, com fallback para respostas não-JSON. |
| `docs/DECISIONS.md` | Seções 5–6 adicionadas (sobreposição Sprint 0/1 e decisões desta sprint). |

## 3. Decisões Técnicas

1. **Não reimplementar o que já existia.** A Sprint 1 foi tratada como verificação + entrega de delta, preservando o trabalho validado da Sprint 0 (princípio de `MASTER_PROMPT.md`: a documentação/histórico é a fonte da verdade; retrabalho sem causa é desvio).
2. **Envelope de erro único, inclusive para validação de entrada do FastAPI.** O formato nativo `{"detail": [...]}` do FastAPI foi substituído pelo envelope `{"erro": ...}` para que o frontend tenha um único contrato de erro (API.md, seção 13). O código usado é `VALIDACAO_FALHOU`, com os erros de campo em `detalhes`.
3. **`500` nunca vaza detalhes internos.** A mensagem da exceção original vai apenas para o log técnico (nível `CRITICAL`, com stack trace); o cliente recebe mensagem genérica — coberto por teste.
4. **Testes de handler em app FastAPI isolada.** Rotas propositalmente falhas são criadas em uma instância de teste, não na aplicação real, evitando rotas fantasma em produção.
5. **`ApiError` no frontend desde já.** Embora o tratamento completo (renovação de token etc.) seja da Sprint 09, o erro tipado foi antecipado por ser parte de "tratamento global de erros" — o contrato já nasce alinhado ao backend.

## 4. Resultado da Validação (autoauditoria)

| Verificação | Resultado |
|---|---|
| `pytest --cov=app` (backend) | **10 passed**, cobertura **98%** |
| `ruff check .` / `black --check .` / `mypy app` | Sem erros |
| `alembic upgrade head` em banco limpo | OK (19 tabelas criadas) |
| Subida real do backend + `GET /api/v1/health` | `200 {"status":"ok","database":"ok"}` |
| `vitest run` (frontend) | **9 passed** (3 arquivos) |
| `eslint` / `prettier --check` | Sem erros |
| `tsc -b && vite build` | Build de produção OK |
| Varredura de segredos hardcoded em `backend/app` e `frontend/src` | Nenhum encontrado |

## 5. Pendências

1. **`docker compose up` segue sem execução ponta a ponta** — herdada da Sprint 0: o daemon Docker não é iniciável neste ambiente de implementação (sem privilégios). `docker compose config` valida sem erros. Recomenda-se executar `docker compose up --build` uma vez em ambiente com Docker antes de fechar esse critério.
2. **README não alterado** — nenhum comando de instalação mudou nesta sprint (condição do prompt para atualização não foi atingida).

## 6. Riscos Identificados

1. **Sobreposição de escopo entre prompts de sprint e a documentação do repositório** (`ROADMAP.md`/`SPRINT_XX.md`): se os próximos prompts seguirem numeração/escopo diferentes dos documentos `SPRINT_XX.md`, há risco de retrabalho ou lacunas. Mitigação: manter a prática desta sprint (gap analysis primeiro, delta depois, registro em `docs/DECISIONS.md`).
2. **Padronização do erro 422 diverge do default do FastAPI**: ferramentas/clientes que esperem o formato nativo `{"detail": ...}` precisarão usar o envelope `erro`. Risco baixo — não há consumidores externos ainda.
3. **Aviso de depreciação do `TestClient`** (starlette/httpx) nos testes do backend: inofensivo hoje, mas pode quebrar em upgrade futuro de FastAPI/Starlette. Monitorar ao atualizar dependências.
4. **Vulnerabilidades reportadas pelo `npm audit`** (5, herdadas de dependências transitivas do ecossistema Vite/dev): não afetam o build de produção diretamente, mas devem ser triadas na Sprint 12 (hardening), conforme `SPRINT_12.md`, seção 4.2.

## 7. Próximos Passos Sugeridos

1. **Sprint 02 (`SPRINT_02.md`) — Autenticação e Usuários**: JWT + bcrypt, CRUD de usuários, RBAC (`AUTENTICACAO.md`, `PERMISSOES.md`). Os error handlers desta sprint já dão suporte aos códigos `PERMISSAO_NEGADA`/`NAO_AUTENTICADO`.
2. Executar `docker compose up --build` em ambiente com Docker para fechar a pendência 5.1.
3. Na sequência natural do `ROADMAP.md`: seeds de UF (parte da Sprint 01 documental ainda não entregue — repositórios concretos e seed de UFs), depois motor de importação (Sprint 03).
