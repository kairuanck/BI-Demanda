# AUTENTICACAO.md — Autenticação

## 1. Finalidade

Este documento especifica o mecanismo de autenticação do Promotores BI, baseado em **JWT (JSON Web Token)** para autenticação stateless da API e **bcrypt** para hashing de senhas. O controle de autorização por perfil (o que cada perfil autenticado pode fazer) está em `PERMISSOES.md`.

## 2. Armazenamento de Senha

1. Senhas nunca são armazenadas em texto puro.
2. O hash é calculado com **bcrypt** (biblioteca `passlib[bcrypt]` ou `bcrypt` diretamente), fator de custo (`cost factor`) igual a `12`.
3. O valor armazenado em `usuarios.senha_hash` inclui o salt (formato padrão do bcrypt: `$2b$12$...`), dispensando coluna de salt separada.
4. Toda comparação de senha em login utiliza a função de verificação do bcrypt (`bcrypt.checkpw` ou equivalente do `passlib`), nunca comparação direta de strings.

## 3. Estrutura do Token JWT

### 3.1 Access Token
- Algoritmo de assinatura: `HS256`.
- Chave secreta: variável de ambiente `JWT_SECRET_KEY` (`DEPLOY.md`).
- Tempo de vida: 30 minutos.
- Claims:
  ```json
  {
    "sub": "123",
    "email": "usuario@empresa.com.br",
    "perfil": "SUPERVISOR",
    "promotor_id": null,
    "supervisor_id": 7,
    "tipo": "access",
    "iat": 1770000000,
    "exp": 1770001800
  }
  ```

### 3.2 Refresh Token
- Algoritmo de assinatura: `HS256`, com chave secreta distinta (`JWT_REFRESH_SECRET_KEY`).
- Tempo de vida: 7 dias.
- Claims mínimos: `sub` (id do usuário), `tipo: "refresh"`, `iat`, `exp`, `jti` (identificador único do token, para permitir invalidação em logout).
- O `jti` de refresh tokens ativos é registrado em uma tabela de sessão em memória/processo simples para a POC (invalidação em `logout` marca o `jti` como revogado); estratégia de invalidação distribuída (ex.: Redis) é item de evolução pós-POC (`ROADMAP.md`).

## 4. Fluxo de Login

1. Cliente envia `POST /api/v1/auth/login` com `{ "email": ..., "senha": ... }`.
2. `AuthService` busca o usuário por e-mail via `UsuarioRepository`.
3. Se o usuário não existir, ou estiver `ativo = false`, ou a senha não corresponder ao hash armazenado, a API retorna `401` com código `CREDENCIAIS_INVALIDAS`, sem indicar qual dos três motivos ocorreu (mitigação de enumeração de usuários).
4. Se as credenciais forem válidas, o serviço:
   - Atualiza `usuarios.ultimo_login_em`.
   - Gera `access_token` e `refresh_token`.
   - Registra um evento em `logs_auditoria` com `acao = LOGIN`.
   - Retorna `200` com `{ "access_token": ..., "refresh_token": ..., "token_type": "bearer", "expires_in": 1800 }`.

## 5. Fluxo de Renovação (Refresh)

1. Cliente envia `POST /api/v1/auth/refresh` com `{ "refresh_token": ... }`.
2. O backend valida a assinatura, expiração e se o `jti` não foi revogado.
3. Se válido, um novo `access_token` é emitido (o `refresh_token` original permanece válido até sua expiração natural — rotação de refresh token é item de evolução pós-POC).
4. Se inválido/expirado/revogado, retorna `401` com código `TOKEN_INVALIDO`.

## 6. Fluxo de Logout

1. Cliente envia `POST /api/v1/auth/logout` com o `refresh_token` corrente.
2. O `jti` do refresh token é marcado como revogado.
3. Um evento é registrado em `logs_auditoria` com `acao = LOGOUT`.
4. O `access_token` corrente permanece tecnicamente válido até sua expiração natural (máximo 30 minutos), por ser stateless — limitação aceita na POC.

## 7. Proteção de Rotas

1. Toda rota protegida declara a dependência `Depends(get_usuario_autenticado)` (`BACKEND.md`, `api/dependencies.py`), que:
   - Extrai o `access_token` do header `Authorization: Bearer <token>`.
   - Valida assinatura e expiração.
   - Carrega o usuário correspondente ao `sub`, verificando `ativo = true`.
   - Injeta o usuário autenticado (com `perfil`, `promotor_id`, `supervisor_id`) no contexto da requisição.
2. A ausência ou invalidade do token resulta em `401` com código `NAO_AUTENTICADO`.
3. A autorização por perfil (o que o usuário autenticado pode acessar) é aplicada em uma segunda camada de dependência, detalhada em `PERMISSOES.md`.

## 8. Política de Senhas

1. Senha mínima de 8 caracteres, exigindo ao menos uma letra e um número (validação na criação/redefinição de usuário, `api/schemas/usuario_schema.py`).
2. Não há, na POC, expiração forçada de senha nem histórico de senhas anteriores — itens de evolução pós-POC.
3. Redefinição de senha é realizada exclusivamente pelo Administrador (`PATCH /api/v1/usuarios/{id}/senha`, `API.md`), não havendo fluxo de "esqueci minha senha" autoatendido na POC (autoatendimento via e-mail é item de evolução pós-POC, dependente de infraestrutura de envio de e-mail fora do escopo atual).

## 9. Proteção Contra Ataques Comuns

1. **Força bruta de login:** limite de 5 tentativas falhas por `email` em uma janela de 15 minutos, com bloqueio temporário (HTTP `429`), implementado em memória de processo para a POC.
2. **Enumeração de usuários:** mensagens de erro de login não distinguem "usuário inexistente" de "senha incorreta" (seção 4, item 3).
3. **Vazamento de segredo:** `JWT_SECRET_KEY` e `JWT_REFRESH_SECRET_KEY` são obrigatoriamente lidos de variável de ambiente, nunca hardcoded, e nunca commitados (`DEPLOY.md`, `GITHUB.md`).
4. **Token em log:** conforme `LOGS.md`, seção 8, tokens nunca são gravados integralmente em log técnico.

## 10. Integração com Perfis de Domínio

Os claims `perfil`, `promotor_id` e `supervisor_id` embutidos no `access_token` são a base para a resolução de escopo de dados descrita em `PERMISSOES.md` — evitando uma consulta adicional ao banco a cada requisição apenas para determinar o escopo de acesso do usuário.

## 11. Seed Inicial

A Sprint 01/02 (`SPRINT_02.md`) cria, via script de seed, um usuário Administrador inicial:
- E-mail: `admin@promotoresbi.local`
- Senha: gerada aleatoriamente e exibida uma única vez no console na execução do seed, exigindo redefinição no primeiro acesso (flag de "senha temporária" tratada na camada de aplicação via comparação de `criado_em` == `atualizado_em`, sem necessidade de coluna adicional na POC).
