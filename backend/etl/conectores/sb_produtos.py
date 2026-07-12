"""Conector do detalhe de visitas do SB Promotor — tipo SB_PRODUTOS.

Arquivo real com 4 abas (`Produtos`, `Gondola`, `ProdutoSimilar`,
`Tarefas`); apenas `Produtos` continha dados no período analisado
(DATA_PROFILING.md, 4.2). 1 linha = 1 produto verificado em 1 visita.
Abas desconhecidas com dados geram alerta (nunca descartar em silêncio).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.domain.enums import SistemaOrigem
from app.infrastructure.models import Cliente, VisitaProdutoSb
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.leitura import celula, indices_por_nome, ler_abas, localizar
from etl.loaders.apoio import obter_ou_criar_promotor, registrar_integracao_cliente
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_data, para_decimal, para_texto

_ABA_PRODUTOS = "PRODUTOS"
_ABAS_CONHECIDAS_SEM_SUPORTE = {"GONDOLA", "PRODUTOSIMILAR", "TAREFAS"}


class ConectorSbProdutos(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        abas = ler_abas(caminho)
        aba_produtos = next(
            (aba for aba in abas if aba.titulo.strip().upper() == _ABA_PRODUTOS), None
        )
        if aba_produtos is None or aba_produtos.vazia:
            return ResultadoConector(
                erros=[
                    ErroLinha(
                        LINHA_ARQUIVO,
                        "Estrutura inesperada: aba 'Produtos' ausente ou vazia "
                        "(detalhe de visitas do SB Promotor).",
                    )
                ],
                estrutural_invalido=True,
            )

        resultado = ResultadoConector()
        for aba in abas:
            titulo = aba.titulo.strip().upper()
            if titulo != _ABA_PRODUTOS and not aba.vazia:
                resultado.erros.append(
                    ErroLinha(
                        LINHA_ARQUIVO,
                        f"Aba '{aba.titulo}' contém dados ainda não suportados pelo "
                        "conector SB_PRODUTOS — nenhum dado dela foi descartado do "
                        "arquivo original (preservado em archive/).",
                    )
                )

        indices = indices_por_nome(aba_produtos.cabecalho_normalizado())
        posicoes = {
            "visita": localizar(indices, "VISITA"),
            "codigo_promotor": localizar(indices, "CODIGO"),
            "nome_promotor": localizar(indices, "FUNCIONARIO"),
            "regiao": localizar(indices, "REGIAO"),
            "codigo_cliente": localizar(indices, "COD._CLIENTE", "COD_CLIENTE"),
            "razao_social": localizar(indices, "RAZAO_SOCIAL"),
            "nome_fantasia": localizar(indices, "NOME_FANTASIA"),
            "data_inicial": localizar(indices, "DATA_INICIAL"),
            "data_final": localizar(indices, "DATA_FINAL"),
            "operacao": localizar(indices, "OPERACAO"),
            "grupo": localizar(indices, "GRUPO"),
            "marca": localizar(indices, "MARCA"),
            "codigo_produto": localizar(indices, "COD._PRODUTO", "COD_PRODUTO"),
            "produto": localizar(indices, "PRODUTO"),
            "validade": localizar(indices, "VALIDADE"),
            "lote": localizar(indices, "LOTE"),
            "estoque": localizar(indices, "ESTOQUE"),
            "preco": localizar(indices, "PRECO"),
            "observacao": localizar(indices, "OBSERVACAO"),
        }
        for obrigatoria in ("visita", "codigo_promotor", "codigo_cliente"):
            if posicoes[obrigatoria] is None:
                resultado.erros.append(
                    ErroLinha(
                        LINHA_ARQUIVO,
                        f"Coluna obrigatória ausente na aba Produtos: {obrigatoria.upper()}.",
                    )
                )
        if any(posicoes[c] is None for c in ("visita", "codigo_promotor", "codigo_cliente")):
            resultado.estrutural_invalido = True
            return resultado

        session = execucao.session
        clientes_por_codigo = {
            codigo: id_
            for codigo, id_ in session.execute(select(Cliente.codigo_externo, Cliente.id))
        }
        existentes = {
            (registro.codigo_visita_externa, registro.codigo_produto, registro.lote)
            for registro in session.scalars(select(VisitaProdutoSb))
        }

        for numero, linha in enumerate(aba_produtos.linhas[1:], start=2):
            if all(v is None for v in linha):
                continue
            resultado.total_linhas += 1
            erros = self._processar_linha(
                execucao, clientes_por_codigo, existentes, posicoes, numero, linha
            )
            if erros:
                resultado.erros.extend(erros)
            else:
                resultado.persistidas += 1
        return resultado

    def _processar_linha(
        self,
        execucao: ExecucaoImportacao,
        clientes_por_codigo: dict[str, str],
        existentes: set[tuple[str, str | None, str | None]],
        posicoes: dict[str, int | None],
        numero: int,
        linha: tuple[Any, ...],
    ) -> list[ErroLinha]:
        def texto(campo: str) -> str | None:
            return para_texto(celula(linha, posicoes[campo]))

        codigo_visita = texto("visita")
        codigo_promotor = texto("codigo_promotor")
        codigo_cliente = texto("codigo_cliente")
        if not codigo_visita or not codigo_promotor or not codigo_cliente:
            return [
                ErroLinha(
                    numero, "VISITA, CÓDIGO (promotor) e COD. CLIENTE são obrigatórios.", "VISITA"
                )
            ]

        session = execucao.session
        cliente_id = clientes_por_codigo.get(codigo_cliente)
        if cliente_id is None:
            registrar_integracao_cliente(
                session,
                SistemaOrigem.SB_PROMOTOR,
                codigo_cliente,
                texto("razao_social") or texto("nome_fantasia"),
                execucao.importacao_id,
            )
            return [
                ErroLinha(
                    numero,
                    f"Cliente não encontrado na Base de Clientes: {codigo_cliente} "
                    "(pendência registrada em clientes_integracao).",
                    "COD._CLIENTE",
                    codigo_cliente,
                )
            ]

        chave = (codigo_visita, texto("codigo_produto"), texto("lote"))
        if chave in existentes:
            return []  # reimportação idempotente do detalhe

        promotor = obter_ou_criar_promotor(
            session, codigo_promotor, texto("nome_promotor"), None, None
        )
        regiao = (texto("regiao") or "").upper() or None
        session.add(
            VisitaProdutoSb(
                codigo_visita_externa=codigo_visita,
                promotor_id=promotor.id,
                cliente_id=cliente_id,
                uf_sigla=regiao if regiao and len(regiao) == 2 else None,
                data_inicial=para_data(celula(linha, posicoes["data_inicial"])),
                data_final=para_data(celula(linha, posicoes["data_final"])),
                operacao=texto("operacao"),
                grupo_marca=texto("grupo"),
                marca=texto("marca"),
                codigo_produto=texto("codigo_produto"),
                produto=texto("produto"),
                validade=para_data(celula(linha, posicoes["validade"])),
                lote=texto("lote"),
                estoque=para_decimal(celula(linha, posicoes["estoque"])),
                preco=para_decimal(celula(linha, posicoes["preco"])),
                observacao=texto("observacao"),
                importacao_id=execucao.importacao_id,
            )
        )
        existentes.add(chave)
        return []
