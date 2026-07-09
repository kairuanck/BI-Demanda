# TELAS.md — Inventário de Telas

## 1. Finalidade

Este documento especifica todas as telas do frontend do Promotores BI: propósito, componentes utilizados (`DESIGN_SYSTEM.md`), dados consumidos (`API.md`) e perfil de acesso (`PERMISSOES.md`). Os fluxos de navegação entre telas estão em `UX.md`.

## 2. Tela — Login

- **Rota:** `/login`
- **Perfil:** Público
- **Componentes:** `Card`, campo de e-mail, campo de senha, `Button` (primary), `Toast` (erro de credenciais).
- **Dados:** `POST /api/v1/auth/login`.
- **Comportamento:** ao autenticar com sucesso, redireciona conforme perfil (`FRONTEND.md`, seção 4). Erro de credenciais exibe `Toast` de erro sem detalhar o motivo (`AUTENTICACAO.md`, seção 4).

## 3. Tela — Dashboard Executivo

- **Rota:** `/dashboard/executivo`
- **Perfil:** Diretoria, Administrador
- **Componentes:** `PageHeader`, `BarraDeFiltros` (todos os filtros), grade de `KpiCard` (Carteira, Cobertura, Positivação, Fora da Carteira, Visitas, Checklists), `BarChart` (faturamento por região), `DoughnutChart` (distribuição por Tipo de Promotor), `StackedBarChart` (faturamento por Laboratório/Departamento ao longo dos meses), `RankingList` (top e bottom promotores), botão de exportação.
- **Dados:** `GET /api/v1/dashboard/executivo` com os filtros da `BarraDeFiltros` (`API.md`, seção 10; `DASHBOARD.md`, seção 3).
- **Comportamento:** alteração de qualquer filtro dispara nova requisição, atualizando todos os blocos simultaneamente. Clique em um `KpiCard` expande o detalhamento correspondente (`DESIGN_SYSTEM.md`, seção 6).

## 4. Tela — Dashboard por Promotor

- **Rota:** `/dashboard/promotor/:id`
- **Perfil:** Promotor (próprio), Supervisor (equipe), Administrador, Diretoria
- **Componentes:** `PageHeader` (nome e tipo do promotor), `BarraDeFiltros` (Ano, Mês — demais filtros ocultos, pois o escopo já é o promotor), `Tabs` (Visão Geral / Carteira / Visitas / Checklists / Ranking), grade de `KpiCard` (Cobertura, Positivação, Visitas Realizadas x Planejadas, Conformidade de Checklist), `LineChart` (evolução mensal de faturamento da carteira), `Table` (lista de clientes da carteira com indicador de positivação e última visita), `ProgressBar` (cobertura e conformidade), botão de exportação.
- **Dados:** `GET /api/v1/dashboard/promotor/{promotor_id}` (`API.md`, seção 10).
- **Comportamento:** se o usuário autenticado for `PROMOTOR`, a rota é automaticamente resolvida para o próprio `id` (`/dashboard/promotor/:id` com `:id` fixo, sem seleção manual de outro promotor). Supervisores e Administradores acessam esta tela a partir de um seletor de promotor exibido na tela de listagem (seção 8).

## 5. Tela — Nova Importação

- **Rota:** `/importacao/nova`
- **Perfil:** Administrador
- **Componentes:** `PageHeader`, `Select` (Tipo de Arquivo: Clientes/Carteira/Faturamento/Checklist/Visitas), `FileUpload`, `Button` (Enviar), `Modal` de confirmação, `Toast` de resultado.
- **Dados:** `POST /api/v1/importacoes` (`API.md`, seção 9).
- **Comportamento:** ao selecionar o arquivo e confirmar o envio, a tela exibe estado de carregamento até a conclusão do processamento síncrono (`ETL.md`); ao concluir, redireciona para a tela de Detalhe de Importação (seção 7) com o resultado.

## 6. Tela — Histórico de Importações

- **Rota:** `/importacao/historico`
- **Perfil:** Administrador
- **Componentes:** `PageHeader`, `BarraDeFiltros` (Tipo de Arquivo, Status), `Table` (colunas: Tipo, Versão, Nome do Arquivo, Status (`Badge`), Usuário, Data, Linhas Válidas/Inválidas), ação por linha "Ver Detalhes", "Baixar Arquivo Original", "Reverter" (quando aplicável).
- **Dados:** `GET /api/v1/importacoes` (`API.md`, seção 9).
- **Comportamento:** cadeia de versões de um mesmo `tipo_arquivo` é visualmente agrupada e expansível, exibindo a árvore de versões (`HASH.md`, seção 5).

## 7. Tela — Detalhe de Importação

- **Rota:** `/importacao/historico/:id`
- **Perfil:** Administrador
- **Componentes:** `PageHeader`, `Card` de metadados (status, versão, hash, contadores), `Tabs` (Resumo / Erros de Validação), `Table` (erros paginados: linha, coluna, valor recebido, mensagem — `VALIDADOR.md`), `Button` "Reverter Importação" (com `Modal` de confirmação e campo de justificativa).
- **Dados:** `GET /api/v1/importacoes/{id}`, `GET /api/v1/importacoes/{id}/erros`, `POST /api/v1/importacoes/{id}/rollback` (`API.md`, seção 9).
- **Comportamento:** o botão "Reverter Importação" só é habilitado quando a importação atende às condições de `REGRAS_DE_NEGOCIO.md`, seção 6, item 4 (não haver versão posterior concluída do mesmo tipo de arquivo).

## 8. Tela — Gestão de Usuários

- **Rota:** `/cadastros/usuarios`
- **Perfil:** Administrador
- **Componentes:** `PageHeader` (ação "Novo Usuário"), `SearchInput`, `BarraDeFiltros` (Perfil, Status), `Table` (Nome, E-mail, Perfil (`Badge`), Status, Último Login), ações por linha "Editar", "Redefinir Senha", "Ativar/Inativar".
- **Dados:** `GET /api/v1/usuarios`, `PUT /api/v1/usuarios/{id}`, `PATCH /api/v1/usuarios/{id}/senha`, `PATCH /api/v1/usuarios/{id}/status` (`API.md`, seção 5).
- **Sub-tela — Formulário de Usuário (Modal):** campos Nome, E-mail, Perfil (`Select`), vínculo condicional (Promotor ou Supervisor, exibido conforme o Perfil selecionado), Senha inicial (apenas na criação).

## 9. Tela — Gestão de Clientes

- **Rota:** `/cadastros/clientes`
- **Perfil:** Supervisor (leitura), Administrador (leitura e inativação)
- **Componentes:** `PageHeader`, `SearchInput`, `BarraDeFiltros` (UF, Cidade, Canal, Status), `Table` (Código, Razão Social, Cidade/UF, Canal, Promotor Vigente, Status), ação por linha "Ver Detalhes", "Ativar/Inativar" (somente Administrador).
- **Dados:** `GET /api/v1/clientes` (`API.md`, seção 7).

## 10. Tela — Detalhe de Cliente

- **Rota:** `/cadastros/clientes/:id`
- **Perfil:** Supervisor, Administrador
- **Componentes:** `PageHeader`, `Card` de dados cadastrais, `Table` de histórico de carteira (todos os promotores que já atenderam o cliente, com período de vigência), `Table` de últimas visitas, `LineChart` de faturamento histórico do cliente.
- **Dados:** `GET /api/v1/clientes/{id}` (`API.md`, seção 7).

## 11. Tela — Gestão de Promotores

- **Rota:** `/cadastros/promotores`
- **Perfil:** Administrador (leitura e edição), Supervisor (leitura restrita à própria equipe)
- **Componentes:** `PageHeader`, `SearchInput`, `BarraDeFiltros` (Tipo de Promotor, Supervisor, Status), `Table` (Nome, Tipo (`Badge`), Supervisor, Status, Data de Admissão), ação por linha "Editar", "Ver Dashboard".
- **Dados:** `GET /api/v1/promotores`, `PUT /api/v1/promotores/{id}` (`API.md`, seção 6).

## 12. Tela — Auditoria

- **Rota:** `/auditoria`
- **Perfil:** Administrador
- **Componentes:** `PageHeader`, `BarraDeFiltros` (Entidade, Ação, Usuário, Intervalo de Data), `Table` (Data/Hora, Usuário, Ação (`Badge`), Entidade, Resumo), ação por linha "Ver Detalhes" (`Modal` exibindo `dados_antes`/`dados_depois` formatados).
- **Dados:** `GET /api/v1/auditoria`, `GET /api/v1/auditoria/{id}` (`API.md`, seção 11).

## 13. Tela — Acesso Negado

- **Rota:** `/acesso-negado`
- **Perfil:** Autenticado (qualquer)
- **Componentes:** `EmptyState` com ícone de bloqueio, mensagem explicativa, botão "Voltar ao início".

## 14. Tela — Não Encontrado (404)

- **Rota:** `*` (fallback)
- **Perfil:** Público
- **Componentes:** `EmptyState`, botão "Voltar ao início".

## 15. Resumo de Telas por Perfil

| Perfil | Telas acessíveis |
|---|---|
| Administrador | Todas |
| Supervisor | Dashboard por Promotor (equipe), Gestão de Clientes (leitura), Gestão de Promotores (leitura da equipe) |
| Promotor | Dashboard por Promotor (próprio) |
| Diretoria | Dashboard Executivo, Dashboard por Promotor (qualquer, somente leitura) |

## 16. Componentes de Exportação Presentes em Múltiplas Telas

As telas de Dashboard Executivo, Dashboard por Promotor, Gestão de Clientes e Gestão de Promotores incluem um menu de exportação padronizado (`DESIGN_SYSTEM.md`, seção 6; `FRONTEND.md`, seção 8), com as opções Excel, CSV e PDF, refletindo os filtros correntes da tela.
