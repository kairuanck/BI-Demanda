"""Serviço do Dashboard Executivo (Sprint 4, ver docs/DECISIONS.md, seções 16-19).

Todos os KPIs e séries são resolvidos com agregações SQL (GROUP BY/SUM/COUNT)
diretamente sobre as tabelas de fato — nunca carregando entidades para somar
em Python, exceto o Índice de Desempenho (Ranking), que combina métricas já
agregadas por promotor em memória (dezenas de promotores na base real).

Nenhuma consulta filtra por `importacoes.status`: o motor de importação só
persiste linhas de domínio dentro de uma importação bem-sucedida
(`REGRAS_DE_NEGOCIO.md`, seção 7; docs/DECISIONS.md, seção 17).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, and_, case, false, func, or_, select
from sqlalchemy.orm import Session

from app.domain.enums import SistemaOrigem, StatusCarteira, StatusVisita, TipoRespostaChecklist
from app.domain.excecoes import RegistroNaoEncontradoError
from app.infrastructure.models import (
    Carteira,
    CarteiraAvert,
    Checklist,
    ChecklistPergunta,
    ChecklistResposta,
    Cliente,
    Faturamento,
    Importacao,
    Laboratorio,
    Promotor,
    Supervisor,
    TipoPromotorCadastro,
    Uf,
    Visita,
)

_PESO_COBERTURA = Decimal("0.35")
_PESO_POSITIVACAO = Decimal("0.35")
_PESO_CONFORMIDADE = Decimal("0.20")
_PESO_VISITAS = Decimal("0.10")


@dataclass(frozen=True)
class FiltrosDashboard:
    """Filtros globais (Sprint 4). Todos opcionais e combináveis (AND)."""

    ano: int | None = None
    mes: int | None = None
    uf_sigla: str | None = None
    laboratorio_id: str | None = None
    tipo_promotor_id: str | None = None
    sistema_origem: SistemaOrigem | None = None
    supervisor_id: str | None = None
    promotor_id: str | None = None

    @property
    def escopo_promotor_ativo(self) -> bool:
        """Algum filtro que restringe a um subconjunto de promotores."""

        return bool(self.tipo_promotor_id or self.supervisor_id or self.promotor_id)

    @property
    def escopo_carteira_ativo(self) -> bool:
        """Algum filtro que exige restringir clientes à(s) carteira(s)."""

        return self.escopo_promotor_ativo or self.sistema_origem is not None


@dataclass
class OpcoesFiltro:
    anos: list[int]
    ufs: list[dict[str, str]]
    laboratorios: list[dict[str, str]]
    tipos_promotor: list[dict[str, str]]
    sistemas_origem: list[str]
    supervisores: list[dict[str, str]]
    promotores: list[dict[str, str]]


@dataclass
class KpisDashboard:
    faturamento_total: Decimal
    faturamento_carteira: Decimal
    faturamento_regiao: Decimal | None
    faturamento_fora_carteira: Decimal | None
    quantidade_clientes: int
    clientes_positivados: int
    cobertura_carteira: Decimal | None
    numero_visitas: int
    numero_checklists: int


@dataclass
class PontoSerieMensal:
    ano: int
    mes: int
    valor: Decimal


@dataclass
class PontoPositivacaoMensal:
    ano: int
    mes: int
    clientes_positivados_carteira: int
    clientes_positivados_regiao: int
    clientes_positivados_fora_carteira: int


@dataclass
class PontoCategoria:
    rotulo: str
    valor: Decimal


@dataclass
class PontoRankingPromotor:
    promotor_id: str
    nome: str
    indice_desempenho: Decimal | None
    cobertura: Decimal | None
    positivacao: Decimal | None


@dataclass
class PontoUF:
    uf_sigla: str
    faturamento_total: Decimal
    quantidade_clientes: int


@dataclass
class LinhaPromotor:
    promotor_id: str
    nome: str
    tipo: str | None
    supervisor: str | None
    sistema_origem: str | None
    quantidade_clientes: int
    numero_visitas: int
    numero_checklists: int
    cobertura_carteira: Decimal | None
    faturamento_carteira: Decimal
    faturamento_regiao: Decimal


@dataclass
class PaginaPromotores:
    itens: list[LinhaPromotor]
    total_itens: int


@dataclass
class DetalhePromotor:
    promotor_id: str
    nome: str
    tipo: str | None
    supervisor: str | None
    codigo_externo: str | None
    area: str | None
    kpis: KpisDashboard
    conformidade_checklist: Decimal | None
    indice_desempenho: Decimal | None
    evolucao_faturamento: list[PontoSerieMensal]
    faturamento_por_laboratorio: list[PontoCategoria]


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------ filtros

    def obter_opcoes_filtro(self) -> OpcoesFiltro:
        anos_fat = self.session.scalars(
            select(Faturamento.ano).distinct().order_by(Faturamento.ano.desc())
        ).all()
        anos_cart = self.session.scalars(
            select(func.strftime("%Y", Carteira.competencia)).where(
                Carteira.competencia.is_not(None)
            )
        ).all()
        anos = sorted({*anos_fat, *(int(a) for a in anos_cart if a)}, reverse=True)

        ufs = [
            {"sigla": sigla, "nome": nome}
            for sigla, nome in self.session.execute(
                select(Uf.sigla, Uf.nome)
                .where(Uf.sigla.in_(select(Cliente.uf_sigla).distinct()))
                .order_by(Uf.nome)
            ).all()
        ]
        laboratorios = [
            {"id": id_, "nome": nome}
            for id_, nome in self.session.execute(
                select(Laboratorio.id, Laboratorio.nome).order_by(Laboratorio.nome)
            ).all()
        ]
        tipos_promotor = [
            {"id": id_, "nome": nome}
            for id_, nome in self.session.execute(
                select(TipoPromotorCadastro.id, TipoPromotorCadastro.nome).order_by(
                    TipoPromotorCadastro.nome
                )
            ).all()
        ]
        supervisores = [
            {"id": id_, "nome": nome}
            for id_, nome in self.session.execute(
                select(Supervisor.id, Supervisor.nome)
                .where(Supervisor.id.in_(select(Promotor.supervisor_id).distinct()))
                .order_by(Supervisor.nome)
            ).all()
        ]
        promotores = [
            {"id": id_, "nome": nome}
            for id_, nome in self.session.execute(
                select(Promotor.id, Promotor.nome).order_by(Promotor.nome)
            ).all()
        ]
        return OpcoesFiltro(
            anos=anos,
            ufs=ufs,
            laboratorios=laboratorios,
            tipos_promotor=tipos_promotor,
            sistemas_origem=[s.value for s in SistemaOrigem],
            supervisores=supervisores,
            promotores=promotores,
        )

    # ------------------------------------------------------ escopo/subqueries

    def _promotor_ids_filtrados(self, filtros: FiltrosDashboard) -> Select[Any]:
        consulta = select(Promotor.id)
        if filtros.tipo_promotor_id:
            consulta = consulta.where(Promotor.tipo_promotor_id == filtros.tipo_promotor_id)
        if filtros.supervisor_id:
            consulta = consulta.where(Promotor.supervisor_id == filtros.supervisor_id)
        if filtros.promotor_id:
            consulta = consulta.where(Promotor.id == filtros.promotor_id)
        return consulta

    def _carteira_sb_cliente_ids(self, filtros: FiltrosDashboard) -> Select[Any]:
        """Clientes com carteira SB vigente (docs/DECISIONS.md, 16/18)."""

        if filtros.sistema_origem in (SistemaOrigem.WECHECK, SistemaOrigem.PAINEL_AVERT):
            return select(Carteira.cliente_id).where(false())
        consulta = select(Carteira.cliente_id).where(
            Carteira.status == StatusCarteira.ATIVA, Carteira.data_fim_vigencia.is_(None)
        )
        if filtros.escopo_promotor_ativo:
            consulta = consulta.where(
                Carteira.promotor_id.in_(self._promotor_ids_filtrados(filtros))
            )
        return consulta

    def _carteira_avert_cliente_ids(self, filtros: FiltrosDashboard) -> Select[Any]:
        """Clientes com carteira Avert (docs/DECISIONS.md, 16/18) — painel único, sem vigência."""

        if filtros.sistema_origem == SistemaOrigem.SB_PROMOTOR:
            return select(CarteiraAvert.cliente_id).where(false())
        consulta = select(CarteiraAvert.cliente_id).where(CarteiraAvert.cliente_id.is_not(None))
        if filtros.escopo_promotor_ativo:
            consulta = consulta.where(
                CarteiraAvert.promotor_id.in_(self._promotor_ids_filtrados(filtros))
            )
        return consulta

    def _clientes_elegiveis_ids(self, filtros: FiltrosDashboard) -> Select[Any]:
        """Universo de clientes considerado pelos filtros de dimensão + escopo."""

        consulta: Select[Any] = select(Cliente.id)
        if filtros.uf_sigla:
            consulta = consulta.where(Cliente.uf_sigla == filtros.uf_sigla)
        if filtros.escopo_carteira_ativo:
            consulta = consulta.where(
                or_(
                    Cliente.id.in_(self._carteira_sb_cliente_ids(filtros)),
                    Cliente.id.in_(self._carteira_avert_cliente_ids(filtros)),
                )
            )
        return consulta

    def _faturamento_query(
        self, filtros: FiltrosDashboard, cliente_ids: Select[Any] | None
    ) -> Select[tuple[Any, ...]]:
        consulta = select(Faturamento)
        if filtros.ano:
            consulta = consulta.where(Faturamento.ano == filtros.ano)
        if filtros.mes:
            consulta = consulta.where(Faturamento.mes == filtros.mes)
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        if cliente_ids is not None:
            consulta = consulta.where(Faturamento.cliente_id.in_(cliente_ids))
        return consulta

    def _soma_faturamento(
        self, filtros: FiltrosDashboard, cliente_ids: Select[Any] | None
    ) -> Decimal:
        subconsulta = self._faturamento_query(filtros, cliente_ids).subquery()
        consulta = select(func.coalesce(func.sum(subconsulta.c.valor_faturado), 0))
        return self.session.scalar(consulta) or Decimal("0")

    def _visitas_query(self, filtros: FiltrosDashboard) -> Select[tuple[Any, ...]]:
        consulta = select(Visita)
        if filtros.ano:
            consulta = consulta.where(func.strftime("%Y", Visita.data_visita) == str(filtros.ano))
        if filtros.mes:
            consulta = consulta.where(
                func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"
            )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        if filtros.escopo_promotor_ativo:
            consulta = consulta.where(Visita.promotor_id.in_(self._promotor_ids_filtrados(filtros)))
        if filtros.uf_sigla:
            consulta = consulta.join(Cliente, Cliente.id == Visita.cliente_id).where(
                Cliente.uf_sigla == filtros.uf_sigla
            )
        return consulta

    # ---------------------------------------------------------------- kpis

    def calcular_kpis(self, filtros: FiltrosDashboard) -> KpisDashboard:
        clientes_elegiveis = self._clientes_elegiveis_ids(filtros)
        faturamento_total = self._soma_faturamento(filtros, clientes_elegiveis)

        carteira_ids = self._com_uf(self._carteira_sb_cliente_ids(filtros), filtros)
        faturamento_carteira = self._soma_faturamento(filtros, carteira_ids)

        regiao_ids = self._com_uf(self._carteira_avert_cliente_ids(filtros), filtros)
        faturamento_regiao = (
            None
            if filtros.sistema_origem == SistemaOrigem.SB_PROMOTOR
            else self._soma_faturamento(filtros, regiao_ids)
        )

        faturamento_fora = self._faturamento_fora_carteira(filtros)

        quantidade_clientes = (
            self.session.scalar(select(func.count()).select_from(clientes_elegiveis.subquery()))
            or 0
        )

        clientes_positivados = self._contar_positivados(filtros, clientes_elegiveis)

        cobertura = self._cobertura_carteira(filtros)

        numero_visitas = (
            self.session.scalar(
                select(func.count()).select_from(self._visitas_query(filtros).subquery())
            )
            or 0
        )

        checklist_consulta = self._checklist_respostas_query(filtros)
        numero_checklists = (
            self.session.scalar(select(func.count()).select_from(checklist_consulta.subquery()))
            or 0
        )

        return KpisDashboard(
            faturamento_total=faturamento_total,
            faturamento_carteira=faturamento_carteira,
            faturamento_regiao=faturamento_regiao,
            faturamento_fora_carteira=faturamento_fora,
            quantidade_clientes=quantidade_clientes,
            clientes_positivados=clientes_positivados,
            cobertura_carteira=cobertura,
            numero_visitas=numero_visitas,
            numero_checklists=numero_checklists,
        )

    def _com_uf(self, cliente_ids: Select[Any], filtros: FiltrosDashboard) -> Select[Any]:
        if not filtros.uf_sigla:
            return cliente_ids
        resultado: Select[Any] = select(Cliente.id).where(
            Cliente.id.in_(cliente_ids), Cliente.uf_sigla == filtros.uf_sigla
        )
        return resultado

    def _faturamento_fora_carteira(self, filtros: FiltrosDashboard) -> Decimal | None:
        """KPIS.md, seção 5: não aplicável com filtro de promotor/supervisor/tipo."""

        if filtros.escopo_promotor_ativo:
            return None
        fora: Select[Any] = select(Cliente.id).where(
            Cliente.id.notin_(self._carteira_sb_cliente_ids(filtros)),
            Cliente.id.notin_(self._carteira_avert_cliente_ids(filtros)),
        )
        return self._soma_faturamento(filtros, self._com_uf(fora, filtros))

    def _contar_positivados(self, filtros: FiltrosDashboard, cliente_ids: Select[Any]) -> int:
        base = self._faturamento_query(filtros, cliente_ids).subquery()
        agrupado = (
            select(base.c.cliente_id)
            .group_by(base.c.cliente_id)
            .having(func.sum(base.c.valor_faturado) > 0)
        )
        return self.session.scalar(select(func.count()).select_from(agrupado.subquery())) or 0

    def _cobertura_carteira(self, filtros: FiltrosDashboard) -> Decimal | None:
        """KPIS.md, seção 8, restrita à carteira SB (docs/DECISIONS.md, 18).

        Uma visita só cobre o cliente quando feita pelo promotor titular
        daquele vínculo de carteira — mesma regra usada pela tabela de
        promotores (`_promotores_com_metricas`, `cobertura_visitados`).
        Sem esse vínculo, a visita de um promotor a um cliente que também
        pertence à carteira de outro promotor inflaria a cobertura deste
        último.
        """

        if filtros.sistema_origem in (SistemaOrigem.WECHECK, SistemaOrigem.PAINEL_AVERT):
            return None
        carteira_ids = self._com_uf(self._carteira_sb_cliente_ids(filtros), filtros)
        total = self.session.scalar(select(func.count()).select_from(carteira_ids.subquery())) or 0
        if total == 0:
            return None

        consulta_cobertos = (
            select(func.count(func.distinct(Carteira.cliente_id)))
            .select_from(Carteira)
            .join(
                Visita,
                and_(
                    Visita.cliente_id == Carteira.cliente_id,
                    Visita.promotor_id == Carteira.promotor_id,
                    Visita.status == StatusVisita.REALIZADA,
                ),
            )
            .where(
                Carteira.status == StatusCarteira.ATIVA,
                Carteira.data_fim_vigencia.is_(None),
                Carteira.cliente_id.in_(carteira_ids),
            )
        )
        if filtros.escopo_promotor_ativo:
            consulta_cobertos = consulta_cobertos.where(
                Carteira.promotor_id.in_(self._promotor_ids_filtrados(filtros))
            )
        if filtros.ano:
            consulta_cobertos = consulta_cobertos.where(
                func.strftime("%Y", Visita.data_visita) == str(filtros.ano)
            )
        if filtros.mes:
            consulta_cobertos = consulta_cobertos.where(
                func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"
            )
        cobertos = self.session.scalar(consulta_cobertos) or 0
        return Decimal(cobertos) / Decimal(total)

    def _checklist_respostas_query(self, filtros: FiltrosDashboard) -> Select[tuple[Any, ...]]:
        consulta = select(ChecklistResposta).join(Visita, Visita.id == ChecklistResposta.visita_id)
        if filtros.ano:
            consulta = consulta.where(func.strftime("%Y", Visita.data_visita) == str(filtros.ano))
        if filtros.mes:
            consulta = consulta.where(
                func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"
            )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        if filtros.escopo_promotor_ativo:
            consulta = consulta.where(Visita.promotor_id.in_(self._promotor_ids_filtrados(filtros)))
        if filtros.uf_sigla:
            consulta = consulta.join(Cliente, Cliente.id == Visita.cliente_id).where(
                Cliente.uf_sigla == filtros.uf_sigla
            )
        return consulta

    # ------------------------------------------------------------ gráficos

    def evolucao_faturamento_mensal(self, filtros: FiltrosDashboard) -> list[PontoSerieMensal]:
        clientes_elegiveis = self._clientes_elegiveis_ids(filtros)
        consulta = (
            select(
                Faturamento.ano,
                Faturamento.mes,
                func.coalesce(func.sum(Faturamento.valor_faturado), 0),
            )
            .where(Faturamento.cliente_id.in_(clientes_elegiveis))
            .group_by(Faturamento.ano, Faturamento.mes)
            .order_by(Faturamento.ano, Faturamento.mes)
        )
        if filtros.ano:
            consulta = consulta.where(Faturamento.ano == filtros.ano)
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        return [
            PontoSerieMensal(ano=ano, mes=mes, valor=valor or Decimal("0"))
            for ano, mes, valor in self.session.execute(consulta).all()
        ]

    def evolucao_positivacao_mensal(
        self, filtros: FiltrosDashboard
    ) -> list[PontoPositivacaoMensal]:
        """Clientes positivados por mês, segmentados por Carteira/Região/Fora."""

        carteira_ids = self._com_uf(self._carteira_sb_cliente_ids(filtros), filtros)
        regiao_ids = self._com_uf(self._carteira_avert_cliente_ids(filtros), filtros)
        fora_ids: Select[Any] = select(Cliente.id).where(
            Cliente.id.notin_(self._carteira_sb_cliente_ids(filtros)),
            Cliente.id.notin_(self._carteira_avert_cliente_ids(filtros)),
        )
        fora_ids = self._com_uf(fora_ids, filtros)

        meses: dict[tuple[int, int], dict[str, int]] = {}
        for rotulo, grupo_ids in (
            ("carteira", carteira_ids),
            ("regiao", regiao_ids),
            ("fora_carteira", fora_ids),
        ):
            base = self._faturamento_query(filtros, grupo_ids).subquery()
            positivados_mes = (
                select(base.c.ano, base.c.mes, base.c.cliente_id)
                .group_by(base.c.ano, base.c.mes, base.c.cliente_id)
                .having(func.sum(base.c.valor_faturado) > 0)
                .subquery()
            )
            resultado = self.session.execute(
                select(positivados_mes.c.ano, positivados_mes.c.mes, func.count()).group_by(
                    positivados_mes.c.ano, positivados_mes.c.mes
                )
            ).all()
            for ano, mes, contagem in resultado:
                chave = (ano, mes)
                meses.setdefault(
                    chave,
                    {"carteira": 0, "regiao": 0, "fora_carteira": 0},
                )[rotulo] = contagem

        return [
            PontoPositivacaoMensal(
                ano=ano,
                mes=mes,
                clientes_positivados_carteira=valores["carteira"],
                clientes_positivados_regiao=valores["regiao"],
                clientes_positivados_fora_carteira=valores["fora_carteira"],
            )
            for (ano, mes), valores in sorted(meses.items())
        ]

    def faturamento_por_laboratorio(self, filtros: FiltrosDashboard) -> list[PontoCategoria]:
        clientes_elegiveis = self._clientes_elegiveis_ids(filtros)
        consulta = (
            select(Laboratorio.nome, func.coalesce(func.sum(Faturamento.valor_faturado), 0))
            .join(Faturamento, Faturamento.laboratorio_id == Laboratorio.id)
            .where(Faturamento.cliente_id.in_(clientes_elegiveis))
            .group_by(Laboratorio.nome)
            .order_by(func.sum(Faturamento.valor_faturado).desc())
        )
        if filtros.ano:
            consulta = consulta.where(Faturamento.ano == filtros.ano)
        if filtros.mes:
            consulta = consulta.where(Faturamento.mes == filtros.mes)
        return [
            PontoCategoria(rotulo=nome, valor=valor or Decimal("0"))
            for nome, valor in self.session.execute(consulta).all()
        ]

    def tipos_checklist(self, filtros: FiltrosDashboard) -> list[PontoCategoria]:
        consulta = (
            select(Checklist.nome, func.count(func.distinct(ChecklistResposta.visita_id)))
            .select_from(ChecklistResposta)
            .join(
                ChecklistPergunta,
                ChecklistPergunta.id == ChecklistResposta.checklist_pergunta_id,
            )
            .join(Checklist, Checklist.id == ChecklistPergunta.checklist_id)
            .join(Visita, Visita.id == ChecklistResposta.visita_id)
            .group_by(Checklist.nome)
            .order_by(func.count(func.distinct(ChecklistResposta.visita_id)).desc())
        )
        if filtros.ano:
            consulta = consulta.where(func.strftime("%Y", Visita.data_visita) == str(filtros.ano))
        if filtros.mes:
            consulta = consulta.where(
                func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"
            )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        if filtros.escopo_promotor_ativo:
            consulta = consulta.where(Visita.promotor_id.in_(self._promotor_ids_filtrados(filtros)))
        return [
            PontoCategoria(rotulo=nome, valor=Decimal(contagem))
            for nome, contagem in self.session.execute(consulta).all()
        ]

    def distribuicao_uf(self, filtros: FiltrosDashboard) -> list[PontoUF]:
        clientes_elegiveis = self._clientes_elegiveis_ids(filtros).subquery()
        consulta = (
            select(
                Cliente.uf_sigla,
                func.coalesce(func.sum(Faturamento.valor_faturado), 0),
                func.count(func.distinct(Cliente.id)),
            )
            .select_from(Cliente)
            .join(clientes_elegiveis, clientes_elegiveis.c.id == Cliente.id)
            .outerjoin(
                Faturamento,
                and_(
                    Faturamento.cliente_id == Cliente.id,
                    *([Faturamento.ano == filtros.ano] if filtros.ano else []),
                    *([Faturamento.mes == filtros.mes] if filtros.mes else []),
                    *(
                        [Faturamento.laboratorio_id == filtros.laboratorio_id]
                        if filtros.laboratorio_id
                        else []
                    ),
                ),
            )
            .group_by(Cliente.uf_sigla)
            .order_by(func.sum(Faturamento.valor_faturado).desc())
        )
        return [
            PontoUF(uf_sigla=uf, faturamento_total=valor or Decimal("0"), quantidade_clientes=qtd)
            for uf, valor, qtd in self.session.execute(consulta).all()
        ]

    def top_promotores(
        self, filtros: FiltrosDashboard, limite: int = 10
    ) -> list[PontoRankingPromotor]:
        """Top N por Índice de Desempenho (KPIS.md, seção 10)."""

        promotores = self._promotores_com_metricas(filtros)
        ranqueados = sorted(
            promotores,
            key=lambda p: (
                p["indice"] if p["indice"] is not None else Decimal("-1"),
                p["positivacao"] if p["positivacao"] is not None else Decimal("-1"),
                p["cobertura"] if p["cobertura"] is not None else Decimal("-1"),
            ),
            reverse=True,
        )
        return [
            PontoRankingPromotor(
                promotor_id=p["id"],
                nome=p["nome"],
                indice_desempenho=p["indice"],
                cobertura=p["cobertura"],
                positivacao=p["positivacao"],
            )
            for p in ranqueados[:limite]
        ]

    # ------------------------------------------------------------- tabela

    def listar_promotores(
        self, filtros: FiltrosDashboard, pagina: int, tamanho_pagina: int
    ) -> PaginaPromotores:
        ids_filtrados = self._promotor_ids_filtrados(filtros)
        if filtros.sistema_origem == SistemaOrigem.SB_PROMOTOR:
            ids_filtrados = select(ids_filtrados.subquery().c.id).where(
                ids_filtrados.subquery().c.id.in_(select(Carteira.promotor_id).distinct())
            )
        elif filtros.sistema_origem in (SistemaOrigem.WECHECK, SistemaOrigem.PAINEL_AVERT):
            ids_filtrados = select(ids_filtrados.subquery().c.id).where(
                ids_filtrados.subquery().c.id.in_(
                    select(CarteiraAvert.promotor_id)
                    .where(CarteiraAvert.promotor_id.is_not(None))
                    .distinct()
                )
            )
        total = self.session.scalar(select(func.count()).select_from(ids_filtrados.subquery())) or 0

        pagina_ids = list(
            self.session.scalars(
                select(Promotor.id)
                .where(Promotor.id.in_(ids_filtrados))
                .order_by(Promotor.nome)
                .offset((pagina - 1) * tamanho_pagina)
                .limit(tamanho_pagina)
            )
        )
        if not pagina_ids:
            return PaginaPromotores(itens=[], total_itens=total)

        metricas = {
            m["id"]: m for m in self._promotores_com_metricas(filtros, apenas_ids=pagina_ids)
        }
        itens = [
            LinhaPromotor(
                promotor_id=id_,
                nome=metricas[id_]["nome"],
                tipo=metricas[id_]["tipo"],
                supervisor=metricas[id_]["supervisor"],
                sistema_origem=metricas[id_]["sistema_origem"],
                quantidade_clientes=metricas[id_]["quantidade_clientes"],
                numero_visitas=metricas[id_]["numero_visitas"],
                numero_checklists=metricas[id_]["numero_checklists"],
                cobertura_carteira=metricas[id_]["cobertura"],
                faturamento_carteira=metricas[id_]["faturamento_carteira"],
                faturamento_regiao=metricas[id_]["faturamento_regiao"],
            )
            for id_ in pagina_ids
            if id_ in metricas
        ]
        return PaginaPromotores(itens=itens, total_itens=total)

    def _promotores_com_metricas(
        self, filtros: FiltrosDashboard, apenas_ids: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Métricas por promotor em poucas queries agregadas (evita N+1)."""

        base_ids = (
            select(Promotor.id)
            if apenas_ids is None
            else select(Promotor.id).where(Promotor.id.in_(apenas_ids))
        )
        if apenas_ids is None:
            base_ids = self._promotor_ids_filtrados(filtros)

        promotores = list(
            self.session.execute(
                select(
                    Promotor.id,
                    Promotor.nome,
                    TipoPromotorCadastro.nome,
                    Supervisor.nome,
                )
                .select_from(Promotor)
                .outerjoin(
                    TipoPromotorCadastro, TipoPromotorCadastro.id == Promotor.tipo_promotor_id
                )
                .outerjoin(Supervisor, Supervisor.id == Promotor.supervisor_id)
                .where(Promotor.id.in_(base_ids))
            ).all()
        )
        ids = [p[0] for p in promotores]
        if not ids:
            return []

        clientes_carteira: dict[str, int] = {
            promotor_id: contagem
            for promotor_id, contagem in self.session.execute(
                select(Carteira.promotor_id, func.count(func.distinct(Carteira.cliente_id)))
                .select_from(Carteira)
                .join(Cliente, Cliente.id == Carteira.cliente_id)
                .where(
                    Carteira.promotor_id.in_(ids),
                    Carteira.status == StatusCarteira.ATIVA,
                    Carteira.data_fim_vigencia.is_(None),
                    *([Cliente.uf_sigla == filtros.uf_sigla] if filtros.uf_sigla else []),
                )
                .group_by(Carteira.promotor_id)
            ).all()
        }
        clientes_avert: dict[str, int] = {
            promotor_id: contagem
            for promotor_id, contagem in self.session.execute(
                select(
                    CarteiraAvert.promotor_id, func.count(func.distinct(CarteiraAvert.cliente_id))
                )
                .select_from(CarteiraAvert)
                .join(Cliente, Cliente.id == CarteiraAvert.cliente_id)
                .where(
                    CarteiraAvert.promotor_id.in_(ids),
                    CarteiraAvert.promotor_id.is_not(None),
                    *([Cliente.uf_sigla == filtros.uf_sigla] if filtros.uf_sigla else []),
                )
                .group_by(CarteiraAvert.promotor_id)
            ).all()
            if promotor_id is not None
        }
        origem_sb = set(
            self.session.scalars(
                select(Carteira.promotor_id).where(Carteira.promotor_id.in_(ids)).distinct()
            )
        )
        origem_avert = set(
            self.session.scalars(
                select(CarteiraAvert.promotor_id)
                .where(CarteiraAvert.promotor_id.in_(ids))
                .distinct()
            )
        )

        faturamento_carteira: dict[str, Decimal] = {
            promotor_id: valor
            for promotor_id, valor in self.session.execute(
                select(Carteira.promotor_id, func.coalesce(func.sum(Faturamento.valor_faturado), 0))
                .select_from(Carteira)
                .join(Faturamento, Faturamento.cliente_id == Carteira.cliente_id)
                .join(Cliente, Cliente.id == Carteira.cliente_id)
                .where(
                    Carteira.promotor_id.in_(ids),
                    Carteira.status == StatusCarteira.ATIVA,
                    Carteira.data_fim_vigencia.is_(None),
                    *([Faturamento.ano == filtros.ano] if filtros.ano else []),
                    *([Faturamento.mes == filtros.mes] if filtros.mes else []),
                    *([Cliente.uf_sigla == filtros.uf_sigla] if filtros.uf_sigla else []),
                )
                .group_by(Carteira.promotor_id)
            ).all()
        }
        faturamento_regiao: dict[str, Decimal] = {
            promotor_id: valor
            for promotor_id, valor in self.session.execute(
                select(
                    CarteiraAvert.promotor_id,
                    func.coalesce(func.sum(Faturamento.valor_faturado), 0),
                )
                .select_from(CarteiraAvert)
                .join(Faturamento, Faturamento.cliente_id == CarteiraAvert.cliente_id)
                .join(Cliente, Cliente.id == CarteiraAvert.cliente_id)
                .where(
                    CarteiraAvert.promotor_id.in_(ids),
                    CarteiraAvert.promotor_id.is_not(None),
                    *([Faturamento.ano == filtros.ano] if filtros.ano else []),
                    *([Faturamento.mes == filtros.mes] if filtros.mes else []),
                    *([Cliente.uf_sigla == filtros.uf_sigla] if filtros.uf_sigla else []),
                )
                .group_by(CarteiraAvert.promotor_id)
            ).all()
            if promotor_id is not None
        }
        consulta_visitas_realizadas = select(Visita.promotor_id, func.count()).where(
            Visita.promotor_id.in_(ids),
            Visita.status == StatusVisita.REALIZADA,
            *([func.strftime("%Y", Visita.data_visita) == str(filtros.ano)] if filtros.ano else []),
            *(
                [func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"]
                if filtros.mes
                else []
            ),
        )
        if filtros.uf_sigla:
            consulta_visitas_realizadas = consulta_visitas_realizadas.join(
                Cliente, Cliente.id == Visita.cliente_id
            ).where(Cliente.uf_sigla == filtros.uf_sigla)
        visitas_realizadas: dict[str, int] = {
            promotor_id: contagem
            for promotor_id, contagem in self.session.execute(
                consulta_visitas_realizadas.group_by(Visita.promotor_id)
            ).all()
        }

        consulta_visitas_planejadas = select(Visita.promotor_id, func.count()).where(
            Visita.promotor_id.in_(ids),
            Visita.status.in_([StatusVisita.REALIZADA, StatusVisita.PENDENTE]),
        )
        if filtros.uf_sigla:
            consulta_visitas_planejadas = consulta_visitas_planejadas.join(
                Cliente, Cliente.id == Visita.cliente_id
            ).where(Cliente.uf_sigla == filtros.uf_sigla)
        visitas_planejadas: dict[str, int] = {
            promotor_id: contagem
            for promotor_id, contagem in self.session.execute(
                consulta_visitas_planejadas.group_by(Visita.promotor_id)
            ).all()
        }

        consulta_checklists = (
            select(Visita.promotor_id, func.count(ChecklistResposta.id))
            .select_from(ChecklistResposta)
            .join(Visita, Visita.id == ChecklistResposta.visita_id)
            .where(Visita.promotor_id.in_(ids))
        )
        if filtros.uf_sigla:
            consulta_checklists = consulta_checklists.join(
                Cliente, Cliente.id == Visita.cliente_id
            ).where(Cliente.uf_sigla == filtros.uf_sigla)
        checklists: dict[str, int] = {
            promotor_id: contagem
            for promotor_id, contagem in self.session.execute(
                consulta_checklists.group_by(Visita.promotor_id)
            ).all()
        }

        consulta_conformes = (
            select(
                Visita.promotor_id,
                func.sum(
                    case((ChecklistResposta.conforme.is_(True), ChecklistPergunta.peso), else_=0)
                ),
                func.sum(ChecklistPergunta.peso),
            )
            .select_from(ChecklistResposta)
            .join(Visita, Visita.id == ChecklistResposta.visita_id)
            .join(
                ChecklistPergunta,
                ChecklistPergunta.id == ChecklistResposta.checklist_pergunta_id,
            )
            .where(
                Visita.promotor_id.in_(ids),
                ChecklistPergunta.tipo_resposta == TipoRespostaChecklist.SIM_NAO,
                ChecklistResposta.conforme.is_not(None),
            )
        )
        if filtros.uf_sigla:
            consulta_conformes = consulta_conformes.join(
                Cliente, Cliente.id == Visita.cliente_id
            ).where(Cliente.uf_sigla == filtros.uf_sigla)
        conformes: dict[str, tuple[Decimal | None, Decimal | None]] = {
            promotor_id: (soma_conforme, soma_peso)
            for promotor_id, soma_conforme, soma_peso in self.session.execute(
                consulta_conformes.group_by(Visita.promotor_id)
            ).all()
        }
        cobertura_visitados = {
            promotor_id: contagem
            for promotor_id, contagem in self.session.execute(
                select(Carteira.promotor_id, func.count(func.distinct(Carteira.cliente_id)))
                .select_from(Carteira)
                .join(
                    Visita,
                    and_(
                        Visita.cliente_id == Carteira.cliente_id,
                        Visita.promotor_id == Carteira.promotor_id,
                        Visita.status == StatusVisita.REALIZADA,
                    ),
                )
                .join(Cliente, Cliente.id == Carteira.cliente_id)
                .where(
                    Carteira.promotor_id.in_(ids),
                    Carteira.status == StatusCarteira.ATIVA,
                    Carteira.data_fim_vigencia.is_(None),
                    *([Cliente.uf_sigla == filtros.uf_sigla] if filtros.uf_sigla else []),
                )
                .group_by(Carteira.promotor_id)
            ).all()
        }

        resultado = []
        for id_, nome, tipo, supervisor in promotores:
            qtd_carteira = clientes_carteira.get(id_, 0)
            qtd_regiao = clientes_avert.get(id_, 0)
            cobertura = (
                Decimal(cobertura_visitados.get(id_, 0)) / Decimal(qtd_carteira)
                if qtd_carteira
                else None
            )
            realizadas = visitas_realizadas.get(id_, 0)
            planejadas = visitas_planejadas.get(id_, 0)
            fat_carteira = faturamento_carteira.get(id_, Decimal("0")) or Decimal("0")
            fat_regiao = faturamento_regiao.get(id_, Decimal("0")) or Decimal("0")
            positivacao = self._positivacao_promotor(id_, filtros)
            conforme_peso, total_peso = conformes.get(id_, (None, None))
            conformidade = (
                (conforme_peso / total_peso) if conforme_peso is not None and total_peso else None
            )
            indice = None
            if cobertura is not None and positivacao is not None and conformidade is not None:
                razao_visitas = (
                    min(Decimal(realizadas) / Decimal(planejadas), Decimal("1"))
                    if planejadas
                    else Decimal("0")
                )
                indice = (
                    cobertura * _PESO_COBERTURA
                    + positivacao * _PESO_POSITIVACAO
                    + conformidade * _PESO_CONFORMIDADE
                    + razao_visitas * _PESO_VISITAS
                )
            sistema = None
            if id_ in origem_sb and id_ in origem_avert:
                sistema = "AMBOS"
            elif id_ in origem_sb:
                sistema = SistemaOrigem.SB_PROMOTOR.value
            elif id_ in origem_avert:
                sistema = "AVERT"

            resultado.append(
                {
                    "id": id_,
                    "nome": nome,
                    "tipo": tipo,
                    "supervisor": supervisor,
                    "sistema_origem": sistema,
                    "quantidade_clientes": qtd_carteira + qtd_regiao,
                    "numero_visitas": realizadas,
                    "numero_checklists": checklists.get(id_, 0),
                    "cobertura": cobertura,
                    "faturamento_carteira": fat_carteira,
                    "faturamento_regiao": fat_regiao,
                    "positivacao": positivacao,
                    "conformidade": conformidade,
                    "indice": indice,
                }
            )
        return resultado

    def _positivacao_promotor(self, promotor_id: str, filtros: FiltrosDashboard) -> Decimal | None:
        carteira_ids: Select[Any] = self._com_uf(
            select(Carteira.cliente_id).where(
                Carteira.promotor_id == promotor_id,
                Carteira.status == StatusCarteira.ATIVA,
                Carteira.data_fim_vigencia.is_(None),
            ),
            filtros,
        )
        total = self.session.scalar(select(func.count()).select_from(carteira_ids.subquery())) or 0
        if total == 0:
            return None
        positivados = self._contar_positivados(filtros, carteira_ids)
        return Decimal(positivados) / Decimal(total)

    # -------------------------------------------------------------- detalhe

    def obter_detalhe_promotor(
        self, promotor_id: str, filtros: FiltrosDashboard
    ) -> DetalhePromotor:
        promotor = self.session.get(Promotor, promotor_id)
        if promotor is None:
            raise RegistroNaoEncontradoError(f"Promotor {promotor_id} não encontrado.")

        filtros_promotor = FiltrosDashboard(
            ano=filtros.ano,
            mes=filtros.mes,
            promotor_id=promotor_id,
        )
        kpis = self.calcular_kpis(filtros_promotor)
        metricas = self._promotores_com_metricas(filtros_promotor, apenas_ids=[promotor_id])
        conformidade = metricas[0]["conformidade"] if metricas else None
        indice = metricas[0]["indice"] if metricas else None

        tipo_nome = self.session.scalar(
            select(TipoPromotorCadastro.nome).where(
                TipoPromotorCadastro.id == promotor.tipo_promotor_id
            )
        )
        supervisor_nome = self.session.scalar(
            select(Supervisor.nome).where(Supervisor.id == promotor.supervisor_id)
        )

        return DetalhePromotor(
            promotor_id=promotor.id,
            nome=promotor.nome,
            tipo=tipo_nome,
            supervisor=supervisor_nome,
            codigo_externo=promotor.codigo_externo,
            area=promotor.area,
            kpis=kpis,
            conformidade_checklist=conformidade,
            indice_desempenho=indice,
            evolucao_faturamento=self.evolucao_faturamento_mensal(filtros_promotor),
            faturamento_por_laboratorio=self.faturamento_por_laboratorio(filtros_promotor),
        )

    # ---------------------------------------------------------- importações

    def listar_ultimas_importacoes(self) -> list[Importacao]:
        """1 importação mais recente por tipo de arquivo (widget da Home)."""

        subconsulta = (
            select(
                Importacao.tipo_arquivo,
                func.max(Importacao.criado_em).label("mais_recente"),
            )
            .where(Importacao.versao > 0)
            .group_by(Importacao.tipo_arquivo)
            .subquery()
        )
        consulta = (
            select(Importacao)
            .join(
                subconsulta,
                and_(
                    Importacao.tipo_arquivo == subconsulta.c.tipo_arquivo,
                    Importacao.criado_em == subconsulta.c.mais_recente,
                ),
            )
            .order_by(Importacao.criado_em.desc())
        )
        return list(self.session.scalars(consulta))
