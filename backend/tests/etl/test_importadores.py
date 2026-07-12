"""Testes dos conectores reais (Sprint 3, Fase 7).

Cada teste usa planilhas sintéticas com as ESTRUTURAS REAIS descobertas na
engenharia reversa (fixtures_reais.py) e dados 100% fictícios.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import (
    CategoriaComercial,
    SistemaOrigem,
    StatusCarteira,
    StatusConciliacao,
    StatusImportacao,
    TipoArquivoImportacao,
    TipoPromotor,
)
from app.infrastructure.models import (
    Carteira,
    CarteiraAvert,
    Checklist,
    ChecklistPergunta,
    ChecklistResposta,
    Cliente,
    ClienteIntegracao,
    ClienteVendedor,
    Faturamento,
    Laboratorio,
    Promotor,
    TipoPromotorCadastro,
    Usuario,
    Vendedor,
    Visita,
    VisitaProdutoSb,
    VisitaResumoSb,
)
from etl.arquivos import FluxoArquivos
from etl.motor import MotorImportacao
from tests.etl.fixtures_reais import (
    xlsx_base_clientes,
    xlsx_checklist_sb,
    xlsx_faturamento_matriz,
    xlsx_painel_avert,
    xlsx_sb_produtos,
    xlsx_sb_supervisor,
    xlsx_wecheck,
)

COMPETENCIA_JUN = date(2026, 6, 1)


def _importar_base(motor: MotorImportacao, fluxo: FluxoArquivos, usuario: Usuario, nome: str):
    importacao = motor.importar(
        xlsx_base_clientes(fluxo, nome), TipoArquivoImportacao.CLIENTES, usuario.id
    )
    assert importacao.status == StatusImportacao.CONCLUIDA
    return importacao


# ------------------------------------------------------------ Base de Clientes


def test_base_clientes_real_cria_clientes_completos_e_vinculos_rca(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    clientes = {c.codigo_externo: c for c in sessao.scalars(select(Cliente))}
    assert set(clientes) == {"10001", "10002", "10003"}
    alfa = clientes["10001"]
    assert alfa.tipo_pessoa == "Jurídica(J)"
    assert alfa.ramo_atividade == "PET SHOP"
    assert alfa.bairro == "CENTRO"
    assert alfa.cep == "13000-000"
    assert alfa.data_ultima_compra is not None
    assert clientes["10003"].tipo_pessoa == "Física(F)"

    vendedores = {v.codigo_externo for v in sessao.scalars(select(Vendedor))}
    assert vendedores == {"77", "88"}
    vinculos = list(sessao.scalars(select(ClienteVendedor)))
    assert len(vinculos) == 3  # 10001: RCA1; 10002: RCA1+RCA2; 10003: nenhum
    por_cliente = {clientes["10002"].id: 0}
    for vinculo in vinculos:
        por_cliente[vinculo.cliente_id] = por_cliente.get(vinculo.cliente_id, 0) + 1
    assert por_cliente[clientes["10002"].id] == 2


def test_base_clientes_atualiza_cadastro_e_remove_rca_ausente(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    linhas_v2 = [
        [
            "10002",
            "22333444000155",
            None,
            "CLINICA VET BETA RENOMEADA",
            None,
            "Jurídica(J)",
            "CLÍNICA VETERINÁRIA",
            "AV B",
            "200",
            "JARDIM",
            "SÃO PAULO",
            "SP",
            "01000-000",
            None,
            "99",
            "VENDEDOR NOVENTA E NOVE",
            None,
            None,
            None,
            None,
            None,
            None,
        ],
    ]
    importacao = motor.importar(
        xlsx_base_clientes(fluxo, "base_v2.xlsx", linhas=linhas_v2),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    beta = sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "10002"))
    assert beta is not None
    assert beta.razao_social == "CLINICA VET BETA RENOMEADA"
    vinculos = list(
        sessao.scalars(select(ClienteVendedor).where(ClienteVendedor.cliente_id == beta.id))
    )
    assert len(vinculos) == 1  # RCA 88 saiu; RCA1 agora é 99
    vendedor = sessao.get(Vendedor, vinculos[0].vendedor_id)
    assert vendedor is not None and vendedor.codigo_externo == "99"


def test_base_clientes_linha_com_uf_invalida_gera_erro_por_linha(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    linhas = [
        [
            "10001",
            None,
            None,
            "CLIENTE OK",
            None,
            None,
            None,
            None,
            None,
            None,
            "CAMPINAS",
            "SP",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        [
            "10009",
            None,
            None,
            "CLIENTE UF RUIM",
            None,
            None,
            None,
            None,
            None,
            None,
            "CIDADE",
            "XX",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
    ]
    importacao = motor.importar(
        xlsx_base_clientes(fluxo, "base_mista.xlsx", linhas=linhas),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS
    assert importacao.linhas_validas == 1
    assert importacao.linhas_invalidas == 1


# ---------------------------------------------------------- Faturamento (wide)


def test_faturamento_matriz_vira_long_com_competencia_do_rodape(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    importacao = motor.importar(
        xlsx_faturamento_matriz(fluxo), TipoArquivoImportacao.FATURAMENTO, usuario_admin.id
    )
    assert importacao.status == StatusImportacao.CONCLUIDA
    assert importacao.competencia == date(2026, 1, 1)

    faturamentos = list(sessao.scalars(select(Faturamento)))
    assert len(faturamentos) == 5  # células preenchidas da matriz
    assert all(f.ano == 2026 and f.mes == 1 for f in faturamentos)
    assert all(f.departamento_id is None for f in faturamentos)
    valores = sorted(float(f.valor_faturado) for f in faturamentos)
    assert valores[0] == -120.00  # devolução líquida preservada

    laboratorios = {lab.nome: lab for lab in sessao.scalars(select(Laboratorio))}
    assert laboratorios["BRINDE"].categoria == CategoriaComercial.BRINDE
    assert laboratorios["AVERT"].categoria == CategoriaComercial.LABORATORIO


def test_faturamento_cliente_fora_da_base_gera_erro_por_celula(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    linhas = [
        ("10001 - PET SHOP ALFA LTDA", ["100.00", None, None]),
        ("99999 - CLIENTE FANTASMA", ["50.00", None, None]),
    ]
    importacao = motor.importar(
        xlsx_faturamento_matriz(fluxo, "fat_fantasma.xlsx", linhas_clientes=linhas),
        TipoArquivoImportacao.FATURAMENTO,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS
    assert importacao.linhas_validas == 1
    assert importacao.linhas_invalidas == 1


def test_faturamento_nunca_sobrescreve_valor_divergente(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")
    motor.importar(
        xlsx_faturamento_matriz(fluxo, "fat_v1.xlsx"),
        TipoArquivoImportacao.FATURAMENTO,
        usuario_admin.id,
    )

    linhas_v2 = [
        ("10001 - PET SHOP ALFA LTDA", ["396.07", "555.55", "10.00"]),  # BBPET é novo
        ("10002 - CLINICA VET BETA", [None, "999.99", None]),  # divergente: era 1250.50
    ]
    importacao = motor.importar(
        xlsx_faturamento_matriz(fluxo, "fat_v2.xlsx", linhas_clientes=linhas_v2),
        TipoArquivoImportacao.FATURAMENTO,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS

    beta = sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "10002"))
    bbpet = sessao.scalar(select(Laboratorio).where(Laboratorio.nome == "BBPET"))
    assert beta is not None and bbpet is not None
    registro = sessao.scalar(
        select(Faturamento).where(
            Faturamento.cliente_id == beta.id, Faturamento.laboratorio_id == bbpet.id
        )
    )
    assert registro is not None
    assert float(registro.valor_faturado) == 1250.50  # nunca sobrescrito


# --------------------------------------------- SB Supervisor (carteira mensal)


def test_sb_supervisor_exige_competencia(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    importacao = motor.importar(
        xlsx_sb_supervisor(fluxo), TipoArquivoImportacao.CARTEIRA, usuario_admin.id
    )
    assert importacao.status == StatusImportacao.FALHOU


def test_sb_supervisor_carrega_resumo_e_deriva_carteira(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    importacao = motor.importar(
        xlsx_sb_supervisor(fluxo),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=COMPETENCIA_JUN,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    promotores = {p.codigo_externo: p for p in sessao.scalars(select(Promotor))}
    assert set(promotores) == {"0343", "0777"}
    assert promotores["0343"].area == "RS"
    # tipo é cadastral: NUNCA inferido na importação (docs/DECISIONS.md, 12.3)
    assert promotores["0343"].tipo_promotor_id is None

    resumos = list(sessao.scalars(select(VisitaResumoSb)))
    assert len(resumos) == 3
    assert all(r.competencia == COMPETENCIA_JUN for r in resumos)
    assert {r.visitas_previstas for r in resumos} == {19, 5}

    vinculos = list(sessao.scalars(select(Carteira)))
    assert len(vinculos) == 3
    assert all(v.status == StatusCarteira.ATIVA for v in vinculos)


def test_sb_supervisor_troca_de_promotor_versiona_vigencia_e_encerra_ausentes(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")
    motor.importar(
        xlsx_sb_supervisor(fluxo, "sb_jun.xlsx"),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=COMPETENCIA_JUN,
    )

    competencia_jul = date(2026, 7, 1)
    linhas_jul = [
        # 10001 muda de 0343 para 0777; 10002 mantém 0343; 10003 sai do arquivo
        [
            "0777",
            "PROMOTOR DOIS",
            "SP",
            "6",
            "6",
            "0",
            "0",
            "10001",
            "PET ALFA",
            "PET SHOP ALFA LTDA",
            "1",
            "1",
            "0",
            "0%",
            "100%",
            "0%",
        ],
        [
            "0343",
            "PROMOTORA UM",
            "RS",
            "12",
            "9",
            "3",
            "1",
            "10002",
            None,
            "CLINICA VET BETA",
            "1",
            "1",
            "0",
            "0%",
            "100%",
            "0%",
        ],
    ]
    importacao = motor.importar(
        xlsx_sb_supervisor(fluxo, "sb_jul.xlsx", linhas=linhas_jul),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=competencia_jul,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    clientes = {c.codigo_externo: c for c in sessao.scalars(select(Cliente))}
    vinculos_10001 = list(
        sessao.scalars(select(Carteira).where(Carteira.cliente_id == clientes["10001"].id))
    )
    assert len(vinculos_10001) == 2
    encerrado = next(v for v in vinculos_10001 if v.status == StatusCarteira.ENCERRADA)
    assert encerrado.data_fim_vigencia == competencia_jul
    vinculo_10003 = sessao.scalar(
        select(Carteira).where(Carteira.cliente_id == clientes["10003"].id)
    )
    assert vinculo_10003 is not None
    assert vinculo_10003.status == StatusCarteira.ENCERRADA  # ausente no snapshot


def test_sb_supervisor_cliente_fora_da_base_vira_pendencia(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    linhas = [
        [
            "0343",
            "PROMOTORA UM",
            "RS",
            "1",
            "1",
            "0",
            "0",
            "10999",
            "SEM CADASTRO",
            "LOJA SEM CADASTRO",
            "1",
            "1",
            "0",
            "0%",
            "100%",
            "0%",
        ],
    ]
    importacao = motor.importar(
        xlsx_sb_supervisor(fluxo, "sb_pendente.xlsx", linhas=linhas),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=COMPETENCIA_JUN,
    )
    assert importacao.status == StatusImportacao.FALHOU  # nenhuma linha válida

    pendencia = sessao.scalar(
        select(ClienteIntegracao).where(
            ClienteIntegracao.sistema_origem == SistemaOrigem.SB_PROMOTOR,
            ClienteIntegracao.codigo_origem == "10999",
        )
    )
    assert pendencia is not None
    assert pendencia.status == StatusConciliacao.PENDENTE
    assert pendencia.cliente_id is None  # nunca cria cliente automaticamente


# ----------------------------------------------------------- SB Produtos


def test_sb_produtos_carrega_detalhe_por_visita(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    importacao = motor.importar(
        xlsx_sb_produtos(fluxo), TipoArquivoImportacao.SB_PRODUTOS, usuario_admin.id
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    detalhes = list(sessao.scalars(select(VisitaProdutoSb)))
    assert len(detalhes) == 1
    detalhe = detalhes[0]
    assert detalhe.codigo_visita_externa == "29883"
    assert detalhe.grupo_marca == "BBPET"
    assert detalhe.uf_sigla == "RS"
    assert detalhe.data_inicial == date(2026, 6, 3)


# ------------------------------------------------- Checklists SB (8 abas wide)


def test_checklist_sb_cria_templates_visitas_e_respostas(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    importacao = motor.importar(
        xlsx_checklist_sb(fluxo), TipoArquivoImportacao.CHECKLIST, usuario_admin.id
    )
    assert importacao.status == StatusImportacao.CONCLUIDA
    assert importacao.total_linhas == 2

    templates = {t.codigo_externo: t for t in sessao.scalars(select(Checklist))}
    assert set(templates) == {"6", "7"}
    assert all(t.origem == SistemaOrigem.SB_PROMOTOR for t in templates.values())
    assert all(t.tipo_promotor_alvo is None for t in templates.values())  # nunca inferido

    perguntas = list(sessao.scalars(select(ChecklistPergunta)))
    assert len(perguntas) == 6  # 3 colunas de pergunta × 2 templates
    assert all(p.obrigatoria is False for p in perguntas)

    visitas = {v.codigo_externo: v for v in sessao.scalars(select(Visita))}
    assert set(visitas) == {"29883", "29884"}
    assert all(v.origem == SistemaOrigem.SB_PROMOTOR for v in visitas.values())
    assert visitas["29883"].data_visita == date(2026, 6, 5)
    assert visitas["29883"].hora_inicio is not None

    respostas = list(sessao.scalars(select(ChecklistResposta)))
    assert len(respostas) == 3  # apenas células preenchidas (wide→long)


def test_checklist_sb_resposta_divergente_nunca_sobrescreve(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")
    motor.importar(
        xlsx_checklist_sb(fluxo, "ck_v1.xlsx"), TipoArquivoImportacao.CHECKLIST, usuario_admin.id
    )

    abas_v2 = {
        "Check-list Visita Técnica": {
            "ck_id": 6,
            "checklist": "Check-list Visita Técnica",
            "linhas": [
                [
                    "0343",
                    "PROMOTORA UM",
                    "RS",
                    "10001",
                    "PET SHOP ALFA LTDA",
                    "PET ALFA",
                    "29883",
                    "05/06/2026 10:30",
                    "TEXTO ALTERADO",
                    None,
                    "77",
                ],
            ],
        },
    }
    importacao = motor.importar(
        xlsx_checklist_sb(fluxo, "ck_v2.xlsx", abas=abas_v2),
        TipoArquivoImportacao.CHECKLIST,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.FALHOU  # única linha conflitou

    visita = sessao.scalar(select(Visita).where(Visita.codigo_externo == "29883"))
    assert visita is not None
    respostas = {
        sessao.get(ChecklistPergunta, r.checklist_pergunta_id).enunciado: r.resposta_valor
        for r in sessao.scalars(
            select(ChecklistResposta).where(ChecklistResposta.visita_id == visita.id)
        )
    }
    assert respostas["Descrever a visita"] == "Visita produtiva"  # valor original mantido


# ------------------------------------------------------------------- WeCheck


def test_wecheck_cria_visitas_sem_cliente_com_pendencia_de_conciliacao(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    importacao = motor.importar(
        xlsx_wecheck(fluxo), TipoArquivoImportacao.WECHECK, usuario_admin.id
    )
    assert importacao.status == StatusImportacao.CONCLUIDA
    assert importacao.total_linhas == 2

    promotora = sessao.scalar(select(Promotor).where(Promotor.nome == "PROMOTORA WECHECK UM"))
    assert promotora is not None
    tipo = sessao.get(TipoPromotorCadastro, promotora.tipo_promotor_id)
    assert tipo is not None
    assert tipo.codigo == TipoPromotor.TRADE.value  # 12.6: promotoras WeCheck são Trade

    visitas = list(sessao.scalars(select(Visita).where(Visita.origem == SistemaOrigem.WECHECK)))
    assert len(visitas) == 2
    assert all(v.cliente_id is None for v in visitas)  # sem código de cliente na origem
    assert all(v.cliente_integracao_id is not None for v in visitas)
    assert {v.local_texto for v in visitas} == {"AGROPET EXEMPLO", "PETSHOP MODELO"}

    pendencias = list(
        sessao.scalars(
            select(ClienteIntegracao).where(
                ClienteIntegracao.sistema_origem == SistemaOrigem.WECHECK
            )
        )
    )
    assert len(pendencias) == 2
    assert all(p.status == StatusConciliacao.PENDENTE for p in pendencias)

    template = sessao.scalar(select(Checklist).where(Checklist.origem == SistemaOrigem.WECHECK))
    assert template is not None and template.nome == "Visita de Trade"
    respostas = list(sessao.scalars(select(ChecklistResposta)))
    assert len(respostas) == 5  # 3 preenchidas na linha 1 + 2 na linha 2


def test_wecheck_reimportacao_e_idempotente_e_tolera_schema_drift(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    motor.importar(
        xlsx_wecheck(fluxo, "wc_jan.xlsx"), TipoArquivoImportacao.WECHECK, usuario_admin.id
    )

    # mês seguinte: mesmas 2 linhas + 1 nova; pergunta nova (schema drift real)
    perguntas_fev = [
        "Tire fotos da fachada:",
        "Há produtos em ruptura?",
        "Visão crítica da visita:",
        "Há material promocional?",  # coluna nova no mês
    ]
    linhas_fev = [
        [
            "Visita de Trade",
            "15/01/2026 09:12",
            "AGROPET EXEMPLO",
            "RUA X, 1",
            "PORTO ALEGRE",
            "RS",
            "PROMOTORA WECHECK UM",
            "Visita mensal",
            None,
            "https://fotos.exemplo/f.jpg",
            "Não",
            "Loja organizada",
            None,
        ],
        [
            "Visita de Trade",
            "16/01/2026 14:40",
            "PETSHOP MODELO",
            None,
            "CANOAS",
            "RS",
            "PROMOTORA WECHECK UM",
            None,
            None,
            None,
            "Sim",
            "Faltou produto Y",
            None,
        ],
        [
            "Visita de Trade",
            "10/02/2026 11:00",
            "AGROPET EXEMPLO",
            "RUA X, 1",
            "PORTO ALEGRE",
            "RS",
            "PROMOTORA WECHECK UM",
            None,
            None,
            None,
            "Não",
            "Tudo ok",
            "Sim",
        ],
    ]
    importacao = motor.importar(
        xlsx_wecheck(fluxo, "wc_fev.xlsx", perguntas=perguntas_fev, linhas=linhas_fev),
        TipoArquivoImportacao.WECHECK,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    visitas = list(sessao.scalars(select(Visita).where(Visita.origem == SistemaOrigem.WECHECK)))
    assert len(visitas) == 3  # 2 repetidas não duplicaram; 1 nova entrou

    template = sessao.scalar(select(Checklist).where(Checklist.origem == SistemaOrigem.WECHECK))
    assert template is not None
    perguntas = list(
        sessao.scalars(
            select(ChecklistPergunta).where(ChecklistPergunta.checklist_id == template.id)
        )
    )
    assert len(perguntas) == 4  # pergunta nova acrescentada ao template
    # só 1 promotora apesar das reimportações
    promotoras = list(sessao.scalars(select(Promotor)))
    assert len(promotoras) == 1


# --------------------------------------------------------------- Painel Avert


def test_painel_avert_carrega_carteira_e_concilia_por_cnpj(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")

    importacao = motor.importar(
        xlsx_painel_avert(fluxo),
        TipoArquivoImportacao.PAINEL_AVERT,
        usuario_admin.id,
        competencia=COMPETENCIA_JUN,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    carteira = {c.cnpj: c for c in sessao.scalars(select(CarteiraAvert))}
    assert set(carteira) == {"11222333000144", "99888777000166"}

    cliente_alfa = sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "10001"))
    assert cliente_alfa is not None
    assert carteira["11222333000144"].cliente_id == cliente_alfa.id  # casou por CNPJ
    assert carteira["99888777000166"].cliente_id is None  # pendente, nunca cria cliente

    integracoes = {
        i.codigo_origem: i
        for i in sessao.scalars(
            select(ClienteIntegracao).where(
                ClienteIntegracao.sistema_origem == SistemaOrigem.PAINEL_AVERT
            )
        )
    }
    assert integracoes["11222333000144"].status == StatusConciliacao.VINCULADO
    assert integracoes["99888777000166"].status == StatusConciliacao.PENDENTE

    promotora = sessao.scalar(select(Promotor).where(Promotor.nome == "PROMOTORA WECHECK UM"))
    assert promotora is not None  # CONSULTOR = promotora (12.5)
    assert carteira["11222333000144"].promotor_id == promotora.id


# ------------------------------------------- Deduplicação por hash de conteúdo


def test_copia_logicamente_identica_e_recusada_mesmo_com_bytes_diferentes(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None
) -> None:
    """Cenário real: 34/26 cópias do mesmo export com bytes distintos
    (metadados internos do xlsx) — a deduplicação por hash de conteúdo
    precisa recusá-las (docs/DECISIONS.md, 11.2)."""

    _importar_base(motor, fluxo, usuario_admin, "base_v1.xlsx")
    primeira = motor.importar(
        xlsx_sb_supervisor(fluxo, "copia_1.xlsx"),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=COMPETENCIA_JUN,
    )
    assert primeira.status == StatusImportacao.CONCLUIDA

    segunda = motor.importar(
        xlsx_sb_supervisor(fluxo, "copia_2.xlsx"),  # regenerada: bytes podem diferir
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
        competencia=COMPETENCIA_JUN,
    )
    assert segunda.status == StatusImportacao.FALHOU
    assert segunda.versao == 0  # recusada fora da cadeia de versões
    assert segunda.hash_conteudo == primeira.hash_conteudo
