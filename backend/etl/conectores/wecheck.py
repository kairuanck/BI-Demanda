"""Conector dos formulários WeCheck (promotoras Avert) — tipo WECHECK.

Estrutura real (DATA_PROFILING.md, seção 5.1): 1 aba por formulário;
colunas = perguntas (wide); 1 linha = 1 visita/evento registrado. Há
schema drift real entre meses (26→31 colunas) — o casamento é por nome
normalizado, tolerante a ausências.

Regras de negócio aplicadas (docs/DECISIONS.md, seção 12):
- 12.4: não há código de cliente e casamento fuzzy é proibido — cada
  `Local` vira `clientes_integracao` PENDENTE; a visita nasce com
  `cliente_id` nulo (ou vinculado, se a conciliação já ocorreu).
- 12.6: promotoras WeCheck são Trade (aplicado apenas na criação).
- 12.7 (análogo SB): 1 linha de formulário = 1 visita; formulário =
  template de checklist; respostas viram `checklist_respostas`.

Idempotência: o WeCheck não expõe id de visita — o conector deriva um
código externo determinístico (SHA-256 de formulário|autor|data|local),
usado na unicidade (origem, codigo_externo).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy import select

from app.domain.enums import SistemaOrigem, StatusConciliacao, StatusVisita, TipoPromotor
from app.infrastructure.models import Checklist, ChecklistPergunta, Visita
from etl.conectores.base import ConectorOrigem, ExecucaoImportacao, ResultadoConector
from etl.conectores.checklist_comum import gravar_respostas, obter_ou_criar_perguntas
from etl.conectores.leitura import AbaBruta, celula, indices_por_nome, ler_abas, localizar
from etl.loaders.apoio import obter_ou_criar_promotor_por_nome, registrar_integracao_cliente
from etl.resultado import LINHA_ARQUIVO, ErroLinha
from etl.transformers import para_data_hora, para_texto

# Colunas de contexto conhecidas (normalizadas). Colunas fora deste conjunto
# são perguntas do formulário. As marcadas com False não entram em
# dados_brutos por já terem campo próprio na visita.
_CONTEXTO = {
    "FORMULARIO",
    "DATA_/_HORA_DO_ITEM",
    "LOCAL",
    "ENDERECO",
    "CIDADE",
    "ESTADO",
    "AUTOR",
    "TAREFA",
    "DESCRICAO",
    "PERFIL",
    "VALIDADO",
    "STATUS_DA_TAREFA",
    "DATA_DE_ABERTURA_(EVENTO)",
}
_CONTEXTO_EXTRA = (
    "TAREFA",
    "DESCRICAO",
    "PERFIL",
    "VALIDADO",
    "STATUS_DA_TAREFA",
    "DATA_DE_ABERTURA_(EVENTO)",
)


def _codigo_visita_wecheck(formulario: str, autor: str, data_hora: str, local: str) -> str:
    base = f"{formulario}|{autor}|{data_hora}|{local}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:40]


class ConectorWeCheck(ConectorOrigem):
    def processar(self, caminho: Path, execucao: ExecucaoImportacao) -> ResultadoConector:
        abas = [aba for aba in ler_abas(caminho) if not aba.vazia]
        if not abas:
            return ResultadoConector(
                erros=[ErroLinha(LINHA_ARQUIVO, "Arquivo vazio ou sem dados.")],
                estrutural_invalido=True,
            )

        resultado = ResultadoConector()
        abas_validas = 0
        for aba in abas:
            processou = self._processar_aba(execucao, aba, resultado)
            abas_validas += 1 if processou else 0
        if abas_validas == 0:
            resultado.estrutural_invalido = True
        return resultado

    def _processar_aba(
        self, execucao: ExecucaoImportacao, aba: AbaBruta, resultado: ResultadoConector
    ) -> bool:
        cabecalho_normalizado = aba.cabecalho_normalizado()
        indices = indices_por_nome(cabecalho_normalizado)
        posicoes = {
            "formulario": localizar(indices, "FORMULARIO"),
            "data_hora": localizar(indices, "DATA_/_HORA_DO_ITEM", "DATA/HORA_DO_ITEM"),
            "local": localizar(indices, "LOCAL"),
            "endereco": localizar(indices, "ENDERECO"),
            "cidade": localizar(indices, "CIDADE"),
            "estado": localizar(indices, "ESTADO"),
            "autor": localizar(indices, "AUTOR"),
        }
        if posicoes["data_hora"] is None or posicoes["autor"] is None:
            resultado.erros.append(
                ErroLinha(
                    LINHA_ARQUIVO,
                    f"Aba '{aba.titulo}': estrutura inesperada para export WeCheck "
                    "(Data/Hora do Item e Autor são obrigatórias) — aba ignorada.",
                )
            )
            return False

        cabecalho_original = aba.cabecalho()
        perguntas_posicoes: list[tuple[int, str]] = [
            (posicao, enunciado)
            for posicao, nome in enumerate(cabecalho_normalizado)
            if nome is not None
            and nome not in _CONTEXTO
            and (enunciado := cabecalho_original[posicao])
        ]
        extras_posicoes = {
            nome: localizar(indices, nome) for nome in _CONTEXTO_EXTRA if nome in indices
        }

        session = execucao.session
        template: Checklist | None = None
        perguntas_por_posicao: dict[int, ChecklistPergunta] = {}

        for numero, linha in enumerate(aba.linhas[1:], start=2):
            if all(v is None for v in linha):
                continue
            resultado.total_linhas += 1

            autor = para_texto(celula(linha, posicoes["autor"]))
            data_hora = para_data_hora(celula(linha, posicoes["data_hora"]))
            local = para_texto(celula(linha, posicoes["local"]))
            formulario = para_texto(celula(linha, posicoes["formulario"])) or aba.titulo.strip()

            erros: list[ErroLinha] = []
            if autor is None:
                erros.append(
                    ErroLinha(numero, f"Aba '{aba.titulo}': Autor é obrigatório.", "AUTOR")
                )
            if data_hora is None:
                valor = para_texto(celula(linha, posicoes["data_hora"]))
                erros.append(
                    ErroLinha(
                        numero,
                        f"Aba '{aba.titulo}': Data/Hora do Item inválida.",
                        "DATA_/_HORA_DO_ITEM",
                        valor,
                    )
                )
            if erros:
                resultado.erros.extend(erros)
                continue
            assert autor is not None and data_hora is not None

            if template is None:
                template = self._obter_template(execucao, formulario)
                perguntas_por_posicao = obter_ou_criar_perguntas(
                    session, template, perguntas_posicoes
                )

            # 12.6: promotoras WeCheck são Trade (aplicado apenas na criação)
            promotora = obter_ou_criar_promotor_por_nome(session, autor, TipoPromotor.TRADE)

            integracao = None
            if local is not None:
                integracao = registrar_integracao_cliente(
                    session,
                    SistemaOrigem.WECHECK,
                    local,
                    local,
                    execucao.importacao_id,
                )

            codigo_visita = _codigo_visita_wecheck(
                formulario, autor, data_hora.isoformat(), local or ""
            )
            visita = session.scalar(
                select(Visita).where(
                    Visita.origem == SistemaOrigem.WECHECK,
                    Visita.codigo_externo == codigo_visita,
                )
            )
            if visita is None:
                cliente_id = (
                    integracao.cliente_id
                    if integracao is not None and integracao.status == StatusConciliacao.VINCULADO
                    else None
                )
                dados_brutos = {
                    rotulo: valor
                    for rotulo, posicao in extras_posicoes.items()
                    if (valor := para_texto(celula(linha, posicao))) is not None
                }
                visita = Visita(
                    origem=SistemaOrigem.WECHECK,
                    codigo_externo=codigo_visita,
                    promotor_id=promotora.id,
                    cliente_id=cliente_id,
                    cliente_integracao_id=integracao.id if integracao is not None else None,
                    data_visita=data_hora.date(),
                    hora_inicio=data_hora.time(),
                    tipo_visita=formulario[:50],
                    local_texto=local,
                    endereco_texto=para_texto(celula(linha, posicoes["endereco"])),
                    cidade_texto=para_texto(celula(linha, posicoes["cidade"])),
                    estado_texto=para_texto(celula(linha, posicoes["estado"])),
                    dados_brutos=dados_brutos or None,
                    status=StatusVisita.REALIZADA,
                    importacao_id=execucao.importacao_id,
                )
                session.add(visita)
                session.flush()

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

    def _obter_template(self, execucao: ExecucaoImportacao, formulario: str) -> Checklist:
        session = execucao.session
        template = session.scalar(
            select(Checklist).where(
                Checklist.origem == SistemaOrigem.WECHECK, Checklist.nome == formulario
            )
        )
        if template is None:
            template = Checklist(
                nome=formulario,
                origem=SistemaOrigem.WECHECK,
                tipo_promotor_alvo=None,  # a origem não informa; nunca inferir
            )
            session.add(template)
            session.flush()
        return template
