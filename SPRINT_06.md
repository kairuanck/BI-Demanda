# SPRINT_06.md — Importador de Faturamento

## 1. Objetivo

Implementar o importador de Faturamento Mensal, incluindo resolução/criação automática de Laboratório, Departamento e Vendedor, e a regra de inserção pura (append) que sustenta os KPIs de Positivação e Fora da Carteira.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `IMPORTADOR.md` (seção 5), `VALIDADOR.md` (seções 3–5 e 8), `REGRAS_DE_NEGOCIO.md` (seção 5.3), `DICIONARIO_DE_DADOS.md` (tabela `faturamentos`).

## 3. Pré-condições

Sprint 04 concluída (Faturamento depende de clientes pré-existentes, `IMPORTADOR.md`, seção 8). Não depende da Sprint 05 (Carteira) para funcionar tecnicamente, embora o KPI de Fora da Carteira, calculado na Sprint 08, relacione as duas entidades.

## 4. Escopo (Backlog Detalhado)

### 4.1 Repositórios de Apoio
1. Completar `app/repositories/laboratorio_repository.py`, `app/repositories/departamento_repository.py`, `app/repositories/vendedor_repository.py` com `buscar_por_codigo_externo` e `criar_se_nao_existir`.
2. Completar `app/repositories/faturamento_repository.py` com `inserir_lote` e consultas agregadas básicas (`somar_por_periodo`, utilizadas posteriormente pela Sprint 08).

### 4.2 Validador Específico
1. Implementar `app/services/importacao/validadores/validador_faturamento.py`, aplicando `FAT-001` a `FAT-004` (`VALIDADOR.md`, seção 8) e `REF-002` (cliente deve existir).

### 4.3 Importador Concreto
1. Implementar `app/services/importacao/importador_faturamento.py`, implementando `ImportadorArquivo`:
   - Extração/transformação do layout de `IMPORTADOR.md`, seção 5.1, incluindo conversão de valores monetários com separador `,`/`.` (`IMPORTADOR.md`, seção 2, item 4).
   - Resolução/criação de Laboratório, Departamento, Vendedor (`IMPORTADOR.md`, seção 5.2).
   - Persistência via inserção pura (append), sem atualização de linhas de versões anteriores (`REGRAS_DE_NEGOCIO.md`, seção 5.3, itens 2–3).
2. Registrar o importador no motor genérico, habilitando `POST /importacoes` com `tipo_arquivo = FATURAMENTO`.

### 4.4 Regra de Seleção de Versão Corrente
1. Implementar em `app/repositories/faturamento_repository.py` (ou em um utilitário compartilhado `app/services/importacao/versao_corrente.py`, reutilizável pelas Sprints 07 e 08) a consulta que filtra exclusivamente registros de importações com `status IN ('CONCLUIDA', 'CONCLUIDA_COM_ERROS')`, considerando a versão mais recente não revertida por `tipo_arquivo` (`REGRAS_DE_NEGOCIO.md`, seção 7). Este utilitário é a base de todas as consultas analíticas da Sprint 08.

## 5. Fora de Escopo desta Sprint

1. Importadores de Visitas e Checklist — Sprint 07.
2. Cálculo de KPIs (Positivação, Fora da Carteira, Região) — Sprint 08.

## 6. Entregáveis

1. Importador de Faturamento Mensal funcional de ponta a ponta.
2. Utilitário de "versão corrente" reutilizável, testado isoladamente.
3. Testes cobrindo valores negativos (estornos), múltiplas versões coexistentes no banco e a exclusão correta de versões antigas/revertidas das consultas de versão corrente.

## 7. Critérios de Aceite

1. Upload de um arquivo de Faturamento válido persiste corretamente todas as linhas, com resolução/criação automática de Laboratório/Departamento/Vendedor.
2. `VALOR_FATURADO` negativo é aceito e persistido sem erro de validação (`REGRAS_DE_NEGOCIO.md`, seção 5.3, item 4).
3. `ANO` fora do intervalo permitido ou `MES` fora de 1–12 gera erro de validação `FAT-001`/`FAT-002` e a linha não é persistida.
4. Reimportação do mesmo período (Ano/Mês) gera uma nova versão cujos registros coexistem fisicamente com a versão anterior no banco, e o utilitário de versão corrente retorna exclusivamente os registros da versão mais recente não revertida.
5. Reversão (rollback) de uma importação de Faturamento faz com que o utilitário de versão corrente volte a considerar a versão anterior.
6. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida, incluindo o teste de regressão "Nunca sobrescrever" (`TESTES.md`, seção 10, item 1).

## 8. Riscos e Observações

1. O utilitário de "versão corrente" implementado nesta Sprint é crítico e será reutilizado, sem alteração de contrato, pelos importadores de Visitas/Checklist (Sprint 07) e por toda a camada de KPIs (Sprint 08) — qualquer ajuste em seu comportamento nesta Sprint deve ser cuidadosamente coberto por teste, dado o alto acoplamento de consumidores futuros.
