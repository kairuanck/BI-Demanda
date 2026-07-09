# DER.md — Diagrama Entidade-Relacionamento

## 1. Finalidade

Este documento apresenta o Diagrama Entidade-Relacionamento (DER) completo do Promotores BI, em notação Mermaid (`erDiagram`), compatível com renderização nativa no GitHub. A definição conceitual de cada entidade está em `MODELAGEM.md`; a definição física (colunas, tipos, restrições) está em `DICIONARIO_DE_DADOS.md`.

## 2. Diagrama Completo

```mermaid
erDiagram
    USUARIOS ||--o| PROMOTORES : "vincula (opcional)"
    USUARIOS ||--o| SUPERVISORES : "vincula (opcional)"
    SUPERVISORES ||--o{ PROMOTORES : "supervisiona"
    UFS ||--o{ CIDADES : "contem"
    CIDADES ||--o{ CLIENTES : "localiza"
    PROMOTORES ||--o{ CARTEIRAS : "atende"
    CLIENTES ||--o{ CARTEIRAS : "e_atendido_em"
    IMPORTACOES ||--o{ CARTEIRAS : "origina"
    CLIENTES ||--o{ FATURAMENTOS : "gera"
    LABORATORIOS ||--o{ FATURAMENTOS : "referencia"
    DEPARTAMENTOS ||--o{ FATURAMENTOS : "referencia"
    VENDEDORES ||--o{ FATURAMENTOS : "atribui (opcional)"
    IMPORTACOES ||--o{ FATURAMENTOS : "origina"
    PROMOTORES ||--o{ VISITAS : "realiza"
    CLIENTES ||--o{ VISITAS : "recebe"
    IMPORTACOES ||--o{ VISITAS : "origina"
    CHECKLISTS ||--o{ CHECKLIST_PERGUNTAS : "possui"
    CHECKLIST_PERGUNTAS ||--o{ CHECKLIST_RESPOSTAS : "e_respondida_em"
    VISITAS ||--o{ CHECKLIST_RESPOSTAS : "contem"
    IMPORTACOES ||--o{ CHECKLIST_RESPOSTAS : "origina"
    IMPORTACOES ||--o{ IMPORTACAO_ERROS : "gera"
    IMPORTACOES ||--|| IMPORTACAO_ARQUIVOS : "armazena"
    IMPORTACOES ||--o| IMPORTACOES : "versao_anterior"
    USUARIOS ||--o{ LOGS_AUDITORIA : "executa"
    USUARIOS ||--o{ IMPORTACOES : "realiza"

    USUARIOS {
        int id PK
        string nome
        string email
        string senha_hash
        string perfil
        bool ativo
        int promotor_id FK
        int supervisor_id FK
        datetime criado_em
        datetime atualizado_em
        datetime ultimo_login_em
    }

    SUPERVISORES {
        int id PK
        string nome
        string codigo_externo
        string email
        bool ativo
        datetime criado_em
        datetime atualizado_em
    }

    PROMOTORES {
        int id PK
        string nome
        string codigo_externo
        string tipo
        int supervisor_id FK
        string email
        string telefone
        bool ativo
        date data_admissao
        datetime criado_em
        datetime atualizado_em
    }

    VENDEDORES {
        int id PK
        string nome
        string codigo_externo
        bool ativo
        datetime criado_em
        datetime atualizado_em
    }

    LABORATORIOS {
        int id PK
        string nome
        string codigo_externo
        bool ativo
        datetime criado_em
        datetime atualizado_em
    }

    DEPARTAMENTOS {
        int id PK
        string nome
        string codigo_externo
        bool ativo
        datetime criado_em
        datetime atualizado_em
    }

    UFS {
        string sigla PK
        string nome
        string regiao
    }

    CIDADES {
        int id PK
        string nome
        string uf_sigla FK
        string codigo_ibge
        datetime criado_em
    }

    CLIENTES {
        int id PK
        string codigo_externo
        string razao_social
        string nome_fantasia
        string cnpj_cpf
        string uf_sigla FK
        int cidade_id FK
        string endereco
        string canal
        bool ativo
        datetime criado_em
        datetime atualizado_em
    }

    CARTEIRAS {
        int id PK
        int promotor_id FK
        int cliente_id FK
        int importacao_id FK
        date data_inicio_vigencia
        date data_fim_vigencia
        string status
        datetime criado_em
    }

    FATURAMENTOS {
        int id PK
        int cliente_id FK
        int laboratorio_id FK
        int departamento_id FK
        int vendedor_id FK
        int ano
        int mes
        numeric valor_faturado
        numeric quantidade
        int importacao_id FK
        datetime criado_em
    }

    VISITAS {
        int id PK
        int promotor_id FK
        int cliente_id FK
        date data_visita
        time hora_inicio
        time hora_fim
        string tipo_visita
        numeric latitude
        numeric longitude
        string observacoes
        string status
        int importacao_id FK
        datetime criado_em
    }

    CHECKLISTS {
        int id PK
        string nome
        string tipo_promotor_alvo
        bool ativo
        int versao
        datetime criado_em
    }

    CHECKLIST_PERGUNTAS {
        int id PK
        int checklist_id FK
        int ordem
        string enunciado
        string tipo_resposta
        bool obrigatoria
        numeric peso
    }

    CHECKLIST_RESPOSTAS {
        int id PK
        int visita_id FK
        int checklist_pergunta_id FK
        string resposta_valor
        bool conforme
        int importacao_id FK
        datetime criado_em
    }

    IMPORTACOES {
        int id PK
        string tipo_arquivo
        string nome_arquivo_original
        string hash_sha256
        int tamanho_bytes
        int usuario_id FK
        string status
        int versao
        int importacao_pai_id FK
        int total_linhas
        int linhas_validas
        int linhas_invalidas
        datetime iniciado_em
        datetime concluido_em
        datetime criado_em
    }

    IMPORTACAO_ERROS {
        int id PK
        int importacao_id FK
        int numero_linha
        string coluna
        string valor_recebido
        string mensagem_erro
        datetime criado_em
    }

    IMPORTACAO_ARQUIVOS {
        int id PK
        int importacao_id FK
        string caminho_armazenamento
        string nome_arquivo
        datetime criado_em
    }

    LOGS_AUDITORIA {
        int id PK
        string entidade
        int entidade_id
        string acao
        int usuario_id FK
        json dados_antes
        json dados_depois
        string ip_origem
        string user_agent
        datetime criado_em
    }
```

## 3. Notas de Leitura do Diagrama

1. Relacionamentos marcados como `o|` ou `o{` no lado "muitos" representam cardinalidade **opcional** (0 ou N); `||` representa cardinalidade **obrigatória** (exatamente 1).
2. O autorrelacionamento `IMPORTACOES ||--o| IMPORTACOES` representa o vínculo `importacao_pai_id`, que conecta uma importação à versão imediatamente anterior do mesmo arquivo lógico (mesmo `tipo_arquivo`), formando uma cadeia de versões.
3. As dimensões geográficas (`UFS`, `CIDADES`) são normalizadas para suportar os filtros de UF e Cidade descritos em `DASHBOARD.md` com integridade referencial, evitando divergência de grafia entre importações.
4. O diagrama reflete exatamente as 19 tabelas físicas descritas em `DICIONARIO_DE_DADOS.md` — nenhuma tabela adicional deve ser criada na implementação sem atualização correspondente deste diagrama.
