# tests/ (raiz do repositório)

Reservado para testes de ponta a ponta que atravessam backend **e** frontend simultaneamente (ver `TESTES.md`, seção 4.3), implementados a partir da Sprint 12.

Os testes unitários e de integração do backend ficam em `backend/tests/` (`pytest`) e os do frontend em `frontend/src/**/*.test.tsx` (`vitest`) — ver `docs/DECISIONS.md`.

`smoke.sh` é um script manual auxiliar (não faz parte da suíte automatizada) para verificar rapidamente, após `docker compose up`, que os dois serviços estão respondendo.
