# Frontend

React 18 + TypeScript (strict) SPA built with Vite, Tailwind CSS and TanStack Query.

## Layout
- `src/app/`: entry, providers, routes
- `src/components/ui/`: reusable primitives (Button, Spinner)
- `src/components/layout/`: application shell (sidebar, top bar, mobile drawer)
- `src/features/<name>/`: feature modules; API hooks live in `api.ts`, never in components
- `src/pages/`: route targets
- `src/api/client.ts`: typed fetch wrapper for `/api/v1` with the standard error shape
- `src/test/`: Vitest + Testing Library tests and helpers

Design tokens from `docs/05-ui-ux-specification.md` are CSS variables in `src/styles/index.css`, mapped in `tailwind.config.ts`.

## Run
```bash
npm install
npm run dev        # http://localhost:5173, proxies /api to http://localhost:8000
```

## Checks
```bash
npm run typecheck
npm test
npm run build
```

## Environment
- `VITE_API_BASE_URL`: backend URL for deployed builds (Cloudflare Pages). Empty in local dev.
