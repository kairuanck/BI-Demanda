"""Conector da Base de Clientes real (22 colunas) — tipo CLIENTES.

Mapeamento adaptativo por nome normalizado, com aliases para o layout
documental da Sprint 2 (IMPORTADOR.md, 3.1) e para o export real do ERP
(DATA_PROFILING.md, seção 2). Os pares RCA 1..4 / Nome RCA viram vínculos
`clientes_vendedores` com a ordem preservada. Detalhes de mapeamento em
IMPORT_MAPPING.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.domain.enums import AcaoAuditoria
from app.infrastructure.models import Cliente, ClienteVendedor, LogAuditoria
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.leitura import AbaBruta, celula, indices_por_nome, ler_abas, localizar
from etl.loaders.apoio import obter_ou_criar_cidade, obter_ou_criar_vendedor
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_data_hora, para_texto
from etl.validators import criar_contexto_validacao
from etl.validators.contexto import ContextoValidacao

# (campo destino, aliases em ordem de preferência, obrigatório?)
_MAPEAMENTO: list[tuple[str, tuple[str, ...], bool]] = [
    ("codigo_externo", ("CODIGO", "CODIGO_CLIENTE"), True),
    ("razao_social", ("CLIENTE", "RAZAO_SOCIAL"), True),
    ("uf_sigla", ("ESTADO", "UF"), True),
    ("cidade_nome", ("NOME_DA_CIDADE", "CIDADE"), True),
    ("nome_fantasia", ("FANTASIA", "NOME_FANTASIA"), False),
    ("cnpj_cpf", ("CNPJ/CPF", "CNPJ_CPF"), False),
    ("inscricao_estadual", ("INSC._EST._/_PRODUTOR", "INSCRICAO_ESTADUAL"), False),
    ("tipo_pessoa", ("TIPO_DE_PESSOA",), False),
    ("ramo_atividade", ("RAMO_ATIVIDADE",), False),
    ("endereco", ("ENDERECO_COMERCIAL", "ENDERECO"), False),
    ("numero", ("NUMERO",), False),
    ("bairro", ("BAIRRO",), False),
    ("cep", ("CEP",), False),
    ("telefone", ("TELEFONE",), False),
    ("canal", ("CANAL",), False),
    ("data_ultima_compra", ("DATA_DA_ULTIMA_COMPRA",), False),
]

_CAMPOS_CADASTRAIS = (
    "razao_social",
    "nome_fantasia",
    "cnpj_cpf",
    "inscricao_estadual",
    "tipo_pessoa",
    "ramo_atividade",
    "uf_sigla",
    "endereco",
    "numero",
    "bairro",
    "cep",
    "telefone",
    "canal",
    "data_ultima_compra",
)

_PADRAO_RCA = re.compile(r"^RCA_?(\d)$")
_PADRAO_NOME_RCA = re.compile(r"^NOME_RCA")


class ConectorBaseClientes(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        abas = ler_abas(caminho)
        if not abas or abas[0].vazia:
            return ResultadoConector(
                erros=[ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados.")],
                estrutural_invalido=True,
            )
        aba = abas[0]
        indices = indices_por_nome(aba.cabecalho_normalizado())

        posicoes: dict[str, int | None] = {}
        erros_estruturais: list[ErroLinha] = []
        for campo, aliases, obrigatoria in _MAPEAMENTO:
            posicao = localizar(indices, *aliases)
            if posicao is None and obrigatoria:
                erros_estruturais.append(
                    ErroLinha(
                        LINHA_ARQUIVO, f"Coluna obrigatória ausente: {aliases[0]}.", aliases[0]
                    )
                )
            posicoes[campo] = posicao
        if erros_estruturais:
            return ResultadoConector(erros=erros_estruturais, estrutural_invalido=True)

        pares_rca = self._parear_rcas(aba)
        contexto = criar_contexto_validacao(execucao.session)

        resultado = ResultadoConector()
        for indice, linha in enumerate(aba.linhas[1:], start=2):
            if all(v is None for v in linha):
                continue
            resultado.total_linhas += 1
            erros = self._processar_linha(execucao, contexto, posicoes, pares_rca, indice, linha)
            if erros:
                resultado.erros.extend(erros)
            else:
                resultado.persistidas += 1
        return resultado

    # ------------------------------------------------------------------ linha

    def _processar_linha(
        self,
        execucao: ExecucaoImportacao,
        contexto: ContextoValidacao,
        posicoes: dict[str, int | None],
        pares_rca: list[tuple[int, int, int | None]],
        numero: int,
        linha: tuple[Any, ...],
    ) -> list[ErroLinha]:
        dados: dict[str, Any] = {
            campo: para_texto(celula(linha, posicao)) for campo, posicao in posicoes.items()
        }
        dados["data_ultima_compra"] = para_data_hora(celula(linha, posicoes["data_ultima_compra"]))

        erros: list[ErroLinha] = []
        if not dados["codigo_externo"]:
            erros.append(ErroLinha(numero, "Código do cliente é obrigatório.", "CODIGO"))
        if not dados["razao_social"]:
            erros.append(ErroLinha(numero, "Razão social é obrigatória.", "CLIENTE"))
        uf = (dados["uf_sigla"] or "").upper()
        if not uf or not contexto.uf_existe(uf):
            erros.append(
                ErroLinha(numero, f"UF inválida: {dados['uf_sigla']}.", "ESTADO", dados["uf_sigla"])
            )
        if not dados["cidade_nome"]:
            erros.append(ErroLinha(numero, "Cidade é obrigatória.", "NOME_DA_CIDADE"))
        if erros:
            return erros

        dados["uf_sigla"] = uf
        self._persistir_cliente(execucao, dados, pares_rca, linha)
        return []

    def _persistir_cliente(
        self,
        execucao: ExecucaoImportacao,
        dados: dict[str, Any],
        pares_rca: list[tuple[int, int, int | None]],
        linha: tuple[Any, ...],
    ) -> None:
        session = execucao.session
        cidade = obter_ou_criar_cidade(session, dados["cidade_nome"], dados["uf_sigla"])
        cliente = session.scalar(
            select(Cliente).where(Cliente.codigo_externo == dados["codigo_externo"])
        )

        if cliente is None:
            cliente = Cliente(
                codigo_externo=dados["codigo_externo"],
                cidade_id=cidade.id,
                **{campo: dados[campo] for campo in _CAMPOS_CADASTRAIS},
            )
            session.add(cliente)
            session.flush()
            session.add(
                LogAuditoria(
                    entidade="clientes",
                    entidade_id=cliente.id,
                    acao=AcaoAuditoria.CRIACAO,
                    usuario_id=execucao.usuario_id,
                    dados_depois={
                        "codigo_externo": cliente.codigo_externo,
                        "importacao_id": execucao.importacao_id,
                    },
                )
            )
        else:
            antes: dict[str, Any] = {}
            depois: dict[str, Any] = {}
            novos = {campo: dados[campo] for campo in _CAMPOS_CADASTRAIS}
            novos["cidade_id"] = cidade.id
            for campo, novo_valor in novos.items():
                atual = getattr(cliente, campo)
                if atual != novo_valor:
                    antes[campo], depois[campo] = str(atual), str(novo_valor)
                    setattr(cliente, campo, novo_valor)
            if depois:
                depois["importacao_id"] = execucao.importacao_id
                session.add(
                    LogAuditoria(
                        entidade="clientes",
                        entidade_id=cliente.id,
                        acao=AcaoAuditoria.ATUALIZACAO,
                        usuario_id=execucao.usuario_id,
                        dados_antes=antes,
                        dados_depois=depois,
                    )
                )

        # RCAs: snapshot cadastral — vínculos por ordem, atualizados no upsert
        vinculos_atuais = {
            v.ordem: v
            for v in session.scalars(
                select(ClienteVendedor).where(ClienteVendedor.cliente_id == cliente.id)
            )
        }
        ordens_no_arquivo: set[int] = set()
        for ordem, pos_codigo, pos_nome in pares_rca:
            codigo_rca = para_texto(celula(linha, pos_codigo))
            if not codigo_rca or codigo_rca == "0":
                continue
            nome_rca = para_texto(celula(linha, pos_nome)) if pos_nome is not None else None
            vendedor = obter_ou_criar_vendedor(session, codigo_rca, nome_rca)
            ordens_no_arquivo.add(ordem)
            vinculo = vinculos_atuais.get(ordem)
            if vinculo is None:
                session.add(
                    ClienteVendedor(
                        cliente_id=cliente.id,
                        vendedor_id=vendedor.id,
                        ordem=ordem,
                        importacao_id=execucao.importacao_id,
                    )
                )
            elif vinculo.vendedor_id != vendedor.id:
                vinculo.vendedor_id = vendedor.id
                vinculo.importacao_id = execucao.importacao_id
        for ordem, vinculo in vinculos_atuais.items():
            if ordem not in ordens_no_arquivo:
                session.delete(vinculo)  # snapshot cadastral: RCA removido no ERP

    # ------------------------------------------------------------------ RCAs

    def _parear_rcas(self, aba: AbaBruta) -> list[tuple[int, int, int | None]]:
        """Localiza os pares (ordem, coluna RCA, coluna Nome RCA) por posição.

        O export real repete o cabeçalho "Nome RCA" e o RCA4 não tem coluna
        de nome — o pareamento é posicional: o "Nome RCA" imediatamente após
        um "RCA n" pertence a ele.
        """

        cabecalho = aba.cabecalho_normalizado()
        pares: list[tuple[int, int, int | None]] = []
        for posicao, nome in enumerate(cabecalho):
            if nome is None:
                continue
            correspondencia = _PADRAO_RCA.match(nome)
            if not correspondencia:
                continue
            ordem = int(correspondencia.group(1))
            proximo = cabecalho[posicao + 1] if posicao + 1 < len(cabecalho) else None
            pos_nome = posicao + 1 if proximo and _PADRAO_NOME_RCA.match(proximo) else None
            pares.append((ordem, posicao, pos_nome))
        return pares
