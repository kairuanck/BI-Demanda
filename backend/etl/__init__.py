"""Módulo ETL independente do Promotores BI (Sprint 2).

Estrutura em camadas (ETL.md):
- `readers/`      — leitura de arquivos Excel (Pandas/OpenPyXL)
- `transformers/` — normalização e conversão de valores
- `validators/`   — validação estrutural e linha a linha (VALIDADOR.md)
- `loaders/`      — persistência por tipo de arquivo (REGRAS_DE_NEGOCIO.md, seção 5)
- `hash/`         — SHA-256 e classificação de duplicidade (HASH.md)
- `logs/`         — log técnico do pipeline (LOGS.md, seção 5, item 2)
- `arquivos/`     — fluxo físico incoming → processed/rejected + archive
- `motor.py`      — orquestração das etapas e importadores registrados
"""
