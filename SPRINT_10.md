# SPRINT_10.md — Dashboards

## 1. Objetivo

Implementar o Dashboard Executivo e o Dashboard por Promotor completos, incluindo todos os gráficos Chart.js, cartões de KPI e a barra de filtros, consumindo os endpoints implementados na Sprint 08.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `DASHBOARD.md`, `KPIS.md`, `GRAFICOS.md`, `TELAS.md` (seções 3–4), `UX.md` (seções 5–7).

## 3. Pré-condições

Sprint 08 concluída (endpoints de dashboard e KPI disponíveis). Sprint 09 concluída (design system, layout, autenticação disponíveis).

## 4. Escopo (Backlog Detalhado)

### 4.1 Componentes de Filtro
1. Implementar todos os componentes de `components/filtros/` (`DESIGN_SYSTEM.md`, seção 8): `FiltroAno`, `FiltroMes`, `FiltroUF`, `FiltroCidade` (dependente de UF), `FiltroDepartamento`, `FiltroLaboratorio`, `FiltroSupervisor`, `FiltroVendedor`, `FiltroPromotor`, `FiltroTipoPromotor`, `BarraDeFiltros`.
2. Implementar `src/hooks/useFiltrosDashboard.js`: estado dos filtros, serialização para query string, persistência do estado na URL.
3. Aplicar a regra de renderização condicional de filtros por perfil (`DESIGN_SYSTEM.md`, seção 8, último parágrafo).

### 4.2 Componentes de Gráfico
1. Implementar todos os wrappers de `components/charts/` (`GRAFICOS.md`, seção 4): `LineChart`, `BarChart`, `StackedBarChart`, `DoughnutChart`, `RadarChart`, `RankingList`.
2. Implementar `src/components/charts/paletaCores.js` (`GRAFICOS.md`, seção 3).
3. Implementar os três estados (carregando/vazio/erro) em todos os wrappers de gráfico (`GRAFICOS.md`, seção 7).

### 4.3 Dashboard Executivo
1. Implementar a página `pages/dashboard-executivo/` completa, com todos os blocos de `DASHBOARD.md`, seção 2.2, e o comportamento de expansão de `KpiCard` (`DASHBOARD.md`, seção 2, referência a `DESIGN_SYSTEM.md`, seção 6).
2. Implementar `src/services/dashboardService.js` e `src/services/kpiService.js`.

### 4.4 Dashboard por Promotor
1. Implementar a página `pages/dashboard-promotor/` completa, com `Tabs` (Visão Geral / Carteira / Visitas / Checklists / Ranking) e todos os blocos de `DASHBOARD.md`, seção 3.2.
2. Implementar a resolução automática de `:id` para o próprio promotor quando o usuário autenticado tem `perfil = PROMOTOR` (`DASHBOARD.md`, seção 4).
3. Implementar a tela de listagem de equipe para o Supervisor, com seletor de promotor (`UX.md`, seção 7).

## 5. Fora de Escopo desta Sprint

1. Exportação (Excel/CSV/PDF) — os botões de exportação podem estar presentes visualmente, mas sua funcionalidade é implementada na Sprint 11.
2. Telas de importação, cadastros e auditoria — Sprint 11.

## 6. Entregáveis

1. Dashboard Executivo completo e funcional, reagindo corretamente a todos os filtros.
2. Dashboard por Promotor completo e funcional, para os 4 perfis, com o devido escopo de acesso.
3. Todos os componentes de gráfico e filtro implementados e reutilizados de forma consistente entre as duas telas.

## 7. Critérios de Aceite

1. Alteração de qualquer filtro na `BarraDeFiltros` do Dashboard Executivo atualiza todos os blocos da tela em uma única requisição.
2. Todos os KPIs exibidos em cartões refletem exatamente os valores retornados pela API, com formatação correta (moeda BRL, percentual).
3. Um usuário Promotor acessa `/dashboard/promotor/:id` e vê automaticamente o próprio dashboard, sem seleção manual de outro promotor.
4. Um usuário Supervisor acessa a listagem de equipe e navega corretamente para o dashboard de cada promotor sob sua supervisão; tentativa de acessar a URL de um promotor fora da equipe resulta em `/acesso-negado`.
5. O bloco de Ranking exibido a um Promotor aplica a regra de anonimização (`DASHBOARD.md`, seção 6), verificada visualmente e por teste de componente.
6. Todos os gráficos exibem corretamente os três estados (carregando/vazio/erro) em cenários de teste simulados.
7. Meta de cobertura de testes de frontend da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. Esta Sprint conclui, em conjunto com a Sprint 09, a experiência de leitura principal do produto (marco M4, parcial, do `ROADMAP.md`) — validação manual do fluxo completo de Diretoria/Supervisor/Promotor, com dados reais de fixture, é recomendada antes de avançar à Sprint 11.
