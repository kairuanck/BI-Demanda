# SPRINT_03.md — Motor de Importação Base (Hash, Versionamento, Log)

## 1. Objetivo

Implementar o pipeline ETL genérico (upload, extração, transformação, validação estrutural, hash/versionamento, carga transacional, log de auditoria), reutilizável pelos 5 importadores específicos das Sprints 04 a 07, sem ainda implementar o parser de nenhum tipo de arquivo específico.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `ETL.md`, `IMPORTADOR.md` (seção 1–2, convenções gerais), `VALIDADOR.md` (seções 1–5, comuns), `HASH.md`, `LOGS.md`, `BACKEND.md`.

## 3. Pré-condições

Sprint 01 (modelos `importacoes`, `importacao_erros`, `importacao_arquivos` disponíveis) e Sprint 02 (autenticação, para vincular `usuario_id` à importação) concluídas.

## 4. Escopo (Backlog Detalhado)

### 4.1 Infraestrutura
1. Implementar `app/infrastructure/hashing/sha256_hasher.py`: cálculo de hash SHA-256 em streaming (`HASH.md`, seção 2).
2. Implementar `app/infrastructure/storage/file_storage.py`: gravação e leitura de arquivos em `STORAGE_DIR`, com nomenclatura conforme `HASH.md`, seção 8.

### 4.2 Contratos de Domínio
1. Definir em `app/domain/contratos/importacao_contratos.py` a interface `ImportadorArquivo` (Protocol), com o método `processar(arquivo: bytes, usuario_id: int) -> ResultadoImportacao`, permitindo que os importadores específicos (Sprints 04–07) sejam plugados sem alterar o motor genérico (`BACKEND.md`, seção 3, item 2).
2. Definir `app/domain/excecoes.py`: `ArquivoDuplicadoError`, `ArquivoInvalidoError`, `ValidacaoEstruturalFalhouError`.

### 4.3 Motor de Importação Genérico
1. Implementar `app/services/importacao/motor_importacao.py`, orquestrando as 7 etapas de `ETL.md`, seção 3, de forma genérica e parametrizada por `tipo_arquivo`:
   - Etapa 1 (Upload): recebe bytes do arquivo, valida extensão/tamanho (`VALIDADOR.md`, seção 3), calcula hash.
   - Etapa 5 (Hash/Version): classifica o upload (`HASH.md`, seção 3) e determina `versao`/`importacao_pai_id` (`REGRAS_DE_NEGOCIO.md`, seção 4).
   - Etapas 2–4 (Extract/Transform/Validate): delegadas ao `ImportadorArquivo` específico injetado (implementado nas Sprints 04–07).
   - Etapa 6 (Load): persiste `importacoes`, `importacao_erros`, `importacao_arquivos` transacionalmente, delegando a persistência de linhas válidas ao `ImportadorArquivo` específico.
   - Etapa 7 (Audit Log): registra evento `IMPORTACAO` em `logs_auditoria` (`AUDITORIA.md`, seção 5).
2. Implementar `app/services/validador_service.py` com as validações estruturais e de campo **comuns** a todos os tipos de arquivo (`VALIDADOR.md`, seções 3–5), reutilizáveis pelos validadores específicos das Sprints 04–07.

### 4.4 Mecanismo de Rollback (Base Genérica)
1. Implementar `app/services/importacao/rollback_service.py` com a lógica genérica de rollback aplicável a qualquer `tipo_arquivo` (`REGRAS_DE_NEGOCIO.md`, seção 6, itens 1 a 4, exceto a lógica específica de reabertura de vigência de Carteira, que é implementada na Sprint 05 quando o modelo de Carteira é manipulado por importação pela primeira vez).
2. Validação da condição de elegibilidade ao rollback (`REGRAS_DE_NEGOCIO.md`, seção 6, item 4).

### 4.5 Endpoints de API
1. `app/api/routers/importacoes_router.py`: `POST /importacoes` (upload), `GET /importacoes`, `GET /importacoes/{id}`, `GET /importacoes/{id}/erros`, `GET /importacoes/{id}/versoes`, `GET /importacoes/{id}/arquivo`, `POST /importacoes/{id}/rollback` (`API.md`, seção 9), todos protegidos por `exige_perfil(ADMINISTRADOR)`.
2. Nesta Sprint, `POST /importacoes` aceita apenas `tipo_arquivo` ainda sem parser implementado — deve retornar erro controlado ("importador ainda não disponível para este tipo de arquivo") até que as Sprints 04–07 registrem os importadores concretos no motor genérico. Este comportamento é temporário e esperado, documentado no corpo do Pull Request desta Sprint (`MASTER_PROMPT.md`, seção 3, item 11).

## 5. Fora de Escopo desta Sprint

1. Parser específico de qualquer um dos 5 tipos de arquivo — Sprints 04 a 07.
2. Regras de negócio de versionamento específicas de Carteira/Faturamento/Visitas/Checklist (`REGRAS_DE_NEGOCIO.md`, seções 5.1 a 5.5) — Sprints 04 a 07.

## 6. Entregáveis

1. Motor de importação genérico funcional, com hash, classificação de versão e persistência transacional de metadados de importação.
2. Endpoints de importação (upload, listagem, detalhe, erros, versões, download de arquivo, rollback), com a limitação documentada da seção 4.5, item 2.
3. Testes unitários de classificação de hash (`HASH.md`, seção 3) e testes de integração do pipeline genérico usando um `ImportadorArquivo` fake de teste.

## 7. Critérios de Aceite

1. Upload de um mesmo arquivo (mesmo hash) duas vezes resulta na segunda tentativa classificada como "Arquivo Repetido" (`HASH.md`, seção 3), com `status = FALHOU` e mensagem apropriada.
2. Upload de dois arquivos de conteúdo diferente para o mesmo `tipo_arquivo` gera `versao = 1` e `versao = 2`, com `importacao_pai_id` da segunda apontando para a primeira.
3. Arquivo original de toda importação aceita é recuperável via `GET /importacoes/{id}/arquivo`.
4. Toda importação processada gera exatamente um registro de auditoria com `acao = IMPORTACAO`.
5. Rollback de uma importação elegível altera seu `status` para `REVERTIDA` e é bloqueado (com mensagem explicativa) quando não elegível.
6. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. O comportamento temporário descrito na seção 4.5, item 2, é esperado e não deve ser tratado como defeito — será resolvido organicamente à medida que cada `ImportadorArquivo` concreto for registrado no motor genérico nas Sprints 04 a 07, sem necessidade de alterar o motor em si (garantia de Open/Closed — `BACKEND.md`, seção 3, item 2).
