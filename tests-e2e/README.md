# End-to-end tests

Playwright smoke tests for critical flows. They run against the production build of the frontend
(`vite preview`) with API responses mocked via `page.route`, so no backend or database is needed.
Full-stack flows (auth, incidents) are added from M1/M2.

```bash
npm install
npx playwright install chromium
npm test
```
