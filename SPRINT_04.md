# SPRINT_04.md — Importador de Clientes

## 1. Objetivo

Implementar o primeiro importador concreto, plugado ao motor genérico da Sprint 03: a Base de Clientes, incluindo resolução/criação automática de dimensões geográficas (UF/Cidade) e a regra de upsert cadastral.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `IMPORTADOR.md` (seção 3), `VALIDADOR.md` (seções 3–6), `REGRAS_DE_NEGOCIO.md` (seção 5.1), `DICIONARIO_DE_DADOS.md` (tabelas `clientes`, `ufs`, `cidades`).

## 3. Pré-condições

Sprint 03 concluída (motor de importação genérico disponível e testável via `ImportadorArquivo` fake).

## 4. Escopo (Backlog Detalhado)

### 4.1 Repositórios de Apoio
1. Completar `app/repositories/uf_repository.py` e `app/repositories/cidade_repository.py` com métodos de busca por sigla/nome (`buscar_por_sigla`, `buscar_por_nome_uf`, `criar_se_nao_existir`).
2. Completar `app/repositories/cliente_repository.py` com `buscar_por_codigo_externo` e `upsert`.

### 4.2 Validador Específico
1. Implementar `app/services/importacao/validadores/validador_clientes.py`, aplicando as regras `CLI-001` e `CLI-002` (`VALIDADOR.md`, seção 6), além das regras comuns (`REF-001` para UF).

### 4.3 Importador Concreto
1. Implementar `app/services/importacao/importador_clientes.py`, implementando a interface `ImportadorArquivo` (`SPRINT_03.md`, seção 4.2):
   - Extração via Pandas do layout de colunas de `IMPORTADOR.md`, seção 3.1.
   - Transformação e normalização (`ETL.md`, seção 3.3).
   - Validação linha a linha via `validador_clientes.py`.
   - Resolução de UF (deve existir) e Cidade (cria se necessário) — `IMPORTADOR.md`, seção 3.2.
   - Persistência via upsert por `codigo_externo` (`REGRAS_DE_NEGOCIO.md`, seção 5.1, itens 2–4), registrando em `logs_auditoria` cada atualização cadastral individual com `dados_antes`/`dados_depois` (`AUDITORIA.md`, seção 3).
2. Registrar o importador concreto no motor genérico (`app/services/importacao/motor_importacao.py`, mapa de `tipo_arquivo -> ImportadorArquivo`), habilitando `POST /importacoes` com `tipo_arquivo = CLIENTES`.

### 4.4 Endpoints de Consulta de Clientes
1. Implementar `app/api/routers/clientes_router.py`: `GET /clientes`, `GET /clientes/{id}`, `PATCH /clientes/{id}/status` (`API.md`, seção 7), protegidos conforme `PERMISSOES.md`, seção 6.

## 5. Fora de Escopo desta Sprint

1. Importadores de Carteira, Faturamento, Visitas, Checklist — Sprints 05 a 07.
2. Tela de Gestão de Clientes no frontend — Sprint 11.

## 6. Entregáveis

1. Importador de Base de Clientes funcional de ponta a ponta via `POST /importacoes`.
2. Endpoints de consulta de clientes.
3. Arquivos de fixture de teste (`TESTES.md`, seção 8): um `.xlsx` 100% válido, um com linhas mistas, um com coluna obrigatória ausente.
4. Testes unitários do validador e testes de integração do importador completo.

## 7. Critérios de Aceite

1. Upload do arquivo de fixture 100% válido resulta em `status = CONCLUIDA`, com todos os clientes persistidos corretamente, incluindo criação automática de cidades inéditas.
2. Upload do arquivo com linhas mistas resulta em `status = CONCLUIDA_COM_ERROS`, com as linhas inválidas listadas em `GET /importacoes/{id}/erros` com o código de regra correto (`CLI-001`, `CLI-002`, `REF-001`, etc.).
3. Reimportação de um cliente já existente (mesmo `codigo_externo`, dados diferentes) atualiza o registro existente e gera um evento de auditoria com `dados_antes`/`dados_depois` corretos.
4. UF inexistente na tabela `ufs` gera erro de validação `REF-001` para a linha correspondente, sem criação automática de UF.
5. `GET /clientes` retorna corretamente paginado e filtrável por UF, Cidade, Canal e Status.
6. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. Esta é a primeira Sprint em que a ordem de dependência entre importadores (`IMPORTADOR.md`, seção 8) se torna relevante — os testes de integração desta Sprint não dependem de nenhum outro importador, mas os das Sprints 05 e 06 dependerão de clientes previamente importados por este importador.
