"""Validador de Visitas (VALIDADOR.md, seção 9; IMPORTADOR.md, seção 7)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from app.domain.enums import StatusVisita
from etl.resultado import ErroLinha, LinhaValida, ResultadoValidacao
from etl.transformers import para_data, para_decimal, para_hora, para_texto
from etl.validators.contexto import ContextoValidacao


def _coordenada_valida(valor: Decimal | None, limite: int) -> bool:
    return valor is None or (-limite <= valor <= limite)


def validar_visitas(
    linhas: list[tuple[int, dict[str, Any]]], contexto: ContextoValidacao
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()

    for numero, bruto in linhas:
        erros: list[ErroLinha] = []
        codigo_promotor = para_texto(bruto.get("CODIGO_PROMOTOR"))
        codigo_cliente = para_texto(bruto.get("CODIGO_CLIENTE"))
        data_visita = para_data(bruto.get("DATA_VISITA"))
        hora_inicio = para_hora(bruto.get("HORA_INICIO"))
        hora_fim = para_hora(bruto.get("HORA_FIM"))
        latitude = para_decimal(bruto.get("LATITUDE"))
        longitude = para_decimal(bruto.get("LONGITUDE"))

        if not codigo_promotor:
            erros.append(
                ErroLinha(
                    numero, "Campo obrigatório não preenchido: CODIGO_PROMOTOR.", "CODIGO_PROMOTOR"
                )
            )
        elif contexto.promotor_id_por_codigo(codigo_promotor) is None:
            # REF-003: a Visita não cria promotores
            erros.append(
                ErroLinha(
                    numero,
                    f"Promotor não encontrado: {codigo_promotor}.",
                    "CODIGO_PROMOTOR",
                    codigo_promotor,
                )
            )

        if not codigo_cliente:
            erros.append(
                ErroLinha(
                    numero, "Campo obrigatório não preenchido: CODIGO_CLIENTE.", "CODIGO_CLIENTE"
                )
            )
        elif contexto.cliente_id_por_codigo(codigo_cliente) is None:
            # REF-002
            erros.append(
                ErroLinha(
                    numero,
                    f"Cliente não encontrado: {codigo_cliente}.",
                    "CODIGO_CLIENTE",
                    codigo_cliente,
                )
            )

        if data_visita is None:
            valor = para_texto(bruto.get("DATA_VISITA"))
            erros.append(
                ErroLinha(numero, f"Data inválida em DATA_VISITA: {valor}.", "DATA_VISITA", valor)
            )
        elif data_visita > date.today():
            # VIS-001
            erros.append(
                ErroLinha(
                    numero, "Data de visita não pode ser futura.", "DATA_VISITA", str(data_visita)
                )
            )

        if hora_inicio and hora_fim and hora_fim <= hora_inicio:
            # VIS-002
            erros.append(
                ErroLinha(numero, "Horário de término anterior ao horário de início.", "HORA_FIM")
            )

        status_texto = para_texto(bruto.get("STATUS"))
        status = StatusVisita.REALIZADA
        if status_texto:
            normalizado = status_texto.upper()
            if normalizado not in StatusVisita.__members__:
                # VIS-003
                erros.append(
                    ErroLinha(
                        numero,
                        f"Status de visita inválido: {status_texto}.",
                        "STATUS",
                        status_texto,
                    )
                )
            else:
                status = StatusVisita(normalizado)

        if not _coordenada_valida(latitude, 90) or not _coordenada_valida(longitude, 180):
            # VIS-004
            erros.append(ErroLinha(numero, "Coordenada geográfica inválida.", "LATITUDE"))

        if erros:
            resultado.erros.extend(erros)
            continue

        resultado.linhas_validas.append(
            LinhaValida(
                numero_linha=numero,
                dados={
                    "codigo_promotor": codigo_promotor,
                    "codigo_cliente": codigo_cliente,
                    "data_visita": data_visita,
                    "hora_inicio": hora_inicio,
                    "hora_fim": hora_fim,
                    "tipo_visita": para_texto(bruto.get("TIPO_VISITA")),
                    "latitude": latitude,
                    "longitude": longitude,
                    "observacoes": para_texto(bruto.get("OBSERVACOES")),
                    "status": status,
                },
            )
        )

    return resultado
