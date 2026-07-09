# DICIONARIO_DE_DADOS.md — Dicionário de Dados Completo

## 1. Finalidade

Este documento é a especificação física definitiva de todas as 19 tabelas do Promotores BI. Toda implementação de modelo SQLAlchemy (Sprint 01) deve corresponder exatamente aos nomes, tipos, restrições e relacionamentos aqui descritos. Convenções gerais de tipos e compatibilidade SQLite/PostgreSQL estão em `DATABASE.md`.

Convenções de leitura:
- **PK** = chave primária. **FK** = chave estrangeira. **UQ** = restrição de unicidade. **NN** = `NOT NULL`.
- Todas as colunas `criado_em` possuem `default=func.now()`. Colunas `atualizado_em` possuem `default=func.now()` e `onupdate=func.now()`.
- Todos os `ondelete` de chave estrangeira estão explicitados; ausência de menção implica `RESTRICT`.

## 2. Tabela `usuarios`

Conta de acesso à plataforma.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN | Nome completo do usuário. |
| email | String(255) | NN, UQ | E-mail de login. |
| senha_hash | String(255) | NN | Hash bcrypt da senha (nunca a senha em texto puro). |
| perfil | Enum(String) | NN | Um de: `ADMINISTRADOR`, `SUPERVISOR`, `PROMOTOR`, `DIRETORIA`. |
| ativo | Boolean | NN, default=true | Indica se o login está habilitado. |
| promotor_id | Integer | FK → `promotores.id`, ondelete=SET NULL, NULL permitido, UQ | Vínculo opcional a um Promotor, exigido quando `perfil = PROMOTOR`. |
| supervisor_id | Integer | FK → `supervisores.id`, ondelete=SET NULL, NULL permitido, UQ | Vínculo opcional a um Supervisor, exigido quando `perfil = SUPERVISOR`. |
| criado_em | DateTime | NN | Data/hora de criação do registro. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |
| ultimo_login_em | DateTime | NULL permitido | Data/hora do último login bem-sucedido. |

Regras de negócio associadas: ver `REGRAS_DE_NEGOCIO.md`, seção "Usuários e Perfis", e `AUTENTICACAO.md`.

## 3. Tabela `supervisores`

Entidade de negócio representando o gestor de equipe.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN | Nome do supervisor. |
| codigo_externo | String(50) | NULL permitido, UQ | Código do supervisor na planilha de origem (Carteira), quando existente. |
| email | String(255) | NULL permitido | E-mail de contato. |
| ativo | Boolean | NN, default=true | Indica se o supervisor está ativo na operação. |
| criado_em | DateTime | NN | Data/hora de criação. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |

## 4. Tabela `promotores`

Entidade de negócio representando o profissional de campo.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN | Nome do promotor. |
| codigo_externo | String(50) | NULL permitido, UQ | Código do promotor na planilha de origem. |
| tipo | Enum(String) | NN | Um de: `TECNICO`, `TRADE` (Tipo de Promotor). |
| supervisor_id | Integer | FK → `supervisores.id`, ondelete=RESTRICT, NN | Supervisor responsável. |
| email | String(255) | NULL permitido | E-mail de contato. |
| telefone | String(20) | NULL permitido | Telefone de contato. |
| ativo | Boolean | NN, default=true | Indica se o promotor está ativo na operação. |
| data_admissao | Date | NULL permitido | Data de admissão/início de atuação. |
| criado_em | DateTime | NN | Data/hora de criação. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |

Índice: `ix_promotores_tipo` em `tipo` (utilizado pelo filtro "Tipo de Promotor").

## 5. Tabela `vendedores`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN | Nome do vendedor. |
| codigo_externo | String(50) | NULL permitido, UQ | Código do vendedor na planilha de Faturamento. |
| ativo | Boolean | NN, default=true | Indica se o vendedor está ativo. |
| criado_em | DateTime | NN | Data/hora de criação. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |

## 6. Tabela `laboratorios`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN, UQ | Nome do laboratório/fabricante. |
| codigo_externo | String(50) | NULL permitido, UQ | Código do laboratório na planilha de origem. |
| ativo | Boolean | NN, default=true | Indica se o laboratório está ativo. |
| criado_em | DateTime | NN | Data/hora de criação. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |

## 7. Tabela `departamentos`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN, UQ | Nome do departamento/linha de produto. |
| codigo_externo | String(50) | NULL permitido, UQ | Código do departamento na planilha de origem. |
| ativo | Boolean | NN, default=true | Indica se o departamento está ativo. |
| criado_em | DateTime | NN | Data/hora de criação. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |

## 8. Tabela `ufs`

Dimensão geográfica de primeiro nível (dado de referência, populado por seed — ver `SPRINT_01.md`).

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| sigla | String(2) | PK | Sigla da UF (ex.: `SP`, `RJ`). |
| nome | String(100) | NN | Nome completo da UF. |
| regiao | String(20) | NN | Região geográfica (`Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul`). |

## 9. Tabela `cidades`

Dimensão geográfica de segundo nível.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN | Nome do município. |
| uf_sigla | String(2) | FK → `ufs.sigla`, ondelete=RESTRICT, NN | UF à qual pertence. |
| codigo_ibge | String(10) | NULL permitido, UQ | Código IBGE do município, quando disponível. |
| criado_em | DateTime | NN | Data/hora de criação. |

Restrição composta: `UQ (nome, uf_sigla)` — não há duas cidades de mesmo nome na mesma UF.

## 10. Tabela `clientes`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| codigo_externo | String(50) | NN, UQ | Código do cliente na planilha de origem (chave de conciliação entre importações). |
| razao_social | String(200) | NN | Razão social do cliente. |
| nome_fantasia | String(200) | NULL permitido | Nome fantasia. |
| cnpj_cpf | String(20) | NULL permitido | CNPJ ou CPF do cliente. |
| uf_sigla | String(2) | FK → `ufs.sigla`, ondelete=RESTRICT, NN | UF do cliente. |
| cidade_id | Integer | FK → `cidades.id`, ondelete=RESTRICT, NN | Cidade do cliente. |
| endereco | String(255) | NULL permitido | Endereço completo. |
| canal | String(50) | NULL permitido | Segmento/canal (ex.: Pet Shop, Clínica Veterinária, Distribuidor). |
| ativo | Boolean | NN, default=true | Indica se o cliente está ativo na base. |
| criado_em | DateTime | NN | Data/hora de criação. |
| atualizado_em | DateTime | NN | Data/hora da última atualização. |

Importador associado: `IMPORTADOR.md`, seção "Base de Clientes".

## 11. Tabela `carteiras`

Fato versionado de vínculo Promotor × Cliente.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| promotor_id | Integer | FK → `promotores.id`, ondelete=RESTRICT, NN | Promotor responsável pelo cliente no período. |
| cliente_id | Integer | FK → `clientes.id`, ondelete=RESTRICT, NN | Cliente atendido. |
| importacao_id | Integer | FK → `importacoes.id`, ondelete=RESTRICT, NN | Importação que originou este registro. |
| data_inicio_vigencia | Date | NN | Data de início do vínculo. |
| data_fim_vigencia | Date | NULL permitido | Data de encerramento do vínculo; `NULL` indica vínculo vigente. |
| status | Enum(String) | NN, default=`ATIVA` | Um de: `ATIVA`, `ENCERRADA`. |
| criado_em | DateTime | NN | Data/hora de criação. |

Índice composto: `ix_carteiras_cliente_vigencia` em `(cliente_id, data_fim_vigencia)`, otimizando a busca do vínculo vigente de um cliente. Regras completas de versionamento em `REGRAS_DE_NEGOCIO.md`.

## 12. Tabela `faturamentos`

Fato de faturamento mensal.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| cliente_id | Integer | FK → `clientes.id`, ondelete=RESTRICT, NN | Cliente faturado. |
| laboratorio_id | Integer | FK → `laboratorios.id`, ondelete=RESTRICT, NN | Laboratório do produto faturado. |
| departamento_id | Integer | FK → `departamentos.id`, ondelete=RESTRICT, NN | Departamento/linha do produto faturado. |
| vendedor_id | Integer | FK → `vendedores.id`, ondelete=SET NULL, NULL permitido | Vendedor responsável, quando informado na planilha. |
| ano | Integer | NN | Ano de referência do faturamento (ex.: `2026`). |
| mes | Integer | NN | Mês de referência (`1`–`12`). |
| valor_faturado | Numeric(14,2) | NN | Valor faturado em Reais (BRL). |
| quantidade | Numeric(14,3) | NULL permitido | Quantidade de itens/unidades faturadas, quando informado. |
| importacao_id | Integer | FK → `importacoes.id`, ondelete=RESTRICT, NN | Importação que originou este registro. |
| criado_em | DateTime | NN | Data/hora de criação. |

Índice composto: `ix_faturamentos_periodo` em `(ano, mes)`. Índice composto: `ix_faturamentos_cliente_periodo` em `(cliente_id, ano, mes)`, utilizado pelos cálculos de Positivação e Fora da Carteira (`KPIS.md`).

## 13. Tabela `visitas`

Fato de visita realizada.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| promotor_id | Integer | FK → `promotores.id`, ondelete=RESTRICT, NN | Promotor que realizou a visita. |
| cliente_id | Integer | FK → `clientes.id`, ondelete=RESTRICT, NN | Cliente visitado. |
| data_visita | Date | NN | Data da visita. |
| hora_inicio | Time | NULL permitido | Horário de início. |
| hora_fim | Time | NULL permitido | Horário de término. |
| tipo_visita | String(50) | NULL permitido | Classificação livre da visita (ex.: Rotina, Emergencial, Treinamento). |
| latitude | Numeric(9,6) | NULL permitido | Latitude de registro, quando informada na planilha. |
| longitude | Numeric(9,6) | NULL permitido | Longitude de registro, quando informada na planilha. |
| observacoes | Text | NULL permitido | Observações livres da visita. |
| status | Enum(String) | NN, default=`REALIZADA` | Um de: `REALIZADA`, `CANCELADA`, `PENDENTE`. |
| importacao_id | Integer | FK → `importacoes.id`, ondelete=RESTRICT, NN | Importação que originou este registro. |
| criado_em | DateTime | NN | Data/hora de criação. |

Índice composto: `ix_visitas_promotor_data` em `(promotor_id, data_visita)`, utilizado pelos KPIs de Visitas e Cobertura.

## 14. Tabela `checklists`

Template de formulário de verificação.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| nome | String(150) | NN | Nome do checklist. |
| tipo_promotor_alvo | Enum(String) | NN | Um de: `TECNICO`, `TRADE`, `AMBOS`. |
| ativo | Boolean | NN, default=true | Indica se o template está em uso. |
| versao | Integer | NN, default=1 | Versão do template (nova versão de perguntas gera novo `checklists.id`, preservando o histórico de respostas de versões anteriores). |
| criado_em | DateTime | NN | Data/hora de criação. |

## 15. Tabela `checklist_perguntas`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| checklist_id | Integer | FK → `checklists.id`, ondelete=CASCADE, NN | Checklist ao qual a pergunta pertence. |
| ordem | Integer | NN | Posição de exibição da pergunta no formulário. |
| enunciado | String(500) | NN | Texto da pergunta. |
| tipo_resposta | Enum(String) | NN | Um de: `SIM_NAO`, `MULTIPLA_ESCOLHA`, `NUMERICO`, `TEXTO`. |
| obrigatoria | Boolean | NN, default=true | Indica se a resposta é obrigatória. |
| peso | Numeric(5,2) | NN, default=1.0 | Peso da pergunta no cálculo de conformidade do checklist. |

Restrição composta: `UQ (checklist_id, ordem)`.

## 16. Tabela `checklist_respostas`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| visita_id | Integer | FK → `visitas.id`, ondelete=CASCADE, NN | Visita à qual a resposta pertence. |
| checklist_pergunta_id | Integer | FK → `checklist_perguntas.id`, ondelete=RESTRICT, NN | Pergunta respondida. |
| resposta_valor | String(500) | NN | Valor textual da resposta, conforme `tipo_resposta` da pergunta. |
| conforme | Boolean | NULL permitido | Indicador calculado de conformidade da resposta (aplica-se a perguntas `SIM_NAO`; `NULL` para tipos não binários). |
| importacao_id | Integer | FK → `importacoes.id`, ondelete=RESTRICT, NN | Importação que originou este registro. |
| criado_em | DateTime | NN | Data/hora de criação. |

Restrição composta: `UQ (visita_id, checklist_pergunta_id)`.

## 17. Tabela `importacoes`

Controle central de versionamento de arquivos importados.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| tipo_arquivo | Enum(String) | NN | Um de: `CLIENTES`, `CARTEIRA`, `FATURAMENTO`, `CHECKLIST`, `VISITAS`. |
| nome_arquivo_original | String(255) | NN | Nome do arquivo enviado pelo usuário. |
| hash_sha256 | String(64) | NN | Hash SHA-256 do conteúdo binário do arquivo (ver `HASH.md`). |
| tamanho_bytes | Integer | NN | Tamanho do arquivo em bytes. |
| usuario_id | Integer | FK → `usuarios.id`, ondelete=RESTRICT, NN | Usuário que realizou a importação. |
| status | Enum(String) | NN, default=`PENDENTE` | Um de: `PENDENTE`, `PROCESSANDO`, `CONCLUIDA`, `CONCLUIDA_COM_ERROS`, `FALHOU`, `REVERTIDA`. |
| versao | Integer | NN, default=1 | Número sequencial da versão dentro do mesmo arquivo lógico (`tipo_arquivo`). |
| importacao_pai_id | Integer | FK → `importacoes.id`, ondelete=SET NULL, NULL permitido | Referência à versão anterior do mesmo arquivo lógico. |
| total_linhas | Integer | NN, default=0 | Total de linhas de dados no arquivo. |
| linhas_validas | Integer | NN, default=0 | Total de linhas validadas com sucesso. |
| linhas_invalidas | Integer | NN, default=0 | Total de linhas rejeitadas. |
| iniciado_em | DateTime | NULL permitido | Início do processamento. |
| concluido_em | DateTime | NULL permitido | Término do processamento. |
| criado_em | DateTime | NN | Data/hora de criação do registro (upload). |

Índice: `ix_importacoes_hash` em `hash_sha256` (detecção de arquivo repetido, ver `HASH.md`). Índice: `ix_importacoes_tipo_versao` em `(tipo_arquivo, versao)`.

## 18. Tabela `importacao_erros`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| importacao_id | Integer | FK → `importacoes.id`, ondelete=CASCADE, NN | Importação à qual o erro pertence. |
| numero_linha | Integer | NN | Número da linha no arquivo original (base 1, considerando o cabeçalho como linha 1). |
| coluna | String(100) | NULL permitido | Nome da coluna com erro, quando aplicável a uma coluna específica. |
| valor_recebido | String(500) | NULL permitido | Valor original que causou o erro. |
| mensagem_erro | String(500) | NN | Descrição do erro de validação (ver `VALIDADOR.md`). |
| criado_em | DateTime | NN | Data/hora de registro do erro. |

## 19. Tabela `importacao_arquivos`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| importacao_id | Integer | FK → `importacoes.id`, ondelete=CASCADE, NN, UQ | Importação à qual o arquivo pertence (relação 1:1). |
| caminho_armazenamento | String(500) | NN | Caminho relativo do arquivo binário armazenado em disco (ver `DEPLOY.md`). |
| nome_arquivo | String(255) | NN | Nome do arquivo armazenado (normalizado, distinto do nome original do usuário). |
| criado_em | DateTime | NN | Data/hora de armazenamento. |

## 20. Tabela `logs_auditoria`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | Integer | PK, autoincrement | Identificador único. |
| entidade | String(100) | NN | Nome da entidade/tabela afetada (ex.: `usuarios`, `importacoes`, `carteiras`). |
| entidade_id | Integer | NULL permitido | Identificador do registro afetado, quando aplicável. |
| acao | Enum(String) | NN | Um de: `CRIACAO`, `ATUALIZACAO`, `EXCLUSAO`, `IMPORTACAO`, `LOGIN`, `LOGOUT`, `ROLLBACK`, `EXPORTACAO`. |
| usuario_id | Integer | FK → `usuarios.id`, ondelete=SET NULL, NULL permitido | Usuário responsável pela ação (`NULL` para ações de sistema). |
| dados_antes | JSON | NULL permitido | Estado do registro antes da ação, serializado em JSON. |
| dados_depois | JSON | NULL permitido | Estado do registro após a ação, serializado em JSON. |
| ip_origem | String(45) | NULL permitido | Endereço IP de origem da requisição. |
| user_agent | String(255) | NULL permitido | User-Agent do cliente HTTP. |
| criado_em | DateTime | NN | Data/hora do evento. |

Índice composto: `ix_logs_auditoria_entidade` em `(entidade, entidade_id)`. Índice: `ix_logs_auditoria_usuario` em `usuario_id`. Detalhamento de uso em `AUDITORIA.md` e `LOGS.md`.

## 21. Resumo de Enums do Sistema

| Enum | Valores | Utilizado em |
|---|---|---|
| PerfilUsuario | ADMINISTRADOR, SUPERVISOR, PROMOTOR, DIRETORIA | `usuarios.perfil` |
| TipoPromotor | TECNICO, TRADE | `promotores.tipo`, `checklists.tipo_promotor_alvo` (+ `AMBOS`) |
| StatusCarteira | ATIVA, ENCERRADA | `carteiras.status` |
| StatusVisita | REALIZADA, CANCELADA, PENDENTE | `visitas.status` |
| TipoRespostaChecklist | SIM_NAO, MULTIPLA_ESCOLHA, NUMERICO, TEXTO | `checklist_perguntas.tipo_resposta` |
| TipoArquivoImportacao | CLIENTES, CARTEIRA, FATURAMENTO, CHECKLIST, VISITAS | `importacoes.tipo_arquivo` |
| StatusImportacao | PENDENTE, PROCESSANDO, CONCLUIDA, CONCLUIDA_COM_ERROS, FALHOU, REVERTIDA | `importacoes.status` |
| AcaoAuditoria | CRIACAO, ATUALIZACAO, EXCLUSAO, IMPORTACAO, LOGIN, LOGOUT, ROLLBACK, EXPORTACAO | `logs_auditoria.acao` |

Todos os Enums são implementados como `String` nativo (`native_enum=False`), conforme `DATABASE.md`, seção 3, item 6.
