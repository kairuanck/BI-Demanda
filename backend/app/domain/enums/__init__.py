"""Enums do sistema (ver DICIONARIO_DE_DADOS.md, seção 21).

Todos os enums são persistidos como `String` (native_enum=False), conforme
DATABASE.md, seção 3, item 6.
"""

from __future__ import annotations

import enum


class PerfilUsuario(enum.StrEnum):
    ADMINISTRADOR = "ADMINISTRADOR"
    SUPERVISOR = "SUPERVISOR"
    PROMOTOR = "PROMOTOR"
    DIRETORIA = "DIRETORIA"


class TipoPromotor(enum.StrEnum):
    TECNICO = "TECNICO"
    TRADE = "TRADE"


class TipoPromotorAlvo(enum.StrEnum):
    """Público-alvo de um template de checklist (promotores.tipo + AMBOS)."""

    TECNICO = "TECNICO"
    TRADE = "TRADE"
    AMBOS = "AMBOS"


class StatusCarteira(enum.StrEnum):
    ATIVA = "ATIVA"
    ENCERRADA = "ENCERRADA"


class StatusVisita(enum.StrEnum):
    REALIZADA = "REALIZADA"
    CANCELADA = "CANCELADA"
    PENDENTE = "PENDENTE"


class TipoRespostaChecklist(enum.StrEnum):
    SIM_NAO = "SIM_NAO"
    MULTIPLA_ESCOLHA = "MULTIPLA_ESCOLHA"
    NUMERICO = "NUMERICO"
    TEXTO = "TEXTO"


class TipoArquivoImportacao(enum.StrEnum):
    CLIENTES = "CLIENTES"
    CARTEIRA = "CARTEIRA"
    FATURAMENTO = "FATURAMENTO"
    CHECKLIST = "CHECKLIST"
    VISITAS = "VISITAS"


class StatusImportacao(enum.StrEnum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDA = "CONCLUIDA"
    CONCLUIDA_COM_ERROS = "CONCLUIDA_COM_ERROS"
    FALHOU = "FALHOU"
    REVERTIDA = "REVERTIDA"


class AcaoAuditoria(enum.StrEnum):
    CRIACAO = "CRIACAO"
    ATUALIZACAO = "ATUALIZACAO"
    EXCLUSAO = "EXCLUSAO"
    IMPORTACAO = "IMPORTACAO"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ROLLBACK = "ROLLBACK"
    EXPORTACAO = "EXPORTACAO"
