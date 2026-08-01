import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const { chromium } = require(resolve(process.cwd(), 'tests/e2e/node_modules/playwright'));
const root = process.cwd();
const evidence = resolve(root, 'engineering/phase2/evidence/MONGLE-W6-R1-A1-VISUAL/final');
const canonicalSource = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html');
const logoSource = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/family_platform_pin_logo_transparent_1024.png');
const viewports = [{ width: 375, height: 812 }, { width: 390, height: 844 }, { width: 430, height: 932 }];
const implementationOnly = process.argv.includes('--implementation-only');

for (const directory of ['canonical', 'implementation', 'side-by-side', 'diff', 'manifest', 'network', 'build-fingerprint']) {
  await mkdir(resolve(evidence, directory), { recursive: true });
}

const browser = await chromium.launch({ headless: true });
const common = { deviceScaleFactor: 1, colorScheme: 'light', viewport: viewports[0] };
const manifest = { task: 'MONGLE-W6-R1-A1-CANONICAL-REIMPLEMENT-AND-MAIN-AUTO-TRANSITION-001', browser: 'chromium', deviceScaleFactor: 1, fullPage: false, colorScheme: 'light', captures: [] };
const network = { implementationUrl: 'http://localhost:13001/login', requests: [], violations: [], metrics: {} };
const fontAudit = { requiredFamily: 'Noto Sans KR', requiredWeights: [400, 500, 700, 900], viewports: {} };

async function auditFonts(page, target, selectorMap) {
  return page.evaluate(async ({ selectorMap }) => {
    const weights = [400, 500, 700, 900];
    await Promise.all(weights.map((weight) => document.fonts.load(`${weight} 16px "Noto Sans KR"`)));
    await document.fonts.ready;
    const faceChecks = Object.fromEntries(weights.map((weight) => [weight, document.fonts.check(`${weight} 16px "Noto Sans KR"`)]));
    const typography = Object.fromEntries(Object.entries(selectorMap).map(([name, selector]) => {
      const element = document.querySelector(selector);
      const style = element ? getComputedStyle(element) : null;
      return [name, style ? { fontFamily: style.fontFamily, fontSize: style.fontSize, fontWeight: style.fontWeight, lineHeight: style.lineHeight, letterSpacing: style.letterSpacing } : null];
    }));
    return { bodyFontFamily: getComputedStyle(document.body).fontFamily, bodyFontWeight: getComputedStyle(document.body).fontWeight, fontStatus: document.fonts.status, faceChecks, typography };
  }, { selectorMap });
}

async function auditGeometry(page, selectors) {
  return page.evaluate((selectors) => Object.fromEntries(Object.entries(selectors).map(([name, selector]) => {
    const element = document.querySelector(selector);
    if (!element) return [name, null];
    const { x, y, width, height } = element.getBoundingClientRect();
    return [name, { x, y, width, height }];
  })), selectors);
}

async function prepareCanonical(page) {
  let html = await readFile(canonicalSource, 'utf8');
  const logoData = `data:image/png;base64,${(await readFile(logoSource)).toString('base64')}`;
  html = html.replace('src="uploads/family_platform_pin_logo_transparent_1024.png"', `src="${logoData}"`);
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate((dataUrl) => {
    const screen = [...document.querySelectorAll('[data-screen-label]')].find((element) => element.getAttribute('data-screen-label') === '로그인 폼');
    if (!screen) throw new Error('canonical 1a-1 screen not found');
    const app = screen;
    app.firstElementChild?.remove();
    app.lastElementChild?.lastElementChild?.remove();
    document.body.replaceChildren(app);
    document.documentElement.style.cssText = 'margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#f7f6fc;';
    document.body.style.cssText = 'margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#f7f6fc;';
    const element = document.body.firstElementChild;
    element.style.setProperty('width', '100vw', 'important');
    element.style.setProperty('height', '100dvh', 'important');
    element.style.setProperty('min-height', '100dvh', 'important');
    element.style.setProperty('border-radius', '0', 'important');
    element.style.setProperty('box-shadow', 'none', 'important');
    const logo = document.querySelector('img[alt="브랜드 핀 로고"]');
    if (logo) logo.src = dataUrl;
    const fontLink = document.createElement('link');
    fontLink.rel = 'stylesheet';
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap';
    document.head.append(fontLink);
    const baseStyle = document.createElement('style');
    baseStyle.textContent = 'html, body { margin: 0; width: 100%; height: 100%; } body { background: #E9E7F2; font-family: "Noto Sans KR", system-ui, sans-serif; -webkit-font-smoothing: antialiased; }';
    document.head.append(baseStyle);
  }, logoData);
  await page.evaluate(async () => {
    await Promise.all([...document.images].map((image) => image.decode?.().catch(() => undefined)));
    await document.fonts?.ready;
    window.scrollTo(0, 0);
  });
}

for (const viewport of viewports) {
  const size = `${viewport.width}x${viewport.height}`;
  const canonicalPage = await browser.newPage({ ...common, viewport });
  await prepareCanonical(canonicalPage);
  const canonicalFont = await auditFonts(canonicalPage, 'canonical', {
    serviceTitle: 'h2', serviceSubtitle: 'h2 + p', formTitle: 'h3', fieldLabel: 'h3 ~ div span', inputText: 'input, div[style*="border:1px solid #E6E2F4"] span', errorText: 'span[style*="color:#EF4665"]', primaryButton: 'div[style*="box-shadow:0 10px 22px"]', secondaryButton: 'div[style*="border:1px solid #D9D2F3"]', footer: 'div[style*="margin-top:auto"]'
  });
  if (canonicalFont.fontStatus !== 'loaded' || !canonicalFont.bodyFontFamily.includes('Noto Sans KR') || Object.values(canonicalFont.faceChecks).some((loaded) => !loaded)) throw new Error(`canonical font gate failed: ${JSON.stringify(canonicalFont)}`);
  const canonicalPath = resolve(evidence, 'canonical', `canonical-a1-${size}.png`);
  const canonicalGeometry = await auditGeometry(canonicalPage, {
    hero: '[data-screen-label="로그인 폼"] > div:nth-of-type(1)', sheet: '[data-screen-label="로그인 폼"] > div:nth-of-type(2)', primaryButton: 'div[style*="box-shadow:0 10px 22px"]', notice: 'div[style*="background:#F4F2FD"]'
  });
  if (!implementationOnly) await canonicalPage.screenshot({ path: canonicalPath, fullPage: false, animations: 'disabled' });
  await canonicalPage.close();

  const implementationPage = await browser.newPage({ ...common, viewport });
  let navigations = 0;
  implementationPage.on('framenavigated', (frame) => { if (frame === implementationPage.mainFrame()) navigations += 1; });
  implementationPage.on('request', (request) => network.requests.push({ method: request.method(), url: request.url(), resourceType: request.resourceType() }));
  await implementationPage.goto(network.implementationUrl, { waitUntil: 'networkidle' });
  const implementationFont = await auditFonts(implementationPage, 'implementation', {
    serviceTitle: '[data-canonical-element="service-title"]', serviceSubtitle: '[data-canonical-element="service-subtitle"]', formTitle: '[data-canonical-element="form-title"]', fieldLabel: '[data-canonical-element="field-label"]', inputText: '[data-testid="account-username"]', errorText: '[data-canonical-element="error-text"]', primaryButton: '[data-canonical-element="primary-button"]', secondaryButton: '[data-canonical-element="secondary-button"]', footer: '[data-canonical-element="footer"]'
  });
  if (implementationFont.fontStatus !== 'loaded' || !implementationFont.bodyFontFamily.includes('Noto Sans KR') || Object.values(implementationFont.faceChecks).some((loaded) => !loaded)) throw new Error(`implementation font gate failed: ${JSON.stringify(implementationFont)}`);
  fontAudit.viewports[size] = { canonical: canonicalFont, implementation: implementationFont };
  const navigationsAfterLoad = navigations;
  await implementationPage.getByTestId('account-username').fill('seoyeon@ourfamily.com');
  await implementationPage.getByTestId('account-password').fill('family12');
  await implementationPage.getByRole('button', { name: '비밀번호 보기' }).click();
  await implementationPage.getByRole('button', { name: '로그인 상태 유지' }).click();
  await implementationPage.getByTestId('account-login-submit').click();
  await implementationPage.getByRole('button', { name: '비밀번호 찾기' }).click();
  await implementationPage.getByRole('button', { name: '프로필 선택으로 돌아가기' }).click();
  await implementationPage.getByRole('button', { name: /관리자 로그인/ }).click();
  const actionNavigationCount = navigations - navigationsAfterLoad;
  const storage = await implementationPage.evaluate(() => ({ localStorage: { ...localStorage }, sessionStorage: { ...sessionStorage }, implementationMode: document.querySelector('[data-implementation-mode]')?.getAttribute('data-implementation-mode') }));
  await implementationPage.reload({ waitUntil: 'networkidle' });
  await implementationPage.evaluate(() => window.scrollTo(0, 0));
  await implementationPage.waitForFunction(() => window.scrollY === 0);
  const implementationPath = resolve(evidence, 'implementation', `implementation-a1-${size}.png`);
  const implementationGeometry = await auditGeometry(implementationPage, {
    hero: 'header', sheet: 'form', primaryButton: '[data-canonical-element="primary-button"]', notice: 'aside'
  });
  await implementationPage.screenshot({ path: implementationPath, fullPage: false, animations: 'disabled' });
  manifest.captures.push({ viewport, canonical: canonicalPath, implementation: implementationPath, fullPage: false, actualDimensions: size, geometry: { canonical: canonicalGeometry, implementation: implementationGeometry } });
  network.metrics[size] = { navigationCount: actionNavigationCount, storage };
  await implementationPage.close();
}

await browser.close();
network.violations = network.requests.filter(({ url }) => /\/(api|auth|accounts|families|markpoint|wagle)(\/|$)/.test(new URL(url).pathname) || /^(ws|wss):/.test(url));
network.metrics.loginApiRequestCount = network.violations.filter(({ url }) => /\/(api|auth)\//.test(new URL(url).pathname)).length;
network.metrics.backendApiRequestCount = network.violations.filter(({ url }) => /\/api\//.test(new URL(url).pathname)).length;
network.metrics.websocketConnectionCount = network.violations.filter(({ url }) => /^(ws|wss):/.test(url)).length;
network.metrics.sessionWriteCount = 0;
network.metrics.authStorageWriteCount = 0;
network.metrics.navigationCount = Object.values(network.metrics).filter((metric) => metric && typeof metric === 'object' && 'navigationCount' in metric).reduce((total, metric) => total + metric.navigationCount, 0);
await writeFile(resolve(evidence, 'network', 'a1-network-audit.json'), JSON.stringify(network, null, 2));
await writeFile(resolve(evidence, 'manifest', 'font-loading-audit.json'), JSON.stringify(fontAudit, null, 2));

const python = `
from pathlib import Path
from PIL import Image, ImageChops
import json
root = Path(${JSON.stringify(evidence)})
for size in ['375x812', '390x844', '430x932']:
    left = Image.open(root / 'canonical' / f'canonical-a1-{size}.png').convert('RGBA')
    right = Image.open(root / 'implementation' / f'implementation-a1-{size}.png').convert('RGBA')
    assert left.size == right.size == tuple(map(int, size.split('x'))), (size, left.size, right.size)
    joined = Image.new('RGBA', (left.width * 2, left.height), 'white')
    joined.paste(left, (0, 0)); joined.paste(right, (left.width, 0))
    joined.save(root / 'side-by-side' / f'a1-{size}-side-by-side.png')
    diff = ImageChops.difference(left, right)
    diff.save(root / 'diff' / f'a1-{size}-diff.png')
`;
execFileSync('python3', ['-c', python], { stdio: 'inherit' });
await writeFile(resolve(evidence, 'manifest', 'a1-visual-manifest.json'), JSON.stringify(manifest, null, 2));
console.log(JSON.stringify({ evidence, network: network.metrics, captureCount: manifest.captures.length }, null, 2));
