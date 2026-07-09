"""Middleware de log de requisição (LOGS.md, seção 5, item 1)."""

from __future__ import annotations

import logging
import time
import uuid

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("promotores_bi.requests")


class LoggingMiddleware:
    """Registra método, rota, status e tempo de execução de cada requisição."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        request_id = str(uuid.uuid4())
        inicio = time.monotonic()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                duracao_ms = round((time.monotonic() - inicio) * 1000, 2)
                logger.info(
                    "%s %s -> %s (%sms) [%s]",
                    request.method,
                    request.url.path,
                    message["status"],
                    duracao_ms,
                    request_id,
                    extra={"request_id": request_id},
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)
