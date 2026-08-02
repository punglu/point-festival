// MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001 — supplementary evidence.
//
// The primary harness renders the canonical document with the canonical
// source's OWN font delivery (Noto Sans KR only), per the 1c precedent. The app
// instead loads a four-family Google Fonts stylesheet from
// frontend/src/styles/global.css (a protected path). Measured consequence: the
// U+0020 advance is 2.500px in the canonical document and 3.094px in the
// implementation document at 11px/700, while every Korean glyph run measures
// identically. Text after a space therefore shifts sub-pixel.
//
// This script re-renders the canonical document under the APP's font stylesheet
// and reports the resulting diff, so the Main Architect can see how much of the
// residual is font-environment rather than A2 fidelity. It writes only to the
// manifest folder and changes no source.
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
const APP_FONT_URL = 'https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&family=Black+Han+Sans&family=Inter:wght@300;500;700&family=Noto+Sans+KR:wght@400;500;700;900&display=swap';
const tmp = resolve(evidence, 'manifest', 'font-env-probe');
await mkdir(tmp, { recursive: true });

const browser = await chromium.launch({ headless: true });
const report = {};
for (const viewport of [{ width: 375, height: 812 }, { width: 390, height: 844 }, { width: 430, height: 932 }]) {
  const size = `${viewport.width}x${viewport.height}`;
  let html = await readFile(canonicalSource, 'utf8');
  const logo = `data:image/png;base64,${(await readFile(logoSource)).toString('base64')}`;
  html = html.replaceAll('src="uploads/family_platform_pin_logo_transparent_1024.png"', `src="${logo}"`);
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1, colorScheme: 'light' });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(async ({ logo, fontUrl }) => {
    const screen = [...document.querySelectorAll('[data-screen-label]')].find((e) => e.getAttribute('data-screen-label') === '홈');
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
    for (const image of document.images) image.src = logo;
    // The one difference from the primary harness: the APP's font stylesheet.
    const link = document.createElement('link');
    link.rel = 'stylesheet'; link.href = fontUrl;
    document.head.append(link);
    await new Promise((done) => { link.onload = done; link.onerror = done; });
    await Promise.all([400, 500, 700, 900].map((w) => document.fonts.load(`${w} 16px "Noto Sans KR"`)));
    await document.fonts.ready;
    window.scrollTo(0, 0);
  }, { logo, fontUrl: APP_FONT_URL });
  report[size] = await page.evaluate(() => {
    const s = document.createElement('span');
    s.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;font-size:11px;font-weight:700;font-family:"Noto Sans KR", system-ui, sans-serif';
    document.body.appendChild(s);
    const w = (t) => { s.textContent = t; return +s.getBoundingClientRect().width.toFixed(3); };
    const out = { spaceAdvancePx: w(' '), koreanRunPx: w('포인트잔치') };
    s.remove();
    return out;
  });
  await page.screenshot({ path: resolve(tmp, `canonical-appfontenv-${size}.png`), fullPage: false, animations: 'disabled' });
  await page.close();
}
await browser.close();

const python = `
from pathlib import Path
from PIL import Image, ImageChops
import json
root = Path(${JSON.stringify(evidence)}); tmp = Path(${JSON.stringify(tmp)})
out = {}
for size in ['375x812','390x844','430x932']:
  a = Image.open(tmp / f'canonical-appfontenv-{size}.png').convert('RGB')
  b = Image.open(root / 'implementation' / f'implementation-A2-{size}.png').convert('RGB')
  d = ImageChops.difference(a, b); px = d.load(); w, h = d.size
  changed = sum(1 for y in range(h) for x in range(w) if sum(px[x, y]) > 12)
  out[size] = {'pixelsAboveThreshold12': changed, 'totalPixels': w*h, 'percentAboveThreshold': round(changed*100.0/(w*h), 4)}
(tmp / 'diff-under-app-font-environment.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
`;
execFileSync('python3', ['-c', python], { stdio: 'inherit' });
await writeFile(resolve(tmp, 'space-advance-measurement.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
