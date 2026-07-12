# IMPORT_MAPPING.md — Mapeamento dos Importadores Reais (Sprint 3)

> Substitui, para as fontes reais, o mapeamento long/documental de `IMPORTADOR.md`
> (Sprint 2). Cada conector vive em `backend/etl/conectores/` e implementa
> `ConectorOrigem.processar(caminho, execucao) -> ResultadoConector`
> (Strategy Pattern — `docs/DECISIONS.md`, seções 11.6 e 14). Nomes de coluna
> são casados por versão normalizada (maiúsculas, sem acento, espaços →
> underscore), nunca por posição fixa nem pelo nome do arquivo.

## 1. Base de Clientes (`TipoArquivoImportacao.CLIENTES`)

Conector: `ConectorBaseClientes`. Estrutura real: 1 aba, 22 colunas, 1 linha = 1 cliente.

| Coluna do export | Campo de destino | Obrigatória |
|---|---|---|
| Código | `clientes.codigo_externo` | Sim |
| Cliente | `clientes.razao_social` | Sim |
| Estado | `clientes.uf_sigla` | Sim |
| Nome da Cidade | `clientes.cidade_id` (get-or-create por nome+UF) | Sim |
| Fantasia | `clientes.nome_fantasia` | Não |
| CNPJ/CPF | `clientes.cnpj_cpf` | Não |
| Insc. Est. / Produtor | `clientes.inscricao_estadual` | Não |
| Tipo de Pessoa | `clientes.tipo_pessoa` | Não |
| Ramo Atividade | `clientes.ramo_atividade` | Não |
| Endereço Comercial | `clientes.endereco` | Não |
| Número | `clientes.numero` | Não |
| Bairro | `clientes.bairro` | Não |
| CEP | `clientes.cep` | Não |
| Telefone | `clientes.telefone` | Não |
| Data da Última Compra | `clientes.data_ultima_compra` | Não |
| RCA 1..4 + Nome RCA (posicional) | `clientes_vendedores` (1 linha por RCA preenchido, `ordem` preservada) | Não |

Upsert por `codigo_externo`; mudança de valor cadastral gera `logs_auditoria`. RCA ausente numa reimportação remove o vínculo (snapshot cadastral).

## 2. Faturamento mensal (`TipoArquivoImportacao.FATURAMENTO`)

Conector: `ConectorFaturamentoMatriz`. Estrutura real: matriz wide (linha 1 = marcas, linha 2 = rótulo, linhas de dados = `"<código> - <razão social>"` × valor por marca, rodapé "Filtros aplicados").

| Elemento do export | Campo de destino |
|---|---|
| Coluna de marca (ex.: BBPET, AVERT, BRINDE) | `laboratorios.nome` (get-or-create); `categoria=BRINDE` só para a marca BRINDE, as demais `LABORATORIO` |
| `"<código> - <razão social>"` | `faturamentos.cliente_id` (resolvido pelo código antes do hífen) |
| Valor da célula cliente×marca | `faturamentos.valor_faturado` (1 linha por célula preenchida — wide→long) |
| Rodapé "Incluídos (1) `<ano>` (Ano) + `<mês>` (Mês)" | `faturamentos.ano`/`mes` e `importacoes.competencia` |

Sem quantidade, vendedor ou departamento na origem (`departamento_id` fica nulo). Reimportação com valor divergente para o mesmo cliente×marca×competência é rejeitada por célula — nunca sobrescreve.

## 3. Carteira mensal oficial — relatório Supervisor do SB Promotor (`TipoArquivoImportacao.CARTEIRA`)

Conector: `ConectorSbSupervisor`. Estrutura real: 1 aba, 16 colunas em 2 blocos lado a lado com cabeçalhos repetidos ("Código"/"Nome" aparecem 2×) — mapeamento **posicional**, não por nome.

| Bloco | Colunas (posição) | Campo de destino |
|---|---|---|
| Promotor | Código (0), Nome (1), Área (2) | `promotores.codigo_externo`/`nome`/`area` (get-or-create) |
| Promotor | Visitas Previstas..Não Prevista Realizadas (3–6) | `visitas_resumo_sb.visitas_previstas`..`nao_previstas_realizadas` |
| Cliente | Código (7) | `carteiras.cliente_id` / `visitas_resumo_sb.cliente_id` |
| Cliente | Nome Fantasia (8), Razão Social (9) | usados só para a pendência em `clientes_integracao` quando o código não existe |
| Cliente | Visitas Previstas..Não Visitas (10–12) | `visitas_resumo_sb.cliente_visitas_previstas`..`cliente_nao_visitas` |
| Cliente | 3 colunas de percentual (13–15) | `visitas_resumo_sb.perc_visitas_a_realizar`/`perc_visitas_realizadas`/`perc_nao_visitas` |

`competencia` é **obrigatória** e vem do parâmetro da importação (o arquivo não a contém). Cada linha promotor×cliente vira 1 registro em `visitas_resumo_sb` (upsert por competência) e deriva a vigência de `carteiras`: promotor igual ao vigente é idempotente; diferente encerra o vínculo anterior e cria um novo; cliente vigente ausente do arquivo é encerrado (snapshot completo). Cliente sem correspondência na Base vira pendência em `clientes_integracao` (sistema `SB_PROMOTOR`), nunca cria cliente.

## 4. Detalhe de produtos por visita — SB Promotor (`TipoArquivoImportacao.SB_PRODUTOS`)

Conector: `ConectorSbProdutos`. Estrutura real: arquivo com 4 abas (`Produtos`, `Gondola`, `ProdutoSimilar`, `Tarefas`); dados observados só em `Produtos`.

| Coluna do export | Campo de destino |
|---|---|
| VISITA | `visitas_produtos_sb.codigo_visita_externa` |
| CÓDIGO / FUNCIONARIO | `visitas_produtos_sb.promotor_id` (get-or-create por código) |
| REGIÃO | `visitas_produtos_sb.uf_sigla` |
| COD. CLIENTE | `visitas_produtos_sb.cliente_id` (obrigatório existir; senão pendência) |
| DATA INICIAL / DATA FINAL | `visitas_produtos_sb.data_inicial`/`data_final` |
| OPERAÇÃO, GRUPO, MARCA | `visitas_produtos_sb.operacao`/`grupo_marca`/`marca` |
| COD. PRODUTO, PRODUTO, VALIDADE, LOTE, ESTOQUE, PREÇO, OBSERVAÇÃO | campos homônimos |

Idempotência por `(codigo_visita_externa, codigo_produto, lote)`. Abas com dados fora de `Produtos` geram alerta em vez de serem descartadas silenciosamente.

## 5. Checklists (`TipoArquivoImportacao.CHECKLIST`)

Conector: `ConectorChecklistSb` (usa `etl/conectores/checklist_comum.py`, compartilhado com WeCheck). Estrutura real: 1 aba por template (8 observadas), todas com as mesmas 42 colunas — 10 de contexto (com `CÓDIGO` repetido: promotor e depois cliente) + 32 de pergunta (união de todos os templates).

| Elemento do export | Campo de destino |
|---|---|
| Nome da aba / CHECKLIST / CK_ID | `checklists` (get-or-create por `(origem=SB_PROMOTOR, codigo_externo=CK_ID)`) |
| CÓDIGO (1ª ocorrência) / FUNCIONÁRIO | `visitas.promotor_id` |
| CÓDIGO (2ª ocorrência) | `visitas.cliente_id` (obrigatório existir; senão pendência) |
| VISITA | `visitas.codigo_externo` — **1 linha = 1 visita** |
| APLICAÇÃO | `visitas.data_visita`/`hora_inicio` |
| UF, RAZÃO SOCIAL, FANTASIA | `visitas.dados_brutos` (JSON, contexto preservado) |
| Cada coluna de pergunta | `checklist_perguntas` (get-or-create por enunciado; `tipo_resposta=TEXTO`, `obrigatoria=False` — nunca inferidos) |
| Célula de pergunta preenchida | `checklist_respostas` (1 por célula não vazia — wide→long) |

Idempotência por `(origem, codigo_externo=VISITA)`; resposta já registrada com valor diferente é erro de linha (nunca sobrescreve), idêntica é no-op.

## 6. WeCheck — formulários das promotoras Avert (`TipoArquivoImportacao.WECHECK`)

Conector: `ConectorWeCheck` (mesma lógica de template/pergunta/resposta do item 5). Estrutura real: 1 aba por formulário (schema drift real entre meses — 26 a 31 colunas).

| Elemento do export | Campo de destino |
|---|---|
| Nome do formulário (ou aba) | `checklists` (get-or-create por `(origem=WECHECK, nome)`) |
| Autor | `promotores` (get-or-create **por nome**, comparação case-insensitive em Python; tipo TRADE aplicado só na criação) |
| Data / Hora do Item | `visitas.data_visita`/`hora_inicio` |
| Local | `clientes_integracao` (sistema `WECHECK`; **nunca casamento fuzzy**; `visitas.cliente_id` só é preenchido se já houver vínculo VINCULADO) |
| Endereço, Cidade, Estado | `visitas.endereco_texto`/`cidade_texto`/`estado_texto` |
| Tarefa, Descrição, Perfil, Validado, Status da Tarefa, Data de Abertura (Evento) — quando presentes no mês | `visitas.dados_brutos` (JSON) |
| Demais colunas (perguntas do formulário) | `checklist_perguntas`/`checklist_respostas`, tolerando colunas ausentes/novas por mês |

A origem não expõe id de visita: `codigo_externo` é derivado deterministicamente via SHA-256(formulário\|autor\|data/hora\|local), garantindo idempotência de reimportação.

## 7. Painel Trade Avert (`TipoArquivoImportacao.PAINEL_AVERT`)

Conector: `ConectorPainelAvert`. Estrutura real: 1 aba, 16 colunas, 1 linha = 1 cliente da carteira Avert (carteira oficial da operação, decisão 12.5).

| Coluna do export | Campo de destino |
|---|---|
| CNPJ | `carteiras_avert.cnpj` + casamento com `clientes.cnpj_cpf` (comparação só de dígitos, determinística) |
| CONSULTOR | `promotores` (get-or-create por nome; é a **promotora**, tipo TRADE) |
| UF, ÁREA, REGIONAL, DISTRIBUIDOR, COORDENADOR, VENDEDOR, GRUPO ECONÔMICO, NOME FANTASIA, RAZÃO SOCIAL, SEGMENTO, OBS | colunas homônimas em `carteiras_avert` (preservadas mesmo vazias) |
| COMPRA 2025, COMPRA 2026, CRESC | `carteiras_avert.compra_2025`/`compra_2026`/`crescimento` |

CNPJ sem correspondência interna vira pendência em `clientes_integracao` (nunca cria cliente); CNPJ correspondente a mais de um cliente interno (documento duplicado no cadastro) fica pendente com observação, em vez de escolher arbitrariamente.

## 8. Ordem de dependência

1. Base de Clientes (pré-requisito de todas as demais, exceto WeCheck que não referencia cliente diretamente)
2. SB Promotor — Supervisor (carteira) e Produtos (independentes entre si)
3. Faturamento, Checklist, WeCheck, Painel Avert (podem rodar em qualquer ordem entre si, após Clientes)
