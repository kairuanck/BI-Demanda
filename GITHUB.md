# GITHUB.md — Fluxo de Controle de Versão

## 1. Finalidade

Este documento especifica o fluxo de branches, convenção de commits, estrutura de Pull Requests e pipeline de CI/CD do Promotores BI. O passo a passo de criação do repositório está em `TUTORIAL.md`, seção 1.

## 2. Estratégia de Branches

1. **`main`:** branch estável, sempre implantável. Nenhum commit é feito diretamente em `main` — toda alteração chega via Pull Request revisado.
2. **`sprint/NN-descricao-curta`:** uma branch por Sprint (ex.: `sprint/03-motor-importacao-base`), criada a partir de `main` atualizada, conforme execução de `SPRINT_XX.md`.
3. **`fix/descricao-curta`:** branches de correção pontual fora do ciclo de Sprint, quando necessário.
4. Não há branch de longa duração adicional (`develop`, `staging`) na POC — a simplicidade do fluxo é uma decisão deliberada para o tamanho da equipe e do projeto nesta fase.

## 3. Convenção de Commits

Formato: **Conventional Commits**, em português, no corpo descritivo, mantendo o prefixo em inglês por padronização de ferramentas:

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>

<corpo opcional explicando o porquê>
```

| Tipo | Uso |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de defeito |
| `docs` | Alteração exclusiva de documentação |
| `test` | Adição/ajuste de testes, sem alteração de comportamento |
| `refactor` | Reestruturação de código sem alteração de comportamento externo |
| `chore` | Tarefas de manutenção (dependências, configuração de tooling) |
| `perf` | Melhoria de desempenho |

Exemplo:
```
feat(importacao): implementa versionamento de carteira por hash SHA-256

Implementa o encerramento automático de vigência de carteira quando
um cliente muda de promotor entre versões de importação, conforme
REGRAS_DE_NEGOCIO.md, seção 5.2.
```

## 4. Estrutura de Pull Request

Todo Pull Request de Sprint segue o template abaixo (a ser criado em `.github/PULL_REQUEST_TEMPLATE.md` na Sprint 00):

```markdown
## Sprint
Sprint XX — <nome da sprint>

## Resumo
<1-3 bullets do que foi entregue>

## Documentos de referência
<lista dos .md utilizados como especificação>

## Checklist de Definition of Done (MASTER_PROMPT.md, seção 6)
- [ ] Entregáveis da SPRINT_XX.md implementados
- [ ] Testes automatizados implementados e passando
- [ ] Migrações Alembic aplicadas com sucesso a partir de banco vazio (quando aplicável)
- [ ] Lint e checagem de tipos sem erros
- [ ] Aplicação sobe localmente sem erros
- [ ] Critérios de Aceite da SPRINT_XX.md satisfeitos

## Critérios de Aceite Verificados
<lista copiada da seção "Critérios de Aceite" do SPRINT_XX.md, marcada item a item>
```

## 5. Revisão de Pull Request

1. Todo Pull Request exige, no mínimo, a validação automatizada do pipeline de CI (seção 6) com status verde antes de estar apto à mesclagem.
2. Revisão humana (do Product Owner/responsável do projeto) valida a aderência aos documentos de especificação referenciados no PR, não apenas a passagem dos testes.
3. Mesclagem via **squash and merge**, preservando uma mensagem de commit final única e descritiva em `main`, mantendo o histórico de `main` limpo por Sprint.

## 6. Pipeline de CI (GitHub Actions)

Definido em `.github/workflows/ci.yml` (criado na Sprint 00, estendido a cada Sprint conforme novas camadas são introduzidas):

| Etapa | Ferramenta | Aplicável a partir de |
|---|---|---|
| Lint Python | `ruff` | Sprint 00 |
| Formatação Python | `black --check` | Sprint 00 |
| Checagem de tipos Python | `mypy` | Sprint 00 |
| Testes backend | `pytest --cov` | Sprint 00 |
| Migrações Alembic (smoke test) | `alembic upgrade head` contra banco efêmero | Sprint 01 |
| Lint frontend | `eslint` | Sprint 09 |
| Testes frontend | `vitest run` | Sprint 09 |
| Build frontend | `npm run build` | Sprint 09 |

O job de CI falha (bloqueando a mesclagem) se qualquer etapa aplicável retornar código de saída diferente de zero.

## 7. Proteção da Branch `main`

1. Exige Pull Request para qualquer alteração (nenhum push direto).
2. Exige que o pipeline de CI (seção 6) esteja com status de sucesso.
3. Exige branch atualizada com `main` antes da mesclagem (rebase ou merge de `main` na branch de Sprint), evitando conflitos silenciosos.

## 8. Arquivos Ignorados (`.gitignore`)

Criado na Sprint 00, cobrindo no mínimo:
```
# Backend
__pycache__/
*.pyc
.venv/
promotores_bi.db
storage/
logs/
.env
backups/

# Frontend
node_modules/
dist/
.env
.env.production

# Diversos
.DS_Store
*.egg-info/
.coverage
htmlcov/
```

## 9. Segredos e Configuração de Repositório

1. Nenhum valor de `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY` ou credencial de banco é commitado — apenas `backend/.env.example` com nomes de variáveis e valores de exemplo não sensíveis.
2. Segredos utilizados no pipeline de CI (quando necessário, ex.: para testes de integração que exigem uma `DATABASE_URL` de teste) são configurados via GitHub Actions Secrets, nunca em arquivo versionado.

## 10. Relação entre Branches de Sprint e o Roadmap

A ordem de abertura de branches `sprint/NN-*` segue exatamente a ordem e as dependências descritas em `ROADMAP.md`, seção 2 e 4. Uma branch de Sprint só é aberta a partir de uma `main` que já incorporou a mesclagem da(s) Sprint(s) da qual ela depende.
