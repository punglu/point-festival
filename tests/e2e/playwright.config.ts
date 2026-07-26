import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  timeout: 30000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:13000',
    headless: true,
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'docker compose -p mc_phase0 --env-file ../../.env.phase0.example -f ../../docker-compose.phase0.yml up -d --build',
    url: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:13000',
    reuseExistingServer: true,
    timeout: 60000,
  },
});
