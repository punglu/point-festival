import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { defineConfig, devices } from '@playwright/test';

// MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001: compute the frontend
// source fingerprint here, in the Playwright process, and hand the same value
// down to the bring-up script. Computing it only inside the script would leave
// the tests with nothing to compare against — a child process cannot export a
// variable back to its parent — so the "is this the current build?" assertion
// would silently skip, which is the failure mode this whole task exists to fix.
process.env.MONGLE_FRONTEND_FINGERPRINT ??= execFileSync(
  path.join(__dirname, 'scripts', 'frontend-source-fingerprint.sh'),
  { encoding: 'utf8' },
).trim();

// MONGLE-FE-E2E-HARNESS-RESTORE-001: webServer/globalTeardown restore the
// isolated mongle stack (db+backend+frontend,
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
    // MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001: was `true`, which is
    // the second stale-image path and the one `--build` cannot close — when
    // something already answers on this port Playwright skips the start script
    // entirely, so neither the rebuild nor the current-source guard ever runs.
    // That is exactly how a previous run produced 41 failures against an image
    // built before the source under test existed. Bring-up is idempotent and
    // layer-cached, so paying for it every run is cheaper than a result that
    // silently describes the wrong build.
    reuseExistingServer: false,
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
