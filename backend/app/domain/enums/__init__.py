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
    """Códigos canônicos de `tipos_promotor` (tabela cadastral, Sprint 3).

    O tipo é informação cadastral — nunca inferido dos dados importados
    (definição de negócio, docs/DECISIONS.md, seção 12).
    """

    TECNICO = "TECNICO"
    TRADE = "TRADE"


class SistemaOrigem(enum.StrEnum):
    """Sistemas externos que originam dados operacionais (Sprint 3)."""

    SB_PROMOTOR = "SB_PROMOTOR"
    WECHECK = "WECHECK"
    PAINEL_AVERT = "PAINEL_AVERT"


class StatusConciliacao(enum.StrEnum):
    """Estado do vínculo de um identificador externo com um cliente interno."""

    PENDENTE = "PENDENTE"
    VINCULADO = "VINCULADO"
    IGNORADO = "IGNORADO"


class CategoriaComercial(enum.StrEnum):
    """Categoria das colunas de marca do faturamento real.

    BRINDE não é laboratório — é categoria comercial à parte
    (definição de negócio, docs/DECISIONS.md, seção 12).
    """

    LABORATORIO = "LABORATORIO"
    BRINDE = "BRINDE"


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
    """Tipos de arquivo aceitos pelo motor.

    Sprint 3 mapeia as fontes reais: CLIENTES = Base de Clientes;
    CARTEIRA = relatório Supervisor do SB Promotor (carteira mensal oficial);
    FATURAMENTO = matriz mensal Cliente×Marca; CHECKLIST = export de
    aplicações de checklist; WECHECK = formulários das promotoras Avert;
    PAINEL_AVERT = painel de carteira Avert; SB_PRODUTOS = detalhe de
    produtos por visita do SB Promotor. VISITAS permanece para o layout
    documental legado (sem fonte real correspondente).
    """

    CLIENTES = "CLIENTES"
    CARTEIRA = "CARTEIRA"
    FATURAMENTO = "FATURAMENTO"
    CHECKLIST = "CHECKLIST"
    VISITAS = "VISITAS"
    WECHECK = "WECHECK"
    PAINEL_AVERT = "PAINEL_AVERT"
    SB_PRODUTOS = "SB_PRODUTOS"


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
