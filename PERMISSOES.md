# PERMISSOES.md — Controle de Acesso por Perfil (RBAC)

## 1. Finalidade

Este documento especifica, de forma exaustiva, o que cada um dos 4 perfis de usuário (Administrador, Supervisor, Promotor, Diretoria) pode acessar e executar no Promotores BI. É a referência obrigatória para a implementação da camada de autorização (`api/dependencies.py`, `BACKEND.md`) e para os testes de controle de acesso (`TESTES.md`).

## 2. Modelo de Autorização

O sistema implementa **RBAC (Role-Based Access Control)** simples, com 4 papéis fixos (`usuarios.perfil`), combinado com **escopo de dados** determinado pelo vínculo do usuário (`promotor_id` ou `supervisor_id`):

1. **Autorização por Funcionalidade:** determina se o perfil pode acessar uma rota/ação, independentemente dos dados (ex.: apenas Administrador pode importar arquivos).
2. **Autorização por Escopo de Dados:** determina, dentro de uma funcionalidade permitida, quais registros o usuário pode ver (ex.: um Supervisor só vê promotores de sua própria equipe).

## 3. Matriz de Permissões por Funcionalidade

| Funcionalidade | Administrador | Supervisor | Promotor | Diretoria |
|---|:---:|:---:|:---:|:---:|
| Login/Logout | Sim | Sim | Sim | Sim |
| Gerenciar usuários (CRUD) | Sim | Não | Não | Não |
| Redefinir senha de terceiros | Sim | Não | Não | Não |
| Importar arquivos | Sim | Não | Não | Não |
| Consultar histórico de importações | Sim | Não | Não | Não |
| Executar rollback de importação | Sim | Não | Não | Não |
| Consultar log de auditoria | Sim | Não | Não | Não |
| Consultar/editar cadastro de Clientes | Sim | Consulta | Não | Não |
| Consultar cadastro de Promotores/Supervisores/Vendedores/Laboratórios/Departamentos | Sim | Consulta (equipe) | Não | Consulta |
| Dashboard Executivo | Sim | Não | Não | Sim |
| Dashboard por Promotor — próprio | Sim | — | Sim | — |
| Dashboard por Promotor — equipe | Sim | Sim | Não | Não |
| Dashboard por Promotor — qualquer | Sim | Não | Não | Sim |
| KPIs (todos os endpoints de `/api/v1/kpis`) | Sim | Sim (escopo da equipe) | Sim (escopo próprio) | Sim (escopo total) |
| Exportação (Excel/CSV/PDF) | Sim | Sim (escopo permitido) | Sim (escopo próprio) | Sim (escopo total) |
| Alterar filtros de dashboard (Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor) | Sim (todos os filtros) | Sim (todos, exceto sair do escopo da própria equipe) | Não (visão fixa: própria carteira) | Sim (todos os filtros) |

## 4. Regras de Escopo de Dados por Perfil

### 4.1 Administrador
Sem restrição de escopo — acessa todos os dados de todas as regiões, promotores, supervisores e períodos.

### 4.2 Supervisor
1. Toda consulta de promotor, carteira, visita, checklist ou KPI é automaticamente restrita a `promotores.supervisor_id = <supervisor_id do token>`, mesmo que o parâmetro `supervisor_id` não seja explicitamente enviado na requisição.
2. Caso o Supervisor envie explicitamente um `supervisor_id` diferente do seu próprio nos filtros da requisição, a API retorna `403` com código `PERMISSAO_NEGADA` — um Supervisor nunca pode consultar dados de outra equipe.
3. Não acessa o Dashboard Executivo consolidado (todas as equipes); acessa apenas a visão agregada da própria equipe, exposta pelo mesmo endpoint `/api/v1/dashboard/promotor/{promotor_id}` iterado para cada promotor da equipe, ou por uma variação agregada de equipe — modelagem de endpoint específica de agregação por equipe é tratada como extensão de `DASHBOARD.md`, seção 4, dentro do mesmo contrato de dados do Dashboard Executivo, porém pré-filtrada pelo backend ao `supervisor_id` do token.

### 4.3 Promotor
1. Toda consulta é automaticamente restrita a `promotor_id = <promotor_id do token>`, independentemente de qualquer parâmetro de filtro enviado.
2. Envio explícito de `promotor_id` diferente do próprio nos filtros da requisição resulta em `403` com código `PERMISSAO_NEGADA`.
3. Não possui acesso às telas/rotas de importação, gestão de usuários ou auditoria — tentativa de acesso resulta em `403`.
4. Não visualiza dados de outros promotores em nenhuma tela, inclusive em componentes de "Ranking" — a tela de Ranking exibe a posição do próprio promotor e valores agregados/anônimos dos demais quando aplicável (regra de exibição detalhada em `DASHBOARD.md`, seção 6).

### 4.4 Diretoria
1. Acesso somente leitura a todos os dados agregados (Dashboard Executivo e Dashboard por Promotor de qualquer promotor), com todos os filtros disponíveis, sem restrição de escopo.
2. Não possui acesso a telas operacionais: importação, cadastro/edição de usuários, cadastro/edição de clientes, rollback e auditoria.
3. Pode exportar qualquer visão à qual tenha acesso de leitura.

## 5. Implementação Técnica da Autorização

1. Cada rota declara o(s) perfil(is) mínimo(s) exigido(s) via dependência `Depends(exige_perfil(...))` (`BACKEND.md`, `api/dependencies.py`), verificada **após** `Depends(get_usuario_autenticado)` (`AUTENTICACAO.md`, seção 7).
2. A aplicação de escopo de dados (seção 4) é implementada na camada de `services/`, nunca apenas na camada de `api/` — garantindo que mesmo chamadas internas entre serviços respeitem o escopo, e não apenas a validação de entrada da rota.
3. Toda tentativa de acesso negado (`403`) gera um registro em `logs_auditoria` com `acao` apropriada e indicação de tentativa não autorizada no campo `dados_depois`, conforme `AUDITORIA.md`.

## 6. Tabela de Decisão Resumida (Perfil Mínimo por Grupo de Rotas)

| Prefixo de Rota | Perfil mínimo exigido |
|---|---|
| `/api/v1/auth/*` | Público (`login`) / Autenticado (demais) |
| `/api/v1/usuarios/*` | Administrador |
| `/api/v1/promotores/*`, `/api/v1/supervisores/*`, `/api/v1/vendedores/*`, `/api/v1/laboratorios/*`, `/api/v1/departamentos/*` | Supervisor (leitura) / Administrador (escrita) |
| `/api/v1/clientes/*` | Supervisor (leitura) / Administrador (escrita) |
| `/api/v1/carteiras/*` | Supervisor |
| `/api/v1/importacoes/*` | Administrador |
| `/api/v1/dashboard/executivo` | Diretoria (inclui Administrador) |
| `/api/v1/dashboard/promotor/*` | Promotor (escopo próprio) |
| `/api/v1/kpis/*` | Promotor (escopo próprio) |
| `/api/v1/auditoria/*` | Administrador |
| `/api/v1/exportacoes/*` | Conforme o recurso exportado (herda a regra do dado de origem) |

Nota: "Perfil mínimo" aqui indica o menor nível de acesso à **funcionalidade**; perfis superiores na hierarquia de dados (Administrador sempre; Diretoria para leitura consolidada) têm acesso adicional conforme a seção 3.

## 7. Hierarquia de Herança de Acesso

Para simplificar a leitura da matriz, adota-se a seguinte convenção de herança **apenas para leitura de dashboards e KPIs**: Administrador ⊇ Diretoria ⊇ Supervisor ⊇ Promotor, em termos de abrangência de dados (não em termos de funcionalidades operacionais, que são exclusivas do Administrador conforme seção 3). Esta convenção não se aplica às funcionalidades de escrita (importação, cadastro), exclusivas do Administrador.
