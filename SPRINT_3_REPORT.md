# SPRINT_3_REPORT.md — Relatório da Sprint 3 (Integração dos Dados Reais)

## 1. Resumo

A Sprint 3 substituiu o modelo documental por um modelo **adaptado à realidade** dos 5 pacotes de dados reais recebidos (Base de Clientes, Faturamento, SB Promotor, WeCheck + Painel Avert, Checklists). Nenhuma regra de negócio foi assumida: todas as ambiguidades identificadas na engenharia reversa foram levadas ao Product Owner e as 8 definições recebidas (`docs/DECISIONS.md`, seção 12) orientaram toda a implementação.

Entregas principais: identidade UUID interna em todas as entidades; 6 tabelas novas para cobrir estruturas sem equivalente documental (`tipos_promotor`, `clientes_integracao`, `visitas_resumo_sb`, `carteiras_avert`, `visitas_produtos_sb`, `clientes_vendedores`); 7 conectores Strategy (um por origem física real) mais um adaptador legado; deduplicação por hash de conteúdo (além do hash binário já existente); CLI de importação com inferência estrutural de tipo; carga completa executada contra os dados reais, validando o sistema ponta a ponta; serviço de qualidade de dados; e a reescrita integral da suíte de testes com estruturas sintéticas fiéis ao real.

Um bug real de dados foi encontrado e corrigido durante a carga (comparação de nomes acentuados via SQL) — descrito na seção 5.

## 2. Fases Executadas

| Fase | Entrega | Commit |
|---|---|---|
| 1. Engenharia reversa | `docs/DATA_PROFILING.md` (sanitizado) | `9228cb5` |
| 2. Modelagem | UUID interno, 6 tabelas novas, migração Alembic em batch mode | `8b91146` |
| 3–4. Conectores | Strategy Pattern por origem real, hash de conteúdo | `ee5eee9` |
| 5–6. Importação e qualidade | CLI, carga real completa, serviço de qualidade, correção de bug | `7da4a79` |
| 7. Testes | Reescrita completa com estruturas reais (incluída nas fases acima) | — |
| Entrega | Este relatório, `IMPORT_MAPPING.md`, autoauditoria final | commit desta entrega |

## 3. Arquivos Criados/Alterados (visão consolidada)

### Documentação
| Arquivo | Conteúdo |
|---|---|
| `docs/DATA_PROFILING.md` | Estrutura sanitizada dos 5 pacotes reais |
| `docs/DECISIONS.md` (seções 11–15) | Decisões técnicas de todas as fases + definições de negócio do PO |
| `MODEL_CHANGES.md` | Diff de modelagem consolidado (Fase 2) |
| `IMPORT_MAPPING.md` | Mapeamento coluna→campo por origem real (Fases 3–4) |
| `docs/DATA_QUALITY.md` | Métricas sanitizadas da carga real (Fases 5–6) |
| `SPRINT_3_REPORT.md` | Este relatório |

### Modelagem (`backend/app/infrastructure/models/`, `backend/app/domain/enums/`)
- `identidade.py` (UUID interno), `tipo_promotor_model.py`, `cliente_integracao_model.py`, `visita_resumo_sb_model.py`, `carteira_avert_model.py`, `visita_produto_sb_model.py`, `cliente_vendedor_model.py` — todos novos.
- `cliente_model.py`, `promotor_model.py`, `carteira_model.py`, `faturamento_model.py`, `visita_model.py`, `checklist_model.py`, `checklist_pergunta_model.py`, `checklist_resposta_model.py`, `importacao_model.py`, `laboratorio_model.py`, `empresa_model.py`, `log_auditoria_model.py`, e as demais 8 tabelas — migradas para UUID e/ou colunas novas.
- `alembic/versions/2026_07_12_1114_sprint_3_identidade_uuid_e_dados_reais.py` — migração batch validada (upgrade/downgrade/upgrade; diff de autogeração vazio).
- Enums novos: `SistemaOrigem`, `StatusConciliacao`, `CategoriaComercial`; `TipoArquivoImportacao` ampliado (WECHECK, PAINEL_AVERT, SB_PRODUTOS).

### ETL (`backend/etl/`)
| Arquivo | Conteúdo |
|---|---|
| `conectores/base.py` | Contrato `ConectorOrigem` (Strategy) |
| `conectores/clientes.py`, `faturamento.py`, `sb_supervisor.py`, `sb_produtos.py`, `checklist_sb.py`, `wecheck.py`, `painel_avert.py`, `legado.py` | Um conector por origem real + adaptador legado |
| `conectores/checklist_comum.py` | Templates/perguntas/respostas compartilhados entre SB e WeCheck |
| `conectores/leitura.py` | Leitura bruta multi-aba tolerante a cabeçalhos duplicados e schema drift |
| `hash/conteudo.py` | Hash SHA-256 de conteúdo lógico (dedup de cópias fisicamente distintas) |
| `motor.py` | Trocou `(validador, loader)` por `CONECTORES` (Strategy); ganhou `competencia` |
| `cli.py` | CLI de importação com inferência estrutural de tipo |
| `loaders/apoio.py` | Helpers de domínio (`obter_ou_criar_promotor_por_nome`, `registrar_integracao_cliente`, `obter_ou_criar_laboratorio_por_nome`) |

### API/Serviços
- `app/services/qualidade_dados_service.py` — cobertura, pendências e anomalias, somente-leitura.
- `app/api/schemas/importacao_schema.py` — expõe `hash_conteudo`/`competencia`.
- `app/services/importacao_service.py` — reprocessamento propaga `competencia`.

### Testes
| Arquivo | Cobre |
|---|---|
| `tests/etl/fixtures_reais.py` | Planilhas sintéticas fiéis às 7 estruturas reais |
| `tests/etl/test_importadores.py` | Os 7 conectores: casos de sucesso, erro por linha/célula, duplicidade, pendências, "nunca sobrescrever", versionamento de carteira |
| `tests/test_qualidade_dados_service.py` | Cobertura, documentos compartilhados, pendências por sistema |
| `tests/test_cli.py` | Inferência estrutural, execução ponta a ponta, código de saída |
| `tests/test_models.py`, `tests/etl/test_motor.py`, `tests/api/test_importacoes_api.py` | Ajustados para UUID/hash de conteúdo/novas mensagens |

## 4. Cobertura de Testes

| Métrica | Resultado |
|---|---|
| Testes | **61 passando** (52 da Sprint 2 revistos + 9 novos de Fase 5–6) |
| Cobertura (`app` + `etl`) | **89%** |
| Lint (`ruff`) / Formatação (`black`) / Tipos (`mypy app etl`) | Sem erros |
| Migração | `upgrade → downgrade → upgrade` validado; diff de autogeração vazio |

## 5. Achado Real Durante a Carga: Bug de Comparação de Nomes Acentuados

Ao executar a carga completa contra os dados reais (Fase 5), `promotores` chegou a 93 registros — muito acima do esperado. Investigação revelou que `obter_ou_criar_promotor_por_nome` comparava nomes via `func.lower()` do SQL; o `LOWER()` nativo do SQLite não faz *case-folding* de caracteres acentuados (`"Ú"` nunca vira `"ú"`), enquanto o Python normaliza corretamente — logo, cada promotora com nome acentuado gerava um registro novo a cada visita processada. Corrigido comparando em Python (`str.casefold`); a recarga produziu 45 promotores, número consistente com a Fase 1. Teste de regressão dedicado adicionado. Detalhe completo em `docs/DECISIONS.md`, seção 15.3, e `docs/DATA_QUALITY.md`, seção 5.

## 6. Validação Contra os Dados Reais

A carga completa (script ad hoc via `etl/cli.py`, banco descartável — nunca commitado) confirmou, número a número, os achados da Fase 1:

- Deduplicação por hash de conteúdo: 33/34 cópias do relatório Supervisor e 25/26 cópias do Checklist corretamente recusadas como duplicatas lógicas (bytes diferentes, conteúdo idêntico).
- 12 clientes citados pela carteira SB sem correspondência na Base; 43/205 CNPJs do Painel Avert sem correspondência; 152 locais distintos do WeCheck sem código de cliente — todos registrados como pendência em `clientes_integracao`, nenhum cliente criado automaticamente.
- 77 documentos CNPJ/CPF compartilhados por 154 clientes distintos — preservados como cadastros distintos, nunca fundidos.
- 1 código de cliente citado no Faturamento de Janeiro sem cadastro correspondente.

Detalhes sanitizados completos em `docs/DATA_QUALITY.md`.

## 7. Decisões Técnicas

Registradas em detalhe em `docs/DECISIONS.md`, seções 11–15. As principais:

1. UUID interno (`String(36)`) como identidade de todas as entidades, exceto `ufs.sigla` (referência geográfica estática) — preparação explícita para multiempresa.
2. Strategy Pattern para as duas origens de visita (SB Promotor/WeCheck) e para as demais fontes reais — nenhuma regra de sistema específico vaza para o domínio.
3. Duas camadas de deduplicação (hash binário + hash de conteúdo lógico) — exigência real, não hipotética: os pacotes vieram com dezenas de cópias fisicamente distintas do mesmo relatório.
4. `clientes_integracao` como fila de conciliação — nunca criação automática de cliente a partir de dados operacionais, cumprindo a definição de negócio mais repetida do PO.
5. Nenhuma coluna ou aba dos arquivos reais foi descartada; o que não tinha campo de domínio foi preservado em `dados_brutos` (JSON).

## 8. Pendências

1. **Conciliação manual de `clientes_integracao`** (219 pendências na carga de referência) — ferramenta de conciliação é sprint futura.
2. **Endpoint de upload HTTP** — segue fora de escopo (herdado da Sprint 2); `etl/cli.py` é o caminho operacional enquanto isso.
3. **Autenticação** — `etl/cli.py` usa um usuário técnico fixo (`sistema@promotoresbi.local`) por não haver login ainda; a sprint de autenticação deve substituir isso por um usuário real autenticado.
4. **Dashboards/KPIs sobre os dados reais** — o serviço de qualidade desta sprint é fundação para isso, mas a apresentação (gráficos, filtros) é escopo de `DASHBOARD.md`/`KPIS.md`.

## 9. Riscos

1. **`checklist_perguntas` cresce por template a cada coluna nova do mês** (schema drift do WeCheck): sem um processo de curadoria, perguntas efêmeras ou digitadas de forma levemente diferente podem acumular como perguntas distintas. Mitigação sugerida: revisão periódica manual, fora do escopo desta sprint.
2. **Resolução de promotoras por nome (WeCheck/Avert) é case-insensitive mas não fuzzy**: erros de digitação ainda criam pessoas duplicadas. Aceito conscientemente pela definição de negócio (12.4) — mitigação seria uma tela de conciliação manual, sprint futura.
3. **Banco de dados real não commitado**: a atual carga de validação existe apenas no ambiente de execução desta sessão. Rodar novamente (`etl/cli.py`) é reprodutível a partir dos arquivos originais, mas o histórico de auditoria dessa carga específica não persiste entre sessões.

## 10. Sugestões para a Sprint 4

1. Autenticação e usuários (JWT + bcrypt + RBAC) — desbloqueia o upload real e substitui o usuário técnico da CLI.
2. Endpoint de upload (`POST /importacoes`, multipart) reaproveitando a inferência estrutural de `etl/cli.py`.
3. Tela/endpoint de conciliação manual de `clientes_integracao`.
4. Dashboards e KPIs consumindo `qualidade_dados_service.py` como base.
