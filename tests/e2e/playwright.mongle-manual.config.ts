import { defineConfig, devices } from '@playwright/test';

// Companion to playwright.mongle.config.ts for `specs-mongle/**`, used when
// the caller is already running its own isolated backend+frontend (e.g. a
// throwaway disposable-Postgres stack started by hand, following the same
// pattern backend pytest verification uses) rather than the shared
// `docker compose -p mongle -f docker-compose.phase1.yml` stack that
// `playwright.mongle.config.ts`'s webServer brings up. That shared stack can
// already be running persistently for unrelated reasons (dev/staging use),
// and running its bring-up script re-seeds it — this config exists so a spec
// can be verified against a genuinely separate, disposable environment
// without touching that shared state. No webServer, no globalTeardown: this
// config brings nothing up and tears nothing down itself; the caller owns
// the full lifecycle of whatever `MONGLE_PLAYWRIGHT_BASE_URL` points at.
export default defineConfig({
  testDir: './specs-mongle',
  timeout: 30000,
  use: {
    baseURL: process.env.MONGLE_PLAYWRIGHT_BASE_URL || 'http://localhost:13001',
    headless: true,
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], browserName: 'chromium' } },
  ],
});
