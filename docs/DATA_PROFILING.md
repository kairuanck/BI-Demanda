# DATA_PROFILING.md — Engenharia Reversa dos Dados Reais (Sprint 3, Fase 1)

> Dados analisados a partir de 5 pacotes reais exportados dos sistemas da empresa
> (recebidos em 12/07/2026). Este documento descreve **estrutura**, não conteúdo:
> nomes de clientes, CNPJs e nomes de funcionários foram deliberadamente omitidos
> por este repositório ser público. Os arquivos originais **não** são versionados
> (ver `.gitignore`) e permanecem apenas no ambiente de execução.

## 1. Inventário Recebido

| Pacote | Conteúdo físico | Conteúdo lógico efetivo |
|---|---|---|
| `BASE DE CLIENTES - BRASIL.xlsx` | 1 xlsx, 1 aba | Cadastro de clientes (21.942 linhas × 22 colunas) |
| `Faturamento.zip` | 6 xlsx (Janeiro…Junho) | Matriz mensal Cliente × Marca (ano 2026) |
| `Visitas promotoras SB promotor.7z` | 35 xlsx | **34 cópias idênticas** de 1 relatório "Supervisor" + 1 arquivo de detalhe de visitas |
| `Promotoras Avert - WeCheck.zip` | 7 xlsx | 6 exports mensais de formulários + 1 painel de carteira Avert |
| `Check-list Junho26.zip` | 26 xlsx | **26 cópias idênticas** de 1 export com 8 abas de checklist |

**Achado crítico de duplicidade física:** os pacotes SB Promotor e Checklist contêm o
mesmo relatório exportado dezenas de vezes (timestamps sequenciais no nome do arquivo,
~7s de intervalo). O hash de **conteúdo de células** é idêntico entre as cópias, mas o
hash **binário** difere (metadados internos do xlsx, ex.: `docProps/core.xml`).
Consequência direta: deduplicação apenas por SHA-256 binário não detecta essas cópias
(ver decisão técnica em `DECISIONS.md`, Sprint 3).

## 2. Fonte: Base de Clientes

- **Formato:** long (1 linha = 1 cliente). 21.942 linhas × 22 colunas.
- **Chave primária:** `Código` (21.942 valores únicos — 100%).
- **Colunas:** Código, CNPJ/CPF, Insc. Est./Produtor, Cliente (razão social),
  Fantasia, Tipo de Pessoa (`Jurídica(J)`/`Física(F)`), Ramo Atividade (19 valores),
  Endereço Comercial, Número, Bairro, Nome da Cidade (1.127), Estado (24 UFs),
  CEP, Telefone, `RCA 1`/`Nome RCA`, `RCA 2`/`Nome RCA`, `RCA 3`/`Nome RCA`,
  `RCA4` (sem coluna de nome), Data da Última Compra (datetime).
- **Observações de qualidade:**
  - 77 documentos CNPJ/CPF aparecem em mais de um cliente (154 linhas) — clientes
    distintos por `Código` compartilhando documento.
  - `RCA 1..4` = vendedores (até 4 por cliente); 254 RCAs distintos no RCA 1.
  - 3.628 clientes sem "Data da Última Compra".
  - Não há coluna de laboratório/departamento — cadastro puro.

## 3. Fonte: Faturamento (mensal)

- **Formato:** **WIDE** — matriz pivotada.
  - Linha 1: rótulo `Departamento` + nomes das marcas nas colunas.
  - Linha 2: rótulo `Cliente` + "Medidas faturamento".
  - Linhas de dados: `"<código> - <razão social>"` na coluna A; valores monetários por marca.
  - Penúltima linha: `Total` por coluna. Última linha: rodapé "Filtros aplicados".
- **Colunas de marca (13–14, varia por mês):** AGROLIFE, AVERT, BBPET, BBPET ESTETICA,
  BIOCLIN, BRINDE (presente apenas em Março e Abril), CEVA, ELANCO, OURO FINO,
  OURO FINO WELLPET, SPIN, SYNTEC, WANPY, Total.
- **Rodapé (todos os 6 arquivos):** "Nome é Faturamento; Operação é Venda ou Devolução;
  Incluídos (1) **2026 (Ano)** + `<mês>` (Mês); NUMNOTA não é 94083" — confirma ano de
  referência 2026, mês correspondente ao nome do arquivo, valores líquidos de
  venda+devolução (negativos possíveis) e exclusão de uma nota específica.
- **Volumetria:** ~3.600 clientes/mês.
- **Integridade referencial:** Janeiro: 3.603 de 3.604 códigos de cliente existem na
  Base de Clientes (1 ausente).
- **Nota semântica:** o export chama a dimensão das colunas de "Departamento", mas os
  valores são marcas/fornecedores — pergunta de negócio aberta (ver seção 8).

## 4. Fonte: SB Promotor

### 4.1 Relatório "Supervisor" (34 cópias idênticas → 1 relatório lógico)
- **Formato:** wide desnormalizado, 18.123 linhas × 16 colunas, dois blocos lado a lado:
  - Bloco promotor (cols 1–7): Código, Nome, Área, Visitas Previstas,
    Previstas Realizadas, Previstas Não Realizadas, Não Prevista Realizadas.
  - Bloco cliente (cols 8–16): Código, Nome Fantasia, Razão Social, Visitas Previstas,
    Visitas Realizadas, Não Visitas, e 3 colunas de percentuais.
- **Granularidade:** 1 linha = 1 par promotor × cliente com **contagens agregadas** de
  visitas. **Não há datas nem período de referência no arquivo** (pergunta de negócio).
- **Volumetria:** 37 promotores; 8.068 clientes distintos (8.056 = 99,85% existem na
  Base de Clientes; 12 ausentes).
- Este relatório é, na prática, a **fotografia da carteira promotor×cliente** do SB
  Promotor, com métricas de execução de visitas.

### 4.2 Arquivo de detalhe (1 arquivo, 4 abas)
- Abas: `Produtos` (16 linhas), `Gondola` (vazia), `ProdutoSimilar` (vazia), `Tarefas` (vazia).
- `Produtos`: VISITA (id numérico), CÓDIGO+FUNCIONARIO (promotor), REGIÃO (UF),
  COD. CLIENTE+RAZAO SOCIAL+NOME FANTASIA, DATA INICIAL/FINAL (dd/mm/aaaa),
  OPERAÇÃO, GRUPO (marca, ex.: BBPET), MARCA, COD. PRODUTO, PRODUTO, VALIDADE, LOTE,
  ESTOQUE, PREÇO, OBSERVAÇÃO. Granularidade: 1 linha = 1 produto verificado em 1 visita.

## 5. Fonte: WeCheck (promotoras Avert)

### 5.1 Exports mensais (6 arquivos, Jan–Jun)
- **Formato:** 1 aba por formulário; colunas = perguntas do formulário (**wide**);
  linhas = respostas (1 linha = 1 visita/evento registrado).
- **Formulários observados:** "1ª Visita de Trade", "Evento", "Visita de Trade".
- **Colunas de contexto comuns:** Formulário, Data/Hora do Item, Local (texto livre),
  Endereço, Cidade, Estado, Autor, Tarefa, Descrição.
- **Schema drift real entre meses:** número e conjunto de colunas variam
  (26→31 colunas na aba principal; meses com colunas extras: Perfil, Validado,
  Status da Tarefa, "Data de Abertura (Evento)"). O conector precisa casar colunas
  por nome normalizado, tolerando ausências.
- **Volumetria (aba principal "Visita de Trade"):** Jan=108, Fev=118, Mar=125,
  Abr=140, Mai=163, Jun=160 registros.
- **Identificação:** **não há código de cliente** — apenas `Local` textual +
  Cidade/Estado. `Autor` = nome da promotora (3 autoras distintas no semestre).
  Perguntas de foto contêm URLs externas (`biolab.wecheck.app/...`).

### 5.2 Painel de carteira Avert (1 arquivo, "PAINEL TRADE - PETSLIFE - NOVO PADRÃO")
- 205 linhas × 16 colunas, 1 linha = 1 cliente da carteira Avert (UF única: RS).
- Colunas: CNPJ (205 únicos), COMPRA 2025/2026/CRESC (vazias), UF, ÁREA, REGIONAL,
  DISTRIBUIDOR, COORDENADOR, CONSULTOR (5), VENDEDOR (15), GRUPO ECONÔMICO,
  NOME FANTASIA, RAZÃO SOCIAL, SEGMENTO (36), OBS (vazia).
- **Cruzamento por CNPJ:** 162 dos 205 CNPJs existem na Base de Clientes; **43 não**.

## 6. Fonte: Checklists (junho/2026)

- 26 arquivos **idênticos em conteúdo** → 1 export lógico com **8 abas**, uma por
  template de checklist: Visita Técnica (CK_ID 6, 958 linhas), Trade (CK_ID 7, 171),
  Visita Loja (390), Trabalho Dia com REP (68), Reunião Clínica (58), Evento (79),
  Avaliação de Uso (240), Reunião (22). Total: **1.986 aplicações**.
- **Todas as abas têm as mesmas 42 colunas** (10 de contexto + 32 perguntas = união de
  todas as perguntas de todos os templates); cada template preenche só as suas —
  formato **wide** a converter para long.
- **Contexto:** CÓDIGO+FUNCIONÁRIO (promotor — 17 distintos, todos presentes também no
  relatório SB Supervisor), UF, CÓDIGO(.1)+RAZÃO SOCIAL+FANTASIA (cliente — 100% dos
  códigos existem na Base de Clientes), **VISITA (id único por linha)**, CK_ID,
  CHECKLIST (nome do template), APLICAÇÃO (data/hora dd/mm/aaaa hh:mm).
- Pergunta "Quem é o RCA responsável pela loja" referencia códigos de RCA da Base de
  Clientes (34 dos 43 valores citados existem lá; valores como `0` são placeholders).

## 7. Grafo de Relacionamentos Descoberto

```
Base de Clientes (Código) ◄────────── Faturamento (código no rótulo "COD - NOME")   [99,97%]
        ▲  ▲  ▲
        │  │  └────────────────────── Checklist (CÓDIGO.1)                           [100%]
        │  └───────────────────────── SB Supervisor (Código cliente)                 [99,85%]
        │
        └── CNPJ/CPF ◄──────────────── Painel Avert (CNPJ)                           [79%: 162/205]

Promotores SB (Código) ── Checklist.CÓDIGO ⊆ SBSupervisor.Código   [17 ⊆ 37]
Vendedores (RCA 1..4 da Base) ◄── Checklist."Quem é o RCA..."      [34/43]
WeCheck.Autor (3 nomes) — sem código; sem vínculo formal com promotores SB
WeCheck.Local (texto) — sem código; vínculo possível apenas por nome/fuzzy com Painel/Base
Marcas: Faturamento (colunas) ∩ SBPromotor.Produtos.GRUPO (ex.: BBPET)
```

## 8. Divergências vs. Modelo Documentado (entradas para Fase 2 e perguntas de negócio)

1. **Faturamento** real é matriz wide Cliente×Marca, sem Vendedor, sem Departamento
   separado de Laboratório, sem quantidade — o layout documentado em `IMPORTADOR.md`
   (long, com CODIGO_VENDEDOR/ANO/MES/QUANTIDADE) não existe na prática.
2. **Não existe arquivo de "Carteira" dedicado**: a carteira emerge do relatório SB
   Supervisor (promotor×cliente) e do Painel Avert (CNPJ×consultor).
3. **Não existe arquivo de "Visitas" individual do SB** (além dos agregados do
   Supervisor e das 16 linhas de detalhe de Produtos); as aplicações de checklist
   carregam o id `VISITA` + data — são o registro individual de visita disponível.
4. **WeCheck** não referencia cliente por código — integração exige decisão de negócio.
5. **Duplicidade física massiva** de exports idênticos exige deduplicação por conteúdo.
6. **Schema drift** entre meses (WeCheck) e entre meses de Faturamento (coluna BRINDE
   presente só em Março/Abril) exige leitura adaptativa por nome de coluna.
