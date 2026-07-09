# FRONTEND.md — Arquitetura de Frontend

## 1. Finalidade

Este documento especifica a arquitetura do frontend do Promotores BI, construído em **React 18** com **Vite** e **TailwindCSS**. O design system (tokens, componentes) está em `DESIGN_SYSTEM.md`; o inventário de telas em `TELAS.md`; os fluxos de UX em `UX.md`.

## 2. Princípios Arquiteturais

1. **Arquitetura por features:** o código é organizado por domínio funcional (autenticação, dashboards, importação, cadastros), não por tipo técnico de arquivo.
2. **Componentização via Design System:** nenhum componente visual é criado fora do conjunto documentado em `DESIGN_SYSTEM.md` sem justificativa registrada no Pull Request correspondente.
3. **Camada de serviço centralizada:** toda chamada HTTP à API (`API.md`) passa exclusivamente por `src/services/`, nunca diretamente em componentes de página.
4. **Tipagem:** o projeto utiliza **JSDoc tipado** com checagem via `// @ts-check` e `jsconfig.json` (premissa adotada para manter a stack estritamente como especificada — React puro via Vite, sem introdução de TypeScript como dependência adicional não listada em `README.md`). Toda função exportada de `services/`, `hooks/` e `utils/` possui anotação JSDoc de parâmetros e retorno.
5. **Estado remoto:** dados vindos da API são geridos via camada de *data fetching* própria (`src/services/httpClient.js` + hooks customizados de `src/hooks/`), com cache simples em memória por chave de requisição, sem introdução de biblioteca de estado global adicional não listada na stack obrigatória.
6. **Estado local:** estado de UI (filtros selecionados, abas ativas, modais) é gerido via `useState`/`useReducer` nativos do React, escopados ao componente ou contexto de página.

## 3. Estrutura de Diretórios

```
frontend/
├── src/
│   ├── main.jsx                      # ponto de entrada, montagem do React root
│   ├── App.jsx                       # definição de rotas (React Router)
│   ├── components/
│   │   ├── ui/                       # componentes base do design system (Button, Card, Table, ...)
│   │   ├── layout/                   # Shell, Sidebar, Topbar, PageHeader
│   │   ├── charts/                   # wrappers Chart.js (LineChart, BarChart, DoughnutChart, ...)
│   │   └── filtros/                  # FiltroAno, FiltroUF, FiltroPromotor, BarraDeFiltros, ...
│   ├── pages/
│   │   ├── login/
│   │   ├── dashboard-executivo/
│   │   ├── dashboard-promotor/
│   │   ├── importacao/
│   │   │   ├── nova-importacao/
│   │   │   └── historico/
│   │   ├── cadastros/
│   │   │   ├── usuarios/
│   │   │   ├── clientes/
│   │   │   └── promotores/
│   │   └── auditoria/
│   ├── services/
│   │   ├── httpClient.js             # wrapper fetch com injeção de token e tratamento de erro (API.md, seção 13)
│   │   ├── authService.js
│   │   ├── dashboardService.js
│   │   ├── kpiService.js
│   │   ├── importacaoService.js
│   │   ├── cadastrosService.js
│   │   ├── auditoriaService.js
│   │   └── exportacaoService.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useFiltrosDashboard.js
│   │   ├── usePaginacao.js
│   │   └── useExportacao.js
│   ├── context/
│   │   └── AuthContext.jsx           # sessão autenticada, perfil, permissões derivadas
│   ├── routes/
│   │   ├── RotaPrivada.jsx           # guarda de rota por autenticação
│   │   └── RotaPorPerfil.jsx         # guarda de rota por perfil (PERMISSOES.md)
│   ├── utils/
│   │   ├── formatadores.js           # moeda BRL, datas, percentuais
│   │   └── validadores.js
│   └── styles/
│       └── index.css                 # diretivas Tailwind + tokens customizados
├── public/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

## 4. Roteamento

1. Biblioteca: **React Router** (`react-router-dom`), configurada em `App.jsx`.
2. Rotas privadas são envolvidas por `RotaPrivada`, que redireciona para `/login` caso não haja sessão válida (`AuthContext`).
3. Rotas restritas por perfil são adicionalmente envolvidas por `RotaPorPerfil`, que consulta `PERMISSOES.md` (replicado como constante `src/constants/permissoes.js`) e redireciona para uma página de "Acesso Negado" caso o perfil do usuário autenticado não tenha acesso.

| Rota | Página | Perfil mínimo |
|---|---|---|
| `/login` | Login | Público |
| `/` | Redireciona conforme perfil (Diretoria/Administrador → Dashboard Executivo; Supervisor/Promotor → Dashboard por Promotor) | Autenticado |
| `/dashboard/executivo` | Dashboard Executivo | Diretoria |
| `/dashboard/promotor/:id` | Dashboard por Promotor | Promotor/Supervisor/Diretoria/Administrador |
| `/importacao/nova` | Nova Importação | Administrador |
| `/importacao/historico` | Histórico de Importações | Administrador |
| `/cadastros/usuarios` | Gestão de Usuários | Administrador |
| `/cadastros/clientes` | Gestão de Clientes | Supervisor (leitura) / Administrador |
| `/cadastros/promotores` | Gestão de Promotores | Administrador |
| `/auditoria` | Log de Auditoria | Administrador |
| `/acesso-negado` | Página de acesso negado | Autenticado |

## 5. Sessão e Autenticação no Frontend

1. `access_token` e `refresh_token` (`AUTENTICACAO.md`) são armazenados em `localStorage`, sob as chaves `pbi_access_token` e `pbi_refresh_token`.
2. `httpClient.js` injeta automaticamente o `access_token` no header `Authorization` de toda requisição.
3. Em caso de resposta `401` com código `TOKEN_INVALIDO`, `httpClient.js` tenta automaticamente uma renovação via `POST /api/v1/auth/refresh`; se a renovação falhar, a sessão é encerrada localmente e o usuário é redirecionado a `/login`.
4. `AuthContext` expõe `{ usuario, perfil, autenticado, login(), logout() }` para toda a árvore de componentes.

## 6. Consumo da API

1. Toda função de `src/services/*.js` retorna diretamente o corpo já desserializado (`JSON.parse`) da resposta, ou lança uma exceção tipada (`ApiError`) contendo `codigo` e `mensagem` conforme o formato de erro padrão de `API.md`, seção 13.
2. Componentes de página tratam o estado de carregamento (`loading`), sucesso (`data`) e erro (`error`) de forma consistente via os hooks de `src/hooks/`.
3. Parâmetros de filtro (`DASHBOARD.md`) são sempre serializados como query string pela camada de serviço, nunca montados manualmente em componentes.

## 7. Gráficos (Chart.js)

1. Todo gráfico é implementado através de um componente wrapper em `src/components/charts/`, que encapsula a configuração padrão de cores, fontes e responsividade do design system (`DESIGN_SYSTEM.md`), recebendo apenas dados e um conjunto mínimo de props específicas do gráfico.
2. Nenhuma página instancia `Chart.js` diretamente — sempre através dos wrappers, garantindo consistência visual entre todos os dashboards (`GRAFICOS.md` detalha os tipos de gráfico utilizados por KPI).

## 8. Exportação no Frontend

1. Toda tela com exportação disponível oferece um menu com as opções Excel, CSV e PDF, que disparam `GET` aos endpoints de `API.md`, seção 12, com os filtros correntes da tela serializados na query string.
2. O download é tratado via `Blob` retornado pela API, com nome de arquivo sugerido no header `Content-Disposition` da resposta.

## 9. Tratamento de Erros e Estados Vazios

1. Todo componente de listagem/dashboard trata explicitamente três estados: carregando, vazio (sem dados para os filtros aplicados) e erro (falha de comunicação com a API), conforme padrões visuais definidos em `DESIGN_SYSTEM.md` e `UX.md`.
2. Erros de permissão (`403`) redirecionam para `/acesso-negado`; erros de dados não encontrados (`404`) exibem mensagem contextual sem redirecionamento.

## 10. Build e Ambiente

1. Variáveis de ambiente do frontend (`VITE_API_BASE_URL`) são lidas via `import.meta.env`, definidas em `.env` (desenvolvimento) e `.env.production` (build de produção), nunca hardcoded no código-fonte.
2. O build de produção (`vite build`) gera artefatos estáticos em `frontend/dist/`, servidos conforme `DEPLOY.md`.
