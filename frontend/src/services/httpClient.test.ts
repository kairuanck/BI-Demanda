import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, httpGet } from "./httpClient";

describe("httpClient", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("retorna o corpo desserializado em caso de sucesso", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );

    await expect(httpGet<{ status: string }>("/health")).resolves.toEqual({ status: "ok" });
  });

  it("lança ApiError tipado quando o backend responde no formato padrão de erro", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({
          erro: { codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Cliente não encontrado." },
        }),
      }),
    );

    const promessa = httpGet("/clientes/999");
    await expect(promessa).rejects.toBeInstanceOf(ApiError);
    await promessa.catch((erro: ApiError) => {
      expect(erro.status).toBe(404);
      expect(erro.codigo).toBe("RECURSO_NAO_ENCONTRADO");
      expect(erro.message).toBe("Cliente não encontrado.");
    });
  });

  it("lança ApiError genérico quando a resposta de erro não é JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        json: async () => {
          throw new SyntaxError("corpo não é JSON");
        },
      }),
    );

    const promessa = httpGet("/health");
    await expect(promessa).rejects.toBeInstanceOf(ApiError);
    await promessa.catch((erro: ApiError) => {
      expect(erro.status).toBe(502);
      expect(erro.codigo).toBe("ERRO_INTERNO");
    });
  });
});
