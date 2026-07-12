"""Identidade interna das entidades (Sprint 3, ver docs/DECISIONS.md, seção 13).

Diretriz de arquitetura definida pelo negócio na Sprint 3:
- Nunca usar identificadores naturais como chave primária.
- UUID interno em todas as entidades; códigos de sistemas externos são
  apenas identificadores de integração (`codigo_externo` / `codigo_origem`).
- Persistido como String(36) para compatibilidade SQLite ↔ PostgreSQL.

Exceção documentada: `ufs` mantém `sigla` como PK por ser tabela de
referência geográfica estática (código oficial imutável, não identidade
de negócio).
"""

from __future__ import annotations

import uuid

UUID_TAMANHO = 36


def novo_uuid() -> str:
    """Gera o identificador interno padrão (UUID v4 canônico em texto)."""

    return str(uuid.uuid4())
