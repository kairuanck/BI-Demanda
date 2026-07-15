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

## 22. KPIs da Visão 360º do Cliente (Sprint 5) — adaptações a granularidade de 1 cliente

`KPIS.md` define Cobertura (§8) e Positivação (§9) como frações sobre um *conjunto* de clientes (carteira de um promotor, ou o universo filtrado). Aplicadas a um único cliente, essas fórmulas colapsam trivialmente para 0 ou 1 (o cliente foi ou não visitado; faturou positivo ou não no período) — pouco útil para um gestor avaliar a "saúde" de um cliente específico ao longo do tempo. Decisão: generalizar para uma **razão temporal mês a mês**, mantendo a mesma ideia de "fração do esperado que aconteceu":

```
Cobertura(cliente) = COUNT(meses da janela com ≥1 visita REALIZADA) / COUNT(meses da janela)
Positivação(cliente) = COUNT(meses da janela com SUM(valor_faturado) > 0) / COUNT(meses da janela)
```

**Janela** (`_janela_meses`, `cliente_service.py`): se `mes` e `ano` estão ambos filtrados, a janela é aquele único mês (degenera para 0%/100%, comportamento correto); se apenas `ano`, a janela são os 12 meses daquele ano; sem nenhum filtro de período, a janela são os últimos 12 meses corridos a partir da data atual — a mesma janela usada pelo KPI "Faturamento últimos 12 meses" (mantém as duas métricas comparáveis quando nenhum filtro está ativo).

Demais adaptações desta sprint:
- **"Faturamento últimos 12 meses" é sempre a janela móvel dos últimos 12 meses**, independente de `ano`/`mes` filtrados — é uma métrica de tendência recente com definição fixa, não outro corte do período filtrado (que já é coberto por "Faturamento acumulado"). Evita uma segunda leitura confusa do mesmo filtro de período.
- **"Dias desde a última visita" ignora `ano`/`mes`** (só respeita `sistema_origem`) — é um indicador de frescor absoluto ("há quanto tempo não visitamos esse cliente, hoje"), não teria sentido de negócio scoped a um período arbitrário do passado.
- **`laboratorio_id` filtra igualmente todo KPI/gráfico derivado de faturamento** (acumulado, evolução mensal, quantidade de laboratórios, tabela de laboratórios), mesmo padrão já estabelecido no Dashboard Executivo (Sprint 4) para "Faturamento por Laboratório" — filtrar por um laboratório específico faz "Quantidade de Laboratórios" colapsar para 0/1 intencionalmente, mesmo raciocínio de "o filtro se aplica de verdade a tudo que ele descreve".
- **Promotor responsável não é único**: a Sprint 3 estabeleceu que um cliente pode estar simultaneamente na carteira SB e na carteira Avert (docs/DECISIONS.md, seção 16), cada uma com seu próprio promotor. A página do cliente expõe uma lista de **vínculos** (0, 1 ou 2), um por sistema de origem presente, em vez de escolher arbitrariamente um "vencedor" — reaproveita `DashboardService._promotores_com_metricas` (mesma rotina anti-N+1 e mesmas métricas já corrigidas na auditoria da Sprint 4) para montar cada cartão de promotor, garantindo que os números batam com a Tabela de Promotores.
- **"Grupo Econômico" e "Segmento"** (pedidos na seção de dados cadastrais) não existem em `clientes` — vêm do registro de `carteiras_avert` do cliente quando existir (colunas herdadas do Painel Avert, docs/DECISIONS.md seção 13); ficam `null` para clientes sem carteira Avert, não inferidos de outra fonte.
- **CNPJ exibido sem máscara** ("quando permitido" no prompt): não há sistema de permissões/autenticação implementado ainda (`PERMISSOES.md` é sprint futura, ver `SPRINT_3_REPORT.md` §11 e `SPRINT_4_REPORT.md` §9) — não há hoje nenhum mecanismo para condicionar a exibição a um perfil. Documentado como pendência, não implementado especulativamente.
- **Timeline combina 4 fontes já existentes, sem tabela nova**: visitas (`visitas.cliente_id`), checklists (1 evento por aplicação = por `visita_id` distinto, não por resposta individual), importações relacionadas (via `importacao_id` referenciado por `faturamentos`/`carteiras`/`visitas`/`carteiras_avert` do cliente) e alterações cadastrais (`logs_auditoria`, `entidade='clientes'` — já populado pelo ETL da Sprint 3 em toda criação/atualização de cliente, `etl/loaders/clientes_loader.py`). As 4 consultas são combinadas e paginadas em Python (não uma `UNION` SQL) — volume por cliente é baixo (dezenas de eventos, não milhares), mesmo raciocínio de custo desprezível já usado para o Índice de Desempenho na Sprint 4.
- **Busca global usa `ILIKE`/`LIKE` simples, sem full-text search**: nenhuma lib de FTS está na stack e o volume de `clientes` nesta POC não justifica a complexidade adicional ("não altere arquitetura sem necessidade"); um índice B-tree não acelera `LIKE '%termo%'` (padrão sem âncora à esquerda), então nenhum índice novo foi criado para `razao_social`/`nome_fantasia` — apenas `clientes.cnpj_cpf` ganhou índice (seção 23), por ser um campo mais frequentemente buscado por prefixo/valor quase-exato.
- **Histórico (Timeline) sempre mostra todos os eventos, ignora os filtros de Ano/Mês/Laboratório/Sistema de Origem da página.** Diferente dos KPIs/gráficos, a Timeline mistura 4 tipos de evento heterogêneos (visita, checklist, importação, alteração cadastral) — "Laboratório" não tem sentido para nenhum deles e "Sistema de Origem" só se aplica a visita/checklist, então aplicar os filtros parcialmente (alguns eventos filtrados, outros não) seria mais confuso do que não filtrar. Mesmo raciocínio da Sprint 4 para "Última Importação" (ignora todos os filtros de propósito — um indicador "global" não deve variar com o recorte da tela).

## 23. Performance da Visão 360º do Cliente (Sprint 5)

Mesmo princípio da Sprint 4 (`docs/DECISIONS.md`, seção 19): todo KPI, gráfico e a tabela de laboratórios são resolvidos com agregação SQL — nunca carregando entidades para somar em Python. A Timeline é a única exceção deliberada (seção 22, "Timeline combina 4 fontes"), mesmo raciocínio já aceito para o Índice de Desempenho.

Índice novo (migração `9553c7d8fa31`, `alembic check` sem drift): `clientes.cnpj_cpf` — busca frequente por esse campo, tipicamente por prefixo/valor quase-exato. Nenhum outro índice foi necessário: `carteiras.cliente_id`/`promotor_id`, `carteiras_avert.cliente_id`/`promotor_id`, `faturamentos.cliente_id`, `visitas.cliente_id` e `logs_auditoria.(entidade, entidade_id)` já estavam cobertos pelos índices da Sprint 4 (e de migrações anteriores) — todos os padrões de acesso desta sprint (filtrar/agrupar por `cliente_id`, montar a Timeline, montar os vínculos de promotor) reaproveitam esses mesmos índices sem necessidade de nenhum novo.

A rotina de "vínculos de promotor" (`_vinculos_promotor`) chama `DashboardService._promotores_com_metricas` até 2 vezes (uma por sistema de origem presente) — cada chamada já é, em si, uma rotina anti-N+1 (poucas queries agregadas fixas, não uma por promotor). Como a Página do Cliente sempre lida com no máximo 2 vínculos, o custo total permanece um punhado de queries pequenas, nunca uma por linha de uma listagem.

## 24. Frontend da Visão 360º do Cliente (Sprint 5)

Construído sobre a mesma infraestrutura do Dashboard Executivo (Sprint 4), reaproveitando `KpiCard`, `Card`, `Skeleton`, `EmptyState`, `ErrorState`, `BlocoGrafico`, `LineChart`, `BarChart` e `formatadores.ts` sem alterar nenhum deles estruturalmente — apenas extraindo `NOMES_MES` (antes duplicado em `BarraDeFiltros`/`PromotorDetalhePage`) para `formatadores.ts`, reaproveitado agora por 3 telas (seção 25, item 3).

1. **Busca global no Topbar** (visível em toda tela autenticada) navega para `/clientes?q=...` — a mesma página `/clientes` funciona como "resultados de pesquisa" completos, evitando duas implementações de busca (um dropdown rápido + uma página cheia); o campo de busca da própria página `/clientes` mantém a UX de digitar e ver resultados atualizados (debounce de 300ms, sem nova biblioteca).
2. **Carteira do promotor exposta via reaproveitamento do endpoint de busca** (`GET /clientes?promotor_id=...`), não um endpoint novo — a Página do Promotor (Sprint 4) ganhou uma seção "Carteira" que lista os clientes daquele promotor com link para a Página do Cliente, fechando a navegação Tabela de Promotores → Promotor → Cliente pedida nesta sprint.
3. **Filtros da Página do Cliente (Ano/Mês/Laboratório/Sistema de Origem) em estado de URL** (`useSearchParams`), mesmo padrão da Sprint 4 — permite recarregar/compartilhar a página já filtrada.
4. **Nenhuma tela nova além de `/clientes` e `/clientes/:clienteId`** — não foi criado CRUD de cliente, exportação ou tela de administração: nada disso foi pedido e construir agora seria funcionalidade não utilizada pela Visão 360º.

## 25. Autoauditoria da Sprint 5: três problemas encontrados e corrigidos antes da entrega

Verificação manual no navegador (backend real + dados sintéticos fictícios, nunca dados reais) e revisão crítica do código encontraram 3 problemas antes do commit final:

1. **Busca de cliente por cidade/razão social com acento não encontrava nada.** `Cliente.razao_social.ilike("%são paulo%")` no SQLite não casava com `"SÃO PAULO"` — o `LOWER()` nativo do SQLite não faz *case-folding* de caracteres acentuados, a mesma limitação já corrigida na Sprint 3 para deduplicação de nomes de promotor (`docs/DECISIONS.md`, seção 15.3), agora reaparecendo na busca textual. Corrigido registrando uma função SQL customizada (`norm_busca`, `app/infrastructure/database.py`) só para o dialeto SQLite — remove acento e caixa via `unicodedata` antes de comparar; o `ILIKE` do PostgreSQL já resolve isso nativamente e continua no caminho original. Campos puramente numéricos (`codigo_externo`, `cnpj_cpf`) não precisam da normalização e permanecem em `ILIKE` simples, preservando o uso do índice novo de `cnpj_cpf` (seção 23). Teste de regressão: `test_busca_clientes_ignora_acento_e_caixa`.
2. **Página de cliente/promotor inexistente demorava ~7s para mostrar o erro amigável.** O React Query tentava de novo automaticamente (padrão: 3 tentativas com backoff) mesmo para um 404 — que nunca vai ter sucesso em uma nova tentativa, já que o registro simplesmente não existe. Nesse meio tempo a tela ficava presa em estado de carregamento (skeletons), contrariando o requisito de UX de "mensagens amigáveis" e "tratamento de erros". Corrigido com uma função `retry` global no `QueryClient` (`main.tsx`) que não tenta de novo especificamente em erros 404, mantendo o retry padrão para erros transitórios (rede, 5xx) — corrige a Página do Cliente (nova) e também a Página do Promotor (Sprint 4, mesmo sintoma, nunca tinha sido percebido porque as capturas de tela da Sprint 4 só testaram IDs válidos).
3. **`NOMES_MES` duplicado em 3 arquivos** (`BarraDeFiltros`, `PromotorDetalhePage` da Sprint 4, e a nova `ClienteDetalhePage`). Consolidado como export único em `utils/formatadores.ts` (seção 24) — sem mudança de comportamento, elimina a duplicação antes que um quarto seletor de mês precisasse dela.

# Sprint 6 — Central de Importações

## 26. Upload Web reaproveita 100% do pipeline ETL — sem reescrever nada do motor

O objetivo da sprint é eliminar a necessidade de terminal, não construir um segundo caminho de importação. `ImportacaoService.importar_upload` grava os bytes recebidos em `imports/incoming/` (mesmo diretório da CLI, via `FluxoArquivos`) e delega para `MotorImportacao.importar()` — o mesmo método, com o mesmo controle de duplicidade/versionamento/auditoria (`etl/motor.py`, inalterado desde a Sprint 3) que a CLI sempre usou. O upload Web não é um "modo diferente" de importar; é uma segunda porta de entrada para o mesmo pipeline.

Duas peças que só existiam dentro de `etl/cli.py` foram extraídas para módulos compartilhados, para que o endpoint HTTP pudesse reutilizá-las sem importar um script de linha de comando na camada de API:
- `inferir_tipo_arquivo` (assinatura de abas/colunas → `TipoArquivoImportacao`, nunca pelo nome do arquivo) → `etl/inferencia.py`. **Isto é o que elimina a necessidade de o usuário escolher manualmente o tipo do arquivo na tela de upload** — o mesmo raciocínio "nunca por nome de arquivo" de `docs/DECISIONS.md`, seção 11.3, agora vale também para o upload Web.
- `obter_ou_criar_usuario_sistema` → `app/services/usuario_service.py`. `etl/cli.py` reexporta os dois nomes (`from etl.inferencia import inferir_tipo_arquivo`, `from app.services.usuario_service import obter_ou_criar_usuario_sistema`), então os testes e chamadores existentes continuam funcionando sem alteração.

**Sem autenticação implementada ainda** (sprint futura, `AUTENTICACAO.md`), o upload Web registra a importação sob o mesmo usuário de sistema que a CLI sempre usou (`sistema@promotoresbi.local`) — não foi criado um segundo usuário técnico "do upload" para não inventar uma distinção de identidade que a autenticação real vai substituir de qualquer forma. O nome de exibição mudou de "Sistema (carga CLI)" para "Sistema (sem autenticação)", já que agora dois caminhos (CLI e Web) compartilham o mesmo usuário.

Arquivo com estrutura não reconhecida **não gera registro em `importacoes`** — o upload é recusado com `422 VALIDACAO_FALHOU` antes de qualquer linha ser escrita, exatamente como a CLI já fazia (`[NAO_RECONHECIDO]`, sem chamar `motor.importar`). Verificado no navegador: o arquivo inválido aparece só como um Toast de erro na fila local, nunca no Histórico.

Nome de arquivo recebido do upload é saneado com `Path(nome_arquivo).name` antes de gravar em `incoming/`, descartando qualquer componente de diretório que o cliente HTTP possa enviar (proteção básica contra path traversal em um campo controlado pelo usuário).

## 27. Cancelamento: escopo deliberadamente restrito a `PENDENTE`

O processamento desta arquitetura é **síncrono** — `motor.importar()` roda dentro da própria requisição HTTP, sem fila em segundo plano (Celery, RQ ou similar). Não existe, portanto, uma execução "em andamento" no servidor que um botão "Cancelar" possa de fato interromper — e criar essa infraestrutura de fila só para viabilizar cancelamento durante o processamento seria alterar a arquitetura sem necessidade, na contramão da instrução explícita da sprint.

`POST /importacoes/{id}/cancelar` cobre o único estado em que cancelar tem sentido real: uma importação `PENDENTE` (registrada mas ainda não iniciada). `MotorImportacao.cancelar()` reaproveita exatamente o mesmo formato de `_registrar_recusa` (status `FALHOU`, `versao=0` — fora da cadeia de versões válidas, `ImportacaoErro` explicativo, registro de auditoria) em vez de introduzir um novo status `CANCELADA` no enum `StatusImportacao` — nenhuma consulta existente (dashboard, timeline do cliente, `MAX(versao)`) precisa aprender a tratar mais um valor.

Para a percepção de "cancelar um upload em andamento" pedida pela UX (arquivo ainda subindo na fila da tela), a solução é inteiramente do lado do cliente: `enviarImportacao` (`services/importacaoService.ts`) usa `XMLHttpRequest` (não `fetch`, que não expõe progresso de upload em todos os navegadores) e devolve uma função `cancelar()` que chama `xhr.abort()` — o botão "Cancelar" da fila aborta a requisição em voo. Isso não interrompe o processamento se o servidor já tiver começado (a janela é pequena: arquivos ≤20MB, processamento tipicamente abaixo de 1s), limitação documentada aqui em vez de resolvida com uma arquitetura de fila que a sprint não pediu.

`Rollback de dados já commitados` (reverter linhas de `faturamentos`/`carteiras`/etc. de uma importação `CONCLUIDA`) continua **fora de escopo**, como já registrado na seção 17 ("rollback de negócio é funcionalidade futura, ainda não implementada"). "Cancelamento" nesta sprint não é sinônimo de "reverter uma importação concluída".

## 28. Relatório de inconsistências e "usuário responsável"

`GET /importacoes/{id}/erros/relatorio` devolve um CSV (delimitador `;`, padrão de planilha brasileira) com todos os erros de validação, sem paginação — reaproveita `ImportacaoRepository.listar_todos_erros` (mesma consulta de `listar_erros`, sem `LIMIT`/`OFFSET`). Um BOM UTF-8 é escrito no início do arquivo para o Excel exibir corretamente nomes de coluna e mensagens acentuadas — mesma classe de cuidado com acentuação já registrada na Sprint 5 (seção 25, item 1), desta vez para abertura em planilha, não para busca em banco.

**`usuario_nome` no `ImportacaoResponse`**: o campo `usuario_id` (UUID) já existia, mas nunca era resolvido para um nome legível — a Central de Importações precisa mostrar "quem importou", não um UUID. `ImportacaoRepository.listar`/`obter` passaram a fazer `JOIN` com `usuarios` (uma consulta, sem N+1, mesmo padrão de `select(Cliente, Cidade.nome)` da Sprint 5); os poucos pontos que devolvem uma `Importacao` fora desse fluxo paginado (`reprocessar`, `importar_upload`, `listar_versoes`) usam um novo `ImportacaoRepository.anexar_usuario_nome`, uma segunda consulta pontual — não é N+1 porque o volume desses pontos é sempre 1 (o resultado de uma única operação) ou uma cadeia curta de versões (dezenas, não milhares), nunca uma linha por item de uma listagem grande.

**Bug pré-existente corrigido**: `ImportacaoResponse.duracao_segundos` já existia como uma `@property` do Pydantic desde a Sprint 2, mas nunca aparecia na resposta JSON da API — Pydantic v2 não serializa `@property` simples, apenas `@computed_field @property`. O campo "tempo de processamento", pedido explicitamente por esta sprint, depende dele; corrigido adicionando `@computed_field`. Teste de regressão: `test_upload_reconhece_estrutura_e_importa_sem_selecao_manual_de_tipo` agora também verifica `duracao_segundos is not None`.

## 29. Frontend da Central de Importações — primeiro uso de `Toast`, `Modal`, `FileUpload` e `ProgressBar`

`DESIGN_SYSTEM.md`, seção 6, sempre catalogou `Toast`, `Modal`, `FileUpload` e `ProgressBar` — nenhum tinha sido implementado até agora porque nenhuma tela anterior precisava deles (a Sprint 4 registrou isso explicitamente, `docs/DECISIONS.md`, seção "Inventário de componentes reduzido ao necessário"). A Central de Importações é a primeira tela que genuinamente precisa dos quatro:
- **`Toast`** (`components/ui/Toast.tsx` + `ToastProvider` em `main.tsx`, hook em `hooks/useToast.ts`): feedback de sucesso/erro de upload, reprocessamento e cancelamento — assíncrono, não bloqueia a navegação. `role="alert"`/`aria-live="assertive"` para erro, `role="status"`/`aria-live="polite"` para sucesso/aviso (acessibilidade — leitores de tela anunciam o toast sem exigir foco).
- **`Modal`** (`components/ui/Modal.tsx`): confirmação antes de reprocessar (gera nova versão dos dados) e antes de cancelar. Foca o título ao abrir e fecha com Esc — verificado no navegador via Playwright (seção 30).
- **`FileUpload`** (`components/ui/FileUpload.tsx`): drag-and-drop com seleção múltipla, filtra por extensão `.xlsx` no cliente (o motor valida de novo no servidor — o filtro do cliente é só conveniência de UX, nunca a única barreira).
- **`ProgressBar`** (`components/ui/ProgressBar.tsx`): progresso real de envio (não uma barra indeterminada) — ver seção 27 sobre o uso de `XMLHttpRequest.upload.onprogress`.

Um quinto componente novo, **`Paginacao`** (`components/ui/Paginacao.tsx`), não estava em `DESIGN_SYSTEM.md` por nome, mas consolida a marcação de "Anterior/Próxima" que o Histórico de Importações e os Erros de Validação (dentro da mesma sprint) precisavam duas vezes — extraído antes de introduzir uma terceira cópia dentro desta própria sprint. As páginas de Clientes/Promotor (Sprints 4/5) repetem essa mesma marcação e **não foram migradas** para o componente novo nesta sprint — seria alterar telas já aprovadas fora do escopo pedido; fica registrado como oportunidade de limpeza futura.

**Invalidação automática do Dashboard**: `hooks/useImportacaoData.ts` exporta `useInvalidarAposImportacao`, chamado após upload e reprocessamento bem-sucedidos (status `CONCLUIDA`/`CONCLUIDA_COM_ERROS`, nunca após uma recusa `FALHOU` — nada mudou no banco nesse caso). Invalida as `queryKey`s `["dashboard"]` e `["clientes"]` do React Query — todos os hooks desses dois domínios já usam esse prefixo (`useDashboardData.ts`, `useClienteData.ts`), então uma única invalidação por prefixo cobre KPIs, gráficos, tabela de promotores e busca de clientes sem precisar listar cada chave individualmente.

**Competência (Ano/Mês) é opcional e vale para o lote inteiro** selecionado no momento do upload — não por arquivo individual. `CARTEIRA` e `PAINEL_AVERT` exigem competência (o conector recusa sem ela); os demais tipos ignoram o campo. Pedir a competência por arquivo individual complicaria a UX de um upload multi-arquivo sem benefício real, já que na prática um lote de exportações do mesmo mês compartilha a mesma competência.

## 30. Autoauditoria da Sprint 6: verificação no navegador e correções antes da entrega

Fluxo completo testado no navegador (backend real + arquivos `.xlsx` sintéticos gerados com as mesmas fixtures reais dos testes automatizados, nunca dados reais) via Playwright: drag-and-drop de múltiplos arquivos, barra de progresso real, conclusão com Toast, histórico atualizado automaticamente, detalhe com metadados/hash/tempo de processamento, reprocessamento com modal de confirmação (recusado corretamente como duplicado ao reprocessar o mesmo arquivo), upload de arquivo com estrutura não reconhecida (recusado com Toast, sem entrar no histórico), cancelamento de uma importação `PENDENTE` (criada diretamente no banco para o teste, já que o fluxo síncrono normal nunca produz esse estado) e download do relatório CSV (BOM presente, delimitador `;`, mensagem de erro correta).

Dois problemas encontrados e corrigidos antes do commit:

1. **Linhas do Histórico de Importações não eram alcançáveis por teclado.** `<tr onClick=...>` sem `role`/`tabIndex`/`onKeyDown` — um padrão já presente em `ClientesPage`/`ClienteDetalhePage` (Sprint 5) e `TabelaPromotores` (Sprint 4), mas que esta sprint, com auditoria de acessibilidade explicitamente pedida, não podia repetir sem correção pelo menos no código novo. Corrigido adicionando `role="button"`, `tabIndex={0}` e `onKeyDown` (Enter/Espaço) na tabela nova (`ImportacoesPage.tsx`) — mesmo padrão já usado em `KpiCard.tsx` para tornar um cartão clicável acessível por teclado. Verificado com Playwright: `Tab` até a primeira linha + `Enter` navega para o detalhe. As tabelas de Clientes/Promotor (fora do escopo desta sprint) não foram alteradas; ficam registradas como pendência de acessibilidade pré-existente.
2. **`duracao_segundos` nunca aparecia na resposta da API** (seção 28) — encontrado ao verificar manualmente o card de "Tempo de Processamento" no Detalhe de Importação, que mostrava sempre "—". Bug do Pydantic v2 (`@property` sem `@computed_field`), não introduzido nesta sprint mas bloqueando um requisito explícito dela — corrigido e coberto por teste de regressão.

Nenhum dos dois problemas foi apontado por feedback do usuário — ambos encontrados durante a própria verificação no navegador exigida pela sprint.

# Validação de Execução Local (pausa na evolução funcional)

## 31. Bug crítico encontrado: banco novo nascia sem as 27 UFs, quebrando toda importação de clientes

Ao preparar o projeto para ser executado por um usuário sem conhecimento técnico (`PRIMEIRO_USO.md`), a validação em um clone genuinamente limpo do repositório (sem `database/app.db`, sem `.venv`, sem `node_modules`) revelou que `alembic upgrade head` sozinho **não populava a tabela `ufs`** — nenhuma migração insere as 27 UFs brasileiras (diferente de `tipos_promotor`, que É semeado por uma migração da Sprint 3). O seed de UFs sempre existiu como script (`app/infrastructure/seeds/seed_ufs.py`), mas nunca era chamado automaticamente fora dos testes (`tests/conftest.py`) — em qualquer ambiente realmente novo (Docker de alguém rodando pela primeira vez, ou um clone limpo), a tabela `ufs` ficava vazia e **toda importação de clientes falhava** (nenhuma linha teria UF válida para resolver).

Esse bug já existia desde a Sprint 1/2 mas nunca tinha sido percebido porque todo desenvolvimento e toda demonstração até agora usaram o mesmo `database/app.db` acumulado ao longo das sprints, cujas UFs foram inseridas manualmente em algum momento da Sprint 3 (carga real de dados) — nunca através do caminho "oficial" de inicialização. Só apareceu ao testar de verdade a partir de um estado zerado, exatamente o cenário que `PRIMEIRO_USO.md` precisa garantir.

**Correção**: `backend/docker-entrypoint.sh` e `scripts/setup.sh` passaram a rodar `python -m app.infrastructure.seeds.seed_ufs` e `python -m app.infrastructure.seeds.seed_tipos_promotor` logo após `alembic upgrade head`, em toda inicialização — os dois scripts são idempotentes por design (nunca alteram registros já existentes), então rodá-los sempre é seguro e não tem custo perceptível. Validado em `EXECUCAO_LOCAL.md`: um upload real de clientes em um banco recém-criado passou de "0/3 linhas válidas" (sem a correção) para "3/3 linhas válidas" (com a correção).

## 32. Único caminho de execução documentado para o usuário final: Docker Compose

`docker-compose.yml`, `backend/Dockerfile` e `frontend/Dockerfile` já existiam desde a Sprint 0 e já cobriam migração automática, variáveis de ambiente com valores padrão (nenhum `.env` é estritamente necessário) e healthcheck do backend antes de subir o frontend — não foi necessário reescrever nada disso, só corrigir o gap de seed (seção 31) e adicionar dois scripts finos (`iniciar.sh`/`parar.sh`, raiz do repositório) que verificam pré-requisitos, sobem os containers em segundo plano, aguardam o backend responder e imprimem mensagens de sucesso/erro em português — sem essa camada, o usuário ficaria olhando para logs técnicos brutos sem saber se deu certo.

O caminho alternativo sem Docker (`scripts/setup.sh` + `dev-backend.sh`/`dev-frontend.sh`, dois terminais) continua existindo no repositório para contribuidores que forem alterar código, mas deixou de ser apresentado como opção em `README.md`/`PRIMEIRO_USO.md` — exige Python 3.12 e Node.js já instalados corretamente, uma barreira desnecessária para quem só quer usar o sistema. Consolidação para "manter apenas a forma mais simples", sem remover a ferramenta de desenvolvimento que ainda é útil internamente.

**Limitação da validação**: o ambiente onde esta preparação foi feita não tem acesso ao daemon Docker (sandbox sem `systemd`/privilégio para `dockerd`), então `docker compose up --build` não pôde ser executado literalmente aqui. Em compensação, cada comando que os containers executam internamente (migração, seeds, subir o backend, build do frontend, servir os arquivos estáticos) foi validado diretamente, na ordem exata do `docker-entrypoint.sh`, contra um clone limpo do repositório — incluindo um upload real de planilha e a verificação do Dashboard com os dados importados. Detalhes completos em `EXECUCAO_LOCAL.md`.

## 33. Segunda alternativa de execução: `iniciar-sem-docker.sh`, para quando o Docker não é uma opção viável

Um usuário real relatou não conseguir instalar o Docker Desktop ("falha na instalação"). Como a seção 32 já havia deixado o caminho manual (`scripts/setup.sh` + dois terminais) como algo só para contribuidores — sem um "único comando" equivalente ao `iniciar.sh` — criei `iniciar-sem-docker.sh`/`parar-sem-docker.sh`: mesma experiência de um comando único, mesmas mensagens/checagens, mesma correção de seeds (seção 31), mas rodando backend e frontend diretamente na máquina (sem containers), exigindo apenas Python 3.12 e Node.js já instalados. Reaproveita 100% a mesma lógica de preparação (`alembic upgrade head` + os dois seeds) já usada por `docker-entrypoint.sh` e `scripts/setup.sh` — nenhuma duplicação de regra de negócio, só orquestração.

**Bug encontrado e corrigido durante a própria validação**: a primeira versão do script iniciava o frontend com `nohup npm run dev -- ... &`, guardando `$!` (o PID do processo `npm`) em `frontend.pid`. `npm run` cria um processo filho (`vite`) com PID diferente do processo `npm` — `kill "$pid_do_npm"` em `parar-sem-docker.sh` matava apenas o `npm`, deixando o `vite` real órfão e ainda ocupando a porta 5173. Confirmado na prática: depois de "encerrar", o processo `node .../vite` continuava listado em `ps aux` e a porta continuava respondendo. Corrigido de duas formas complementares: (1) o script passou a chamar o binário `./node_modules/.bin/vite` diretamente, sem o `npm run` intermediário — elimina o processo extra, então o PID capturado já é o processo real; (2) `parar-sem-docker.sh` chama `pkill -P "$pid"` antes de `kill "$pid"`, como rede de segurança para qualquer processo-filho remanescente, mesmo que uma mudança futura reintroduza um wrapper. Validado em um clone limpo: depois da correção, `ps aux` fica vazio (nenhum `uvicorn`/`vite` remanescente) e ambas as portas voltam a responder "conexão recusada" após `./parar-sem-docker.sh`.

`PRIMEIRO_USO.md` ganhou uma seção "Alternativa: não consigo instalar ou rodar o Docker", cobrindo instalação do Python/Node e os dois comandos novos — o restante do guia (acessar, importar, Dashboard, dados salvos) é idêntico independente do caminho escolhido, então não foi duplicado.

## 34. Terceira alternativa: Windows sem Git e sem permissão de administrador (`iniciar-sem-docker.ps1`)

O mesmo usuário da seção 33 também não conseguiu instalar o Git (necessário para rodar `iniciar-sem-docker.sh`, um script `.sh`, no Windows) — perfil de usuário sem permissão de administrador, comum em máquinas corporativas. `.sh` não roda nativamente em `cmd`/PowerShell; a alternativa sem exigir nenhuma instalação adicional é escrever o equivalente em PowerShell, que já vem em qualquer Windows.

`iniciar-sem-docker.ps1`/`parar-sem-docker.ps1` replicam exatamente a mesma lógica (mesmas checagens, mesma correção de seeds, mesmo formato de mensagens) traduzida para PowerShell — nenhuma regra nova, só a terceira forma de orquestrar os mesmos comandos. `PRIMEIRO_USO.md` documenta como instalar Python e Node.js **sem administrador**: Python via "Customize installation" → desmarcar "Install for all users"; Node.js via download `.zip` portátil (sem instalador), extraído numa pasta do próprio usuário e adicionado ao PATH em "Editar variáveis de ambiente da sua conta" — ambos editam apenas configuração do usuário atual, nunca exigem elevação. A política de execução de scripts do PowerShell (`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`) também usa escopo de usuário, sem administrador.

**Limitação explícita**: diferente das versões Docker e Bash (ambas validadas de ponta a ponta neste ambiente — seções 30 e 33), **a versão PowerShell não pôde ser executada em uma máquina Windows real** — este ambiente de desenvolvimento não tem Windows disponível. A revisão foi só de código, mas encontrou e corrigiu dois problemas reais antes de entregar:
1. `Start-Process` no Windows não herda de forma confiável o diretório de trabalho do processo que o chama — sem `-WorkingDirectory` explícito, o `uvicorn` não encontraria o pacote `app` (erro de import) e o `vite` não encontraria seus arquivos de configuração. Corrigido adicionando `-WorkingDirectory` explícito às duas chamadas de `Start-Process`.
2. Aplicado preventivamente o mesmo cuidado da seção 33 (processo-filho órfão sobrevivendo ao "encerrar"): `parar-sem-docker.ps1` primeiro localiza e mata processos-filho via `Get-CimInstance Win32_Process -Filter "ParentProcessId = ..."` antes de matar o processo principal — mesmo que aqui os processos sejam chamados diretamente (sem um wrapper como `npm run`), reduzindo o risco de o problema já corrigido na versão Bash se repetir de outra forma no Windows.

Peço ao usuário para reportar a mensagem exata de qualquer erro encontrado, para corrigir rapidamente — sem uma máquina Windows para testar, este é o caminho mais provável de precisar de um ajuste na prática.

## 35. Dois bugs reais encontrados na validação com o usuário no Windows

Confirmando a limitação da seção 34, a primeira execução real em Windows encontrou dois problemas, ambos corrigidos:

1. **Acentos quebravam o parser do PowerShell** (`"A cadeia de caracteres não tem o terminador"`). O Windows PowerShell 5.1 (a versão pré-instalada — diferente do PowerShell 7+) só reconhece um `.ps1` como UTF-8 se o arquivo começar com BOM; sem isso, ele lê pelo codepage ANSI do sistema, e qualquer acento (`ç`, `ã`, `ção`...) corrompe a leitura a partir daquele ponto. Os dois scripts `.ps1` foram criados sem BOM (padrão da ferramenta usada para gerá-los). Corrigido adicionando o BOM UTF-8 (`EF BB BF`) no início de `iniciar-sem-docker.ps1` e `parar-sem-docker.ps1`.
2. **Checagem de versão do Python rejeitava versões novas.** O script comparava a versão instalada contra a string exata `"3.12"` — um usuário com Python 3.14 instalado (mais novo, portanto compatível) era informado que "não encontrei o Python 3.12 instalado", mesmo tendo uma versão válida. `pyproject.toml` declara `requires-python = ">=3.12"`, sem limite superior — não há razão para recusar 3.13/3.14/etc. Corrigido em ambas as versões (`.sh` e `.ps1`) para comparar `(major, minor) >= (3, 12)` numericamente, em vez de comparar a string inteira.

Confirma o padrão desta preparação: cada canal de execução (Docker, Bash, PowerShell) só ganhou confiança real depois de alguém genuinamente tentar usá-lo do zero — a validação em sandbox (seções 30, 33) pegou a maioria dos problemas, mas não todos; o teste com o usuário real continua sendo o critério final.

## 36. Terceiro bug real no Windows: checagem de saúde via `localhost` falhava mesmo com o backend rodando

Depois dos dois problemas da seção 35 corrigidos, o mesmo usuário chegou mais longe: o backend chegou a subir com sucesso (`backend.log` mostrava `Uvicorn running on http://0.0.0.0:8000` e `Application startup complete`), mas `iniciar-sem-docker.ps1` mesmo assim reportava "O backend demorou demais para responder" depois de 60 tentativas (120 segundos) de `Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health"`.

Causa: no Windows, `localhost` resolve para `::1` (IPv6) e `127.0.0.1` (IPv4), nessa ordem de preferência. O backend, iniciado com `--host 0.0.0.0`, só escuta em IPv4 — não há nada ouvindo em `::1`. O PowerShell 5.1 usa a pilha HTTP do .NET Framework (não o .NET moderno, que implementa *Happy Eyeballs* e cairia para IPv4 automaticamente); ao tentar `::1` e ser recusado, ele não tenta o endereço IPv4 seguinte dentro da mesma chamada — a requisição simplesmente falha, de forma consistente, em **todas** as tentativas do loop, mesmo com o servidor real respondendo normalmente em `127.0.0.1:8000`. O log do processo (prova de que o servidor estava de pé) foi o que permitiu descartar "backend não subiu" e isolar o problema na checagem em si, não na inicialização.

**Correção**: as duas checagens de saúde em `iniciar-sem-docker.ps1` (backend em `/api/v1/health`, frontend na raiz) passaram a usar `http://127.0.0.1:...` explicitamente, em vez de `http://localhost:...` — remove a ambiguidade de resolução, sem depender de comportamento de fallback que o PowerShell 5.1 não tem. Aplicada a mesma troca, preventivamente, nas checagens equivalentes de `iniciar-sem-docker.sh` (`curl` normalmente já lida bem com IPv6 recusado e cai para IPv4 sozinho, então o Bash não exibiu esse sintoma na prática — mas não há motivo para depender desse comportamento implícito quando `127.0.0.1` é igualmente correto e explícito nos dois casos). A mensagem final de sucesso continua apontando `http://localhost:5173` para o usuário abrir no navegador — navegadores modernos implementam *Happy Eyeballs* corretamente e não reproduzem esse problema.

Terceiro bug seguido encontrado apenas por teste real em Windows, não por revisão de código — reforça a conclusão da seção 35.
