# EXECUCAO_LOCAL.md — Relatório de Preparação para Execução Local

## 1. Objetivo

Interromper temporariamente a evolução funcional do projeto para preparar o Promotores BI de forma que **um usuário sem conhecimento de programação** consiga colocar o sistema completo para funcionar no próprio computador, seguindo apenas um documento (`PRIMEIRO_USO.md`), sem depender de mim (Claude Code) durante a execução.

## 2. O que foi entregue

1. **Comando único para iniciar tudo**: `./iniciar.sh` (raiz do repositório) — sobe backend, frontend e banco de dados com um único comando, via Docker Compose. Verifica pré-requisitos (Docker instalado e em execução), constrói e inicia os containers em segundo plano, aguarda o backend responder e imprime uma mensagem de sucesso em português com o endereço de acesso. `./parar.sh` encerra tudo, preservando os dados.
2. **`README.md` atualizado**: seção "Como Executar Localmente" reescrita para apresentar **apenas** o caminho Docker como forma suportada de execução, com um aviso logo no topo do arquivo apontando usuários não técnicos para `PRIMEIRO_USO.md`. O caminho manual (sem Docker) foi movido para uma seção "Ambiente de desenvolvimento (contribuidores)", claramente separada — continua existindo para quem for alterar código, mas não é mais apresentado como opção ao usuário final.
3. **`PRIMEIRO_USO.md` criado**, com as sete seções pedidas (Pré-requisitos, Instalação, Como iniciar, Como acessar no navegador, Como importar os arquivos, Como visualizar o Dashboard, Como encerrar a aplicação), mais uma seção de Problemas Comuns. Linguagem sem jargão técnico, com três capturas de tela reais do sistema rodando (`docs/screenshots/`), geradas durante a própria validação deste trabalho — não são mockups.
4. **Um bug crítico corrigido**: um banco de dados novo (o cenário exato de um primeiro uso) nascia sem as 27 UFs brasileiras cadastradas, porque nenhuma migração Alembic as inseria (diferente de `tipos_promotor`, que é semeado por uma migração da Sprint 3) — o script de seed existia mas nunca era chamado fora dos testes automatizados. Isso fazia **toda importação de clientes falhar** em qualquer ambiente genuinamente novo. Corrigido rodando os dois seeds (idempotentes) automaticamente em toda inicialização, tanto no Docker (`backend/docker-entrypoint.sh`) quanto no caminho manual (`scripts/setup.sh`). Detalhes em `docs/DECISIONS.md`, seção 31.
5. **`docs/DECISIONS.md`** — seções 31 e 32 documentam o bug encontrado/corrigido e a decisão de consolidar em um único caminho de execução documentado.

## 3. Como a validação foi feita, e sua limitação

**O ambiente onde esta tarefa foi executada não tem acesso ao daemon do Docker** (é um sandbox sem `systemd` e sem privilégio para iniciar o `dockerd`) — então **não foi possível rodar `docker compose up --build` literalmente aqui**, e por isso não posso afirmar ter visto o comando `./iniciar.sh` funcionar de ponta a ponta com meus próprios olhos.

O que foi de fato validado, para compensar essa limitação:

- **`docker compose config`** — valida que `docker-compose.yml` está sintaticamente correto e resolve todas as variáveis de ambiente (não precisa do daemon rodando). Resultado: OK.
- **Simulação de máquina limpa**: o repositório foi clonado do zero em um diretório temporário (`git clone`), sem `database/app.db`, sem `.venv`, sem `node_modules`, sem `.env` — exatamente o estado de um computador que nunca rodou o projeto.
- **Cada comando que os containers executam internamente** (a sequência definida em `backend/docker-entrypoint.sh` e nos `Dockerfile`s) foi rodado diretamente nesse clone limpo, na mesma ordem:
  1. `pip install -e ".[dev]"` (equivalente ao build da imagem do backend) — concluído sem erros.
  2. `alembic upgrade head` em um banco SQLite novo — todas as 5 migrações aplicadas com sucesso.
  3. **Antes da correção**: tabela `ufs` ficava com 0 registros. **Depois da correção**: `python -m app.infrastructure.seeds.seed_ufs` populou as 27 UFs; `python -m app.infrastructure.seeds.seed_tipos_promotor` confirmou os 2 tipos (já semeados por migração, seed roda de forma idempotente por cima).
  4. Backend iniciado (`uvicorn`) — `GET /api/v1/health` respondeu `{"status":"ok","database":"ok"}`.
  5. **Upload real de uma planilha de clientes** via `POST /api/v1/importacoes/upload` (mesmo endpoint que a tela "Importações" usa) — resultado `"status": "CONCLUIDA"`, `"linhas_validas": 3`, `"linhas_invalidas": 0`. Esse é o teste decisivo: prova que o bug das UFs realmente bloquearia uma primeira importação, e que a correção resolve.
  6. `GET /api/v1/dashboard/kpis` — refletiu corretamente os 3 clientes recém-importados.
  7. `npm ci && npm run build` (equivalente ao build da imagem do frontend) — build concluído sem erros, gerando os arquivos estáticos finais.
  8. Frontend servido estaticamente e aberto em um navegador real (Playwright/Chromium): páginas Home, Dashboard e Importações carregadas e navegadas de ponta a ponta, **zero erros de JavaScript no console**. As três capturas de tela usadas em `PRIMEIRO_USO.md` vêm exatamente desta execução.

Em resumo: **a lógica de inicialização foi validada de ponta a ponta, incluindo uma importação real e a conferência do Dashboard** — só a camada de orquitração de containers propriamente dita (build das imagens Docker, rede entre os dois containers, healthcheck) não pôde ser exercitada neste ambiente específico. `docker-compose.yml`/`Dockerfile`s não foram alterados nesta tarefa (só o script de entrada do backend), então o risco residual é baixo, mas recomendo que a primeira ação do usuário seja rodar `./iniciar.sh` e confirmar que a mensagem de sucesso aparece — se algo divergir, os logs impressos pelo próprio script (`docker compose logs`) já indicam onde olhar.

## 4. Arquivos criados/alterados

| Arquivo | O que mudou |
|---|---|
| `iniciar.sh` (novo) | Comando único para subir a aplicação. |
| `parar.sh` (novo) | Comando único para encerrar a aplicação. |
| `PRIMEIRO_USO.md` (novo) | Guia de primeiro uso para usuário não técnico. |
| `docs/screenshots/*.png` (novo) | 3 capturas de tela reais (Home, Dashboard, Importações), usadas no guia. |
| `backend/docker-entrypoint.sh` | Passa a rodar os seeds de UF e tipo de promotor após a migração. |
| `scripts/setup.sh` | Mesmo ajuste, para o caminho de desenvolvimento sem Docker. |
| `README.md` | Seção "Como Executar Localmente" consolidada em um único caminho (Docker); aviso no topo apontando para `PRIMEIRO_USO.md`; estrutura de pastas atualizada. |
| `docs/DECISIONS.md` | Seções 31 (bug das UFs) e 32 (consolidação do caminho de execução). |

Nenhum arquivo de código de produto (backend/frontend, fora do script de entrada) foi alterado — esta tarefa não introduziu nem alterou funcionalidade, conforme pedido.

## 5. O que NÃO foi feito (e por quê)

- **Não removi** `scripts/setup.sh`, `dev-backend.sh` e `dev-frontend.sh` do repositório — continuam funcionando para quem for desenvolver, só deixaram de ser apresentados como opção na documentação voltada ao usuário final. Interpretei "manter apenas a forma mais simples" como uma decisão de **documentação/UX**, não de exclusão de ferramentas internas ainda úteis.
- **Não criei scripts `.bat`/PowerShell dedicados para Windows** — o comando alternativo universal (`docker compose up --build` / `docker compose down`) funciona em qualquer terminal com Docker instalado, incluindo Windows, e está documentado como alternativa em `PRIMEIRO_USO.md`. Criar e não conseguir validar um `.bat` específico pareceu pior do que documentar o comando universal com clareza.
- **Não validei em Windows/Mac reais** — apenas no ambiente Linux disponível nesta sessão (ver seção 3). Recomendo um teste real em pelo menos uma máquina Windows e uma Mac antes de distribuir `PRIMEIRO_USO.md` amplamente.

## 6. Próximos passos recomendados

1. Rodar `./iniciar.sh` em uma máquina real (idealmente uma que nunca teve o projeto instalado) e confirmar que a mensagem de sucesso aparece e que http://localhost:5173 carrega.
2. Importar uma planilha real seguindo `PRIMEIRO_USO.md` e confirmar que os dados aparecem no Dashboard.
3. Se tudo funcionar, este documento pode ser considerado a confirmação final antes de retomar a evolução funcional do projeto.

## 7. Adendo — alternativa sem Docker

Depois da entrega inicial, o Docker Desktop não instalou em uma máquina real de teste ("falha na instalação"). Isso é exatamente o cenário que a seção 5 já havia sinalizado como risco não coberto (sem validação em máquinas Windows/Mac reais) — para não deixar o usuário sem opção, adicionei um segundo caminho, sem depender do Docker:

- **`iniciar-sem-docker.sh` / `parar-sem-docker.sh`** (raiz do repositório) — mesma experiência de comando único, mesma correção de seeds (seção 31), mas rodando backend e frontend diretamente na máquina. Exige Python 3.12 e Node.js instalados (dois instaladores comuns, geralmente mais simples de instalar que o Docker Desktop em máquinas restritas).
- **Diferente da entrega inicial, este caminho pôde ser validado de ponta a ponta neste próprio ambiente** (que tem Python e Node, mas não o daemon Docker): clone limpo → `./iniciar-sem-docker.sh` → upload real de planilha → Dashboard refletindo os dados → `./parar-sem-docker.sh` → confirmação de que nenhum processo ficou para trás.
- **Um bug real foi encontrado nessa validação e corrigido antes de entregar**: a primeira versão do script usava `npm run dev`, cujo PID não correspondia ao processo real do servidor — `./parar-sem-docker.sh` "encerrava" o comando errado, deixando o frontend rodando escondido e a porta 5173 ocupada. Corrigido chamando o `vite` diretamente e adicionando uma segunda camada de segurança (`pkill -P`) em `parar-sem-docker.sh`. Detalhes em `docs/DECISIONS.md`, seção 33.
- `PRIMEIRO_USO.md` e `README.md` foram atualizados para apresentar as duas opções — Docker como recomendado, o caminho sem Docker como alternativa clara para quando o primeiro não for viável.
