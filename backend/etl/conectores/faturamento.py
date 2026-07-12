"""Conector da matriz mensal de Faturamento real — tipo FATURAMENTO.

Estrutura real (DATA_PROFILING.md, seção 3):
- Linha 1: rótulo "Departamento" + nomes de marca por coluna (a dimensão
  chama-se Departamento no export, mas as colunas são Laboratórios —
  definição de negócio 12.1; BRINDE é categoria comercial à parte).
- Linha 2: rótulo "Cliente" + "Medidas faturamento".
- Linhas de dados: "<código> - <razão social>" + valores por marca.
- Linha "Total" e rodapé "Filtros aplicados..." (de onde vêm ano e mês).

Transformação wide→long: 1 célula cliente×marca preenchida = 1 linha de
`faturamentos` (valor líquido de venda+devolução — negativos possíveis).
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.domain.enums import CategoriaComercial
from app.infrastructure.models import Cliente, Faturamento
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.leitura import ler_abas
from etl.loaders.apoio import obter_ou_criar_laboratorio_por_nome
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_decimal, para_texto

_PADRAO_ROTULO_CLIENTE = re.compile(r"^\s*(\d+)\s*-\s*(.*)$")
_PADRAO_ANO = re.compile(r"(\d{4})\s*\(Ano\)")
_PADRAO_MES = re.compile(r"\+\s*([A-Za-zÀ-ÿ]+)\s*\(M", re.IGNORECASE)
_COLUNA_TOTAL = "TOTAL"
_MARCA_BRINDE = "BRINDE"

_MESES_PT = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARCO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}


def _sem_acento_maiusculo(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().upper()


class ConectorFaturamentoMatriz(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        abas = ler_abas(caminho)
        if not abas or len(abas[0].linhas) < 3:
            return ResultadoConector(
                erros=[ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados.")],
                estrutural_invalido=True,
            )
        linhas = abas[0].linhas

        marcas = self._mapear_marcas(linhas[0])
        if not marcas:
            return ResultadoConector(
                erros=[
                    ErroLinha(
                        LINHA_ARQUIVO,
                        "Estrutura inesperada: linha 1 deveria conter as marcas "
                        "(matriz Cliente × Marca).",
                    )
                ],
                estrutural_invalido=True,
            )

        competencia = self._competencia(linhas, execucao)
        if competencia is None:
            return ResultadoConector(
                erros=[
                    ErroLinha(
                        LINHA_ARQUIVO,
                        "Competência não encontrada: informe o mês de referência na "
                        "importação (o rodapé do arquivo não a declara).",
                    )
                ],
                estrutural_invalido=True,
            )
        execucao.importacao.competencia = competencia

        session = execucao.session
        clientes_por_codigo = {
            codigo: id_
            for codigo, id_ in session.execute(select(Cliente.codigo_externo, Cliente.id))
        }
        laboratorios = {
            marca: obter_ou_criar_laboratorio_por_nome(
                session,
                marca,
                (
                    CategoriaComercial.BRINDE
                    if _sem_acento_maiusculo(marca) == _MARCA_BRINDE
                    else CategoriaComercial.LABORATORIO
                ),
            )
            for _, marca in marcas
        }
        existentes = self._faturamentos_existentes(execucao, competencia, laboratorios)

        resultado = ResultadoConector()
        for numero, linha in enumerate(linhas[2:], start=3):
            rotulo = para_texto(linha[0] if linha else None)
            if rotulo is None:
                continue
            if _sem_acento_maiusculo(rotulo) == "TOTAL":
                break  # fim dos dados; abaixo ficam apenas total e rodapé
            correspondencia = _PADRAO_ROTULO_CLIENTE.match(rotulo)
            if not correspondencia:
                continue  # rodapé/ruído
            codigo_cliente = correspondencia.group(1)
            cliente_id = clientes_por_codigo.get(codigo_cliente)

            for posicao, marca in marcas:
                valor_bruto = linha[posicao] if posicao < len(linha) else None
                if valor_bruto is None or str(valor_bruto).strip() == "":
                    continue
                resultado.total_linhas += 1
                valor = para_decimal(valor_bruto)
                if valor is None:
                    resultado.erros.append(
                        ErroLinha(
                            numero,
                            f"Valor de faturamento inválido para a marca {marca}.",
                            marca,
                            str(valor_bruto)[:100],
                        )
                    )
                    continue
                if cliente_id is None:
                    resultado.erros.append(
                        ErroLinha(
                            numero,
                            f"Cliente não encontrado na Base de Clientes: {codigo_cliente}.",
                            "CLIENTE",
                            rotulo[:100],
                        )
                    )
                    continue
                laboratorio = laboratorios[marca]
                chave = (cliente_id, laboratorio.id)
                valor_existente = existentes.get(chave)
                if valor_existente is not None:
                    if valor_existente == valor:
                        resultado.persistidas += 1  # reimportação idempotente
                    else:
                        resultado.erros.append(
                            ErroLinha(
                                numero,
                                "Faturamento já registrado com valor diferente para "
                                f"{codigo_cliente} × {marca} em "
                                f"{competencia.month:02d}/{competencia.year} — dados nunca "
                                "são sobrescritos (REGRAS_DE_NEGOCIO.md, 5.3).",
                                marca,
                                str(valor),
                            )
                        )
                    continue
                session.add(
                    Faturamento(
                        cliente_id=cliente_id,
                        laboratorio_id=laboratorio.id,
                        ano=competencia.year,
                        mes=competencia.month,
                        valor_faturado=valor,
                        importacao_id=execucao.importacao_id,
                    )
                )
                existentes[chave] = valor
                resultado.persistidas += 1
        return resultado

    # ------------------------------------------------------------------ apoio

    def _mapear_marcas(self, linha_marcas: tuple[Any, ...]) -> list[tuple[int, str]]:
        """Posições e nomes das colunas de marca (exclui a coluna Total)."""

        marcas: list[tuple[int, str]] = []
        for posicao, valor in enumerate(linha_marcas[1:], start=1):
            marca = para_texto(valor)
            if marca is None:
                continue
            if _sem_acento_maiusculo(marca) == _COLUNA_TOTAL:
                continue
            marcas.append((posicao, marca))
        return marcas

    def _competencia(
        self, linhas: list[tuple[Any, ...]], execucao: ExecucaoImportacao
    ) -> date | None:
        """Extrai ano/mês do rodapé "Filtros aplicados"; senão usa o parâmetro."""

        for linha in reversed(linhas[-5:]):
            texto = " ".join(str(v) for v in linha if v is not None)
            ano_encontrado = _PADRAO_ANO.search(texto)
            mes_encontrado = _PADRAO_MES.search(texto)
            if ano_encontrado and mes_encontrado:
                mes = _MESES_PT.get(_sem_acento_maiusculo(mes_encontrado.group(1)))
                if mes:
                    return date(int(ano_encontrado.group(1)), mes, 1)
        return execucao.importacao.competencia

    def _faturamentos_existentes(
        self,
        execucao: ExecucaoImportacao,
        competencia: date,
        laboratorios: dict[str, Any],
    ) -> dict[tuple[str, str], Any]:
        ids_laboratorios = [laboratorio.id for laboratorio in laboratorios.values()]
        registros = execucao.session.execute(
            select(
                Faturamento.cliente_id, Faturamento.laboratorio_id, Faturamento.valor_faturado
            ).where(
                Faturamento.ano == competencia.year,
                Faturamento.mes == competencia.month,
                Faturamento.laboratorio_id.in_(ids_laboratorios),
            )
        )
        return {(cliente, laboratorio): valor for cliente, laboratorio, valor in registros}
