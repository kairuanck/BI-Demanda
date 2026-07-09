# BACKEND.md — Arquitetura de Backend

## 1. Finalidade

Este documento especifica a arquitetura de backend do Promotores BI: princípios, estrutura de diretórios, responsabilidades de cada camada e convenções de implementação. É a referência obrigatória para toda implementação em Python/FastAPI realizada a partir da Sprint 00.

## 2. Princípios Arquiteturais

O backend segue **Clean Architecture**, com as seguintes camadas, sempre dependendo apenas de camadas mais internas (nunca o inverso):

```
┌─────────────────────────────────────────────────────────┐
│                         api/                             │  (mais externa)
│         routers, schemas de request/response, deps       │
├─────────────────────────────────────────────────────────┤
│                       services/                           │
│              regras de negócio, orquestração              │
├─────────────────────────────────────────────────────────┤
│                      repositories/                        │
│           acesso a dados, consultas, persistência          │
├─────────────────────────────────────────────────────────┤
│                        domain/                             │  (mais interna)
│        entidades, contratos (Protocols), exceções          │
└─────────────────────────────────────────────────────────┘
                              ▲
                              │ implementa contratos de
                              │
                       infrastructure/
        SQLAlchemy, hashing, sistema de arquivos, JWT
```

1. **`domain/`** define contratos (interfaces via `typing.Protocol` ou `abc.ABC`) e entidades de negócio puras, sem qualquer dependência de framework ou biblioteca de infraestrutura.
2. **`repositories/`** implementa os contratos de acesso a dados definidos em `domain/`, utilizando SQLAlchemy. Nenhuma regra de negócio reside aqui — apenas consultas e persistência.
3. **`services/`** contém toda a regra de negócio (`REGRAS_DE_NEGOCIO.md`), orquestrando repositórios e demais serviços via **Injeção de Dependência**. Services nunca acessam o banco diretamente — sempre através de repositórios injetados.
4. **`api/`** expõe os serviços via rotas FastAPI, traduzindo requisições/respostas HTTP em chamadas de serviço, sem lógica de negócio.
5. **`infrastructure/`** contém as implementações concretas de baixo nível (conexão de banco, hashing SHA-256/bcrypt, geração/validação de JWT, armazenamento de arquivos), injetadas nas camadas superiores via os contratos de `domain/`.

## 3. Princípios SOLID Aplicados

1. **Single Responsibility:** cada `service` trata de um único agregado de negócio (ex.: `ImportacaoService`, `CarteiraService`, `KpiService`); cada `repository` trata de uma única entidade.
2. **Open/Closed:** novos tipos de importador (`IMPORTADOR.md`) são adicionados implementando a interface `ImportadorArquivo` (`domain/importacao/contratos.py`), sem alterar o motor genérico de `ETL.md`.
3. **Liskov Substitution:** qualquer implementação de repositório (`SqlAlchemyClienteRepository`, por exemplo) é substituível por outra implementação do mesmo `Protocol` sem alterar o `service` consumidor — condição usada nos testes unitários (`TESTES.md`), que utilizam implementações em memória (fakes) dos repositórios.
4. **Interface Segregation:** contratos de `domain/` são pequenos e específicos por caso de uso (ex.: `LeitorDeHash`, `ArmazenadorDeArquivo`), evitando interfaces genéricas grandes.
5. **Dependency Inversion:** `services/` dependem de abstrações de `domain/`, nunca de classes concretas de `infrastructure/`. A ligação concreta ocorre exclusivamente na camada de composição (`api/dependencies.py`), via injeção de dependência do FastAPI (`Depends`).

## 4. Estrutura de Diretórios

```
backend/
├── app/
│   ├── main.py                       # instância FastAPI, registro de routers e middlewares
│   ├── core/
│   │   ├── config.py                 # leitura de variáveis de ambiente (Pydantic Settings)
│   │   ├── security.py               # utilitários de JWT/bcrypt (wrappers sobre infrastructure)
│   │   └── logging.py                # configuração do logging técnico (LOGS.md)
│   ├── domain/
│   │   ├── entidades/                # dataclasses de entidades de negócio (Usuario, Promotor, ...)
│   │   ├── enums/                    # Enums do sistema (DICIONARIO_DE_DADOS.md, seção 21)
│   │   ├── contratos/                # Protocols de repositórios e serviços de infraestrutura
│   │   └── excecoes.py               # exceções de domínio (ex.: ArquivoDuplicadoError)
│   ├── repositories/
│   │   ├── usuario_repository.py
│   │   ├── promotor_repository.py
│   │   ├── supervisor_repository.py
│   │   ├── vendedor_repository.py
│   │   ├── laboratorio_repository.py
│   │   ├── departamento_repository.py
│   │   ├── cliente_repository.py
│   │   ├── uf_repository.py
│   │   ├── cidade_repository.py
│   │   ├── carteira_repository.py
│   │   ├── faturamento_repository.py
│   │   ├── visita_repository.py
│   │   ├── checklist_repository.py
│   │   ├── importacao_repository.py
│   │   └── auditoria_repository.py
│   ├── services/
│   │   ├── auth_service.py           # AUTENTICACAO.md
│   │   ├── usuario_service.py
│   │   ├── importacao/
│   │   │   ├── motor_importacao.py   # ETL.md — pipeline genérico
│   │   │   ├── importador_clientes.py
│   │   │   ├── importador_carteira.py
│   │   │   ├── importador_faturamento.py
│   │   │   ├── importador_checklist.py
│   │   │   └── importador_visitas.py
│   │   ├── validador_service.py      # VALIDADOR.md
│   │   ├── hash_service.py           # HASH.md
│   │   ├── kpi_service.py            # KPIS.md
│   │   ├── dashboard_service.py      # DASHBOARD.md
│   │   ├── exportacao_service.py     # Excel/CSV/PDF
│   │   └── auditoria_service.py      # AUDITORIA.md
│   ├── infrastructure/
│   │   ├── database.py               # engine/session SQLAlchemy (DATABASE.md)
│   │   ├── models/                   # modelos SQLAlchemy (mapeiam DICIONARIO_DE_DADOS.md)
│   │   ├── security/
│   │   │   ├── jwt_provider.py
│   │   │   └── password_hasher.py    # bcrypt
│   │   ├── hashing/
│   │   │   └── sha256_hasher.py      # HASH.md
│   │   ├── storage/
│   │   │   └── file_storage.py       # armazenamento de importacao_arquivos
│   │   └── exporters/
│   │       ├── excel_exporter.py
│   │       ├── csv_exporter.py
│   │       └── pdf_exporter.py
│   └── api/
│       ├── dependencies.py           # composição de injeção de dependência
│       ├── middlewares/
│       │   ├── logging_middleware.py
│       │   └── auth_middleware.py
│       ├── schemas/                  # Pydantic models de request/response (API.md)
│       └── routers/
│           ├── auth_router.py
│           ├── usuarios_router.py
│           ├── clientes_router.py
│           ├── carteiras_router.py
│           ├── importacoes_router.py
│           ├── dashboards_router.py
│           ├── kpis_router.py
│           ├── auditoria_router.py
│           └── exportacoes_router.py
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic.ini
├── pyproject.toml
└── .env.example
```

## 5. Fluxo de uma Requisição Típica

```
Cliente HTTP
   │
   ▼
api/routers/<recurso>_router.py   (recebe requisição, valida schema Pydantic)
   │  Depends(...)
   ▼
api/dependencies.py               (resolve service concreto via injeção)
   │
   ▼
services/<recurso>_service.py     (executa regra de negócio, orquestra repositórios)
   │
   ▼
repositories/<entidade>_repository.py   (executa consulta/persistência via SQLAlchemy)
   │
   ▼
infrastructure/database.py        (sessão de banco)
   │
   ▼
Banco de Dados (SQLite/PostgreSQL)
```

## 6. Injeção de Dependência

1. Toda dependência entre camadas é declarada via `Depends()` do FastAPI, resolvida em `api/dependencies.py`.
2. Repositórios são injetados em serviços através do construtor (`__init__`), nunca instanciados diretamente dentro de um `service`.
3. A sessão de banco (`Session` do SQLAlchemy) é criada por requisição (`Depends(get_db_session)`), com escopo de vida limitado à requisição HTTP (padrão *session-per-request*).

## 7. Tipagem

1. Toda função, método, parâmetro e retorno possui anotação de tipo (`from __future__ import annotations` habilitado em todos os módulos).
2. Modelos de entrada/saída da API são `Pydantic BaseModel` (`api/schemas/`), nunca dicionários soltos.
3. Verificação de tipos estática via `mypy`, executada no pipeline de CI (`GITHUB.md`).

## 8. Tratamento de Erros

1. Exceções de domínio (`domain/excecoes.py`) são específicas por caso (`ArquivoDuplicadoError`, `RegistroNaoEncontradoError`, `PermissaoNegadaError`, `ValidacaoFalhouError`).
2. Um manipulador global de exceções (`api/main.py`) traduz exceções de domínio em respostas HTTP com código e corpo padronizados (`API.md`, seção de tratamento de erros).
3. Exceções não mapeadas resultam em HTTP 500, registradas em nível `CRITICAL` (`LOGS.md`).

## 9. Testes

Estratégia detalhada em `TESTES.md`. Em síntese: testes unitários de `services` utilizam repositórios fake (em memória); testes de integração de `repositories` utilizam SQLite efêmero com migrações aplicadas; testes end-to-end de `api` utilizam `TestClient` do FastAPI contra um banco de teste completo.

## 10. Documentação Automática da API

O FastAPI gera automaticamente a documentação OpenAPI/Swagger (`/docs`) e ReDoc (`/redoc`) a partir dos schemas Pydantic e docstrings dos routers — esta documentação viva complementa, mas não substitui, a especificação funcional completa em `API.md`.
