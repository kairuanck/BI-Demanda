"""Conector do relatório "Supervisor" do SB Promotor — tipo CARTEIRA.

É a **carteira mensal oficial** promotor×cliente (definição de negócio
12.2), com contagens agregadas de visitas. Estrutura real: dois blocos
lado a lado com cabeçalhos repetidos ("Código"/"Nome" aparecem nos dois),
o que exige mapeamento POSICIONAL — DATA_PROFILING.md, seção 4.1.

O arquivo não contém datas: a competência é obrigatória e vem do ato da
importação. Carrega `visitas_resumo_sb` (espelho fiel) e deriva as
vigências de `carteiras` (encerra vínculo anterior quando o promotor do
cliente muda; encerra vigentes ausentes do arquivo — snapshot completo).
`carteiras` é alimentada exclusivamente por esta origem; a carteira Avert
vive em `carteiras_avert` (12.5), sem interferência mútua.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.domain.enums import SistemaOrigem, StatusCarteira
from app.infrastructure.models import Carteira, Cliente, Promotor, VisitaResumoSb
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.leitura import ler_abas
from etl.loaders.apoio import registrar_integracao_cliente
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_inteiro, para_percentual, para_texto

# Posições fixas dos dois blocos do relatório real (16 colunas)
_POS_PROMOTOR_CODIGO = 0
_POS_PROMOTOR_NOME = 1
_POS_PROMOTOR_AREA = 2
_POS_PROMOTOR_PREVISTAS = 3
_POS_PROMOTOR_PREV_REALIZADAS = 4
_POS_PROMOTOR_PREV_NAO_REALIZADAS = 5
_POS_PROMOTOR_NAO_PREV_REALIZADAS = 6
_POS_CLIENTE_CODIGO = 7
_POS_CLIENTE_FANTASIA = 8
_POS_CLIENTE_RAZAO = 9
_POS_CLIENTE_PREVISTAS = 10
_POS_CLIENTE_REALIZADAS = 11
_POS_CLIENTE_NAO_VISITAS = 12
_POS_PERC_A_REALIZAR = 13
_POS_PERC_REALIZADAS = 14
_POS_PERC_NAO_VISITAS = 15


class ConectorSbSupervisor(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        competencia = execucao.importacao.competencia
        if competencia is None:
            return ResultadoConector(
                erros=[
                    ErroLinha(
                        LINHA_ARQUIVO,
                        "Competência obrigatória: o relatório Supervisor não contém o mês "
                        "de referência — informe-o na importação (docs/DECISIONS.md, 12.2).",
                    )
                ],
                estrutural_invalido=True,
            )

        abas = ler_abas(caminho)
        if not abas or abas[0].vazia:
            return ResultadoConector(
                erros=[ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados.")],
                estrutural_invalido=True,
            )
        aba = abas[0]
        cabecalho = aba.cabecalho_normalizado()
        if (
            len(cabecalho) < 16
            or cabecalho[_POS_PROMOTOR_CODIGO] != "CODIGO"
            or cabecalho[_POS_CLIENTE_CODIGO] != "CODIGO"
            or cabecalho[_POS_PROMOTOR_NOME] != "NOME"
        ):
            return ResultadoConector(
                erros=[
                    ErroLinha(
                        LINHA_ARQUIVO,
                        "Estrutura inesperada: esperado o relatório Supervisor do SB "
                        "Promotor (dois blocos Código/Nome, 16 colunas).",
                    )
                ],
                estrutural_invalido=True,
            )

        session = execucao.session
        clientes_por_codigo = {
            codigo: id_
            for codigo, id_ in session.execute(select(Cliente.codigo_externo, Cliente.id))
        }
        promotores_por_codigo = {
            promotor.codigo_externo: promotor
            for promotor in session.scalars(
                select(Promotor).where(Promotor.codigo_externo.is_not(None))
            )
        }
        resumos_existentes = {
            (resumo.promotor_id, resumo.cliente_id): resumo
            for resumo in session.scalars(
                select(VisitaResumoSb).where(VisitaResumoSb.competencia == competencia)
            )
        }
        vigentes_por_cliente = {
            carteira.cliente_id: carteira
            for carteira in session.scalars(
                select(Carteira).where(
                    Carteira.data_fim_vigencia.is_(None),
                    Carteira.status == StatusCarteira.ATIVA,
                )
            )
        }

        resultado = ResultadoConector()
        clientes_no_arquivo: set[str] = set()
        for numero, linha in enumerate(aba.linhas[1:], start=2):
            if all(v is None for v in linha):
                continue
            resultado.total_linhas += 1

            codigo_promotor = para_texto(self._valor(linha, _POS_PROMOTOR_CODIGO))
            codigo_cliente = para_texto(self._valor(linha, _POS_CLIENTE_CODIGO))
            if not codigo_promotor or not codigo_cliente:
                resultado.erros.append(
                    ErroLinha(numero, "Códigos de promotor e cliente são obrigatórios.", "CODIGO")
                )
                continue

            promotor = promotores_por_codigo.get(codigo_promotor)
            if promotor is None:
                promotor = Promotor(
                    codigo_externo=codigo_promotor,
                    nome=para_texto(self._valor(linha, _POS_PROMOTOR_NOME)) or codigo_promotor,
                    area=para_texto(self._valor(linha, _POS_PROMOTOR_AREA)),
                )
                session.add(promotor)
                session.flush()
                promotores_por_codigo[codigo_promotor] = promotor
            elif promotor.area is None:
                promotor.area = para_texto(self._valor(linha, _POS_PROMOTOR_AREA))

            cliente_id = clientes_por_codigo.get(codigo_cliente)
            if cliente_id is None:
                registrar_integracao_cliente(
                    session,
                    SistemaOrigem.SB_PROMOTOR,
                    codigo_cliente,
                    para_texto(self._valor(linha, _POS_CLIENTE_RAZAO))
                    or para_texto(self._valor(linha, _POS_CLIENTE_FANTASIA)),
                    execucao.importacao_id,
                )
                resultado.erros.append(
                    ErroLinha(
                        numero,
                        f"Cliente não encontrado na Base de Clientes: {codigo_cliente} "
                        "(pendência registrada em clientes_integracao).",
                        "CODIGO",
                        codigo_cliente,
                    )
                )
                continue

            clientes_no_arquivo.add(cliente_id)
            self._gravar_resumo(execucao, resumos_existentes, linha, promotor.id, cliente_id)
            self._versionar_carteira(execucao, vigentes_por_cliente, promotor.id, cliente_id)
            resultado.persistidas += 1

        # snapshot completo: vigentes ausentes do arquivo são encerrados
        for cliente_id, vigente in vigentes_por_cliente.items():
            if cliente_id not in clientes_no_arquivo:
                vigente.data_fim_vigencia = competencia
                vigente.status = StatusCarteira.ENCERRADA
        return resultado

    # ------------------------------------------------------------------ apoio

    @staticmethod
    def _valor(linha: tuple[Any, ...], posicao: int) -> Any:
        return linha[posicao] if posicao < len(linha) else None

    def _gravar_resumo(
        self,
        execucao: ExecucaoImportacao,
        existentes: dict[tuple[str, str], VisitaResumoSb],
        linha: tuple[Any, ...],
        promotor_id: str,
        cliente_id: str,
    ) -> None:
        contagens = {
            "visitas_previstas": para_inteiro(self._valor(linha, _POS_PROMOTOR_PREVISTAS)),
            "previstas_realizadas": para_inteiro(self._valor(linha, _POS_PROMOTOR_PREV_REALIZADAS)),
            "previstas_nao_realizadas": para_inteiro(
                self._valor(linha, _POS_PROMOTOR_PREV_NAO_REALIZADAS)
            ),
            "nao_previstas_realizadas": para_inteiro(
                self._valor(linha, _POS_PROMOTOR_NAO_PREV_REALIZADAS)
            ),
            "cliente_visitas_previstas": para_inteiro(self._valor(linha, _POS_CLIENTE_PREVISTAS)),
            "cliente_visitas_realizadas": para_inteiro(self._valor(linha, _POS_CLIENTE_REALIZADAS)),
            "cliente_nao_visitas": para_inteiro(self._valor(linha, _POS_CLIENTE_NAO_VISITAS)),
            "perc_visitas_a_realizar": para_percentual(self._valor(linha, _POS_PERC_A_REALIZAR)),
            "perc_visitas_realizadas": para_percentual(self._valor(linha, _POS_PERC_REALIZADAS)),
            "perc_nao_visitas": para_percentual(self._valor(linha, _POS_PERC_NAO_VISITAS)),
        }
        chave = (promotor_id, cliente_id)
        resumo = existentes.get(chave)
        if resumo is None:
            resumo = VisitaResumoSb(
                promotor_id=promotor_id,
                cliente_id=cliente_id,
                competencia=execucao.importacao.competencia,
                importacao_id=execucao.importacao_id,
                **contagens,
            )
            execucao.session.add(resumo)
            existentes[chave] = resumo
        else:
            # nova versão do relatório do mesmo mês: snapshot substitui contagens
            for campo, valor in contagens.items():
                setattr(resumo, campo, valor)
            resumo.importacao_id = execucao.importacao_id

    def _versionar_carteira(
        self,
        execucao: ExecucaoImportacao,
        vigentes: dict[str, Carteira],
        promotor_id: str,
        cliente_id: str,
    ) -> None:
        """REGRAS_DE_NEGOCIO.md, 5.2: nunca sobrescrever vínculos — versionar."""

        competencia = execucao.importacao.competencia
        assert competencia is not None  # garantido no início do processamento
        vigente = vigentes.get(cliente_id)
        if vigente is not None and vigente.promotor_id == promotor_id:
            return  # idempotente: mesmo promotor
        if vigente is not None:
            vigente.data_fim_vigencia = competencia
            vigente.status = StatusCarteira.ENCERRADA
        novo = Carteira(
            promotor_id=promotor_id,
            cliente_id=cliente_id,
            importacao_id=execucao.importacao_id,
            data_inicio_vigencia=competencia,
            competencia=competencia,
            status=StatusCarteira.ATIVA,
        )
        execucao.session.add(novo)
        vigentes[cliente_id] = novo
