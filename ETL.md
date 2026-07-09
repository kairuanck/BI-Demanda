# ETL.md — Processo de Extração, Transformação e Carga

## 1. Finalidade

Este documento descreve o pipeline ETL (Extract, Transform, Load) genérico utilizado por todos os importadores do Promotores BI. A especificação de cada importador específico está em `IMPORTADOR.md`; as regras de validação em `VALIDADOR.md`; a estratégia de hash/versionamento em `HASH.md`; e o registro de eventos em `LOGS.md`.

## 2. Escopo do ETL

O ETL do Promotores BI é **acionado manualmente** pelo usuário (Administrador ou Supervisor, conforme `PERMISSOES.md`), via upload de planilha Excel na interface web. Não há, na POC, agendamento automático nem integração via API externa — esta é uma premissa de escopo registrada em `PROJECT.md`, seção 5.

## 3. Etapas do Pipeline

O pipeline é único e genérico para os 5 tipos de arquivo, parametrizado por `tipo_arquivo`. Toda etapa é implementada na camada `services/importacao/` (`BACKEND.md`).

```
┌──────────┐   ┌───────────┐   ┌────────────┐   ┌───────────────┐   ┌──────────────┐   ┌──────────┐
│ 1. Upload│──►│2. Extract │──►│3. Transform│──►│4. Validate     │──►│5. Hash/Version│──►│6. Load   │
│          │   │(Pandas)   │   │(Normalize) │   │(VALIDADOR.md)  │   │(HASH.md)       │   │(persist) │
└──────────┘   └───────────┘   └────────────┘   └───────────────┘   └──────────────┘   └──────────┘
                                                                                                │
                                                                                                ▼
                                                                                         ┌──────────────┐
                                                                                         │7. Audit Log  │
                                                                                         │(LOGS.md)     │
                                                                                         └──────────────┘
```

### 3.1 Etapa 1 — Upload
1. O usuário seleciona o `tipo_arquivo` na interface (`TELAS.md`, tela "Importação") e envia um arquivo `.xlsx`.
2. O backend recebe o arquivo via endpoint `POST /importacoes` (`API.md`), armazena o binário em disco (`importacao_arquivos`, ver `DEPLOY.md` para o diretório de armazenamento) e cria um registro em `importacoes` com `status = PENDENTE`.
3. Validações estruturais mínimas nesta etapa: extensão `.xlsx`, tamanho máximo de 20 MB, arquivo não corrompido (abertura válida via OpenPyXL).

### 3.2 Etapa 2 — Extract
1. O arquivo é lido com **Pandas** (`pandas.read_excel`, engine `openpyxl`), utilizando o mapeamento de colunas esperado por `tipo_arquivo` (`IMPORTADOR.md`).
2. A leitura considera a primeira aba (planilha) do arquivo, com cabeçalho na primeira linha, salvo exceção documentada por tipo de arquivo em `IMPORTADOR.md`.
3. O resultado é um `DataFrame` bruto, mantendo todos os valores como lidos (sem conversão de tipo nesta etapa).

### 3.3 Etapa 3 — Transform
1. Normalização de nomes de colunas (trim, uppercase para comparação, mapeamento para os nomes canônicos definidos em `IMPORTADOR.md`).
2. Normalização de valores textuais: `trim()`, remoção de espaços duplicados, padronização de caixa quando aplicável (ex.: siglas de UF em maiúsculas).
3. Conversão de tipos conforme o dicionário de dados de destino (`DICIONARIO_DE_DADOS.md`): strings para `Decimal` (valores monetários), strings para `date`/`datetime`, strings para os Enums esperados.
4. Remoção de linhas completamente vazias (todas as colunas nulas), sem gerar erro de validação para essas linhas.
5. Nesta etapa, o `DataFrame` transformado é o que será submetido à validação — nenhuma persistência ocorre ainda.

### 3.4 Etapa 4 — Validate
1. Cada linha do `DataFrame` transformado passa pelas regras descritas em `VALIDADOR.md`, específicas do `tipo_arquivo`.
2. Linhas válidas seguem para a etapa 6 (Load); linhas inválidas geram um registro em `importacao_erros` (etapa que ocorre em paralelo à carga, dentro da mesma transação).
3. Ao final desta etapa, os contadores `total_linhas`, `linhas_validas` e `linhas_invalidas` são calculados e serão persistidos em `importacoes` na etapa 6.

### 3.5 Etapa 5 — Hash/Version
1. O hash SHA-256 do conteúdo binário do arquivo (calculado já na Etapa 1, antes de qualquer leitura) é comparado ao histórico de `importacoes` do mesmo `tipo_arquivo`, conforme `HASH.md` e `REGRAS_DE_NEGOCIO.md`, seção 4.
2. Se o arquivo for identificado como repetido, o pipeline é interrompido nesta etapa, antes de qualquer persistência de linhas, e a `Importação` é marcada como `FALHOU` com motivo "arquivo duplicado".
3. Caso contrário, `versao` e `importacao_pai_id` são determinados conforme `REGRAS_DE_NEGOCIO.md`, seção 4.

### 3.6 Etapa 6 — Load
1. Toda a carga ocorre dentro de **uma única transação de banco**: linhas válidas do `tipo_arquivo` correspondente e os registros de `importacao_erros` são persistidos atomicamente.
2. As regras de persistência específicas por `tipo_arquivo` (upsert de Clientes, versionamento de Carteira, inserção de Faturamento/Visitas/Checklist) seguem `REGRAS_DE_NEGOCIO.md`, seção 5.
3. Ao final, `importacoes.status` é atualizado para `CONCLUIDA` (zero linhas inválidas) ou `CONCLUIDA_COM_ERROS` (uma ou mais linhas inválidas, porém ao menos uma linha válida), ou `FALHOU` (nenhuma linha válida, ou erro inesperado — neste caso a transação é revertida integralmente).
4. `iniciado_em` é registrado no início da Etapa 2; `concluido_em` ao final da Etapa 6.

### 3.7 Etapa 7 — Audit Log
1. Um registro em `logs_auditoria` é criado com `entidade = 'importacoes'`, `entidade_id = importacoes.id`, `acao = 'IMPORTACAO'`, contendo em `dados_depois` um resumo do resultado (status, versão, contadores).
2. Detalhamento completo em `LOGS.md` e `AUDITORIA.md`.

## 4. Idempotência e Repetição de Execução

1. Reenviar o mesmo arquivo (mesmo hash) nunca gera efeito duplicado — é recusado na Etapa 5.
2. Reenviar um arquivo com conteúdo diferente do mesmo `tipo_arquivo` sempre gera uma nova versão, nunca sobrescreve a anterior (`REGRAS_DE_NEGOCIO.md`).
3. Falhas técnicas durante a Etapa 6 (ex.: queda de conexão com o banco) resultam em rollback automático da transação; a `Importação` permanece com `status = FALHOU` e pode ser reenviada pelo usuário como um novo upload independente.

## 5. Desempenho e Limites (POC)

1. Tamanho máximo de arquivo: 20 MB.
2. Limite de linhas processadas por importação: 100.000 linhas (limite de POC; revisão de arquitetura de processamento assíncrono é item de evolução pós-POC, `ROADMAP.md`).
3. Processamento síncrono dentro da requisição HTTP para arquivos dentro dos limites acima, com timeout de 120 segundos configurado no servidor ASGI (`DEPLOY.md`).

## 6. Relação com os Documentos de Importador

Este documento descreve o **pipeline genérico**. As particularidades de layout de colunas, chaves de conciliação e regras específicas de cada um dos 5 tipos de arquivo (Base de Clientes, Carteira dos Promotores, Faturamento Mensal, Checklists, Visitas) estão detalhadas em `IMPORTADOR.md`.
