# API.md — Especificação da API REST

## 1. Finalidade

Este documento especifica todos os endpoints da API REST do Promotores BI. A arquitetura de camadas que implementa estes endpoints está em `BACKEND.md`; a autenticação em `AUTENTICACAO.md`; as permissões por perfil em `PERMISSOES.md`; as fórmulas de KPI em `KPIS.md`.

## 2. Convenções Gerais

1. Prefixo base: `/api/v1`.
2. Formato de payload: `application/json`, exceto upload de arquivo (`multipart/form-data`) e download de exportação (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `text/csv`, `application/pdf`, conforme o formato solicitado).
3. Autenticação: header `Authorization: Bearer <token JWT>` em todos os endpoints exceto `POST /api/v1/auth/login`.
4. Paginação: parâmetros de query `pagina` (default `1`) e `tamanho_pagina` (default `20`, máximo `100`); resposta paginada sempre no formato:
   ```json
   {
     "itens": [ ... ],
     "pagina": 1,
     "tamanho_pagina": 20,
     "total_itens": 137,
     "total_paginas": 7
   }
   ```
5. Datas em query string e payload: formato ISO 8601 (`AAAA-MM-DD`).
6. Todos os endpoints de listagem/dashboard aceitam os filtros descritos na seção 3, quando aplicável ao recurso.
7. Códigos de status HTTP: `200` (sucesso), `201` (criação), `204` (sucesso sem corpo), `400` (erro de validação de entrada), `401` (não autenticado), `403` (não autorizado), `404` (não encontrado), `409` (conflito — ex.: e-mail já cadastrado, arquivo duplicado), `422` (erro de validação semântica), `500` (erro interno).

## 3. Parâmetros de Filtro Padrão (Dashboards e KPIs)

| Parâmetro | Tipo | Descrição |
|---|---|---|
| ano | int | Filtra por `faturamentos.ano` / ano de referência da métrica. |
| mes | int | Filtra por mês (1–12). |
| uf | string | Sigla da UF. |
| cidade_id | int | Identificador da cidade. |
| departamento_id | int | Identificador do departamento. |
| laboratorio_id | int | Identificador do laboratório. |
| supervisor_id | int | Identificador do supervisor. |
| vendedor_id | int | Identificador do vendedor. |
| promotor_id | int | Identificador do promotor. |
| tipo_promotor | string | `TECNICO` ou `TRADE`. |

Múltiplos filtros são combinados com `AND`. Todos os parâmetros são opcionais; a ausência de um filtro significa "todos os valores". Regras de escopo por perfil (ex.: um Promotor sempre filtrado pelo próprio `promotor_id`) são aplicadas automaticamente pelo backend, conforme `PERMISSOES.md`, independentemente dos parâmetros enviados.

## 4. Autenticação

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Autentica com e-mail/senha, retorna `access_token` e `refresh_token` | Público |
| POST | `/api/v1/auth/refresh` | Renova `access_token` a partir de `refresh_token` válido | Autenticado |
| POST | `/api/v1/auth/logout` | Invalida o `refresh_token` corrente | Autenticado |
| GET | `/api/v1/auth/me` | Retorna dados do usuário autenticado e perfil | Autenticado |

Detalhamento completo do fluxo em `AUTENTICACAO.md`.

## 5. Usuários

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/usuarios` | Lista usuários, paginado, filtrável por `perfil` e `ativo` | Administrador |
| POST | `/api/v1/usuarios` | Cria usuário | Administrador |
| GET | `/api/v1/usuarios/{id}` | Detalha usuário | Administrador |
| PUT | `/api/v1/usuarios/{id}` | Atualiza dados cadastrais do usuário | Administrador |
| PATCH | `/api/v1/usuarios/{id}/senha` | Redefine senha do usuário | Administrador |
| PATCH | `/api/v1/usuarios/{id}/status` | Ativa/inativa o usuário | Administrador |

## 6. Cadastros de Apoio (Promotores, Supervisores, Vendedores, Laboratórios, Departamentos)

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/promotores` | Lista promotores, filtrável por `tipo`, `supervisor_id`, `ativo` | Supervisor |
| GET | `/api/v1/promotores/{id}` | Detalha promotor | Supervisor (apenas da própria equipe) / Administrador |
| PUT | `/api/v1/promotores/{id}` | Atualiza dados cadastrais do promotor | Administrador |
| GET | `/api/v1/supervisores` | Lista supervisores | Administrador |
| GET | `/api/v1/vendedores` | Lista vendedores | Administrador |
| GET | `/api/v1/laboratorios` | Lista laboratórios | Administrador |
| GET | `/api/v1/departamentos` | Lista departamentos | Administrador |
| GET | `/api/v1/ufs` | Lista UFs (dado de referência) | Autenticado |
| GET | `/api/v1/cidades` | Lista cidades, filtrável por `uf` | Autenticado |

## 7. Clientes

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/clientes` | Lista clientes, filtrável por `uf`, `cidade_id`, `canal`, `ativo`, `promotor_id` (via carteira vigente) | Supervisor |
| GET | `/api/v1/clientes/{id}` | Detalha cliente, incluindo histórico de carteira (promotores que já o atenderam) | Supervisor / Administrador |
| PATCH | `/api/v1/clientes/{id}/status` | Ativa/inativa cliente | Administrador |

## 8. Carteira

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/carteiras` | Lista vínculos de carteira, filtrável por `promotor_id`, `cliente_id`, `vigente` (bool) | Supervisor |
| GET | `/api/v1/carteiras/promotor/{promotor_id}` | Carteira vigente completa de um promotor | Promotor (próprio) / Supervisor (equipe) / Administrador |

## 9. Importação

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| POST | `/api/v1/importacoes` | Upload de novo arquivo (`multipart/form-data`, campos `arquivo` e `tipo_arquivo`) | Administrador |
| GET | `/api/v1/importacoes` | Lista importações, paginado, filtrável por `tipo_arquivo`, `status` | Administrador |
| GET | `/api/v1/importacoes/{id}` | Detalha importação, incluindo contadores e metadados | Administrador |
| GET | `/api/v1/importacoes/{id}/erros` | Lista erros de validação da importação, paginado | Administrador |
| GET | `/api/v1/importacoes/{id}/versoes` | Lista a cadeia completa de versões do mesmo `tipo_arquivo` | Administrador |
| POST | `/api/v1/importacoes/{id}/rollback` | Executa rollback da importação | Administrador |
| GET | `/api/v1/importacoes/{id}/arquivo` | Baixa o arquivo binário original armazenado | Administrador |

Corpo de resposta de `GET /api/v1/importacoes/{id}` inclui: `id`, `tipo_arquivo`, `nome_arquivo_original`, `hash_sha256`, `status`, `versao`, `importacao_pai_id`, `total_linhas`, `linhas_validas`, `linhas_invalidas`, `usuario` (nome), `iniciado_em`, `concluido_em`.

## 10. Dashboards e KPIs

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/dashboard/executivo` | Retorna todos os blocos do Dashboard Executivo (`DASHBOARD.md`), aceitando todos os filtros da seção 3 | Diretoria |
| GET | `/api/v1/dashboard/promotor/{promotor_id}` | Retorna todos os blocos do Dashboard por Promotor (`DASHBOARD.md`) | Promotor (próprio) / Supervisor (equipe) / Administrador / Diretoria |
| GET | `/api/v1/kpis/carteira` | KPI de Carteira (`KPIS.md`, seção 3) | Supervisor |
| GET | `/api/v1/kpis/regiao` | KPI de Região (`KPIS.md`, seção 4) | Diretoria |
| GET | `/api/v1/kpis/fora-da-carteira` | KPI de Fora da Carteira (`KPIS.md`, seção 5) | Supervisor |
| GET | `/api/v1/kpis/visitas` | KPI de Visitas (`KPIS.md`, seção 6) | Supervisor |
| GET | `/api/v1/kpis/checklists` | KPI de Checklists (`KPIS.md`, seção 7) | Supervisor |
| GET | `/api/v1/kpis/cobertura` | KPI de Cobertura (`KPIS.md`, seção 8) | Supervisor |
| GET | `/api/v1/kpis/positivacao` | KPI de Positivação (`KPIS.md`, seção 9) | Supervisor |
| GET | `/api/v1/kpis/ranking` | KPI de Ranking (`KPIS.md`, seção 10) | Supervisor |

Todos os endpoints de KPI aceitam os filtros da seção 3 e retornam, no mínimo, `{ "valor": ..., "detalhamento": [...] }`, onde `detalhamento` contém a quebra por dimensão relevante ao KPI (ver `KPIS.md` para o formato exato de cada um).

## 11. Auditoria

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/auditoria` | Lista eventos de `logs_auditoria`, paginado, filtrável por `entidade`, `acao`, `usuario_id`, `data_inicio`, `data_fim` | Administrador |
| GET | `/api/v1/auditoria/{id}` | Detalha um evento de auditoria, incluindo `dados_antes`/`dados_depois` | Administrador |

## 12. Exportação

| Método | Rota | Descrição | Perfil mínimo |
|---|---|---|---|
| GET | `/api/v1/exportacoes/dashboard-executivo` | Exporta o Dashboard Executivo no formato solicitado (`?formato=xlsx\|csv\|pdf`), aplicando os filtros da seção 3 | Diretoria |
| GET | `/api/v1/exportacoes/dashboard-promotor/{promotor_id}` | Exporta o Dashboard por Promotor no formato solicitado | Promotor (próprio) / Supervisor (equipe) / Administrador / Diretoria |
| GET | `/api/v1/exportacoes/clientes` | Exporta a listagem de clientes filtrada | Supervisor |
| GET | `/api/v1/exportacoes/carteiras` | Exporta a listagem de carteira filtrada | Supervisor |

## 13. Tratamento de Erros — Formato Padrão

Toda resposta de erro segue o formato:

```json
{
  "erro": {
    "codigo": "ARQUIVO_DUPLICADO",
    "mensagem": "Este arquivo já foi importado anteriormente.",
    "detalhes": {
      "importacao_original_id": 42,
      "importado_em": "2026-05-10T14:32:00Z"
    }
  }
}
```

Códigos de erro padronizados incluem: `NAO_AUTENTICADO`, `PERMISSAO_NEGADA`, `RECURSO_NAO_ENCONTRADO`, `ARQUIVO_DUPLICADO`, `ARQUIVO_INVALIDO`, `VALIDACAO_FALHOU`, `CONFLITO_DE_DADOS`, `ERRO_INTERNO`.

## 14. Versionamento da API

1. A API é versionada via prefixo de URL (`/api/v1`). Alterações incompatíveis (breaking changes) exigem introdução de `/api/v2`, mantendo `/api/v1` funcional até depreciação formal — fora do escopo da POC, referência para evolução futura (`ROADMAP.md`).
2. Dentro da POC (Sprints 00–12), apenas `/api/v1` existe.

## 15. Documentação Interativa

A documentação interativa (Swagger UI) é servida em `/docs` e a especificação OpenAPI em `/openapi.json`, geradas automaticamente pelo FastAPI a partir dos routers e schemas Pydantic (`BACKEND.md`, seção 10).
