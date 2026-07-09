# TESTES.md — Estratégia de Testes

## 1. Finalidade

Este documento define a estratégia de testes automatizados do Promotores BI, aplicável a partir da primeira linha de código (Sprint 00) e obrigatória em todas as Sprints subsequentes, conforme `MASTER_PROMPT.md`, seção 3, item 6.

## 2. Pirâmide de Testes

```
                ▲
               / \        E2E (poucos, fluxos críticos completos)
              /---\
             /     \      Integração (repositórios, importadores, API)
            /-------\
           /         \    Unitários (services, validadores, cálculo de KPI)
          /___________\
```

## 3. Backend — Ferramentas

1. **Test runner:** `pytest`.
2. **Cobertura:** `pytest-cov`, relatório mínimo obrigatório de **80% de cobertura de linha** na camada `services/` e **90%** na camada `services/importacao/` e `services/kpi_service.py` (lógica crítica de negócio).
3. **Fixtures de banco:** SQLite em arquivo temporário por sessão de teste, com `alembic upgrade head` aplicado antes da suíte (`conftest.py`, `BACKEND.md`).
4. **Fakes de repositório:** implementações em memória dos `Protocols` de `domain/contratos/`, utilizadas nos testes unitários de `services/` para isolar a lógica de negócio da camada de persistência real.
5. **Cliente de API:** `TestClient` do FastAPI (`starlette.testclient`), utilizado nos testes de integração de `api/routers/`.

## 4. Backend — Categorias de Teste

### 4.1 Testes Unitários (`tests/unit/`)
- Cálculo de cada KPI (`KPIS.md`), com casos de borda: denominador zero, ausência de vínculo de carteira, faturamento negativo, mês sem dado.
- Regras de validação por tipo de arquivo (`VALIDADOR.md`), um teste por código de regra (`CAM-001`, `REF-002`, `FAT-001`, etc.), cobrindo caso válido e caso inválido.
- Regras de versionamento de carteira (`REGRAS_DE_NEGOCIO.md`, seção 5.2): abertura de novo vínculo, encerramento de vínculo por troca de promotor, encerramento por ausência no novo arquivo.
- Classificação de hash (`HASH.md`, seção 3): arquivo novo, repetido, alterado, reenvio pós-falha.
- Regras de autorização por perfil (`PERMISSOES.md`): matriz completa de acesso permitido/negado por combinação perfil × funcionalidade.
- Geração e validação de JWT, hashing de senha (`AUTENTICACAO.md`).

### 4.2 Testes de Integração (`tests/integration/`)
- Cada `repository` testado contra um banco SQLite real (migrado via Alembic), validando consultas, `joins`, índices funcionais e integridade referencial (`ondelete` conforme `DICIONARIO_DE_DADOS.md`).
- Pipeline de importação completo (`ETL.md`), do upload de um arquivo de exemplo até a persistência final, para cada um dos 5 tipos de arquivo, incluindo casos com linhas mistas (válidas e inválidas no mesmo arquivo).
- Fluxo completo de rollback de importação (`REGRAS_DE_NEGOCIO.md`, seção 6), verificando reabertura de vigências de carteira.
- Endpoints de API (`API.md`) via `TestClient`, cobrindo códigos de status esperados (200/201/400/401/403/404/409/422) para os principais cenários de cada rota.

### 4.3 Testes End-to-End (`tests/e2e/`, a partir da Sprint 12)
- Fluxo completo: login → upload de Base de Clientes → upload de Carteira → upload de Faturamento → consulta de Dashboard Executivo → exportação em Excel.
- Fluxo de controle de acesso: tentativa de acesso de um usuário Promotor a rota de importação, verificando `403` de ponta a ponta.
- Fluxo de rollback: importação de Carteira → rollback → verificação de que o Dashboard reflete o estado anterior.

## 5. Frontend — Ferramentas

1. **Test runner e assertions:** `Vitest` (nativamente compatível com Vite, mantendo a stack sem adição de ferramentas fora do ecossistema já definido).
2. **Testes de componente:** `@testing-library/react`, priorizando testes que simulam interação do usuário (clique, digitação, seleção de filtro) sobre testes de implementação interna.
3. **Mock de API:** interceptação das chamadas de `src/services/` via mocks de módulo (`vi.mock`), retornando payloads de exemplo consistentes com `API.md`.

## 6. Frontend — Categorias de Teste

1. **Componentes de UI (`DESIGN_SYSTEM.md`):** `Button`, `Table`, `KpiCard`, `Modal`, `FileUpload` — renderização correta de variantes e estados (carregando/vazio/erro).
2. **Hooks (`FRONTEND.md`, seção 3):** `useAuth`, `useFiltrosDashboard`, `usePaginacao` — comportamento de estado isolado da UI.
3. **Fluxos de página (`UX.md`):** login com sucesso/falha, aplicação de filtro no Dashboard Executivo, upload de arquivo com sucesso/erro, tentativa de acesso negado.
4. **Guardas de rota (`RotaPrivada`, `RotaPorPerfil`):** redirecionamento correto conforme sessão e perfil.

## 7. Metas de Cobertura por Sprint

| Sprint | Meta de cobertura backend | Meta de cobertura frontend |
|---|---|---|
| 00–02 | ≥ 70% dos módulos criados | N/A (frontend inicia na Sprint 09) |
| 03–08 | ≥ 80% geral, ≥ 90% em `services/importacao/` e `kpi_service.py` | N/A |
| 09–11 | mantém metas de backend | ≥ 70% dos componentes/páginas criados |
| 12 | ≥ 80% geral consolidado | ≥ 75% geral consolidado, suíte E2E completa passando |

## 8. Dados de Teste (Fixtures)

1. Arquivos `.xlsx` de exemplo para cada um dos 5 tipos de importação são mantidos em `backend/tests/fixtures/arquivos/`, cobrindo: caso 100% válido, caso com linhas mistas, caso com coluna obrigatória ausente (falha estrutural), caso de arquivo duplicado (mesmo conteúdo de outro fixture).
2. Dados de seed mínimos (UFs, um conjunto reduzido de Cidades, um usuário Administrador de teste) são gerados via fixture de `conftest.py`, nunca dependendo de dados de produção.

## 9. Execução Contínua

1. Toda suíte (backend e frontend) é executada automaticamente no pipeline de CI a cada Pull Request, conforme `GITHUB.md`.
2. Nenhum Pull Request é mesclado (`merge`) com testes falhando ou com cobertura abaixo da meta da Sprint corrente (seção 7), conforme `MASTER_PROMPT.md`, seção 6.

## 10. Testes de Regressão de Regras de Negócio Críticas

Casos de teste obrigatórios e permanentes (nunca removidos em Sprints futuras, apenas estendidos), por representarem as garantias centrais do produto (`REGRAS_DE_NEGOCIO.md`, seção 2):

1. "Nunca sobrescrever": um teste que garante que, após duas importações sucessivas de Faturamento para o mesmo período, ambos os conjuntos de registros permanecem fisicamente no banco.
2. "Sempre versionar": um teste que garante que toda importação bem-sucedida recebe `versao` estritamente maior que a anterior do mesmo `tipo_arquivo`.
3. "Sempre validar antes de importar": um teste que garante que nenhuma linha inválida é persistida na tabela de destino, apenas em `importacao_erros`.
4. "Sempre permitir rollback": um teste que garante que o estado de `carteiras` após um rollback de importação de Carteira é idêntico ao estado imediatamente anterior à importação revertida.
