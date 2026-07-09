# SPRINT_01.md — Modelagem de Dados e Migrations

## 1. Objetivo

Implementar todos os modelos SQLAlchemy correspondentes às 19 tabelas do modelo de dados, configurar Alembic e gerar a migração inicial, além dos scripts de seed de dados de referência (UFs) e dados mínimos de teste.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `DATABASE.md`, `MODELAGEM.md`, `DER.md`, `DICIONARIO_DE_DADOS.md`, `BACKEND.md` (seção 4, camada `infrastructure/models/`).

## 3. Pré-condições

Sprint 00 concluída (backend executável, tooling configurado).

## 4. Escopo (Backlog Detalhado)

### 4.1 Infraestrutura de Banco
1. Implementar `app/infrastructure/database.py`: criação do `Engine` (SQLite por padrão, PostgreSQL via `DATABASE_URL`), `SessionLocal`, `Base` declarativa, ativação de `PRAGMA foreign_keys=ON` para SQLite (`DATABASE.md`, seção 3, item 7).
2. Atualizar `GET /api/v1/health` para incluir verificação real de conectividade com o banco (`SELECT 1`).

### 4.2 Modelos SQLAlchemy (`app/infrastructure/models/`)
Implementar, um módulo por tabela, todos os 19 modelos com tipagem completa, exatamente conforme `DICIONARIO_DE_DADOS.md`:
1. `usuario_model.py` (`usuarios`)
2. `supervisor_model.py` (`supervisores`)
3. `promotor_model.py` (`promotores`)
4. `vendedor_model.py` (`vendedores`)
5. `laboratorio_model.py` (`laboratorios`)
6. `departamento_model.py` (`departamentos`)
7. `uf_model.py` (`ufs`)
8. `cidade_model.py` (`cidades`)
9. `cliente_model.py` (`clientes`)
10. `carteira_model.py` (`carteiras`)
11. `faturamento_model.py` (`faturamentos`)
12. `visita_model.py` (`visitas`)
13. `checklist_model.py` (`checklists`)
14. `checklist_pergunta_model.py` (`checklist_perguntas`)
15. `checklist_resposta_model.py` (`checklist_respostas`)
16. `importacao_model.py` (`importacoes`)
17. `importacao_erro_model.py` (`importacao_erros`)
18. `importacao_arquivo_model.py` (`importacao_arquivos`)
19. `log_auditoria_model.py` (`logs_auditoria`)

Todos os Enums do sistema (`DICIONARIO_DE_DADOS.md`, seção 21) implementados em `app/domain/enums/`, reutilizados pelos modelos.

### 4.3 Entidades de Domínio
1. Implementar as `dataclasses` de entidade de negócio em `app/domain/entidades/`, espelhando os campos relevantes de cada modelo, desacopladas do SQLAlchemy (`BACKEND.md`, seção 2, item 1).

### 4.4 Migrations
1. Configurar `alembic.ini` e `alembic/env.py` para carregar `Base.metadata` dos modelos e ler `DATABASE_URL` de `app/core/config.py`.
2. Gerar a migração inicial via `alembic revision --autogenerate -m "modelagem inicial completa"`, revisar manualmente o arquivo gerado (`DATABASE.md`, seção 4, item 1) e ajustar `ondelete` de todas as chaves estrangeiras conforme `DICIONARIO_DE_DADOS.md`.
3. Validar `alembic upgrade head` a partir de um banco SQLite vazio.
4. Validar `alembic downgrade base` seguido de `alembic upgrade head` novamente, garantindo reversibilidade da migração inicial.

### 4.5 Repositórios (Camada Mínima)
1. Implementar os contratos (`Protocol`) de cada repositório em `app/domain/contratos/`.
2. Implementar as classes concretas `SqlAlchemy<Entidade>Repository` em `app/repositories/`, com métodos básicos de CRUD (`obter_por_id`, `listar`, `criar`, `atualizar`) para cada uma das 19 entidades — sem ainda expor via API (isso ocorre em Sprints específicas de cada funcionalidade).

### 4.6 Seeds
1. Implementar script `app/infrastructure/seeds/seed_ufs.py`, populando a tabela `ufs` com as 27 UFs brasileiras e suas respectivas regiões, executável via comando único (`python -m app.infrastructure.seeds.seed_ufs`).

## 5. Fora de Escopo desta Sprint

1. Endpoints de API para qualquer entidade — Sprints 02 em diante.
2. Regras de negócio de versionamento (`REGRAS_DE_NEGOCIO.md`) — Sprints 03 a 07.
3. Cálculo de KPIs — Sprint 08.

## 6. Entregáveis

1. 19 modelos SQLAlchemy implementados, tipados, correspondentes exatamente a `DICIONARIO_DE_DADOS.md`.
2. Migração Alembic inicial, aplicável e reversível.
3. Repositórios básicos das 19 entidades.
4. Script de seed de UFs.
5. Testes de integração de repositórios (`TESTES.md`, seção 4.2) cobrindo criação, leitura e restrições de integridade referencial das 19 tabelas.

## 7. Critérios de Aceite

1. `alembic upgrade head` aplica-se com sucesso a partir de um banco SQLite vazio, criando exatamente as 19 tabelas descritas em `DICIONARIO_DE_DADOS.md`, com todos os índices e restrições especificados.
2. Inserção de um registro em cada tabela via repositório, respeitando `NOT NULL`/`UNIQUE`/`FOREIGN KEY`, é coberta por teste de integração passando.
3. Tentativa de violar uma restrição de integridade referencial (ex.: `cidade_id` inexistente em `clientes`) resulta em exceção capturada e testada.
4. Script de seed de UFs povoa corretamente as 27 UFs com suas regiões.
5. `mypy` não aponta erro de tipagem nos módulos criados.
6. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. A revisão manual da migração autogerada (item 4.2 da seção 4.4) é obrigatória — o Alembic pode nem sempre inferir corretamente `ondelete` e restrições compostas a partir da introspecção automática; a fonte da verdade final é sempre `DICIONARIO_DE_DADOS.md`, não a saída padrão do `autogenerate`.
