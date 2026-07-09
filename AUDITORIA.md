# AUDITORIA.md — Auditoria de Negócio

## 1. Finalidade

Este documento especifica o mecanismo de auditoria de negócio do Promotores BI, centrado na tabela `logs_auditoria` (`DICIONARIO_DE_DADOS.md`, seção 20). Distingue-se do log técnico de execução (`LOGS.md`) por registrar exclusivamente **ações relevantes de negócio**, com objetivo de rastreabilidade, compliance e suporte a investigações administrativas.

## 2. Objetivo da Auditoria

1. Permitir responder, a qualquer momento, às perguntas: "quem fez o quê, quando, e qual era o estado antes/depois".
2. Sustentar a garantia de "nunca sobrescrever dados" (`REGRAS_DE_NEGOCIO.md`, seção 2) com evidência auditável, não apenas com o desenho do modelo de dados.
3. Fornecer a trilha necessária para decisões de rollback informadas (`REGRAS_DE_NEGOCIO.md`, seção 6).

## 3. Eventos Auditados (Obrigatórios)

| Evento | `entidade` | `acao` | Momento do registro |
|---|---|---|---|
| Login bem-sucedido | `usuarios` | `LOGIN` | Imediatamente após emissão do token |
| Logout | `usuarios` | `LOGOUT` | Imediatamente após revogação do refresh token |
| Criação de usuário | `usuarios` | `CRIACAO` | Após persistência bem-sucedida |
| Atualização de usuário | `usuarios` | `ATUALIZACAO` | Após persistência bem-sucedida, com `dados_antes`/`dados_depois` |
| Ativação/inativação de usuário | `usuarios` | `ATUALIZACAO` | Idem |
| Redefinição de senha | `usuarios` | `ATUALIZACAO` | Idem (sem incluir o valor da senha em `dados_depois` — ver seção 6) |
| Upload/processamento de importação | `importacoes` | `IMPORTACAO` | Ao final do pipeline (`ETL.md`, Etapa 7), com resultado consolidado |
| Rollback de importação | `importacoes` | `ROLLBACK` | Ao final da operação de reversão |
| Atualização cadastral de Cliente via importação | `clientes` | `ATUALIZACAO` | Por cliente afetado, com `dados_antes`/`dados_depois` |
| Ativação/inativação de Cliente | `clientes` | `ATUALIZACAO` | Após persistência bem-sucedida |
| Exportação de dados | `exportacoes` | `EXPORTACAO` | Ao gerar o arquivo de exportação, com filtros utilizados |
| Tentativa de acesso não autorizado | `<entidade da rota acessada>` | conforme a ação tentada | No momento da negação (`403`) |

## 4. Estrutura do Registro de Auditoria

Cada evento gera exatamente um registro em `logs_auditoria` (`DICIONARIO_DE_DADOS.md`, seção 20), contendo:
- `entidade` e `entidade_id`: o que foi afetado.
- `acao`: a natureza do evento.
- `usuario_id`: quem executou (ou `NULL` para eventos de sistema, quando aplicável).
- `dados_antes`/`dados_depois`: estado relevante antes/depois, serializado em JSON, contendo apenas os campos que mudaram (não o registro completo, para reduzir volume) exceto em `CRIACAO`, onde `dados_antes` é `NULL` e `dados_depois` contém o registro criado.
- `ip_origem`/`user_agent`: contexto da requisição HTTP de origem.
- `criado_em`: timestamp do evento.

## 5. Auditoria de Importações — Detalhamento Específico

Para o evento de `IMPORTACAO`, o campo `dados_depois` contém obrigatoriamente:
```json
{
  "tipo_arquivo": "FATURAMENTO",
  "versao": 3,
  "status": "CONCLUIDA_COM_ERROS",
  "total_linhas": 1500,
  "linhas_validas": 1487,
  "linhas_invalidas": 13,
  "hash_sha256": "a1b2c3..."
}
```

Para o evento de `ROLLBACK`, o campo `dados_depois` contém obrigatoriamente:
```json
{
  "importacao_revertida_id": 87,
  "tipo_arquivo": "CARTEIRA",
  "vinculos_reabertos": 12,
  "vinculos_reencerrados": 4,
  "justificativa": "Arquivo enviado com supervisor incorreto para a regional Sul."
}
```

O campo `justificativa`, exigido na interface de rollback (`TELAS.md`, seção 7), é obrigatório e de preenchimento livre pelo Administrador, garantindo contexto humano além dos dados técnicos da reversão.

## 6. Dados Sensíveis na Auditoria

1. `dados_antes`/`dados_depois` de eventos relativos a `usuarios` **nunca** incluem `senha_hash`, mesmo em eventos de redefinição de senha — apenas um marcador booleano `{"senha_alterada": true}` é registrado.
2. Nenhum dado de CNPJ/CPF completo é mascarado na auditoria (diferente de log técnico, a auditoria de negócio preserva o dado íntegro por exigência de rastreabilidade), mas o acesso à tela de Auditoria é restrito exclusivamente ao Administrador (`PERMISSOES.md`, seção 6).

## 7. Consulta e Visualização

1. A tela de Auditoria (`TELAS.md`, seção 12) permite filtrar por `entidade`, `acao`, `usuario_id` e intervalo de datas, com paginação (`API.md`, seção 11).
2. Cada registro pode ser expandido para visualização formatada (não apenas JSON bruto) de `dados_antes`/`dados_depois`, com destaque visual (`diff`) dos campos alterados entre os dois estados.
3. A auditoria é, por padrão, ordenada por `criado_em` decrescente (eventos mais recentes primeiro).

## 8. Retenção

1. Na POC, os registros de `logs_auditoria` não possuem expurgo automático — retenção indefinida, dado o volume esperado em ambiente de demonstração.
2. Política de retenção configurável (ex.: expurgo após N anos, conforme exigência regulatória do cliente contratante) é item de evolução pós-POC, relevante especialmente na transição para SaaS (`TUTORIAL.md`, seção 14).

## 9. Relação com Outros Documentos

- A lista mínima de ações auditáveis também está referenciada em `REGRAS_DE_NEGOCIO.md`, seção 10.
- A distinção entre esta camada e o log técnico está detalhada em `LOGS.md`, seção 2.
- O uso da auditoria para fundamentar decisões de rollback está detalhado em `REGRAS_DE_NEGOCIO.md`, seção 6.
