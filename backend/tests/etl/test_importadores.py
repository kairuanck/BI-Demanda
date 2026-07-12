"""Testes dos 5 importadores: banco vazio, banco com dados e regras específicas."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import (
    StatusCarteira,
    StatusImportacao,
    TipoArquivoImportacao,
    TipoPromotor,
    TipoPromotorAlvo,
    TipoRespostaChecklist,
)
from app.infrastructure.models import (
    Carteira,
    Checklist,
    ChecklistPergunta,
    ChecklistResposta,
    Cliente,
    Faturamento,
    Promotor,
    Supervisor,
    TipoPromotorCadastro,
    Usuario,
    Visita,
)
from etl.arquivos import FluxoArquivos
from etl.motor import MotorImportacao
from tests.etl.fixtures_xlsx import (
    xlsx_carteira,
    xlsx_checklist,
    xlsx_clientes,
    xlsx_faturamento,
    xlsx_visitas,
)


def _importar_clientes(motor: MotorImportacao, fluxo: FluxoArquivos, usuario: Usuario) -> None:
    resultado = motor.importar(
        xlsx_clientes(fluxo, f"clientes_{len(list(fluxo.processed.iterdir()))}.xlsx"),
        TipoArquivoImportacao.CLIENTES,
        usuario.id,
    )
    assert resultado.status == StatusImportacao.CONCLUIDA


def _importar_carteira(motor: MotorImportacao, fluxo: FluxoArquivos, usuario: Usuario) -> None:
    resultado = motor.importar(
        xlsx_carteira(fluxo, f"carteira_{len(list(fluxo.processed.iterdir()))}.xlsx"),
        TipoArquivoImportacao.CARTEIRA,
        usuario.id,
    )
    assert resultado.status == StatusImportacao.CONCLUIDA


# ------------------------------------------------------------------- Clientes


def test_importador_clientes_com_linhas_mistas(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    linhas = [
        ["C001", "Cliente Válido", None, None, "SP", "Campinas", None, "Pet Shop"],
        [None, "Sem Código", None, None, "SP", "Campinas", None, None],  # CAM-001
        ["C002", "UF Errada", None, None, "XX", "Cidade", None, None],  # REF-001
        ["C001", "Duplicado no Arquivo", None, None, "SP", "Campinas", None, None],  # CLI-001
        ["C003", "CNPJ Ruim", None, "123", "SP", "Campinas", None, None],  # CLI-002
    ]
    importacao = motor.importar(
        xlsx_clientes(fluxo, linhas=linhas), TipoArquivoImportacao.CLIENTES, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS
    assert importacao.linhas_validas == 1
    assert importacao.linhas_invalidas == 4
    clientes = list(sessao.scalars(select(Cliente)))
    assert len(clientes) == 1
    assert clientes[0].codigo_externo == "C001"


def test_importador_clientes_atualiza_cadastro_existente(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    """Banco com dados: reimportação faz upsert (REGRAS_DE_NEGOCIO.md, seção 5.1)."""

    _importar_clientes(motor, fluxo, usuario_admin)
    linhas_novas = [
        [
            "C001",
            "Pet Shop Alfa RENOMEADO",
            "Pet Alfa",
            None,
            "MG",
            "Belo Horizonte",
            None,
            "Pet Shop",
        ],
        ["C099", "Cliente Novo", None, None, "SP", "Santos", None, "Clínica Veterinária"],
    ]
    importacao = motor.importar(
        xlsx_clientes(fluxo, "clientes_v2.xlsx", linhas=linhas_novas),
        TipoArquivoImportacao.CLIENTES,
        usuario_admin.id,
    )

    assert importacao.status == StatusImportacao.CONCLUIDA
    c001 = sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "C001"))
    assert c001 is not None
    assert c001.razao_social == "Pet Shop Alfa RENOMEADO"
    assert c001.uf_sigla == "MG"
    # os demais clientes da 1ª importação não foram excluídos
    assert sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "C002")) is not None
    assert sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "C099")) is not None


# ------------------------------------------------------------------- Carteira


def test_importador_carteira_cria_promotores_supervisores_e_vinculos(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    _importar_carteira(motor, fluxo, usuario_admin)

    assert len(list(sessao.scalars(select(Supervisor)))) == 1
    promotores = {p.codigo_externo: p for p in sessao.scalars(select(Promotor))}
    assert set(promotores) == {"P001", "P002"}
    tipo_p001 = sessao.get(TipoPromotorCadastro, promotores["P001"].tipo_promotor_id)
    assert tipo_p001 is not None
    assert tipo_p001.codigo == TipoPromotor.TECNICO.value
    vinculos = list(sessao.scalars(select(Carteira)))
    assert len(vinculos) == 3
    assert all(v.status == StatusCarteira.ATIVA for v in vinculos)


def test_importador_carteira_troca_de_promotor_versiona_vigencia(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    """Banco com dados: troca encerra o vínculo anterior sem apagá-lo."""

    _importar_clientes(motor, fluxo, usuario_admin)
    _importar_carteira(motor, fluxo, usuario_admin)

    nova_data = date(2026, 7, 1)
    linhas_v2 = [
        # C001 muda de P001 para P002; C002 mantém P001; C003 sai do arquivo
        ["C001", "P002", "Promotor Dois", "TRADE", "S001", "Supervisor Um", nova_data],
        ["C002", "P001", "Promotor Um", "TECNICO", "S001", "Supervisor Um", nova_data],
    ]
    importacao = motor.importar(
        xlsx_carteira(fluxo, "carteira_v2.xlsx", linhas=linhas_v2),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
    )
    assert importacao.status == StatusImportacao.CONCLUIDA

    cliente_c001 = sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "C001"))
    cliente_c003 = sessao.scalar(select(Cliente).where(Cliente.codigo_externo == "C003"))
    assert cliente_c001 is not None and cliente_c003 is not None

    vinculos_c001 = list(
        sessao.scalars(select(Carteira).where(Carteira.cliente_id == cliente_c001.id))
    )
    assert len(vinculos_c001) == 2  # histórico preservado: encerrado + novo
    encerrado = next(v for v in vinculos_c001 if v.status == StatusCarteira.ENCERRADA)
    vigente = next(v for v in vinculos_c001 if v.status == StatusCarteira.ATIVA)
    assert encerrado.data_fim_vigencia == nova_data
    assert vigente.data_inicio_vigencia == nova_data

    # C003 ausente no novo arquivo: vínculo encerrado automaticamente
    vinculo_c003 = sessao.scalar(select(Carteira).where(Carteira.cliente_id == cliente_c003.id))
    assert vinculo_c003 is not None
    assert vinculo_c003.status == StatusCarteira.ENCERRADA


def test_importador_carteira_e_idempotente_para_mesmo_promotor(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    _importar_carteira(motor, fluxo, usuario_admin)
    total_antes = len(list(sessao.scalars(select(Carteira))))

    linhas_iguais = [
        ["C001", "P001", "Promotor Um", "TECNICO", "S001", "Supervisor Um", date(2026, 7, 15)],
        ["C002", "P001", "Promotor Um", "TECNICO", "S001", "Supervisor Um", date(2026, 7, 15)],
        ["C003", "P002", "Promotor Dois", "TRADE", "S001", "Supervisor Um", date(2026, 7, 15)],
    ]
    motor.importar(
        xlsx_carteira(fluxo, "carteira_repetida.xlsx", linhas=linhas_iguais),
        TipoArquivoImportacao.CARTEIRA,
        usuario_admin.id,
    )
    total_depois = len(list(sessao.scalars(select(Carteira))))
    assert total_depois == total_antes  # nenhum vínculo novo: mesmos promotores


# ---------------------------------------------------------------- Faturamento


def test_importador_faturamento_insere_e_aceita_estorno_negativo(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    importacao = motor.importar(
        xlsx_faturamento(fluxo), TipoArquivoImportacao.FATURAMENTO, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.CONCLUIDA
    faturamentos = list(sessao.scalars(select(Faturamento)))
    assert len(faturamentos) == 3
    valores = sorted(f.valor_faturado for f in faturamentos)
    assert str(valores[0]) == "-120.00"  # estorno preservado (FAT-003)


def test_importador_faturamento_rejeita_mes_e_ano_invalidos(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    linhas = [
        ["C001", "L01", "Lab", "D01", "Dep", None, None, 2026, 13, "10,00", None],  # FAT-002
        ["C001", "L01", "Lab", "D01", "Dep", None, None, 1999, 5, "10,00", None],  # FAT-001
        ["C001", "L01", "Lab", "D01", "Dep", None, None, 2026, 5, "abc", None],  # FAT-003
        ["C001", "L01", "Lab", "D01", "Dep", None, None, 2026, 5, "10,00", None],  # válida
    ]
    importacao = motor.importar(
        xlsx_faturamento(fluxo, linhas=linhas), TipoArquivoImportacao.FATURAMENTO, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS
    assert importacao.linhas_validas == 1
    assert importacao.linhas_invalidas == 3


def test_reimportacao_de_faturamento_nunca_sobrescreve(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    """Regra "Nunca sobrescrever" (TESTES.md, seção 10, item 1)."""

    _importar_clientes(motor, fluxo, usuario_admin)
    motor.importar(
        xlsx_faturamento(fluxo, "fat_v1.xlsx"), TipoArquivoImportacao.FATURAMENTO, usuario_admin.id
    )
    linhas_v2 = [
        ["C001", "L01", "Lab Um", "D01", "Nutrição", None, None, 2026, 5, "9999,99", None],
    ]
    motor.importar(
        xlsx_faturamento(fluxo, "fat_v2.xlsx", linhas=linhas_v2),
        TipoArquivoImportacao.FATURAMENTO,
        usuario_admin.id,
    )

    faturamentos = list(sessao.scalars(select(Faturamento)))
    assert len(faturamentos) == 4  # 3 da v1 + 1 da v2, todos fisicamente preservados


# -------------------------------------------------------------------- Visitas


def test_importador_visitas_com_referencias_validas_e_invalidas(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    _importar_carteira(motor, fluxo, usuario_admin)

    linhas = [
        ["P001", "C001", date(2026, 6, 10), "09:00", "10:00", "Rotina", "REALIZADA"],
        ["P999", "C001", date(2026, 6, 10), None, None, None, None],  # REF-003
        ["P001", "C999", date(2026, 6, 10), None, None, None, None],  # REF-002
        ["P001", "C002", date(2099, 1, 1), None, None, None, None],  # VIS-001 futura
        ["P001", "C002", date(2026, 6, 11), "10:00", "09:00", None, None],  # VIS-002
    ]
    importacao = motor.importar(
        xlsx_visitas(fluxo, linhas=linhas), TipoArquivoImportacao.VISITAS, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS
    assert importacao.linhas_validas == 1
    assert len(list(sessao.scalars(select(Visita)))) == 1


# ------------------------------------------------------------------ Checklist


def _criar_template_checklist(sessao: Session) -> None:
    template = Checklist(nome="Checklist Técnico Padrão", tipo_promotor_alvo=TipoPromotorAlvo.AMBOS)
    sessao.add(template)
    sessao.flush()
    sessao.add_all(
        [
            ChecklistPergunta(
                checklist_id=template.id,
                ordem=1,
                enunciado="Produto exposto corretamente?",
                tipo_resposta=TipoRespostaChecklist.SIM_NAO,
            ),
            ChecklistPergunta(
                checklist_id=template.id,
                ordem=2,
                enunciado="Observações da gôndola",
                tipo_resposta=TipoRespostaChecklist.TEXTO,
            ),
        ]
    )
    sessao.commit()


def test_importador_checklist_calcula_conformidade(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    _importar_carteira(motor, fluxo, usuario_admin)
    _criar_template_checklist(sessao)
    motor.importar(xlsx_visitas(fluxo), TipoArquivoImportacao.VISITAS, usuario_admin.id)
    visita_id = sessao.scalars(select(Visita.id)).first()
    assert visita_id is not None

    linhas = [[visita_id, 1, "SIM"], [visita_id, 2, "Tudo em ordem"]]
    importacao = motor.importar(
        xlsx_checklist(fluxo, linhas=linhas), TipoArquivoImportacao.CHECKLIST, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.CONCLUIDA
    respostas = {r.checklist_pergunta_id: r for r in sessao.scalars(select(ChecklistResposta))}
    assert len(respostas) == 2
    conformes = [r.conforme for r in respostas.values()]
    assert True in conformes  # SIM_NAO respondida com SIM
    assert None in conformes  # TEXTO não compõe conformidade


def test_importador_checklist_rejeita_visita_inexistente_e_duplicidade(
    motor: MotorImportacao, fluxo: FluxoArquivos, usuario_admin: Usuario, ufs: None, sessao: Session
) -> None:
    _importar_clientes(motor, fluxo, usuario_admin)
    _importar_carteira(motor, fluxo, usuario_admin)
    _criar_template_checklist(sessao)
    motor.importar(xlsx_visitas(fluxo), TipoArquivoImportacao.VISITAS, usuario_admin.id)
    visita_id = sessao.scalars(select(Visita.id)).first()
    assert visita_id is not None

    linhas = [
        [visita_id, 1, "SIM"],
        [visita_id, 1, "NAO"],  # CHK-004: duplicada no arquivo
        [99999, 1, "SIM"],  # REF-004: visita inexistente
        [visita_id, 99, "SIM"],  # REF-005: ordem inexistente no template
    ]
    importacao = motor.importar(
        xlsx_checklist(fluxo, linhas=linhas), TipoArquivoImportacao.CHECKLIST, usuario_admin.id
    )

    assert importacao.status == StatusImportacao.CONCLUIDA_COM_ERROS
    assert importacao.linhas_validas == 1
    assert importacao.linhas_invalidas == 3
