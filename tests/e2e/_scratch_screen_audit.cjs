const { chromium } = require('playwright');

const ROUTES = [
  { path: '/family/schedule', label: '가족 일정' },
  { path: '/family/album', label: '앨범' },
  { path: '/family/todo', label: '할 일' },
  { path: '/family/members', label: '가족 구성원' },
  { path: '/family/notifications', label: '알림' },
  { path: '/family/rules', label: '가족 규칙' },
  { path: '/family/search', label: '검색' },
  { path: '/markpoint', label: '마크포인트' },
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.getByTestId('account-username').fill('owner.a');
  await page.getByTestId('account-password').fill('Synthetic!Pass9');
  await Promise.all([
    page.waitForURL(/\/family/, { timeout: 10000 }).catch(() => null),
    page.getByTestId('account-login-submit').click(),
  ]);
  await page.waitForTimeout(800);
  await page.selectOption('select', { label: 'Synthetic Family Alpha' });
  await page.waitForTimeout(1000);

  for (const r of ROUTES) {
    await page.goto(`http://localhost:5173${r.path}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    const safeName = r.path.replace(/\//g, '_');
    await page.screenshot({ path: `${process.argv[2]}${safeName}.png`, fullPage: true });
    console.log('captured', r.path, r.label);
  }
  await browser.close();
})();
