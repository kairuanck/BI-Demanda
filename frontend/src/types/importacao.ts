// Tipos espelhando os schemas Pydantic de Importação (Sprint 2/6).

export type TipoArquivoImportacao =
  | "CLIENTES"
  | "CARTEIRA"
  | "FATURAMENTO"
  | "CHECKLIST"
  | "VISITAS"
  | "WECHECK"
  | "PAINEL_AVERT"
  | "SB_PRODUTOS";

export type StatusImportacao =
  "PENDENTE" | "PROCESSANDO" | "CONCLUIDA" | "CONCLUIDA_COM_ERROS" | "FALHOU" | "REVERTIDA";

export interface Importacao {
  id: string;
  tipo_arquivo: TipoArquivoImportacao;
  nome_arquivo_original: string;
  hash_sha256: string;
  hash_conteudo: string | null;
  tamanho_bytes: number;
  competencia: string | null;
  usuario_id: string;
  usuario_nome: string;
  status: StatusImportacao;
  versao: number;
  importacao_pai_id: string | null;
  total_linhas: number;
  linhas_validas: number;
  linhas_invalidas: number;
  iniciado_em: string | null;
  concluido_em: string | null;
  criado_em: string;
  duracao_segundos: number | null;
}

export interface ImportacaoErro {
  id: string;
  numero_linha: number;
  coluna: string | null;
  valor_recebido: string | null;
  mensagem_erro: string;
}

export interface PaginaImportacoes {
  itens: Importacao[];
  pagina: number;
  tamanho_pagina: number;
  total_itens: number;
  total_paginas: number;
}

export interface PaginaErrosImportacao {
  itens: ImportacaoErro[];
  pagina: number;
  tamanho_pagina: number;
  total_itens: number;
  total_paginas: number;
}

export interface FiltrosHistoricoImportacoes {
  tipo_arquivo?: TipoArquivoImportacao;
  status?: StatusImportacao;
}

// Estado de um arquivo na fila de envio da tela de Importações (Sprint 6) —
// puramente do lado do cliente, não existe no backend.
export type EstadoEnvio = "enviando" | "processando" | "concluido" | "erro" | "cancelado";

export interface ArquivoNaFila {
  idLocal: string;
  arquivo: File;
  estado: EstadoEnvio;
  progresso: number;
  resultado?: Importacao;
  mensagemErro?: string;
}
