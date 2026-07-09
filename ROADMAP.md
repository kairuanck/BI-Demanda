# ROADMAP.md — Roteiro de Execução do Projeto

## 1. Visão Geral

O projeto Promotores BI é executado em duas macro-fases:

- **Fase 0 — Documentação** (concluída neste repositório): produção de todos os documentos listados em `SPEC_INDEX.md`.
- **Fase 1 — Implementação da POC**: execução das Sprints 00 a 12, descritas individualmente em `SPRINT_00.md` a `SPRINT_12.md`.

Após a Fase 1, o projeto está apto às fases de evolução descritas na seção 5 deste documento e detalhadas operacionalmente em `TUTORIAL.md`.

## 2. Linha do Tempo das Sprints

| Sprint | Nome | Foco Principal | Depende de |
|---|---|---|---|
| 00 | Fundação do Projeto | Estrutura de repositório, backend e frontend inicializados, tooling, CI básico | — |
| 01 | Modelagem de Dados e Migrations | Modelos SQLAlchemy, Alembic, seeds de UF/Cidade | Sprint 00 |
| 02 | Autenticação e Usuários | JWT, bcrypt, CRUD de usuários, RBAC | Sprint 01 |
| 03 | Motor de Importação Base | Hash SHA256, versionamento, upload genérico, rollback | Sprint 01, 02 |
| 04 | Importador de Clientes | Parser e regras da Base de Clientes | Sprint 03 |
| 05 | Importador de Carteira | Parser e regras da Carteira dos Promotores | Sprint 04 |
| 06 | Importador de Faturamento | Parser e regras do Faturamento Mensal | Sprint 04 |
| 07 | Importador de Visitas e Checklists | Parsers de Visitas e Checklists | Sprint 05 |
| 08 | API de KPIs e Regras de Negócio | Serviços de cálculo de KPIs, endpoints de dashboard | Sprint 05, 06, 07 |
| 09 | Frontend Base e Design System | Scaffold React/Vite/Tailwind, autenticação no frontend, layout | Sprint 02 |
| 10 | Dashboards | Dashboard Executivo e Dashboard por Promotor, gráficos Chart.js | Sprint 08, 09 |
| 11 | Importação (Frontend), Exportações e Auditoria UI | Telas de upload, histórico, rollback, exportações, auditoria | Sprint 03–07, 09 |
| 12 | Testes, Auditoria Final, Deploy e Hardening | Cobertura de testes, CI/CD, guia de deploy, checklist final | Todas anteriores |

## 3. Marcos (Milestones)

| Marco | Sprints associadas | Critério de conclusão |
|---|---|---|
| M1 — Base Técnica Pronta | 00, 01, 02 | Backend inicializado, banco modelado, autenticação funcionando |
| M2 — Motor de Dados Completo | 03, 04, 05, 06, 07 | Todas as 5 planilhas importáveis, versionadas e auditadas |
| M3 — Inteligência de Negócio Pronta | 08 | Todos os KPIs calculáveis via API, com filtros completos |
| M4 — Experiência do Usuário Pronta | 09, 10, 11 | Frontend completo, dashboards, importação e exportação operacionais |
| M5 — POC Pronta para Publicação | 12 | Testes, auditoria, deploy e documentação de operação finalizados |

## 4. Dependências Críticas entre Sprints

```
Sprint 00 ──► Sprint 01 ──► Sprint 02 ──► Sprint 03 ──┬──► Sprint 04 ──┬──► Sprint 05 ──► Sprint 08 ──► Sprint 10 ──► Sprint 12
                                                        │                ├──► Sprint 06 ──► Sprint 08
                                                        │                └──► Sprint 07 ──► Sprint 08
                                                        └──► Sprint 09 ──► Sprint 10 ──► Sprint 11 ──► Sprint 12
```

## 5. Roadmap Pós-POC (fora do escopo de implementação desta documentação, referência estratégica)

Estes itens **não** fazem parte das Sprints 00–12, mas orientam decisões arquiteturais tomadas ao longo da documentação (ex.: compatibilidade SQLite/PostgreSQL, isolamento de camadas), de modo que a evolução abaixo não exija reescrita:

1. **Migração de SQLite para PostgreSQL** em ambiente produtivo (detalhado em `DEPLOY.md` e `TUTORIAL.md`, seção 13).
2. **Evolução para SaaS multi-tenant**, com introdução de `tenant_id` nas tabelas principais e isolamento lógico de dados por cliente contratante (`TUTORIAL.md`, seção 14).
3. **Importação automatizada** via API/EDI com ERPs de clientes, substituindo/complementando a importação manual de planilhas.
4. **Aplicativo mobile de campo** para registro de visitas e checklists em tempo real, substituindo o fluxo de digitação em planilha.
5. **Faturamento e billing do SaaS** (planos, cobrança recorrente).
6. **Internacionalização** (i18n) da interface, caso o produto seja comercializado fora do Brasil.

## 6. Regras de Progressão entre Sprints

1. Nenhuma Sprint é iniciada antes de suas dependências (coluna "Depende de" da seção 2) estarem com Definition of Done cumprida (`MASTER_PROMPT.md`, seção 6).
2. A ordem numérica das Sprints é a ordem de execução padrão; alterações de ordem só são permitidas se não violarem o grafo de dependências da seção 4.
3. Cada Sprint concluída gera um Pull Request próprio, revisado conforme `GITHUB.md`.
