# DESIGN_SYSTEM.md — Design System

## 1. Finalidade

Este documento define os tokens visuais (cores, tipografia, espaçamento) e o inventário de componentes reutilizáveis do Promotores BI, implementados com **TailwindCSS**. Toda tela descrita em `TELAS.md` deve ser construída exclusivamente a partir dos componentes aqui definidos.

## 2. Princípios de Design

1. **Clareza sobre densidade:** dashboards de BI priorizam legibilidade dos números sobre quantidade de informação por tela.
2. **Consistência:** o mesmo tipo de dado (KPI, filtro, tabela) é sempre representado pelo mesmo componente em qualquer tela.
3. **Acessibilidade mínima:** contraste de texto conforme WCAG AA, todos os componentes interativos navegáveis por teclado, `aria-label` em ícones sem texto visível.
4. **Responsividade:** todas as telas são utilizáveis a partir de resolução mínima de 1280px de largura (uso corporativo em desktop/notebook); adaptação completa a dispositivos móveis é item de evolução pós-POC.

## 3. Tokens de Cor

| Token | Uso | Valor (Tailwind) |
|---|---|---|
| `primary` | Ações principais, links, elementos de destaque de marca | `#1D4ED8` (`blue-700`) |
| `primary-hover` | Estado hover de ações principais | `#1E40AF` (`blue-800`) |
| `secondary` | Ações secundárias | `#334155` (`slate-700`) |
| `success` | Indicadores positivos (cobertura/positivação acima da meta) | `#15803D` (`green-700`) |
| `warning` | Indicadores de atenção (próximo do limite da meta) | `#B45309` (`amber-700`) |
| `danger` | Indicadores críticos (abaixo da meta), ações destrutivas | `#B91C1C` (`red-700`) |
| `info` | Mensagens informativas neutras | `#0369A1` (`sky-700`) |
| `surface` | Fundo de cartões e painéis | `#FFFFFF` (branco) |
| `surface-muted` | Fundo de página | `#F1F5F9` (`slate-100`) |
| `border` | Bordas de cartões, tabelas, inputs | `#E2E8F0` (`slate-200`) |
| `text-primary` | Texto principal | `#0F172A` (`slate-900`) |
| `text-secondary` | Texto secundário/legendas | `#64748B` (`slate-500`) |

Paleta categórica para gráficos com múltiplas séries (KPIs por Laboratório, Departamento, Tipo de Promotor) — 8 cores distintas e acessíveis, definidas em `GRAFICOS.md`, seção 3, reutilizando os tokens `primary`, `success`, `warning`, `danger`, `info` como base e complementando com tons intermediários de `Tailwind` (`violet-600`, `teal-600`, `orange-600`).

## 4. Tipografia

| Token | Fonte | Tamanho | Peso | Uso |
|---|---|---|---|---|
| `heading-1` | Inter / sans-serif do sistema | 28px | 700 | Título de página |
| `heading-2` | idem | 20px | 600 | Título de seção/cartão |
| `heading-3` | idem | 16px | 600 | Subtítulo, cabeçalho de tabela |
| `body` | idem | 14px | 400 | Texto padrão |
| `caption` | idem | 12px | 400 | Legendas, metadados |
| `kpi-value` | idem | 32px | 700 | Valor numérico de destaque em cards de KPI |

## 5. Espaçamento e Grid

1. Unidade base: `4px` (escala padrão do Tailwind: `1 = 4px`).
2. Espaçamento padrão entre cartões/seções: `24px` (`gap-6`).
3. Grid de dashboards: `12` colunas, com cartões de KPI ocupando `3` colunas em telas largas (4 por linha) e `6` colunas em telas médias (2 por linha).
4. Raio de borda padrão de cartões e botões: `8px` (`rounded-lg`).
5. Sombra padrão de cartões: `shadow-sm`, elevando para `shadow-md` em estado de hover quando o cartão é interativo (ex.: card de KPI clicável que expande detalhamento).

## 6. Inventário de Componentes Base (`components/ui/`)

| Componente | Descrição |
|---|---|
| `Button` | Variantes: `primary`, `secondary`, `ghost`, `danger`. Tamanhos: `sm`, `md`, `lg`. |
| `Card` | Container padrão de conteúdo, com `title`, `actions` (slot de botões no cabeçalho) e `body`. |
| `KpiCard` | Especialização de `Card` para exibição de um KPI: valor em destaque (`kpi-value`), rótulo, variação percentual (opcional), indicador de cor (`success`/`warning`/`danger`) conforme meta. |
| `Table` | Tabela com cabeçalho fixo, ordenação por coluna, paginação integrada (`usePaginacao`), estado vazio e estado de carregamento (skeleton). |
| `Badge` | Rótulo curto colorido (ex.: status de importação, tipo de promotor). |
| `Modal` | Diálogo modal com overlay, usado em confirmações (ex.: rollback de importação). |
| `Toast` | Notificação temporária não bloqueante (sucesso, erro, aviso). |
| `Select` | Campo de seleção único, usado em filtros e formulários. |
| `MultiSelect` | Campo de seleção múltipla, usado em filtros que aceitam mais de um valor (ex.: múltiplos Laboratórios). |
| `DateRangePicker` | Seletor de Ano/Mês, usado na Barra de Filtros. |
| `SearchInput` | Campo de busca textual com debounce, usado em listagens (Clientes, Promotores). |
| `Tabs` | Navegação por abas dentro de uma página (ex.: Dashboard por Promotor: Visão Geral / Visitas / Checklists). |
| `ProgressBar` | Barra de progresso, usada para indicadores percentuais (Cobertura, Positivação, conformidade de Checklist). |
| `FileUpload` | Campo de upload de arquivo `.xlsx`, com drag-and-drop, usado na tela de Nova Importação. |
| `EmptyState` | Estado vazio padronizado (ícone, mensagem, ação sugerida). |
| `ErrorState` | Estado de erro padronizado (mensagem, botão de nova tentativa). |
| `Skeleton` | Placeholder de carregamento para cartões e tabelas. |
| `Avatar` | Iniciais/foto do usuário autenticado, exibido na Topbar. |
| `Breadcrumb` | Trilha de navegação hierárquica. |

## 7. Componentes de Layout (`components/layout/`)

| Componente | Descrição |
|---|---|
| `Shell` | Estrutura raiz de página autenticada: `Sidebar` + `Topbar` + área de conteúdo. |
| `Sidebar` | Menu de navegação lateral, itens renderizados condicionalmente conforme `PERMISSOES.md`. |
| `Topbar` | Barra superior com nome da aplicação, `Avatar` do usuário, menu de logout. |
| `PageHeader` | Cabeçalho de página com título, `Breadcrumb` e slot de ações (ex.: botão "Nova Importação"). |

## 8. Componentes de Filtro (`components/filtros/`)

| Componente | Filtro correspondente (`DASHBOARD.md`) |
|---|---|
| `FiltroAno` | Ano |
| `FiltroMes` | Mês |
| `FiltroUF` | UF |
| `FiltroCidade` | Cidade (dependente da UF selecionada) |
| `FiltroDepartamento` | Departamento |
| `FiltroLaboratorio` | Laboratório |
| `FiltroSupervisor` | Supervisor |
| `FiltroVendedor` | Vendedor |
| `FiltroPromotor` | Promotor |
| `FiltroTipoPromotor` | Tipo de Promotor |
| `BarraDeFiltros` | Composição de todos os filtros aplicáveis à tela corrente, com botão "Limpar filtros" e contagem de filtros ativos |

`BarraDeFiltros` renderiza apenas os filtros permitidos ao perfil do usuário autenticado (ex.: `FiltroPromotor` não é exibido a um usuário Promotor, cujo escopo já é fixo — `PERMISSOES.md`).

## 9. Componentes de Gráfico (`components/charts/`)

Detalhados em `GRAFICOS.md`: `LineChart`, `BarChart`, `StackedBarChart`, `DoughnutChart`, `RadarChart`, `RankingList`.

## 10. Estados de Interface Padronizados

| Estado | Componente utilizado | Regra |
|---|---|---|
| Carregando | `Skeleton` | Exibido enquanto a requisição à API está pendente. |
| Vazio | `EmptyState` | Exibido quando a resposta da API não contém dados para os filtros aplicados. |
| Erro | `ErrorState` | Exibido quando a requisição falha (rede ou erro `5xx`); inclui botão de nova tentativa. |
| Sucesso com dados | Componente de conteúdo normal (`Table`, gráficos, `KpiCard`) | — |

## 11. Ícones

Biblioteca de ícones: `lucide-react` (SVG, leve, consistente com o estilo visual minimalista adotado). Uso exclusivo através de um componente wrapper `Icon` que padroniza tamanho (`16px`/`20px`/`24px`) e cor herdada do texto (`currentColor`).

## 12. Modo Escuro

Fora do escopo da POC. A estrutura de tokens (seção 3) é definida via variáveis CSS (`:root`) para permitir introdução futura de tema escuro sem refatoração, mas nenhuma implementação de alternância de tema é entregue nas Sprints 00–12.
