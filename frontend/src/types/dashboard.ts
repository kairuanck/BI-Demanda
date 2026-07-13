// Tipos espelhando os schemas Pydantic do Dashboard Executivo (Sprint 4).
// Campos `Decimal` no backend serializam como string em JSON — nunca `number`.

export interface OpcaoFiltro {
  id: string;
  nome: string;
}

export interface OpcaoUf {
  sigla: string;
  nome: string;
}

export interface OpcoesFiltro {
  anos: number[];
  ufs: OpcaoUf[];
  laboratorios: OpcaoFiltro[];
  tipos_promotor: OpcaoFiltro[];
  sistemas_origem: string[];
  supervisores: OpcaoFiltro[];
  promotores: OpcaoFiltro[];
}

export interface FiltrosDashboard {
  ano?: number;
  mes?: number;
  uf?: string;
  laboratorio_id?: string;
  tipo_promotor_id?: string;
  sistema_origem?: string;
  supervisor_id?: string;
  promotor_id?: string;
}

export interface KpisDashboard {
  faturamento_total: string;
  faturamento_carteira: string;
  faturamento_regiao: string | null;
  faturamento_fora_carteira: string | null;
  quantidade_clientes: number;
  clientes_positivados: number;
  cobertura_carteira: string | null;
  numero_visitas: number;
  numero_checklists: number;
}

export interface PontoSerieMensal {
  ano: number;
  mes: number;
  valor: string;
}

export interface PontoPositivacaoMensal {
  ano: number;
  mes: number;
  clientes_positivados_carteira: number;
  clientes_positivados_regiao: number;
  clientes_positivados_fora_carteira: number;
}

export interface PontoCategoria {
  rotulo: string;
  valor: string;
}

export interface PontoRankingPromotor {
  promotor_id: string;
  nome: string;
  indice_desempenho: string | null;
  cobertura: string | null;
  positivacao: string | null;
}

export interface PontoUf {
  uf_sigla: string;
  faturamento_total: string;
  quantidade_clientes: number;
}

export interface LinhaPromotor {
  promotor_id: string;
  nome: string;
  tipo: string | null;
  supervisor: string | null;
  sistema_origem: string | null;
  quantidade_clientes: number;
  numero_visitas: number;
  numero_checklists: number;
  cobertura_carteira: string | null;
  faturamento_carteira: string;
  faturamento_regiao: string;
}

export interface PaginaPromotores {
  itens: LinhaPromotor[];
  pagina: number;
  tamanho_pagina: number;
  total_itens: number;
  total_paginas: number;
}

export interface DetalhePromotor {
  promotor_id: string;
  nome: string;
  tipo: string | null;
  supervisor: string | null;
  codigo_externo: string | null;
  area: string | null;
  kpis: KpisDashboard;
  conformidade_checklist: string | null;
  indice_desempenho: string | null;
  evolucao_faturamento: PontoSerieMensal[];
  faturamento_por_laboratorio: PontoCategoria[];
}

export interface UltimaImportacao {
  id: string;
  tipo_arquivo: string;
  nome_arquivo_original: string;
  status: string;
  total_linhas: number;
  linhas_validas: number;
  linhas_invalidas: number;
  iniciado_em: string | null;
  concluido_em: string | null;
  criado_em: string;
  duracao_segundos: number | null;
}
