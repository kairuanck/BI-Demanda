# PROMPTS.md — Prompts Operacionais para o Claude Code

## 1. Finalidade

Este documento contém os **prompts prontos para uso**, um por Sprint, a serem colados diretamente na sessão do Claude Code (terminal, IDE ou Claude Code on the web) para disparar a implementação de cada etapa do projeto Promotores BI.

Cada prompt pressupõe que:

1. O repositório já contém toda a documentação (`README.md` até `SPEC_INDEX.md`).
2. O Claude Code tem acesso de leitura a todo o repositório.
3. O arquivo `MASTER_PROMPT.md` já foi apresentado ao Claude Code na sessão (diretamente ou via `CLAUDE.md`), OU está referenciado no início de cada prompt abaixo.

Não repita explicações de arquitetura nos prompts abaixo — eles apenas **apontam** para os documentos corretos, conforme a diretriz de "nunca reescrever o que já está documentado".

## 2. Prompt de Inicialização de Sessão (usar uma vez, antes da Sprint 00)

```
Você é o Engenheiro de Software Implementador do projeto Promotores BI.

Leia, nesta ordem, os seguintes arquivos deste repositório:
1. README.md
2. PROJECT.md
3. MASTER_PROMPT.md
4. ROADMAP.md

Confirme que compreendeu:
- A stack tecnológica obrigatória.
- As regras invioláveis do MASTER_PROMPT.md.
- A ordem de dependência das Sprints descrita em ROADMAP.md.

Não implemente nada ainda. Ao final, apenas confirme a leitura e aguarde o prompt da Sprint 00.
```

## 3. Prompt — Sprint 00 (Fundação do Projeto)

```
Execute a Sprint 00 do projeto Promotores BI, conforme especificado em SPRINT_00.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, BACKEND.md, FRONTEND.md, GITHUB.md, SPRINT_00.md.

Implemente exclusivamente os entregáveis listados na seção "Entregáveis" de SPRINT_00.md.
Ao final, valide cada item da seção "Critérios de Aceite" de SPRINT_00.md e reporte o resultado.
Commit conforme o padrão descrito em GITHUB.md.
```

## 4. Prompt — Sprint 01 (Modelagem de Dados e Migrations)

```
Execute a Sprint 01 do projeto Promotores BI, conforme especificado em SPRINT_01.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, DATABASE.md, MODELAGEM.md, DER.md, DICIONARIO_DE_DADOS.md, SPRINT_01.md.

Implemente todos os modelos SQLAlchemy e a migração Alembic inicial descritos em DICIONARIO_DE_DADOS.md, exatamente com os nomes de tabelas, colunas, tipos e relacionamentos especificados — não introduza campos ou tabelas adicionais fora do que está documentado.

Ao final, valide os "Critérios de Aceite" de SPRINT_01.md e reporte o resultado.
```

## 5. Prompt — Sprint 02 (Autenticação e Usuários)

```
Execute a Sprint 02 do projeto Promotores BI, conforme especificado em SPRINT_02.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, AUTENTICACAO.md, PERMISSOES.md, API.md, SPRINT_02.md.

Implemente autenticação JWT, hashing de senha com bcrypt, CRUD de usuários e o mecanismo de autorização por perfil (RBAC) exatamente conforme AUTENTICACAO.md e PERMISSOES.md.

Ao final, valide os "Critérios de Aceite" de SPRINT_02.md e reporte o resultado.
```

## 6. Prompt — Sprint 03 (Motor de Importação Base)

```
Execute a Sprint 03 do projeto Promotores BI, conforme especificado em SPRINT_03.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, ETL.md, IMPORTADOR.md, VALIDADOR.md, HASH.md, LOGS.md, SPRINT_03.md.

Implemente o motor de importação genérico (upload, cálculo de hash SHA256, detecção de duplicidade/versão, transação de persistência, registro de erros e log de auditoria), sem ainda implementar os parsers específicos de cada tipo de arquivo — estes serão implementados nas Sprints 04 a 07.

Ao final, valide os "Critérios de Aceite" de SPRINT_03.md e reporte o resultado.
```

## 7. Prompt — Sprint 04 (Importador de Clientes)

```
Execute a Sprint 04 do projeto Promotores BI, conforme especificado em SPRINT_04.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, IMPORTADOR.md (seção Base de Clientes), VALIDADOR.md, DICIONARIO_DE_DADOS.md, SPRINT_04.md.

Implemente o importador de Base de Clientes utilizando o motor genérico da Sprint 03, com todas as validações e regras de resolução de UF/Cidade especificadas.

Ao final, valide os "Critérios de Aceite" de SPRINT_04.md e reporte o resultado.
```

## 8. Prompt — Sprint 05 (Importador de Carteira)

```
Execute a Sprint 05 do projeto Promotores BI, conforme especificado em SPRINT_05.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, IMPORTADOR.md (seção Carteira dos Promotores), VALIDADOR.md, REGRAS_DE_NEGOCIO.md, SPRINT_05.md.

Implemente o importador de Carteira dos Promotores, incluindo a lógica de encerramento de vigência anterior e abertura de nova vigência, sem jamais sobrescrever registros históricos.

Ao final, valide os "Critérios de Aceite" de SPRINT_05.md e reporte o resultado.
```

## 9. Prompt — Sprint 06 (Importador de Faturamento)

```
Execute a Sprint 06 do projeto Promotores BI, conforme especificado em SPRINT_06.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, IMPORTADOR.md (seção Faturamento Mensal), VALIDADOR.md, REGRAS_DE_NEGOCIO.md, SPRINT_06.md.

Implemente o importador de Faturamento Mensal, incluindo resolução de Laboratório, Departamento e Vendedor, e cálculo de campos derivados necessários aos KPIs de Positivação e Fora da Carteira.

Ao final, valide os "Critérios de Aceite" de SPRINT_06.md e reporte o resultado.
```

## 10. Prompt — Sprint 07 (Importador de Visitas e Checklists)

```
Execute a Sprint 07 do projeto Promotores BI, conforme especificado em SPRINT_07.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, IMPORTADOR.md (seções Visitas e Checklists), VALIDADOR.md, REGRAS_DE_NEGOCIO.md, SPRINT_07.md.

Implemente os importadores de Visitas e de Checklists, incluindo o vínculo de respostas de checklist às visitas correspondentes e o cálculo de conformidade.

Ao final, valide os "Critérios de Aceite" de SPRINT_07.md e reporte o resultado.
```

## 11. Prompt — Sprint 08 (API de KPIs e Regras de Negócio)

```
Execute a Sprint 08 do projeto Promotores BI, conforme especificado em SPRINT_08.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, KPIS.md, REGRAS_DE_NEGOCIO.md, API.md, SPRINT_08.md.

Implemente a camada de serviço de cálculo de todos os KPIs definidos em KPIS.md e os endpoints de dashboard definidos em API.md, com suporte completo aos filtros (Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor).

Ao final, valide os "Critérios de Aceite" de SPRINT_08.md e reporte o resultado.
```

## 12. Prompt — Sprint 09 (Frontend Base e Design System)

```
Execute a Sprint 09 do projeto Promotores BI, conforme especificado em SPRINT_09.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, FRONTEND.md, DESIGN_SYSTEM.md, UX.md, SPRINT_09.md.

Implemente o scaffold do frontend (Vite + React + TailwindCSS), o fluxo de autenticação (tela de login, armazenamento e renovação de token), o layout base e os componentes de design system especificados.

Ao final, valide os "Critérios de Aceite" de SPRINT_09.md e reporte o resultado.
```

## 13. Prompt — Sprint 10 (Dashboards)

```
Execute a Sprint 10 do projeto Promotores BI, conforme especificado em SPRINT_10.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, DASHBOARD.md, KPIS.md, GRAFICOS.md, TELAS.md, SPRINT_10.md.

Implemente o Dashboard Executivo e o Dashboard por Promotor, incluindo todos os gráficos Chart.js e cards de KPI especificados, consumindo os endpoints implementados na Sprint 08.

Ao final, valide os "Critérios de Aceite" de SPRINT_10.md e reporte o resultado.
```

## 14. Prompt — Sprint 11 (Importação Frontend, Exportações e Auditoria UI)

```
Execute a Sprint 11 do projeto Promotores BI, conforme especificado em SPRINT_11.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, TELAS.md, UX.md, AUDITORIA.md, API.md, SPRINT_11.md.

Implemente as telas de upload de planilha por tipo de arquivo, histórico de importações com opção de rollback, exportação Excel/CSV/PDF e a tela de log de auditoria.

Ao final, valide os "Critérios de Aceite" de SPRINT_11.md e reporte o resultado.
```

## 15. Prompt — Sprint 12 (Testes, Auditoria Final, Deploy e Hardening)

```
Execute a Sprint 12 do projeto Promotores BI, conforme especificado em SPRINT_12.md.

Documentos de referência obrigatórios: MASTER_PROMPT.md, TESTES.md, AUDITORIA.md, DEPLOY.md, GITHUB.md, SPRINT_12.md.

Complete a cobertura de testes definida em TESTES.md, finalize o pipeline de CI/CD descrito em GITHUB.md, valide o guia de deploy em DEPLOY.md e execute o checklist final de auditoria.

Ao final, valide os "Critérios de Aceite" de SPRINT_12.md, gere um relatório consolidado do estado da POC e reporte o resultado.
```

## 16. Prompt de Verificação Contínua (usar ao final de qualquer Sprint, em caso de dúvida sobre conformidade)

```
Revise o código implementado até agora em relação a MASTER_PROMPT.md, seções 3 (Regras Invioláveis) e 6 (Definition of Done).

Liste, para cada regra, se ela está sendo cumprida (SIM/NÃO) e, em caso de NÃO, o que precisa ser corrigido antes de prosseguir para a próxima Sprint.
```
