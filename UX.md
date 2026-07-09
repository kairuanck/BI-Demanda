# UX.md — Fluxos de Experiência do Usuário

## 1. Finalidade

Este documento descreve os fluxos de navegação e interação (jornadas de usuário) do Promotores BI, complementando o inventário de telas (`TELAS.md`) e o design system (`DESIGN_SYSTEM.md`) com a sequência de passos que cada persona percorre para realizar suas tarefas principais.

## 2. Fluxo — Autenticação

```
[Login] --credenciais válidas--> [Redirecionamento por perfil]
   │
   ├─ ADMINISTRADOR / DIRETORIA → Dashboard Executivo
   └─ SUPERVISOR / PROMOTOR      → Dashboard por Promotor
[Login] --credenciais inválidas--> [Toast de erro] --> permanece em [Login]
[Qualquer tela] --sessão expirada (refresh falhou)--> [Login]
```

Detalhamento técnico em `AUTENTICACAO.md`, seção 4; regras de redirecionamento em `FRONTEND.md`, seção 4.

## 3. Fluxo — Administrador Realiza uma Importação

```
[Login] → [Sidebar: Importação] → [Nova Importação]
   → seleciona Tipo de Arquivo
   → seleciona/arrasta o arquivo .xlsx
   → confirma envio
   → [estado de carregamento]
   ├─ sucesso sem erros de linha        → [Detalhe de Importação: status CONCLUIDA]
   ├─ sucesso com linhas rejeitadas     → [Detalhe de Importação: status CONCLUIDA_COM_ERROS, aba Erros destacada]
   └─ arquivo duplicado / falha total   → [Toast de erro] → permanece em [Nova Importação]
```

Regras de negócio subjacentes: `ETL.md`, `VALIDADOR.md`, `HASH.md`, `REGRAS_DE_NEGOCIO.md`.

## 4. Fluxo — Administrador Reverte uma Importação

```
[Histórico de Importações] → seleciona uma importação → [Detalhe de Importação]
   → clica em "Reverter Importação"
   → [Modal de confirmação: exige justificativa textual]
   ├─ condições de rollback atendidas    → confirma → [importação marcada REVERTIDA] → [Toast de sucesso]
   └─ condições não atendidas (botão desabilitado) → [tooltip explicando o motivo: existe versão posterior concluída]
```

Regras de elegibilidade ao rollback: `REGRAS_DE_NEGOCIO.md`, seção 6.

## 5. Fluxo — Diretoria Analisa o Dashboard Executivo

```
[Login] → [Dashboard Executivo] (filtros padrão: Ano corrente, todos os meses, todas as regiões)
   → ajusta filtros (Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor)
   → [dashboard recarrega todos os blocos]
   → clica em um KpiCard (ex.: Cobertura)
   → [expande detalhamento por Supervisor/Promotor daquele KPI]
   → clica em "Exportar" → seleciona formato (Excel/CSV/PDF)
   → [download do arquivo refletindo os filtros correntes]
```

## 6. Fluxo — Promotor Consulta o Próprio Desempenho

```
[Login] → [Dashboard por Promotor (próprio, automático)]
   → aba "Visão Geral": KPIs de Cobertura, Positivação, Visitas, Checklist
   → aba "Carteira": lista de clientes, indicador de positivação e última visita de cada um
   → aba "Visitas": histórico de visitas realizadas no período filtrado
   → aba "Checklists": conformidade por checklist respondido
   → aba "Ranking": posição própria no ranking geral e por Tipo de Promotor
```

O Promotor não possui `BarraDeFiltros` com seleção de outro promotor — apenas Ano e Mês são ajustáveis (`TELAS.md`, seção 4; `PERMISSOES.md`, seção 4.3).

## 7. Fluxo — Supervisor Acompanha a Equipe

```
[Login] → [Dashboard por Promotor] (tela inicial de listagem da equipe, com seletor de promotor)
   → seleciona um promotor da própria equipe
   → [Dashboard por Promotor daquele promotor, mesma estrutura do fluxo da seção 6]
   → botão "Voltar à Equipe" retorna à listagem
```

Tentativa de acessar diretamente a URL de um promotor fora da própria equipe resulta no fluxo da seção 9 (Acesso Negado).

## 8. Fluxo — Administrador Gerencia Usuários

```
[Sidebar: Cadastros → Usuários] → [Gestão de Usuários]
   → clica em "Novo Usuário"
   → [Modal: preenche Nome, E-mail, Perfil]
   → se Perfil = PROMOTOR ou SUPERVISOR → [campo adicional: seleciona o registro de Promotor/Supervisor a vincular]
   → confirma criação
   → [Toast de sucesso] → usuário aparece na listagem
```

Fluxo de redefinição de senha e inativação seguem o mesmo padrão de modal de confirmação, descritos em `TELAS.md`, seção 8.

## 9. Fluxo — Tentativa de Acesso Não Autorizado

```
[Usuário autenticado navega para rota fora de seu perfil/escopo]
   → [RotaPorPerfil detecta violação] → redireciona para [Acesso Negado]
   → backend, em paralelo, retorna 403 para qualquer chamada de API subjacente
   → evento registrado em logs_auditoria (PERMISSOES.md, seção 5, item 3)
```

## 10. Princípios de Feedback ao Usuário

1. Toda ação assíncrona (upload, exportação, rollback, salvamento de formulário) exibe estado de carregamento explícito (`DESIGN_SYSTEM.md`, seção 10) — nunca uma tela "congelada" sem indicação visual.
2. Toda ação concluída com sucesso exibe `Toast` de confirmação; toda ação que falha exibe `Toast` ou `ErrorState` com mensagem acionável (nunca apenas um código de erro técnico).
3. Ações destrutivas ou de grande impacto (rollback de importação, inativação de usuário) sempre exigem confirmação explícita via `Modal`, nunca são executadas em um único clique.
4. Filtros aplicados em qualquer tela permanecem visíveis e editáveis a qualquer momento, nunca escondidos após a primeira consulta.

## 11. Consistência de Navegação

1. A `Sidebar` é sempre visível em telas autenticadas, com o item de menu correspondente à tela atual destacado.
2. O `Breadcrumb` reflete a hierarquia de navegação em todas as telas com mais de um nível (ex.: Cadastros → Clientes → Detalhe do Cliente).
3. Toda listagem paginada mantém os filtros e a página corrente ao navegar para o detalhe de um item e retornar (estado preservado via query string da URL).
