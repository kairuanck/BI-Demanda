import { useQuery } from "@tanstack/react-query";

import { httpGet } from "../services/httpClient";

interface HealthResponse {
  status: string;
  database: string;
}

// Usado apenas para validar a comunicação frontend<->backend nesta Sprint
// (SPRINT_00.md, Critérios de Aceite) — não é uma funcionalidade de negócio.
export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => httpGet<HealthResponse>("/health"),
    retry: 1,
  });
}
