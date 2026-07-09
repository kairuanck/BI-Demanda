"""Exceções de domínio (ver BACKEND.md, seção 8)."""

from __future__ import annotations


class DominioError(Exception):
    """Classe base de toda exceção de domínio do Promotores BI."""


class RegistroNaoEncontradoError(DominioError):
    """Levantada quando um registro solicitado não existe."""


class PermissaoNegadaError(DominioError):
    """Levantada quando o usuário autenticado não tem permissão para a ação."""


class ValidacaoFalhouError(DominioError):
    """Levantada quando uma validação de negócio falha."""


class ArquivoDuplicadoError(DominioError):
    """Levantada quando um arquivo de importação já foi processado (HASH.md)."""


class ArquivoInvalidoError(DominioError):
    """Levantada quando um arquivo de importação é estruturalmente inválido."""
