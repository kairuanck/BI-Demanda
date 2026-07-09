# REGRAS_DE_NEGOCIO.md — Regras de Negócio

## 1. Finalidade

Este documento consolida todas as regras de negócio do Promotores BI que não são triviais a partir da modelagem física (`DICIONARIO_DE_DADOS.md`). Toda implementação de camada de serviço (`services/`, ver `BACKEND.md`) deve obedecer estritamente às regras aqui descritas.

## 2. Princípios Gerais (Imutáveis)

1. **Nunca sobrescrever dados.** Nenhuma operação do sistema executa `UPDATE` sobre valores de negócio já persistidos em tabelas de fato (`carteiras`, `faturamentos`, `visitas`, `checklist_respostas`). Toda correção ocorre por meio de nova importação, gerando nova versão.
2. **Sempre versionar.** Toda importação recebe um número de `versao` sequencial dentro do seu `tipo_arquivo`, e referencia sua `importacao_pai_id` quando não é a primeira versão.
3. **Sempre manter histórico.** Registros de versões anteriores nunca são fisicamente excluídos, exceto por rotina administrativa de expurgo fora do escopo da POC.
4. **Sempre validar antes de importar.** Nenhuma linha é persistida sem passar pelas validações descritas em `VALIDADOR.md`.
5. **Sempre gerar logs.** Toda ação relevante gera um registro em `logs_auditoria`, conforme `AUDITORIA.md`.
6. **Sempre permitir rollback.** Toda importação concluída pode ser revertida por um usuário com permissão de Administrador, conforme seção 6 deste documento.

## 3. Usuários e Perfis

1. Um usuário com `perfil = PROMOTOR` deve obrigatoriamente ter `promotor_id` preenchido; a ausência desse vínculo impede o login (validação na camada de serviço de autenticação).
2. Um usuário com `perfil = SUPERVISOR` deve obrigatoriamente ter `supervisor_id` preenchido.
3. Usuários com `perfil = ADMINISTRADOR` ou `perfil = DIRETORIA` não possuem vínculo com `promotores` nem `supervisores`.
4. Um mesmo registro de `promotores` ou `supervisores` pode estar vinculado a, no máximo, um `usuarios.id` (restrição de unicidade em `usuarios.promotor_id` e `usuarios.supervisor_id`).
5. Usuários inativos (`ativo = false`) não conseguem autenticar, mesmo com credenciais corretas (`AUTENTICACAO.md`).
6. A exclusão de usuário nunca é física — apenas inativação (`ativo = false`), preservando a integridade referencial de `logs_auditoria.usuario_id` e `importacoes.usuario_id`.

## 4. Versionamento de Importações

1. Ao receber um novo arquivo, o sistema calcula o hash SHA-256 do conteúdo binário (`HASH.md`).
2. Se o hash for **idêntico** a uma importação já existente do mesmo `tipo_arquivo`, o sistema recusa a importação como **arquivo repetido**, informando ao usuário a importação original correspondente, e nenhuma nova versão é criada.
3. Se o hash for **diferente**, mas o `tipo_arquivo` já possui importações anteriores, a nova importação é tratada como **nova versão**: `versao = MAX(versao existente para o tipo_arquivo) + 1`, e `importacao_pai_id` aponta para a importação de maior `versao` anterior com status `CONCLUIDA` ou `CONCLUIDA_COM_ERROS`.
4. Se não houver importação anterior para o `tipo_arquivo`, a nova importação recebe `versao = 1` e `importacao_pai_id = NULL`.
5. O conteúdo semântico de "arquivo alterado" (mesmo arquivo lógico, conteúdo diferente) é inferido pela combinação de `tipo_arquivo` idêntico e `hash_sha256` diferente — não há comparação célula a célula entre versões na POC.

## 5. Regras Específicas por Tipo de Arquivo

### 5.1 Base de Clientes (`CLIENTES`)
1. A chave de conciliação é `clientes.codigo_externo`.
2. Cliente já existente (mesmo `codigo_externo`) tem seus dados cadastrais **atualizados** (razão social, endereço, UF, cidade, canal) — esta é a única tabela de cadastro em que a reimportação atualiza o registro existente em vez de criar nova linha, pois representa dados mestres, não fatos históricos. A atualização, ainda assim, gera um registro em `logs_auditoria` com `dados_antes`/`dados_depois`.
3. Cliente novo (`codigo_externo` inédito) é criado.
4. Clientes ausentes em uma reimportação **não são excluídos** nem inativados automaticamente — apenas alteração explícita via tela administrativa pode inativar um cliente.

### 5.2 Carteira dos Promotores (`CARTEIRA`)
1. A chave de conciliação é `clientes.codigo_externo` + `promotores.codigo_externo`.
2. Para cada cliente presente no novo arquivo:
   - Se o cliente **já possui** um vínculo vigente (`data_fim_vigencia IS NULL`) com um promotor **diferente** do informado no novo arquivo, esse vínculo vigente é encerrado (`data_fim_vigencia = data de referência da nova importação`, `status = ENCERRADA`), e um novo registro de `carteiras` é criado com o novo promotor, `data_inicio_vigencia = data de referência da nova importação`.
   - Se o cliente já possui vínculo vigente com o **mesmo** promotor, nenhuma alteração é feita (idempotência).
   - Se o cliente não possui vínculo vigente, um novo registro de `carteiras` é criado.
3. Clientes com vínculo vigente que **não aparecem** no novo arquivo têm seu vínculo automaticamente encerrado (`status = ENCERRADA`, `data_fim_vigencia` = data de referência da importação), passando a compor o KPI "Fora da Carteira" caso apresentem faturamento.
4. Todo registro de `carteiras` criado ou encerrado por uma importação referencia essa `importacao_id`.

### 5.3 Faturamento Mensal (`FATURAMENTO`)
1. A granularidade do arquivo é: Cliente × Laboratório × Departamento × Vendedor × Ano × Mês.
2. Cada linha válida gera um novo registro em `faturamentos`, vinculado à `importacao_id` corrente. Não há atualização de linhas existentes.
3. Caso o mesmo período (Ano/Mês) seja reimportado (nova versão do arquivo de Faturamento), os registros da versão anterior **permanecem no banco**, mas são **excluídos das consultas analíticas correntes** (dashboards e KPIs consideram exclusivamente os registros da versão mais recente e não revertida de cada `tipo_arquivo`, conforme seção 7 deste documento).
4. Valores negativos de `valor_faturado` são permitidos (representam estornos/devoluções) e não são rejeitados pelo validador, desde que numericamente válidos.

### 5.4 Checklists (`CHECKLIST`)
1. O arquivo de Checklists importa **respostas** a um template já cadastrado (`checklists` e `checklist_perguntas` são mantidos via tela administrativa, não via importação de planilha de respostas).
2. A chave de conciliação de cada resposta é `visitas.id` (via identificador de visita informado na planilha) + `checklist_perguntas.id` (via enunciado/ordem mapeado ao template ativo do `tipo_promotor_alvo` correspondente).
3. Cada resposta importada gera um novo registro em `checklist_respostas` vinculado à `importacao_id` corrente; não há atualização de respostas existentes — uma reimportação da mesma visita gera nova versão de resposta, e a consulta analítica considera a mais recente não revertida (mesma regra da seção 7).
4. O campo `conforme` é calculado automaticamente pelo importador: para perguntas do tipo `SIM_NAO`, `conforme = true` quando a resposta indica atendimento ao critério esperado (definido no cadastro da pergunta); para os demais tipos, `conforme = NULL` na importação, podendo ser tratado por regras específicas de KPI documentadas em `KPIS.md`.

### 5.5 Visitas (`VISITAS`)
1. Cada linha do arquivo gera um novo registro em `visitas`, vinculado à `importacao_id` corrente.
2. Não há deduplicação de visitas por conteúdo — cada linha do arquivo é considerada uma visita distinta. A prevenção de duplicidade ocorre no nível do **arquivo** (hash SHA-256), não da linha individual.
3. Visitas com `status = CANCELADA` são importadas e armazenadas, mas excluídas do cálculo dos KPIs de Cobertura e Visitas Realizadas (`KPIS.md`).

## 6. Rollback de Importação

1. Rollback é uma operação exclusiva do perfil Administrador (`PERMISSOES.md`).
2. Ao reverter uma importação:
   - O `status` da importação revertida é alterado para `REVERTIDA`.
   - Para importações de `CARTEIRA`: todo vínculo de `carteiras` criado por essa importação é marcado com `status = ENCERRADA` (se ainda vigente) e todo vínculo que essa importação havia encerrado é **reaberto** (`data_fim_vigencia = NULL`, `status = ATIVA`), desde que não tenha sido subsequentemente alterado por uma importação posterior não revertida.
   - Para importações de `FATURAMENTO`, `VISITAS` e `CHECKLIST`: os registros permanecem fisicamente no banco (nunca excluídos), porém passam a ser ignorados pelas consultas analíticas, pois estas sempre filtram `importacoes.status NOT IN ('REVERTIDA')` (seção 7).
   - Para importações de `CLIENTES`: como a importação de clientes realiza atualização direta (seção 5.1), o rollback restaura os valores anteriores registrados em `dados_antes` de `logs_auditoria` para cada cliente afetado por aquela importação.
3. Toda operação de rollback gera um registro em `logs_auditoria` com `acao = ROLLBACK`.
4. Não é permitido reverter uma importação que já possui uma versão posterior **do mesmo tipo de arquivo** concluída com sucesso, para evitar inconsistência de encadeamento de vigências — nesse caso, a interface deve orientar o usuário a reverter primeiro a versão mais recente.

## 7. Regra de Seleção de Versão Corrente para Consultas Analíticas

Toda consulta de dashboard e KPI (`KPIS.md`, `API.md`) considera exclusivamente registros cuja `importacao_id` aponte para uma importação com `status IN ('CONCLUIDA', 'CONCLUIDA_COM_ERROS')` — nunca `PENDENTE`, `PROCESSANDO`, `FALHOU` ou `REVERTIDA`. Para os tipos de arquivo em que múltiplas versões coexistem fisicamente no banco (Faturamento, Visitas, Checklist), a versão corrente considerada é sempre a de maior `versao` dentro do `tipo_arquivo`, entre as não revertidas.

## 8. Regras de Cálculo — Referência

As fórmulas completas dos KPIs (Carteira, Região, Fora da Carteira, Visitas, Checklists, Cobertura, Positivação, Ranking) estão detalhadas em `KPIS.md`. Este documento define apenas as regras de origem e integridade dos dados que alimentam esses cálculos.

## 9. Regras de Exportação

1. Toda exportação (Excel, CSV, PDF) reflete exatamente os filtros aplicados na tela de origem no momento da exportação.
2. Toda exportação gera um registro em `logs_auditoria` com `acao = EXPORTACAO`, contendo os filtros utilizados em `dados_depois`.

## 10. Regras de Auditoria Mínima

Toda ação das categorias abaixo é obrigatoriamente registrada em `logs_auditoria`, conforme `AUDITORIA.md`:
1. Login e logout de usuários.
2. Criação, atualização e inativação de usuários.
3. Toda importação (criação, conclusão, falha, rollback).
4. Toda exportação de dados.

## 11. Regras de Consistência Temporal

1. `ano` em `faturamentos` deve estar entre `2000` e o ano corrente + 1 (tolerância para lançamentos de faturamento futuro planejado/orçado, quando aplicável).
2. `mes` em `faturamentos` deve estar entre `1` e `12`.
3. `data_visita` não pode ser superior à data corrente no momento da importação.
4. `data_inicio_vigencia` de uma nova carteira nunca pode ser anterior à `data_fim_vigencia` do vínculo que ela eventualmente encerra para o mesmo cliente.
