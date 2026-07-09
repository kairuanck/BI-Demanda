# PROJECT.md — Visão de Produto e Escopo

## 1. Identificação do Projeto

- **Nome do produto:** Promotores BI
- **Tipo:** Plataforma web de Business Intelligence (POC evolutiva para SaaS)
- **Domínio de negócio:** Mercado pet — gestão de equipes de campo (Promotores Técnicos e Promotores Trade)
- **Papel do responsável nesta documentação:** Arquiteto Técnico e Product Owner
- **Status:** Fase de documentação técnica, anterior à implementação de código

## 2. Contexto de Negócio

Empresas do mercado pet (indústrias e distribuidores de produtos veterinários e pet care) mantêm equipes de campo compostas por dois tipos de profissionais:

- **Promotor Técnico:** atua principalmente em apoio técnico-científico junto a clínicas veterinárias e pontos de venda especializados, orientando quanto ao uso correto de produtos, treinamento de equipes e suporte pós-venda.
- **Promotor Trade:** atua no ponto de venda com foco comercial — execução de trade marketing, exposição de produtos, negociação local, cobertura de carteira e geração de positivação.

Cada Promotor está vinculado a um **Supervisor** e possui uma **carteira de clientes** (pet shops, clínicas, distribuidores) sob sua responsabilidade, distribuída por **região (UF/Cidade)**. O desempenho da operação é hoje acompanhado por meio de planilhas Excel dispersas, sem versionamento, sem trilha de auditoria e sem visão consolidada em tempo hábil para a Diretoria.

## 3. Problema a Resolver

1. Ausência de repositório único e confiável dos dados de carteira, faturamento, visitas e checklists.
2. Impossibilidade de saber, de forma auditável, qual versão de cada planilha gerou quais números.
3. Risco de sobrescrita silenciosa de dados históricos ao reimportar arquivos.
4. Falta de indicadores padronizados de cobertura, positivação e ranking entre promotores.
5. Ausência de visão executiva consolidada por região, laboratório, departamento e período.
6. Falta de rastreabilidade (auditoria) de quem importou o quê e quando.

## 4. Objetivo do Produto

Entregar uma POC profissional, com arquitetura limpa e escalável, que permita:

1. Importar manualmente planilhas Excel de 5 naturezas (Base de Clientes, Carteira dos Promotores, Faturamento Mensal, Checklists, Visitas), com versionamento e trilha de auditoria completa.
2. Consultar dashboards executivos e por promotor, com KPIs de Carteira, Região, Fora da Carteira, Visitas, Checklists, Cobertura, Positivação e Ranking.
3. Filtrar toda a informação por Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor e Tipo de Promotor.
4. Exportar qualquer visão analítica em Excel, CSV e PDF.
5. Operar com controle de acesso por perfil (Administrador, Supervisor, Promotor, Diretoria).
6. Evoluir, sem reescrita, de SQLite (POC) para PostgreSQL (produção) e de aplicação single-tenant para SaaS multi-tenant.

## 5. Objetivos Explicitamente Fora de Escopo da POC

Estes itens são premissas adotadas para delimitar o escopo da POC e **não representam limitações permanentes** — são extensões previstas no `ROADMAP.md` pós-POC:

- Integração automática (API/EDI) com ERP para importação automática de faturamento. Na POC, toda importação é **manual**, via upload de planilha.
- Multi-tenancy (múltiplas empresas na mesma instalação). A POC é single-tenant; o caminho de evolução para SaaS está descrito em `TUTORIAL.md`, seção 14.
- Aplicativo mobile nativo para registro de visitas em campo. A POC recebe visitas e checklists **já digitados em planilha**, não via app de campo.
- Geolocalização em tempo real. Os campos de latitude/longitude do modelo de dados (ver `DICIONARIO_DE_DADOS.md`) existem para suportar planilhas que já tragam essa informação, mas não há captura em tempo real na POC.
- Notificações push/e-mail automatizadas. Fora do escopo da POC; mencionado como extensão futura no `ROADMAP.md`.

## 6. Personas

### 6.1 Administrador
Responsável técnico/operacional pela plataforma. Cadastra usuários, realiza importações, acompanha logs de auditoria, executa rollback de importações incorretas. Enxerga todos os dashboards e todos os filtros, sem restrição de carteira.

### 6.2 Supervisor
Gestor de uma equipe de Promotores. Acompanha o dashboard executivo restrito à sua equipe (promotores sob sua supervisão) e o dashboard individual de cada promotor supervisionado. Não realiza importações nem gerencia usuários.

### 6.3 Promotor
Profissional de campo (Técnico ou Trade). Acessa exclusivamente o próprio dashboard: própria carteira, próprias visitas, próprios checklists e a própria posição no ranking. Não enxerga dados de outros promotores.

### 6.4 Diretoria
Perfil executivo, somente leitura. Acessa o Dashboard Executivo consolidado, com todos os filtros disponíveis, sem acesso a telas operacionais (importação, cadastro de usuários, auditoria).

Matriz completa de permissões por funcionalidade em `PERMISSOES.md`.

## 7. Funcionalidades do Produto

### 7.1 Autenticação e Usuários
- Login com e-mail e senha (JWT + bcrypt).
- Cadastro, edição, ativação/inativação de usuários (Administrador).
- Vínculo de usuário Promotor a um registro de Promotor (carteira).
- Vínculo de usuário Supervisor a um registro de Supervisor (equipe).

### 7.2 Importação de Dados
- Upload manual de planilha Excel, um importador dedicado por tipo de arquivo:
  - Base de Clientes
  - Carteira dos Promotores
  - Faturamento Mensal
  - Checklists
  - Visitas
- Versionamento de cada importação (nunca sobrescreve; sempre cria nova versão vinculada à anterior).
- Detecção de duplicidade e de arquivo repetido/alterado via hash SHA256.
- Validação pré-importação com relatório de erros linha a linha.
- Histórico completo de importações, com possibilidade de rollback.
- Log de auditoria de toda operação de importação.

### 7.3 Dashboard Executivo
Visão consolidada da operação (todos os promotores, todas as regiões), com KPIs agregados e gráficos comparativos. Detalhado em `DASHBOARD.md`.

### 7.4 Dashboard por Promotor
Visão individual: carteira do promotor, cobertura, positivação, visitas realizadas x planejadas, conformidade de checklists e posição no ranking geral e por tipo de promotor. Detalhado em `DASHBOARD.md`.

### 7.5 KPIs
Carteira, Região, Fora da Carteira, Visitas, Checklists, Cobertura, Positivação, Ranking — fórmulas e regras de cálculo detalhadas em `KPIS.md`.

### 7.6 Filtros
Ano, Mês, UF, Cidade, Departamento, Laboratório, Supervisor, Vendedor, Promotor, Tipo de Promotor — comportamento detalhado em `DASHBOARD.md` e `API.md`.

### 7.7 Exportação
Excel, CSV e PDF, disponíveis em todas as telas de dashboard e listagens. Detalhado em `TELAS.md` e `API.md`.

## 8. Origem dos Dados

Todos os dados operacionais chegam à plataforma via **importação manual de planilhas Excel**, preparadas fora do sistema (extraídas de ERP, ferramentas de CRM ou controles internos). Não há, na POC, integração automática com sistemas terceiros. Cada tipo de arquivo tem estrutura, regras de validação e importador próprios, detalhados em `IMPORTADOR.md`.

## 9. Premissas Adotadas

Estas premissas foram adotadas para permitir a continuidade da documentação sem interrupção, na ausência de definição explícita, conforme instrução de condução do projeto:

1. O idioma da aplicação (telas, mensagens, exportações) é **Português do Brasil**.
2. A moeda utilizada em faturamento é o **Real (BRL)**.
3. O ano fiscal coincide com o ano civil (janeiro a dezembro).
4. Cada Promotor pertence exatamente a um Supervisor em um dado momento (histórico de mudança de supervisor é suportado via versionamento de carteira, não via tabela própria de histórico de supervisão).
5. "Fora da Carteira" refere-se a faturamento associado a clientes que, no período analisado, não possuem vínculo vigente com nenhum promotor.
6. Checklists possuem estrutura de perguntas fixas por versão de checklist (template), aplicadas em cada visita.
7. A POC é single-tenant; a arquitetura de dados e autenticação é desenhada para permitir a introdução futura de um campo `tenant_id` sem reestruturação (ver `TUTORIAL.md`, seção 14).
8. O fuso horário de referência é `America/Sao_Paulo`.

## 10. Critérios de Sucesso da POC

1. Todas as 5 planilhas de origem podem ser importadas com validação, versionamento e histórico funcionando de ponta a ponta.
2. O Dashboard Executivo e o Dashboard por Promotor exibem corretamente todos os KPIs definidos em `KPIS.md`, reagindo corretamente a todos os filtros definidos em `DASHBOARD.md`.
3. Controle de acesso por perfil funcionando conforme `PERMISSOES.md`.
4. Exportação Excel, CSV e PDF funcionando em pelo menos uma tela de dashboard e uma tela de listagem.
5. Cobertura de testes automatizados conforme metas definidas em `TESTES.md`.
6. Aplicação executável localmente com SQLite e documentadamente migrável para PostgreSQL sem alteração de modelagem (`DATABASE.md`).
7. Repositório GitHub com histórico de commits organizado por Sprint, conforme `GITHUB.md`.

## 11. Glossário

| Termo | Definição |
|---|---|
| Carteira | Conjunto de clientes vinculados a um promotor em um período de vigência. |
| Positivação | Cliente da carteira que apresentou faturamento maior que zero no período analisado. |
| Cobertura | Percentual de clientes da carteira efetivamente visitados/atendidos no período. |
| Fora da Carteira | Faturamento de clientes sem vínculo vigente com nenhum promotor no período. |
| Checklist | Formulário estruturado de verificação aplicado durante uma visita. |
| Ranking | Ordenação dos promotores por desempenho combinado de KPIs, no período e filtros selecionados. |
| Vigência | Intervalo de tempo em que um vínculo (ex.: carteira) é considerado válido. |
| Importação | Operação de carregamento de uma planilha para o sistema, versionada e auditada. |
| Rollback | Reversão de uma importação, restaurando o estado anterior à sua aplicação. |
