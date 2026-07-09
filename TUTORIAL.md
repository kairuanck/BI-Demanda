# TUTORIAL.md — Tutorial Operacional Completo

## 1. Finalidade

Este documento é o guia operacional passo a passo do projeto Promotores BI, cobrindo desde a criação do repositório até a evolução da POC para um produto SaaS. Ele pressupõe que toda a documentação de especificação (`SPEC_INDEX.md`) já foi produzida e está disponível. Sempre que um passo referenciar uma regra de negócio ou arquitetural, o documento correspondente é citado — este tutorial não repete a especificação, apenas orienta a execução.

Neste projeto específico, o repositório `kairuanck/Pedidos-redes` já existe e a documentação já está publicada na branch `claude/promotores-bi-docs-ieimki`. As seções 1 a 3 abaixo descrevem o processo completo do zero, útil tanto como registro do que já foi feito quanto como referência caso um novo repositório precise ser criado no futuro (ex.: no início da jornada SaaS, seção 14).

## 2. Como Criar o Repositório GitHub

1. Acesse [github.com](https://github.com) autenticado com a conta que será a proprietária do projeto.
2. Clique em "New repository".
3. Preencha:
   - **Repository name:** `promotores-bi` (ou o nome equivalente já em uso, como `Pedidos-redes`, se o repositório for reaproveitado).
   - **Visibility:** Privado, recomendado para a fase de POC (a documentação e o código ainda não são destinados à publicação aberta).
   - **Initialize with:** um `README.md` mínimo (será substituído pelo `README.md` completo desta documentação) e um `.gitignore` para Python (será substituído pelo `.gitignore` definido em `GITHUB.md`, seção 8).
4. Clique em "Create repository".
5. Configure a proteção da branch `main` (Settings → Branches → Add rule), conforme `GITHUB.md`, seção 7: exigir Pull Request, exigir status de CI aprovado, exigir branch atualizada antes da mesclagem.
6. Clone o repositório localmente:
   ```bash
   git clone https://github.com/<sua-organizacao>/promotores-bi.git
   cd promotores-bi
   ```

## 3. Estrutura Correta de Pastas

1. Na raiz do repositório, mantenha todos os documentos `.md` de especificação (`README.md` até `SPEC_INDEX.md`, mais `TUTORIAL.md`), conforme entregues nesta documentação — a raiz é o local correto, pois o Claude Code lê a documentação a partir do diretório de trabalho do repositório sem necessidade de navegação adicional.
2. As pastas `backend/` e `frontend/` são criadas **durante a execução da Sprint 00** (`SPRINT_00.md`), não antes — não crie manualmente a estrutura de código antes de disparar a Sprint 00 ao Claude Code, para evitar divergência entre o que existe no repositório e o que a Sprint 00 espera encontrar (repositório limpo, apenas com a documentação).
3. Estrutura da raiz do repositório ao final da fase de documentação (antes da Sprint 00):
   ```
   promotores-bi/
   ├── README.md
   ├── PROJECT.md
   ├── MASTER_PROMPT.md
   ├── ROADMAP.md
   ├── PROMPTS.md
   ├── DATABASE.md
   ├── MODELAGEM.md
   ├── DER.md
   ├── DICIONARIO_DE_DADOS.md
   ├── REGRAS_DE_NEGOCIO.md
   ├── ETL.md
   ├── IMPORTADOR.md
   ├── VALIDADOR.md
   ├── HASH.md
   ├── LOGS.md
   ├── BACKEND.md
   ├── API.md
   ├── AUTENTICACAO.md
   ├── PERMISSOES.md
   ├── FRONTEND.md
   ├── DESIGN_SYSTEM.md
   ├── TELAS.md
   ├── UX.md
   ├── DASHBOARD.md
   ├── KPIS.md
   ├── GRAFICOS.md
   ├── TESTES.md
   ├── AUDITORIA.md
   ├── DEPLOY.md
   ├── GITHUB.md
   ├── SPRINT_00.md ... SPRINT_12.md
   ├── SPEC_INDEX.md
   ├── TUTORIAL.md
   └── .gitignore
   ```
4. A partir da Sprint 00, a estrutura evolui para incluir `backend/` e `frontend/` exatamente conforme `BACKEND.md`, seção 4, e `FRONTEND.md`, seção 3.

## 4. Como Enviar Toda a Documentação

1. Copie (ou gere, se estiver reproduzindo este processo em um novo repositório) todos os 45 arquivos `.md` listados na seção 3 para a raiz do repositório clonado.
2. Adicione e commite:
   ```bash
   git checkout -b claude/promotores-bi-docs-ieimki
   git add *.md .gitattributes
   git commit -m "docs: adiciona documentação completa do projeto Promotores BI"
   git push -u origin claude/promotores-bi-docs-ieimki
   ```
3. Abra um Pull Request desta branch para `main`, revise o conteúdo (mesmo sendo apenas documentação, a revisão garante que nenhum arquivo ficou incompleto) e mescle.
4. A partir deste ponto, `main` contém toda a especificação do projeto, pronta para o início da implementação.

## 5. Como Instalar o Claude Code

1. Pré-requisito: Node.js 18 ou superior instalado.
2. Instale o Claude Code globalmente:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. Verifique a instalação:
   ```bash
   claude --version
   ```
4. Autentique-se conforme o método disponível para sua conta (assinatura Claude ou chave de API Anthropic), seguindo o fluxo interativo apresentado no primeiro uso do comando `claude`.
5. Alternativamente, o Claude Code também está disponível como extensão de IDE (VS Code, JetBrains) e como ambiente web (Claude Code on the web, `claude.ai/code`) — qualquer uma dessas formas de acesso é compatível com este tutorial, desde que tenha acesso de leitura/escrita ao repositório do projeto.

## 6. Como Conectar ao GitHub

1. Dentro do diretório do repositório clonado localmente, inicie o Claude Code:
   ```bash
   cd promotores-bi
   claude
   ```
2. Caso esteja utilizando o Claude Code on the web, conecte a conta GitHub à sessão através do fluxo de "Add repository" da interface web, selecionando o repositório `promotores-bi` (ou `kairuanck/Pedidos-redes`, no caso deste projeto).
3. Confirme que o Claude Code tem acesso de leitura ao histórico e de escrita (commit/push) à branch de trabalho, conforme as permissões configuradas na sessão.
4. Valide o acesso pedindo ao Claude Code para listar os arquivos `.md` da raiz do repositório — a resposta deve corresponder exatamente à lista de `SPEC_INDEX.md`, seção 2.

## 7. Como Executar a Sprint 0

1. Garanta que a branch corrente está atualizada com `main` (pós-mesclagem da documentação).
2. Crie a branch de trabalho da Sprint:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b sprint/00-fundacao-do-projeto
   ```
3. No Claude Code, cole o **Prompt de Inicialização de Sessão** (`PROMPTS.md`, seção 2) e aguarde a confirmação de leitura.
4. Em seguida, cole o **Prompt — Sprint 00** (`PROMPTS.md`, seção 3).
5. Acompanhe a execução: o Claude Code deve criar a estrutura de `backend/` e `frontend/`, o esqueleto FastAPI e Vite/React, o `.gitignore`, o template de Pull Request e o workflow de CI, conforme `SPRINT_00.md`.
6. Ao final, peça ao Claude Code para validar localmente os critérios de aceite (`SPRINT_00.md`, seção 7) — subir o backend, subir o frontend, rodar lint/mypy.
7. Revise as alterações (`git diff`, `git status`), commit conforme `GITHUB.md`, seção 3, e abra o Pull Request usando o template (`GITHUB.md`, seção 4).

## 8. Como Executar a Sprint 1

1. Após a mesclagem do Pull Request da Sprint 00 em `main`, atualize e crie a nova branch:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b sprint/01-modelagem-de-dados-e-migrations
   ```
2. No Claude Code, cole o **Prompt — Sprint 01** (`PROMPTS.md`, seção 4).
3. Acompanhe a execução: modelos SQLAlchemy das 19 tabelas, migração Alembic inicial, seed de UFs, repositórios básicos, conforme `SPRINT_01.md`.
4. Valide localmente: `alembic upgrade head` a partir de um banco vazio deve criar exatamente as 19 tabelas (`DICIONARIO_DE_DADOS.md`).
5. Execute a suíte de testes (seção 9 deste tutorial) antes de abrir o Pull Request.
6. Repita este mesmo padrão (atualizar `main`, nova branch `sprint/NN-*`, colar o prompt correspondente de `PROMPTS.md`, validar critérios de aceite de `SPRINT_NN.md`, testar, commitar, abrir PR) para todas as Sprints seguintes, de 02 a 12, respeitando a ordem de dependência de `ROADMAP.md`, seção 2.

## 9. Como Revisar Pull Requests

1. Ao abrir um Pull Request de Sprint, verifique automaticamente:
   - O pipeline de CI (`GITHUB.md`, seção 6) está com status verde.
   - O template de PR (`GITHUB.md`, seção 4) está preenchido, com o checklist de Definition of Done marcado.
2. Revise manualmente:
   - Se os arquivos alterados correspondem ao escopo da Sprint (`SPRINT_NN.md`, seção 4) — nenhuma alteração fora de escopo deve estar presente sem justificativa.
   - Se os "Critérios de Aceite" (`SPRINT_NN.md`, seção 7) estão de fato demonstrados (testes correspondentes existem e passam).
   - Se a documentação de especificação foi respeitada literalmente (nomes de tabelas, endpoints, regras) — divergências não documentadas indicam desvio a ser corrigido antes da mesclagem.
3. Utilize comentários de revisão diretamente no Pull Request para apontar ajustes; solicite ao Claude Code que aplique as correções na mesma branch antes de nova revisão.
4. Após aprovação, mescle utilizando **squash and merge** (`GITHUB.md`, seção 5, item 3).
5. Após a mesclagem, delete a branch de Sprint (mantendo o repositório limpo) e prossiga para a Sprint seguinte (seção 8 deste tutorial).

## 10. Como Validar os Testes

1. **Backend:**
   ```bash
   cd backend
   pytest --cov=app --cov-report=term-missing
   ```
   Compare o percentual de cobertura reportado com a meta da Sprint corrente (`TESTES.md`, seção 7).
2. **Backend — qualidade de código:**
   ```bash
   ruff check .
   black --check .
   mypy .
   ```
3. **Frontend (a partir da Sprint 09):**
   ```bash
   cd frontend
   npm run lint
   npm run test -- --coverage
   ```
4. **Migrações (a partir da Sprint 01):**
   ```bash
   cd backend
   alembic downgrade base
   alembic upgrade head
   ```
   Deve executar sem erros, validando reversibilidade e reprodutibilidade do schema.
5. Nenhum Pull Request deve ser mesclado com qualquer um dos comandos acima retornando erro ou cobertura abaixo da meta da Sprint (`GITHUB.md`, seção 9; `TESTES.md`, seção 9).

## 11. Como Importar os Arquivos Excel

Aplicável a partir da conclusão da Sprint 07 (todos os 5 importadores disponíveis) e da Sprint 11 (interface de importação no frontend). Antes da Sprint 11, a importação pode ser validada via `POST /api/v1/importacoes` diretamente pelo Swagger UI (`http://localhost:8000/docs`).

1. Prepare os arquivos `.xlsx` de origem seguindo exatamente o layout de colunas de `IMPORTADOR.md`, para cada tipo: Base de Clientes (seção 3.1), Carteira dos Promotores (seção 4.1), Faturamento Mensal (seção 5.1), Checklists (seção 6.1), Visitas (seção 7.1).
2. Respeite a ordem de dependência de primeira carga (`IMPORTADOR.md`, seção 8): Clientes → Carteira → Faturamento → Visitas → Checklist.
3. Acesse a tela "Nova Importação" (`TELAS.md`, seção 5) autenticado como Administrador, ou utilize o Swagger UI:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/importacoes" \
     -H "Authorization: Bearer <access_token>" \
     -F "tipo_arquivo=CLIENTES" \
     -F "arquivo=@base_de_clientes.xlsx"
   ```
4. Repita para os demais tipos de arquivo, na ordem da etapa 2.
5. Após cada importação, consulte o resultado (seção 12 deste tutorial) antes de prosseguir para o próximo tipo de arquivo, especialmente na primeira carga de um ambiente novo.

## 12. Como Validar a Importação

1. Acesse a tela "Detalhe de Importação" (`TELAS.md`, seção 7) ou consulte via API:
   ```bash
   curl -H "Authorization: Bearer <access_token>" \
     "http://localhost:8000/api/v1/importacoes/<id>"
   ```
2. Verifique `status`: `CONCLUIDA` (sem erros) ou `CONCLUIDA_COM_ERROS` (algumas linhas rejeitadas — aceitável, dependendo da origem dos dados).
3. Se `CONCLUIDA_COM_ERROS`, consulte `GET /api/v1/importacoes/{id}/erros` e corrija a planilha de origem conforme os códigos de `VALIDADOR.md`, reimportando em seguida (nova versão será criada automaticamente, `HASH.md`).
4. Verifique os contadores `total_linhas`, `linhas_validas`, `linhas_invalidas` batem com a expectativa da planilha enviada.
5. Para importações de Carteira: confira, em `GET /api/v1/carteiras`, que os vínculos vigentes refletem corretamente o arquivo importado (`REGRAS_DE_NEGOCIO.md`, seção 5.2).
6. Para importações de Faturamento/Visitas/Checklist: confira, no Dashboard Executivo, que os KPIs correspondentes (`KPIS.md`) refletem os novos dados após a importação.
7. Consulte a tela de Auditoria (`TELAS.md`, seção 12) para confirmar o registro do evento `IMPORTACAO` correspondente.

## 13. Como Publicar a POC

Siga o checklist completo de `DEPLOY.md`, seção 13, executando, em ordem:
1. Provisionar o ambiente de hospedagem escolhido para backend (contêiner) e frontend (hosting estático), conforme `DEPLOY.md`, seção 8.
2. Configurar as variáveis de ambiente de produção (`DEPLOY.md`, seções 3–4), incluindo `JWT_SECRET_KEY`/`JWT_REFRESH_SECRET_KEY` gerados especificamente para produção (nunca reaproveitando os de desenvolvimento).
3. Aplicar as migrações (`alembic upgrade head`) contra o banco de produção.
4. Executar os seeds de UF e usuário Administrador (`SPRINT_01.md`, `SPRINT_02.md`).
5. Publicar o build do frontend (`npm run build`) apontando `VITE_API_BASE_URL` para a URL pública do backend.
6. Validar `GET /api/v1/health` publicamente.
7. Realizar login manual com o usuário Administrador de seed e executar uma importação de teste de ponta a ponta.
8. Comunicar a URL de acesso aos usuários de demonstração (Diretoria, Supervisores, Promotores de teste), com credenciais individuais criadas via tela de Gestão de Usuários.

## 14. Como Evoluir Posteriormente para PostgreSQL

Siga `DEPLOY.md`, seção 9:
1. Provisionar uma instância PostgreSQL 14+.
2. Definir `DATABASE_URL=postgresql+psycopg://usuario:senha@host:porta/banco` no ambiente de destino.
3. Executar `alembic upgrade head` contra o novo banco — nenhuma migração precisa ser reescrita, por força das regras de compatibilidade de `DATABASE.md`, seção 3.
4. Caso já exista dados em SQLite a preservar, exportar tabela a tabela (via Pandas ou `pgloader`) e importar no PostgreSQL, respeitando a ordem de dependência de chaves estrangeiras (`DICIONARIO_DE_DADOS.md`): dimensões antes de fatos, fatos antes de auditoria.
5. Atualizar a variável `DATABASE_URL` do ambiente de produção e reiniciar a aplicação — nenhuma alteração de código é necessária.
6. Validar novamente o checklist da seção 13 deste tutorial contra o novo banco.

## 15. Como Transformar a POC em um SaaS

Este é um roteiro estratégico de evolução, consistente com as decisões arquiteturais já tomadas nesta documentação (que deliberadamente evitam decisões que dificultem este caminho), mas cuja implementação está fora do escopo das Sprints 00–12:

1. **Multi-tenancy:** introduzir um campo `tenant_id` (inteiro, `FK` para uma nova tabela `tenants`) em todas as tabelas de cadastro e fato (`DICIONARIO_DE_DADOS.md`), com migração Alembic aditiva. Todo `repository` passa a filtrar implicitamente por `tenant_id` do usuário autenticado (extensão direta do mecanismo de escopo já existente em `PERMISSOES.md`, seção 5, item 2), minimizando o retrabalho de camada de serviço.
2. **Identificação de tenant:** decidir entre subdomínio por cliente (`clienteX.promotoresbi.com`) ou seleção de organização pós-login; ambas as opções são compatíveis com o `AuthContext` já existente (`FRONTEND.md`, seção 5), bastando adicionar o `tenant_id` como claim adicional do JWT (`AUTENTICACAO.md`, seção 3.1).
3. **Billing e planos:** introduzir um módulo de assinatura (integração com um provedor de pagamento recorrente), gating de funcionalidades por plano contratado, e uma tela de gestão de assinatura para o perfil Administrador da organização contratante.
4. **Onboarding self-service:** criar um fluxo de cadastro de nova organização (tenant) e usuário Administrador inicial sem intervenção manual, substituindo o seed manual usado na POC (`AUTENTICACAO.md`, seção 11).
5. **Migração de banco:** este é o momento em que a migração de PostgreSQL (seção 14) deixa de ser opcional e passa a ser pré-requisito, dada a necessidade de suportar múltiplos tenants com volume de produção real.
6. **Importação automatizada:** avaliar a substituição gradual da importação manual de planilhas (`ETL.md`) por integrações diretas com ERPs dos clientes contratantes (API/EDI), mantendo o importador manual como via alternativa sempre disponível — a arquitetura de `ImportadorArquivo` (`BACKEND.md`, seção 3, item 2) já foi desenhada para admitir novas origens de dados sem alterar o motor genérico.
7. **Observabilidade de produção:** introduzir ferramenta de observabilidade externa (métricas, tracing, alertas), evoluindo a base de logging técnico já estruturada em JSON Lines (`LOGS.md`).
8. **Conformidade e retenção de dados:** revisar a política de retenção de `logs_auditoria` (`AUDITORIA.md`, seção 8) por tenant, conforme exigência contratual/regulatória de cada cliente.
9. **Internacionalização:** caso o produto seja comercializado fora do Brasil, revisar a premissa de idioma único (`PROJECT.md`, seção 9, item 1) e introduzir i18n na camada de frontend.

Cada um destes itens deve, quando priorizado, gerar sua própria documentação de especificação (seguindo o mesmo padrão desta documentação) antes da implementação, preservando a prática de "documentação completa antes do código" adotada desde a origem deste projeto.

## 16. Resumo do Ciclo Operacional Completo

```
Criar repositório (seção 2)
        │
        ▼
Enviar documentação (seções 3-4)
        │
        ▼
Instalar e conectar Claude Code (seções 5-6)
        │
        ▼
Executar Sprints 00 → 12, uma a uma (seções 7-9), com testes (seção 10) a cada Sprint
        │
        ▼
Importar e validar dados de demonstração (seções 11-12)
        │
        ▼
Publicar a POC (seção 13)
        │
        ▼
Evoluir para PostgreSQL quando necessário (seção 14)
        │
        ▼
Evoluir para SaaS multi-tenant (seção 15)
```
