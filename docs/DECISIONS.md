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

## 12. Definições de negócio da Sprint 3 (respondidas pelo Product Owner em 12/07/2026)

As perguntas registradas na Fase 1 foram respondidas integralmente. Estas definições são **autoritativas** e orientam toda a implementação das Fases 2–7:

1. **Faturamento**: as colunas de marca da matriz mensal são **Laboratórios**. Exceção: **BRINDE não é laboratório** — é categoria comercial à parte (modelada via `laboratorios.categoria`). Não existe dimensão "Departamento" nos dados reais.
2. **Carteira oficial**: o relatório "Supervisor" do SB Promotor é a **carteira mensal oficial** promotor×cliente. Em conflito, a carteira prevalece sobre o que os checklists sugerirem. O mês de competência é informado no ato da importação (o arquivo não o contém).
3. **Tipo do promotor é cadastral** — nunca inferido dos dados importados. Promotor novo criado por importação fica com tipo pendente até definição cadastral.
4. **WeCheck sem correspondência automática**: proibido casamento fuzzy por nome. Cada `Local` do WeCheck vira registro em `clientes_integracao` (status PENDENTE) até conciliação manual/futura.
5. **Painel Avert é a carteira oficial da operação Avert**; a coluna CONSULTOR identifica a **promotora** (mesmas pessoas do `Autor` do WeCheck). CNPJs sem correspondência na Base de Clientes ficam **pendentes** — nunca criam cliente automaticamente.
6. **Promotoras do WeCheck são Trade** (operação Avert/WeCheck).
7. **Aplicação de checklist = visita**: cada linha dos exports de checklist (id `VISITA` + data/hora `APLICAÇÃO`) é o registro individual de visita do SB Promotor.
8. **Arquitetura**: nunca usar identificadores naturais como chave primária; `Código Cliente` não é identificador global; **UUID interno em todas as entidades**; códigos externos são apenas identificadores de integração; arquitetura preparada para multiempresa.

## 13. Decisões técnicas da Fase 2 (modelagem adaptada aos dados reais)

1. **Identidade UUID interna como PK de todas as entidades** (`String(36)`, UUID v4 gerado em `app/infrastructure/models/identidade.py`), cumprindo a diretriz do item 12.8. Todas as FKs foram convertidas em conjunto. **Exceção documentada:** `ufs.sigla` permanece PK — é tabela de referência geográfica estática com código oficial imutável (não é identidade de negócio). `String(36)` (e não tipo nativo `UUID`) mantém compatibilidade SQLite ↔ PostgreSQL; a troca por `UUID` nativo no PostgreSQL é evolução isolada de infraestrutura.
2. **`empresas.uuid` consolidada no próprio `id`** — com UUID generalizado, a coluna separada da Sprint 2 tornou-se redundante.
3. **`tipos_promotor` (tabela cadastral) substitui o enum embutido `promotores.tipo`**, permitindo gestão de tipos sem alteração de código (item 12.3). Seed TECNICO/TRADE aplicado pela própria migração (e restaurável via `seed_tipos_promotor.py`). `promotores.tipo_promotor_id` é **nulo** para promotores criados por importação sem definição cadastral. `promotores.supervisor_id` passou a aceitar nulo (nenhuma fonte real informa supervisor) e `promotores.area` registra a Área do relatório SB.
4. **`clientes_integracao`**: conciliação de identidades externas (sistema de origem + código/CNPJ/texto livre → cliente interno), com status PENDENTE/VINCULADO/IGNORADO. Implementa os itens 12.4 e 12.5 — nunca cria cliente automaticamente.
5. **Novas tabelas de staging fiéis às fontes reais** (regra "nunca descartar colunas"): `visitas_resumo_sb` (relatório Supervisor: contagens por promotor×cliente×competência), `carteiras_avert` (Painel Avert completo, inclusive colunas de compra vazias), `visitas_produtos_sb` (detalhe de produtos por visita), `clientes_vendedores` (RCA 1..4 da Base de Clientes com a ordem preservada).
6. **`visitas` é a entidade unificada das duas origens** (Strategy, item 11.6): ganhou `origem` (SB_PROMOTOR/WECHECK), `codigo_externo` (id VISITA), `cliente_id` **nulo permitido** (WeCheck não referencia cliente), `cliente_integracao_id`, campos textuais de localização do WeCheck e `dados_brutos` (JSON) para preservação integral do contexto de origem. Unicidade `(origem, codigo_externo)` garante idempotência de reimportação.
7. **`checklists`/`checklist_perguntas` importáveis**: templates ganham `codigo_externo` (CK_ID) e `origem`; `tipo_promotor_alvo` aceita nulo (fontes reais não informam o público-alvo e ele não pode ser inferido). `checklist_respostas.resposta_valor` virou `Text` (respostas reais excedem 500 caracteres — URLs de fotos e descrições longas).
8. **`faturamentos.departamento_id` aceita nulo** (item 12.1) e `laboratorios.categoria` distingue LABORATORIO/BRINDE.
9. **`importacoes` ganhou `hash_conteudo`** (deduplicação por conteúdo lógico, decisão 11.2) **e `competencia`** (mês de referência informado na importação, decisão 12.2). Novos tipos de arquivo: WECHECK, PAINEL_AVERT, SB_PRODUTOS (CARTEIRA passa a designar o relatório Supervisor do SB).
10. **`clientes` cobre as 22 colunas reais** da Base de Clientes: inscrição estadual, tipo de pessoa, ramo de atividade, número, bairro, CEP, telefone e data da última compra; RCAs vão para `clientes_vendedores`.
11. **Migração Alembic em batch mode** (`render_as_batch` no SQLite, que recria tabelas para ALTER), com ciclo `upgrade → downgrade → upgrade` validado e diff de autogeneração vazio ao final (esquema ≡ modelos). Linhas pré-existentes preservariam o id numérico como texto (não há base em produção na POC); linhas novas recebem UUID v4.
12. **Multiempresa**: a identidade UUID e a ausência de chaves naturais deixam o esquema pronto para introduzir `empresa_id` (FK para `empresas`) nas entidades de negócio quando o multi-tenant for ativado (TUTORIAL.md, seção 15) — decisão de não adicionar a coluna agora: metade de um tenant (coluna sem filtro em consultas/autorização) daria falsa sensação de isolamento.

## 14. Decisões técnicas das Fases 3–4 (conectores Strategy por origem real)

1. **Um conector por origem física, não por entidade de domínio** (`etl/conectores/`): `ConectorBaseClientes`, `ConectorFaturamentoMatriz`, `ConectorSbSupervisor`, `ConectorSbProdutos`, `ConectorChecklistSb`, `ConectorWeCheck`, `ConectorPainelAvert`, mais `ConectorLegado` (adaptador que preserva o pipeline documental de `VISITAS`, sem fonte real). Todos implementam `ConectorOrigem.processar(caminho, execucao) -> ResultadoConector` (`etl/conectores/base.py`) — o motor não conhece particularidades de nenhuma origem, cumprindo a exigência de Strategy Pattern (item 11.6) sem espalhar regras de sistema pelo domínio.
2. **`etl/motor.py` trocou `IMPORTADORES` (validador, loader) por `CONECTORES` (Strategy)**: `_processar` delega integralmente ao conector; hash de conteúdo (`calcular_hash_conteudo`) é calculado sempre, junto ao SHA-256 binário, e a duplicidade é checada primeiro por bytes, depois por conteúdo lógico — reproduzindo a decisão 11.2 em código.
3. **`etl/motor.py` ganhou o parâmetro `competencia`** (mês de referência), repassado à `Importacao` e usado pelos conectores que dependem dele (`ConectorSbSupervisor`, `ConectorFaturamentoMatriz` como fallback do rodapé, `ConectorPainelAvert`). Reprocessamento (`ImportacaoService.reprocessar`) propaga a `competencia` da importação original — sem isso, reprocessar uma CARTEIRA falharia por competência ausente.
4. **Leitura bruta multi-aba própria dos conectores reais** (`etl/conectores/leitura.py`): `ler_abas`/`indices_por_nome`/`localizar` operam por posição e nome normalizado, tolerando cabeçalhos duplicados (dois blocos "Código" no relatório Supervisor) e colunas ausentes/extras (schema drift do WeCheck) — o leitor documental `ler_excel` (layout fixo, 1 aba) permanece só para `ConectorLegado`.
5. **Lógica de checklist compartilhada entre SB e WeCheck** (`etl/conectores/checklist_comum.py`: `obter_ou_criar_perguntas`, `gravar_respostas`, `desambiguar_enunciados`) — os dois conectores tratam formulário/aba como template, coluna como pergunta (`tipo_resposta=TEXTO`, `obrigatoria=False`, nunca inferidos) e célula preenchida como resposta; é o mesmo modelo de domínio alimentado por duas origens, conforme a exigência de Strategy.
6. **Idempotência por chave natural de cada origem, nunca por posição de linha**: SB usa `(origem, codigo_externo=VISITA)`; WeCheck deriva um `codigo_externo` determinístico via SHA-256(formulário|autor|data/hora|local) — a origem não expõe id de evento. Resposta já existente com valor diferente vira erro de linha ("nunca sobrescrever"); idêntica é no-op idempotente.
7. **Faturamento**: competência extraída do rodapé "Filtros aplicados" (regex de ano/mês); marca `BRINDE` recebe `CategoriaComercial.BRINDE`, as demais `LABORATORIO` (decisão 12.1). Reimportação com valor divergente para o mesmo cliente×marca×competência é rejeitada por célula, nunca sobrescrita.
8. **Painel Avert**: casamento CNPJ→cliente por comparação apenas de dígitos (determinístico, não fuzzy); CNPJ com mais de um cliente interno correspondente (77 documentos duplicados descobertos na Fase 1) fica PENDENTE com observação explicando a ambiguidade, em vez de escolher arbitrariamente. CONSULTOR vira `Promotor` via `obter_ou_criar_promotor_por_nome` com tipo TRADE (decisão 12.6), aplicado somente na criação.
9. **Testes reescritos com estruturas sintéticas fiéis ao real** (`tests/etl/fixtures_reais.py` + `tests/etl/test_importadores.py`), substituindo as fixtures de layout documental (`fixtures_xlsx.py` permanece só para `ConectorLegado`/motor). Validadores e loaders exclusivos do layout documental antigo (`carteira`, `faturamento`, `checklist`) foram removidos — sem fonte real, mantê-los seria código morto.

## 15. Decisões técnicas das Fases 5–6 (importação real completa e qualidade)

1. **CLI de importação com inferência estrutural de tipo** (`etl/cli.py`): como o endpoint de upload segue fora de escopo (SPRINT_2_REPORT.md, pendência 1), a CLI é o caminho operacional para carregar arquivos — inclusive os desta sprint. `inferir_tipo_arquivo` decide o tipo por assinatura de abas/colunas (nunca pelo nome do arquivo, que é livre nos exports reais): nomes de aba conhecidos (`Produtos`/`Gondola`/...) para SB_PRODUTOS; conjuntos de colunas do cabeçalho da primeira aba para os demais tipos. Arquivo que não casa com nenhuma assinatura é reportado como não reconhecido, nunca importado às cegas.
2. **Carga completa executada contra os 5 pacotes reais** (ambiente de execução, banco descartável — nunca commitado): confirma em produção-símile todas as decisões de Fases 1–4. Resultados batem exatamente com o profiling da Fase 1: 33/34 cópias do Supervisor e 25/26 cópias do Checklist recusadas por hash de conteúdo; 12 clientes ausentes citados pela carteira SB; 1 código ausente no Faturamento de Janeiro; 43/205 CNPJs do Painel Avert sem correspondência; 8.056 clientes com carteira SB ativa. Detalhes sanitizados em `docs/DATA_QUALITY.md`.
3. **Bug real encontrado e corrigido na carga**: `obter_ou_criar_promotor_por_nome` (WeCheck/Painel Avert) comparava nomes via `func.lower()` do SQL. O `LOWER()` nativo do SQLite não faz case-folding de caracteres acentuados — `"Ú"` nunca vira `"ú"` — enquanto o Python normaliza corretamente; logo, toda promotora com nome acentuado criava um registro novo a cada visita (chegou a 93 `promotores` em vez dos ~45 esperados). Corrigido comparando em Python (`str.casefold`), sem depender de nenhuma função de case do SQL. Teste de regressão: `test_wecheck_nome_acentuado_nao_duplica_promotora`. Nenhum outro ponto do código usava `func.lower`/`func.upper`/`ilike` (varredura confirmada).
4. **Serviço de qualidade de dados** (`app/services/qualidade_dados_service.py`): consultas somente-leitura agregando cobertura (faturamento, carteira SB, carteira Avert) e pendências de conciliação por sistema de origem, mais detecção de documentos (CNPJ/CPF) compartilhados por múltiplos clientes — anomalia herdada do ERP, nunca corrigida automaticamente (apenas reportada). Não expõe endpoint HTTP nesta sprint: dashboards/KPIs são escopo de sprint futura (KPIS.md/DASHBOARD.md); aqui o serviço alimenta apenas `docs/DATA_QUALITY.md` e é coberto por testes unitários.

---

# Sprint 4 — Dashboard Executivo

## 16. Adaptação dos KPIs à realidade do schema (diverge de `KPIS.md` §4)

Sprints 0/1 (documentais) escreveram `KPIS.md` **antes** da engenharia reversa dos dados reais (Sprint 3). Lá, "Região" é apenas uma quebra dimensional (`GROUP BY uf_sigla`) dos KPIs de Carteira/Cobertura/Positivação — não existe um "carteira regional" separado da carteira SB. A Sprint 3, porém, revelou que a operação tem **dois conceitos de carteira genuinamente distintos e paralelos**, cada um com sua própria fonte e tabela: a carteira SB (`carteiras`, promotores Técnico/Trade não-Avert, decisão 12.2) e a carteira Avert (`carteiras_avert`, promotoras Trade/Avert, organizada pelo próprio painel de origem por campo `REGIONAL`, decisão 12.5).

O prompt desta Sprint pede 4 cartões de faturamento paralelos e mutuamente exclusivos (Total / Carteira / Região / Fora da Carteira) — estrutura que só faz sentido de negócio se "Região" for a segunda carteira (Avert), não uma quebra geográfica (que já vira o gráfico de "Distribuição por UF" desta sprint). Decisão: **`Faturamento da Região` = faturamento dos clientes vinculados à carteira Avert (`carteiras_avert`, sem restrição de vigência — o painel não versiona)**, análogo em estrutura ao KPI Carteira do `KPIS.md` §3 mas aplicado a `carteiras_avert` em vez de `carteiras`. UF continua sendo filtro global e ganha representação própria no gráfico de distribuição geográfica (item 6 dos gráficos) — nenhuma informação da intenção original de `KPIS.md` foi perdida, apenas realocada para o componente mais adequado ao dado real.

Regra de mutualidade: `Faturamento Total = Faturamento Carteira + Faturamento Região + Faturamento Fora da Carteira` sempre que nenhum filtro de promotor/supervisor/tipo restringe o universo — um cliente com faturamento nunca pertence a mais de um dos três grupos simultaneamente (carteira SB e carteira Avert atendem populações de cliente distintas na prática, mas a query de "Fora da Carteira" exclui explicitamente quem está em qualquer uma das duas, garantindo a soma mesmo em sobreposição eventual).

## 17. Elegibilidade de importação (confirma `REGRAS_DE_NEGOCIO.md` §7 — sem custo extra)

`REGRAS_DE_NEGOCIO.md` §7 exige que toda consulta analítica considere apenas registros de importações `CONCLUIDA`/`CONCLUIDA_COM_ERROS`. Nenhuma query do dashboard precisa impor esse filtro manualmente: o motor de importação (Sprint 2/3) só persiste linhas de domínio (`faturamentos`, `carteiras`, `visitas`, `checklist_respostas` etc.) dentro da transação de uma importação bem-sucedida — `FALHOU` sempre faz rollback completo (`etl/motor.py`, testado desde a Sprint 2) e `PENDENTE`/`PROCESSANDO`/`REVERTIDA` nunca chegam a gravar linhas de domínio (rollback de negócio é funcionalidade futura, ainda não implementada). Logo, toda linha existente nas tabelas de fato já satisfaz a regra por construção — evita joins desnecessários com `importacoes` em cada KPI (`REGRAS_DE_NEGOCIO.md` §7 combinada com a garantia transacional do motor).

Pela mesma razão, a "seleção de versão corrente" (mesma seção, para Faturamento/Visitas/Checklist) também não exige lógica extra: os conectores da Sprint 3 impõem unicidade por chave natural (`faturamentos` por cliente×laboratório×competência é idempotente/rejeitado em conflito — nunca duplica; `visitas` é única por `(origem, codigo_externo)`; `checklist_respostas` é única por `(visita_id, checklist_pergunta_id)`) — só existe uma linha "corrente" possível por natureza do dado, não pela maior `importacoes.versao`.

## 18. Definições dos KPIs implementados (cartões da Sprint 4)

Convenções de `KPIS.md` §2 mantidas: divisão por zero retorna `null` (nunca `0` nem erro); percentuais retornam como fração decimal; formatação percentual é só de apresentação (frontend).

| KPI | Fórmula | Filtros aplicáveis |
|---|---|---|
| Faturamento Total | `SUM(faturamentos.valor_faturado)` no escopo de cliente resultante dos filtros (ver §16) | Ano, Mês, UF, Laboratório, Tipo Promotor, Sistema Origem, Supervisor, Promotor |
| Faturamento da Carteira | `SUM(valor_faturado)` restrito a `cliente_id` em `carteiras` ATIVA/vigente (`KPIS.md` §3) | idem |
| Faturamento da Região | `SUM(valor_faturado)` restrito a `cliente_id` em `carteiras_avert` (seção 16) | idem |
| Faturamento Fora da Carteira | `SUM(valor_faturado)` para `cliente_id` fora de `carteiras` E fora de `carteiras_avert` (`KPIS.md` §5) | Ano, Mês, UF, Laboratório apenas — `null`/"não aplicável" se Promotor/Supervisor/Tipo Promotor ativos |
| Quantidade de Clientes | `COUNT(DISTINCT cliente_id)` no escopo filtrado | todos |
| Clientes Positivados | `COUNT(DISTINCT cliente_id)` com `SUM(valor_faturado) > 0` no escopo filtrado (`KPIS.md` §9, generalizado para além da carteira) | todos |
| Cobertura da Carteira | `KPIS.md` §8, restrito à carteira SB: `COUNT(clientes carteira com visita REALIZADA no período) / COUNT(clientes carteira)` | Ano, Mês, UF, Tipo Promotor, Supervisor, Promotor |
| Número de Visitas | `COUNT(visitas.id)` no escopo filtrado (por `promotor_id`/`data_visita`/`origem`) | Ano, Mês, UF (via cliente), Tipo Promotor, Sistema Origem, Supervisor, Promotor |
| Número de Checklists | `COUNT(checklist_respostas.id)` no escopo filtrado (via `visitas`) | idem |
| Última Importação | mais recente `importacoes` por `tipo_arquivo` (reaproveita `ImportacaoRepository`) | nenhum |

`Conformidade de Checklist` (`KPIS.md` §7, percentual ponderado por peso, só perguntas `SIM_NAO`) e o `Índice de Desempenho`/Ranking (`KPIS.md` §10, pesos 35/35/20/10) são implementados **exatamente pela fórmula original** — usados no gráfico "Top Promotores" (por Índice de Desempenho) e na página de detalhe do promotor ("Principais indicadores"), não como cartões avulsos na Home (o prompt da sprint já cobre "Número de Checklists" como contagem simples nos cartões; o percentual de conformidade fica no nível analítico mais adequado).

`Sistema de Origem` como filtro: quando fixado em `SB_PROMOTOR`, a Região (Avert) fica `null`/zero (sem interseção de população); quando fixado em `WECHECK`/`PAINEL_AVERT`, a Carteira (SB) fica `null`/zero — reflete a segregação real das duas operações (decisão 11.6).

## 19. Performance

Todos os KPIs, séries de gráfico e a tabela de promotores são resolvidos com agregações SQL (`GROUP BY`/`func.sum`/`func.count`) — nunca carregando entidades para agregar em Python, exceto o cálculo do Índice de Desempenho (Ranking), que combina 4 métricas já agregadas por promotor em memória (dezenas de promotores na base real — custo desprezível, evita 4 subqueries correlacionadas por linha). Índices novos adicionados via migração quando o padrão de acesso do dashboard não era coberto pelos índices da Sprint 2/3.

Índices novos (migração `4ccef2784c6d`, `alembic check` sem drift): `clientes.uf_sigla` (filtro/GROUP BY em quase todo endpoint), `carteiras.promotor_id` e `carteiras_avert.promotor_id`/`cliente_id` (`.in_(ids)` recorrente em `_promotores_com_metricas`, a rotina anti-N+1 da tabela de promotores/ranking), `faturamentos.laboratorio_id` (filtro/GROUP BY de "Faturamento por Laboratório"), `visitas.cliente_id` (join de cobertura e do filtro de UF em visitas). Colunas já cobertas por índice composto existente (`faturamentos.cliente_id`, `checklist_respostas.visita_id`, `checklist_perguntas.checklist_id`) não repetidas. `promotores.supervisor_id` e `importacoes.criado_em` deliberadamente não indexados: ambas as tabelas permanecem pequenas em produção (dezenas de promotores; uma linha de importação por arquivo processado), tornando o índice um custo de escrita sem ganho de leitura mensurável — reavaliar se o volume real divergir dessa premissa.

## 20. Frontend do Dashboard Executivo (Sprint 4)

Construído inteiramente sobre a infraestrutura da Sprint 0 (React 18 + Vite + TypeScript + TailwindCSS + React Router + TanStack React Query + Chart.js/react-chartjs-2), sem novas dependências. Decisões específicas desta sprint:

1. **Filtros globais refletidos na URL** (`useFiltrosDashboard`, via `useSearchParams`): cada alteração de filtro atualiza a query string em vez de estado local isolado — permite recarregar a página, voltar/avançar no navegador e enviar um link do dashboard já filtrado, sem introduzir uma lib de estado global (`FRONTEND.md` §2.5 já veta isso fora da stack obrigatória).
2. **`BarraDeFiltros` com `<select>` nativos**, não os componentes `Select`/`MultiSelect` do inventário completo de `DESIGN_SYSTEM.md` §6 — todos os 8 filtros do backend são de seleção única; construir um componente `Select` customizado só para reimplementar um `<select>` nativo seria complexidade sem benefício nesta POC ("Feito é melhor que perfeito").
3. **Distribuição por UF como tabela, não mapa**: o prompt da sprint permite explicitamente esse fallback quando não há suporte a mapa; nenhuma lib de mapas está na stack (`README.md` §3) e adicioná-la só para este bloco violaria "não altere arquitetura sem necessidade".
4. **Inventário de componentes reduzido ao necessário**: apenas `Card`, `KpiCard`, `Skeleton`, `EmptyState`, `ErrorState` e os wrappers de gráfico (`LineChart`, `BarChart`, `DoughnutChart`) foram implementados de `DESIGN_SYSTEM.md` §6/§9 — `Modal`, `Toast`, `MultiSelect`, `DateRangePicker`, `FileUpload`, `Tabs`, `RadarChart`, `Breadcrumb`, `Avatar` real e `RankingList` dedicado não são usados por nenhuma tela desta sprint (autenticação, exportação e upload seguem fora de escopo) — construí-los agora seria funcionalidade não utilizada pelo Dashboard, na contramão da instrução explícita da sprint.
5. **`PromotorDetalhePage` nova (`/dashboard/promotores/:promotorId`)** cobre o papel de "Dashboard por Promotor" (`TELAS.md` §4) de forma simplificada: cadastro, KPIs individuais, evolução de faturamento e faturamento por laboratório, sem abas (`Tabs`) — carteira detalhada, visitas e checklists linha-a-linha ficam para quando essas listagens tiverem endpoint próprio (não pedidas nesta sprint).
6. **`react-chartjs-2`/Chart.js registrados uma única vez** em `components/charts/chartSetup.ts`, importado por cada wrapper — evita registrar elementos repetidamente e mantém a paleta categórica (`GRAFICOS.md` §3) centralizada em `paletaCores.ts`.

## 21. Autoauditoria da Sprint 4: dois bugs de cálculo encontrados e corrigidos antes da entrega

Verificação manual do Dashboard no navegador (backend real + dados sintéticos, nunca dados reais — repositório público) contra a tabela de promotores expôs duas divergências de número entre blocos da mesma tela, ambas corrigidas com teste de regressão antes do commit final:

1. **Cobertura da carteira contava visita de promotor errado.** `_cobertura_carteira` (usada pelos cartões de KPI e pela página de detalhe) verificava apenas se *algum* `REALIZADA` existia para um cliente da carteira filtrada, sem exigir que a visita fosse do promotor titular daquele vínculo — um cliente presente na carteira de dois promotores (por coincidência de dado, não deveria ocorrer em regra mas a query não impedia) fazia a visita de um promotor "cobrir" a carteira do outro. A tabela de promotores já calculava certo (`_promotores_com_metricas`, join `Visita.promotor_id == Carteira.promotor_id`); `_cobertura_carteira` foi reescrita para exigir o mesmo vínculo. Teste de regressão: `test_cobertura_carteira_nao_credita_visita_de_outro_promotor`.
2. **Filtro de UF não chegava às métricas por promotor.** `_promotores_com_metricas` (tabela de promotores e gráfico "Top Promotores") ignorava `filtros.uf_sigla` em todas as 9 subconsultas agregadas — um promotor cuja carteira inteira estava fora da UF filtrada continuava aparecendo com seus números completos, violando o requisito explícito de que os filtros globais atualizam todos os componentes da tela. Corrigido adicionando o `JOIN`/`WHERE` de UF (via `Cliente.uf_sigla`) às 9 subconsultas e a `_positivacao_promotor` (reaproveitando `_com_uf`, já existente para os KPIs agregados). Teste de regressão: `test_listar_promotores_respeita_filtro_de_uf`.

Ambos os bugs só existiam nos caminhos "por promotor" (tabela/detalhe/ranking) — os KPIs e gráficos agregados do topo da tela (calculados por `calcular_kpis` e pelos métodos `evolucao_*`/`*_por_*`) já estavam corretos, o que explica por que a divergência só apareceu ao comparar dois blocos lado a lado, não em um único número isolado.
