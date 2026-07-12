"""Serviço de qualidade de dados (Sprint 3, Fase 6).

Calcula métricas objetivas sobre o estado atual do banco após a carga dos
dados reais — cobertura entre fontes, pendências de conciliação e
anomalias cadastrais — sem alterar nenhum dado (somente leitura). Alimenta
`docs/DATA_QUALITY.md`, sempre reportado de forma sanitizada (sem CNPJs,
nomes ou outros dados de negócio identificáveis).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.enums import StatusCarteira, StatusConciliacao
from app.infrastructure.models import (
    Carteira,
    CarteiraAvert,
    Cliente,
    ClienteIntegracao,
    Faturamento,
)


@dataclass
class RelatorioQualidadeDados:
    total_clientes: int
    clientes_com_faturamento: int
    clientes_com_carteira_ativa: int
    documentos_cnpj_cpf_compartilhados: int
    clientes_afetados_por_documento_compartilhado: int
    integracoes_pendentes_por_sistema: dict[str, int] = field(default_factory=dict)
    carteira_avert_total: int = 0
    carteira_avert_vinculada: int = 0

    @property
    def cobertura_faturamento_pct(self) -> float:
        return _percentual(self.clientes_com_faturamento, self.total_clientes)

    @property
    def cobertura_carteira_pct(self) -> float:
        return _percentual(self.clientes_com_carteira_ativa, self.total_clientes)

    @property
    def cobertura_carteira_avert_pct(self) -> float:
        return _percentual(self.carteira_avert_vinculada, self.carteira_avert_total)


def _percentual(parte: int, total: int) -> float:
    return round((parte / total) * 100, 2) if total else 0.0


def gerar_relatorio_qualidade(session: Session) -> RelatorioQualidadeDados:
    """Calcula o relatório completo em consultas somente-leitura."""

    total_clientes = session.scalar(select(func.count()).select_from(Cliente)) or 0

    clientes_com_faturamento = (
        session.scalar(select(func.count(func.distinct(Faturamento.cliente_id)))) or 0
    )

    clientes_com_carteira_ativa = (
        session.scalar(
            select(func.count(func.distinct(Carteira.cliente_id))).where(
                Carteira.status == StatusCarteira.ATIVA, Carteira.data_fim_vigencia.is_(None)
            )
        )
        or 0
    )

    documentos_compartilhados, clientes_afetados = _documentos_compartilhados(session)

    pendentes_por_sistema = {
        sistema.value: total
        for sistema, total in session.execute(
            select(ClienteIntegracao.sistema_origem, func.count())
            .where(ClienteIntegracao.status == StatusConciliacao.PENDENTE)
            .group_by(ClienteIntegracao.sistema_origem)
        ).all()
    }

    carteira_avert_total = session.scalar(select(func.count()).select_from(CarteiraAvert)) or 0
    carteira_avert_vinculada = (
        session.scalar(
            select(func.count())
            .select_from(CarteiraAvert)
            .where(CarteiraAvert.cliente_id.is_not(None))
        )
        or 0
    )

    return RelatorioQualidadeDados(
        total_clientes=total_clientes,
        clientes_com_faturamento=clientes_com_faturamento,
        clientes_com_carteira_ativa=clientes_com_carteira_ativa,
        documentos_cnpj_cpf_compartilhados=documentos_compartilhados,
        clientes_afetados_por_documento_compartilhado=clientes_afetados,
        integracoes_pendentes_por_sistema=pendentes_por_sistema,
        carteira_avert_total=carteira_avert_total,
        carteira_avert_vinculada=carteira_avert_vinculada,
    )


def _documentos_compartilhados(session: Session) -> tuple[int, int]:
    """Documentos (CNPJ/CPF) usados por mais de um cliente — e quantos clientes afeta.

    Cadastros distintos com o mesmo documento são uma anomalia herdada do
    ERP de origem (DATA_PROFILING.md, seção 2); a importação nunca funde
    nem descarta esses clientes — apenas reporta.
    """

    subconsulta = (
        select(Cliente.cnpj_cpf)
        .where(Cliente.cnpj_cpf.is_not(None))
        .group_by(Cliente.cnpj_cpf)
        .having(func.count() > 1)
    ).subquery()

    total_documentos = session.scalar(select(func.count()).select_from(subconsulta)) or 0
    total_clientes_afetados = (
        session.scalar(
            select(func.count())
            .select_from(Cliente)
            .where(Cliente.cnpj_cpf.in_(select(subconsulta.c.cnpj_cpf)))
        )
        or 0
    )
    return total_documentos, total_clientes_afetados
