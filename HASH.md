# HASH.md — Estratégia de Hash e Versionamento de Arquivos

## 1. Finalidade

Este documento especifica a estratégia de cálculo de hash, detecção de duplicidade e versionamento de arquivos importados, mecanismo central da garantia de que o Promotores BI **nunca sobrescreve dados** e **sempre mantém histórico**, conforme princípios definidos em `REGRAS_DE_NEGOCIO.md`, seção 2.

## 2. Algoritmo de Hash

1. Algoritmo utilizado: **SHA-256** (biblioteca `hashlib` do Python, função `hashlib.sha256`).
2. O hash é calculado sobre o **conteúdo binário integral** do arquivo `.xlsx` recebido no upload, antes de qualquer leitura ou transformação (ou seja, byte a byte do arquivo original, não do conteúdo interpretado pelo Pandas).
3. O resultado é armazenado como string hexadecimal de 64 caracteres em `importacoes.hash_sha256` (`DICIONARIO_DE_DADOS.md`, seção 17).
4. O cálculo é realizado em streaming (leitura em blocos de 8192 bytes), evitando carregar arquivos grandes integralmente em memória apenas para o cálculo do hash.

## 3. Classificação do Upload

A cada novo upload, o sistema classifica o arquivo em uma das quatro categorias abaixo, cruzando o hash calculado com o histórico de `importacoes` do mesmo `tipo_arquivo`:

| Categoria | Condição | Comportamento |
|---|---|---|
| **Arquivo Novo (primeira versão)** | Não existe nenhuma importação anterior para o `tipo_arquivo` | Cria importação com `versao = 1`, `importacao_pai_id = NULL`. |
| **Arquivo Repetido** | Existe importação anterior do mesmo `tipo_arquivo` com `hash_sha256` **idêntico** | Importação é recusada (`status = FALHOU`), nenhuma linha é processada. Usuário é informado da importação original (data, versão, responsável). |
| **Arquivo Alterado (nova versão)** | Existe importação anterior do mesmo `tipo_arquivo`, mas com `hash_sha256` **diferente** | Cria nova importação com `versao = MAX(versao) + 1` para o `tipo_arquivo`, `importacao_pai_id` apontando para a importação de maior versão concluída anterior. |
| **Reenvio Pós-Falha** | Existe importação anterior do mesmo `tipo_arquivo` e mesmo hash, porém com `status = FALHOU` | Tratado como nova tentativa: nova importação é criada (mesma regra de versão do "Arquivo Alterado"), pois uma importação com `status = FALHOU` não é considerada uma versão válida para efeito de detecção de repetição. |

## 4. Momento do Cálculo no Pipeline

O hash é calculado na **Etapa 1 (Upload)** do pipeline ETL (`ETL.md`), imediatamente após o recebimento do arquivo e antes do armazenamento em disco, permitindo recusar arquivos repetidos antes mesmo de gravar o binário em `importacao_arquivos`.

Exceção: o arquivo de uma importação classificada como "Arquivo Repetido" **não é armazenado** em `importacao_arquivos` nem gera novo registro de `carteiras`/`faturamentos`/etc. — apenas um registro de tentativa é mantido em `importacoes` com `status = FALHOU`, para fins de auditoria da tentativa (`LOGS.md`).

## 5. Cadeia de Versões

1. Cada `tipo_arquivo` possui sua própria sequência independente de `versao`, iniciando em 1.
2. A cadeia de versões é navegável em ambas as direções via `importacao_pai_id` (da mais recente para a mais antiga) e por consulta inversa (da mais antiga para a mais recente, filtrando por `importacao_pai_id`).
3. A interface de histórico de importações (`TELAS.md`, tela "Histórico de Importações") exibe a cadeia completa de versões de cada `tipo_arquivo`, com indicação visual da versão corrente (maior `versao` com `status IN ('CONCLUIDA', 'CONCLUIDA_COM_ERROS')`, não revertida).

## 6. Hash e Rollback

1. Reverter uma importação (`REGRAS_DE_NEGOCIO.md`, seção 6) não apaga seu registro de `hash_sha256` — o hash permanece associado à importação com `status = REVERTIDA`.
2. Consequência direta: reenviar exatamente o mesmo arquivo que foi revertido é tratado como **Arquivo Alterado (nova versão)**, não como duplicado, pois a importação revertida não é mais considerada "a versão vigente" para fins de comparação — apenas a comparação de hash contra importações com `status = REVERTIDA` é ignorada na regra de detecção de repetição da seção 3. Esta é uma decisão de negócio deliberada: permite reimportar deliberadamente um arquivo cuja versão foi revertida por engano.

## 7. Garantias de Integridade

1. O hash SHA-256 garante detecção de **qualquer** alteração de conteúdo binário do arquivo, incluindo alterações de formatação que não mudem valores visíveis (ex.: uma célula recalculada pelo Excel gerando bytes internos diferentes) — esta é uma limitação conhecida e aceita na POC: o hash detecta diferença de **arquivo**, não necessariamente diferença de **dado semântico**. A comparação semântica linha a linha entre versões é um item de evolução pós-POC (`ROADMAP.md`).
2. O hash é recalculado e conferido a cada leitura de auditoria de integridade (não há reuso de hash previamente calculado por outro arquivo).

## 8. Armazenamento do Arquivo Original

1. Todo arquivo aceito (classificado como Novo, Alterado ou Reenvio Pós-Falha) tem seu binário original preservado em disco, referenciado por `importacao_arquivos.caminho_armazenamento`, permitindo:
   - Auditoria completa (reabertura do arquivo original que gerou determinado conjunto de dados).
   - Rollback com possibilidade de reprocessamento manual, se necessário.
2. O nome de armazenamento em disco segue o padrão `{tipo_arquivo}_{importacao_id}_{hash_sha256_curto}.xlsx`, onde `hash_sha256_curto` são os primeiros 12 caracteres do hash, evitando colisão de nomes e mantendo rastreabilidade visual do arquivo no sistema de arquivos.
3. Detalhamento do diretório de armazenamento em `DEPLOY.md`.
