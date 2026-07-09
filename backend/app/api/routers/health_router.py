"""Endpoint de verificação de saúde (DEPLOY.md, seção 11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
def verificar_saude(db: Session = Depends(get_db_session)) -> dict[str, str]:
    """Retorna o status da aplicação e da conectividade com o banco."""

    database_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - health check nunca deve propagar exceção
        database_status = "erro"

    return {"status": "ok", "database": database_status}
