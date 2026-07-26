import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './specs-naran',
  timeout: 30000,
  use: {
    baseURL: process.env.NARAN_PLAYWRIGHT_BASE_URL || 'http://localhost:13001',
    headless: true,
    screenshot: 'only-on-failure',
  },
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
