import { defineConfig, devices } from '@playwright/test'

const PORT = 4173

export default defineConfig({
  testDir: './e2e',
  // Tests share one emulator and reset its accounts in beforeEach, so they must not run in parallel.
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  // Real Firebase Auth Emulator plus the production build of the frontend. Backend API calls are
  // mocked per test with page.route, so these tests need no backend or database.
  webServer: [
    {
      command: 'npx -y firebase-tools@13.35.1 emulators:start --only auth --project demo-nexora',
      cwd: '..',
      url: 'http://127.0.0.1:9099',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: `npm run build && npx vite preview --port ${PORT} --strictPort`,
      cwd: '../frontend',
      url: `http://localhost:${PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        VITE_FIREBASE_API_KEY: 'demo-api-key',
        VITE_FIREBASE_AUTH_DOMAIN: 'demo-nexora.firebaseapp.com',
        VITE_FIREBASE_PROJECT_ID: 'demo-nexora',
        VITE_FIREBASE_AUTH_EMULATOR_URL: 'http://127.0.0.1:9099',
      },
    },
  ],
})
