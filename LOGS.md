# LOGS.md — Estratégia de Logging

## 1. Finalidade

Este documento especifica a estratégia de logging técnico (aplicacional) do Promotores BI, distinta e complementar à trilha de **auditoria de negócio** registrada na tabela `logs_auditoria` (detalhada em `AUDITORIA.md`). Enquanto `AUDITORIA.md` trata do registro de ações de negócio para fins de rastreabilidade e compliance, este documento trata do **log técnico de execução** da aplicação (arquivos de log, níveis de severidade, formato, rotação).

## 2. Duas Camadas de Log

| Camada | Finalidade | Onde é registrada | Documento de referência |
|---|---|---|---|
| Log de Auditoria de Negócio | Rastreabilidade de ações de usuário e de sistema sobre dados de negócio | Tabela `logs_auditoria` (banco de dados) | `AUDITORIA.md` |
| Log Técnico de Execução | Diagnóstico operacional, erros de infraestrutura, desempenho | Arquivos de log estruturado (JSON Lines) em disco | Este documento |

As duas camadas são complementares: uma falha de importação gera **um** registro de auditoria de negócio (`acao = IMPORTACAO`, resultado de falha) e, potencialmente, **múltiplas** linhas de log técnico (stack trace, tempo de execução de cada etapa do ETL).

## 3. Biblioteca e Formato

1. Biblioteca: `logging` padrão do Python, configurada com formatação estruturada em **JSON Lines** (`python-json-logger` ou formatter customizado equivalente).
2. Cada linha de log é um objeto JSON com, no mínimo, os campos:
   - `timestamp` (ISO 8601, UTC)
   - `level` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
   - `logger` (nome do módulo/logger de origem)
   - `message` (mensagem descritiva)
   - `request_id` (identificador único da requisição HTTP, quando aplicável)
   - `usuario_id` (quando disponível no contexto da requisição)
   - `contexto` (objeto livre com dados adicionais relevantes ao evento)

## 4. Níveis de Log e Uso

| Nível | Uso |
|---|---|
| DEBUG | Detalhes internos de execução, habilitado apenas em ambiente de desenvolvimento (`DEPLOY.md`). |
| INFO | Eventos normais relevantes: início/fim de importação, login bem-sucedido, requisição processada. |
| WARNING | Situações anômalas não bloqueantes: linha de importação rejeitada por validação, tentativa de acesso a recurso sem permissão. |
| ERROR | Falhas tratadas que impedem a conclusão de uma operação: falha de importação, exceção de negócio capturada. |
| CRITICAL | Falhas de infraestrutura que comprometem a disponibilidade da aplicação: falha de conexão com banco de dados, erro não tratado na camada de API. |

## 5. Pontos de Instrumentação Obrigatórios

1. **Requisições HTTP:** middleware de log registra, em `INFO`, método, rota, status de resposta, tempo de execução e `request_id` de toda requisição (`BACKEND.md`, camada `api/middlewares/`).
2. **Pipeline de Importação (`ETL.md`):** cada uma das 7 etapas registra em `INFO` seu início e fim, com `importacao_id` e tempo de execução; falhas registram em `ERROR` com stack trace completo.
3. **Autenticação (`AUTENTICACAO.md`):** tentativas de login (sucesso em `INFO`, falha em `WARNING`), emissão e renovação de token.
4. **Erros não tratados:** um manipulador global de exceções do FastAPI (`BACKEND.md`) registra em `CRITICAL` qualquer exceção não capturada explicitamente, antes de retornar uma resposta HTTP 500 genérica ao cliente.

## 6. Correlação entre Log Técnico e Auditoria de Negócio

Todo log técnico relativo a uma operação que também gera um registro de `logs_auditoria` inclui, no campo `contexto`, o identificador do registro de auditoria correspondente (`logs_auditoria.id`), permitindo correlação entre as duas camadas durante uma investigação.

## 7. Armazenamento e Rotação (POC)

1. Os logs técnicos são gravados em `backend/logs/app.log`, com rotação diária (`TimedRotatingFileHandler`, `when="midnight"`, `backupCount=30`).
2. Em ambiente de contêiner (`DEPLOY.md`), os logs são adicionalmente direcionados a `stdout`/`stderr`, para compatibilidade com coletores de log da plataforma de hospedagem.
3. Não há, na POC, integração com ferramenta externa de observabilidade (ex.: ELK, Datadog) — item de evolução pós-POC (`ROADMAP.md`).

## 8. Dados Sensíveis em Log

1. Senhas (mesmo em texto cifrado/hash), tokens JWT completos e conteúdo integral de arquivos importados **nunca** são gravados em log técnico.
2. Quando necessário registrar contexto de usuário, apenas `usuario_id` e `email` são incluídos — nunca `senha_hash`.
3. Tokens JWT, quando mencionados em log, são truncados (primeiros 8 caracteres seguidos de `...`).

## 9. Relação com Testes

A suíte de testes (`TESTES.md`) inclui casos que verificam:
1. Que uma falha de importação gera log técnico em nível `ERROR` com `importacao_id` correto.
2. Que nenhuma senha em texto puro é emitida em nenhum log durante o fluxo de autenticação.
3. Que o middleware de requisição registra corretamente `request_id` único por requisição.
