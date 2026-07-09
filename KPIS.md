# KPIS.md — Definição e Fórmulas dos KPIs

## 1. Finalidade

Este documento define, de forma precisa e não ambígua, a fórmula de cálculo de cada um dos 8 KPIs do Promotores BI: Carteira, Região, Fora da Carteira, Visitas, Checklists, Cobertura, Positivação e Ranking. Toda implementação em `services/kpi_service.py` (`BACKEND.md`) deve corresponder exatamente às fórmulas aqui descritas. A origem dos dados que alimentam estes cálculos está em `REGRAS_DE_NEGOCIO.md`, seção 7 (regra de seleção de versão corrente).

## 2. Convenções Comuns

1. Todo KPI é calculado sobre o conjunto de dados resultante da aplicação dos filtros ativos (`API.md`, seção 3), combinados com o escopo de acesso do usuário (`PERMISSOES.md`).
2. Toda divisão cujo denominador seja zero retorna `null` (ausência de dado), nunca erro nem `0` — a interface exibe "sem dados" (`EmptyState` ou indicador equivalente) nesse caso (`DESIGN_SYSTEM.md`).
3. Valores percentuais são calculados e retornados pela API como fração decimal (`0.812` = 81,2%), formatados como percentual apenas na camada de apresentação (`FRONTEND.md`, `utils/formatadores.js`).
4. Todo cálculo considera exclusivamente registros oriundos de importações com status elegível (`REGRAS_DE_NEGOCIO.md`, seção 7).

## 3. KPI — Carteira

**Definição:** quantidade e valor de clientes atualmente vinculados a um promotor, no período e filtros selecionados.

**Fórmula:**
```
Carteira(filtros) = COUNT(DISTINCT carteiras.cliente_id)
  WHERE carteiras.status = 'ATIVA'
    AND carteiras.data_fim_vigencia IS NULL
    AND <filtros de dimensão aplicados via join com clientes/promotores>
```

**Detalhamento adicional retornado:** valor de faturamento associado à carteira no período (`SUM(faturamentos.valor_faturado)` para os `cliente_id` presentes na carteira filtrada, no `ano`/`mes` filtrado).

## 4. KPI — Região

**Definição:** distribuição de faturamento, cobertura e positivação por UF/Cidade.

**Fórmula:**
```
Regiao(filtros) = GROUP BY clientes.uf_sigla (ou clientes.cidade_id, conforme o nível de detalhamento solicitado)
  SUM(faturamentos.valor_faturado) AS faturamento_total
  Cobertura(filtros + uf) AS cobertura_regional
  Positivacao(filtros + uf) AS positivacao_regional
```

Este KPI é essencialmente uma quebra dimensional dos KPIs de Faturamento, Cobertura e Positivação por UF/Cidade, e não introduz uma fórmula de cálculo própria além da agregação por dimensão geográfica.

## 5. KPI — Fora da Carteira

**Definição:** faturamento associado a clientes que, no período analisado, não possuem vínculo de carteira vigente com nenhum promotor.

**Fórmula:**
```
ForaDaCarteira(filtros) = SUM(faturamentos.valor_faturado)
  WHERE faturamentos.cliente_id NOT IN (
    SELECT cliente_id FROM carteiras
    WHERE status = 'ATIVA' AND data_fim_vigencia IS NULL
  )
  AND <filtros de ano/mes/uf/laboratorio/departamento aplicados>
```

**Nota:** este KPI, por definição, não é filtrável por Promotor, Supervisor ou Tipo de Promotor (não há promotor associado aos clientes que o compõem) — quando esses filtros estão ativos, o KPI retorna `null` com indicação de "não aplicável ao filtro selecionado" na interface.

## 6. KPI — Visitas

**Definição:** quantidade de visitas realizadas no período e filtros selecionados, comparada à quantidade planejada, quando disponível.

**Fórmula:**
```
VisitasRealizadas(filtros) = COUNT(visitas.id)
  WHERE visitas.status = 'REALIZADA'
    AND <filtros de ano/mes (via visitas.data_visita) e demais dimensões>

VisitasPlanejadas(filtros) = COUNT(visitas.id)
  WHERE visitas.status IN ('REALIZADA', 'PENDENTE')
    AND <mesmos filtros>
```

**Nota:** "Planejadas" é uma métrica derivada da soma de visitas com status `REALIZADA` e `PENDENTE` presentes na planilha de origem — a POC não possui um módulo de planejamento de rota independente; a meta de visitas é a quantidade total informada pela operação via planilha (premissa adotada, registrada em `PROJECT.md`, seção 9).

## 7. KPI — Checklists

**Definição:** percentual de conformidade das respostas de checklist no período e filtros selecionados.

**Fórmula:**
```
ConformidadeChecklist(filtros) =
  SUM(checklist_respostas.conforme = true ? checklist_perguntas.peso : 0)
  /
  SUM(checklist_perguntas.peso)
  WHERE checklist_respostas.conforme IS NOT NULL
    AND <filtros aplicados via join visitas -> promotor/cliente>
```

**Nota:** apenas perguntas do tipo `SIM_NAO` (as únicas com `conforme` calculado, conforme `REGRAS_DE_NEGOCIO.md`, seção 5.4, item 4) compõem este índice na POC. Perguntas de outros tipos (`MULTIPLA_ESCOLHA`, `NUMERICO`, `TEXTO`) são exibidas informativamente nas telas de detalhe (`TELAS.md`), mas não compõem o índice numérico de conformidade.

## 8. KPI — Cobertura

**Definição:** percentual de clientes da carteira vigente que foram efetivamente visitados no período filtrado.

**Fórmula:**
```
Cobertura(filtros) =
  COUNT(DISTINCT cliente_id da carteira vigente QUE POSSUI ao menos uma visita com status = 'REALIZADA' dentro do período filtrado)
  /
  COUNT(DISTINCT cliente_id da carteira vigente, dentro dos demais filtros de dimensão)
```

**Nota:** quando o filtro de Mês não é informado (apenas Ano, ou nenhum período), a "cobertura" considera qualquer visita realizada dentro do Ano filtrado (ou, na ausência de filtro de Ano, dentro dos últimos 12 meses a partir da data corrente — premissa adotada para evitar que a ausência de filtro temporal produza um resultado sem sentido de negócio).

## 9. KPI — Positivação

**Definição:** percentual de clientes da carteira vigente que apresentaram faturamento maior que zero no período filtrado.

**Fórmula:**
```
Positivacao(filtros) =
  COUNT(DISTINCT cliente_id da carteira vigente COM SUM(faturamentos.valor_faturado) > 0 no período filtrado)
  /
  COUNT(DISTINCT cliente_id da carteira vigente, dentro dos demais filtros de dimensão)
```

**Nota:** clientes com faturamento líquido negativo no período (predominância de estornos — `REGRAS_DE_NEGOCIO.md`, seção 5.3, item 4) **não** são considerados positivados (`SUM > 0`, estritamente maior que zero).

## 10. KPI — Ranking

**Definição:** ordenação dos promotores no escopo filtrado, por um índice de desempenho combinado.

**Fórmula do Índice de Desempenho:**
```
Indice(promotor, filtros) =
    (Cobertura(promotor, filtros)    * 0.35)
  + (Positivacao(promotor, filtros)  * 0.35)
  + (ConformidadeChecklist(promotor, filtros) * 0.20)
  + (min(VisitasRealizadas(promotor, filtros) / VisitasPlanejadas(promotor, filtros), 1.0) * 0.10)
```

**Regras de desempate:** em caso de índice idêntico entre dois ou mais promotores, o desempate ocorre, em ordem: (1) maior Positivação; (2) maior Cobertura; (3) ordem alfabética do nome.

**Ranking Geral vs. Ranking por Tipo:** o Ranking Geral ordena todos os promotores do escopo filtrado; o Ranking por Tipo ordena separadamente Promotores Técnicos e Promotores Trade, pois os dois perfis têm naturezas de atuação distintas (`PROJECT.md`, seção 2) e não devem ser comparados pelo mesmo índice absoluto sem segmentação — ambos os rankings são expostos simultaneamente (`DASHBOARD.md`, seção 3.4, campo `ranking`).

**Justificativa dos pesos:** os pesos (35/35/20/10) são uma premissa adotada, documentada aqui como parâmetro de negócio configurável em `services/kpi_service.py` (`BACKEND.md`), passível de ajuste futuro por decisão de negócio sem impacto na arquitetura.

## 11. Resumo de Filtros Aplicáveis por KPI

| KPI | Ano/Mês | UF/Cidade | Departamento/Laboratório | Supervisor/Vendedor/Promotor | Tipo de Promotor |
|---|:---:|:---:|:---:|:---:|:---:|
| Carteira | Sim | Sim | Não | Sim | Sim |
| Região | Sim | Sim (dimensão de quebra) | Sim | Sim | Sim |
| Fora da Carteira | Sim | Sim | Sim | Não (ver seção 5, nota) | Não |
| Visitas | Sim | Sim | Não | Sim | Sim |
| Checklists | Sim | Sim | Não | Sim | Sim |
| Cobertura | Sim | Sim | Não | Sim | Sim |
| Positivação | Sim | Sim | Sim | Sim | Sim |
| Ranking | Sim | Sim | Não | Sim (exceto Promotor individual, que define o escopo do próprio ranking) | Sim |

## 12. Cache e Desempenho de Cálculo (POC)

Todos os KPIs são calculados sob demanda a cada requisição, via consultas agregadas diretamente sobre as tabelas de fato (`DATABASE.md`, seção 6). Não há cache nem tabela de agregação materializada na POC — decisão consistente com o volume de dados esperado em ambiente de demonstração. Introdução de cache (ex.: agregações pré-calculadas em job noturno) é item de evolução pós-POC (`ROADMAP.md`).
