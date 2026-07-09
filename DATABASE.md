# DATABASE.md — Estratégia de Banco de Dados

## 1. Visão Geral

O Promotores BI utiliza **SQLite** como banco de dados da POC e é modelado, desde o primeiro dia, para ser **100% compatível com PostgreSQL**, permitindo migração sem alteração de modelagem lógica. Todo o acesso a dados é realizado via **SQLAlchemy 2.x** (ORM) e todas as alterações de schema são controladas via **Alembic**.

Este documento define a estratégia geral do banco de dados. A modelagem lógica das entidades está em `MODELAGEM.md`, o diagrama entidade-relacionamento em `DER.md` e o dicionário de dados completo (tabela a tabela, coluna a coluna) em `DICIONARIO_DE_DADOS.md`.

## 2. Motivos da Escolha SQLite → PostgreSQL

| Critério | SQLite (POC) | PostgreSQL (produção/SaaS) |
|---|---|---|
| Instalação | Zero configuração, arquivo único | Requer servidor dedicado |
| Concorrência de escrita | Limitada (adequada a POC/single-tenant) | Alta concorrência, MVCC completo |
| Tipos avançados | Suporte limitado a JSON, arrays | Suporte nativo robusto a JSON/JSONB |
| Escalabilidade | Vertical, arquivo local | Horizontal/vertical, replicação |
| Uso no projeto | Ambiente de desenvolvimento e demonstração da POC | Ambiente de produção, após validação da POC |

## 3. Regras de Compatibilidade Obrigatórias

Para garantir a portabilidade SQLite → PostgreSQL sem retrabalho de modelagem, todo modelo SQLAlchemy deste projeto deve obedecer:

1. **Chaves primárias:** sempre inteiros autoincrementais (`Integer`, `primary_key=True`, `autoincrement=True`), exceto a tabela `ufs`, cuja chave primária natural é a sigla (`String(2)`). Nunca utilizar tipos específicos de um único dialeto (ex.: `AUTOINCREMENT` literal do SQLite).
2. **Tipos de dado:** usar exclusivamente tipos SQLAlchemy genéricos (`Integer`, `String`, `Boolean`, `Date`, `DateTime`, `Numeric`, `Text`, `Enum`) — nunca tipos específicos de dialeto (`sqlite.JSON`, `postgresql.ARRAY`, etc.), com exceção documentada do campo `dados_antes`/`dados_depois` de `logs_auditoria`, que usa `JSON` genérico do SQLAlchemy (suportado nativamente por ambos os dialetos via serialização).
3. **Booleanos:** sempre `Boolean` do SQLAlchemy (SQLite armazena como `INTEGER 0/1` de forma transparente; PostgreSQL usa `BOOLEAN` nativo).
4. **Datas e horas:** sempre `DateTime` (armazenamento em UTC na camada de persistência; conversão para `America/Sao_Paulo` ocorre na camada de apresentação/API, nunca no banco).
5. **Valores monetários e numéricos decimais:** sempre `Numeric(precision, scale)`, nunca `Float`, para evitar problemas de arredondamento em valores de faturamento.
6. **Enums:** implementados como `Enum` do SQLAlchemy baseado em `enum.Enum` do Python, armazenados como `String` no banco (`native_enum=False`), garantindo compatibilidade idêntica entre SQLite e PostgreSQL e facilitando migrações futuras de valores.
7. **Chaves estrangeiras:** sempre declaradas explicitamente com `ForeignKey`, com `ondelete` explícito (`RESTRICT`, `CASCADE` ou `SET NULL`, conforme definido por tabela em `DICIONARIO_DE_DADOS.md`). SQLite exige `PRAGMA foreign_keys=ON`, habilitado obrigatoriamente na inicialização da conexão (`infrastructure/database.py`, ver `BACKEND.md`).
8. **Índices:** declarados via `Index`/`index=True` no modelo, nunca criados manualmente fora do controle do Alembic.
9. **Strings:** sempre com tamanho explícito (`String(n)`) exceto campos de texto livre, que usam `Text`.
10. **Nomenclatura:** tabelas e colunas em `snake_case`, em português, no singular para colunas e no plural para tabelas (ex.: tabela `promotores`, coluna `nome`).

## 4. Estratégia de Migrações (Alembic)

1. Toda alteração de schema é feita exclusivamente via migração Alembic gerada a partir dos modelos SQLAlchemy (`alembic revision --autogenerate`), seguida de revisão manual obrigatória do arquivo gerado antes de aplicar.
2. Migrações são sempre aditivas por padrão. Alterações destrutivas (remoção de coluna/tabela) exigem:
   - Registro da decisão em `REGRAS_DE_NEGOCIO.md` ou no corpo do Pull Request correspondente.
   - Uma migração de "depreciação" (torna a coluna nula/não utilizada) antes de uma migração futura de remoção efetiva, quando aplicável ao contexto de dados já existentes.
3. O identificador de cada migração segue o padrão `AAAA_MM_DD_HHmm_descricao_curta`, gerado automaticamente pelo Alembic com `file_template` configurado em `alembic.ini` (detalhado em `BACKEND.md`).
4. O ambiente de testes automatizados aplica todas as migrações do zero (`alembic upgrade head`) contra um banco SQLite efêmero antes da execução da suíte de testes, garantindo que o histórico de migrações é sempre válido.

## 5. Estrutura de Conexão

- **POC (SQLite):** arquivo `backend/promotores_bi.db`, fora do controle de versão (listado em `.gitignore`), criado automaticamente na primeira execução das migrações.
- **Produção (PostgreSQL):** string de conexão via variável de ambiente `DATABASE_URL`, no formato `postgresql+psycopg://usuario:senha@host:porta/banco`.
- A camada de infraestrutura (`backend/app/infrastructure/database.py`) lê `DATABASE_URL` do ambiente; na ausência da variável, assume o padrão SQLite local da POC (`sqlite:///./promotores_bi.db`), conforme detalhado em `DEPLOY.md`.
- O `Engine` do SQLAlchemy é criado com `pool_pre_ping=True` em ambos os dialetos, e com `connect_args={"check_same_thread": False}` exclusivamente quando o dialeto é SQLite.

## 6. Categorias de Tabelas

O modelo de dados do Promotores BI (detalhado em `MODELAGEM.md` e `DICIONARIO_DE_DADOS.md`) é organizado em quatro categorias:

1. **Cadastros/Dimensões:** `usuarios`, `supervisores`, `promotores`, `vendedores`, `laboratorios`, `departamentos`, `ufs`, `cidades`, `clientes`.
2. **Fatos versionados:** `carteiras`, `faturamentos`, `visitas`, `checklists`, `checklist_perguntas`, `checklist_respostas`.
3. **Controle de Importação:** `importacoes`, `importacao_erros`, `importacao_arquivos`.
4. **Auditoria:** `logs_auditoria`.

Nenhum KPI (`KPIS.md`) é armazenado em tabela própria na POC — todos são calculados sob demanda pela camada de serviço a partir das tabelas de fato, conforme `REGRAS_DE_NEGOCIO.md`. Esta é uma premissa adotada para simplicidade da POC; a introdução de tabelas de agregação materializada é um item de evolução pós-POC (`ROADMAP.md`, seção 5).

## 7. Estratégia de Backup (POC)

1. O arquivo SQLite (`promotores_bi.db`) é copiado integralmente antes de qualquer operação de rollback de importação em massa, para o diretório `backend/backups/`, com nome `promotores_bi_AAAAMMDD_HHmmss.db`.
2. Esta cópia é adicional à trilha de auditoria em `logs_auditoria` e ao histórico de `importacoes` — não a substitui.
3. Em produção (PostgreSQL), a estratégia de backup é a nativa do provedor de hospedagem (`DEPLOY.md`), fora do escopo de implementação da POC.

## 8. Isolamento e Transações

1. Toda operação de importação (Sprints 03 a 07) é executada dentro de uma única transação de banco: ou todas as linhas válidas e os registros de controle são persistidos, ou nada é persistido em caso de falha inesperada durante a gravação.
2. O nível de isolamento padrão do SQLAlchemy (`READ COMMITTED` em PostgreSQL; SQLite usa serialização própria) é mantido sem customização na POC.
3. Rollback de importação (`REGRAS_DE_NEGOCIO.md`) é uma operação de negócio distinta de rollback de transação de banco — consiste em uma nova operação que reverte o efeito de uma importação anterior, preservando o histórico (nunca um `DELETE` físico dos dados da importação revertida).
