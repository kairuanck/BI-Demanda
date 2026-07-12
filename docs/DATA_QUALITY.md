# DATA_QUALITY.md — Qualidade dos Dados Reais (Sprint 3, Fase 6)

> Métricas calculadas por `app/services/qualidade_dados_service.py` (consultas
> somente-leitura) após a carga completa dos 5 pacotes reais via `etl/cli.py`
> (Fase 5). Números apenas — nenhum CNPJ, razão social ou nome de pessoa é
> reproduzido aqui (o repositório é público). O banco carregado com os dados
> reais existe apenas no ambiente de execução (`database/`, `imports/`,
> ambos git-ignored) e não foi commitado.

## 1. Carga executada

| Fonte | Arquivos processados | Resultado |
|---|---|---|
| Base de Clientes | 1 | `CONCLUIDA_COM_ERROS` — 21.940/21.942 linhas válidas |
| SB Promotor — Supervisor (carteira) | 35 (34 cópias + 1x rejeitado por engano de inferência¹) | 1 `CONCLUIDA_COM_ERROS` (18.101/18.123) + 33 recusados como **duplicata de conteúdo** |
| SB Promotor — detalhe de produtos | 1 | `CONCLUIDA` — 16/16 linhas válidas |
| Faturamento (6 meses) | 6 | Todos `CONCLUIDA` ou `CONCLUIDA_COM_ERROS` |
| Checklists (26 cópias) | 26 | 1 `CONCLUIDA` (1.986/1.986) + 25 recusados como **duplicata de conteúdo** |
| WeCheck (6 meses) | 6 | Todos `CONCLUIDA` ou `CONCLUIDA_COM_ERROS` |
| Painel Avert | 1 | `CONCLUIDA` — 205/205 linhas válidas |

¹ Nota técnica: das 35 cópias do pacote SB Promotor, 34 são o relatório Supervisor e 1 é o arquivo de detalhe (`Produtos`); a inferência estrutural (`etl/cli.py`) roteou corretamente as 34 para `CARTEIRA` e a 1 para `SB_PRODUTOS` — nenhum arquivo foi mal classificado.

A deduplicação por **hash de conteúdo** (decisão 11.2/14.2) funcionou exatamente como projetado: 33 das 34 cópias do Supervisor e 25 das 26 cópias do Checklist — fisicamente distintas em bytes, idênticas em conteúdo de células — foram recusadas como duplicatas, exatamente a assinatura descrita em `DATA_PROFILING.md`, seção 1.

## 2. Cobertura entre fontes

| Métrica | Valor |
|---|---|
| Total de clientes cadastrados | 21.940 |
| Clientes com ao menos 1 lançamento de faturamento (algum dos 6 meses) | 7.794 (35,52%) |
| Clientes com carteira SB ativa (vínculo promotor×cliente vigente) | 8.056 (36,72%) |
| Carteira Avert: CNPJs vinculados a cliente interno | 162 / 205 (79,02%) |

A cobertura de ~36% em faturamento/carteira **não é uma anomalia de importação**: reflete que a Base de Clientes (21.940 registros) é um cadastro histórico amplo, enquanto carteira e faturamento mensal cobrem apenas a base ativa/operacional — consistente com o que a Fase 1 já indicava (8.068 clientes na carteira SB, ~3.600 clientes/mês em faturamento).

## 3. Pendências de conciliação (`clientes_integracao`)

| Sistema de origem | Identificador | Pendências | Observação |
|---|---|---|---|
| SB_PROMOTOR | Código de cliente do relatório Supervisor | 12 | Códigos citados na carteira sem correspondência na Base de Clientes |
| PAINEL_AVERT | CNPJ | 43 | CNPJs da carteira Avert sem correspondência na Base de Clientes |
| WECHECK | `Local` (texto livre) | 152 | Locais distintos citados nas visitas, sem código de cliente na origem — proibido casamento fuzzy (decisão 12.4) |

Nenhuma dessas pendências gerou cliente automaticamente (regra de negócio 12.4/12.5): todas ficam com `status=PENDENTE` em `clientes_integracao`, disponíveis para conciliação manual futura.

## 4. Anomalias cadastrais herdadas do ERP de origem

| Achado | Valor |
|---|---|
| Documentos (CNPJ/CPF) usados por mais de um cliente distinto | 77 documentos, afetando 154 cadastros |
| Linhas de Base de Clientes sem cidade preenchida (rejeitadas) | 2 |
| Código de cliente citado no Faturamento sem cadastro correspondente | 1 (mês de Janeiro) |

Confirma exatamente os achados da Fase 1 (`DATA_PROFILING.md`, seção 2). Nenhum desses registros foi fundido, descartado ou "corrigido" pela importação — a regra "nunca simplificar dados" foi seguida à risca: documentos duplicados permanecem como clientes distintos; linhas inválidas foram rejeitadas por linha/célula com motivo registrado em `importacao_erros`.

## 5. Achado de correção durante a Fase 5 (nomes acentuados)

Ao rodar a carga real completa, `promotores` chegou a **93 registros** na primeira execução — muito acima do esperado (37 promotores SB + poucas promotoras/consultoras WeCheck/Avert). Investigação encontrou um bug real: `obter_ou_criar_promotor_por_nome` comparava nomes via `func.lower()` do SQL, e o `LOWER()` nativo do SQLite **não faz case-folding de caracteres acentuados** (`"Ú"` permanece `"Ú"`, nunca vira `"ú"`), enquanto o Python normaliza corretamente. Resultado: uma promotora com nome acentuado (ex.: "JÚLIA") criava um registro novo a cada visita processada, em vez de reaproveitar o existente.

**Correção:** a comparação passou a ser feita inteiramente em Python (`str.casefold`), sem depender do `LOWER()` do banco. Após a correção, a recarga completa produziu **45 promotores** (37 com código SB + 8 identificados só por nome — WeCheck/Avert), número consistente com a Fase 1 (WeCheck: 3 autoras; Painel Avert: 5 consultoras). Um teste de regressão (`test_wecheck_nome_acentuado_nao_duplica_promotora`) cobre este caso. Detalhe técnico em `docs/DECISIONS.md`, seção 15.

## 6. Limitações conhecidas

1. **Painel Avert e WeCheck identificam pessoas só por nome** (sem código); a resolução por nome usa comparação exata (case-insensitive), não fuzzy — grafias diferentes da mesma pessoa entre sistemas permanecem como registros distintos, por definição de negócio (12.4).
2. **`clientes_integracao` não é conciliada automaticamente** — é uma fila para revisão humana futura (fora do escopo desta sprint).
3. Os números deste relatório refletem uma carga de referência (Junho/2026 para SB e Painel Avert; Jan–Jun/2026 para Faturamento e WeCheck) e mudarão a cada nova competência importada.
