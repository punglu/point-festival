// MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001
// A2 / canonical screen 1b visual evidence harness.
//
// Deliberately modelled on the passed 1c harness
// (engineering/phase2/evidence/MONGLE-W6-R2-1C-VISUAL/capture-1c.mjs) so A2's
// evidence is directly comparable with A1/1c: same canonical isolation rules,
// same device-chrome exclusions, same font/scroll gates, same viewport set.
//
// Run from the repository root with the A2 dev server already listening:
//   node engineering/phase2/evidence/MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/capture-a2.mjs
import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const root = process.cwd();
const { chromium } = require(resolve(root, 'tests/e2e/node_modules/playwright'));
const evidence = resolve(root, 'engineering/phase2/evidence/MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/final');
const canonicalSource = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html');
const logoSource = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/family_platform_pin_logo_transparent_1024.png');
const implementationUrl = 'http://127.0.0.1:4174/a2-family-home-preview.html';
const viewports = [{ width: 375, height: 812 }, { width: 390, height: 844 }, { width: 430, height: 932 }];

for (const directory of ['canonical', 'implementation', 'side-by-side', 'diff', 'overlay', 'manifest', 'network', 'build-fingerprint']) {
  await mkdir(resolve(evidence, directory), { recursive: true });
}

const rectFn = `(element) => { if (!element) return null; const { x, y, width, height } = element.getBoundingClientRect(); return { x, y, width, height }; }`;

async function fontAudit(page) {
  return page.evaluate(async () => {
    const weights = [400, 500, 700, 900];
    await Promise.all(weights.map((weight) => document.fonts.load(`${weight} 16px "Noto Sans KR"`)));
    await document.fonts.ready;
    return {
      status: document.fonts.status,
      family: getComputedStyle(document.body).fontFamily,
      checks: Object.fromEntries(weights.map((weight) => [weight, document.fonts.check(`${weight} 16px "Noto Sans KR"`)])),
    };
  });
}

function assertFontGate(audit, side, size) {
  const ok = audit.status === 'loaded' && audit.family.includes('Noto Sans KR') && Object.values(audit.checks).every(Boolean);
  if (!ok) throw new Error(`font gate failed — ${side} ${size}: ${JSON.stringify(audit)}`);
}

async function settle(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map((image) => image.decode?.().catch(() => undefined)));
    document.activeElement instanceof HTMLElement && document.activeElement.blur();
    if (window.getSelection) window.getSelection().removeAllRanges();
    window.scrollTo(0, 0);
  });
  await page.waitForFunction(() => window.scrollX === 0 && window.scrollY === 0);
}

async function overflowAudit(page) {
  return page.evaluate(() => ({
    scrollX: window.scrollX,
    scrollY: window.scrollY,
    documentScrollWidth: document.documentElement.scrollWidth,
    documentClientWidth: document.documentElement.clientWidth,
    horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
}

// Canonical 1b, after the two DEVICE_CHROME children are removed, is
// [ content wrapper, dock ]; the content wrapper is
// [ profile, hero, activity, services ].
async function canonicalGeometry(page) {
  return page.evaluate(`(() => {
    const rect = ${rectFn};
    const screen = document.querySelector('[data-screen-label="홈"]');
    const [content, dock] = screen.children;
    const [profile, hero, activity, services] = content.children;
    return {
      content: rect(content),
      profile: rect(profile),
      hero: rect(hero),
      heroCta: rect(hero.firstElementChild.children[2]),
      activity: rect(activity),
      activityRows: [...activity.children].slice(1).map(rect),
      services: rect(services),
      serviceTiles: [...services.children[1].children].map(rect),
      dock: rect(dock),
      dockItems: [...dock.children].map(rect),
    };
  })()`);
}

async function implementationGeometry(page) {
  return page.evaluate(`(() => {
    const rect = ${rectFn};
    const q = (selector) => document.querySelector(selector);
    const all = (selector) => [...document.querySelectorAll(selector)].map(rect);
    return {
      content: rect(q('[data-visual-zone="profile"]').parentElement),
      profile: rect(q('[data-visual-zone="profile"]')),
      hero: rect(q('[data-visual-zone="hero"]')),
      heroCta: rect(q('[data-visual-zone="hero"] button')),
      activity: rect(q('[data-visual-zone="activity"]')),
      activityRows: all('[data-visual-zone="activity-row"]'),
      services: rect(q('[data-visual-zone="services"]')),
      serviceTiles: all('[data-visual-zone="service-tile"]'),
      dock: rect(q('[data-visual-zone="dock"]')),
      dockItems: [...q('[data-visual-zone="dock"]').children].map(rect),
    };
  })()`);
}

async function prepareCanonical(page) {
  let html = await readFile(canonicalSource, 'utf8');
  const logo = `data:image/png;base64,${(await readFile(logoSource)).toString('base64')}`;
  html = html.replaceAll('src="uploads/family_platform_pin_logo_transparent_1024.png"', `src="${logo}"`);
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate((logo) => {
    const screen = [...document.querySelectorAll('[data-screen-label]')].find((element) => element.getAttribute('data-screen-label') === '홈');
    if (!screen) throw new Error('canonical screen 1b (홈) not found');
    // DEVICE_CHROME: OS status bar (first child) and home indicator (last child).
    screen.firstElementChild?.remove();
    screen.lastElementChild?.remove();
    // GALLERY_DECORATION: the "1b / 가족 홈" badge row is a sibling; dropping
    // every other body child removes it along with the presentation background.
    document.body.replaceChildren(screen);
    document.documentElement.style.cssText = 'margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#F7F6FC;';
    document.body.style.cssText = 'margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#F7F6FC;font-family:"Noto Sans KR",system-ui,sans-serif;-webkit-font-smoothing:antialiased;';
    screen.style.setProperty('width', '100vw', 'important');
    screen.style.setProperty('height', '100dvh', 'important');
    screen.style.setProperty('min-height', '100dvh', 'important');
    screen.style.setProperty('border-radius', '0', 'important');
    screen.style.setProperty('box-shadow', 'none', 'important');
    for (const image of document.images) image.src = logo;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap';
    document.head.append(link);
  }, logo);
  await settle(page);
}

const browser = await chromium.launch({ headless: true });
const manifest = {
  task: 'MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001',
  screen: 'A2', htmlAnchor: '1b', label: '가족 플랫폼 홈',
  status: 'DRAFT_NOT_MAIN_WORKTREE_INTEGRATED',
  browser: 'chromium', deviceScaleFactor: 1, fullPage: false, colorScheme: 'light',
  canonicalComparisonBase: 'canonical HTML 1b rendered per viewport (approved PNG is not a single-scale render of it — see measurement §3)',
  implementationUrl, captures: [],
};
const fonts = {};
const network = { implementationUrl, requests: [], violations: [], metrics: {} };

for (const viewport of viewports) {
  const size = `${viewport.width}x${viewport.height}`;
  const common = { viewport, deviceScaleFactor: 1, colorScheme: 'light' };

  const canonical = await browser.newPage(common);
  await prepareCanonical(canonical);
  const canonicalFont = await fontAudit(canonical);
  assertFontGate(canonicalFont, 'canonical', size);
  const canonicalBoxes = await canonicalGeometry(canonical);
  const canonicalOverflow = await overflowAudit(canonical);
  await canonical.screenshot({ path: resolve(evidence, 'canonical', `canonical-A2-${size}.png`), fullPage: false, animations: 'disabled' });
  await canonical.close();

  const implementation = await browser.newPage(common);
  let navigations = 0;
  implementation.on('framenavigated', (frame) => { if (frame === implementation.mainFrame()) navigations += 1; });
  implementation.on('request', (request) => network.requests.push({ url: request.url(), type: request.resourceType(), method: request.method() }));
  implementation.on('websocket', (socket) => network.violations.push({ url: socket.url(), type: 'websocket' }));
  const consoleErrors = [];
  implementation.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  implementation.on('pageerror', (error) => consoleErrors.push(String(error)));
  const failedRequests = [];
  implementation.on('response', (response) => { if (response.status() >= 400) failedRequests.push({ url: response.url(), status: response.status() }); });

  await implementation.goto(implementationUrl, { waitUntil: 'networkidle' });
  const afterLoad = navigations;
  const implementationFont = await fontAudit(implementation);
  assertFontGate(implementationFont, 'implementation', size);
  await settle(implementation);
  const implementationBoxes = await implementationGeometry(implementation);
  const implementationOverflow = await overflowAudit(implementation);
  const storage = await implementation.evaluate(() => ({
    localStorage: { ...localStorage },
    sessionStorage: { ...sessionStorage },
    cookie: document.cookie,
    mode: document.querySelector('[data-implementation-mode]')?.getAttribute('data-implementation-mode'),
    screenId: document.querySelector('[data-canonical-screen-id]')?.getAttribute('data-canonical-screen-id'),
  }));
  await implementation.screenshot({ path: resolve(evidence, 'implementation', `implementation-A2-${size}.png`), fullPage: false, animations: 'disabled' });

  manifest.captures.push({
    viewport, actualDimensions: size, scroll: [0, 0],
    geometry: { canonical: canonicalBoxes, implementation: implementationBoxes },
    overflow: { canonical: canonicalOverflow, implementation: implementationOverflow },
  });
  fonts[size] = { canonical: canonicalFont, implementation: implementationFont };
  network.metrics[size] = {
    navigationCountAfterLoad: navigations - afterLoad,
    consoleErrorCount: consoleErrors.length, consoleErrors,
    failedRequestCount: failedRequests.length, failedRequests,
    storage,
  };
  await implementation.close();
}
await browser.close();

const pathOf = (url) => { try { return new URL(url).pathname; } catch { return url; } };
network.violations.push(...network.requests.filter(({ url }) => /\/(api|auth|accounts|families|markpoint|wagle)(\/|$)/.test(pathOf(url)) || /^(ws|wss):/.test(url)));
network.metrics.backendApiRequestCount = network.violations.filter(({ url }) => /\/api\//.test(pathOf(url))).length;
network.metrics.websocketConnectionCount = network.violations.filter(({ type }) => type === 'websocket').length;
network.metrics.localStorageWriteCount = Object.values(network.metrics).filter((v) => v && v.storage).reduce((sum, v) => sum + Object.keys(v.storage.localStorage).length, 0);
network.metrics.sessionStorageWriteCount = Object.values(network.metrics).filter((v) => v && v.storage).reduce((sum, v) => sum + Object.keys(v.storage.sessionStorage).length, 0);
network.metrics.cookieCount = Object.values(network.metrics).filter((v) => v && v.storage).reduce((sum, v) => sum + (v.storage.cookie ? 1 : 0), 0);
network.metrics.navigationCount = Object.values(network.metrics).filter((v) => v && typeof v === 'object' && 'navigationCountAfterLoad' in v).reduce((sum, v) => sum + v.navigationCountAfterLoad, 0);
network.metrics.totalRequestCount = network.requests.length;
network.metrics.externalHosts = [...new Set(network.requests.map((r) => { try { return new URL(r.url).host; } catch { return 'invalid'; } }))];

await writeFile(resolve(evidence, 'network', 'a2-network-audit.json'), JSON.stringify(network, null, 2));
await writeFile(resolve(evidence, 'manifest', 'font-loading-audit.json'), JSON.stringify(fonts, null, 2));

const python = `
from pathlib import Path
from PIL import Image, ImageChops
import json
root = Path(${JSON.stringify(evidence)})
report = {}
for size in ['375x812','390x844','430x932']:
  canonical = Image.open(root / 'canonical' / f'canonical-A2-{size}.png').convert('RGBA')
  implementation = Image.open(root / 'implementation' / f'implementation-A2-{size}.png').convert('RGBA')
  assert canonical.size == implementation.size == tuple(map(int, size.split('x'))), (size, canonical.size, implementation.size)
  joined = Image.new('RGBA', (canonical.width * 2, canonical.height), 'white')
  joined.paste(canonical, (0, 0)); joined.paste(implementation, (canonical.width, 0))
  joined.save(root / 'side-by-side' / f'A2-{size}-side-by-side-r1.png')
  # Difference on RGBA yields alpha 0 everywhere (both images are opaque), which
  # renders the saved diff fully transparent and therefore unreadable. Diff on
  # RGB, then also emit an amplified copy so small residuals are actually visible.
  diff = ImageChops.difference(canonical.convert('RGB'), implementation.convert('RGB'))
  diff.save(root / 'diff' / f'A2-{size}-diff-r1.png')
  diff.point(lambda v: min(255, v * 8)).save(root / 'diff' / f'A2-{size}-diff-amplified-r1.png')
  Image.blend(canonical, implementation, 0.5).save(root / 'overlay' / f'A2-{size}-overlay-r1.png')
  px = diff.load()
  w, h = diff.size
  changed = sum(1 for y in range(h) for x in range(w) if sum(px[x, y]) > 12)
  report[size] = {'diffBoundingBox': diff.getbbox(), 'pixelsAboveThreshold12': changed, 'totalPixels': w * h,
                  'percentAboveThreshold': round(changed * 100.0 / (w * h), 4),
                  'maxChannelSumDelta': max(sum(px[x, y]) for y in range(h) for x in range(w))}
(root / 'manifest' / 'a2-pixel-diff-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
`;
execFileSync('python3', ['-c', python], { stdio: 'inherit' });

await writeFile(resolve(evidence, 'manifest', 'a2-visual-manifest.json'), JSON.stringify(manifest, null, 2));
console.log(JSON.stringify({ evidence, metrics: network.metrics }, null, 2));
