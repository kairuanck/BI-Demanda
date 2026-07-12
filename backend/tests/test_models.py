"""Testes de estrutura do banco e relacionamentos (DICIONARIO_DE_DADOS.md +
adaptações da Sprint 3 aos dados reais, docs/DECISIONS.md, seção 13)."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.enums import PerfilUsuario, StatusCarteira, TipoArquivoImportacao, TipoPromotor
from app.infrastructure.database import engine
from app.infrastructure.models import (
    Carteira,
    Cidade,
    Cliente,
    Empresa,
    Importacao,
    Promotor,
    Supervisor,
    TipoPromotorCadastro,
    Uf,
    Usuario,
)

TABELAS_ESPERADAS = {
    "usuarios",
    "supervisores",
    "promotores",
    "vendedores",
    "laboratorios",
    "departamentos",
    "ufs",
    "cidades",
    "clientes",
    "carteiras",
    "faturamentos",
    "visitas",
    "checklists",
    "checklist_perguntas",
    "checklist_respostas",
    "importacoes",
    "importacao_erros",
    "importacao_arquivos",
    "logs_auditoria",
    "empresas",
    # Sprint 3 — dados reais
    "tipos_promotor",
    "clientes_integracao",
    "visitas_resumo_sb",
    "carteiras_avert",
    "visitas_produtos_sb",
    "clientes_vendedores",
}


def test_todas_as_26_tabelas_existem_apos_migracao() -> None:
    inspetor = inspect(engine)
    tabelas_existentes = set(inspetor.get_table_names())

    faltando = TABELAS_ESPERADAS - tabelas_existentes
    assert not faltando, f"Tabelas ausentes após a migração: {faltando}"


def test_chave_estrangeira_promotor_supervisor_configurada() -> None:
    inspetor = inspect(engine)
    fks = inspetor.get_foreign_keys("promotores")
    colunas_fk = {fk["constrained_columns"][0] for fk in fks}

    assert "supervisor_id" in colunas_fk
    assert "tipo_promotor_id" in colunas_fk


def test_tipos_promotor_semeados_pela_migracao(sessao: Session) -> None:
    """O seed cadastral TECNICO/TRADE é aplicado pela própria migração."""

    codigos = set(sessao.scalars(select(TipoPromotorCadastro.codigo)))
    assert {TipoPromotor.TECNICO.value, TipoPromotor.TRADE.value} <= codigos


def test_relacionamento_carteira_exige_cliente_e_promotor_validos(
    sessao: Session, usuario_admin: Usuario, ufs: None
) -> None:
    """Integridade referencial: FK inválida é rejeitada (PRAGMA foreign_keys=ON)."""

    importacao = Importacao(
        tipo_arquivo=TipoArquivoImportacao.CARTEIRA,
        nome_arquivo_original="x.xlsx",
        hash_sha256="0" * 64,
        tamanho_bytes=10,
        usuario_id=usuario_admin.id,
    )
    sessao.add(importacao)
    sessao.commit()

    vinculo_invalido = Carteira(
        promotor_id="inexistente-99999",
        cliente_id="inexistente-99999",
        importacao_id=importacao.id,
        data_inicio_vigencia=date(2026, 1, 1),
        status=StatusCarteira.ATIVA,
    )
    sessao.add(vinculo_invalido)
    with pytest.raises(IntegrityError):
        sessao.commit()
    sessao.rollback()


def test_relacionamento_completo_cliente_promotor_carteira(
    sessao: Session, usuario_admin: Usuario, ufs: None
) -> None:
    cidade = Cidade(nome="Campinas", uf_sigla="SP")
    sessao.add(cidade)
    sessao.flush()
    cliente = Cliente(
        codigo_externo="C900",
        razao_social="Cliente Relacionamento",
        uf_sigla="SP",
        cidade_id=cidade.id,
    )
    supervisor = Supervisor(nome="Sup Rel", codigo_externo="S900")
    sessao.add_all([cliente, supervisor])
    sessao.flush()
    tipo_tecnico = sessao.scalar(
        select(TipoPromotorCadastro).where(
            TipoPromotorCadastro.codigo == TipoPromotor.TECNICO.value
        )
    )
    assert tipo_tecnico is not None
    promotor = Promotor(
        nome="Pro Rel",
        codigo_externo="P900",
        tipo_promotor_id=tipo_tecnico.id,
        supervisor_id=supervisor.id,
    )
    sessao.add(promotor)
    sessao.flush()
    importacao = Importacao(
        tipo_arquivo=TipoArquivoImportacao.CARTEIRA,
        nome_arquivo_original="rel.xlsx",
        hash_sha256="1" * 64,
        tamanho_bytes=10,
        usuario_id=usuario_admin.id,
    )
    sessao.add(importacao)
    sessao.flush()
    vinculo = Carteira(
        promotor_id=promotor.id,
        cliente_id=cliente.id,
        importacao_id=importacao.id,
        data_inicio_vigencia=date(2026, 6, 1),
    )
    sessao.add(vinculo)
    sessao.commit()

    assert vinculo.id is not None
    assert sessao.get(Uf, "SP") is not None


def test_identidade_uuid_interna_em_todas_as_entidades(
    sessao: Session, usuario_admin: Usuario
) -> None:
    """Diretriz Sprint 3: UUID interno como identidade (docs/DECISIONS.md, 13)."""

    empresa = Empresa(nome="Empresa UUID", cnpj="98765432000100")
    sessao.add(empresa)
    sessao.commit()

    for entidade in (usuario_admin, empresa):
        assert isinstance(entidade.id, str) and len(entidade.id) == 36


def test_empresa_possui_soft_delete_e_auditoria(sessao: Session, usuario_admin: Usuario) -> None:
    empresa = Empresa(nome="Empresa Teste", cnpj="12345678000199", criado_por=usuario_admin.id)
    sessao.add(empresa)
    sessao.commit()

    assert empresa.id and len(empresa.id) == 36
    assert empresa.criado_em is not None
    assert empresa.deletado_em is None
    assert empresa.criado_por == usuario_admin.id


def test_usuario_admin_criado(usuario_admin: Usuario) -> None:
    assert usuario_admin.perfil == PerfilUsuario.ADMINISTRADOR
