"""Serviço da Visão 360º do Cliente (Sprint 5, ver docs/DECISIONS.md, seção 22).

Segue o mesmo princípio do `DashboardService` (Sprint 4): todo KPI e série é
resolvido com agregação SQL — nunca carregando entidades para somar em
Python, exceto a Timeline (4 fontes pequenas combinadas e paginadas em
memória, mesmo raciocínio de custo desprezível do Índice de Desempenho).

Reaproveita `PontoSerieMensal`/`PontoCategoria` e a rotina anti-N+1
`_promotores_com_metricas` de `dashboard_service.py` para os "vínculos de
promotor" do cliente, garantindo que os números batam com a Tabela de
Promotores (docs/DECISIONS.md, seção 22).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.domain.enums import AcaoAuditoria, SistemaOrigem, StatusCarteira, StatusVisita
from app.domain.excecoes import RegistroNaoEncontradoError
from app.infrastructure.database import normalizar_para_busca
from app.infrastructure.models import (
    Carteira,
    CarteiraAvert,
    Checklist,
    ChecklistPergunta,
    ChecklistResposta,
    Cidade,
    Cliente,
    Faturamento,
    Importacao,
    Laboratorio,
    LogAuditoria,
    Promotor,
    Visita,
)
from app.services.dashboard_service import (
    DashboardService,
    FiltrosDashboard,
    PontoCategoria,
    PontoSerieMensal,
)

_LIMITE_EVENTOS_POR_FONTE = 500


def _mes_inicial_ultimos_12(hoje: date) -> tuple[int, int]:
    ano, mes = hoje.year, hoje.month - 11
    while mes <= 0:
        mes += 12
        ano -= 1
    return ano, mes


@dataclass(frozen=True)
class FiltrosCliente:
    """Filtros da Visão 360 (Sprint 5): Período (Ano/Mês), Laboratório, Sistema de Origem."""

    ano: int | None = None
    mes: int | None = None
    laboratorio_id: str | None = None
    sistema_origem: SistemaOrigem | None = None


@dataclass
class KpisCliente:
    faturamento_acumulado: Decimal
    faturamento_12_meses: Decimal
    quantidade_laboratorios: int
    quantidade_visitas: int
    quantidade_checklists: int
    dias_desde_ultima_visita: int | None
    cobertura: Decimal
    positivacao: Decimal


@dataclass
class VinculoPromotorCliente:
    sistema_origem: str
    promotor_id: str
    nome: str
    tipo: str | None
    supervisor: str | None
    quantidade_clientes_carteira: int
    cobertura: Decimal | None
    faturamento_carteira: Decimal


@dataclass
class DetalheCliente:
    id: str
    codigo_externo: str
    razao_social: str
    nome_fantasia: str | None
    cidade: str
    uf_sigla: str
    cnpj_cpf: str | None
    ativo: bool
    grupo_economico: str | None
    segmento: str | None
    vinculos: list[VinculoPromotorCliente]
    kpis: KpisCliente


@dataclass
class LinhaLaboratorioCliente:
    laboratorio: str
    primeiro_ano: int
    primeiro_mes: int
    ultimo_ano: int
    ultimo_mes: int
    valor_acumulado: Decimal
    participacao_percentual: Decimal


@dataclass
class EventoTimeline:
    tipo: str
    data: datetime
    titulo: str
    descricao: str | None


@dataclass
class PaginaTimeline:
    itens: list[EventoTimeline]
    total_itens: int


@dataclass
class LinhaClienteBusca:
    id: str
    codigo_externo: str
    razao_social: str
    nome_fantasia: str | None
    cidade: str
    uf_sigla: str
    ativo: bool


@dataclass
class PaginaClientesBusca:
    itens: list[LinhaClienteBusca]
    total_itens: int


class ClienteService:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------------------------------------------------------------- busca

    def buscar_clientes(
        self, termo: str, pagina: int, tamanho_pagina: int, promotor_id: str | None = None
    ) -> PaginaClientesBusca:
        """Busca global (Sprint 5). `promotor_id` restringe à carteira (SB ou
        Avert) de um promotor — usado pela Página do Promotor para navegar
        Promotor → Cliente (docs/DECISIONS.md, seção 22)."""

        consulta = (
            select(Cliente, Cidade.nome)
            .select_from(Cliente)
            .join(Cidade, Cidade.id == Cliente.cidade_id)
        )
        if promotor_id:
            ids_carteira_sb = select(Carteira.cliente_id).where(
                Carteira.promotor_id == promotor_id,
                Carteira.status == StatusCarteira.ATIVA,
                Carteira.data_fim_vigencia.is_(None),
            )
            ids_carteira_avert = select(CarteiraAvert.cliente_id).where(
                CarteiraAvert.promotor_id == promotor_id
            )
            consulta = consulta.where(
                or_(Cliente.id.in_(ids_carteira_sb), Cliente.id.in_(ids_carteira_avert))
            )
        termo_normalizado = termo.strip()
        if termo_normalizado:
            termo_like = f"%{termo_normalizado}%"
            # codigo_externo/cnpj_cpf são dígitos — sem acento, plain ILIKE
            # basta e preserva o índice de cnpj_cpf (seção 23).
            condicoes = [
                Cliente.codigo_externo.ilike(termo_like),
                Cliente.cnpj_cpf.ilike(termo_like),
            ]
            if self.session.get_bind().dialect.name == "sqlite":
                # LOWER() do SQLite não faz case-fold de acento (mesma
                # limitação da Sprint 3, docs/DECISIONS.md, seção 15.3) —
                # sem isso, "são paulo" não encontra "SÃO PAULO".
                termo_busca = f"%{normalizar_para_busca(termo_normalizado)}%"
                condicoes += [
                    func.norm_busca(Cliente.razao_social).like(termo_busca),
                    func.norm_busca(Cliente.nome_fantasia).like(termo_busca),
                    func.norm_busca(Cidade.nome).like(termo_busca),
                ]
            else:
                condicoes += [
                    Cliente.razao_social.ilike(termo_like),
                    Cliente.nome_fantasia.ilike(termo_like),
                    Cidade.nome.ilike(termo_like),
                ]
            consulta = consulta.where(or_(*condicoes))
        total = self.session.scalar(select(func.count()).select_from(consulta.subquery())) or 0
        pagina_consulta = (
            consulta.order_by(Cliente.razao_social)
            .offset((pagina - 1) * tamanho_pagina)
            .limit(tamanho_pagina)
        )
        itens = [
            LinhaClienteBusca(
                id=cliente.id,
                codigo_externo=cliente.codigo_externo,
                razao_social=cliente.razao_social,
                nome_fantasia=cliente.nome_fantasia,
                cidade=cidade_nome,
                uf_sigla=cliente.uf_sigla,
                ativo=cliente.ativo,
            )
            for cliente, cidade_nome in self.session.execute(pagina_consulta).all()
        ]
        return PaginaClientesBusca(itens=itens, total_itens=total)

    # -------------------------------------------------------------- detalhe

    def obter_detalhe_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> DetalheCliente:
        cliente = self.session.get(Cliente, cliente_id)
        if cliente is None:
            raise RegistroNaoEncontradoError(f"Cliente {cliente_id} não encontrado.")

        cidade_nome = (
            self.session.scalar(select(Cidade.nome).where(Cidade.id == cliente.cidade_id)) or ""
        )
        carteira_avert = self.session.scalar(
            select(CarteiraAvert)
            .where(CarteiraAvert.cliente_id == cliente_id)
            .order_by(CarteiraAvert.criado_em.desc())
        )

        return DetalheCliente(
            id=cliente.id,
            codigo_externo=cliente.codigo_externo,
            razao_social=cliente.razao_social,
            nome_fantasia=cliente.nome_fantasia,
            cidade=cidade_nome,
            uf_sigla=cliente.uf_sigla,
            cnpj_cpf=cliente.cnpj_cpf,
            ativo=cliente.ativo,
            grupo_economico=carteira_avert.grupo_economico if carteira_avert else None,
            segmento=carteira_avert.segmento if carteira_avert else None,
            vinculos=self._vinculos_promotor(cliente_id),
            kpis=self._kpis_cliente(cliente_id, filtros),
        )

    def _resumo_promotor(self, promotor_id: str) -> dict[str, Any] | None:
        """Reaproveita a rotina anti-N+1 do Dashboard (Sprint 4) — mesmos números da Tabela."""

        metricas = DashboardService(self.session)._promotores_com_metricas(
            FiltrosDashboard(), apenas_ids=[promotor_id]
        )
        return metricas[0] if metricas else None

    def _vinculos_promotor(self, cliente_id: str) -> list[VinculoPromotorCliente]:
        vinculos: list[VinculoPromotorCliente] = []

        carteira_sb = self.session.scalar(
            select(Carteira).where(
                Carteira.cliente_id == cliente_id,
                Carteira.status == StatusCarteira.ATIVA,
                Carteira.data_fim_vigencia.is_(None),
            )
        )
        if carteira_sb is not None:
            resumo = self._resumo_promotor(carteira_sb.promotor_id)
            if resumo is not None:
                vinculos.append(
                    VinculoPromotorCliente(
                        sistema_origem=SistemaOrigem.SB_PROMOTOR.value,
                        promotor_id=resumo["id"],
                        nome=resumo["nome"],
                        tipo=resumo["tipo"],
                        supervisor=resumo["supervisor"],
                        quantidade_clientes_carteira=resumo["quantidade_clientes"],
                        cobertura=resumo["cobertura"],
                        faturamento_carteira=resumo["faturamento_carteira"],
                    )
                )

        carteira_avert = self.session.scalar(
            select(CarteiraAvert)
            .where(CarteiraAvert.cliente_id == cliente_id, CarteiraAvert.promotor_id.is_not(None))
            .order_by(CarteiraAvert.criado_em.desc())
        )
        if carteira_avert is not None and carteira_avert.promotor_id:
            resumo = self._resumo_promotor(carteira_avert.promotor_id)
            if resumo is not None:
                vinculos.append(
                    VinculoPromotorCliente(
                        sistema_origem=SistemaOrigem.PAINEL_AVERT.value,
                        promotor_id=resumo["id"],
                        nome=resumo["nome"],
                        tipo=resumo["tipo"],
                        supervisor=resumo["supervisor"],
                        quantidade_clientes_carteira=resumo["quantidade_clientes"],
                        cobertura=resumo["cobertura"],
                        faturamento_carteira=resumo["faturamento_carteira"],
                    )
                )
        return vinculos

    # ------------------------------------------------------------------ kpis

    def _faturamento_query_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> Select[Any]:
        consulta = select(Faturamento).where(Faturamento.cliente_id == cliente_id)
        if filtros.ano:
            consulta = consulta.where(Faturamento.ano == filtros.ano)
        if filtros.mes:
            consulta = consulta.where(Faturamento.mes == filtros.mes)
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        return consulta

    def _soma_faturamento_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> Decimal:
        subconsulta = self._faturamento_query_cliente(cliente_id, filtros).subquery()
        consulta = select(func.coalesce(func.sum(subconsulta.c.valor_faturado), 0))
        return self.session.scalar(consulta) or Decimal("0")

    def _faturamento_ultimos_12_meses(self, cliente_id: str, filtros: FiltrosCliente) -> Decimal:
        """Janela móvel fixa dos últimos 12 meses — independe de `ano`/`mes` filtrados."""

        hoje = date.today()
        ano_ini, mes_ini = _mes_inicial_ultimos_12(hoje)
        codigo_ini = ano_ini * 100 + mes_ini
        codigo_fim = hoje.year * 100 + hoje.month
        consulta = select(Faturamento).where(
            Faturamento.cliente_id == cliente_id,
            (Faturamento.ano * 100 + Faturamento.mes).between(codigo_ini, codigo_fim),
        )
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        subconsulta = consulta.subquery()
        return self.session.scalar(
            select(func.coalesce(func.sum(subconsulta.c.valor_faturado), 0))
        ) or Decimal("0")

    def _quantidade_laboratorios(self, cliente_id: str, filtros: FiltrosCliente) -> int:
        consulta = select(func.count(func.distinct(Faturamento.laboratorio_id))).where(
            Faturamento.cliente_id == cliente_id
        )
        if filtros.ano:
            consulta = consulta.where(Faturamento.ano == filtros.ano)
        if filtros.mes:
            consulta = consulta.where(Faturamento.mes == filtros.mes)
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        return self.session.scalar(consulta) or 0

    def _visitas_query_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> Select[Any]:
        consulta = select(Visita).where(
            Visita.cliente_id == cliente_id, Visita.status == StatusVisita.REALIZADA
        )
        if filtros.ano:
            consulta = consulta.where(func.strftime("%Y", Visita.data_visita) == str(filtros.ano))
        if filtros.mes:
            consulta = consulta.where(
                func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"
            )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        return consulta

    def _quantidade_visitas(self, cliente_id: str, filtros: FiltrosCliente) -> int:
        consulta = select(func.count()).select_from(
            self._visitas_query_cliente(cliente_id, filtros).subquery()
        )
        return self.session.scalar(consulta) or 0

    def _quantidade_checklists(self, cliente_id: str, filtros: FiltrosCliente) -> int:
        consulta = (
            select(func.count(ChecklistResposta.id))
            .select_from(ChecklistResposta)
            .join(Visita, Visita.id == ChecklistResposta.visita_id)
            .where(Visita.cliente_id == cliente_id)
        )
        if filtros.ano:
            consulta = consulta.where(func.strftime("%Y", Visita.data_visita) == str(filtros.ano))
        if filtros.mes:
            consulta = consulta.where(
                func.strftime("%m", Visita.data_visita) == f"{filtros.mes:02d}"
            )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        return self.session.scalar(consulta) or 0

    def _dias_desde_ultima_visita(self, cliente_id: str, filtros: FiltrosCliente) -> int | None:
        consulta = select(func.max(Visita.data_visita)).where(
            Visita.cliente_id == cliente_id, Visita.status == StatusVisita.REALIZADA
        )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        ultima = self.session.scalar(consulta)
        return (date.today() - ultima).days if ultima else None

    def _janela(self, filtros: FiltrosCliente) -> tuple[int, int, int, int, int]:
        """Janela (ano_ini, mes_ini, ano_fim, mes_fim, total_meses) de Cobertura/Positivação."""

        if filtros.ano and filtros.mes:
            return filtros.ano, filtros.mes, filtros.ano, filtros.mes, 1
        if filtros.ano:
            return filtros.ano, 1, filtros.ano, 12, 12
        hoje = date.today()
        ano_ini, mes_ini = _mes_inicial_ultimos_12(hoje)
        return ano_ini, mes_ini, hoje.year, hoje.month, 12

    def _cobertura_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> Decimal:
        ano_ini, mes_ini, ano_fim, mes_fim, total_meses = self._janela(filtros)
        data_inicio = date(ano_ini, mes_ini, 1)
        data_fim = date(ano_fim, mes_fim, calendar.monthrange(ano_fim, mes_fim)[1])
        consulta = select(
            func.count(func.distinct(func.strftime("%Y-%m", Visita.data_visita)))
        ).where(
            Visita.cliente_id == cliente_id,
            Visita.status == StatusVisita.REALIZADA,
            Visita.data_visita >= data_inicio,
            Visita.data_visita <= data_fim,
        )
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        cobertos = self.session.scalar(consulta) or 0
        return Decimal(cobertos) / Decimal(total_meses)

    def _positivacao_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> Decimal:
        ano_ini, mes_ini, ano_fim, mes_fim, total_meses = self._janela(filtros)
        codigo_ini = ano_ini * 100 + mes_ini
        codigo_fim = ano_fim * 100 + mes_fim
        consulta = select(
            Faturamento.ano, Faturamento.mes, func.sum(Faturamento.valor_faturado).label("total")
        ).where(
            Faturamento.cliente_id == cliente_id,
            (Faturamento.ano * 100 + Faturamento.mes).between(codigo_ini, codigo_fim),
        )
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        base = consulta.group_by(Faturamento.ano, Faturamento.mes).subquery()
        positivos = (
            self.session.scalar(select(func.count()).select_from(base).where(base.c.total > 0)) or 0
        )
        return Decimal(positivos) / Decimal(total_meses)

    def _kpis_cliente(self, cliente_id: str, filtros: FiltrosCliente) -> KpisCliente:
        return KpisCliente(
            faturamento_acumulado=self._soma_faturamento_cliente(cliente_id, filtros),
            faturamento_12_meses=self._faturamento_ultimos_12_meses(cliente_id, filtros),
            quantidade_laboratorios=self._quantidade_laboratorios(cliente_id, filtros),
            quantidade_visitas=self._quantidade_visitas(cliente_id, filtros),
            quantidade_checklists=self._quantidade_checklists(cliente_id, filtros),
            dias_desde_ultima_visita=self._dias_desde_ultima_visita(cliente_id, filtros),
            cobertura=self._cobertura_cliente(cliente_id, filtros),
            positivacao=self._positivacao_cliente(cliente_id, filtros),
        )

    # --------------------------------------------------------------- gráficos

    def evolucao_faturamento_cliente(
        self, cliente_id: str, filtros: FiltrosCliente
    ) -> list[PontoSerieMensal]:
        consulta = (
            select(
                Faturamento.ano,
                Faturamento.mes,
                func.coalesce(func.sum(Faturamento.valor_faturado), 0),
            )
            .where(Faturamento.cliente_id == cliente_id)
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

    def _laboratorios_cliente_bruto(self, cliente_id: str, filtros: FiltrosCliente) -> list[Any]:
        consulta = (
            select(
                Laboratorio.nome,
                func.min(Faturamento.ano * 100 + Faturamento.mes),
                func.max(Faturamento.ano * 100 + Faturamento.mes),
                func.coalesce(func.sum(Faturamento.valor_faturado), 0),
            )
            .select_from(Faturamento)
            .join(Laboratorio, Laboratorio.id == Faturamento.laboratorio_id)
            .where(Faturamento.cliente_id == cliente_id)
            .group_by(Laboratorio.nome)
            .order_by(func.sum(Faturamento.valor_faturado).desc())
        )
        if filtros.ano:
            consulta = consulta.where(Faturamento.ano == filtros.ano)
        if filtros.mes:
            consulta = consulta.where(Faturamento.mes == filtros.mes)
        if filtros.laboratorio_id:
            consulta = consulta.where(Faturamento.laboratorio_id == filtros.laboratorio_id)
        return list(self.session.execute(consulta).all())

    def faturamento_por_laboratorio_cliente(
        self, cliente_id: str, filtros: FiltrosCliente
    ) -> list[PontoCategoria]:
        linhas = self._laboratorios_cliente_bruto(cliente_id, filtros)
        return [
            PontoCategoria(rotulo=nome, valor=valor or Decimal("0")) for nome, _, _, valor in linhas
        ]

    def laboratorios_cliente(
        self, cliente_id: str, filtros: FiltrosCliente
    ) -> list[LinhaLaboratorioCliente]:
        linhas = self._laboratorios_cliente_bruto(cliente_id, filtros)
        total_geral = sum(
            (valor or Decimal("0") for _, _, _, valor in linhas), Decimal("0")
        ) or Decimal("1")
        resultado = []
        for nome, primeiro, ultimo, valor in linhas:
            valor = valor or Decimal("0")
            primeiro_ano, primeiro_mes = divmod(int(primeiro), 100)
            ultimo_ano, ultimo_mes = divmod(int(ultimo), 100)
            resultado.append(
                LinhaLaboratorioCliente(
                    laboratorio=nome,
                    primeiro_ano=primeiro_ano,
                    primeiro_mes=primeiro_mes,
                    ultimo_ano=ultimo_ano,
                    ultimo_mes=ultimo_mes,
                    valor_acumulado=valor,
                    participacao_percentual=valor / total_geral,
                )
            )
        return resultado

    def visitas_por_mes_cliente(
        self, cliente_id: str, filtros: FiltrosCliente
    ) -> list[PontoSerieMensal]:
        ano_expr = func.strftime("%Y", Visita.data_visita)
        mes_expr = func.strftime("%m", Visita.data_visita)
        consulta = (
            select(ano_expr, mes_expr, func.count())
            .where(Visita.cliente_id == cliente_id, Visita.status == StatusVisita.REALIZADA)
            .group_by(ano_expr, mes_expr)
            .order_by(ano_expr, mes_expr)
        )
        if filtros.ano:
            consulta = consulta.where(ano_expr == str(filtros.ano))
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        return [
            PontoSerieMensal(ano=int(ano), mes=int(mes), valor=Decimal(contagem))
            for ano, mes, contagem in self.session.execute(consulta).all()
        ]

    def checklists_por_mes_cliente(
        self, cliente_id: str, filtros: FiltrosCliente
    ) -> list[PontoSerieMensal]:
        ano_expr = func.strftime("%Y", Visita.data_visita)
        mes_expr = func.strftime("%m", Visita.data_visita)
        consulta = (
            select(ano_expr, mes_expr, func.count(ChecklistResposta.id))
            .select_from(ChecklistResposta)
            .join(Visita, Visita.id == ChecklistResposta.visita_id)
            .where(Visita.cliente_id == cliente_id)
            .group_by(ano_expr, mes_expr)
            .order_by(ano_expr, mes_expr)
        )
        if filtros.ano:
            consulta = consulta.where(ano_expr == str(filtros.ano))
        if filtros.sistema_origem:
            consulta = consulta.where(Visita.origem == filtros.sistema_origem)
        return [
            PontoSerieMensal(ano=int(ano), mes=int(mes), valor=Decimal(contagem))
            for ano, mes, contagem in self.session.execute(consulta).all()
        ]

    # -------------------------------------------------------------- timeline

    def timeline_cliente(self, cliente_id: str, pagina: int, tamanho_pagina: int) -> PaginaTimeline:
        eventos: list[EventoTimeline] = []
        eventos.extend(self._eventos_visitas(cliente_id))
        eventos.extend(self._eventos_checklists(cliente_id))
        eventos.extend(self._eventos_importacoes(cliente_id))
        eventos.extend(self._eventos_alteracoes_cadastrais(cliente_id))
        eventos.sort(key=lambda evento: evento.data, reverse=True)

        total = len(eventos)
        inicio = (pagina - 1) * tamanho_pagina
        return PaginaTimeline(itens=eventos[inicio : inicio + tamanho_pagina], total_itens=total)

    def _eventos_visitas(self, cliente_id: str) -> list[EventoTimeline]:
        linhas = self.session.execute(
            select(Visita, Promotor.nome)
            .join(Promotor, Promotor.id == Visita.promotor_id)
            .where(Visita.cliente_id == cliente_id)
            .order_by(Visita.data_visita.desc())
            .limit(_LIMITE_EVENTOS_POR_FONTE)
        ).all()
        return [
            EventoTimeline(
                tipo="VISITA",
                data=datetime.combine(visita.data_visita, visita.hora_inicio or time.min),
                titulo=f"Visita {visita.status.value.lower()}",
                descricao=f"{nome_promotor} · origem {visita.origem.value}"
                + (f" · {visita.tipo_visita}" if visita.tipo_visita else ""),
            )
            for visita, nome_promotor in linhas
        ]

    def _eventos_checklists(self, cliente_id: str) -> list[EventoTimeline]:
        linhas = self.session.execute(
            select(Visita.data_visita, Visita.hora_inicio, Checklist.nome, Promotor.nome)
            .select_from(ChecklistResposta)
            .join(Visita, Visita.id == ChecklistResposta.visita_id)
            .join(
                ChecklistPergunta, ChecklistPergunta.id == ChecklistResposta.checklist_pergunta_id
            )
            .join(Checklist, Checklist.id == ChecklistPergunta.checklist_id)
            .join(Promotor, Promotor.id == Visita.promotor_id)
            .where(Visita.cliente_id == cliente_id)
            .distinct()
            .order_by(Visita.data_visita.desc())
            .limit(_LIMITE_EVENTOS_POR_FONTE)
        ).all()
        return [
            EventoTimeline(
                tipo="CHECKLIST",
                data=datetime.combine(data_visita, hora_inicio or time.min),
                titulo=f"Checklist: {nome_checklist}",
                descricao=f"Aplicado por {nome_promotor}",
            )
            for data_visita, hora_inicio, nome_checklist, nome_promotor in linhas
        ]

    def _eventos_importacoes(self, cliente_id: str) -> list[EventoTimeline]:
        ids_faturamento = select(Faturamento.importacao_id).where(
            Faturamento.cliente_id == cliente_id
        )
        ids_carteira = select(Carteira.importacao_id).where(Carteira.cliente_id == cliente_id)
        ids_visita = select(Visita.importacao_id).where(Visita.cliente_id == cliente_id)
        ids_avert = select(CarteiraAvert.importacao_id).where(
            CarteiraAvert.cliente_id == cliente_id
        )
        ids_unidos = ids_faturamento.union(ids_carteira, ids_visita, ids_avert).subquery()

        importacoes = self.session.scalars(
            select(Importacao)
            .where(Importacao.id.in_(select(ids_unidos.c.importacao_id)))
            .order_by(Importacao.criado_em.desc())
            .limit(_LIMITE_EVENTOS_POR_FONTE)
        ).all()
        return [
            EventoTimeline(
                tipo="IMPORTACAO",
                data=importacao.criado_em,
                titulo=f"Importação de {importacao.tipo_arquivo.value}",
                descricao=f"{importacao.nome_arquivo_original} · {importacao.status.value}",
            )
            for importacao in importacoes
        ]

    def _eventos_alteracoes_cadastrais(self, cliente_id: str) -> list[EventoTimeline]:
        logs = self.session.scalars(
            select(LogAuditoria)
            .where(LogAuditoria.entidade == "clientes", LogAuditoria.entidade_id == cliente_id)
            .order_by(LogAuditoria.criado_em.desc())
            .limit(_LIMITE_EVENTOS_POR_FONTE)
        ).all()

        eventos = []
        for log in logs:
            if log.acao == AcaoAuditoria.CRIACAO:
                titulo, descricao = "Cliente cadastrado", None
            else:
                campos = sorted(set((log.dados_depois or {}).keys()) - {"importacao_id"})
                titulo = "Dados cadastrais atualizados"
                descricao = f"Campos alterados: {', '.join(campos)}" if campos else None
            eventos.append(
                EventoTimeline(
                    tipo="ALTERACAO_CADASTRAL",
                    data=log.criado_em,
                    titulo=titulo,
                    descricao=descricao,
                )
            )
        return eventos
