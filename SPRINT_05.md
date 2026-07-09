# SPRINT_05.md — Importador de Carteira

## 1. Objetivo

Implementar o importador da Carteira dos Promotores, incluindo a criação automática de Supervisores e Promotores inéditos, e a lógica central de versionamento de vigência que materializa a garantia de "nunca sobrescrever dados" para o relacionamento Promotor × Cliente.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `IMPORTADOR.md` (seção 4), `VALIDADOR.md` (seções 3–5 e 7), `REGRAS_DE_NEGOCIO.md` (seção 5.2), `DICIONARIO_DE_DADOS.md` (tabelas `carteiras`, `promotores`, `supervisores`).

## 3. Pré-condições

Sprint 04 concluída (importador de Clientes disponível — a Carteira depende de clientes pré-existentes, `IMPORTADOR.md`, seção 8).

## 4. Escopo (Backlog Detalhado)

### 4.1 Repositórios de Apoio
1. Completar `app/repositories/supervisor_repository.py` e `app/repositories/promotor_repository.py` com `buscar_por_codigo_externo` e `criar_se_nao_existir`.
2. Completar `app/repositories/carteira_repository.py` com `buscar_vinculo_vigente_por_cliente`, `encerrar_vigencia`, `criar_vinculo`.

### 4.2 Validador Específico
1. Implementar `app/services/importacao/validadores/validador_carteira.py`, aplicando `CAR-001`, `CAR-002`, `CAR-003` (`VALIDADOR.md`, seção 7) e a regra de referência `REF-002` (cliente deve existir).

### 4.3 Importador Concreto
1. Implementar `app/services/importacao/importador_carteira.py`, implementando `ImportadorArquivo`:
   - Extração/transformação do layout de `IMPORTADOR.md`, seção 4.1.
   - Resolução/criação de Supervisor e Promotor (`IMPORTADOR.md`, seção 4.2).
   - Para cada cliente do arquivo: comparação com o vínculo vigente atual (`REGRAS_DE_NEGOCIO.md`, seção 5.2, item 2) — idempotência quando o promotor não muda; encerramento + criação de novo vínculo quando muda; criação simples quando não havia vínculo.
   - Para clientes com vínculo vigente ausentes no novo arquivo: encerramento automático do vínculo (`REGRAS_DE_NEGOCIO.md`, seção 5.2, item 3).
   - Toda alteração de vínculo referencia a `importacao_id` corrente.
2. Registrar o importador no motor genérico, habilitando `POST /importacoes` com `tipo_arquivo = CARTEIRA`.

### 4.4 Rollback Específico de Carteira
1. Completar `app/services/importacao/rollback_service.py` (iniciado na Sprint 03) com a lógica específica de reabertura de vigência para importações de `tipo_arquivo = CARTEIRA` (`REGRAS_DE_NEGOCIO.md`, seção 6, item 2, segundo marcador).

### 4.5 Endpoints de Carteira
1. Implementar `app/api/routers/carteiras_router.py`: `GET /carteiras`, `GET /carteiras/promotor/{promotor_id}` (`API.md`, seção 8), com aplicação de escopo por perfil (`PERMISSOES.md`, seção 4).

## 5. Fora de Escopo desta Sprint

1. Importadores de Faturamento, Visitas, Checklist — Sprints 06 e 07.
2. Cálculo de KPIs que consomem Carteira (Cobertura, Positivação, Fora da Carteira) — Sprint 08.

## 6. Entregáveis

1. Importador de Carteira funcional de ponta a ponta, incluindo criação automática de Supervisores/Promotores.
2. Lógica de versionamento de vigência completa e testada (abertura, troca, encerramento por ausência).
3. Rollback de importação de Carteira reabrindo corretamente vigências encerradas.
4. Endpoints de consulta de Carteira.

## 7. Critérios de Aceite

1. Importação inicial de Carteira cria vínculos `ATIVA` para todos os clientes do arquivo, cada um com `data_inicio_vigencia` igual à `DATA_REFERENCIA`.
2. Reimportação com um cliente atribuído a um promotor diferente encerra o vínculo anterior (`status = ENCERRADA`, `data_fim_vigencia` preenchida) e cria um novo vínculo `ATIVA` com o novo promotor, sem excluir o registro anterior.
3. Reimportação em que um cliente antes presente deixa de constar no arquivo encerra automaticamente seu vínculo vigente.
4. Reimportação com o mesmo promotor para um cliente já vinculado não gera nenhuma alteração (idempotência verificada por teste que compara o estado do banco antes/depois).
5. Rollback de uma importação de Carteira restaura exatamente o estado de `carteiras` anterior à importação revertida, verificado por teste de comparação de estado completo.
6. `GET /carteiras/promotor/{id}` retorna exclusivamente os vínculos vigentes (`data_fim_vigencia IS NULL`) do promotor.
7. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida, incluindo o teste de regressão "Sempre permitir rollback" (`TESTES.md`, seção 10, item 4).

## 8. Riscos e Observações

1. A regra de que "um cliente não pode ter dois promotores simultâneos" (`VALIDADOR.md`, `CAR-003`) se aplica apenas **dentro do mesmo arquivo**; entre arquivos de tipo_arquivo diferentes não há tal restrição, pois cada `tipo_arquivo` tem sua própria cadeia de versão independente.
