"""Log técnico do pipeline ETL (LOGS.md, seção 5, item 2).

Cada etapa do pipeline registra início/fim com `importacao_id` e tempo de
execução; falhas registram stack trace em ERROR.
"""

from __future__ import annotations

import logging

_LOGGER_ETL = "promotores_bi.etl"


def obter_logger_etl() -> logging.Logger:
    return logging.getLogger(_LOGGER_ETL)
