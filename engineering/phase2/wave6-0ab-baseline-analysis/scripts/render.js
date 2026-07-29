// Read-only evidence capture: render approved standalone-src.html via existing
// Playwright install and dump full-page screenshot + zone bounding boxes.
// Writes ONLY under /tmp/mongle-wave6-0ab/. Does not modify the source file,
// does not touch the product Playwright config/tests.
const path = require("path");
const fs = require("fs");

const PW_MODULE = "/Users/mac/mac_Project/minecraft_points_festivals_doran_ui/tests/e2e/node_modules/playwright";
const { chromium } = require(PW_MODULE);

const OUT_DIR = "/tmp/mongle-wave6-0ab/evidence/approved-html-render";
const URL = "http://127.0.0.1:18321/standalone-src.html";

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1700, height: 1200 } });
  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => consoleErrors.push(String(err)));

  await page.goto(URL, { waitUntil: "networkidle", timeout: 30000 });
  // give the dc-runtime a moment to boot React and render the template
  await page.waitForTimeout(2000);

  await page.screenshot({ path: path.join(OUT_DIR, "full_canvas.png"), fullPage: true });

  const screenIds = ["1a", "1a-1", "1b", "1c", "1d", "1e", "1f", "1g", "1h", "1i"];
  const result = await page.evaluate((ids) => {
    const out = {};
    for (const id of ids) {
      const el = document.getElementById(id);
      if (!el) { out[id] = null; continue; }
      const inner = el.querySelector("[data-screen-label]");
      const target = inner || el;
      const r = target.getBoundingClientRect();
      const cs = window.getComputedStyle(target);
      out[id] = {
        label: inner ? inner.getAttribute("data-screen-label") : null,
        x: r.x, y: r.y, width: r.width, height: r.height,
        borderRadius: cs.borderRadius,
        background: cs.backgroundColor || cs.backgroundImage,
        boxShadow: cs.boxShadow,
      };
    }
    return out;
  }, screenIds);

  fs.writeFileSync(path.join(OUT_DIR, "zone_bounding_boxes.json"), JSON.stringify(result, null, 2));

  // Resize viewport to cover the full document so clip-based crops work for
  // zones below the fold (Playwright's non-fullPage clip is viewport-relative).
  const docSize = await page.evaluate(() => ({
    width: Math.ceil(document.documentElement.scrollWidth),
    height: Math.ceil(document.documentElement.scrollHeight),
  }));
  await page.setViewportSize({ width: Math.min(docSize.width, 4000), height: Math.min(docSize.height, 8000) });
  await page.waitForTimeout(300);

  // per-screen crop screenshots for visual delta comparison against approved PNGs
  for (const id of screenIds) {
    const info = result[id];
    if (!info || !info.width) continue;
    try {
      await page.screenshot({
        path: path.join(OUT_DIR, `screen_${id.replace("-", "_")}.png`),
        clip: { x: Math.max(0, info.x), y: Math.max(0, info.y), width: info.width, height: info.height },
      });
    } catch (e) {
      fs.appendFileSync(path.join(OUT_DIR, "render_errors.log"), `crop ${id} failed: ${e}\n`);
    }
  }

  fs.writeFileSync(path.join(OUT_DIR, "console_errors.json"), JSON.stringify(consoleErrors, null, 2));

  await browser.close();
  console.log("DONE");
  console.log(JSON.stringify(result, null, 2));
})().catch((e) => {
  console.error("RENDER_FAILED", e);
  fs.writeFileSync("/tmp/mongle-wave6-0ab/evidence/approved-html-render/render_errors.log", String(e && e.stack || e));
  process.exit(1);
});
