# DASHBOARD.md — Especificação dos Dashboards

## 1. Finalidade

Este documento especifica o conteúdo, a composição e o comportamento de filtro dos dois dashboards do Promotores BI: **Dashboard Executivo** e **Dashboard por Promotor**. As fórmulas dos KPIs exibidos estão em `KPIS.md`; os tipos de gráfico em `GRAFICOS.md`; o layout visual em `TELAS.md`, seções 3 e 4.

## 2. Dashboard Executivo

### 2.1 Propósito
Visão consolidada da operação inteira (ou da equipe, quando acessado por um Supervisor — `PERMISSOES.md`, seção 4.2), permitindo à Diretoria e ao Administrador identificar tendências, comparar regiões/laboratórios/departamentos e localizar desvios de desempenho.

### 2.2 Blocos do Dashboard Executivo

| Bloco | Conteúdo | KPI/Fonte |
|---|---|---|
| Cartões de KPI Consolidados | Cobertura média, Positivação média, Faturamento total, Faturamento Fora da Carteira, Total de Visitas Realizadas, Conformidade média de Checklist | `KPIS.md`, seções 3–9 |
| Faturamento por Região | Gráfico de barras: faturamento total por UF (ou por Região, agrupando UFs) | `KPIS.md`, seção 4 |
| Faturamento por Departamento e Laboratório | Gráfico de barras empilhadas: faturamento por Departamento, com quebra por Laboratório | Consulta direta de `faturamentos` agregada |
| Evolução Mensal | Gráfico de linha: faturamento total mês a mês dentro do Ano filtrado (ou dos últimos 12 meses quando nenhum Ano é filtrado) | Consulta direta de `faturamentos` agregada por `ano`/`mes` |
| Distribuição por Tipo de Promotor | Gráfico de rosca: proporção de Cobertura/Positivação entre Promotores Técnicos e Trade | `KPIS.md`, seções 8–9, quebrado por `tipo` |
| Ranking de Promotores | Lista ordenável dos promotores no escopo filtrado, por índice de desempenho combinado | `KPIS.md`, seção 10 |
| Fora da Carteira | Cartão de destaque + tabela de clientes faturando sem promotor vigente | `KPIS.md`, seção 5 |

### 2.3 Filtros Aplicáveis
Todos os filtros descritos em `API.md`, seção 3 (Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor) são aplicáveis ao Dashboard Executivo, sem restrição, para os perfis Administrador e Diretoria. Para o perfil Supervisor, o filtro de Supervisor é fixado ao próprio supervisor autenticado (`PERMISSOES.md`, seção 4.2).

### 2.4 Comportamento de Atualização
Qualquer alteração em qualquer filtro da `BarraDeFiltros` dispara uma única requisição a `GET /api/v1/dashboard/executivo` (`API.md`, seção 10), que retorna todos os blocos simultaneamente em um único payload, evitando múltiplas chamadas concorrentes e garantindo consistência entre os blocos (mesmo instante de corte de dados para todos os números exibidos).

### 2.5 Formato de Resposta (Estrutura de Referência)

```json
{
  "filtros_aplicados": { "ano": 2026, "mes": null, "uf": null, ... },
  "kpis": {
    "cobertura": { "valor": 0.812, "meta": 0.85 },
    "positivacao": { "valor": 0.734, "meta": 0.80 },
    "faturamento_total": 4123456.78,
    "faturamento_fora_da_carteira": 89210.55,
    "visitas_realizadas": 1342,
    "conformidade_checklist": 0.91
  },
  "faturamento_por_regiao": [ { "uf": "SP", "valor": 1500000.00 }, ... ],
  "faturamento_por_departamento": [ { "departamento": "Nutrição", "laboratorio": "LabX", "valor": 250000.00 }, ... ],
  "evolucao_mensal": [ { "ano": 2026, "mes": 1, "valor": 300000.00 }, ... ],
  "distribuicao_tipo_promotor": [ { "tipo": "TECNICO", "cobertura": 0.83, "positivacao": 0.75 }, { "tipo": "TRADE", "cobertura": 0.79, "positivacao": 0.71 } ],
  "ranking": [ { "promotor_id": 12, "nome": "Fulano", "indice": 0.88, "posicao": 1 }, ... ],
  "fora_da_carteira_clientes": [ { "cliente_id": 331, "razao_social": "Pet Shop X", "valor_faturado": 4200.00 }, ... ]
}
```

## 3. Dashboard por Promotor

### 3.1 Propósito
Visão individual de desempenho de um único promotor, utilizada pelo próprio Promotor (autoavaliação), pelo Supervisor (acompanhamento de equipe) e pela Diretoria/Administrador (auditoria pontual de desempenho).

### 3.2 Blocos do Dashboard por Promotor

| Bloco | Conteúdo | KPI/Fonte |
|---|---|---|
| Cabeçalho | Nome, Tipo de Promotor, Supervisor, período filtrado | Cadastro do promotor |
| Cartões de KPI Individuais | Cobertura, Positivação, Visitas Realizadas x Planejadas, Conformidade de Checklist | `KPIS.md`, seções 6–9 |
| Evolução de Faturamento da Carteira | Gráfico de linha: faturamento mensal somado da carteira do promotor | Consulta de `faturamentos` filtrada pelos clientes da carteira vigente do promotor |
| Carteira Detalhada | Tabela: cliente, cidade/UF, status de positivação no período, data da última visita | `KPIS.md`, seção 3 e 9 |
| Visitas no Período | Tabela: data, cliente, tipo de visita, status | Consulta direta de `visitas` |
| Checklists no Período | Tabela: data da visita, checklist aplicado, percentual de conformidade | `KPIS.md`, seção 7 |
| Posição no Ranking | Cartão: posição geral e posição dentro do próprio Tipo de Promotor | `KPIS.md`, seção 10 |

### 3.3 Filtros Aplicáveis
Apenas Ano e Mês (`TELAS.md`, seção 4). O `promotor_id` é fixado pela rota (`/dashboard/promotor/:id`), respeitando o escopo definido em `PERMISSOES.md`.

### 3.4 Formato de Resposta (Estrutura de Referência)

```json
{
  "promotor": { "id": 12, "nome": "Fulano", "tipo": "TECNICO", "supervisor": "Ciclana" },
  "filtros_aplicados": { "ano": 2026, "mes": 6 },
  "kpis": {
    "cobertura": 0.90,
    "positivacao": 0.78,
    "visitas_realizadas": 24,
    "visitas_planejadas": 26,
    "conformidade_checklist": 0.93
  },
  "evolucao_faturamento_carteira": [ { "ano": 2026, "mes": 1, "valor": 45000.00 }, ... ],
  "carteira": [ { "cliente_id": 88, "razao_social": "Clínica Y", "cidade": "Campinas", "uf": "SP", "positivado": true, "ultima_visita": "2026-06-14" }, ... ],
  "visitas": [ { "data": "2026-06-14", "cliente": "Clínica Y", "tipo_visita": "Rotina", "status": "REALIZADA" }, ... ],
  "checklists": [ { "data_visita": "2026-06-14", "checklist": "Checklist Trade Padrão", "conformidade": 1.0 }, ... ],
  "ranking": { "posicao_geral": 4, "total_geral": 38, "posicao_tipo": 2, "total_tipo": 19 }
}
```

## 4. Regra de Agregação por Equipe (Supervisor)

Quando um Supervisor acessa a listagem de equipe (`UX.md`, seção 7), o backend expõe uma variação agregada equivalente à estrutura da seção 2.5, porém pré-filtrada a `supervisor_id` do token, através do mesmo endpoint `GET /api/v1/dashboard/executivo` (`PERMISSOES.md`, seção 4.2, item 3) — não há endpoint HTTP adicional para este caso, apenas a aplicação do filtro obrigatório de escopo no backend.

## 5. Metas de Referência (Premissa Adotada)

Na ausência de definição explícita de metas por cliente/contrato, adotam-se as seguintes metas de referência, utilizadas exclusivamente para colorização de indicadores (`success`/`warning`/`danger` — `DESIGN_SYSTEM.md`, seção 3), sem qualquer efeito sobre o cálculo dos KPIs em si:

| KPI | Meta de Referência | Faixa de Atenção (warning) | Faixa Crítica (danger) |
|---|---|---|---|
| Cobertura | ≥ 85% | 70%–84,9% | < 70% |
| Positivação | ≥ 80% | 65%–79,9% | < 65% |
| Conformidade de Checklist | ≥ 90% | 75%–89,9% | < 75% |

Estas metas são configuráveis por tela administrativa em evolução futura (`ROADMAP.md`); na POC, são constantes definidas em `services/kpi_service.py` (`BACKEND.md`).

## 6. Regra de Anonimização no Ranking para Promotores

Conforme `PERMISSOES.md`, seção 4.3, item 4: quando exibido a um usuário com `perfil = PROMOTOR`, o bloco de Ranking (seção 2.2 e 3.2) exibe a posição e o índice do próprio promotor de forma nominal, e as demais posições do ranking de forma anônima (rótulo "Promotor #N", sem nome), preservando apenas a posição relativa como referência de desempenho.
