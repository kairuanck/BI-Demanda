# SPRINT_08.md — API de KPIs e Regras de Negócio

## 1. Objetivo

Implementar a camada de serviço de cálculo de todos os 8 KPIs do sistema e os endpoints de dashboard e KPI, com suporte completo aos 10 filtros definidos em `API.md`, seção 3, consolidando toda a inteligência analítica do backend.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `KPIS.md`, `REGRAS_DE_NEGOCIO.md`, `DASHBOARD.md`, `API.md` (seções 3 e 10), `PERMISSOES.md`.

## 3. Pré-condições

Sprints 04, 05, 06 e 07 concluídas (todos os importadores disponíveis, dados de teste importáveis para validar os cálculos).

## 4. Escopo (Backlog Detalhado)

### 4.1 Infraestrutura de Filtros
1. Implementar `app/api/schemas/filtros_schema.py`: schema Pydantic único de filtros (Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor), reutilizado por todos os endpoints de KPI e dashboard.
2. Implementar `app/services/escopo_service.py`: aplica automaticamente as restrições de escopo por perfil (`PERMISSOES.md`, seção 4) sobre o schema de filtros recebido, antes de repassar aos serviços de KPI, incluindo a rejeição (`403`) de filtros que extrapolem o escopo do usuário autenticado (`PERMISSOES.md`, seção 4.2, item 2, e seção 4.3, item 2).

### 4.2 Serviço de KPIs
Implementar `app/services/kpi_service.py`, com um método por KPI, cada um implementando exatamente a fórmula correspondente de `KPIS.md`:
1. `calcular_carteira(filtros)` — `KPIS.md`, seção 3.
2. `calcular_regiao(filtros)` — `KPIS.md`, seção 4.
3. `calcular_fora_da_carteira(filtros)` — `KPIS.md`, seção 5, incluindo o retorno `null` quando filtros incompatíveis são aplicados (Promotor/Supervisor/Tipo de Promotor).
4. `calcular_visitas(filtros)` — `KPIS.md`, seção 6.
5. `calcular_checklists(filtros)` — `KPIS.md`, seção 7.
6. `calcular_cobertura(filtros)` — `KPIS.md`, seção 8.
7. `calcular_positivacao(filtros)` — `KPIS.md`, seção 9.
8. `calcular_ranking(filtros)` — `KPIS.md`, seção 10, incluindo ranking geral e por Tipo de Promotor, com a fórmula de índice combinado e regras de desempate.

Todas as consultas agregadas reutilizam o utilitário de "versão corrente" implementado na Sprint 06 (`SPRINT_06.md`, seção 4.4).

### 4.3 Serviço de Dashboard
1. Implementar `app/services/dashboard_service.py`: `montar_dashboard_executivo(filtros)` e `montar_dashboard_promotor(promotor_id, filtros)`, compondo as estruturas de resposta exatamente conforme `DASHBOARD.md`, seções 2.5 e 3.4, orquestrando chamadas a `kpi_service.py` e consultas agregadas adicionais (faturamento por região/departamento, evolução mensal).
2. Implementar a regra de metas de referência e colorização (`DASHBOARD.md`, seção 5) como constantes do serviço.
3. Implementar a regra de anonimização de ranking para o perfil Promotor (`DASHBOARD.md`, seção 6).

### 4.4 Endpoints
1. `app/api/routers/kpis_router.py`: os 8 endpoints de `API.md`, seção 10 (`/kpis/carteira` a `/kpis/ranking`).
2. `app/api/routers/dashboards_router.py`: `GET /dashboard/executivo`, `GET /dashboard/promotor/{promotor_id}` (`API.md`, seção 10), com autorização conforme `PERMISSOES.md`, seção 6.

## 5. Fora de Escopo desta Sprint

1. Qualquer implementação de frontend — Sprints 09 e 10.
2. Exportação (Excel/CSV/PDF) — Sprint 11.

## 6. Entregáveis

1. Serviço de KPIs completo, com os 8 cálculos implementados e testados isoladamente (casos de borda incluídos).
2. Endpoints de dashboard e KPI funcionais, retornando exatamente as estruturas de `DASHBOARD.md`.
3. Aplicação de escopo por perfil validada para os 4 perfis em todos os endpoints desta Sprint.

## 7. Critérios de Aceite

1. Para um conjunto de dados de teste conhecido (fixture determinístico), cada um dos 8 KPIs retorna o valor matematicamente esperado, verificado por teste unitário com cálculo manual de referência no próprio teste.
2. Denominador zero em qualquer KPI percentual retorna `null`, nunca erro nem `0` (`KPIS.md`, seção 2, item 2).
3. `GET /kpis/fora-da-carteira` com filtro de `promotor_id` retorna `null` com indicação de "não aplicável" (`KPIS.md`, seção 5, nota).
4. Um usuário Supervisor que envie `supervisor_id` diferente do próprio nos filtros recebe `403` em todos os endpoints desta Sprint.
5. Um usuário Promotor que envie `promotor_id` diferente do próprio recebe `403` em todos os endpoints desta Sprint.
6. `GET /dashboard/executivo` retorna a estrutura completa de `DASHBOARD.md`, seção 2.5, incluindo todos os blocos listados na seção 2.2.
7. `GET /dashboard/promotor/{id}` retorna a estrutura completa de `DASHBOARD.md`, seção 3.4, incluindo todos os blocos listados na seção 3.2.
8. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida, com ≥ 90% em `kpi_service.py`.

## 8. Riscos e Observações

1. Esta Sprint conclui o marco M3 do `ROADMAP.md` — toda a inteligência de negócio do backend está completa ao final dela. É o ponto de maior risco de divergência sutil entre a fórmula documentada (`KPIS.md`) e a implementação; recomenda-se atenção especial aos casos de borda descritos na seção 7, itens 1–3, antes de avançar ao frontend.
