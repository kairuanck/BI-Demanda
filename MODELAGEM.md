# MODELAGEM.md — Modelagem Conceitual e Lógica de Dados

## 1. Visão Geral

Este documento descreve, de forma conceitual, as 19 entidades do modelo de dados do Promotores BI, seus relacionamentos e cardinalidades. A especificação física completa (colunas, tipos, restrições) está em `DICIONARIO_DE_DADOS.md`. O diagrama visual está em `DER.md`.

## 2. Entidades e Descrição Conceitual

### 2.1 Cadastros / Dimensões

**Usuário (`usuarios`)** — Conta de acesso à plataforma. Possui um perfil (Administrador, Supervisor, Promotor, Diretoria) e pode, opcionalmente, estar vinculado a um registro de Promotor ou de Supervisor, para fins de escopo de dados (um usuário Promotor só acessa a própria carteira; um usuário Supervisor só acessa a carteira de sua equipe).

**Supervisor (`supervisores`)** — Gestor de uma equipe de Promotores. Entidade de negócio, distinta da conta de acesso (`usuarios`), pois pode existir em dados importados (planilha de Carteira) antes de possuir login no sistema.

**Promotor (`promotores`)** — Profissional de campo, do tipo Técnico ou Trade, vinculado a um Supervisor. Entidade de negócio, distinta da conta de acesso.

**Vendedor (`vendedores`)** — Representante comercial responsável pela venda/faturamento junto ao cliente, conforme identificado na planilha de Faturamento Mensal. Não possui, na POC, conta de acesso própria à plataforma.

**Laboratório (`laboratorios`)** — Indústria/fabricante cujos produtos geram o faturamento analisado (dimensão de origem do produto).

**Departamento (`departamentos`)** — Linha/categoria de produto ou unidade de negócio à qual o faturamento pertence (ex.: Nutrição, Saúde Animal, Acessórios).

**UF (`ufs`)** — Unidade federativa brasileira, dimensão geográfica de primeiro nível.

**Cidade (`cidades`)** — Município brasileiro, dimensão geográfica de segundo nível, vinculado a uma UF.

**Cliente (`clientes`)** — Pet shop, clínica veterinária, distribuidor ou demais canais atendidos, localizados em uma Cidade/UF.

### 2.2 Fatos Versionados

**Carteira (`carteiras`)** — Vínculo, com vigência temporal, entre um Promotor e um Cliente. Uma nova importação de Carteira **não sobrescreve** vínculos anteriores: encerra a vigência do vínculo anterior (quando alterado) e cria um novo registro vigente, preservando o histórico completo de qual promotor atendeu qual cliente em qual período.

**Faturamento (`faturamentos`)** — Registro de valor faturado para um Cliente, em um Laboratório e Departamento específicos, em um determinado Ano/Mês, atribuído a um Vendedor. Cada importação gera novos registros vinculados à sua `importacao_id`; reimportações do mesmo período são tratadas como nova versão (ver `REGRAS_DE_NEGOCIO.md`), nunca sobrescrevendo os registros da versão anterior.

**Visita (`visitas`)** — Registro de uma visita realizada por um Promotor a um Cliente em uma data específica.

**Checklist (`checklists`)** — Modelo/template de formulário de verificação, com perguntas associadas, direcionado a um tipo de Promotor.

**Pergunta de Checklist (`checklist_perguntas`)** — Item de verificação pertencente a um Checklist (template).

**Resposta de Checklist (`checklist_respostas`)** — Resposta dada a uma Pergunta de Checklist no contexto de uma Visita específica.

### 2.3 Controle de Importação

**Importação (`importacoes`)** — Registro de cada operação de carregamento de planilha: tipo de arquivo, hash, versão, status, usuário responsável e vínculo com a versão anterior do mesmo arquivo lógico.

**Erro de Importação (`importacao_erros`)** — Registro de cada linha rejeitada durante a validação de uma importação, com motivo do erro.

**Arquivo de Importação (`importacao_arquivos`)** — Armazenamento do arquivo binário original de cada importação, para fins de auditoria e rollback.

### 2.4 Auditoria

**Log de Auditoria (`logs_auditoria`)** — Registro de toda ação relevante realizada na plataforma (criação, atualização, exclusão, importação, rollback, login, exportação), com estado anterior e posterior quando aplicável.

## 3. Relacionamentos e Cardinalidades

| Origem | Relacionamento | Destino | Cardinalidade |
|---|---|---|---|
| Usuário | vincula-se a (opcional) | Promotor | N:1 (vários usuários nunca compartilham o mesmo promotor — 1:1 na prática, modelado como N:1 com unicidade) |
| Usuário | vincula-se a (opcional) | Supervisor | N:1 (1:1 na prática, modelado como N:1 com unicidade) |
| Promotor | pertence a | Supervisor | N:1 |
| Cliente | localiza-se em | Cidade | N:1 |
| Cidade | pertence a | UF | N:1 |
| Carteira | vincula | Promotor | N:1 |
| Carteira | vincula | Cliente | N:1 |
| Carteira | originada por | Importação | N:1 |
| Faturamento | refere-se a | Cliente | N:1 |
| Faturamento | refere-se a | Laboratório | N:1 |
| Faturamento | refere-se a | Departamento | N:1 |
| Faturamento | atribuído a | Vendedor | N:1 (opcional) |
| Faturamento | originado por | Importação | N:1 |
| Visita | realizada por | Promotor | N:1 |
| Visita | realizada em | Cliente | N:1 |
| Visita | originada por | Importação | N:1 |
| Checklist | possui | Pergunta de Checklist | 1:N |
| Resposta de Checklist | responde | Pergunta de Checklist | N:1 |
| Resposta de Checklist | pertence a | Visita | N:1 |
| Resposta de Checklist | originada por | Importação | N:1 |
| Importação | gera | Erro de Importação | 1:N |
| Importação | armazena | Arquivo de Importação | 1:1 |
| Importação | sucede | Importação (versão anterior) | N:1 (autorrelacionamento opcional) |
| Log de Auditoria | referencia | Usuário | N:1 |

## 4. Regras de Integridade Conceitual

1. Um Cliente pode estar, em um dado momento, vinculado a **no máximo um** registro de Carteira vigente (`data_fim_vigencia IS NULL`) por Promotor — múltiplos promotores não compartilham simultaneamente o mesmo cliente na POC (premissa adotada; ver `PROJECT.md`, seção 9).
2. Faturamento **não exige** vínculo de Carteira vigente — é justamente a ausência desse vínculo que caracteriza o KPI "Fora da Carteira" (`KPIS.md`).
3. Toda Visita deve referenciar um Promotor e um Cliente válidos; não é exigido, porém, que o Cliente esteja na carteira vigente do Promotor no momento da visita (o sistema apenas sinaliza essa condição para fins analíticos).
4. Toda Resposta de Checklist deve referenciar uma Pergunta pertencente ao mesmo Checklist aplicado na Visita correspondente.
5. Toda linha de qualquer tabela de fato ou de carteira deve referenciar uma `importacao_id` válida, garantindo rastreabilidade total da origem do dado.
6. Nenhuma tabela de fato permite `UPDATE` de valores de negócio após persistida — apenas `INSERT` de novas versões e, quando aplicável, marcação de encerramento de vigência (`data_fim_vigencia`, `status`). Esta regra é detalhada em `REGRAS_DE_NEGOCIO.md`.

## 5. Ciclo de Vida de uma Versão de Dado

Todo dado versionado (Carteira, Faturamento, Visita, Resposta de Checklist) segue o mesmo ciclo:

1. Uma nova `Importação` é criada com status `PENDENTE`.
2. O arquivo é validado linha a linha (`VALIDADOR.md`); linhas inválidas geram `importacao_erros` e são excluídas da persistência.
3. As linhas válidas são persistidas, vinculadas à `importacao_id`.
4. No caso específico de Carteira, vínculos anteriores conflitantes têm sua vigência encerrada (`data_fim_vigencia` preenchida), nunca excluídos.
5. A `Importação` é marcada como `CONCLUIDA` ou `CONCLUIDA_COM_ERROS`.
6. Um registro de `logs_auditoria` é criado para a operação.
7. Caso um rollback seja solicitado posteriormente, uma nova operação reverte o efeito da importação (reabrindo vigências encerradas por ela e desconsiderando os registros que ela criou nas consultas analíticas, conforme `REGRAS_DE_NEGOCIO.md`), preservando integralmente o histórico.

## 6. Compatibilidade com Estrutura Física

Toda entidade descrita neste documento corresponde a exatamente uma tabela física descrita em `DICIONARIO_DE_DADOS.md`, sem tabelas físicas adicionais fora deste conjunto de 19 entidades para o escopo da POC.
