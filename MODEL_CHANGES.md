# MODEL_CHANGES.md — Mudanças de Modelagem da Sprint 3 (dados reais)

> Fase 2 da Sprint 3: o modelo foi adaptado aos dados reais — **o sistema se
> adapta aos dados, nunca o contrário**. Racional completo em
> `docs/DECISIONS.md`, seções 12 (definições de negócio) e 13 (decisões
> técnicas). Migração: `alembic/versions/2026_07_12_1114_sprint_3_identidade_uuid_e_dados_reais.py`
> (ciclo upgrade → downgrade → upgrade validado; diff de autogeneração vazio).

## 1. Identidade UUID interna (diretriz de arquitetura do PO)

| Antes | Depois |
|---|---|
| PK `INTEGER AUTOINCREMENT` em 19 tabelas | PK `String(36)` com UUID v4 (`identidade.novo_uuid`) em **todas** as entidades |
| `empresas.uuid` como coluna separada | consolidada no próprio `id` |
| `logs_auditoria.entidade_id INTEGER` | `String(36)` |
| FKs `INTEGER` | `String(36)` em todas |

- **Exceção documentada:** `ufs.sigla` segue como PK (referência geográfica estática, código oficial imutável — não é identidade de negócio).
- Códigos de sistemas externos (`codigo_externo`, `codigo_origem`, CNPJ) são **apenas identificadores de integração** — nunca chave primária nem identidade global.

## 2. Tabelas novas

| Tabela | Origem real | Conteúdo |
|---|---|---|
| `tipos_promotor` | cadastro (seed TECNICO/TRADE na migração) | Tipo do promotor como dado cadastral — nunca inferido de importação |
| `clientes_integracao` | WeCheck (Local), Painel Avert (CNPJ) | Conciliação identidade externa → cliente interno; status PENDENTE/VINCULADO/IGNORADO; **nunca cria cliente automaticamente**; UQ (sistema_origem, codigo_origem) |
| `visitas_resumo_sb` | Relatório "Supervisor" SB Promotor | Carteira mensal oficial: contagens de visitas por promotor×cliente×competência (blocos promotor e cliente + 3 percentuais preservados); UQ (promotor, cliente, competência) |
| `carteiras_avert` | Painel Trade Avert | Carteira oficial Avert por CNPJ: consultor (promotora), vendedor, regional, grupo econômico, segmento e colunas de compra (mesmo vazias) |
| `visitas_produtos_sb` | Detalhe SB Promotor (aba Produtos) | 1 linha = 1 produto verificado em 1 visita (id externo da visita, marca, validade, lote, estoque, preço…) |
| `clientes_vendedores` | Base de Clientes (RCA 1..4) | Vínculo cliente×vendedor com `ordem` (posição original preservada); UQ (cliente, ordem) |

## 3. Colunas novas / nulabilidades em tabelas existentes

| Tabela | Mudança | Motivo (fonte real) |
|---|---|---|
| `clientes` | + inscricao_estadual, tipo_pessoa, ramo_atividade, numero, bairro, cep, telefone, data_ultima_compra | Base de Clientes tem 22 colunas — todas cobertas (nunca descartar colunas) |
| `promotores` | `tipo` (enum) → `tipo_promotor_id` FK **nula**; `supervisor_id` **nulo**; + `area` | Tipo é cadastral; nenhuma fonte informa supervisor; SB traz Área |
| `visitas` | + origem (SB_PROMOTOR/WECHECK), codigo_externo, cliente_integracao_id, local_texto, endereco_texto, cidade_texto, estado_texto, dados_brutos (JSON); `cliente_id` **nulo**; UQ (origem, codigo_externo) | Entidade unificada das duas origens (Strategy); WeCheck não tem código de cliente |
| `checklists` | + codigo_externo (CK_ID), origem; `tipo_promotor_alvo` **nulo**; UQ (origem, codigo_externo) | Templates nascem dos exports; público-alvo não é informado nem inferível |
| `checklist_respostas` | `resposta_valor` String(500) → **Text** | Respostas reais excedem 500 chars (URLs de fotos, descrições) |
| `faturamentos` | `departamento_id` **nulo** | Matriz real não tem departamento (colunas = laboratórios) |
| `laboratorios` | + categoria (LABORATORIO/BRINDE, default LABORATORIO) | BRINDE é categoria comercial à parte, não laboratório (definição do PO) |
| `importacoes` | + hash_conteudo (indexado), + competencia | Dedup por conteúdo (34/26 cópias físicas distintas em bytes, idênticas em células); fontes mensais não trazem o período no arquivo |
| `carteiras` | + competencia | Mês de referência informado na importação |

## 4. Enums

- Novos: `SistemaOrigem` (SB_PROMOTOR/WECHECK/PAINEL_AVERT), `StatusConciliacao` (PENDENTE/VINCULADO/IGNORADO), `CategoriaComercial` (LABORATORIO/BRINDE).
- `TipoArquivoImportacao` ampliado: + WECHECK, PAINEL_AVERT, SB_PRODUTOS. `CARTEIRA` passa a designar o relatório Supervisor do SB Promotor (carteira mensal oficial); `VISITAS` permanece para o layout documental legado.
- `TipoPromotor` continua existindo como o conjunto canônico de códigos de `tipos_promotor` (usado por validação e seed).

## 5. Impacto no código (varredura junto com a migração)

- Assinaturas `*_id: int` → `str` em motor, loaders, validadores, repositório, serviço, schemas e rotas (path param `importacao_id` agora é string).
- `obter_ou_criar_promotor` resolve `tipos_promotor` por código e **não aplica default de tipo** (era `TRADE` — seria inferência, proibida).
- Validador de checklist trata `ID_VISITA` como identificador **opaco** (texto), não número.
- Fixture de testes `_limpar_banco` reaplica o seed de `tipos_promotor` (banco volta ao estado "migração recém-executada").
- Suíte: 46 testes verdes; ruff/black/mypy sem erros; `alembic upgrade/downgrade` validados.
