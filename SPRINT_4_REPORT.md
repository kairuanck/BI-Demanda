# SPRINT_4_REPORT.md — Relatório da Sprint 4 (Dashboard Executivo Funcional)

## 1. Resumo

A Sprint 4 entregou a primeira versão funcional do **Dashboard Executivo**: 8 filtros globais, 10 cartões de KPI, 6 blocos de gráfico, tabela paginada de promotores e página de detalhe por promotor, todos consumindo dados reais importados na Sprint 3 (nenhum dado mockado). Toda a infraestrutura de Sprints 0–3 foi reaproveitada — nenhuma refatoração de funcionalidade existente, nenhuma mudança de arquitetura, nenhuma dependência nova.

O backend expõe 11 endpoints REST em `/api/v1/dashboard/*`, todos resolvidos com agregação SQL (nunca carregando entidades para somar em Python, exceto o Índice de Desempenho — ver seção 4). O frontend consome esses endpoints via React Query, com os 3 estados de interface padronizados (carregando/vazio/erro) em todo bloco.

A autoauditoria manual no navegador (backend real + dados sintéticos fictícios) encontrou e corrigiu **2 bugs de cálculo reais** antes da entrega — detalhados na seção 6 e em `docs/DECISIONS.md`, seção 21.

## 2. Escopo Entregue

| Área | Entrega |
|---|---|
| Filtros globais | Ano, Mês, UF, Laboratório, Tipo de Promotor, Sistema de Origem, Supervisor, Promotor — refletidos na URL |
| KPIs (10 cartões) | Faturamento Total, da Carteira, da Região, Fora da Carteira, Quantidade de Clientes, Clientes Positivados, Cobertura da Carteira, Número de Visitas, Número de Checklists, Última Importação |
| Gráficos (6 blocos) | Evolução Mensal do Faturamento (linha), Evolução da Positivação por Carteira/Região/Fora (linha, 3 séries), Faturamento por Laboratório (barra), Top Promotores por Índice de Desempenho (barra horizontal), Tipos de Checklist (rosca), Distribuição por UF (tabela — sem lib de mapa na stack) |
| Tabela de Promotores | Paginada; Nome, Tipo, Supervisor, Sistema, Clientes, Visitas, Checklists, Cobertura, Fat. Carteira, Fat. Região; clique na linha abre o detalhe |
| Página de Detalhe do Promotor | `/dashboard/promotores/:promotorId` — dados cadastrais, KPIs individuais, evolução de faturamento, faturamento por laboratório, Índice de Desempenho, Conformidade de Checklist |
| Home | Últimas importações por tipo de arquivo: status, linhas válidas/inválidas, data, duração |

## 3. Arquivos Criados/Alterados (visão consolidada)

### Backend
| Arquivo | Conteúdo |
|---|---|
| `app/services/dashboard_service.py` | Núcleo da sprint — todos os KPIs, séries e a rotina anti-N+1 `_promotores_com_metricas` |
| `app/api/schemas/dashboard_schema.py` | 13 schemas Pydantic v2, `ConfigDict(from_attributes=True)` |
| `app/api/routers/dashboard_router.py` | 11 endpoints REST, registrado em `app/main.py` |
| `app/repositories/importacao_repository.py` | Correção: `listar()` ordenava por `id.desc()` (sem sentido pós-UUID), passou a `criado_em.desc()` |
| `app/infrastructure/models/{cliente,carteira,carteira_avert,faturamento,visita}_model.py` | 6 índices novos (seção 5) |
| `alembic/versions/2026_07_13_..._sprint_4_indices_de_performance_do_.py` | Migração dos 6 índices — `upgrade→downgrade→upgrade` e `alembic check` validados |

### Frontend
| Arquivo | Conteúdo |
|---|---|
| `src/types/dashboard.ts` | Tipos espelhando os schemas do backend (campos `Decimal` como `string`) |
| `src/services/dashboardService.ts` | Camada de serviço — único ponto de chamada HTTP do domínio |
| `src/services/httpClient.ts` | Estendido para aceitar query params (`httpGet<T>(path, params)`) |
| `src/hooks/useFiltrosDashboard.ts` | Filtros globais como estado de URL (`useSearchParams`) |
| `src/hooks/useDashboardData.ts` | 11 hooks React Query, um por endpoint |
| `src/utils/formatadores.ts` | Moeda BRL, percentual, data/hora, duração |
| `src/components/charts/{LineChart,BarChart,DoughnutChart,paletaCores,chartSetup}.tsx` | Wrappers Chart.js reutilizáveis |
| `src/components/filtros/BarraDeFiltros.tsx` | 8 filtros globais |
| `src/components/dashboard/{BlocoGrafico,TabelaPromotores}.tsx` | Composição padrão de gráfico (loading/vazio/erro) e tabela paginada |
| `src/components/ui/{Card,KpiCard,Skeleton,EmptyState,ErrorState}.tsx` | Componentes base novos do design system |
| `src/pages/dashboard/DashboardPage.tsx` | Reescrita — substitui o placeholder da Sprint 0 |
| `src/pages/promotor/PromotorDetalhePage.tsx` | Nova |
| `src/pages/home/HomePage.tsx` | Estendida com o bloco de últimas importações |
| `src/App.tsx` | Nova rota `/dashboard/promotores/:promotorId` |

### Testes
| Arquivo | Cobre |
|---|---|
| `backend/tests/test_dashboard_service.py` | 16 testes — KPIs, filtros combinados, gráficos, tabela de promotores, detalhe, os 2 bugs da seção 6 |
| `backend/tests/api/test_dashboard_api.py` | 13 testes — os 11 endpoints via `TestClient`, incluindo 404 padrão |
| `frontend/src/App.test.tsx` | Ajustado: rota `/dashboard` agora renderiza o Dashboard Executivo real |

### Documentação
- `docs/DECISIONS.md`, seções 16–21: adaptação dos KPIs ao schema real, elegibilidade de importação, fórmulas implementadas, performance/índices, arquitetura do frontend, autoauditoria.
- `README.md`: status de implementação atualizado (Sprints 0–4 concluídas).

## 4. Decisões Técnicas Principais

Detalhadas em `docs/DECISIONS.md`, seções 16–20. As mais relevantes:

1. **"Faturamento da Região" = carteira Avert** (`carteiras_avert`), não uma quebra geográfica — `KPIS.md` original definiu "Região" antes da Sprint 3 revelar que a operação tem duas carteiras paralelas genuinamente distintas. A quebra geográfica original vira o bloco "Distribuição por UF".
2. **Nenhuma query filtra `importacoes.status`** — o motor de importação só persiste linhas de domínio dentro de uma importação bem-sucedida (garantia transacional desde a Sprint 2), então toda linha das tabelas de fato já satisfaz `REGRAS_DE_NEGOCIO.md` §7 por construção.
3. **Índice de Desempenho é a única agregação em Python** — combina 4 métricas já agregadas por promotor (dezenas de promotores na base real); todo o resto é `GROUP BY`/`SUM`/`COUNT` no banco.
4. **Distribuição por UF como tabela, não mapa** — o prompt da sprint permite esse fallback explicitamente; nenhuma lib de mapas está na stack e adicioná-la violaria "não altere arquitetura sem necessidade".
5. **Filtros globais refletidos na URL**, não em estado local — permite recarregar/compartilhar um link do dashboard já filtrado sem introduzir uma lib de estado global fora da stack.
6. **Inventário de componentes reduzido ao necessário**: `Modal`, `Toast`, `MultiSelect`, `Tabs`, `RadarChart`, `Avatar` real etc. não foram construídos — nenhuma tela desta sprint os usa (autenticação/exportação seguem fora de escopo).

## 5. Performance

Índices novos adicionados via migração (`clientes.uf_sigla`, `carteiras.promotor_id`, `carteiras_avert.promotor_id`/`cliente_id`, `faturamentos.laboratorio_id`, `visitas.cliente_id`) — cobrem os padrões de acesso do dashboard não atendidos pelos índices das Sprints 2/3. `alembic check` confirma zero *drift* entre os modelos SQLAlchemy e a cadeia de migrações. A tabela de promotores e o ranking resolvem métricas de N promotores em ~9 queries agregadas fixas (`_promotores_com_metricas`), não N+1 — mesmo padrão usado pelo KPI de Cobertura (seção 6).

## 6. Autoauditoria: Dois Bugs Encontrados e Corrigidos

A verificação manual no navegador (backend real, `uvicorn` + `vite`, dados sintéticos fictícios — nunca dados reais, repositório público) comparou os mesmos números entre blocos diferentes da mesma tela e encontrou duas divergências:

1. **Cobertura da carteira contava visita de promotor errado.** O cartão de KPI "Cobertura da Carteira" e a página de detalhe do promotor mostravam 100% de cobertura para um promotor com metade da carteira visitada, porque `_cobertura_carteira` não exigia que a visita `REALIZADA` fosse do promotor titular daquele vínculo de carteira — bastava que *algum* promotor tivesse visitado o cliente. A tabela de promotores já calculava certo (join explícito `Visita.promotor_id == Carteira.promotor_id`); `_cobertura_carteira` foi reescrita para o mesmo critério. Corrigido e coberto por `test_cobertura_carteira_nao_credita_visita_de_outro_promotor`.
2. **Filtro de UF não chegava às métricas por promotor.** Filtrar o dashboard por UF=SP recalculava corretamente os KPIs agregados e os gráficos, mas a tabela de promotores continuava mostrando o faturamento e a contagem de clientes completos de um promotor cuja carteira inteira era de outro estado — violando o requisito de que os filtros globais atualizam todos os componentes da tela. As 9 subconsultas agregadas de `_promotores_com_metricas` (e `_positivacao_promotor`) foram corrigidas para respeitar `uf_sigla`. Corrigido e coberto por `test_listar_promotores_respeita_filtro_de_uf`.

Detalhe técnico completo, incluindo por que ambos os bugs só afetavam os caminhos "por promotor" e não os KPIs/gráficos agregados do topo da tela, em `docs/DECISIONS.md`, seção 21.

## 7. Cobertura de Testes

| Métrica | Resultado |
|---|---|
| Testes backend | **90 passando** (74 pré-existentes + 16 novos desta sprint: 14 de serviço + 2 de regressão dos bugs da seção 6) |
| Testes API (endpoint) | **13 passando** (`tests/api/test_dashboard_api.py`, novo) |
| Testes frontend | **9 passando** (`vitest`) |
| Cobertura backend (`app` + `etl`) | **90%** — `dashboard_service.py` 95%, `dashboard_router.py` 100%, `dashboard_schema.py` 99% |
| Lint (`ruff`) / Formatação (`black`) / Tipos (`mypy app etl`) | Sem erros |
| Lint/Tipos frontend (`eslint`, `tsc -b`) | Sem erros |
| Migração | `upgrade → downgrade → upgrade` validado; `alembic check` sem *drift* |

## 8. Validação Manual no Navegador

Backend (`uvicorn`) e frontend (`vite`) executados lado a lado contra um banco de desenvolvimento populado com os mesmos dados sintéticos fictícios dos testes automatizados (3 clientes, carteira SB, carteira Avert, checklist). Fluxos verificados via captura de tela e console do navegador (zero erros JS):

- Home → últimas importações com status, contagem de linhas e duração.
- Dashboard → 10 KPIs, 6 gráficos e tabela de promotores carregando dados reais simultaneamente.
- Alteração de filtro (UF) → todos os blocos recalculam e a URL reflete `?uf=SP`; estado vazio correto em "Top Promotores" quando o Índice de Desempenho não é calculável (Conformidade de Checklist ausente para aqueles promotores — comportamento correto, não bug).
- Clique em uma linha da tabela → navega para `/dashboard/promotores/:id`, preservando Ano/Mês na URL; página de detalhe mostra os mesmos números da linha de origem (cobertura consistente após a correção da seção 6).
- Layout íntegro em 1280px de largura (mínimo suportado por `DESIGN_SYSTEM.md` §2, item 4).

## 9. Pendências

1. **Conciliação de `clientes_integracao`, upload HTTP e autenticação** — heard das Sprints 2/3, seguem fora de escopo desta sprint (não pedidas no prompt).
2. **Exportação (Excel/CSV/PDF)** — `TELAS.md`/`FRONTEND.md` preveem, mas não fazia parte do critério de sucesso desta sprint; nenhum botão/endpoint foi criado para evitar funcionalidade não utilizada.
3. **Filtro de UF em `_positivacao_promotor` corrigido, mas não testado isoladamente** — a correção reaproveita `_com_uf` (já testado no contexto dos KPIs agregados); um teste dedicado ao efeito em `positivacao`/Índice de Desempenho por promotor fica como próximo incremento caso o Ranking passe a ser auditado com o mesmo rigor da tabela.
4. **`Cobertura da Carteira` em `_cobertura_carteira` não filtra por `laboratorio_id`** (nenhum outro KPI de cobertura/visita faz isso — Laboratório só se aplica a Faturamento/Checklist na definição de negócio) — comportamento intencional, não pendência real, mas vale registrar para não ser reaberto como "bug" numa auditoria futura.

## 10. Riscos

1. **Banco de desenvolvimento usado na validação manual não é commitado** (dados sintéticos, `database/app.db` gitignored) — reproduzível a qualquer momento a partir de `tests/etl/fixtures_reais.py`, mas o estado exato da validação desta sprint não persiste entre sessões.
2. **`Última Importação` no cartão de KPI mostra a importação mais recente entre todos os tipos de arquivo**, não uma por tipo (a Home já mostra a quebra por tipo) — decisão de simplicidade para caber em um único cartão; se o negócio precisar do detalhamento por tipo no próprio Dashboard, é extensão trivial do mesmo endpoint já existente.

## 11. Sugestões para a Sprint 5

1. Autenticação (JWT + bcrypt + RBAC) — desbloqueia perfis reais (`PERMISSOES.md`) e substitui o usuário técnico fixo da CLI de importação.
2. Upload HTTP de importações (`POST /importacoes`, multipart), reaproveitando a inferência estrutural do `etl/cli.py`.
3. Tela de conciliação manual de `clientes_integracao`.
4. Se o volume de dados reais crescer significativamente, medir os índices desta sprint sob carga real e revisitar `promotores.supervisor_id`/`importacoes.criado_em` (deliberadamente não indexados agora — seção 5 de `docs/DECISIONS.md`, seção 19).
