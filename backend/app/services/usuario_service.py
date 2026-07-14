"""Usuário técnico usado enquanto não há autenticação (Sprint 3, CLI).

Extraído de `etl/cli.py` na Sprint 6 para ser compartilhado pelo endpoint
HTTP de upload — CLI e upload Web são igualmente não autenticados nesta
fase (AUTENTICACAO.md fica para sprint futura), então ambos registram as
importações sob o mesmo usuário de sistema (docs/DECISIONS.md).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import PerfilUsuario
from app.infrastructure.models import Usuario

EMAIL_USUARIO_SISTEMA = "sistema@promotoresbi.local"


def obter_ou_criar_usuario_sistema(session: Session) -> Usuario:
    """Usuário técnico para `usuario_id` enquanto não há autenticação (Sprint futura)."""

    usuario = session.scalar(select(Usuario).where(Usuario.email == EMAIL_USUARIO_SISTEMA))
    if usuario is None:
        usuario = Usuario(
            nome="Sistema (sem autenticação)",
            email=EMAIL_USUARIO_SISTEMA,
            senha_hash="!",  # login desabilitado; autenticação é sprint futura
            perfil=PerfilUsuario.ADMINISTRADOR,
        )
        session.add(usuario)
        session.commit()
    return usuario
