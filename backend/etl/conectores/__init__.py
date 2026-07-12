"""Conectores de origem — Strategy Pattern da Sprint 3 (docs/DECISIONS.md, 11.6).

Cada sistema de origem (SB Promotor, WeCheck, Painel Avert, ERP) tem seu
conector, que encapsula leitura, transformação wide→long, validação e
carga. Todos alimentam o MESMO modelo de domínio — nenhuma regra
específica de sistema vaza para fora deste pacote.
"""

from __future__ import annotations

from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.checklist_sb import ConectorChecklistSb
from etl.conectores.clientes import ConectorBaseClientes
from etl.conectores.faturamento import ConectorFaturamentoMatriz
from etl.conectores.legado import ConectorLegado
from etl.conectores.painel_avert import ConectorPainelAvert
from etl.conectores.sb_produtos import ConectorSbProdutos
from etl.conectores.sb_supervisor import ConectorSbSupervisor
from etl.conectores.wecheck import ConectorWeCheck

__all__ = [
    "ConectorOrigem",
    "ExecucaoImportacao",
    "ResultadoConector",
    "ConectorBaseClientes",
    "ConectorChecklistSb",
    "ConectorFaturamentoMatriz",
    "ConectorLegado",
    "ConectorPainelAvert",
    "ConectorSbProdutos",
    "ConectorSbSupervisor",
    "ConectorWeCheck",
]
