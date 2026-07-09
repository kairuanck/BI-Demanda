# SPRINT_11.md — Importação (Frontend), Exportações e Auditoria UI

## 1. Objetivo

Implementar as telas operacionais restantes do frontend: upload de planilhas por tipo de arquivo, histórico de importações com rollback, exportação em Excel/CSV/PDF e a tela de log de auditoria, além das telas de gestão de cadastros (Usuários, Clientes, Promotores).

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `TELAS.md` (seções 5–13), `UX.md` (seções 3, 4, 8), `AUDITORIA.md`, `API.md` (seções 5–9, 11, 12).

## 3. Pré-condições

Sprint 03 a 07 concluídas (backend de importação completo). Sprint 09 e 10 concluídas (design system e dashboards disponíveis).

## 4. Escopo (Backlog Detalhado)

### 4.1 Importação
1. Implementar `pages/importacao/nova-importacao/` (`TELAS.md`, seção 5), incluindo `FileUpload`, seleção de Tipo de Arquivo e feedback de resultado (`UX.md`, seção 3).
2. Implementar `pages/importacao/historico/` (`TELAS.md`, seção 6), com listagem, filtros e visualização de cadeia de versões.
3. Implementar a tela de Detalhe de Importação (`TELAS.md`, seção 7), incluindo a aba de Erros de Validação paginada e o fluxo de rollback com justificativa obrigatória (`UX.md`, seção 4).
4. Implementar `src/services/importacaoService.js`.

### 4.2 Exportação
1. Implementar `src/services/exportacaoService.js` e `src/hooks/useExportacao.js`, tratando o download via `Blob` (`FRONTEND.md`, seção 8).
2. Implementar o menu de exportação padronizado (`DESIGN_SYSTEM.md`, seção 6, `TELAS.md`, seção 16) e integrá-lo às telas de Dashboard Executivo, Dashboard por Promotor, Gestão de Clientes e Gestão de Promotores (ativando a funcionalidade cujos botões já existiam visualmente desde a Sprint 10).

### 4.3 Auditoria
1. Implementar `pages/auditoria/` (`TELAS.md`, seção 12), com filtros, listagem paginada e modal de detalhe com formatação de `dados_antes`/`dados_depois` (`AUDITORIA.md`, seção 7).
2. Implementar `src/services/auditoriaService.js`.

### 4.4 Cadastros
1. Implementar `pages/cadastros/usuarios/` (`TELAS.md`, seção 8), incluindo o formulário modal de criação/edição com vínculo condicional a Promotor/Supervisor.
2. Implementar `pages/cadastros/clientes/` e a tela de Detalhe de Cliente (`TELAS.md`, seções 9–10).
3. Implementar `pages/cadastros/promotores/` (`TELAS.md`, seção 11).
4. Implementar `src/services/cadastrosService.js`.

## 5. Fora de Escopo desta Sprint

1. Tela completa de administração de templates de Checklist (perguntas) — a Sprint 07 entrega apenas os endpoints mínimos; a interface visual completa é item de evolução pós-POC, não bloqueando a demonstração da POC via importação de planilha de respostas.

## 6. Entregáveis

1. Fluxo de importação completo no frontend, incluindo rollback.
2. Exportação Excel/CSV/PDF funcional em todas as telas aplicáveis.
3. Tela de Auditoria funcional.
4. Telas de Gestão de Usuários, Clientes e Promotores funcionais.

## 7. Critérios de Aceite

1. Upload de um arquivo `.xlsx` via `FileUpload` completa o fluxo e exibe o resultado (sucesso/erros) sem necessidade de recarregar a página manualmente.
2. Histórico de Importações exibe corretamente a cadeia de versões de um mesmo `tipo_arquivo`, com indicação visual da versão corrente.
3. Rollback de uma importação elegível funciona de ponta a ponta a partir da interface, exigindo justificativa antes de confirmar.
4. Exportação em Excel, CSV e PDF do Dashboard Executivo gera arquivos com os dados refletindo exatamente os filtros correntes da tela.
5. Tela de Auditoria permite localizar, filtrar e visualizar em detalhe qualquer evento gerado pelas Sprints anteriores (login, importação, rollback, alteração de usuário).
6. Criação de um novo usuário com `perfil = PROMOTOR` exige e valida a seleção de um registro de Promotor existente antes de permitir o envio do formulário.
7. Meta de cobertura de testes de frontend da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. Esta Sprint conclui o marco M4 do `ROADMAP.md` — a experiência completa do produto (leitura e operação) está pronta ao final dela, restando à Sprint 12 a consolidação de qualidade, auditoria final e publicação.
