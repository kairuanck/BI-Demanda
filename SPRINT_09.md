# SPRINT_09.md — Frontend Base e Design System

## 1. Objetivo

Implementar o scaffold do frontend (Vite + React + TailwindCSS), o fluxo completo de autenticação no cliente, o layout base da aplicação e o conjunto de componentes reutilizáveis do design system, preparando a base sobre a qual os dashboards (Sprint 10) e demais telas (Sprint 11) serão construídos.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `FRONTEND.md`, `DESIGN_SYSTEM.md`, `UX.md`, `TELAS.md` (seção 2), `API.md` (seção 4).

## 3. Pré-condições

Sprint 02 concluída (autenticação disponível no backend). Sprint 00 concluída (scaffold inicial do frontend).

## 4. Escopo (Backlog Detalhado)

### 4.1 Camada de Serviço e Sessão
1. Implementar `src/services/httpClient.js`: wrapper `fetch` com injeção automática de `Authorization`, tratamento de erro padronizado (`ApiError`, `API.md`, seção 13) e renovação automática de token em `401`/`TOKEN_INVALIDO` (`FRONTEND.md`, seção 5).
2. Implementar `src/services/authService.js`: `login`, `logout`, `me`, `refresh`.
3. Implementar `src/context/AuthContext.jsx`: estado de sessão, `usuario`, `perfil`, `login()`, `logout()`.
4. Implementar `src/routes/RotaPrivada.jsx` e `src/routes/RotaPorPerfil.jsx` (`FRONTEND.md`, seção 4).
5. Implementar `src/constants/permissoes.js`, replicando a matriz de `PERMISSOES.md`, seção 6, como constante consumida pelas guardas de rota.

### 4.2 Design System — Componentes Base (`components/ui/`)
1. Implementar todos os componentes listados em `DESIGN_SYSTEM.md`, seção 6: `Button`, `Card`, `KpiCard`, `Table`, `Badge`, `Modal`, `Toast`, `Select`, `MultiSelect`, `DateRangePicker`, `SearchInput`, `Tabs`, `ProgressBar`, `FileUpload`, `EmptyState`, `ErrorState`, `Skeleton`, `Avatar`, `Breadcrumb`.
2. Configurar os tokens de cor, tipografia e espaçamento (`DESIGN_SYSTEM.md`, seções 3–5) como extensão do tema Tailwind (`tailwind.config.js`).
3. Implementar `src/components/Icon.jsx`, wrapper padronizado sobre `lucide-react` (`DESIGN_SYSTEM.md`, seção 11).

### 4.3 Layout Base
1. Implementar `src/components/layout/Shell.jsx`, `Sidebar.jsx`, `Topbar.jsx`, `PageHeader.jsx` (`DESIGN_SYSTEM.md`, seção 7), com itens de menu renderizados condicionalmente conforme `PERMISSOES.md`.

### 4.4 Tela de Login
1. Implementar a tela de Login (`TELAS.md`, seção 2), incluindo o fluxo de redirecionamento por perfil (`UX.md`, seção 2).

### 4.5 Roteamento Base
1. Implementar `App.jsx` com todas as rotas de `FRONTEND.md`, seção 4, incluindo `/acesso-negado` e o fallback `404` — as páginas de destino ainda podem ser placeholders mínimos nesta Sprint para as rotas cujas telas completas só são implementadas nas Sprints 10 e 11, desde que a navegação e a guarda de perfil já estejam funcionais.

## 5. Fora de Escopo desta Sprint

1. Conteúdo completo do Dashboard Executivo e do Dashboard por Promotor (gráficos, KPIs reais) — Sprint 10.
2. Telas de importação, cadastros e auditoria com funcionalidade completa — Sprint 11.

## 6. Entregáveis

1. Frontend com autenticação funcional de ponta a ponta contra o backend.
2. Conjunto completo de componentes de design system implementados e testados isoladamente.
3. Layout base (Shell/Sidebar/Topbar) funcional, com navegação condicionada por perfil.
4. Roteamento completo, com placeholders navegáveis para as telas ainda não implementadas em conteúdo.

## 7. Critérios de Aceite

1. Login com credenciais válidas redireciona corretamente conforme o perfil do usuário (`UX.md`, seção 2).
2. Login com credenciais inválidas exibe `Toast` de erro sem detalhar o motivo.
3. Sessão expirada (token inválido) redireciona automaticamente para `/login`.
4. `Sidebar` exibe apenas os itens de menu permitidos ao perfil autenticado, validado para os 4 perfis.
5. Tentativa de navegação direta (via URL) a uma rota fora do perfil do usuário redireciona para `/acesso-negado`.
6. Todos os componentes de `DESIGN_SYSTEM.md`, seção 6, possuem testes de renderização básicos (`TESTES.md`, seção 6).
7. `npm run build` gera o artefato de produção sem erros.
8. Meta de cobertura de testes de frontend da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. Os placeholders de tela mencionados na seção 4.5 devem ser claramente identificáveis como incompletos (ex.: um `EmptyState` com texto "Em construção") e nunca simular dados falsos de negócio, para não gerar falsa sensação de completude ao usuário de demonstração antes da Sprint 10/11.
