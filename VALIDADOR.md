# VALIDADOR.md — Regras de Validação de Importação

## 1. Finalidade

Este documento especifica as regras de validação aplicadas a cada linha de cada tipo de arquivo importado, executadas na Etapa 4 (Validate) do pipeline descrito em `ETL.md`. Toda violação gera um registro em `importacao_erros` (`DICIONARIO_DE_DADOS.md`, seção 18) e a linha correspondente **não** é persistida, sem interromper a validação das demais linhas do arquivo.

## 2. Categorias de Validação

1. **Estrutural** — aplicada ao arquivo como um todo, antes da leitura linha a linha (ex.: colunas obrigatórias ausentes). Interrompe a importação inteira.
2. **De campo** — aplicada a um valor individual de uma coluna em uma linha (ex.: tipo de dado, formato, obrigatoriedade).
3. **De referência** — aplicada à existência de uma dimensão referenciada (ex.: UF inexistente, cliente inexistente).
4. **De negócio** — aplicada a regras específicas do domínio (ex.: data de visita futura, mês fora do intervalo 1–12).

## 3. Validações Estruturais (Comuns a Todos os Arquivos)

| Código | Regra | Mensagem padrão |
|---|---|---|
| EST-001 | Arquivo deve ter extensão `.xlsx` | "Formato de arquivo inválido. Utilize .xlsx." |
| EST-002 | Arquivo deve conter ao menos uma linha de dados além do cabeçalho | "Arquivo vazio ou sem dados." |
| EST-003 | Todas as colunas obrigatórias do `tipo_arquivo` (`IMPORTADOR.md`) devem estar presentes no cabeçalho | "Coluna obrigatória ausente: {coluna}." |
| EST-004 | Tamanho do arquivo não pode exceder 20 MB | "Arquivo excede o tamanho máximo permitido (20 MB)." |

## 4. Validações de Campo (Comuns)

| Código | Regra | Mensagem padrão |
|---|---|---|
| CAM-001 | Campo obrigatório não pode estar vazio | "Campo obrigatório não preenchido: {coluna}." |
| CAM-002 | Campo numérico deve ser conversível para `Decimal`/`Integer` | "Valor numérico inválido em {coluna}: {valor}." |
| CAM-003 | Campo de data deve ser conversível para `date`, nos formatos aceitos (`DD/MM/AAAA` ou data nativa do Excel) | "Data inválida em {coluna}: {valor}." |
| CAM-004 | Campo de código (`codigo_externo`) deve ter no máximo 50 caracteres | "Código excede o tamanho máximo em {coluna}: {valor}." |
| CAM-005 | Campo textual obrigatório deve ter no máximo o tamanho definido em `DICIONARIO_DE_DADOS.md` para a coluna de destino | "Texto excede o tamanho máximo em {coluna}." |

## 5. Validações de Referência (Comuns)

| Código | Regra | Mensagem padrão |
|---|---|---|
| REF-001 | UF informada deve existir em `ufs` | "UF inexistente: {valor}." |
| REF-002 | Cliente referenciado deve existir em `clientes` quando o importador não cria clientes (Carteira, Faturamento, Visitas) | "Cliente não encontrado: {codigo}." |
| REF-003 | Promotor referenciado deve existir em `promotores` quando o importador não cria promotores (Visitas) | "Promotor não encontrado: {codigo}." |
| REF-004 | Visita referenciada deve existir em `visitas` (Checklist) | "Visita não encontrada: {id}." |
| REF-005 | Pergunta de checklist referenciada deve existir no template ativo correspondente (Checklist) | "Pergunta de checklist não encontrada para a ordem informada: {ordem}." |

## 6. Validações Específicas — Base de Clientes

| Código | Regra | Mensagem padrão |
|---|---|---|
| CLI-001 | `CODIGO_CLIENTE` obrigatório e único dentro do próprio arquivo | "Código de cliente duplicado no arquivo: {codigo}." |
| CLI-002 | `CNPJ_CPF`, quando informado, deve conter 11 ou 14 dígitos numéricos (CPF ou CNPJ) | "CNPJ/CPF inválido: {valor}." |

## 7. Validações Específicas — Carteira dos Promotores

| Código | Regra | Mensagem padrão |
|---|---|---|
| CAR-001 | `TIPO_PROMOTOR`, quando promotor é inédito, deve ser `TECNICO` ou `TRADE` | "Tipo de promotor inválido: {valor}." |
| CAR-002 | `DATA_REFERENCIA` não pode ser futura em relação à data de upload | "Data de referência não pode ser futura." |
| CAR-003 | Não pode haver duas linhas para o mesmo `CODIGO_CLIENTE` no mesmo arquivo (um cliente não pode ter dois promotores simultâneos no mesmo arquivo de carteira) | "Cliente informado mais de uma vez no arquivo: {codigo}." |

## 8. Validações Específicas — Faturamento Mensal

| Código | Regra | Mensagem padrão |
|---|---|---|
| FAT-001 | `ANO` deve estar entre 2000 e o ano corrente + 1 | "Ano fora do intervalo permitido: {valor}." |
| FAT-002 | `MES` deve estar entre 1 e 12 | "Mês inválido: {valor}." |
| FAT-003 | `VALOR_FATURADO` deve ser numérico (podendo ser negativo, representando estorno) | "Valor faturado inválido: {valor}." |
| FAT-004 | `QUANTIDADE`, quando informada, deve ser numérica e não negativa | "Quantidade inválida: {valor}." |

## 9. Validações Específicas — Visitas

| Código | Regra | Mensagem padrão |
|---|---|---|
| VIS-001 | `DATA_VISITA` não pode ser posterior à data de upload | "Data de visita não pode ser futura." |
| VIS-002 | `HORA_FIM`, quando informada junto de `HORA_INICIO`, deve ser posterior a `HORA_INICIO` | "Horário de término anterior ao horário de início." |
| VIS-003 | `STATUS`, quando informado, deve ser `REALIZADA`, `CANCELADA` ou `PENDENTE` | "Status de visita inválido: {valor}." |
| VIS-004 | `LATITUDE`/`LONGITUDE`, quando informadas, devem estar dentro dos intervalos geográficos válidos (-90 a 90 / -180 a 180) | "Coordenada geográfica inválida." |

## 10. Validações Específicas — Checklists

| Código | Regra | Mensagem padrão |
|---|---|---|
| CHK-001 | `RESPOSTA` para pergunta do tipo `SIM_NAO` deve ser um de: `SIM`, `NAO` (normalizado, case-insensitive) | "Resposta inválida para pergunta Sim/Não: {valor}." |
| CHK-002 | `RESPOSTA` para pergunta do tipo `NUMERICO` deve ser conversível para número | "Resposta numérica inválida: {valor}." |
| CHK-003 | `RESPOSTA` para pergunta obrigatória não pode estar vazia | "Resposta obrigatória não preenchida para a pergunta de ordem {ordem}." |
| CHK-004 | Não pode haver duas respostas para a mesma `ID_VISITA` + `ORDEM_PERGUNTA` no mesmo arquivo | "Resposta duplicada no arquivo para visita {id} e pergunta {ordem}." |

## 11. Comportamento em Caso de Erro

1. Toda violação identificada gera exatamente um registro em `importacao_erros`, com `numero_linha`, `coluna` (quando aplicável), `valor_recebido` e `mensagem_erro` preenchidos conforme as tabelas acima.
2. Uma linha pode gerar múltiplos registros de erro caso viole mais de uma regra simultaneamente.
3. Uma linha com ao menos um erro **não é persistida** na tabela de destino.
4. O processamento continua para as demais linhas do arquivo, independentemente de erros em linhas anteriores (validação não é "fail-fast" em nível de linha, apenas em nível estrutural — seção 3).

## 12. Relatório de Validação

Ao final da importação, a interface exibe (`TELAS.md`, tela "Detalhe de Importação"):
1. Total de linhas processadas, válidas e inválidas (`importacoes.total_linhas`, `linhas_validas`, `linhas_invalidas`).
2. Lista paginada de erros, agrupável por `coluna` e por `mensagem_erro`, permitindo exportação em CSV para correção offline da planilha de origem.
