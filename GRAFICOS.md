# GRAFICOS.md — Especificação de Gráficos (Chart.js)

## 1. Finalidade

Este documento especifica os tipos de gráfico, bibliotecas de suporte e configurações visuais padronizadas utilizadas nos dashboards do Promotores BI, todos implementados com **Chart.js** através dos componentes wrapper descritos em `FRONTEND.md`, seção 7.

## 2. Biblioteca e Integração

1. Biblioteca: `chart.js` (core) + `react-chartjs-2` (bindings React), mantendo a stack estritamente dentro do que está definido em `README.md`.
2. Todo gráfico é responsivo (`responsive: true`, `maintainAspectRatio: false`), ocupando o container definido pelo grid do `DESIGN_SYSTEM.md`, seção 5.
3. Tooltips habilitados em todos os gráficos, formatando valores monetários em BRL e percentuais conforme `utils/formatadores.js` (`FRONTEND.md`).

## 3. Paleta de Cores para Séries

Para gráficos com múltiplas séries (mais de uma categoria simultânea), a paleta categórica ordenada é:

| Ordem | Cor | Token base |
|---|---|---|
| 1 | `#1D4ED8` | `primary` |
| 2 | `#15803D` | `success` |
| 3 | `#B45309` | `warning` |
| 4 | `#B91C1C` | `danger` |
| 5 | `#0369A1` | `info` |
| 6 | `#7C3AED` | `violet-600` |
| 7 | `#0D9488` | `teal-600` |
| 8 | `#C2410C` | `orange-600` |

Esta paleta é definida como constante única em `src/components/charts/paletaCores.js`, reutilizada por todos os wrappers de gráfico, garantindo que a mesma dimensão (ex.: um Laboratório específico) sempre receba a mesma cor em qualquer gráfico da aplicação, dentro de uma mesma sessão de visualização.

## 4. Inventário de Componentes de Gráfico

### 4.1 `LineChart`
- **Uso:** séries temporais (Evolução Mensal de Faturamento — `DASHBOARD.md`, seções 2.2 e 3.2).
- **Configuração:** eixo X = Ano/Mês; eixo Y = valor monetário; linha única (Dashboard por Promotor) ou múltiplas linhas (Dashboard Executivo, quando comparando regiões/laboratórios selecionados); pontos marcados (`pointRadius: 3`); preenchimento suave abaixo da linha com opacidade `0.08` da cor da série.

### 4.2 `BarChart`
- **Uso:** comparação entre categorias discretas (Faturamento por Região — `DASHBOARD.md`, seção 2.2).
- **Configuração:** barras verticais; ordenação decrescente por valor por padrão; rótulo de valor exibido acima de cada barra quando o número de categorias for ≤ 12 (acima disso, apenas tooltip).

### 4.3 `StackedBarChart`
- **Uso:** composição de uma métrica por múltiplas subcategorias (Faturamento por Departamento com quebra por Laboratório — `DASHBOARD.md`, seção 2.2).
- **Configuração:** `stacked: true` em ambos os eixos; legenda interativa (clique oculta/exibe a série); cores conforme a paleta da seção 3, atribuídas por Laboratório.

### 4.4 `DoughnutChart`
- **Uso:** proporção entre poucas categorias (Distribuição por Tipo de Promotor — `DASHBOARD.md`, seção 2.2).
- **Configuração:** máximo de 6 fatias antes de agrupar categorias residuais em "Outros"; rótulo central exibindo o valor total agregado.

### 4.5 `RadarChart`
- **Uso:** comparação multidimensional de um único promotor contra a média do seu Tipo de Promotor (Cobertura, Positivação, Conformidade de Checklist, Cumprimento de Visitas), disponível como visão complementar na aba "Visão Geral" do Dashboard por Promotor.
- **Configuração:** 4 eixos (um por KPI normalizado de 0 a 1); duas séries sobrepostas (promotor vs. média do tipo), com opacidade de preenchimento `0.15`.

### 4.6 `RankingList`
- **Uso:** não é um gráfico Chart.js, mas um componente de lista ordenada com barra de progresso inline (`ProgressBar`, `DESIGN_SYSTEM.md`) representando visualmente o índice de desempenho de cada promotor no Ranking (`KPIS.md`, seção 10). Tratado nesta especificação por compor a mesma área visual dos demais gráficos no layout dos dashboards.

## 5. Mapeamento KPI → Tipo de Gráfico

| Bloco do Dashboard | Tipo de Gráfico |
|---|---|
| Faturamento por Região | `BarChart` |
| Faturamento por Departamento/Laboratório | `StackedBarChart` |
| Evolução Mensal | `LineChart` |
| Distribuição por Tipo de Promotor | `DoughnutChart` |
| Comparação Multidimensional do Promotor | `RadarChart` |
| Ranking de Promotores | `RankingList` |
| Evolução de Faturamento da Carteira (Dashboard por Promotor) | `LineChart` |

## 6. Acessibilidade de Gráficos

1. Todo gráfico possui um `title` textual acessível (`aria-label`) descrevendo seu conteúdo, independente da legenda visual.
2. Toda informação apresentada visualmente em gráfico está também disponível em formato tabular (`Table`) na mesma tela ou via exportação (`API.md`, seção 12), garantindo que nenhum dado seja exclusivo de uma representação gráfica não textual.
3. A paleta de cores (seção 3) é verificada para contraste suficiente entre séries adjacentes, evitando depender exclusivamente de matiz de cor para diferenciação (uso complementar de padrões de traço em `LineChart` quando há mais de 4 séries simultâneas).

## 7. Estado de Carregamento e Vazio em Gráficos

Todo componente de gráfico observa os três estados definidos em `DESIGN_SYSTEM.md`, seção 10: `Skeleton` no formato de um placeholder retangular do mesmo tamanho do gráfico final durante o carregamento; `EmptyState` compacto sobreposto à área do gráfico quando a resposta da API não contém pontos de dados para os filtros aplicados; renderização normal do gráfico em caso de sucesso com dados.
