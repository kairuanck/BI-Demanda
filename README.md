# Promotores BI

Plataforma web de Business Intelligence para gestão de Promotores Técnicos e Promotores Trade do mercado pet.

## 1. Visão Geral

O **Promotores BI** é uma plataforma de business intelligence voltada à gestão, ao acompanhamento e à análise de desempenho de equipes de campo (Promotores Técnicos e Promotores Trade) que atuam no mercado pet, atendendo uma carteira de clientes (pet shops, clínicas veterinárias, distribuidores e demais canais).

A plataforma consolida dados historicamente dispersos em planilhas Excel — base de clientes, carteira de promotores, faturamento mensal, checklists de visita e registros de visitas — em um repositório único, versionado, auditável e consultável através de dashboards executivos e dashboards individuais por promotor.

Este repositório contém, nesta primeira fase, a **documentação completa de arquitetura, modelagem, backend, frontend, dados, testes e execução em sprints** do projeto. A implementação de código é realizada posteriormente, sprint a sprint, por meio do Claude Code, utilizando os documentos aqui produzidos como especificação de referência.

## 2. Natureza do Projeto

Este projeto é conduzido em duas fases:

1. **Fase de Documentação (atual)** — produção de toda a especificação técnica e de produto necessária para a construção do sistema, sem escrita de código de aplicação.
2. **Fase de Implementação (Sprints 00 a 12)** — execução, pelo Claude Code, das tarefas descritas em `SPRINT_00.md` a `SPRINT_12.md`, utilizando os prompts consolidados em `PROMPTS.md` e `MASTER_PROMPT.md`.

A POC (Proof of Concept) resultante é desenhada desde o início para evoluir para um produto **SaaS multi-tenant**, conforme descrito em `TUTORIAL.md` (seção 14).

## 3. Stack Tecnológica

### Backend
- **FastAPI** — framework web assíncrono para a API REST.
- **Python 3.11+** — linguagem da aplicação backend.
- **SQLAlchemy 2.x** — ORM e camada de acesso a dados.
- **Alembic** — controle de migrações de schema.
- **SQLite** — banco de dados da POC, com modelagem 100% compatível com **PostgreSQL** para evolução futura sem retrabalho.

### Frontend
- **React 18** — biblioteca de construção de interface.
- **Vite** — build tool e dev server.
- **Chart.js** — biblioteca de gráficos dos dashboards.
- **TailwindCSS** — framework de estilos utilitários e design system.

### Importação de Dados
- **Pandas** — leitura, tratamento e transformação de planilhas.
- **OpenPyXL** — leitura/escrita de arquivos `.xlsx`.

### Autenticação e Segurança
- **JWT (JSON Web Token)** — autenticação stateless da API.
- **bcrypt** — hashing de senhas.

### Controle de Versão
- **Git** e **GitHub** — versionamento de código e documentação, fluxo de branches e Pull Requests.

## 4. Perfis de Usuário

| Perfil | Descrição resumida |
|---|---|
| Administrador | Acesso total: usuários, importações, configurações, auditoria. |
| Supervisor | Gestão da equipe de promotores sob sua supervisão; dashboards da equipe. |
| Promotor | Acesso ao próprio dashboard, própria carteira e próprias visitas/checklists. |
| Diretoria | Visão executiva consolidada, somente leitura, sem acesso operacional. |

Detalhamento completo em `PERMISSOES.md`.

## 5. Funcionalidades Principais

- Autenticação e controle de usuários por perfil.
- Importação manual de planilhas Excel, com versionamento, detecção de duplicidade (hash SHA256), histórico completo e rollback.
- Dashboard Executivo (visão consolidada da operação).
- Dashboard por Promotor (visão individual de carteira, visitas, checklists e cobertura).
- KPIs: Carteira, Região, Fora da Carteira, Visitas, Checklists, Cobertura, Positivação e Ranking.
- Filtros por Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor e Tipo de Promotor.
- Exportação de dados em Excel, CSV e PDF.
- Auditoria completa de ações e importações.

Detalhamento funcional completo em `PROJECT.md`, `DASHBOARD.md`, `KPIS.md` e `TELAS.md`.

## 6. Arquitetura

O backend segue **Clean Architecture**, princípios **SOLID**, **Repository Pattern**, **Service Layer** e **Injeção de Dependência**, com tipagem completa (type hints) em todo o código Python. Detalhes em `BACKEND.md`.

O frontend segue arquitetura por features, com design system próprio documentado em `DESIGN_SYSTEM.md` e componentização detalhada em `FRONTEND.md`.

## 7. Estrutura da Documentação

Toda a documentação do projeto está listada, em ordem de leitura recomendada, em `SPEC_INDEX.md`. Os documentos estão organizados nos seguintes grupos:

1. **Visão e Governança do Projeto** — `PROJECT.md`, `MASTER_PROMPT.md`, `ROADMAP.md`, `PROMPTS.md`.
2. **Dados** — `DATABASE.md`, `MODELAGEM.md`, `DER.md`, `DICIONARIO_DE_DADOS.md`, `REGRAS_DE_NEGOCIO.md`.
3. **Importação de Dados** — `ETL.md`, `IMPORTADOR.md`, `VALIDADOR.md`, `HASH.md`, `LOGS.md`.
4. **Backend** — `BACKEND.md`, `API.md`, `AUTENTICACAO.md`, `PERMISSOES.md`.
5. **Frontend** — `FRONTEND.md`, `DESIGN_SYSTEM.md`, `TELAS.md`, `UX.md`.
6. **Business Intelligence** — `DASHBOARD.md`, `KPIS.md`, `GRAFICOS.md`.
7. **Qualidade e Operação** — `TESTES.md`, `AUDITORIA.md`, `DEPLOY.md`, `GITHUB.md`.
8. **Execução** — `SPRINT_00.md` a `SPRINT_12.md`.
9. **Índice** — `SPEC_INDEX.md`.
10. **Tutorial Operacional** — `TUTORIAL.md`.

## 8. Estrutura de Pastas do Repositório (alvo, pós-Sprint 00)

```
Pedidos-redes/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── styles/
│   ├── public/
│   └── package.json
├── docs/            (opcional — os .md também podem permanecer na raiz)
├── .github/
│   └── workflows/
├── README.md
└── ... (demais arquivos .md desta documentação)
```

A estrutura definitiva e o detalhamento pasta a pasta estão em `BACKEND.md` (seção de estrutura de diretórios) e `FRONTEND.md` (seção de estrutura de diretórios).

## 9. Como Começar

O passo a passo completo — criação do repositório, upload da documentação, instalação do Claude Code, execução da Sprint 0 em diante, revisão de PRs, validação de testes, importação de planilhas e publicação — está descrito integralmente em `TUTORIAL.md`.

## 10. Licença e Uso

Projeto de uso interno / POC. Definição formal de licença de software é uma decisão de negócio a ser tomada antes da publicação como produto SaaS (ver `TUTORIAL.md`, seção 14).
