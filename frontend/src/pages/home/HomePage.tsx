import { useHealthCheck } from "../../hooks/useHealthCheck";

export function HomePage() {
  const { data, isLoading, isError } = useHealthCheck();

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-8">
      <h1 className="text-2xl font-semibold text-slate-900">Bem-vindo ao Promotores BI</h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-500">
        Plataforma de Business Intelligence para gestão de Promotores Técnicos e Promotores Trade do
        mercado pet. Esta é a infraestrutura da Sprint 0 — ver README.md e SPRINT_00.md.
      </p>

      <div className="mt-6 flex items-center gap-2 text-sm">
        <span className="font-medium text-slate-700">Status da API:</span>
        {isLoading && <span className="text-slate-400">verificando...</span>}
        {isError && <span className="text-danger">indisponível</span>}
        {data && (
          <span className="inline-flex items-center gap-1 text-success">
            <span className="h-2 w-2 rounded-full bg-success" />
            {data.status} · banco {data.database}
          </span>
        )}
      </div>
    </div>
  );
}
