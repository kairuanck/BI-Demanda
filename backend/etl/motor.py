"""Motor de importação — orquestra o pipeline ETL (ETL.md, seção 3).

Etapas: upload → extract → transform/validate → hash/versão → load
transacional → auditoria, com movimentação física do arquivo
(incoming → processed/rejected + cópia em archive).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.enums import (
    AcaoAuditoria,
    StatusImportacao,
    TipoArquivoImportacao,
)
from app.infrastructure.models import (
    Importacao,
    ImportacaoArquivo,
    ImportacaoErro,
    LogAuditoria,
)
from etl.arquivos import FluxoArquivos
from etl.conectores import (
    ConectorBaseClientes,
    ConectorChecklistSb,
    ConectorFaturamentoMatriz,
    ConectorLegado,
    ConectorOrigem,
    ConectorPainelAvert,
    ConectorSbProdutos,
    ConectorSbSupervisor,
    ConectorWeCheck,
    ExecucaoImportacao,
)
from etl.hash import calcular_hash_conteudo, calcular_sha256_arquivo
from etl.layouts import LAYOUTS
from etl.loaders import carregar_visitas
from etl.logs import obter_logger_etl
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.validators.visitas import validar_visitas

TAMANHO_MAXIMO_BYTES = 20 * 1024 * 1024  # VALIDADOR.md, EST-004
EXTENSAO_ACEITA = ".xlsx"  # VALIDADOR.md, EST-001

logger = obter_logger_etl()


def _agora_utc() -> datetime:
    """UTC naive — consistente com as colunas DateTime do modelo (DATABASE.md)."""

    return datetime.now(UTC).replace(tzinfo=None)


# Strategy por tipo de arquivo (docs/DECISIONS.md, 11.6): cada origem real
# tem seu conector; VISITAS mantém o layout documental legado (sem fonte
# real correspondente) via adaptador.
CONECTORES: dict[TipoArquivoImportacao, ConectorOrigem] = {
    TipoArquivoImportacao.CLIENTES: ConectorBaseClientes(),
    TipoArquivoImportacao.CARTEIRA: ConectorSbSupervisor(),
    TipoArquivoImportacao.FATURAMENTO: ConectorFaturamentoMatriz(),
    TipoArquivoImportacao.CHECKLIST: ConectorChecklistSb(),
    TipoArquivoImportacao.SB_PRODUTOS: ConectorSbProdutos(),
    TipoArquivoImportacao.WECHECK: ConectorWeCheck(),
    TipoArquivoImportacao.PAINEL_AVERT: ConectorPainelAvert(),
    TipoArquivoImportacao.VISITAS: ConectorLegado(
        LAYOUTS[TipoArquivoImportacao.VISITAS], validar_visitas, carregar_visitas
    ),
}


@dataclass
class MotorImportacao:
    session: Session
    fluxo: FluxoArquivos

    def importar(
        self,
        caminho: Path,
        tipo: TipoArquivoImportacao,
        usuario_id: str,
        competencia: date | None = None,
    ) -> Importacao:
        """Executa o pipeline completo para um arquivo em `incoming/`.

        `competencia` é o mês de referência dos dados (1º dia do mês) —
        obrigatório para fontes mensais que não o declaram no arquivo
        (ex.: relatório Supervisor do SB; docs/DECISIONS.md, 12.2).
        """

        inicio = time.monotonic()
        logger.info("Importação iniciada: tipo=%s arquivo=%s", tipo.value, caminho.name)

        erro_estrutural = self._validar_arquivo_fisico(caminho)
        hash_sha256 = calcular_sha256_arquivo(caminho)
        tamanho = caminho.stat().st_size
        hash_conteudo = self._hash_conteudo_seguro(caminho) if erro_estrutural is None else None

        # Etapa 5 — classificação de duplicidade (HASH.md, seção 3):
        # 1º pelos bytes; 2º pelo conteúdo lógico das células — os exports
        # reais chegam em dezenas de cópias byte a byte distintas porém
        # idênticas em conteúdo (docs/DECISIONS.md, 11.2).
        duplicada_de = self._buscar_duplicada(tipo, hash_sha256)
        if duplicada_de is None and hash_conteudo is not None:
            duplicada_de = self._buscar_duplicada_por_conteudo(tipo, hash_conteudo)
        if duplicada_de is not None:
            return self._registrar_recusa(
                caminho,
                tipo,
                usuario_id,
                hash_sha256,
                tamanho,
                f"Arquivo duplicado: idêntico à importação #{duplicada_de.id} "
                f"(versão {duplicada_de.versao}, de {duplicada_de.criado_em:%d/%m/%Y}).",
                hash_conteudo=hash_conteudo,
            )
        if erro_estrutural is not None:
            return self._registrar_recusa(
                caminho, tipo, usuario_id, hash_sha256, tamanho, erro_estrutural
            )

        versao, pai_id = self._proxima_versao(tipo)
        importacao = Importacao(
            tipo_arquivo=tipo,
            nome_arquivo_original=caminho.name,
            hash_sha256=hash_sha256,
            hash_conteudo=hash_conteudo,
            tamanho_bytes=tamanho,
            competencia=competencia,
            usuario_id=usuario_id,
            status=StatusImportacao.PROCESSANDO,
            versao=versao,
            importacao_pai_id=pai_id,
            iniciado_em=_agora_utc(),
        )
        self.session.add(importacao)
        self.session.commit()  # o registro da importação sobrevive a falhas da carga

        try:
            resultado = self._processar(caminho, tipo, importacao, usuario_id)
        except Exception:
            self.session.rollback()
            logger.exception(
                "Falha inesperada na importação #%s (tipo=%s)", importacao.id, tipo.value
            )
            importacao.status = StatusImportacao.FALHOU
            importacao.concluido_em = _agora_utc()
            self.session.add(
                ImportacaoErro(
                    importacao_id=importacao.id,
                    numero_linha=LINHA_ARQUIVO,
                    mensagem_erro=(
                        "Falha inesperada durante o processamento; " "nenhuma linha foi persistida."
                    ),
                )
            )
            self._auditar(importacao, usuario_id)
            self.session.commit()
            self.fluxo.mover_para_rejected(caminho)
            return importacao

        duracao = round(time.monotonic() - inicio, 3)
        logger.info(
            "Importação #%s concluída: status=%s validas=%s invalidas=%s duracao=%ss",
            importacao.id,
            importacao.status.value,
            importacao.linhas_validas,
            importacao.linhas_invalidas,
            duracao,
        )
        if importacao.status == StatusImportacao.FALHOU:
            self.fluxo.mover_para_rejected(caminho)
        else:
            self.fluxo.arquivar(caminho, tipo.value, importacao.id, hash_sha256)
            destino = self.fluxo.mover_para_processed(caminho)
            arquivo_archive = self.fluxo.archive / (
                f"{tipo.value}_{importacao.id}_{hash_sha256[:12]}{destino.suffix}"
            )
            self.session.add(
                ImportacaoArquivo(
                    importacao_id=importacao.id,
                    caminho_armazenamento=str(arquivo_archive.relative_to(self.fluxo.base)),
                    nome_arquivo=arquivo_archive.name,
                )
            )
            self.session.commit()
        return resultado

    # ------------------------------------------------------------------ etapas

    def _validar_arquivo_fisico(self, caminho: Path) -> str | None:
        if caminho.suffix.lower() != EXTENSAO_ACEITA:
            return "Formato de arquivo inválido. Utilize .xlsx."  # EST-001
        if caminho.stat().st_size > TAMANHO_MAXIMO_BYTES:
            return "Arquivo excede o tamanho máximo permitido (20 MB)."  # EST-004
        return None

    def _buscar_duplicada(self, tipo: TipoArquivoImportacao, hash_sha256: str) -> Importacao | None:
        """Importação anterior idêntica, ignorando FALHOU/REVERTIDA (HASH.md, seções 3 e 6)."""

        return self.session.scalar(
            select(Importacao).where(
                Importacao.tipo_arquivo == tipo,
                Importacao.hash_sha256 == hash_sha256,
                Importacao.status.not_in([StatusImportacao.FALHOU, StatusImportacao.REVERTIDA]),
            )
        )

    def _buscar_duplicada_por_conteudo(
        self, tipo: TipoArquivoImportacao, hash_conteudo: str
    ) -> Importacao | None:
        """Duplicidade lógica: mesmo conteúdo de células em bytes diferentes."""

        return self.session.scalar(
            select(Importacao).where(
                Importacao.tipo_arquivo == tipo,
                Importacao.hash_conteudo == hash_conteudo,
                Importacao.status.not_in([StatusImportacao.FALHOU, StatusImportacao.REVERTIDA]),
            )
        )

    @staticmethod
    def _hash_conteudo_seguro(caminho: Path) -> str | None:
        """Hash de conteúdo; arquivo ilegível vira erro estrutural adiante."""

        try:
            return calcular_hash_conteudo(caminho)
        except Exception:  # noqa: BLE001 - xlsx corrompido é tratado pelo conector
            return None

    def _proxima_versao(self, tipo: TipoArquivoImportacao) -> tuple[int, str | None]:
        """REGRAS_DE_NEGOCIO.md, seção 4: MAX(versão) exclui FALHOU/REVERTIDA."""

        anterior = self.session.scalar(
            select(Importacao)
            .where(
                Importacao.tipo_arquivo == tipo,
                Importacao.status.in_(
                    [StatusImportacao.CONCLUIDA, StatusImportacao.CONCLUIDA_COM_ERROS]
                ),
            )
            .order_by(Importacao.versao.desc())
            .limit(1)
        )
        if anterior is None:
            return 1, None
        return anterior.versao + 1, anterior.id

    def _processar(
        self,
        caminho: Path,
        tipo: TipoArquivoImportacao,
        importacao: Importacao,
        usuario_id: str,
    ) -> Importacao:
        conector = CONECTORES[tipo]
        execucao = ExecucaoImportacao(session=self.session, importacao=importacao)
        resultado = conector.processar(caminho, execucao)

        if resultado.estrutural_invalido:
            self.session.rollback()  # descarta qualquer resíduo antes da falha
            importacao.status = StatusImportacao.FALHOU
            importacao.concluido_em = _agora_utc()
            self._registrar_erros(importacao.id, resultado.erros)
            self._auditar(importacao, usuario_id)
            self.session.commit()
            return importacao

        self._registrar_erros(importacao.id, resultado.erros)
        importacao.total_linhas = resultado.total_linhas
        importacao.linhas_validas = resultado.persistidas
        importacao.linhas_invalidas = max(resultado.total_linhas - resultado.persistidas, 0)
        importacao.concluido_em = _agora_utc()
        if resultado.persistidas == 0:
            importacao.status = StatusImportacao.FALHOU
        elif importacao.linhas_invalidas > 0:
            importacao.status = StatusImportacao.CONCLUIDA_COM_ERROS
        else:
            importacao.status = StatusImportacao.CONCLUIDA

        self._auditar(importacao, usuario_id)
        self.session.commit()
        return importacao

    # ------------------------------------------------------------------ apoio

    def _registrar_recusa(
        self,
        caminho: Path,
        tipo: TipoArquivoImportacao,
        usuario_id: str,
        hash_sha256: str,
        tamanho: int,
        mensagem: str,
        hash_conteudo: str | None = None,
    ) -> Importacao:
        """Tentativa recusada antes do processamento (duplicidade/estrutura física).

        versao=0 marca a tentativa como fora da cadeia de versões válidas
        (ver docs/DECISIONS.md).
        """

        importacao = Importacao(
            tipo_arquivo=tipo,
            nome_arquivo_original=caminho.name,
            hash_sha256=hash_sha256,
            hash_conteudo=hash_conteudo,
            tamanho_bytes=tamanho,
            usuario_id=usuario_id,
            status=StatusImportacao.FALHOU,
            versao=0,
            concluido_em=_agora_utc(),
        )
        self.session.add(importacao)
        self.session.flush()
        self.session.add(
            ImportacaoErro(
                importacao_id=importacao.id,
                numero_linha=LINHA_ARQUIVO,
                mensagem_erro=mensagem,
            )
        )
        self._auditar(importacao, usuario_id)
        self.session.commit()
        logger.warning("Importação recusada (tipo=%s): %s", tipo.value, mensagem)
        self.fluxo.mover_para_rejected(caminho)
        return importacao

    def cancelar(self, importacao: Importacao, usuario_id: str) -> Importacao:
        """Cancela uma importação `PENDENTE`, antes de iniciar o processamento (Sprint 6).

        Nesta arquitetura o processamento é síncrono (sem fila em segundo
        plano), então não existe uma execução "em andamento" que possa ser
        interrompida no servidor — `PENDENTE` é o único estado em que
        cancelar tem sentido. Reusa o mesmo formato de tentativa recusada
        de `_registrar_recusa`: `status=FALHOU`, `versao=0` (fora da cadeia
        de versões) e um `ImportacaoErro` explicando o motivo.
        """

        importacao.status = StatusImportacao.FALHOU
        importacao.versao = 0
        importacao.concluido_em = _agora_utc()
        self.session.add(
            ImportacaoErro(
                importacao_id=importacao.id,
                numero_linha=LINHA_ARQUIVO,
                mensagem_erro="Importação cancelada pelo usuário.",
            )
        )
        self._auditar(importacao, usuario_id)
        self.session.commit()
        logger.info("Importação #%s cancelada pelo usuário.", importacao.id)
        return importacao

    def _registrar_erros(self, importacao_id: str, erros: list[ErroLinha]) -> None:
        for erro in erros:
            self.session.add(
                ImportacaoErro(
                    importacao_id=importacao_id,
                    numero_linha=erro.numero_linha,
                    coluna=erro.coluna,
                    valor_recebido=erro.valor_recebido,
                    mensagem_erro=erro.mensagem,
                )
            )

    def _auditar(self, importacao: Importacao, usuario_id: str) -> None:
        duracao_segundos: float | None = None
        if importacao.iniciado_em and importacao.concluido_em:
            duracao_segundos = (importacao.concluido_em - importacao.iniciado_em).total_seconds()
        self.session.add(
            LogAuditoria(
                entidade="importacoes",
                entidade_id=importacao.id,
                acao=AcaoAuditoria.IMPORTACAO,
                usuario_id=usuario_id,
                dados_depois={
                    "tipo_arquivo": importacao.tipo_arquivo.value,
                    "versao": importacao.versao,
                    "status": importacao.status.value,
                    "total_linhas": importacao.total_linhas,
                    "linhas_validas": importacao.linhas_validas,
                    "linhas_invalidas": importacao.linhas_invalidas,
                    "hash_sha256": importacao.hash_sha256,
                    "duracao_segundos": duracao_segundos,
                },
            )
        )


def contar_registros(session: Session, modelo: type[Any]) -> int:
    """Utilitário de teste/diagnóstico: total de linhas de uma tabela."""

    return session.scalar(select(func.count()).select_from(modelo)) or 0
