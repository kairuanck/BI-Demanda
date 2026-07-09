# SPRINT_02.md — Autenticação e Usuários

## 1. Objetivo

Implementar autenticação JWT completa, hashing de senha com bcrypt, CRUD de usuários e o mecanismo de autorização por perfil (RBAC), habilitando o primeiro fluxo ponta a ponta protegido da aplicação.

## 2. Documentos de Referência Obrigatórios

`MASTER_PROMPT.md`, `AUTENTICACAO.md`, `PERMISSOES.md`, `API.md` (seções 4 e 5), `BACKEND.md`.

## 3. Pré-condições

Sprint 01 concluída (modelo `usuarios` disponível, repositório básico implementado).

## 4. Escopo (Backlog Detalhado)

### 4.1 Infraestrutura de Segurança
1. Implementar `app/infrastructure/security/password_hasher.py`: funções `gerar_hash(senha: str) -> str` e `verificar_senha(senha: str, hash: str) -> bool`, usando bcrypt com fator de custo 12 (`AUTENTICACAO.md`, seção 2).
2. Implementar `app/infrastructure/security/jwt_provider.py`: funções `gerar_access_token`, `gerar_refresh_token`, `validar_token`, conforme claims de `AUTENTICACAO.md`, seção 3.
3. Implementar mecanismo de revogação de `jti` de refresh tokens em memória de processo (`AUTENTICACAO.md`, seção 3.2), com estrutura testável e isolada (permitindo troca futura por armazenamento distribuído sem alterar a interface).

### 4.2 Serviço de Autenticação
1. Implementar `app/services/auth_service.py`: `autenticar(email, senha)`, `renovar_token(refresh_token)`, `revogar_sessao(refresh_token)`, implementando exatamente os fluxos de `AUTENTICACAO.md`, seções 4–6, incluindo o limite de tentativas (seção 9, item 1) e a atualização de `usuarios.ultimo_login_em`.
2. Cada operação relevante deste serviço dispara o registro de auditoria correspondente (`AUDITORIA.md`, seção 3), via `app/services/auditoria_service.py` (implementação inicial mínima, estendida em Sprints futuras).

### 4.3 Serviço de Usuários
1. Implementar `app/services/usuario_service.py`: `criar_usuario`, `atualizar_usuario`, `redefinir_senha`, `alterar_status`, `listar_usuarios`, aplicando as regras de `REGRAS_DE_NEGOCIO.md`, seção 3 (vínculo obrigatório a Promotor/Supervisor conforme perfil, unicidade de vínculo, inativação em vez de exclusão física).

### 4.4 Dependências de API (Autorização)
1. Implementar `Depends(get_usuario_autenticado)` em `app/api/dependencies.py`, conforme `AUTENTICACAO.md`, seção 7.
2. Implementar `Depends(exige_perfil(*perfis))`, aplicando a matriz de `PERMISSOES.md`, seção 3.
3. Implementar o manipulador global de exceções para `401`/`403` no formato padrão de `API.md`, seção 13.

### 4.5 Endpoints de API
1. `app/api/routers/auth_router.py`: `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me` (`API.md`, seção 4).
2. `app/api/routers/usuarios_router.py`: `GET /usuarios`, `POST /usuarios`, `GET /usuarios/{id}`, `PUT /usuarios/{id}`, `PATCH /usuarios/{id}/senha`, `PATCH /usuarios/{id}/status` (`API.md`, seção 5), todos protegidos por `exige_perfil(ADMINISTRADOR)`.
3. Schemas Pydantic de request/response em `app/api/schemas/auth_schema.py` e `app/api/schemas/usuario_schema.py`, incluindo validação de política de senha (`AUTENTICACAO.md`, seção 8).

### 4.6 Seed de Usuário Administrador
1. Implementar `app/infrastructure/seeds/seed_admin.py`, criando o usuário Administrador inicial conforme `AUTENTICACAO.md`, seção 11.

## 5. Fora de Escopo desta Sprint

1. Fluxo de "esqueci minha senha" autoatendido (`AUTENTICACAO.md`, seção 8, item 3) — fora do escopo da POC.
2. Tela de login no frontend — Sprint 09.
3. Importação de arquivos — Sprint 03 em diante.

## 6. Entregáveis

1. Fluxo completo de login/refresh/logout funcionando via `TestClient`/Swagger UI.
2. CRUD de usuários funcionando, respeitando as regras de vínculo por perfil.
3. Mecanismo de autorização por perfil aplicável a qualquer rota futura via `Depends(exige_perfil(...))`.
4. Seed do usuário Administrador inicial.
5. Testes unitários e de integração cobrindo os fluxos de `AUTENTICACAO.md` e a matriz de `PERMISSOES.md`.

## 7. Critérios de Aceite

1. `POST /api/v1/auth/login` com credenciais válidas retorna `200` com `access_token` e `refresh_token` válidos; com credenciais inválidas retorna `401` com código `CREDENCIAIS_INVALIDAS`, sem distinguir usuário inexistente de senha incorreta.
2. `POST /api/v1/auth/refresh` com refresh token válido retorna novo `access_token`; com token revogado ou expirado retorna `401`.
3. Rotas protegidas retornam `401` sem token e `403` quando o perfil do usuário autenticado não atende à exigência da rota, conforme a matriz de `PERMISSOES.md`, seção 6.
4. Criação de usuário com `perfil = PROMOTOR` sem `promotor_id` é rejeitada com `422`.
5. Após 5 tentativas de login falhas para o mesmo e-mail em 15 minutos, a sexta tentativa retorna `429`.
6. Toda senha persistida em `usuarios.senha_hash` está no formato bcrypt (`$2b$...`), nunca em texto puro, verificado por teste que inspeciona diretamente o banco de teste.
7. Login, logout e alterações de usuário geram os registros de auditoria correspondentes (`AUDITORIA.md`, seção 3).

## 8. Riscos e Observações

1. A revogação de refresh tokens em memória de processo (item 4.1.3) implica que reiniciar o processo do backend invalida silenciosamente a lista de revogados — comportamento aceito na POC e documentado como limitação conhecida, sem impacto de segurança relevante (tokens revogados eram, de qualquer forma, destinados a expirar naturalmente).
