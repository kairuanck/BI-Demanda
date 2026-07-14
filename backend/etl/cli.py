"""CLI de importação (Sprint 3, Fase 5).

A partir da Sprint 6 o caminho operacional recomendado é o upload Web
(`POST /api/v1/importacoes/upload`, docs/DECISIONS.md); esta CLI permanece
disponível para scripts/automação e reusa a mesma inferência de tipo
(`etl/inferencia.py`) e o mesmo usuário de sistema
(`app/services/usuario_service.py`) usados pelo endpoint.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from app.infrastructure.database import SessionLocal
from app.services.usuario_service import obter_ou_criar_usuario_sistema
from etl.arquivos import FluxoArquivos
from etl.inferencia import inferir_tipo_arquivo
from etl.motor import MotorImportacao

__all__ = ["inferir_tipo_arquivo", "obter_ou_criar_usuario_sistema", "main"]


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
