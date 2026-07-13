// Tipos espelhando os schemas Pydantic da Visão 360º do Cliente (Sprint 5).
// Campos `Decimal` no backend serializam como string em JSON.

export interface FiltrosCliente {
  ano?: number;
  mes?: number;
  laboratorio_id?: string;
  sistema_origem?: string;
}

export interface KpisCliente {
  faturamento_acumulado: string;
  faturamento_12_meses: string;
  quantidade_laboratorios: number;
  quantidade_visitas: number;
  quantidade_checklists: number;
  dias_desde_ultima_visita: number | null;
  cobertura: string;
  positivacao: string;
}

export interface VinculoPromotorCliente {
  sistema_origem: string;
  promotor_id: string;
  nome: string;
  tipo: string | null;
  supervisor: string | null;
  quantidade_clientes_carteira: number;
  cobertura: string | null;
  faturamento_carteira: string;
}

export interface DetalheCliente {
  id: string;
  codigo_externo: string;
  razao_social: string;
  nome_fantasia: string | null;
  cidade: string;
  uf_sigla: string;
  cnpj_cpf: string | null;
  ativo: boolean;
  grupo_economico: string | null;
  segmento: string | null;
  vinculos: VinculoPromotorCliente[];
  kpis: KpisCliente;
}

export interface LinhaLaboratorioCliente {
  laboratorio: string;
  primeiro_ano: number;
  primeiro_mes: number;
  ultimo_ano: number;
  ultimo_mes: number;
  valor_acumulado: string;
  participacao_percentual: string;
}

export interface EventoTimeline {
  tipo: "VISITA" | "CHECKLIST" | "IMPORTACAO" | "ALTERACAO_CADASTRAL";
  data: string;
  titulo: string;
  descricao: string | null;
}

export interface PaginaTimeline {
  itens: EventoTimeline[];
  pagina: number;
  tamanho_pagina: number;
  total_itens: number;
  total_paginas: number;
}

export interface LinhaClienteBusca {
  id: string;
  codigo_externo: string;
  razao_social: string;
  nome_fantasia: string | null;
  cidade: string;
  uf_sigla: string;
  ativo: boolean;
}

export interface PaginaClientesBusca {
  itens: LinhaClienteBusca[];
  pagina: number;
  tamanho_pagina: number;
  total_itens: number;
  total_paginas: number;
}
