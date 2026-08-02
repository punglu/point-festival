// MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-CORRECTION-001
// PRIMARY comparison: implementation vs the APPROVED PNG's native content bounds.
// Authority: approved PNG = visual-final. Crop only; no resize/stretch/warp of
// either side. The implementation is rendered at a native device scale so its
// raster lands on the PNG's own pixel grid.
//
// Scale derivation (recorded, not invented):
//   No HTML value is assumed. A least-squares fit of PNG-measured landmark
//   heights (hero 467, activity 447, services 341) against the implementation's
//   own CSS heights returns deviceScaleFactor = 1.9961, i.e. 2.0, giving a design
//   canvas of 941/2 = 470.5 x 1672/2 = 836 CSS px — the signature of a standard
//   2x design export. rms residual 9.44 px, the best of every scale tested
//   (1.9604 -> 10.12, 2.05 -> 10.17, 2.2951 -> 23.20). This RESOLVES D-A2-5.
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const root = process.cwd();
const { chromium } = require(resolve(root, 'tests/e2e/node_modules/playwright'));
const evidence = resolve(root, 'engineering/phase2/evidence/MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/final/primary-png-comparison');
await mkdir(evidence, { recursive: true });

// Approved-PNG app-content crop (DEVICE_CHROME excluded, crop only).
const CROP = { x: 0, y: 83, w: 941, h: 1558 };   // status-bar bottom .. home-indicator top
const W = 470, DSF = 2.0;
const H = Math.round(CROP.h / DSF);              // 684

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: DSF, colorScheme: 'light' });
await page.goto('http://127.0.0.1:4174/a2-family-home-preview.html', { waitUntil: 'networkidle' });
await page.evaluate(async () => {
  await Promise.all([400, 500, 700, 900].map((w) => document.fonts.load(`${w} 16px "Noto Sans KR"`)));
  await document.fonts.ready;
  await Promise.all([...document.images].map((i) => i.decode?.().catch(() => undefined)));
  document.activeElement instanceof HTMLElement && document.activeElement.blur();
  window.getSelection?.().removeAllRanges();
  window.scrollTo(0, 0);
});
const fontAudit = await page.evaluate(() => ({
  status: document.fonts.status,
  checks: Object.fromEntries([400, 500, 700, 900].map((w) => [w, document.fonts.check(`${w} 16px "Noto Sans KR"`)])),
}));
if (fontAudit.status !== 'loaded' || !Object.values(fontAudit.checks).every(Boolean)) throw new Error('primary font gate failed');

const zones = await page.evaluate(`(() => {
  const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect(); return { x:+b.x.toFixed(2), y:+b.y.toFixed(2), width:+b.width.toFixed(2), height:+b.height.toFixed(2) }; };
  const q = (s) => document.querySelector(s);
  return {
    profile:  r(q('[data-visual-zone="profile"]')),
    hero:     r(q('[data-visual-zone="hero"]')),
    activity: r(q('[data-visual-zone="activity"]')),
    services: r(q('[data-visual-zone="services"]')),
    dock:     r(q('[data-visual-zone="dock"]')),
    documentHeight: document.documentElement.scrollHeight,
    horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  };
})()`);

await page.screenshot({ path: resolve(evidence, 'implementation-native-clipped.png'), fullPage: false, animations: 'disabled' });
await page.screenshot({ path: resolve(evidence, 'implementation-native-fullpage.png'), fullPage: true, animations: 'disabled' });
await page.close();
await browser.close();

// Approved-PNG zone landmarks, measured directly from the PNG in absolute PNG px.
const pngZones = {
  profileTop: 103, heroTop: 226, heroBottom: 642,
  activityTop: 683, activityBottom: 1129,
  servicesTop: 1189, servicesBottom: 1491,
  dockTop: 1511, cardLeft: 41, cardRight: 898,
};
const toCss = (v) => +((v - CROP.y) / DSF).toFixed(2);
const comparison = {
  task: 'MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-CORRECTION-001',
  authority: 'APPROVED_PNG = visual-final. canonical HTML = structure/content/CSS reference only.',
  approvedPng: {
    path: 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/screen_family_home_approved.png',
    sha256: 'd486d0eb921b1cf5ed4085fe9d23bc5d4597399c5415406af5674c5c4070e9f2',
    fullDimensions: '941x1672', contentBounds: '0,0,941,1672', appContentCrop: CROP,
  },
  scaleDerivation: { method: 'least-squares fit of PNG landmark heights vs implementation CSS heights; assumes no HTML value', fittedDeviceScaleFactor: 1.9961, usedDeviceScaleFactor: DSF, designCanvasCssPx: '470.5 x 836', rmsResidualPx: 9.44, alternativesTested: { '1.9604': 10.12, '2.05': 10.17, '2.2951': 23.2 } },
  fontAudit,
  implementationCss: zones,
  approvedPngCssEquivalent: {
    profileTop: toCss(pngZones.profileTop),
    heroTop: toCss(pngZones.heroTop), heroHeight: +((pngZones.heroBottom - pngZones.heroTop + 1) / DSF).toFixed(2),
    activityTop: toCss(pngZones.activityTop), activityHeight: +((pngZones.activityBottom - pngZones.activityTop + 1) / DSF).toFixed(2),
    servicesTop: toCss(pngZones.servicesTop), servicesHeight: +((pngZones.servicesBottom - pngZones.servicesTop + 1) / DSF).toFixed(2),
    dockTop: toCss(pngZones.dockTop),
  },
};
comparison.deltaCssPx = {
  profileTop: +(zones.profile.y - comparison.approvedPngCssEquivalent.profileTop).toFixed(2),
  heroTop: +(zones.hero.y - comparison.approvedPngCssEquivalent.heroTop).toFixed(2),
  heroHeight: +(zones.hero.height - comparison.approvedPngCssEquivalent.heroHeight).toFixed(2),
  activityTop: +(zones.activity.y - comparison.approvedPngCssEquivalent.activityTop).toFixed(2),
  activityHeight: +(zones.activity.height - comparison.approvedPngCssEquivalent.activityHeight).toFixed(2),
  servicesTop: +(zones.services.y - comparison.approvedPngCssEquivalent.servicesTop).toFixed(2),
  servicesHeight: +(zones.services.height - comparison.approvedPngCssEquivalent.servicesHeight).toFixed(2),
  dockTop: +(zones.dock.y - comparison.approvedPngCssEquivalent.dockTop).toFixed(2),
};
await writeFile(resolve(evidence, 'primary-comparison.json'), JSON.stringify(comparison, null, 2));

const python = `
from pathlib import Path
from PIL import Image, ImageChops
import json
root = Path(${JSON.stringify(evidence)})
src = Path(${JSON.stringify(resolve(root, 'engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/screen_family_home_approved.png'))})
canon = Image.open(src).convert('RGB').crop((${CROP.x}, ${CROP.y}, ${CROP.x + CROP.w}, ${CROP.y + CROP.h}))
canon.save(root / 'canonical-approved-png-appcontent-crop.png')
impl = Image.open(root / 'implementation-native-clipped.png').convert('RGB')
if impl.size != canon.size:
    impl = impl.crop((0, 0, min(impl.width, canon.width), min(impl.height, canon.height)))
    canon2 = canon.crop((0, 0, impl.width, impl.height))
else:
    canon2 = canon
joined = Image.new('RGB', (canon2.width*2, canon2.height), 'white')
joined.paste(canon2, (0,0)); joined.paste(impl, (canon2.width,0))
joined.save(root / 'A2-primary-native-side-by-side-r1.png')
d = ImageChops.difference(canon2, impl)
d.save(root / 'A2-primary-native-diff-r1.png')
d.point(lambda v: min(255, v*8)).save(root / 'A2-primary-native-diff-amplified-r1.png')
Image.blend(canon2.convert('RGBA'), impl.convert('RGBA'), 0.5).save(root / 'A2-primary-native-overlay-r1.png')
px = d.load(); w,h = d.size
changed = sum(1 for y in range(h) for x in range(w) if sum(px[x,y]) > 12)
(root / 'primary-pixel-diff-report.json').write_text(json.dumps({
  'comparedSize': f'{w}x{h}', 'implementationRasterSize': f'{impl.width}x{impl.height}',
  'pixelsAboveThreshold12': changed, 'totalPixels': w*h,
  'percentAboveThreshold': round(changed*100.0/(w*h), 4)}, indent=2))
print(json.dumps({'comparedSize': f'{w}x{h}', 'percentAboveThreshold': round(changed*100.0/(w*h), 4)}, indent=2))
`;
execFileSync('python3', ['-c', python], { stdio: 'inherit' });
console.log(JSON.stringify({ implementationCss: zones, delta: comparison.deltaCssPx }, null, 2));
