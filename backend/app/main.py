"""Ponto de entrada da aplicação FastAPI (ver BACKEND.md, seção 4)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import registrar_error_handlers
from app.api.middlewares.logging_middleware import LoggingMiddleware
from app.api.routers.cliente_router import router as cliente_router
from app.api.routers.dashboard_router import router as dashboard_router
from app.api.routers.health_router import router as health_router
from app.api.routers.importacoes_router import router as importacoes_router
from app.core.config import get_settings
from app.core.logging import configurar_logging

settings = get_settings()
configurar_logging(settings.log_level)

app = FastAPI(
    title="Promotores BI",
    description="API do Promotores BI — plataforma de BI para gestão de promotores.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

registrar_error_handlers(app)

app.include_router(health_router, prefix="/api/v1")
app.include_router(importacoes_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(cliente_router, prefix="/api/v1")
