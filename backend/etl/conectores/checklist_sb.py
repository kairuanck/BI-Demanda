"""Conector do export de checklists do SB Promotor — tipo CHECKLIST.

Estrutura real (DATA_PROFILING.md, seção 6): 8 abas (uma por template),
todas com as mesmas 42 colunas = 10 de contexto + a UNIÃO das perguntas de
todos os templates (formato wide). Cada linha é **uma aplicação de
checklist, que é uma visita** (definição de negócio 12.7): id `VISITA` +
data/hora `APLICAÇÃO`.

Transformações:
- template (aba) → `checklists` (codigo_externo=CK_ID, origem=SB_PROMOTOR);
- coluna de pergunta → `checklist_perguntas` (get-or-create por enunciado);
- linha → `visitas` (origem SB_PROMOTOR, codigo_externo=VISITA);
- célula de pergunta preenchida → `checklist_respostas` (wide→long).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.domain.enums import SistemaOrigem, StatusVisita
from app.infrastructure.models import Checklist, ChecklistPergunta, Cliente, Visita
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.checklist_comum import gravar_respostas, obter_ou_criar_perguntas
from etl.conectores.leitura import AbaBruta, celula, indices_por_nome, ler_abas, localizar
from etl.loaders.apoio import obter_ou_criar_promotor, registrar_integracao_cliente
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_data_hora, para_texto

# Colunas de contexto do export real (normalizadas); todo o resto é pergunta.
_CONTEXTO = {
    "CODIGO",
    "FUNCIONARIO",
    "UF",
    "RAZAO_SOCIAL",
    "FANTASIA",
    "VISITA",
    "CK_ID",
    "CHECKLIST",
    "APLICACAO",
}


class ConectorChecklistSb(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        abas = [aba for aba in ler_abas(caminho) if not aba.vazia]
        if not abas:
            return ResultadoConector(
                erros=[ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados.")],
                estrutural_invalido=True,
            )

        session = execucao.session
        clientes_por_codigo = {
            codigo: id_
            for codigo, id_ in session.execute(select(Cliente.codigo_externo, Cliente.id))
        }

        resultado = ResultadoConector()
        abas_validas = 0
        for aba in abas:
            processou = self._processar_aba(execucao, clientes_por_codigo, aba, resultado)
            abas_validas += 1 if processou else 0
        if abas_validas == 0:
            resultado.estrutural_invalido = True
        return resultado

    # ------------------------------------------------------------------ aba

    def _processar_aba(
        self,
        execucao: ExecucaoImportacao,
        clientes_por_codigo: dict[str, str],
        aba: AbaBruta,
        resultado: ResultadoConector,
    ) -> bool:
        cabecalho_normalizado = aba.cabecalho_normalizado()
        indices = indices_por_nome(cabecalho_normalizado)
        posicoes = {
            "codigo_promotor": localizar(indices, "CODIGO", ocorrencia=0),
            "nome_promotor": localizar(indices, "FUNCIONARIO"),
            "uf": localizar(indices, "UF"),
            "codigo_cliente": localizar(indices, "CODIGO", ocorrencia=1),
            "razao_social": localizar(indices, "RAZAO_SOCIAL"),
            "fantasia": localizar(indices, "FANTASIA"),
            "visita": localizar(indices, "VISITA"),
            "ck_id": localizar(indices, "CK_ID"),
            "checklist": localizar(indices, "CHECKLIST"),
            "aplicacao": localizar(indices, "APLICACAO"),
        }
        obrigatorias = ("codigo_promotor", "codigo_cliente", "visita", "ck_id", "aplicacao")
        if any(posicoes[campo] is None for campo in obrigatorias):
            resultado.erros.append(
                ErroLinha(
                    LINHA_ARQUIVO,
                    f"Aba '{aba.titulo}': estrutura inesperada para export de checklists "
                    "(CÓDIGO×2, VISITA, CK_ID e APLICAÇÃO são obrigatórias) — aba ignorada.",
                )
            )
            return False

        perguntas_posicoes = self._colunas_de_pergunta(aba, cabecalho_normalizado)
        contexto_extra_posicoes = {
            "UF": posicoes["uf"],
            "RAZAO_SOCIAL": posicoes["razao_social"],
            "FANTASIA": posicoes["fantasia"],
        }

        session = execucao.session
        template: Checklist | None = None
        perguntas_por_posicao: dict[int, ChecklistPergunta] = {}

        for numero, linha in enumerate(aba.linhas[1:], start=2):
            if all(v is None for v in linha):
                continue
            resultado.total_linhas += 1

            codigo_promotor = para_texto(celula(linha, posicoes["codigo_promotor"]))
            codigo_cliente = para_texto(celula(linha, posicoes["codigo_cliente"]))
            codigo_visita = para_texto(celula(linha, posicoes["visita"]))
            aplicacao = para_data_hora(celula(linha, posicoes["aplicacao"]))

            erros: list[ErroLinha] = []
            if not codigo_promotor or not codigo_cliente or not codigo_visita:
                erros.append(
                    ErroLinha(
                        numero,
                        f"Aba '{aba.titulo}': CÓDIGO (promotor), CÓDIGO (cliente) e VISITA "
                        "são obrigatórios.",
                        "VISITA",
                    )
                )
            if aplicacao is None:
                valor = para_texto(celula(linha, posicoes["aplicacao"]))
                erros.append(
                    ErroLinha(
                        numero,
                        f"Aba '{aba.titulo}': data/hora de APLICAÇÃO inválida.",
                        "APLICACAO",
                        valor,
                    )
                )
            if erros:
                resultado.erros.extend(erros)
                continue
            assert codigo_cliente is not None and codigo_visita is not None
            assert codigo_promotor is not None and aplicacao is not None

            cliente_id = clientes_por_codigo.get(codigo_cliente)
            if cliente_id is None:
                registrar_integracao_cliente(
                    session,
                    SistemaOrigem.SB_PROMOTOR,
                    codigo_cliente,
                    para_texto(celula(linha, posicoes["razao_social"])),
                    execucao.importacao_id,
                )
                resultado.erros.append(
                    ErroLinha(
                        numero,
                        f"Aba '{aba.titulo}': cliente não encontrado na Base de Clientes: "
                        f"{codigo_cliente} (pendência registrada em clientes_integracao).",
                        "CODIGO",
                        codigo_cliente,
                    )
                )
                continue

            if template is None:
                template = self._obter_template(execucao, aba, linha, posicoes)
                perguntas_por_posicao = obter_ou_criar_perguntas(
                    session, template, perguntas_posicoes
                )

            promotor = obter_ou_criar_promotor(
                session,
                codigo_promotor,
                para_texto(celula(linha, posicoes["nome_promotor"])),
                None,
                None,
            )
            visita = self._obter_visita(
                execucao,
                codigo_visita,
                promotor.id,
                cliente_id,
                aplicacao,
                template.nome,
                {
                    rotulo: para_texto(celula(linha, posicao))
                    for rotulo, posicao in contexto_extra_posicoes.items()
                    if posicao is not None
                }
                | {"CK_ID": template.codigo_externo, "ABA": aba.titulo},
            )
            conflitos = gravar_respostas(
                session,
                aba.titulo,
                numero,
                linha,
                visita,
                perguntas_por_posicao,
                execucao.importacao_id,
            )
            if conflitos:
                resultado.erros.extend(conflitos)
                continue
            resultado.persistidas += 1
        return True

    # ------------------------------------------------------------------ apoio

    def _colunas_de_pergunta(
        self, aba: AbaBruta, cabecalho_normalizado: list[str | None]
    ) -> list[tuple[int, str]]:
        """Posição + enunciado original de cada coluna que não é contexto."""

        cabecalho_original = aba.cabecalho()
        colunas: list[tuple[int, str]] = []
        codigos_vistos = 0
        for posicao, nome in enumerate(cabecalho_normalizado):
            if nome is None:
                continue
            if nome == "CODIGO":
                codigos_vistos += 1
                continue
            if nome in _CONTEXTO:
                continue
            enunciado = cabecalho_original[posicao]
            if enunciado:
                colunas.append((posicao, enunciado))
        return colunas

    def _obter_template(
        self,
        execucao: ExecucaoImportacao,
        aba: AbaBruta,
        linha: tuple[Any, ...],
        posicoes: dict[str, int | None],
    ) -> Checklist:
        session = execucao.session
        ck_id = para_texto(celula(linha, posicoes["ck_id"]))
        nome = para_texto(celula(linha, posicoes["checklist"])) or aba.titulo.strip()
        template = session.scalar(
            select(Checklist).where(
                Checklist.origem == SistemaOrigem.SB_PROMOTOR,
                Checklist.codigo_externo == ck_id,
            )
        )
        if template is None:
            template = Checklist(
                nome=nome,
                codigo_externo=ck_id,
                origem=SistemaOrigem.SB_PROMOTOR,
                tipo_promotor_alvo=None,  # a origem não informa; nunca inferir (12.3)
            )
            session.add(template)
            session.flush()
        return template

    def _obter_visita(
        self,
        execucao: ExecucaoImportacao,
        codigo_visita: str,
        promotor_id: str,
        cliente_id: str,
        aplicacao: Any,
        tipo_visita: str,
        dados_brutos: dict[str, Any],
    ) -> Visita:
        session = execucao.session
        visita = session.scalar(
            select(Visita).where(
                Visita.origem == SistemaOrigem.SB_PROMOTOR,
                Visita.codigo_externo == codigo_visita,
            )
        )
        if visita is None:
            visita = Visita(
                origem=SistemaOrigem.SB_PROMOTOR,
                codigo_externo=codigo_visita,
                promotor_id=promotor_id,
                cliente_id=cliente_id,
                data_visita=aplicacao.date(),
                hora_inicio=aplicacao.time(),
                tipo_visita=tipo_visita[:50],
                dados_brutos={k: v for k, v in dados_brutos.items() if v is not None},
                status=StatusVisita.REALIZADA,
                importacao_id=execucao.importacao_id,
            )
            session.add(visita)
            session.flush()
        return visita
