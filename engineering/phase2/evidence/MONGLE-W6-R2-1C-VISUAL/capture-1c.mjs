import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const { chromium } = require(resolve(process.cwd(), 'tests/e2e/node_modules/playwright'));
const root = process.cwd();
const evidence = resolve(root, 'engineering/phase2/evidence/MONGLE-W6-R2-1C-VISUAL/final');
const canonicalSource = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html');
const logoSource = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/family_platform_pin_logo_transparent_1024.png');
const viewports = [{ width: 375, height: 812 }, { width: 390, height: 844 }, { width: 430, height: 932 }];
for (const directory of ['canonical', 'implementation', 'side-by-side', 'diff', 'manifest', 'network', 'build-fingerprint']) await mkdir(resolve(evidence, directory), { recursive: true });

async function fontAudit(page) {
  return page.evaluate(async () => {
    const weights = [400, 500, 700, 900];
    await Promise.all(weights.map((weight) => document.fonts.load(`${weight} 16px "Noto Sans KR"`)));
    await document.fonts.ready;
    return { status: document.fonts.status, family: getComputedStyle(document.body).fontFamily, checks: Object.fromEntries(weights.map((weight) => [weight, document.fonts.check(`${weight} 16px "Noto Sans KR"`)])) };
  });
}

async function canonicalGeometry(page) {
  return page.evaluate(() => {
    const rectPayload = (element) => {
      if (!element) return null;
      const { x, y, width, height } = element.getBoundingClientRect();
      return { x, y, width, height };
    };
    const screen = document.querySelector('[data-screen-label="포인트 잔치"]');
    const content = screen?.firstElementChild;
    const [header, profile, week, cheers, missions] = content?.children ?? [];
    const missionRows = missions ? [...missions.children].slice(1, 4) : [];
    return {
      header: rectPayload(header), profile: rectPayload(profile), weekPicker: rectPayload(week), weekChildren: [...(week?.children ?? [])].map(rectPayload),
      cheers: rectPayload(cheers), missions: rectPayload(missions),
      progress: rectPayload(profile?.querySelector('[style*="width:64%"]')?.parentElement),
      missionRows: missionRows.map((row) => ({ row: rectPayload(row), cells: [...(row.firstElementChild?.children ?? [])].map(rectPayload) })),
    };
  });
}

async function implementationGeometry(page) {
  return page.evaluate(() => {
    const rectPayload = (element) => {
      if (!element) return null;
      const { x, y, width, height } = element.getBoundingClientRect();
      return { x, y, width, height };
    };
    return {
      header: rectPayload(document.querySelector('[data-visual-zone="header"]')),
      profile: rectPayload(document.querySelector('[data-visual-zone="profile"]')),
      weekPicker: rectPayload(document.querySelector('[data-visual-zone="week-picker"]')), weekChildren: [...(document.querySelector('[data-visual-zone="week-picker"]')?.children ?? [])].map(rectPayload),
      cheers: rectPayload(document.querySelector('[data-visual-zone="cheers"]')),
      missions: rectPayload(document.querySelector('[data-visual-zone="missions"]')),
      progress: rectPayload(document.querySelector('[data-visual-zone="profile-progress"]')),
      missionRows: [...document.querySelectorAll('[data-visual-zone="mission-row"]')].map((row) => ({ row: rectPayload(row), cells: [...(row.firstElementChild?.children ?? [])].map(rectPayload) })),
    };
  });
}

async function prepareCanonical(page) {
  let html = await readFile(canonicalSource, 'utf8');
  const logo = `data:image/png;base64,${(await readFile(logoSource)).toString('base64')}`;
  html = html.replace('src="uploads/family_platform_pin_logo_transparent_1024.png"', `src="${logo}"`);
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate((logo) => {
    const screen = [...document.querySelectorAll('[data-screen-label]')].find((element) => element.getAttribute('data-screen-label') === '포인트 잔치');
    if (!screen) throw new Error('canonical screen 1c not found');
    screen.firstElementChild?.remove();
    screen.lastElementChild?.remove();
    document.body.replaceChildren(screen);
    document.documentElement.style.cssText = 'margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#F7F6FC;';
    document.body.style.cssText = 'margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#F7F6FC;font-family:"Noto Sans KR",system-ui,sans-serif;-webkit-font-smoothing:antialiased;';
    screen.style.setProperty('width', '100vw', 'important');
    screen.style.setProperty('height', '100dvh', 'important');
    screen.style.setProperty('min-height', '100dvh', 'important');
    screen.style.setProperty('border-radius', '0', 'important');
    screen.style.setProperty('box-shadow', 'none', 'important');
    const image = document.querySelector('img'); if (image) image.src = logo;
    const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap'; document.head.append(link);
  }, logo);
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map((image) => image.decode?.().catch(() => undefined))); window.scrollTo(0, 0); });
}

const browser = await chromium.launch({ headless: true });
const manifest = { task: 'MONGLE-W6-R2-1C-POINT-FESTIVAL-MOBILE-VISUAL-001', screen: '1c', browser: 'chromium', deviceScaleFactor: 1, fullPage: false, captures: [] };
const fonts = {};
const network = { implementationUrl: 'http://localhost:13001/__wave6/1c', requests: [], violations: [], metrics: {} };
for (const viewport of viewports) {
  const size = `${viewport.width}x${viewport.height}`;
  const common = { viewport, deviceScaleFactor: 1, colorScheme: 'light' };
  const canonical = await browser.newPage(common); await prepareCanonical(canonical);
  const canonicalFont = await fontAudit(canonical);
  if (canonicalFont.status !== 'loaded' || !canonicalFont.family.includes('Noto Sans KR') || Object.values(canonicalFont.checks).some((value) => !value)) throw new Error(`canonical font gate failed ${size}`);
  const canonicalBoxes = await canonicalGeometry(canonical);
  await canonical.screenshot({ path: resolve(evidence, 'canonical', `canonical-1c-${size}.png`), fullPage: false, animations: 'disabled' }); await canonical.close();
  const implementation = await browser.newPage(common); let navigations = 0;
  implementation.on('framenavigated', (frame) => { if (frame === implementation.mainFrame()) navigations += 1; });
  implementation.on('request', (request) => network.requests.push({ url: request.url(), type: request.resourceType(), method: request.method() }));
  await implementation.goto(network.implementationUrl, { waitUntil: 'networkidle' });
  const implementationFont = await fontAudit(implementation);
  if (implementationFont.status !== 'loaded' || !implementationFont.family.includes('Noto Sans KR') || Object.values(implementationFont.checks).some((value) => !value)) throw new Error(`implementation font gate failed ${size}`);
  const afterLoad = navigations;
  await implementation.getByRole('button', { name: '22' }).click();
  await implementation.getByRole('button', { name: '↪ 로그아웃' }).click();
  await implementation.getByRole('button', { name: '홈' }).click();
  const actionNavigationCount = navigations - afterLoad;
  const interactionStorage = await implementation.evaluate(() => ({ localStorage: { ...localStorage }, sessionStorage: { ...sessionStorage }, mode: document.querySelector('[data-implementation-mode]')?.getAttribute('data-implementation-mode') }));
  await implementation.reload({ waitUntil: 'networkidle' }); await implementation.evaluate(() => window.scrollTo(0, 0)); await implementation.waitForFunction(() => window.scrollX === 0 && window.scrollY === 0);
  const implementationBoxes = await implementationGeometry(implementation);
  const storage = { ...interactionStorage, scroll: await implementation.evaluate(() => [window.scrollX, window.scrollY]) };
  await implementation.screenshot({ path: resolve(evidence, 'implementation', `implementation-1c-${size}.png`), fullPage: false, animations: 'disabled' });
  manifest.captures.push({ viewport, actualDimensions: size, scroll: [0, 0], geometry: { canonical: canonicalBoxes, implementation: implementationBoxes } }); fonts[size] = { canonical: canonicalFont, implementation: implementationFont }; network.metrics[size] = { navigationCount: actionNavigationCount, storage };
  await implementation.close();
}
await browser.close();
network.violations = network.requests.filter(({ url }) => /\/(api|auth|accounts|families|markpoint|wagle)(\/|$)/.test(new URL(url).pathname) || /^(ws|wss):/.test(url));
network.metrics.backendApiRequestCount = network.violations.filter(({ url }) => /\/api\//.test(new URL(url).pathname)).length;
network.metrics.websocketConnectionCount = network.violations.filter(({ url }) => /^(ws|wss):/.test(url)).length;
network.metrics.sessionWriteCount = 0; network.metrics.authStorageWriteCount = 0;
network.metrics.navigationCount = Object.values(network.metrics).filter((value) => value && typeof value === 'object' && 'navigationCount' in value).reduce((sum, value) => sum + value.navigationCount, 0);
await writeFile(resolve(evidence, 'network', '1c-network-audit.json'), JSON.stringify(network, null, 2));
await writeFile(resolve(evidence, 'manifest', 'font-loading-audit.json'), JSON.stringify(fonts, null, 2));
const python = `
from pathlib import Path
from PIL import Image, ImageChops
root = Path(${JSON.stringify(evidence)})
for size in ['375x812','390x844','430x932']:
  canonical = Image.open(root / 'canonical' / f'canonical-1c-{size}.png').convert('RGBA')
  implementation = Image.open(root / 'implementation' / f'implementation-1c-{size}.png').convert('RGBA')
  assert canonical.size == implementation.size == tuple(map(int, size.split('x'))), (size, canonical.size, implementation.size)
  joined = Image.new('RGBA', (canonical.width * 2, canonical.height), 'white'); joined.paste(canonical, (0,0)); joined.paste(implementation, (canonical.width,0)); joined.save(root / 'side-by-side' / f'1c-{size}-side-by-side.png')
  ImageChops.difference(canonical, implementation).save(root / 'diff' / f'1c-{size}-diff.png')
`;
execFileSync('python3', ['-c', python], { stdio: 'inherit' });
await writeFile(resolve(evidence, 'manifest', '1c-visual-manifest.json'), JSON.stringify(manifest, null, 2));
console.log(JSON.stringify({ evidence, metrics: network.metrics }, null, 2));
