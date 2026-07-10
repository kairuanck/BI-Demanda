"""Modelos SQLAlchemy — mapeiam exatamente DICIONARIO_DE_DADOS.md.

Importar este módulo garante que todos os modelos estejam registrados em
`Base.metadata` antes de qualquer `alembic revision --autogenerate`.
"""

from __future__ import annotations

from app.infrastructure.models.carteira_model import Carteira
from app.infrastructure.models.checklist_model import Checklist
from app.infrastructure.models.checklist_pergunta_model import ChecklistPergunta
from app.infrastructure.models.checklist_resposta_model import ChecklistResposta
from app.infrastructure.models.cidade_model import Cidade
from app.infrastructure.models.cliente_model import Cliente
from app.infrastructure.models.departamento_model import Departamento
from app.infrastructure.models.empresa_model import Empresa
from app.infrastructure.models.faturamento_model import Faturamento
from app.infrastructure.models.importacao_arquivo_model import ImportacaoArquivo
from app.infrastructure.models.importacao_erro_model import ImportacaoErro
from app.infrastructure.models.importacao_model import Importacao
from app.infrastructure.models.laboratorio_model import Laboratorio
from app.infrastructure.models.log_auditoria_model import LogAuditoria
from app.infrastructure.models.promotor_model import Promotor
from app.infrastructure.models.supervisor_model import Supervisor
from app.infrastructure.models.uf_model import Uf
from app.infrastructure.models.usuario_model import Usuario
from app.infrastructure.models.vendedor_model import Vendedor
from app.infrastructure.models.visita_model import Visita

__all__ = [
    "Carteira",
    "Checklist",
    "ChecklistPergunta",
    "ChecklistResposta",
    "Cidade",
    "Cliente",
    "Departamento",
    "Empresa",
    "Faturamento",
    "ImportacaoArquivo",
    "ImportacaoErro",
    "Importacao",
    "Laboratorio",
    "LogAuditoria",
    "Promotor",
    "Supervisor",
    "Uf",
    "Usuario",
    "Vendedor",
    "Visita",
]
