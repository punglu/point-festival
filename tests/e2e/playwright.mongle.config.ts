import { defineConfig, devices } from '@playwright/test';

// MONGLE-FE-E2E-HARNESS-RESTORE-001: webServer/globalTeardown restore the
// previously-deleted isolated mc_phase1 stack (db+backend+frontend,
// ports 15434/18001/13001) so this suite is runnable again without any
// shared/operating environment dependency. See
// tests/e2e/scripts/start-mongle-phase1.sh and docker-compose.phase1.yml.
export default defineConfig({
  testDir: './specs-mongle',
  timeout: 30000,
  use: {
    baseURL: process.env.MONGLE_PLAYWRIGHT_BASE_URL || 'http://localhost:13001',
    headless: true,
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: './scripts/start-mongle-phase1.sh',
    url: process.env.MONGLE_PLAYWRIGHT_BASE_URL || 'http://localhost:13001',
    reuseExistingServer: true,
    timeout: 180000,
  },
  globalTeardown: process.env.MONGLE_SKIP_TEARDOWN ? undefined : './scripts/mongle-phase1-teardown.ts',
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], browserName: 'chromium' } },
    // Chromium viewport emulation is intentional here; Safari/device evidence
    // remains a Human Gate rather than a claim from this shell baseline.
    { name: 'iphone', use: { ...devices['iPhone 13'], browserName: 'chromium' } },
    { name: 'ipad', use: { ...devices['iPad Pro 11'], browserName: 'chromium' } },
    { name: 'android-tablet-portrait', use: { ...devices['Pixel 5'], viewport: { width: 800, height: 1280 }, isMobile: true } },
    { name: 'android-tablet-landscape', use: { ...devices['Pixel 5'], viewport: { width: 1280, height: 800 }, isMobile: true } },
  ],
});
