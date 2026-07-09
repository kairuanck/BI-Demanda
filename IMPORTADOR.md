# IMPORTADOR.md — Especificação dos Importadores por Tipo de Arquivo

## 1. Finalidade

Este documento especifica, para cada um dos 5 tipos de arquivo importáveis pelo Promotores BI, o layout de colunas esperado, o mapeamento para as entidades do modelo de dados (`DICIONARIO_DE_DADOS.md`), a chave de conciliação e as regras de resolução de dimensões. O pipeline comum a todos os importadores está em `ETL.md`; as regras de validação linha a linha estão em `VALIDADOR.md`; as regras de negócio de versionamento estão em `REGRAS_DE_NEGOCIO.md`.

## 2. Convenções Gerais de Layout

1. Todo arquivo é `.xlsx`, com cabeçalho na primeira linha e dados a partir da segunda linha.
2. Nomes de coluna são comparados de forma normalizada (maiúsculas, sem acentuação, espaços internos convertidos para underscore) para tolerar pequenas variações de digitação no cabeçalho.
3. Datas podem ser fornecidas como data nativa do Excel ou como texto no formato `DD/MM/AAAA`.
4. Valores monetários podem ser fornecidos com separador decimal `,` ou `.`; o importador normaliza para `Decimal` com 2 casas.
5. Campos de código (`codigo_externo`) são sempre tratados como texto, mesmo quando numericamente representados, para preservar zeros à esquerda.

## 3. Importador — Base de Clientes (`tipo_arquivo = CLIENTES`)

### 3.1 Colunas Esperadas

| Coluna no arquivo | Campo de destino | Obrigatória |
|---|---|---|
| CODIGO_CLIENTE | `clientes.codigo_externo` | Sim |
| RAZAO_SOCIAL | `clientes.razao_social` | Sim |
| NOME_FANTASIA | `clientes.nome_fantasia` | Não |
| CNPJ_CPF | `clientes.cnpj_cpf` | Não |
| UF | `clientes.uf_sigla` | Sim |
| CIDADE | `clientes.cidade_id` (resolvido por nome + UF) | Sim |
| ENDERECO | `clientes.endereco` | Não |
| CANAL | `clientes.canal` | Não |

### 3.2 Resolução de Dimensões
1. `UF`: deve corresponder a uma sigla existente em `ufs`. Sigla inexistente gera erro de validação (não há criação automática de UF).
2. `CIDADE`: buscada por `(nome, uf_sigla)` em `cidades`. Se não encontrada, um novo registro de `cidades` é criado automaticamente, vinculado à UF informada.

### 3.3 Regra de Persistência
Conforme `REGRAS_DE_NEGOCIO.md`, seção 5.1: upsert por `codigo_externo` (atualiza cliente existente; cria se inédito).

## 4. Importador — Carteira dos Promotores (`tipo_arquivo = CARTEIRA`)

### 4.1 Colunas Esperadas

| Coluna no arquivo | Campo de destino | Obrigatória |
|---|---|---|
| CODIGO_CLIENTE | `carteiras.cliente_id` (resolvido por `codigo_externo`) | Sim |
| CODIGO_PROMOTOR | `carteiras.promotor_id` (resolvido por `codigo_externo`) | Sim |
| NOME_PROMOTOR | usado apenas para criação de Promotor quando `CODIGO_PROMOTOR` é inédito | Sim (se promotor inédito) |
| TIPO_PROMOTOR | `promotores.tipo` (usado apenas na criação do promotor) | Sim (se promotor inédito) |
| CODIGO_SUPERVISOR | `promotores.supervisor_id` (resolvido por `codigo_externo`) | Sim |
| NOME_SUPERVISOR | usado apenas para criação de Supervisor quando `CODIGO_SUPERVISOR` é inédito | Sim (se supervisor inédito) |
| DATA_REFERENCIA | data de referência da vigência (`carteiras.data_inicio_vigencia` / `data_fim_vigencia`) | Sim |

### 4.2 Resolução de Dimensões
1. `CODIGO_CLIENTE`: deve existir previamente em `clientes` (importado via arquivo de Base de Clientes). Cliente inexistente gera erro de validação — a Carteira **não cria** clientes novos.
2. `CODIGO_SUPERVISOR`: se inédito, cria automaticamente um novo registro em `supervisores` com os dados de `NOME_SUPERVISOR`.
3. `CODIGO_PROMOTOR`: se inédito, cria automaticamente um novo registro em `promotores`, com `tipo` obtido de `TIPO_PROMOTOR` (valores aceitos: `TECNICO`, `TRADE`, normalizados) e `supervisor_id` já resolvido. Se o promotor já existir e `CODIGO_SUPERVISOR` for diferente do supervisor atualmente vinculado, o campo `promotores.supervisor_id` é atualizado (mudança de supervisão é tratada como atualização cadastral direta, não como fato versionado, conforme premissa de `PROJECT.md`, seção 9, item 4).

### 4.3 Regra de Persistência
Conforme `REGRAS_DE_NEGOCIO.md`, seção 5.2: versionamento de vigência — encerramento do vínculo anterior e criação de novo vínculo quando o promotor de um cliente muda; encerramento de vínculo para clientes ausentes no novo arquivo.

## 5. Importador — Faturamento Mensal (`tipo_arquivo = FATURAMENTO`)

### 5.1 Colunas Esperadas

| Coluna no arquivo | Campo de destino | Obrigatória |
|---|---|---|
| CODIGO_CLIENTE | `faturamentos.cliente_id` (resolvido por `codigo_externo`) | Sim |
| CODIGO_LABORATORIO | `faturamentos.laboratorio_id` (resolvido por `codigo_externo`) | Sim |
| NOME_LABORATORIO | usado apenas para criação quando `CODIGO_LABORATORIO` é inédito | Sim (se inédito) |
| CODIGO_DEPARTAMENTO | `faturamentos.departamento_id` (resolvido por `codigo_externo`) | Sim |
| NOME_DEPARTAMENTO | usado apenas para criação quando `CODIGO_DEPARTAMENTO` é inédito | Sim (se inédito) |
| CODIGO_VENDEDOR | `faturamentos.vendedor_id` (resolvido por `codigo_externo`) | Não |
| NOME_VENDEDOR | usado apenas para criação quando `CODIGO_VENDEDOR` é inédito | Não |
| ANO | `faturamentos.ano` | Sim |
| MES | `faturamentos.mes` | Sim |
| VALOR_FATURADO | `faturamentos.valor_faturado` | Sim |
| QUANTIDADE | `faturamentos.quantidade` | Não |

### 5.2 Resolução de Dimensões
1. `CODIGO_CLIENTE`: deve existir previamente em `clientes`. Cliente inexistente gera erro de validação.
2. `CODIGO_LABORATORIO` e `CODIGO_DEPARTAMENTO`: se inéditos, criam automaticamente novos registros em `laboratorios`/`departamentos`.
3. `CODIGO_VENDEDOR`: se informado e inédito, cria automaticamente novo registro em `vendedores`. Se a coluna estiver vazia, `faturamentos.vendedor_id` é gravado como `NULL`.

### 5.3 Regra de Persistência
Conforme `REGRAS_DE_NEGOCIO.md`, seção 5.3: inserção pura (append), sem atualização de linhas existentes; versões anteriores do mesmo período permanecem no banco, mas são desconsideradas nas consultas analíticas em favor da versão mais recente não revertida.

## 6. Importador — Checklists (`tipo_arquivo = CHECKLIST`)

### 6.1 Colunas Esperadas

| Coluna no arquivo | Campo de destino | Obrigatória |
|---|---|---|
| ID_VISITA | `checklist_respostas.visita_id` | Sim |
| ORDEM_PERGUNTA | usado para localizar `checklist_perguntas` dentro do checklist do template ativo | Sim |
| RESPOSTA | `checklist_respostas.resposta_valor` | Sim |

### 6.2 Resolução de Dimensões
1. `ID_VISITA`: deve existir previamente em `visitas` (importada via arquivo de Visitas). Visita inexistente gera erro de validação.
2. `ORDEM_PERGUNTA`: resolvida dentro do `checklist_id` correspondente ao `tipo_promotor_alvo` do promotor responsável pela visita, considerando o template `ativo = true` de maior `versao`. Ordem inexistente no template gera erro de validação.
3. `RESPOSTA`: validada conforme `tipo_resposta` da pergunta (`VALIDADOR.md`).

### 6.3 Regra de Persistência
Conforme `REGRAS_DE_NEGOCIO.md`, seção 5.4: inserção de nova resposta vinculada à importação corrente; cálculo automático de `conforme` para perguntas `SIM_NAO`.

## 7. Importador — Visitas (`tipo_arquivo = VISITAS`)

### 7.1 Colunas Esperadas

| Coluna no arquivo | Campo de destino | Obrigatória |
|---|---|---|
| CODIGO_PROMOTOR | `visitas.promotor_id` (resolvido por `codigo_externo`) | Sim |
| CODIGO_CLIENTE | `visitas.cliente_id` (resolvido por `codigo_externo`) | Sim |
| DATA_VISITA | `visitas.data_visita` | Sim |
| HORA_INICIO | `visitas.hora_inicio` | Não |
| HORA_FIM | `visitas.hora_fim` | Não |
| TIPO_VISITA | `visitas.tipo_visita` | Não |
| LATITUDE | `visitas.latitude` | Não |
| LONGITUDE | `visitas.longitude` | Não |
| OBSERVACOES | `visitas.observacoes` | Não |
| STATUS | `visitas.status` | Não (default `REALIZADA`) |

### 7.2 Resolução de Dimensões
1. `CODIGO_PROMOTOR`: deve existir previamente em `promotores`. Promotor inexistente gera erro de validação — a Visita **não cria** promotores novos.
2. `CODIGO_CLIENTE`: deve existir previamente em `clientes`. Cliente inexistente gera erro de validação.

### 7.3 Regra de Persistência
Conforme `REGRAS_DE_NEGOCIO.md`, seção 5.5: inserção pura (append) por linha, sem deduplicação por conteúdo.

## 8. Ordem de Dependência entre Importadores

Para que os importadores relacionais funcionem sem erro de validação por dimensão inexistente, a ordem recomendada de primeira carga é:

```
1. CLIENTES
2. CARTEIRA
3. FATURAMENTO
4. VISITAS
5. CHECKLIST
```

Esta ordem é orientativa para a **primeira carga** de um ambiente novo; em operação corrente, cada tipo de arquivo é reimportado de forma independente, respeitando apenas a exigência de que os Clientes, Promotores e Visitas referenciados já existam (seções 3 a 7).

## 9. Mapeamento de Colunas — Tolerância e Erros

1. Colunas obrigatórias ausentes no cabeçalho do arquivo interrompem a importação inteira antes da Etapa 4 do ETL (`ETL.md`), com mensagem de erro estrutural (não linha a linha).
2. Colunas não mapeadas (extras) no arquivo são ignoradas silenciosamente.
3. Colunas obrigatórias presentes no cabeçalho, mas vazias em uma linha específica, geram erro de validação daquela linha (`VALIDADOR.md`), sem interromper as demais linhas do arquivo.
