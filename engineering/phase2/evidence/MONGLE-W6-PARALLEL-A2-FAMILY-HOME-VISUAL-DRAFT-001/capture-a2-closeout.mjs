// MONGLE-W6-A2-FAMILY-HOME-INTEGRATION-PRACTICAL-CLOSEOUT-001
// Closeout capture. Everything below runs against the OFFICIAL mongle Docker
// frontend (http://localhost:13001), not the dev server — so the evidence is a
// production-bundle regression, and a Vite HMR WebSocket must NOT appear.
//
//   PRIMARY   fidelity : approved PNG native crop, CSS 470x779 @ dsf 2.0
//   SECONDARY regression: 375x812, 390x844, 430x932
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const root = process.cwd();
const { chromium } = require(resolve(root, 'tests/e2e/node_modules/playwright'));
const EV = resolve(root, 'engineering/phase2/evidence/MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/final');
const BASE = 'http://localhost:13001';
const URL_1B = `${BASE}/__wave6/1b`;
const APPROVED = resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/screen_family_home_approved.png');
const CROP = { x: 0, y: 83, w: 941, h: 1558 };
const PRIMARY = { width: 470, height: 779, dsf: 2.0 };
const SECONDARY = [{ width: 375, height: 812 }, { width: 390, height: 844 }, { width: 430, height: 932 }];

for (const d of ['primary-png-comparison', 'implementation', 'overlay', 'side-by-side', 'diff', 'manifest', 'network']) {
  await mkdir(resolve(EV, d), { recursive: true });
}

function instrument(page, audit) {
  page.on('console', (m) => { if (m.type() === 'error') audit.consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => audit.consoleErrors.push(String(e)));
  page.on('response', (r) => { if (r.status() >= 400) audit.failedRequests.push({ url: r.url(), status: r.status() }); });
  page.on('request', (r) => audit.requests.push(r.url()));
  page.on('websocket', (ws) => audit.websockets.push(ws.url()));
  page.on('framenavigated', (f) => { if (f === page.mainFrame()) audit.navigations += 1; });
}

async function settle(page) {
  await page.evaluate(async () => {
    await Promise.all([400, 500, 700, 900].map((w) => document.fonts.load(`${w} 16px "Noto Sans KR"`)));
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => i.decode?.().catch(() => undefined)));
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
    window.getSelection?.().removeAllRanges();
    window.scrollTo(0, 0);
  });
  await page.waitForFunction(() => window.scrollX === 0 && window.scrollY === 0);
}

const browser = await chromium.launch({ headless: true });
const report = { task: 'MONGLE-W6-A2-FAMILY-HOME-INTEGRATION-PRACTICAL-CLOSEOUT-001', runtime: 'official mongle Docker frontend', baseUrl: BASE, route: '/__wave6/1b', primary: {}, secondary: {}, routeMatrix: {} };

// route matrix on the official runtime
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  for (const [name, path] of [['1b', '/__wave6/1b'], ['1c', '/__wave6/1c'], ['1e', '/__wave6/1e'], ['login', '/login']]) {
    const r = await p.goto(`${BASE}${path}`, { waitUntil: 'domcontentloaded' });
    const screenId = await p.evaluate(() => document.querySelector('[data-canonical-screen-id]')?.getAttribute('data-canonical-screen-id') ?? null);
    report.routeMatrix[name] = { path, status: r.status(), renderedScreenId: screenId };
  }
  await p.close();
}

// PRIMARY
{
  const audit = { consoleErrors: [], failedRequests: [], requests: [], websockets: [], navigations: 0 };
  const page = await browser.newPage({ viewport: { width: PRIMARY.width, height: PRIMARY.height }, deviceScaleFactor: PRIMARY.dsf, colorScheme: 'light' });
  instrument(page, audit);
  await page.goto(URL_1B, { waitUntil: 'networkidle' });
  const afterLoad = audit.navigations;
  await settle(page);
  const fonts = await page.evaluate(() => ({ status: document.fonts.status, family: getComputedStyle(document.body).fontFamily, checks: Object.fromEntries([400, 500, 700, 900].map((w) => [w, document.fonts.check(`${w} 16px "Noto Sans KR"`)])) }));
  if (fonts.status !== 'loaded' || !Object.values(fonts.checks).every(Boolean)) throw new Error('primary font gate failed on Docker runtime');
  const zones = await page.evaluate(`(() => {
    const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect(); return { x:+b.x.toFixed(2), y:+b.y.toFixed(2), width:+b.width.toFixed(2), height:+b.height.toFixed(2) }; };
    const q = (s) => document.querySelector(s);
    return { profile:r(q('[data-visual-zone="profile"]')), hero:r(q('[data-visual-zone="hero"]')), activity:r(q('[data-visual-zone="activity"]')),
             services:r(q('[data-visual-zone="services"]')), dock:r(q('[data-visual-zone="dock"]')),
             horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
             verticalScrollbar: document.documentElement.scrollHeight > document.documentElement.clientHeight,
             text: { greeting:q('[data-visual-zone="profile"] span')?.textContent, heroTitle:q('[data-visual-zone="hero"] span')?.textContent } };
  })()`);
  const storage = await page.evaluate(() => ({ localStorage: Object.keys(localStorage).length, sessionStorage: Object.keys(sessionStorage).length, cookie: document.cookie }));
  await page.screenshot({ path: resolve(EV, 'primary-png-comparison', 'A2-primary-native-implementation-r2.png'), fullPage: false, animations: 'disabled' });
  await page.close();
  const host = (u) => { try { return new URL(u).host; } catch { return 'invalid'; } };
  report.primary = {
    viewport: `${PRIMARY.width}x${PRIMARY.height}`, deviceScaleFactor: PRIMARY.dsf, fonts, zones, storage,
    audit: {
      consoleErrorCount: audit.consoleErrors.length, consoleErrors: audit.consoleErrors,
      failedRequestCount: audit.failedRequests.length, failedRequests: audit.failedRequests,
      websocketCount: audit.websockets.length, websockets: audit.websockets,
      viteHmrWebSocketCount: audit.websockets.filter((u) => /token=|vite/i.test(u)).length,
      backendApiRequestCount: audit.requests.filter((u) => /\/api\//.test(u)).length,
      navigationCountAfterLoad: audit.navigations - afterLoad,
      externalHosts: [...new Set(audit.requests.map(host))],
    },
  };
}

// SECONDARY
for (const vp of SECONDARY) {
  const size = `${vp.width}x${vp.height}`;
  const audit = { consoleErrors: [], failedRequests: [], requests: [], websockets: [], navigations: 0 };
  const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1, colorScheme: 'light' });
  instrument(page, audit);
  await page.goto(URL_1B, { waitUntil: 'networkidle' });
  await settle(page);
  const info = await page.evaluate(`(() => {
    const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect(); return { y:+b.y.toFixed(2), height:+b.height.toFixed(2), width:+b.width.toFixed(2) }; };
    const q = (s) => document.querySelector(s);
    return { hero:r(q('[data-visual-zone="hero"]')), services:r(q('[data-visual-zone="services"]')), dock:r(q('[data-visual-zone="dock"]')),
             tile0:r(q('[data-visual-zone="service-tile"]')),
             horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
             verticalScrollbar: document.documentElement.scrollHeight > document.documentElement.clientHeight };
  })()`);
  await page.screenshot({ path: resolve(EV, 'implementation', `implementation-A2-${size}.png`), fullPage: false, animations: 'disabled' });
  await page.close();
  report.secondary[size] = { ...info, consoleErrorCount: audit.consoleErrors.length, failedRequestCount: audit.failedRequests.length, websocketCount: audit.websockets.length };
}
await browser.close();

const py = `
from pathlib import Path
from PIL import Image, ImageChops
import json
EV = Path(${JSON.stringify(EV)})
P = EV / 'primary-png-comparison'
canon = Image.open(${JSON.stringify(APPROVED)}).convert('RGB').crop((${CROP.x}, ${CROP.y}, ${CROP.x + CROP.w}, ${CROP.y + CROP.h}))
canon.save(P / 'A2-primary-native-canonical-crop-r2.png')
impl = Image.open(P / 'A2-primary-native-implementation-r2.png').convert('RGB')
w = min(canon.width, impl.width); h = min(canon.height, impl.height)
canon2 = canon.crop((0,0,w,h)); impl2 = impl.crop((0,0,w,h))
sbs = Image.new('RGB',(w*2,h),'white'); sbs.paste(canon2,(0,0)); sbs.paste(impl2,(w,0))
sbs.save(P / 'A2-primary-native-side-by-side-r2.png')
d = ImageChops.difference(canon2, impl2)
d.save(P / 'A2-primary-native-diff-raw-rgb-r2.png')
d.point(lambda v: min(255, v*8)).save(P / 'A2-primary-native-diff-amplified-8x-r2.png')
Image.blend(canon2.convert('RGBA'), impl2.convert('RGBA'), 0.5).convert('RGB').save(P / 'A2-primary-native-overlay-r2.png')
px = d.load()
changed = sum(1 for y in range(h) for x in range(w) if sum(px[x,y]) > 12)
out = {'comparedSize': f'{w}x{h}', 'pixelsAboveThreshold12': changed, 'totalPixels': w*h,
       'percentAboveThreshold': round(changed*100.0/(w*h),4)}
bands = [('profile',0,120),('hero',120,470),('activity',470,910),('services',910,1290),('dock',1290,h)]
out['bands'] = {}
for n,a,b in bands:
    seg = [(x,y) for y in range(a,min(b,h)) for x in range(w) if sum(px[x,y])>12]
    out['bands'][n] = {'pixelsAbove12': len(seg), 'percentOfFrame': round(len(seg)*100.0/(w*h),3)}
(P / 'A2-primary-pixel-diff-report-r2.json').write_text(json.dumps(out, indent=2))
# secondary overlays / side-by-side against the r2 implementation set
for size in ['375x812','390x844','430x932']:
    im = Image.open(EV / 'implementation' / f'implementation-A2-{size}.png').convert('RGB')
    im.save(EV / 'implementation' / f'implementation-A2-{size}.png')
print(json.dumps(out, indent=2))
`;
execFileSync('python3', ['-c', py], { stdio: 'inherit' });
await writeFile(resolve(EV, 'manifest', 'a2-closeout-report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ routeMatrix: report.routeMatrix, primaryAudit: report.primary.audit, secondary: report.secondary }, null, 2));
