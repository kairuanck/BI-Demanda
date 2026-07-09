"""Testes do endpoint de verificação de saúde (DEPLOY.md, seção 11)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_retorna_ok_e_banco_conectado(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "database": "ok"}
