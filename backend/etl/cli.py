"""CLI de importação (Sprint 3, Fase 5).

Endpoint de upload HTTP segue fora de escopo (SPRINT_2_REPORT.md, pendência
1); esta CLI é o caminho operacional para carregar arquivos reais
enquanto ele não existe. Também é o instrumento usado para a carga
completa dos dados reais desta sprint.

Inferência estrutural de tipo (nunca por nome de arquivo — os exports reais
têm nomes livres): cada `TipoArquivoImportacao` tem uma assinatura de abas +
colunas: nome de aba conhecido, ou conjunto de colunas do cabeçalho da
primeira aba. Arquivo que não casa com nenhuma assinatura é reportado como
não reconhecido — nunca importado às cegas.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from app.domain.enums import PerfilUsuario, TipoArquivoImportacao
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Usuario
from etl.arquivos import FluxoArquivos
from etl.conectores.leitura import ler_abas
from etl.motor import MotorImportacao

_ABAS_BASE_CLIENTES = {"CÓDIGO", "CNPJ/CPF", "CLIENTE", "ESTADO"}
_ABAS_SB_PRODUTOS = {"PRODUTOS", "GONDOLA", "PRODUTOSIMILAR", "TAREFAS"}
_COLUNAS_SB_SUPERVISOR = {
    "ÁREA",
    "VISITAS PREVISTAS",
    "PREVISTAS REALIZADAS",
    "NÃO VISITAS",
}
_COLUNAS_PAINEL_AVERT = {"CNPJ", "CONSULTOR", "GRUPO ECONÔMICO", "SEGMENTO"}
_COLUNAS_WECHECK = {"FORMULÁRIO", "AUTOR", "DATA / HORA DO ITEM"}
_COLUNAS_CHECKLIST = {"VISITA", "CK_ID", "APLICAÇÃO"}
_COLUNAS_FATURAMENTO = {"DEPARTAMENTO"}


def inferir_tipo_arquivo(caminho: Path) -> TipoArquivoImportacao | None:
    """Estrutura do arquivo → tipo, nunca o nome (docs/DECISIONS.md, 11.3)."""

    try:
        abas = ler_abas(caminho)
    except Exception:  # noqa: BLE001 - arquivo ilegível: deixa o motor recusar
        return None
    if not abas:
        return None

    titulos = {aba.titulo.strip().upper() for aba in abas}
    if titulos & _ABAS_SB_PRODUTOS:
        return TipoArquivoImportacao.SB_PRODUTOS

    primeira = abas[0]
    cabecalho = {c.strip().upper() for c in primeira.cabecalho() if c}
    if _COLUNAS_CHECKLIST <= cabecalho:
        return TipoArquivoImportacao.CHECKLIST
    if _COLUNAS_SB_SUPERVISOR <= cabecalho:
        return TipoArquivoImportacao.CARTEIRA
    if _COLUNAS_PAINEL_AVERT <= cabecalho:
        return TipoArquivoImportacao.PAINEL_AVERT
    if _COLUNAS_WECHECK <= cabecalho:
        return TipoArquivoImportacao.WECHECK
    if _COLUNAS_FATURAMENTO <= cabecalho:
        return TipoArquivoImportacao.FATURAMENTO
    if _ABAS_BASE_CLIENTES <= cabecalho:
        return TipoArquivoImportacao.CLIENTES
    return None


def obter_ou_criar_usuario_sistema(session) -> Usuario:  # type: ignore[no-untyped-def]
    """Usuário técnico para `usuario_id` enquanto não há autenticação (Sprint futura)."""

    from sqlalchemy import select

    usuario = session.scalar(select(Usuario).where(Usuario.email == "sistema@promotoresbi.local"))
    if usuario is None:
        usuario = Usuario(
            nome="Sistema (carga CLI)",
            email="sistema@promotoresbi.local",
            senha_hash="!",  # login desabilitado; autenticação é sprint futura
            perfil=PerfilUsuario.ADMINISTRADOR,
        )
        session.add(usuario)
        session.commit()
    return usuario


def _competencia_de(texto: str) -> date | None:
    ano, mes = (int(parte) for parte in texto.split("-"))
    return date(ano, mes, 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Importa arquivos reais (Sprint 3, Fase 5).")
    parser.add_argument("caminhos", nargs="+", type=Path, help="Arquivos .xlsx a importar")
    parser.add_argument(
        "--competencia",
        type=_competencia_de,
        default=None,
        help="Mês de referência AAAA-MM, para fontes que exigem (CARTEIRA/PAINEL_AVERT)",
    )
    parser.add_argument(
        "--storage-dir", type=Path, default=None, help="Diretório de imports/ (padrão: settings)"
    )
    argumentos = parser.parse_args(argv)

    from app.core.config import get_settings

    storage_dir = argumentos.storage_dir or Path(get_settings().storage_dir)
    fluxo = FluxoArquivos(storage_dir)
    session = SessionLocal()
    try:
        usuario = obter_ou_criar_usuario_sistema(session)
        motor = MotorImportacao(session=session, fluxo=fluxo)

        codigo_saida = 0
        for caminho_original in argumentos.caminhos:
            destino = fluxo.incoming / caminho_original.name
            if destino != caminho_original:
                destino.write_bytes(caminho_original.read_bytes())
            tipo = inferir_tipo_arquivo(destino)
            if tipo is None:
                print(f"[NAO_RECONHECIDO] {caminho_original.name}: estrutura não identificada.")
                codigo_saida = 1
                continue
            importacao = motor.importar(
                destino, tipo, usuario.id, competencia=argumentos.competencia
            )
            print(
                f"[{importacao.status.value}] {caminho_original.name} -> {tipo.value} "
                f"(v{importacao.versao}, {importacao.linhas_validas}/{importacao.total_linhas} "
                "linhas válidas)"
            )
            if importacao.status.value == "FALHOU":
                codigo_saida = 1
        return codigo_saida
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
