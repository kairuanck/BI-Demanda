# SPRINT_07.md — Importador de Visitas e Checklists

## 1. Objetivo

Implementar os importadores de Visitas e de Checklists, incluindo o vínculo de respostas de checklist às visitas correspondentes e o cálculo automático de conformidade, completando o conjunto dos 5 importadores do sistema.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `IMPORTADOR.md` (seções 6 e 7), `VALIDADOR.md` (seções 3–5, 9 e 10), `REGRAS_DE_NEGOCIO.md` (seções 5.4 e 5.5), `DICIONARIO_DE_DADOS.md` (tabelas `visitas`, `checklists`, `checklist_perguntas`, `checklist_respostas`).

## 3. Pré-condições

Sprint 05 concluída (Visitas depende de Promotores e Clientes pré-existentes, `IMPORTADOR.md`, seção 8). Checklist depende de Visitas pré-existentes e de templates de `checklists`/`checklist_perguntas` previamente cadastrados (seção 4.1 abaixo).

## 4. Escopo (Backlog Detalhado)

### 4.1 Cadastro de Templates de Checklist (Pré-requisito Administrativo)
1. Implementar `app/repositories/checklist_repository.py` com métodos de leitura de template ativo por `tipo_promotor_alvo` e maior `versao`.
2. Implementar endpoints administrativos mínimos para cadastro de templates e perguntas (`POST /api/v1/checklists`, `POST /api/v1/checklists/{id}/perguntas`), necessários para que exista ao menos um template ativo antes de qualquer importação de respostas de Checklist ser válida. Estes endpoints não fazem parte de `API.md` como rota de dashboard, mas são pré-requisito operacional documentado nesta Sprint como extensão administrativa mínima de `API.md`, seção 6, sob o mesmo padrão de autorização (Administrador).
3. Implementar script de seed `app/infrastructure/seeds/seed_checklists_exemplo.py`, criando ao menos um template ativo por Tipo de Promotor, com perguntas de exemplo, para viabilizar os testes desta Sprint e a demonstração da POC.

### 4.2 Importador de Visitas
1. Implementar `app/services/importacao/validadores/validador_visitas.py`, aplicando `VIS-001` a `VIS-004` (`VALIDADOR.md`, seção 9) e `REF-002`/`REF-003`.
2. Implementar `app/services/importacao/importador_visitas.py`, implementando `ImportadorArquivo`, com persistência via inserção pura (append) por linha (`REGRAS_DE_NEGOCIO.md`, seção 5.5).
3. Registrar o importador no motor genérico, habilitando `POST /importacoes` com `tipo_arquivo = VISITAS`.
4. Implementar `app/repositories/visita_repository.py` com `buscar_por_promotor_periodo`, reutilizado pela Sprint 08.

### 4.3 Importador de Checklists
1. Implementar `app/services/importacao/validadores/validador_checklist.py`, aplicando `CHK-001` a `CHK-004` (`VALIDADOR.md`, seção 10) e `REF-004`/`REF-005`.
2. Implementar `app/services/importacao/importador_checklist.py`, implementando `ImportadorArquivo`:
   - Resolução de `ID_VISITA` (deve existir).
   - Resolução do template ativo correspondente ao `tipo_promotor_alvo` do promotor da visita, e da pergunta pelo `ORDEM_PERGUNTA` (`IMPORTADOR.md`, seção 6.2).
   - Cálculo automático de `conforme` para perguntas `SIM_NAO` (`REGRAS_DE_NEGOCIO.md`, seção 5.4, item 4).
   - Persistência via inserção de nova resposta vinculada à `importacao_id` corrente.
3. Registrar o importador no motor genérico, habilitando `POST /importacoes` com `tipo_arquivo = CHECKLIST`.
4. Implementar `app/repositories/checklist_resposta_repository.py`, reutilizado pela Sprint 08.

## 5. Fora de Escopo desta Sprint

1. Cálculo dos KPIs de Visitas e Checklists (`KPIS.md`, seções 6–7) — Sprint 08.
2. Tela administrativa completa de gestão de templates de Checklist no frontend — tratada como funcionalidade administrativa mínima via API nesta Sprint; interface visual completa é item de evolução pós-POC, não bloqueando o fluxo de importação de respostas.

## 6. Entregáveis

1. Importador de Visitas funcional de ponta a ponta.
2. Importador de Checklists funcional de ponta a ponta, incluindo cálculo de conformidade.
3. Endpoints mínimos de cadastro de template de Checklist e seed de exemplo.
4. Testes cobrindo os 5 tipos de importador agora completos, incluindo o cenário de dependência (Visitas antes de Checklist).

## 7. Critérios de Aceite

1. Upload de um arquivo de Visitas válido persiste corretamente todas as linhas, incluindo casos de `STATUS = CANCELADA`.
2. Upload de um arquivo de Checklist referenciando uma `ID_VISITA` inexistente gera erro `REF-004` e a linha não é persistida.
3. Resposta `SIM`/`NAO` a uma pergunta `SIM_NAO` calcula corretamente o campo `conforme` conforme o critério de conformidade cadastrado na pergunta.
4. Resposta duplicada para a mesma `ID_VISITA` + `ORDEM_PERGUNTA` no mesmo arquivo gera erro `CHK-004`.
5. Todos os 5 tipos de arquivo (`CLIENTES`, `CARTEIRA`, `FATURAMENTO`, `VISITAS`, `CHECKLIST`) estão registrados e funcionais no motor genérico ao final desta Sprint, validado por um teste de integração que executa a sequência completa descrita em `IMPORTADOR.md`, seção 8.
6. Meta de cobertura de testes da Sprint (`TESTES.md`, seção 7) atingida.

## 8. Riscos e Observações

1. Ao final desta Sprint, o conjunto completo de importadores está disponível — é o marco M2 do `ROADMAP.md`. Recomenda-se, antes de prosseguir à Sprint 08, uma validação manual exploratória do fluxo completo de importação das 5 planilhas em sequência, além dos testes automatizados.
