"""Composição de injeção de dependência da API (ver BACKEND.md, seção 6).

Escopo desta Sprint: apenas `get_db_session`, reexportada aqui como ponto
único de acesso da camada de API à sessão de banco. As dependências de
autenticação/autorização (`get_usuario_autenticado`, `exige_perfil`) são
implementadas na Sprint 02, conforme AUTENTICACAO.md e PERMISSOES.md.
"""

from __future__ import annotations

from app.infrastructure.database import get_db_session

__all__ = ["get_db_session"]
