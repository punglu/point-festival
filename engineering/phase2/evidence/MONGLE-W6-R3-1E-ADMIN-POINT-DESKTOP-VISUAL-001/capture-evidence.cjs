/* Evidence producer for the UI-only `/__wave6/1e` preview.
 * It writes only within this task-owned evidence folder. The approved PNG is
 * never altered: because the canonical crop contract is 0,0,1448,1086, its
 * byte-identical copy is the comparison source. */
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { chromium } = require('../../../../tests/e2e/node_modules/playwright');

const root = path.resolve(__dirname);
const canonicalSource = path.resolve(root, '../mongle-wave6-tablet-canonical/assets/uploads/screen_admin_point_approved.png');
const output = {
  canonical: path.join(root, 'canonical'), implementation: path.join(root, 'implementation'),
  comparison: path.join(root, 'comparison'), diff: path.join(root, 'diff'), manifests: path.join(root, 'manifests'),
};
for (const dir of Object.values(output)) fs.mkdirSync(dir, { recursive: true });
const canonicalCopy = path.join(output.canonical, 'canonical-original.png');
fs.copyFileSync(canonicalSource, canonicalCopy);

const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const dataUrl = (file) => `data:image/png;base64,${fs.readFileSync(file).toString('base64')}`;

async function canvasImage(browser, name, render) {
  const page = await browser.newPage({ viewport: { width: 2896, height: 1086 }, deviceScaleFactor: 1, colorScheme: 'light' });
  await page.setContent('<canvas id="canvas"></canvas>');
  await page.evaluate(async ({ canonical, implementation, mode }) => {
    const load = (src) => new Promise((resolve, reject) => { const image = new Image(); image.onload = () => resolve(image); image.onerror = reject; image.src = src; });
    const [left, right] = await Promise.all([load(canonical), load(implementation)]);
    const canvas = document.getElementById('canvas');
    canvas.width = mode === 'diff' || mode === 'overlay' ? left.width : left.width + right.width;
    canvas.height = left.height;
    const context = canvas.getContext('2d');
    if (mode === 'overlay') { context.globalAlpha = .5; context.drawImage(left, 0, 0); context.drawImage(right, 0, 0); }
    else if (mode === 'diff') {
      const first = document.createElement('canvas'); first.width = left.width; first.height = left.height;
      const second = document.createElement('canvas'); second.width = right.width; second.height = right.height;
      const a = first.getContext('2d'); const b = second.getContext('2d'); a.drawImage(left, 0, 0); b.drawImage(right, 0, 0);
      const ai = a.getImageData(0, 0, left.width, left.height); const bi = b.getImageData(0, 0, right.width, right.height); const result = context.createImageData(left.width, left.height);
      for (let index = 0; index < ai.data.length; index += 4) {
        const delta = Math.abs(ai.data[index] - bi.data[index]) + Math.abs(ai.data[index + 1] - bi.data[index + 1]) + Math.abs(ai.data[index + 2] - bi.data[index + 2]);
        result.data[index] = delta > 12 ? 238 : ai.data[index] * .18;
        result.data[index + 1] = delta > 12 ? 70 : ai.data[index + 1] * .18;
        result.data[index + 2] = delta > 12 ? 101 : ai.data[index + 2] * .18;
        result.data[index + 3] = 255;
      }
      context.putImageData(result, 0, 0);
    } else { context.drawImage(left, 0, 0); context.drawImage(right, left.width, 0); }
  }, { canonical: dataUrl(canonicalCopy), implementation: dataUrl(path.join(output.implementation, 'implementation.png')), mode: render });
  await page.locator('#canvas').screenshot({ path: name });
  await page.close();
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1448, height: 1086 }, deviceScaleFactor: 1, colorScheme: 'light' });
  const requests = []; const consoleErrors = []; const navigations = [];
  page.on('request', request => requests.push({ url: request.url(), type: request.resourceType(), method: request.method() }));
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => consoleErrors.push(String(error)));
  page.on('framenavigated', frame => { if (frame === page.mainFrame()) navigations.push(frame.url()); });
  await page.goto('http://localhost:13001/__wave6/1e', { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; window.scrollTo(0, 0); });
  const initialNavigationCount = navigations.length;
  const fontAudit = await page.evaluate(() => ({
    status: document.fonts.status,
    checks: [400, 500, 700, 900].map(weight => ({ weight, loaded: document.fonts.check(`${weight} 16px \"Noto Sans KR\"`) })),
    scroll: [window.scrollX, window.scrollY],
    root: (() => { const r = document.querySelector('[data-canonical-screen-id="1e"]').getBoundingClientRect(); return { width:r.width, height:r.height, x:r.x, y:r.y }; })(),
  }));
  const storageBefore = await page.evaluate(() => ({ local: JSON.stringify(localStorage), session: JSON.stringify(sessionStorage), cookie: document.cookie }));
  const rootLocator = page.locator('[data-canonical-screen-id="1e"]');
  await rootLocator.screenshot({ path: path.join(output.implementation, 'implementation.png'), animations: 'disabled' });
  await page.getByRole('button', { name: '차감 추가' }).click();
  await page.getByRole('button', { name: '전체 필터' }).click();
  await page.getByRole('button', { name: '서연 내역 수정' }).first().click();
  const storageAfter = await page.evaluate(() => ({ local: JSON.stringify(localStorage), session: JSON.stringify(sessionStorage), cookie: document.cookie }));
  await page.close();
  await canvasImage(browser, path.join(output.comparison, 'side-by-side.png'), 'side-by-side');
  await canvasImage(browser, path.join(output.diff, 'pixel-diff.png'), 'diff');
  await canvasImage(browser, path.join(output.comparison, 'visual-overlay.png'), 'overlay');
  await browser.close();
  const files = [canonicalCopy, path.join(output.implementation, 'implementation.png'), path.join(output.comparison, 'side-by-side.png'), path.join(output.comparison, 'visual-overlay.png'), path.join(output.diff, 'pixel-diff.png')];
  const evidence = files.map(file => ({ file: path.relative(root, file), size: fs.statSync(file).size, sha256: sha256(file) }));
  fs.writeFileSync(path.join(output.manifests, 'network-audit.json'), JSON.stringify({ requests, consoleErrors, navigations, initialNavigationCount, storageBefore, storageAfter, counts: { backendApi: requests.filter(r => /localhost:18001|\/api\//.test(r.url)).length, websocket: requests.filter(r => /^ws/.test(r.url)).length, navigation: navigations.length - initialNavigationCount, storageChanged: Number(JSON.stringify(storageBefore) !== JSON.stringify(storageAfter)) } }, null, 2));
  fs.writeFileSync(path.join(output.manifests, 'font-audit.json'), JSON.stringify(fontAudit, null, 2));
  fs.writeFileSync(path.join(output.manifests, '1e-visual-manifest.json'), JSON.stringify({ task: 'MONGLE-W6-R3-1E-ADMIN-POINT-DESKTOP-VISUAL-001', route: '/__wave6/1e', canonicalBounds: [0,0,1448,1086], comparison: { crop: 0, resize: 0, deviceScaleFactor: 1, fullPage: false }, files: evidence, status: 'READY_FOR_GPT_VISUAL_REVIEW_PENDING_DRIVE' }, null, 2));
  fs.writeFileSync(path.join(output.manifests, 'SHA256SUMS.txt'), evidence.map(entry => `${entry.sha256}  ${entry.file}`).join('\n') + '\n');
})().catch(error => { console.error(error); process.exit(1); });
