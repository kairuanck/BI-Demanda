"""Conector do Painel Trade Avert — tipo PAINEL_AVERT.

É a **carteira oficial da operação Avert** (definição de negócio 12.5):
1 linha = 1 cliente da carteira, identificado por CNPJ. CONSULTOR é a
promotora (as mesmas pessoas do `Autor` do WeCheck).

Regras aplicadas:
- CNPJ casa com `clientes.cnpj_cpf` por comparação de dígitos (normali-
  zação determinística, não fuzzy). Sem correspondência → pendência em
  `clientes_integracao`, nunca cria cliente (12.5).
- CNPJ associado a mais de um cliente interno (77 documentos duplicados
  na Base) → pendência com observação; o vínculo automático seria ambíguo.
- Todas as colunas do painel são preservadas em `carteiras_avert`,
  inclusive as de compra vazias (nunca descartar colunas).
"""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import select

from app.domain.enums import SistemaOrigem, StatusConciliacao, TipoPromotor
from app.infrastructure.models import CarteiraAvert, Cliente
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.leitura import celula, indices_por_nome, ler_abas, localizar
from etl.loaders.apoio import obter_ou_criar_promotor_por_nome, registrar_integracao_cliente
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_decimal, para_texto
from etl.validators import criar_contexto_validacao

_SO_DIGITOS = re.compile(r"\D+")

_MAPEAMENTO: list[tuple[str, tuple[str, ...]]] = [
    ("cnpj", ("CNPJ",)),
    ("compra_2025", ("COMPRA_2025",)),
    ("compra_2026", ("COMPRA_2026",)),
    ("crescimento", ("CRESC", "CRESCIMENTO")),
    ("uf", ("UF",)),
    ("area", ("AREA",)),
    ("regional", ("REGIONAL",)),
    ("distribuidor", ("DISTRIBUIDOR",)),
    ("coordenador", ("COORDENADOR",)),
    ("consultor", ("CONSULTOR",)),
    ("vendedor", ("VENDEDOR",)),
    ("grupo_economico", ("GRUPO_ECONOMICO",)),
    ("nome_fantasia", ("NOME_FANTASIA",)),
    ("razao_social", ("RAZAO_SOCIAL",)),
    ("segmento", ("SEGMENTO",)),
    ("observacao", ("OBS:", "OBS", "OBSERVACAO")),
]


def _apenas_digitos(valor: str | None) -> str | None:
    if valor is None:
        return None
    digitos = _SO_DIGITOS.sub("", valor)
    return digitos or None


class ConectorPainelAvert(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        abas = [aba for aba in ler_abas(caminho) if not aba.vazia]
        if not abas:
            return ResultadoConector(
                erros=[ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados.")],
                estrutural_invalido=True,
            )
        aba = abas[0]
        indices = indices_por_nome(aba.cabecalho_normalizado())
        posicoes = {campo: localizar(indices, *aliases) for campo, aliases in _MAPEAMENTO}
        if posicoes["cnpj"] is None or posicoes["consultor"] is None:
            return ResultadoConector(
                erros=[
                    ErroLinha(
                        LINHA_ARQUIVO,
                        "Estrutura inesperada: esperado o Painel Trade Avert "
                        "(colunas CNPJ e CONSULTOR).",
                    )
                ],
                estrutural_invalido=True,
            )

        session = execucao.session
        contexto = criar_contexto_validacao(session)
        clientes_por_documento: dict[str, list[str]] = {}
        for documento, id_ in session.execute(
            select(Cliente.cnpj_cpf, Cliente.id).where(Cliente.cnpj_cpf.is_not(None))
        ):
            digitos = _apenas_digitos(documento)
            if digitos:
                clientes_por_documento.setdefault(digitos, []).append(id_)

        resultado = ResultadoConector()
        for numero, linha in enumerate(aba.linhas[1:], start=2):
            if all(v is None for v in linha):
                continue
            resultado.total_linhas += 1

            valores = {
                campo: para_texto(celula(linha, posicao)) for campo, posicao in posicoes.items()
            }
            cnpj = _apenas_digitos(valores["cnpj"])
            if cnpj is None:
                resultado.erros.append(
                    ErroLinha(numero, "CNPJ é obrigatório no Painel Avert.", "CNPJ")
                )
                continue

            candidatos = clientes_por_documento.get(cnpj, [])
            cliente_id = candidatos[0] if len(candidatos) == 1 else None
            integracao = registrar_integracao_cliente(
                session,
                SistemaOrigem.PAINEL_AVERT,
                cnpj,
                valores["nome_fantasia"] or valores["razao_social"],
                execucao.importacao_id,
                cliente_id=cliente_id,
            )
            if len(candidatos) > 1 and integracao.status == StatusConciliacao.PENDENTE:
                integracao.observacao = (
                    f"CNPJ associado a {len(candidatos)} clientes internos — "
                    "vínculo automático seria ambíguo."
                )

            promotora = None
            if valores["consultor"]:
                # CONSULTOR é a promotora (12.5); Trade por definição (12.6)
                promotora = obter_ou_criar_promotor_por_nome(
                    session, valores["consultor"], TipoPromotor.TRADE
                )

            uf = (valores["uf"] or "").upper() or None
            session.add(
                CarteiraAvert(
                    cnpj=cnpj,
                    cliente_id=cliente_id,
                    promotor_id=promotora.id if promotora is not None else None,
                    competencia=execucao.importacao.competencia,
                    uf_sigla=uf if uf and contexto.uf_existe(uf) else None,
                    area=valores["area"],
                    regional=valores["regional"],
                    distribuidor=valores["distribuidor"],
                    coordenador=valores["coordenador"],
                    consultor=valores["consultor"],
                    vendedor=valores["vendedor"],
                    grupo_economico=valores["grupo_economico"],
                    nome_fantasia=valores["nome_fantasia"],
                    razao_social=valores["razao_social"],
                    segmento=valores["segmento"],
                    compra_2025=para_decimal(celula(linha, posicoes["compra_2025"])),
                    compra_2026=para_decimal(celula(linha, posicoes["compra_2026"])),
                    crescimento=para_decimal(celula(linha, posicoes["crescimento"])),
                    observacao=valores["observacao"],
                    importacao_id=execucao.importacao_id,
                )
            )
            resultado.persistidas += 1
        return resultado
