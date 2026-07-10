# SPRINT_2_REPORT.md — Relatório da Sprint 2 (Banco de Dados, ETL e Motor de Importação)

## 1. Resumo

A Sprint 2 entregou o coração do sistema: o módulo `etl/` independente com os 5 importadores (Clientes, Carteira, Faturamento, Checklists, Visitas), hash SHA-256, controle de duplicidade, versionamento encadeado, histórico completo, fluxo físico de arquivos (`incoming/processed/rejected/archive`) e os endpoints REST de consulta/reprocessamento/exclusão de importações — sem upload via interface, conforme restrição do prompt.

A modelagem pedida já estava 94% coberta pelo esquema aprovado implementado na Sprint 0 (19 tabelas de `DICIONARIO_DE_DADOS.md`). O gap analysis completo, entidade a entidade, está em `docs/DECISIONS.md`, seção 7. A única entidade nova é `empresas`.

## 2. Arquivos Criados

### Modelagem e seeds
| Arquivo | Conteúdo |
|---|---|
| `backend/app/infrastructure/models/empresa_model.py` | Tabela `empresas` com UUID, soft delete (`deletado_em`) e auditoria (`criado_por`/`atualizado_por`) |
| `backend/alembic/versions/2026_07_10_0823_adiciona_empresas.py` | Migração aditiva, aplicada e reversível |
| `backend/app/infrastructure/seeds/seed_ufs.py` | Seed idempotente das 27 UFs (`python -m app.infrastructure.seeds.seed_ufs`) |

### Módulo ETL (`backend/etl/`)
| Arquivo | Conteúdo |
|---|---|
| `etl/motor.py` | Orquestrador do pipeline (7 etapas de `ETL.md`) + registro dos 5 importadores |
| `etl/resultado.py` | Estruturas `ErroLinha`/`LinhaValida`/`ResultadoValidacao` |
| `etl/layouts.py` | Layouts de colunas por tipo de arquivo (`IMPORTADOR.md`) |
| `etl/hash/sha256.py` | SHA-256 em streaming (blocos de 8 KB) |
| `etl/logs/etl_logger.py` | Logger técnico do pipeline (`promotores_bi.etl`) |
| `etl/arquivos/fluxo_arquivos.py` | `incoming → processed/rejected` + cópia imutável em `archive/` |
| `etl/readers/excel_reader.py` | Leitura Pandas/OpenPyXL, normalização de cabeçalhos, erros estruturais |
| `etl/transformers/normalizacao.py` | Conversores (texto, inteiro, decimal BR, data, hora) |
| `etl/validators/contexto.py` | Consultas referenciais injetáveis (UF, cliente, promotor, visita, pergunta) |
| `etl/validators/{clientes,carteira,faturamento,checklist,visitas}.py` | Regras de `VALIDADOR.md` por tipo (CLI/CAR/FAT/CHK/VIS/REF/CAM) |
| `etl/loaders/apoio.py` | Get-or-create de dimensões (cidade, supervisor, promotor, laboratório, departamento, vendedor) |
| `etl/loaders/{clientes,carteira,faturamento,checklist,visitas}_loader.py` | Persistência por tipo (`REGRAS_DE_NEGOCIO.md`, seção 5) |

### API
| Arquivo | Conteúdo |
|---|---|
| `backend/app/repositories/importacao_repository.py` | Consultas paginadas, cadeia de versões, arquivo, exclusão |
| `backend/app/services/importacao_service.py` | Regras de consulta, reprocessamento e exclusão de pendentes |
| `backend/app/api/schemas/importacao_schema.py` | Schemas Pydantic v2 de resposta |
| `backend/app/api/routers/importacoes_router.py` | 7 endpoints: listar, detalhe, erros, versões, arquivo, reprocessar, excluir pendente |

### Testes
| Arquivo | Cobre |
|---|---|
| `backend/tests/test_hash.py` | Hash streaming × hashlib, determinismo, sensibilidade a 1 byte |
| `backend/tests/test_migracoes.py` | Ciclo upgrade → downgrade → upgrade em banco isolado |
| `backend/tests/test_models.py` (ampliado) | 20 tabelas, FKs, integridade referencial, relacionamento completo, `empresas` |
| `backend/tests/etl/fixtures_xlsx.py` | Construtores de planilhas determinísticas (OpenPyXL) |
| `backend/tests/etl/test_motor.py` | Banco vazio, duplicidade, versionamento encadeado, sequências independentes, extensão inválida, coluna ausente, **rollback transacional**, auditoria |
| `backend/tests/etl/test_importadores.py` | Os 5 importadores: linhas mistas, upsert de clientes, versionamento de vigência da carteira, idempotência, estorno negativo, "nunca sobrescrever" faturamento, conformidade de checklist, duplicidades |
| `backend/tests/api/test_importacoes_api.py` | Os 7 endpoints, paginação/filtros, 404 padrão, exclusão de pendente × não-pendente |

### Ajustes em arquivos existentes
`app/main.py` (registro do router), `alembic/env.py` (URL programática respeitada em testes), `pyproject.toml` (pacote `etl*`), `tests/conftest.py` (fixtures: limpeza de banco por teste, `usuario_admin`, `ufs`, `fluxo`, `motor`, `STORAGE_DIR` de teste).

## 3. Cobertura de Testes

| Métrica | Resultado |
|---|---|
| Testes | **44 passando** (10 anteriores + 34 novos) |
| Cobertura total (`app` + `etl`) | **93%** |
| `etl/motor.py` | 91% |
| Loaders | 89–100% |
| Validadores | 80–93% |
| Lint (`ruff`) / Formatação (`black`) / Tipos (`mypy app etl`) | Sem erros |

## 4. Decisões Técnicas

Registradas em detalhe em `docs/DECISIONS.md`, seções 7–9. As principais:

1. **Sem duplicação de modelagem**: das 17 entidades pedidas, 16 já existiam com nomenclatura aprovada (`Venda`→`faturamentos`, `CarteiraCliente`→`carteiras`, `Perfil`→enum, `Região`→`ufs.regiao`, `ArquivoImportado`→`importacao_arquivos`); apenas `empresas` foi criada.
2. **UUID/soft-delete/auditoria de usuário aplicados apenas à tabela nova**, preservando o esquema aprovado das 19 existentes.
3. **`versao=0` para tentativas recusadas** (duplicado/arquivo inválido), mantendo-as auditáveis sem poluir a cadeia de versões.
4. **Carga em transação única com rollback garantido por teste**; o registro da importação sobrevive à falha com status `FALHOU` e mensagem em `importacao_erros`.
5. **Resposta de checklist duplicada entre importações é rejeitada por linha** — conflito documentado entre a UQ do dicionário e a regra 5.4.3; prevaleceu o schema + "nunca sobrescrever".
6. **Endpoints ainda sem autenticação** (restrição do prompt); a trava de perfil Administrador entra na sprint de autenticação.

## 5. Pendências

1. **Upload via API/interface** — explicitamente fora do escopo desta sprint; o motor está pronto para receber o endpoint `POST /importacoes` (multipart) na sprint correspondente.
2. **Autenticação/autorização dos endpoints de importação** — sprint de autenticação (`SPRINT_02.md` documental / `AUTENTICACAO.md`).
3. **Rollback de negócio de importações** (reabertura de vigências, `REGRAS_DE_NEGOCIO.md`, seção 6) — distinto do rollback transacional entregue; pertence à sprint que expõe `POST /importacoes/{id}/rollback`.
4. **Versionamento de respostas de checklist** — pendente de decisão formal (conflito de especificação documentado em `docs/DECISIONS.md`, seção 9, item 5).
5. **`docker compose up` ponta a ponta** — herdada das sprints anteriores (daemon Docker indisponível neste ambiente).

## 6. Riscos

1. **Encerramento de vínculos por ausência no arquivo de carteira** (`REGRAS_DE_NEGOCIO.md`, seção 5.2, item 3): um arquivo parcial (ex.: só uma regional) encerraria vínculos legítimos de clientes fora dele. Mitigação sugerida: orientação operacional de sempre enviar a carteira completa; ou flag "arquivo parcial" em sprint futura.
2. **Processamento síncrono** (limite de 100k linhas/20 MB, `ETL.md`, seção 5): arquivos grandes bloqueiam a requisição quando o upload HTTP chegar; avaliar processamento assíncrono pós-POC.
3. **`Cliente` sem vínculo com `Empresa`**: `empresas` existe isolada (single-tenant); a introdução de `tenant_id` nas demais tabelas é evolução pós-POC (`TUTORIAL.md`, seção 15) — risco baixo, decisão já prevista.
4. **Duas fontes de verdade para status de visita em arquivo** (`STATUS` livre na planilha): valores fora do enum são rejeitados por linha, o que pode gerar volume de erros se a operação usar grafias variadas; monitorar nos primeiros usos reais.

## 7. Sugestões para a Sprint 3

1. **Autenticação e usuários** (JWT + bcrypt + RBAC, `AUTENTICACAO.md`/`PERMISSOES.md`) — desbloqueia a proteção dos endpoints de importação já entregues e o vínculo real de `usuario_id` no upload.
2. **Endpoint de upload** (`POST /importacoes`, multipart) — o motor já aceita qualquer arquivo em `incoming/`; falta apenas a borda HTTP.
3. **Rollback de negócio** (`POST /importacoes/{id}/rollback` com reabertura de vigências de carteira e justificativa obrigatória).
4. Resolver formalmente (via atualização de especificação) o versionamento de respostas de checklist.
