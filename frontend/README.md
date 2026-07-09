# Promotores BI — Frontend

Frontend do Promotores BI (React + Vite + TypeScript + TailwindCSS). Ver `FRONTEND.md` e `DESIGN_SYSTEM.md` na raiz do repositório para a especificação completa.

## Comandos

```bash
npm install
cp .env.example .env
npm run dev        # servidor de desenvolvimento em http://localhost:5173
npm run build       # build de produção em dist/
npm run lint         # ESLint
npm run format:check # Prettier (verificação)
npm run test          # Vitest
```

Requer o backend rodando em `http://localhost:8000` (ver `../backend/README.md` ou `DEPLOY.md`), ou ajuste `VITE_API_BASE_URL` em `.env`.
