# SPRINT_12.md — Testes, Auditoria Final, Deploy e Hardening

## 1. Objetivo

Completar a cobertura de testes automatizados de backend e frontend às metas finais, executar um checklist de auditoria e segurança de ponta a ponta, finalizar o pipeline de CI/CD, validar o guia de publicação e produzir um relatório consolidado do estado final da POC.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `TESTES.md`, `AUDITORIA.md`, `DEPLOY.md`, `GITHUB.md`, todos os demais documentos como referência de verificação cruzada.

## 3. Pré-condições

Sprints 00 a 11 concluídas — esta é a última Sprint da POC.

## 4. Escopo (Backlog Detalhado)

### 4.1 Consolidação de Testes
1. Elevar a cobertura de backend ao mínimo de 80% geral / 90% em `services/importacao/` e `kpi_service.py` (`TESTES.md`, seção 7), preenchendo lacunas identificadas por `pytest-cov`.
2. Elevar a cobertura de frontend ao mínimo de 75% geral (`TESTES.md`, seção 7).
3. Implementar a suíte de testes end-to-end (`tests/e2e/`) descrita em `TESTES.md`, seção 4.3: fluxo completo de importação até dashboard e exportação; fluxo de controle de acesso negado; fluxo de rollback.
4. Garantir que os 4 testes de regressão de regras de negócio críticas (`TESTES.md`, seção 10) estão implementados e permanentemente presentes na suíte.

### 4.2 Hardening de Segurança
1. Revisar `CORS_ALLOWED_ORIGINS`, garantindo que não há valor coringa (`*`) em configuração de exemplo de produção (`DEPLOY.md`, seção 12).
2. Revisar que nenhum segredo está commitado no histórico do repositório (varredura de `git log` e `git grep` por padrões de chave/senha).
3. Revisar que todas as rotas protegidas exigem autenticação e autorização corretas, executando a suíte completa de `PERMISSOES.md` contra os 4 perfis em todos os endpoints de `API.md`.
4. Validar rate limiting de login (`AUTENTICACAO.md`, seção 9, item 1) sob teste de carga simples.
5. Executar varredura de dependências (`pip-audit` para backend, `npm audit` para frontend), corrigindo vulnerabilidades de severidade alta/crítica encontradas.

### 4.3 Auditoria Final
1. Validar, um a um, os eventos obrigatórios de `AUDITORIA.md`, seção 3, confirmando geração correta em ambiente de teste integrado.
2. Validar que nenhum dado sensível (senha, token completo) aparece em `logs_auditoria` ou em log técnico (`AUDITORIA.md`, seção 6; `LOGS.md`, seção 8).

### 4.4 CI/CD e Deploy
1. Finalizar `.github/workflows/ci.yml` com todas as etapas de `GITHUB.md`, seção 6, aplicáveis.
2. Criar `backend/Dockerfile` e, se aplicável, `frontend/Dockerfile` (ou pipeline de build estático), conforme `DEPLOY.md`, seção 8.
3. Executar o checklist de publicação completo de `DEPLOY.md`, seção 13, em um ambiente de demonstração real.
4. Validar a migração de SQLite para PostgreSQL (`DEPLOY.md`, seção 9) em um ambiente de teste, confirmando que `alembic upgrade head` se aplica sem alteração de código.

### 4.5 Relatório Final da POC
1. Produzir um relatório consolidado (`RELATORIO_FINAL_POC.md`, criado nesta Sprint como artefato de encerramento, fora da lista fixa de documentos de especificação) contendo: status de cada critério de sucesso de `PROJECT.md`, seção 10; cobertura de testes final; lista de eventuais desvios ou premissas adicionais adotadas durante a implementação (`MASTER_PROMPT.md`, seção 8).

## 5. Fora de Escopo desta Sprint

1. Qualquer nova funcionalidade de negócio não prevista nas Sprints 00 a 11.
2. Itens do Roadmap Pós-POC (`ROADMAP.md`, seção 5): multi-tenant, integração automática com ERP, aplicativo mobile, billing.

## 6. Entregáveis

1. Suítes de teste (unitária, integração, E2E) completas, atingindo as metas finais de cobertura.
2. Checklist de segurança executado e documentado, sem pendência de severidade alta/crítica em aberto.
3. Pipeline de CI/CD completo e verde.
4. Ambiente de demonstração publicado e validado contra o checklist de `DEPLOY.md`, seção 13.
5. `RELATORIO_FINAL_POC.md`.

## 7. Critérios de Aceite

1. Cobertura de backend ≥ 80% geral, ≥ 90% em `services/importacao/` e `kpi_service.py`, medida por `pytest-cov` no pipeline de CI.
2. Cobertura de frontend ≥ 75% geral, medida por `vitest --coverage` no pipeline de CI.
3. Suíte E2E completa passando de ponta a ponta em ambiente de CI.
4. Todos os 7 critérios de sucesso da POC listados em `PROJECT.md`, seção 10, estão marcados como atendidos no `RELATORIO_FINAL_POC.md`, com evidência (link de teste ou captura) para cada um.
5. `pip-audit`/`npm audit` sem vulnerabilidade de severidade alta/crítica sem tratamento documentado.
6. Ambiente de demonstração publicado responde corretamente ao checklist de `DEPLOY.md`, seção 13, item a item.
7. Migração de teste para PostgreSQL concluída com sucesso, sem qualquer alteração de código de aplicação além da variável `DATABASE_URL`.

## 8. Riscos e Observações

1. Esta é a Sprint de encerramento da POC (marco M5 do `ROADMAP.md`). Qualquer desvio identificado nesta Sprint entre o comportamento implementado e a documentação de especificação deve ser corrigido no código (não na documentação retroativamente), preservando a documentação como fonte da verdade — exceto quando o próprio Product Owner decidir formalmente alterar uma regra, caso em que o documento correspondente deve ser atualizado em um commit `docs` específico, revisado como qualquer outra mudança de especificação.
