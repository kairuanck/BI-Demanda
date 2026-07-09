# SPEC_INDEX.md — Índice Mestre da Documentação

## 1. Finalidade

Este documento é o índice completo e a ordem de leitura recomendada de toda a documentação do projeto Promotores BI. É o último documento de especificação produzido, servindo como mapa de navegação para qualquer pessoa ou para o Claude Code antes de iniciar a implementação (`MASTER_PROMPT.md`, seção 4).

## 2. Visão Geral por Grupo

| # | Documento | Grupo | Resumo em uma linha |
|---|---|---|---|
| 1 | `README.md` | Visão e Governança | Visão geral do produto, stack e estrutura do repositório. |
| 2 | `PROJECT.md` | Visão e Governança | Contexto de negócio, personas, funcionalidades, premissas e critérios de sucesso. |
| 3 | `MASTER_PROMPT.md` | Visão e Governança | Prompt mestre e regras invioláveis para o Claude Code. |
| 4 | `ROADMAP.md` | Visão e Governança | Linha do tempo, marcos e dependências entre Sprints. |
| 5 | `PROMPTS.md` | Visão e Governança | Prompts operacionais prontos, um por Sprint. |
| 6 | `DATABASE.md` | Dados | Estratégia de banco de dados e compatibilidade SQLite/PostgreSQL. |
| 7 | `MODELAGEM.md` | Dados | Modelagem conceitual das 19 entidades e relacionamentos. |
| 8 | `DER.md` | Dados | Diagrama entidade-relacionamento (Mermaid). |
| 9 | `DICIONARIO_DE_DADOS.md` | Dados | Especificação física completa de todas as tabelas e colunas. |
| 10 | `REGRAS_DE_NEGOCIO.md` | Dados | Regras de versionamento, importação, rollback e consistência. |
| 11 | `ETL.md` | Importação | Pipeline ETL genérico de 7 etapas. |
| 12 | `IMPORTADOR.md` | Importação | Layout e regras específicas dos 5 importadores. |
| 13 | `VALIDADOR.md` | Importação | Regras de validação linha a linha, por código. |
| 14 | `HASH.md` | Importação | Estratégia de hash SHA-256 e versionamento de arquivos. |
| 15 | `LOGS.md` | Importação | Estratégia de log técnico de execução. |
| 16 | `BACKEND.md` | Backend | Clean Architecture, SOLID, estrutura de diretórios. |
| 17 | `API.md` | Backend | Especificação completa de todos os endpoints REST. |
| 18 | `AUTENTICACAO.md` | Backend | Fluxo JWT/bcrypt completo. |
| 19 | `PERMISSOES.md` | Backend | Matriz RBAC por perfil e escopo de dados. |
| 20 | `FRONTEND.md` | Frontend | Arquitetura React/Vite, estrutura de diretórios. |
| 21 | `DESIGN_SYSTEM.md` | Frontend | Tokens visuais e inventário de componentes. |
| 22 | `TELAS.md` | Frontend | Especificação de todas as telas da aplicação. |
| 23 | `UX.md` | Frontend | Fluxos de navegação e interação por persona. |
| 24 | `DASHBOARD.md` | Business Intelligence | Composição dos dois dashboards e formato de resposta. |
| 25 | `KPIS.md` | Business Intelligence | Fórmulas precisas dos 8 KPIs. |
| 26 | `GRAFICOS.md` | Business Intelligence | Tipos de gráfico Chart.js e mapeamento por KPI. |
| 27 | `TESTES.md` | Qualidade e Operação | Estratégia e metas de cobertura de testes. |
| 28 | `AUDITORIA.md` | Qualidade e Operação | Eventos e estrutura da trilha de auditoria de negócio. |
| 29 | `DEPLOY.md` | Qualidade e Operação | Execução local, publicação e migração para PostgreSQL. |
| 30 | `GITHUB.md` | Qualidade e Operação | Fluxo de branches, commits, PRs e CI/CD. |
| 31 | `SPRINT_00.md` | Execução | Fundação do projeto. |
| 32 | `SPRINT_01.md` | Execução | Modelagem de dados e migrations. |
| 33 | `SPRINT_02.md` | Execução | Autenticação e usuários. |
| 34 | `SPRINT_03.md` | Execução | Motor de importação base. |
| 35 | `SPRINT_04.md` | Execução | Importador de Clientes. |
| 36 | `SPRINT_05.md` | Execução | Importador de Carteira. |
| 37 | `SPRINT_06.md` | Execução | Importador de Faturamento. |
| 38 | `SPRINT_07.md` | Execução | Importador de Visitas e Checklists. |
| 39 | `SPRINT_08.md` | Execução | API de KPIs e regras de negócio. |
| 40 | `SPRINT_09.md` | Execução | Frontend base e design system. |
| 41 | `SPRINT_10.md` | Execução | Dashboards. |
| 42 | `SPRINT_11.md` | Execução | Importação (frontend), exportações e auditoria UI. |
| 43 | `SPRINT_12.md` | Execução | Testes, auditoria final, deploy e hardening. |
| 44 | `SPEC_INDEX.md` | Índice | Este documento. |

Documento adicional de encerramento da fase de documentação: `TUTORIAL.md` (guia operacional de 14 passos, do zero à evolução para SaaS).

## 3. Ordem de Leitura Recomendada (Primeira Leitura Integral)

1. `README.md`
2. `PROJECT.md`
3. `MASTER_PROMPT.md`
4. `ROADMAP.md`
5. `DATABASE.md` → `MODELAGEM.md` → `DER.md` → `DICIONARIO_DE_DADOS.md` → `REGRAS_DE_NEGOCIO.md`
6. `ETL.md` → `IMPORTADOR.md` → `VALIDADOR.md` → `HASH.md` → `LOGS.md`
7. `BACKEND.md` → `API.md` → `AUTENTICACAO.md` → `PERMISSOES.md`
8. `FRONTEND.md` → `DESIGN_SYSTEM.md` → `TELAS.md` → `UX.md`
9. `DASHBOARD.md` → `KPIS.md` → `GRAFICOS.md`
10. `TESTES.md` → `AUDITORIA.md` → `DEPLOY.md` → `GITHUB.md`
11. `PROMPTS.md` (revisitado após o entendimento completo do restante)
12. `SPRINT_00.md` a `SPRINT_12.md`, em ordem
13. `TUTORIAL.md`

## 4. Mapa de Dependência de Leitura por Sprint

Esta tabela replica, para consulta rápida, os "Documentos de Referência Obrigatórios" de cada Sprint (já listados individualmente em cada `SPRINT_XX.md`, seção 2):

| Sprint | Documentos de Referência Obrigatórios |
|---|---|
| 00 | MASTER_PROMPT, BACKEND, FRONTEND, GITHUB, DEPLOY |
| 01 | MASTER_PROMPT, DATABASE, MODELAGEM, DER, DICIONARIO_DE_DADOS, BACKEND |
| 02 | MASTER_PROMPT, AUTENTICACAO, PERMISSOES, API, BACKEND |
| 03 | MASTER_PROMPT, ETL, IMPORTADOR, VALIDADOR, HASH, LOGS, BACKEND |
| 04 | MASTER_PROMPT, IMPORTADOR, VALIDADOR, REGRAS_DE_NEGOCIO, DICIONARIO_DE_DADOS |
| 05 | MASTER_PROMPT, IMPORTADOR, VALIDADOR, REGRAS_DE_NEGOCIO, DICIONARIO_DE_DADOS |
| 06 | MASTER_PROMPT, IMPORTADOR, VALIDADOR, REGRAS_DE_NEGOCIO, DICIONARIO_DE_DADOS |
| 07 | MASTER_PROMPT, IMPORTADOR, VALIDADOR, REGRAS_DE_NEGOCIO, DICIONARIO_DE_DADOS |
| 08 | MASTER_PROMPT, KPIS, REGRAS_DE_NEGOCIO, DASHBOARD, API, PERMISSOES |
| 09 | MASTER_PROMPT, FRONTEND, DESIGN_SYSTEM, UX, TELAS, API |
| 10 | MASTER_PROMPT, DASHBOARD, KPIS, GRAFICOS, TELAS, UX |
| 11 | MASTER_PROMPT, TELAS, UX, AUDITORIA, API |
| 12 | MASTER_PROMPT, TESTES, AUDITORIA, DEPLOY, GITHUB |

## 5. Rastreabilidade Funcionalidade → Documentos

| Funcionalidade (`README.md`, seção 5) | Documentos que a especificam |
|---|---|
| Login / Controle de usuários | `AUTENTICACAO.md`, `PERMISSOES.md`, `API.md`, `TELAS.md` |
| Importação manual de Excel, versionamento, duplicidade, histórico | `ETL.md`, `IMPORTADOR.md`, `VALIDADOR.md`, `HASH.md`, `REGRAS_DE_NEGOCIO.md` |
| Dashboard Executivo / Dashboard por Promotor | `DASHBOARD.md`, `GRAFICOS.md`, `TELAS.md`, `UX.md` |
| KPIs (Carteira, Região, Fora da Carteira, Visitas, Checklists, Cobertura, Positivação, Ranking) | `KPIS.md`, `REGRAS_DE_NEGOCIO.md` |
| Filtros (Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor) | `API.md` (seção 3), `DASHBOARD.md`, `DESIGN_SYSTEM.md` (seção 8) |
| Exportação (Excel, CSV, PDF) | `API.md` (seção 12), `FRONTEND.md` (seção 8), `TELAS.md` (seção 16) |

## 6. Convenções Transversais

1. Todos os documentos utilizam Português do Brasil (`PROJECT.md`, seção 9, premissa 1).
2. Toda referência cruzada entre documentos utiliza o nome exato do arquivo `.md` entre crases, permitindo navegação direta no GitHub.
3. Nenhum documento desta lista contém código de implementação — apenas especificação, conforme instrução de condução do projeto.
4. Toda alteração retroativa a um documento já "congelado" (produzido em uma entrega anterior) deve ser feita como um commit `docs` explícito e revisado, nunca silenciosamente durante a implementação de uma Sprint (`SPRINT_12.md`, seção 8).

## 7. Status da Documentação

Todos os 44 documentos listados na seção 2, mais `TUTORIAL.md`, estão concluídos e íntegros neste repositório, na branch `claude/promotores-bi-docs-ieimki`. A fase de documentação (`ROADMAP.md`, seção 1, Fase 0) está encerrada. A implementação (Fase 1) inicia pela Sprint 00, conforme `PROMPTS.md`, seção 2.
