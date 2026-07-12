# DECISIONS.md — Decisões e Inconsistências da Sprint 0

## 1. Finalidade

Este documento registra, conforme instrução da Sprint 0, as inconsistências encontradas entre o prompt de execução da Sprint 0 e a documentação de especificação já existente (`README.md` e demais arquivos `.md` da raiz), bem como as decisões técnicas adicionais tomadas durante o bootstrap, sem bloquear a implementação. Ele não substitui nem invalida a documentação de especificação — sinaliza pontos que merecem revisão/atualização formal dos documentos correspondentes em uma sprint futura, se o Product Owner assim decidir.

## 2. Inconsistências entre o Prompt da Sprint 0 e a Documentação Existente

### 2.1 TypeScript no frontend

- **Documentação existente:** `FRONTEND.md`, seção 2, item 4, decide explicitamente **não** introduzir TypeScript, para manter a stack restrita ao que está listado em `README.md` ("React puro via Vite, sem introdução de TypeScript").
- **Prompt da Sprint 0:** exige TypeScript como tecnologia obrigatória do frontend.
- **Resolução adotada:** `README.md` (documento de maior autoridade, item 1 das instruções da Sprint 0) lista apenas "React, Vite, Chart.js, TailwindCSS" sem proibir TypeScript — a restrição era uma decisão mais específica de `FRONTEND.md`. Optou-se por seguir o prompt da Sprint 0 e adotar TypeScript (`.tsx`/`.ts`), por ser uma instrução explícita e atual do Product Owner. `FRONTEND.md` deve ser considerado desatualizado neste ponto específico; as convenções de tipagem lá descritas (JSDoc tipado) não se aplicam mais.

### 2.2 React Query

- **Documentação existente:** `FRONTEND.md`, seção 2, item 5, decide não introduzir biblioteca de estado remoto adicional além de hooks nativos.
- **Prompt da Sprint 0:** exige React Query instalado.
- **Resolução adotada:** instalado e configurado (`QueryClientProvider` em `main.tsx`), com um único uso mínimo (`useHealthCheck`) para validar a integração frontend↔backend exigida nos critérios de aceite. Nenhuma outra chamada de negócio usa React Query ainda. `FRONTEND.md` deve ser considerado desatualizado neste ponto.

### 2.3 Docker e Docker Compose antecipados

- **Documentação existente:** `ROADMAP.md` e `SPRINT_12.md` posicionam a criação de `Dockerfile`/containerização apenas na Sprint 12 (hardening/deploy final). `SPRINT_00.md` (versão original desta documentação) não previa Docker.
- **Prompt da Sprint 0:** exige que o projeto suba com `docker compose up`.
- **Resolução adotada:** `backend/Dockerfile`, `frontend/Dockerfile` e `docker-compose.yml` foram implementados já nesta sprint. A Sprint 12 deve tratar isso como já entregue, focando em *hardening* (revisão de segurança, imagens de produção, etc.) em vez de criar do zero.

### 2.4 Estrutura de pastas na raiz (`database/`, `imports/`, `scripts/`, `tests/`)

- **Documentação existente:** `README.md`, seção 8, e `BACKEND.md`/`FRONTEND.md` não previam essas quatro pastas na raiz do repositório. O armazenamento de arquivos importados (`STORAGE_DIR`) estava documentado em `DEPLOY.md` como `./storage/importacoes` (relativo a `backend/`), e o banco SQLite como `backend/promotores_bi.db`.
- **Prompt da Sprint 0:** exige `database/`, `imports/`, `scripts/` e `tests/` como pastas mínimas na raiz.
- **Resolução adotada:**
  - `database/`: passa a ser a localização oficial do arquivo SQLite (`database/app.db`), calculada dinamicamente a partir da raiz do repositório em `backend/app/core/config.py` (`REPO_ROOT_DIR`). `DATABASE.md`/`DEPLOY.md` devem ser atualizados formalmente para refletir este caminho em uma revisão futura da documentação.
  - `imports/`: passa a ser o `STORAGE_DIR` oficial (antes `./storage/importacoes`). Mesma observação de atualização futura de `DEPLOY.md`.
  - `scripts/`: criada com utilitários de desenvolvimento (`setup.sh`, `dev-backend.sh`, `dev-frontend.sh`), não documentados anteriormente — adição pura, sem conflito.
  - `tests/` (raiz): reservada para testes de ponta a ponta que atravessam backend e frontend (`TESTES.md`, seção 4.3, Sprint 12). Os testes unitários/integração do backend continuam em `backend/tests/` (pytest) e do frontend em `frontend/src/**/*.test.tsx` (vitest), exatamente como `TESTES.md` já especificava — nenhum teste existente foi movido.

### 2.5 Modelagem de banco completa nesta sprint

- **Documentação existente:** `ROADMAP.md` separa "Fundação do Projeto" (Sprint 00, infraestrutura) de "Modelagem de Dados e Migrations" (Sprint 01, os 19 modelos SQLAlchemy completos de `DICIONARIO_DE_DADOS.md`).
- **Prompt da Sprint 0:** pede apenas "estrutura inicial" de banco cobrindo 8 grupos de entidade (usuários, promotores, clientes, departamentos, importações, visitas, checklists, faturamento), reforçando "nesta sprint, apenas a estrutura base é necessária" e proibindo regras de negócio.
- **Resolução adotada:** como o esquema físico completo das 19 tabelas (incluindo as dependências diretas dos 8 grupos citados — `ufs`, `cidades`, `supervisores`, `vendedores`, `laboratorios`, `checklist_perguntas`, `checklist_respostas`, `importacao_erros`, `importacao_arquivos`, `logs_auditoria`) já estava 100% especificado em `DICIONARIO_DE_DADOS.md`, optou-se por implementar o modelo completo agora — é **estrutura de dados**, não regra de negócio (nenhum repositório, serviço, validador ou endpoint de negócio foi criado sobre essas tabelas). Isso evita construir um subconjunto solto sem integridade referencial e depois descartá-lo na Sprint 01. A Sprint 01 deve focar no que ainda falta: seeds (UF/Cidade), repositórios concretos por entidade e testes de modelagem mais aprofundados — não na recriação das tabelas.

## 3. Decisões Técnicas Adicionais (sem conflito com a documentação)

1. **Python 3.12**: `README.md` pede "Python 3.11+"; o prompt da Sprint 0 pede especificamente 3.12. `pyproject.toml` fixa `requires-python = ">=3.12"`, dentro do intervalo já permitido por `README.md`.
2. **React 18.3, não React 19**: o scaffold padrão do `create-vite` mais recente instala React 19; foi fixado explicitamente em `^18.3.1` para aderir literalmente a `README.md` ("React 18").
3. **Enums em Python via `enum.StrEnum`** (recurso do Python 3.12) em vez do padrão `class X(str, enum.Enum)`: equivalente em serialização (continua persistido como `String`, `native_enum=False`, conforme `DATABASE.md`), apenas mais idiomático para o alvo Python 3.12 (sinalizado pelo Ruff, regra `UP042`).
4. **ESLint 9 (flat config, `eslint.config.js`)** em vez do formato legado `.eslintrc`: decisão de ferramental, sem impacto de escopo.
5. **Três arquivos `.env.example`**: um na raiz (variáveis lidas pelo `docker-compose.yml`), um em `backend/` e um em `frontend/` (variáveis lidas pela aplicação em desenvolvimento local sem Docker). `DEPLOY.md` documentava apenas os dois últimos.
6. **Camadas `repositories/`, `services/`, `domain/entidades/`, `domain/contratos/`**: criadas como estrutura de pacote (pastas + `__init__.py` com docstring explicando o escopo futuro), sem implementações concretas — para não antecipar regras de negócio nesta sprint, conforme a restrição explícita do prompt. Implementações concretas começam na Sprint 01/02 (`ROADMAP.md`).

## 4. Pendências Conhecidas ao Final da Sprint 0

1. **`docker compose up` não pôde ser executado de ponta a ponta neste ambiente de implementação** — o daemon Docker não está disponível/iniciável no sandbox usado nesta sessão (sem privilégios para `dockerd`). Foi validado o que era possível sem o daemon: `docker compose config` (parse e resolução de variáveis bem-sucedidos, sem erros de sintaxe/configuração) e revisão manual dos `Dockerfile`s (padrões multi-stage padrão de mercado para Python/FastAPI e Node/Vite+nginx). **Recomenda-se que o usuário execute `docker compose up --build` em um ambiente com Docker disponível antes de considerar este critério de aceite 100% validado.**
2. Nenhuma outra pendência funcional identificada — todos os demais critérios de aceite (backend local, frontend local, testes, lint, build) foram executados e validados nesta sessão.

---

# Sprint 1 — Fundação do Produto

## 5. Sobreposição entre o prompt da Sprint 1 e a Sprint 0 já entregue

- **Inconsistência:** o prompt da Sprint 1 solicita, quase integralmente, o mesmo escopo já entregue e validado na Sprint 0 (estrutura backend/frontend, SQLite/SQLAlchemy, Alembic, Docker/Compose, GitHub Actions, `.env`, `/health`, página inicial, layout base, logging, testes básicos).
- **Resolução adotada:** nenhum item já entregue foi reimplementado ou reescrito. A Sprint 1 foi executada como *gap analysis* + entrega do delta real, que era um único item ausente: **tratamento global de erros** (backend e frontend). O detalhamento está em `SPRINT_1_REPORT.md`.

## 6. Decisões técnicas da Sprint 1

1. **Backend — manipuladores globais de exceção** (`app/api/error_handlers.py`): exceções de domínio (`app/domain/excecoes.py`) são traduzidas para o formato padrão de erro de `API.md`, seção 13 (`{"erro": {"codigo", "mensagem", "detalhes"}}`), com mapeamento explícito exceção→(status, código). `RequestValidationError` do FastAPI também foi padronizado para o mesmo envelope (código `VALIDACAO_FALHOU`), substituindo o formato nativo `{"detail": [...]}` — decisão de consistência de contrato; consumidores devem usar sempre o envelope `erro`. Exceções não mapeadas retornam `500 ERRO_INTERNO` genérico e são registradas em nível `CRITICAL` (`LOGS.md`, seção 5, item 4), sem vazar detalhes internos ao cliente.
2. **Frontend — `ErrorBoundary`** na raiz da aplicação (`main.tsx`), com fallback amigável e botão de recarga; **`ApiError`** tipado em `httpClient.ts`, que interpreta o envelope de erro padrão do backend (com fallback para respostas não-JSON, ex.: erros de proxy).
3. Testes dos handlers do backend usam uma instância FastAPI isolada com rotas propositalmente falhas, em vez de poluir a aplicação real com rotas de teste.

---

# Sprint 2 — Banco de Dados, ETL e Motor de Importação

## 7. Gap Analysis: entidades pedidas × modelo aprovado

O prompt da Sprint 2 lista 17 entidades. O modelo aprovado (`DICIONARIO_DE_DADOS.md`, implementado na Sprint 0) já cobria 16 delas, com nomenclatura própria. Mapeamento adotado, sem duplicação de tabelas:

| Entidade do prompt | Realização no modelo aprovado |
|---|---|
| Empresa | **Nova tabela `empresas`** (única lacuna real) — ver item 8 |
| Usuário | `usuarios` (existente) |
| Perfil | Enum `PerfilUsuario` em `usuarios.perfil` — RBAC de 4 perfis fixos (`PERMISSOES.md`); tabela própria não foi criada para não conflitar com a decisão aprovada |
| Promotor | `promotores` (existente) |
| Departamento | `departamentos` (existente) |
| Laboratório | `laboratorios` (existente) |
| Cliente | `clientes` (existente) |
| Cidade | `cidades` (existente) |
| UF | `ufs` (existente) |
| Carteira / CarteiraCliente | `carteiras` — o vínculo Promotor×Cliente com vigência já É o item de carteira; não há tabela-cabeçalho separada no modelo aprovado |
| Região | Atributo `ufs.regiao` (dimensão embutida na UF, conforme `DICIONARIO_DE_DADOS.md`, seção 8) |
| Importação | `importacoes` (existente) |
| ArquivoImportado | `importacao_arquivos` (existente) |
| Venda | `faturamentos` — nomenclatura aprovada do fato de venda/faturamento mensal |
| Checklist | `checklists` + `checklist_perguntas` + `checklist_respostas` (existentes) |
| Visita | `visitas` (existente) |

**Tabelas de apoio pedidas:** "auditoria das importações" = `logs_auditoria` (existente, evento `IMPORTACAO`); "logs" = `importacao_erros` (por linha) + log técnico em arquivo (`LOGS.md`) — sem tabela adicional; "versões" = colunas `versao`/`importacao_pai_id` de `importacoes` — o versionamento é intrínseco à cadeia, sem tabela separada.

## 8. UUID / Soft Delete / created_by nas tabelas existentes

O prompt pede UUID, `deleted_at` e `created_by`/`updated_by` em todos os modelos, "sempre que fizer sentido". Decisão: **aplicado integralmente apenas à tabela nova (`empresas`)**. As 19 tabelas existentes mantêm o esquema aprovado (`DICIONARIO_DE_DADOS.md`: PK inteira, `criado_em`/`atualizado_em`, inativação via `ativo`) — reescrever o esquema aprovado violaria as instruções "considere as decisões existentes como aprovadas" e "não reescreva código existente". A introdução de UUID/soft-delete geral pode ser reavaliada como migração aditiva em sprint futura, se o Product Owner decidir.

## 9. Decisões técnicas da Sprint 2

1. **Módulo `etl/` independente** (`backend/etl/`), com camadas `readers/`, `validators/`, `transformers/`, `loaders/`, `hash/`, `logs/`, `arquivos/` e o orquestrador `motor.py`. Os 5 importadores são pares (validador, loader) registrados em `IMPORTADORES` — plugáveis sem alterar o motor (Open/Closed, `BACKEND.md`, seção 3).
2. **Fluxo físico de arquivos**: `imports/incoming → processed|rejected`, com cópia imutável de todo arquivo aceito em `imports/archive` (nome `{TIPO}_{id}_{hash12}.xlsx`, `HASH.md`, seção 8). Diretórios criados automaticamente; nenhum arquivo é excluído, apenas movido/copiado.
3. **Tentativas recusadas (duplicidade/arquivo inválido) recebem `versao=0`**, mantendo-as fora da cadeia de versões válidas; `MAX(versao)` para a próxima versão exclui `FALHOU`/`REVERTIDA` (`REGRAS_DE_NEGOCIO.md`, seção 4 + `HASH.md`, seções 3 e 6). A tentativa fica registrada em `importacoes` + `importacao_erros` para auditoria.
4. **Transacionalidade em duas fases**: o registro da `Importacao` é commitado antes da carga (sobrevive a falhas); a carga de linhas roda em transação única — exceção inesperada faz rollback de todas as linhas e marca `FALHOU` (testado em `test_falha_no_loader_faz_rollback_completo_da_carga`).
5. **Reimportação de resposta de checklist já existente é rejeitada como erro de linha** (não versionada): a UQ `(visita_id, checklist_pergunta_id)` do `DICIONARIO_DE_DADOS.md`, seção 16, conflita com `REGRAS_DE_NEGOCIO.md`, seção 5.4, item 3 (nova versão de resposta). Prevaleceu o schema aprovado + "nunca sobrescrever"; o versionamento de respostas individuais fica pendente de decisão formal de especificação.
6. **Datas do pipeline em UTC naive** (`_agora_utc()`), consistentes com as colunas `DateTime` sem timezone do modelo (armazenamento UTC, `DATABASE.md`, seção 3, item 4).
7. **Endpoints de importação sem autenticação nesta sprint** (restrição explícita do prompt: "não implementar autenticação/permissões"). A exigência de perfil Administrador (`PERMISSOES.md`) será aplicada na sprint de autenticação via `Depends(exige_perfil(...))` — os endpoints já estão isolados atrás de `get_importacao_service` para facilitar isso.
8. **Reprocessamento** (`POST /importacoes/{id}/reprocessar`) copia o arquivo de `archive/` para `incoming/` e reexecuta o pipeline como importação independente — o controle de duplicidade continua valendo (reprocessar uma importação CONCLUIDA idêntica é recusado; útil para FALHOU, cujo hash é ignorado na detecção).
9. **Exclusão física permitida apenas para `status=PENDENTE`** (importação que nunca processou dados), preservando o princípio de histórico imutável para todos os demais status.
10. **Seed de UFs** (`app/infrastructure/seeds/seed_ufs.py`) entregue nesta sprint — era pendência da Sprint 01 documental e é pré-requisito dos importadores (REF-001).

## 10. Correção pós-Sprint 2: falha intermitente de CI em `test_arquivo_identico_e_recusado_como_duplicado`

**Sintoma:** o GitHub Actions reportou falha na suíte (1 de 44 testes) no push do commit `ddbdf57` (Sprint 2), embora a suíte passasse localmente.

**Causa raiz:** `tests/etl/fixtures_xlsx.py` gerava os dois arquivos do teste de duplicidade chamando `criar_xlsx()` duas vezes (mesmo conteúdo, nomes diferentes). O OpenPyXL grava um timestamp `modified` em `docProps/core.xml` no instante de `workbook.save()` — e esse valor é **sobrescrito internamente pelo próprio writer da biblioteca** (`openpyxl/writer/excel.py`), não podendo ser fixado via `workbook.properties` antes do save. Como resultado, dois arquivos com conteúdo logicamente idêntico, mas gerados em segundos de relógio diferentes, produzem bytes — e portanto hash SHA-256 — diferentes. Localmente as duas chamadas ocorriam rápido o bastante para cair no mesmo segundo (teste passava); no runner do GitHub, mais lento, cruzaram a fronteira do segundo (teste falhava). Não é um defeito do motor de importação ou do cálculo de hash (`etl/hash/sha256.py`) — ambos se comportam corretamente diante de bytes diferentes.

**Correção:** adicionado `duplicar_arquivo()` em `fixtures_xlsx.py`, que copia o arquivo já gerado byte a byte para um novo nome (`shutil.copy2`), em vez de regenerar via OpenPyXL — fiel ao cenário real de "o mesmo arquivo reenviado sob outro nome" (`HASH.md`, seção 3) e imune a variação de timestamp. `test_arquivo_identico_e_recusado_como_duplicado` foi ajustado para usá-la. Mantido, como melhoria secundária, o `created` fixo em `criar_xlsx()` (reduz ruído, ainda que não elimine sozinho a não determinismo, já documentado no comentário do arquivo).

**Verificação:** reproduzido o bug isoladamente (dois `Workbook()` salvos com >1s de intervalo geram hashes diferentes mesmo com `created` fixo); confirmado que `duplicar_arquivo()` produz hash idêntico independente de tempo decorrido; suíte completa (44 testes) e lint/mypy re-executados localmente após a correção.

---

# Sprint 3 — Integração dos Dados Reais

## 11. Decisões técnicas da Fase 1 (engenharia reversa)

1. **Dados reais nunca são versionados.** O repositório é público; os arquivos da operação (com CNPJs, nomes de clientes e funcionários) permanecem exclusivamente no ambiente de execução (`imports/`, ignorado pelo git). `docs/DATA_PROFILING.md` documenta apenas estrutura, contagens e exemplos sanitizados.
2. **Deduplicação por hash de conteúdo, além do hash binário.** O profiling provou que o mesmo relatório foi exportado 34× (SB Promotor) e 26× (Checklist) com bytes diferentes (metadados internos do xlsx variam a cada export), mas conteúdo de células idêntico. O SHA-256 binário (HASH.md) continua sendo a identidade do arquivo físico; um **hash de conteúdo** (SHA-256 sobre os valores das células, aba a aba, linha a linha) passa a ser calculado e usado como segundo critério de duplicidade. Novo campo em `importacoes`.
3. **Leitura adaptativa por nome de coluna normalizado**, nunca por posição fixa, com tolerância a colunas ausentes/extras por arquivo — exigido pelo schema drift real (WeCheck 26→31 colunas entre meses; coluna BRINDE presente só em Março/Abril no Faturamento).
4. **Wide → Long antes da persistência** (exigência da sprint, confirmada pela realidade): Faturamento (matriz Cliente×Marca → 1 linha por cliente×marca×mês), Checklists (42 colunas → 1 linha por visita×pergunta respondida), WeCheck (colunas de pergunta → linhas resposta). Nenhum dado analítico é armazenado em wide.
5. **Preservação integral**: toda linha/coluna dos arquivos de origem é preservada — colunas sem mapeamento de domínio vão para um campo JSON `dados_brutos` na tabela de staging correspondente, nunca descartadas.
6. **Strategy Pattern para origens de visita** (exigência da sprint): `SBPromotorImporter` e `WeCheckImporter` implementam o mesmo contrato e alimentam o mesmo modelo de domínio de visitas; particularidades de cada sistema ficam confinadas ao respectivo conector em `etl/`.

## 12. Perguntas de negócio abertas (bloqueiam Fases 2–5)

Registradas em 12/07/2026; implementação de importadores aguarda resposta do Product Owner (regra da sprint: nunca assumir regras de negócio). Lista enviada na conversa da sprint.
