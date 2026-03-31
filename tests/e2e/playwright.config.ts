import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  baseURL: 'http://localhost:3000',
  timeout: 30000,
  use: {
    headless: true,
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'docker-compose up -d',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
    timeout: 60000,
  },
});
