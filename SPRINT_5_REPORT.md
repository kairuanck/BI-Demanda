# SPRINT_5_REPORT.md — Relatório da Sprint 5 (Visão 360º do Cliente)

## 1. Resumo

A Sprint 5 entregou a Visão 360º do Cliente: busca global (por código, razão social, nome fantasia, CNPJ ou cidade), uma página completa por cliente com dados cadastrais, 8 KPIs, 4 gráficos, tabela de laboratórios comprados, cartão(ões) de promotor vinculado e uma timeline cronológica combinando visitas, checklists, importações e alterações cadastrais — tudo sobre dados reais importados na Sprint 3, reaproveitando integralmente a infraestrutura do Dashboard Executivo (Sprint 4). Nenhuma refatoração de funcionalidade existente, nenhuma mudança de arquitetura, nenhuma dependência nova.

O backend expõe 8 endpoints REST em `/api/v1/clientes/*`, todos resolvidos com agregação SQL (a Timeline é a única exceção deliberada, mesma lógica já aceita para o Índice de Desempenho da Sprint 4). O frontend reaproveita `KpiCard`, `Card`, `BlocoGrafico`, os wrappers de gráfico e os estados de UX (`Skeleton`/`EmptyState`/`ErrorState`) da Sprint 4 sem alterá-los estruturalmente.

A autoauditoria manual encontrou e corrigiu **3 problemas reais** antes da entrega — detalhados na seção 6 e em `docs/DECISIONS.md`, seção 25, incluindo um bug de busca textual da mesma classe já encontrada (e corrigida) na Sprint 3.

## 2. Escopo Entregue

| Área | Entrega |
|---|---|
| Busca global | Campo no Topbar (visível em toda tela) + página `/clientes` com resultados paginados; busca por código, razão social, nome fantasia, CNPJ e cidade |
| Dados Cadastrais | Código, Razão Social, Nome Fantasia, Cidade/UF, CNPJ, Status, Grupo Econômico, Segmento |
| KPIs (8 cartões) | Faturamento Acumulado, Faturamento 12 Meses, Laboratórios Comprados, Dias Desde Última Visita, Visitas, Checklists, Cobertura, Positivação |
| Gráficos (4 blocos) | Evolução do Faturamento (linha), Faturamento por Laboratório (barra), Visitas por Mês (linha), Checklists por Mês (linha) |
| Laboratórios | Tabela: laboratório, primeira compra, última compra, valor acumulado, participação percentual |
| Promotor | 1 cartão por vínculo (carteira SB e/ou carteira Avert): nome, tipo, supervisor, sistema, carteira, cobertura, faturamento — com link para a página do promotor |
| Histórico (Timeline) | Visitas, checklists, importações relacionadas e alterações cadastrais, mais recente primeiro, paginado |
| Filtros | Ano, Mês, Laboratório, Sistema de Origem — estado de URL |
| Navegação | Cliente ↔ Promotor ↔ Dashboard: busca (Topbar/`/clientes`) → Cliente; Carteira do Promotor → Cliente; cartão de Promotor na página do Cliente → Promotor |

## 3. Arquivos Criados/Alterados (visão consolidada)

### Backend
| Arquivo | Conteúdo |
|---|---|
| `app/services/cliente_service.py` | Núcleo da sprint — KPIs, gráficos, laboratórios, timeline e busca, reaproveitando `PontoSerieMensal`/`PontoCategoria`/`_promotores_com_metricas` de `dashboard_service.py` |
| `app/api/schemas/cliente_schema.py` | 8 schemas Pydantic v2 |
| `app/api/routers/cliente_router.py` | 8 endpoints REST, registrado em `app/main.py` |
| `app/infrastructure/database.py` | Função SQL `norm_busca` (busca acento/caixa-insensível no SQLite, seção 6, item 1) |
| `app/infrastructure/models/cliente_model.py` | Índice novo `ix_clientes_cnpj_cpf` |
| `alembic/versions/2026_07_13_..._sprint_5_indice_de_busca_de_clientes.py` | Migração do índice — `upgrade→downgrade→upgrade` e `alembic check` validados |

### Frontend
| Arquivo | Conteúdo |
|---|---|
| `src/types/cliente.ts` | Tipos espelhando os schemas do backend |
| `src/services/clienteService.ts` | Camada de serviço — reaproveita `PontoSerieMensal`/`PontoCategoria` de `types/dashboard.ts` |
| `src/hooks/useClienteData.ts` | 8 hooks React Query |
| `src/pages/clientes/ClientesPage.tsx` | Busca/resultados, nova rota `/clientes` |
| `src/pages/clientes/ClienteDetalhePage.tsx` | Página completa da Visão 360, nova rota `/clientes/:clienteId` |
| `src/components/layout/Topbar.tsx` | Campo de busca global, visível em toda tela |
| `src/components/layout/Sidebar.tsx` | Item de menu "Clientes" |
| `src/pages/promotor/PromotorDetalhePage.tsx` | Seção "Carteira" nova (lista de clientes do promotor, link para cada cliente) |
| `src/utils/formatadores.ts` | `NOMES_MES` passa a ser exportado — elimina duplicação (seção 6, item 3) |
| `src/main.tsx` | `QueryClient` não tenta de novo em 404 (seção 6, item 2) |

### Testes
| Arquivo | Cobre |
|---|---|
| `backend/tests/test_cliente_service.py` | 18 testes — busca (incluindo acento/caixa e filtro por promotor), detalhe, KPIs, gráficos, laboratórios, timeline |
| `backend/tests/api/test_cliente_api.py` | 10 testes — os 8 endpoints via `TestClient`, incluindo 404 padrão |
| `frontend/src/App.test.tsx` | Ajustado: item "Clientes" no menu |

### Documentação
- `docs/DECISIONS.md`, seções 22–25: adaptação dos KPIs à granularidade de 1 cliente, performance/índices, arquitetura do frontend, autoauditoria.
- `README.md`: status de implementação e funcionalidades atualizados.

## 4. Decisões Técnicas Principais

Detalhadas em `docs/DECISIONS.md`, seções 22–24. As mais relevantes:

1. **Cobertura/Positivação do cliente generalizadas para razão temporal mês-a-mês** — `KPIS.md` define esses KPIs sobre um conjunto de clientes; aplicados a 1 cliente só, a fórmula original colapsa para 0%/100%. A janela (mês único, ano inteiro ou últimos 12 meses corridos) é a mesma usada pelo KPI "Faturamento últimos 12 meses" quando nenhum período está filtrado.
2. **Promotor responsável não é único** — um cliente pode estar na carteira SB e na carteira Avert simultaneamente (Sprint 3); a página expõe uma lista de vínculos (0, 1 ou 2) em vez de escolher um "vencedor" arbitrário, reaproveitando a mesma rotina anti-N+1 da Tabela de Promotores para garantir números consistentes.
3. **Grupo Econômico/Segmento vêm de `carteiras_avert`**, não existem em `clientes` — `null` quando o cliente não tem carteira Avert.
4. **Timeline ignora os filtros de página** (Ano/Mês/Laboratório/Sistema de Origem) — mistura 4 tipos de evento heterogêneos onde os filtros não se aplicam uniformemente; mesmo raciocínio já usado para "Última Importação" na Sprint 4.
5. **Carteira do promotor reaproveita o endpoint de busca** (`GET /clientes?promotor_id=...`) em vez de um endpoint novo — fecha a navegação Promotor → Cliente pedida nesta sprint sem duplicar lógica de listagem.
6. **Busca sem full-text search** — `ILIKE`/`LIKE` simples; único índice novo é `clientes.cnpj_cpf` (campos de texto livre não se beneficiam de índice B-tree com `LIKE '%termo%'`).

## 5. Performance

Todo KPI, gráfico e a tabela de laboratórios são resolvidos com agregação SQL — nenhuma entidade é carregada para somar em Python (mesmo princípio da Sprint 4). Índice novo (`clientes.cnpj_cpf`) via migração validada (`alembic check` sem drift). Todos os demais padrões de acesso desta sprint (filtrar/agrupar por `cliente_id`) já estavam cobertos pelos índices da Sprint 4 — nenhum outro índice foi necessário. A rotina de vínculos de promotor reaproveita a mesma rotina anti-N+1 (`_promotores_com_metricas`) já validada e corrigida na Sprint 4.

## 6. Autoauditoria: Três Problemas Encontrados e Corrigidos

1. **Busca de cliente por cidade/razão social com acento não encontrava nada.** `são paulo` não encontrava um cliente cadastrado em `SÃO PAULO` — o `LOWER()` nativo do SQLite não faz *case-folding* de caracteres acentuados, a mesma limitação que a Sprint 3 já havia corrigido para deduplicação de nomes de promotor, reaparecendo aqui na busca textual. Corrigido registrando uma função SQL customizada (`norm_busca`) só para o dialeto SQLite; o `ILIKE` do PostgreSQL já resolve isso nativamente. Coberto por `test_busca_clientes_ignora_acento_e_caixa`, confirmado como regressão real (falha contra o código anterior, passa com a correção).
2. **Página de cliente ou promotor inexistente levava ~7s para mostrar o erro amigável**, porque o React Query tentava de novo automaticamente um 404 — que nunca terá sucesso numa nova tentativa. Corrigido com uma função `retry` global no `QueryClient` que não tenta de novo especificamente em 404; o tempo até o erro amigável caiu de ~7s para ~1s. Corrige tanto a nova Página do Cliente quanto a Página do Promotor da Sprint 4 (mesmo sintoma, não detectado antes por falta de teste manual com ID inválido).
3. **`NOMES_MES` duplicado em 3 arquivos** (2 da Sprint 4 + a nova página do cliente) — consolidado como export único em `utils/formatadores.ts`.

## 7. Cobertura de Testes

| Métrica | Resultado |
|---|---|
| Testes backend | **118 passando** (90 pré-existentes + 28 novos desta sprint: 18 de serviço + 10 de endpoint) |
| Testes frontend | **9 passando** (`vitest`) |
| Cobertura backend (`app` + `etl`) | **91%** — `cliente_service.py` 93%, `cliente_router.py` 100%, `cliente_schema.py` 100%, `database.py` 100% |
| Lint (`ruff`) / Formatação (`black`) / Tipos (`mypy app etl`) | Sem erros |
| Lint/Tipos frontend (`eslint`, `tsc -b`) | Sem erros |
| Migração | `upgrade → downgrade → upgrade` validado; `alembic check` sem *drift* |

## 8. Validação Manual no Navegador

Backend (`uvicorn`) e frontend (`vite`) executados lado a lado contra o mesmo banco de desenvolvimento com dados sintéticos fictícios da Sprint 4 (reutilizado, com o migration novo aplicado). Fluxos verificados via captura de tela e console do navegador (zero erros JS, exceto os 2 erros de rede esperados no teste de 404):

- Busca por "PET SHOP ALFA", "10001", "11222333000144", "CAMPINAS" → mesmo cliente encontrado por qualquer campo.
- Página do cliente → dados cadastrais, 8 KPIs, 4 gráficos, laboratórios (participação soma 100%), 2 cartões de promotor (SB e Avert) e 7 eventos de histórico ordenados corretamente (mais recente primeiro), incluindo a visita "cruzada" (Sprint 4) aparecendo corretamente como evento factual mesmo sem contar para a cobertura do promotor dono da carteira.
- Busca via Topbar → Enter → `/clientes?q=...` → clique na linha → `/clientes/:id`, zero erros de console.
- Página do Promotor → seção "Carteira" nova lista os clientes certos, clique navega para `/clientes/:id`.
- Estado vazio (`/clientes?q=NAOEXISTE123`) e estado de erro (cliente inexistente) renderizam mensagens amigáveis com botão de nova tentativa.
- Layout íntegro em 1280px de largura (mínimo suportado por `DESIGN_SYSTEM.md`, seção 2, item 4).

## 9. Pendências

1. **CNPJ sem máscara/permissão** — o prompt pede exibição "quando permitido", mas não há sistema de autenticação/permissões implementado ainda (`PERMISSOES.md` segue como sprint futura); documentado, não implementado especulativamente.
2. **Timeline não filtra por página** (seção 4, item 4) — decisão deliberada, não pendência real, mas registrada para não ser reaberta como bug numa auditoria futura.
3. **Exportação, CRUD de cliente e tela de administração** — não pedidos nesta sprint; nenhum botão/endpoint foi criado para evitar funcionalidade não utilizada.

## 10. Riscos

1. **Banco de desenvolvimento usado na validação manual não é commitado** (dados sintéticos, `database/app.db` gitignored) — reproduzível a qualquer momento a partir de `tests/etl/fixtures_reais.py`.
2. **`norm_busca` é uma função Python registrada por conexão SQLite** — funciona automaticamente em qualquer sessão nova, mas é específica do dialeto; se a stack migrar para PostgreSQL (`README.md`, seção 3), o caminho `ILIKE` já correto assume o lugar sem nenhuma mudança de código adicional (o branch de dialeto já existe em `cliente_service.py`).

## 11. Sugestões para a Sprint 6

1. Autenticação (JWT + bcrypt + RBAC) — desbloqueia perfis reais e a exibição condicional de CNPJ.
2. Exportação (Excel/CSV/PDF) da Página do Cliente e da busca, se o negócio priorizar.
3. Se o volume de dados reais crescer, medir a busca textual sob carga real e reavaliar a necessidade de full-text search (hoje deliberadamente fora de escopo, seção 4, item 6).
