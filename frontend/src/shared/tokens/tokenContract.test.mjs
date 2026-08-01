// MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md / §19 Token-Primitive tests.
//
// Zero-new-dependency static contract tests. This repo has no test runner
// installed (no vitest/jest/@testing-library — confirmed by grep of
// node_modules/.pnpm at Wave 6.1 Gate A/Inventory time) and installing one
// would be a dependency/lockfile change, which is an absolute constraint
// violation for this task. These tests use only Node's built-in `node:test` +
// `node:assert` (ships with Node itself; no package.json/lockfile touched) and
// verify the actual source text of the token SSOT and the three reconciled
// primitives. They are static/source-level checks, not rendered-DOM behavior
// tests — see MONGLE_W6_1_FOUNDATION_IMPLEMENTATION_PLAN.md's "Testing note"
// and MONGLE_W6_1_PRIMITIVE_CONTRACT.md for the explicit disclosure of what
// this does and does not cover.
//
// Run with: node --test frontend/src/shared/tokens/tokenContract.test.mjs

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const frontendSrc = path.resolve(here, '..', '..');

function read(relPath) {
  return readFileSync(path.join(frontendSrc, relPath), 'utf8');
}

const globalCss = read('styles/global.css');
const avatarTsx = read('shared/components/Avatar/Avatar.tsx');
const avatarCss = read('shared/components/Avatar/Avatar.module.css');
const iconButtonTsx = read('shared/components/IconButton/IconButton.tsx');
const iconButtonCss = read('shared/components/IconButton/IconButton.module.css');
const buttonTsx = read('shared/components/Button/Button.tsx');
const buttonCss = read('shared/components/Button/Button.module.css');

// --- (A) Static token contract tests -----------------------------------

test('canonical brand accent (D2) is #5A35DF', () => {
  assert.match(globalCss, /--color-brand-600:\s*#5A35DF/);
});

test('canonical ink/text-primary (D3) is #17103A', () => {
  assert.match(globalCss, /--color-ink-900:\s*#17103A/);
});

test('canonical admin sidebar tone (D8) is #FBFAFE', () => {
  assert.match(globalCss, /--admin-sidebar-bg:\s*#FBFAFE/);
});

test('font-family stack (D4) places Noto Sans KR first, Pretendard as fallback', () => {
  assert.match(
    globalCss,
    /--font-family-base:\s*'Noto Sans KR',\s*Pretendard,\s*-apple-system,\s*BlinkMacSystemFont,\s*'Segoe UI',\s*sans-serif;/,
  );
});

test('root body/input font-family reference the canonical token, not a hardcoded family', () => {
  assert.match(globalCss, /body\s*{[^}]*font-family:\s*var\(--font-family-base\)/s);
  assert.match(globalCss, /input,\s*select,\s*textarea\s*{[^}]*font-family:\s*var\(--font-family-base\)/s);
});

test('Noto Sans KR CDN import requests only the weights actually consumed (400/600/700)', () => {
  assert.match(globalCss, /family=Noto\+Sans\+KR:wght@400;600;700/);
});

test('spacing scale (D14) includes the full 4..64px global semantic base', () => {
  for (const [name, px] of [
    ['--space-1', '4px'], ['--space-2', '8px'], ['--space-3', '12px'], ['--space-4', '16px'],
    ['--space-5', '20px'], ['--space-6', '24px'], ['--space-8', '32px'], ['--space-10', '40px'],
    ['--space-12', '48px'], ['--space-16', '64px'],
  ]) {
    assert.match(globalCss, new RegExp(`${name}:\\s*${px}`), `${name} should equal ${px}`);
  }
});

test('touch target minimum is frozen at 44px', () => {
  assert.match(globalCss, /--size-touch-min:\s*44px/);
});

test('legacy duplicate --danger token is flagged DEPRECATED_CANDIDATE, not silently reused', () => {
  assert.match(globalCss, /DEPRECATED_CANDIDATE[\s\S]{0,400}--danger:\s*#ef4444/);
  assert.match(globalCss, /--color-danger:\s*#EF4665/);
});

test('avatar size scale tokens (xs/sm/md/lg) match the tablet-confirmed values', () => {
  assert.match(globalCss, /--size-avatar-xs:\s*34px/);
  assert.match(globalCss, /--size-avatar-sm:\s*44px/);
  assert.match(globalCss, /--size-avatar-md:\s*60px/);
  assert.match(globalCss, /--size-avatar-lg:\s*78px/);
});

test('safe-area inset tokens are declared as additive aliases', () => {
  for (const side of ['top', 'right', 'bottom', 'left']) {
    assert.match(globalCss, new RegExp(`--safe-area-inset-${side}:\\s*env\\(safe-area-inset-${side}`));
  }
});

test('layout gutter/max-width foundation tokens are declared', () => {
  assert.match(globalCss, /--layout-gutter-mobile:\s*var\(--space-4\)/);
  assert.match(globalCss, /--layout-gutter-tablet:\s*var\(--space-6\)/);
  assert.match(globalCss, /--layout-content-max-width:\s*1440px/);
});

// --- (B) Avatar primitive tests -----------------------------------------

test('Avatar keeps every pre-existing numeric size option (API not broken)', () => {
  assert.match(avatarTsx, /export type AvatarSize = 28 \| 36 \| 44 \| 56 \| 72 \| AvatarNamedSize;/);
});

test('Avatar named-size map matches the canonical avatar token values', () => {
  assert.match(avatarTsx, /xs:\s*34,/);
  assert.match(avatarTsx, /sm:\s*44,/);
  assert.match(avatarTsx, /md:\s*60,/);
  assert.match(avatarTsx, /lg:\s*78,/);
});

test('Avatar requires an accessible name (alt) and preserves fallback aria-label semantics', () => {
  assert.match(avatarTsx, /alt: string;/);
  assert.match(avatarTsx, /aria-label=\{alt\}/);
});

test('Avatar image-failure fallback branch is still present (src ? <img> : fallback span)', () => {
  assert.match(avatarTsx, /\{src \? \(/);
  assert.match(avatarTsx, /styles\.fallback/);
});

// MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001: .avatar's overflow:hidden used
// to clip the corner-positioned .statusDot into a quarter-circle. The circular
// clip now lives on a dedicated inner wrapper so the status dot, a sibling of
// that wrapper, is never clipped.
test('circular clipping is scoped to an inner wrapper, not the outer .avatar box', () => {
  assert.doesNotMatch(avatarCss, /\.avatar\s*{[^}]*overflow:\s*hidden/s);
  assert.match(avatarCss, /\.avatarInner\s*{[^}]*overflow:\s*hidden/s);
});

test('Avatar renders the image/fallback inside the inner clipping wrapper', () => {
  assert.match(avatarTsx, /<span className=\{styles\.avatarInner\}>/);
});

test('statusDot is a sibling of avatarInner, not nested inside it (so it cannot be clipped by it)', () => {
  const openTag = avatarTsx.indexOf('<span className={styles.avatarInner}>');
  const closeTag = avatarTsx.indexOf('</span>', openTag);
  const statusDotIdx = avatarTsx.indexOf('styles.statusDot');
  assert.ok(openTag > -1 && closeTag > -1 && statusDotIdx > -1);
  assert.ok(statusDotIdx > closeTag, 'statusDot must be rendered after avatarInner closes');
});

// --- (C) IconButton primitive tests --------------------------------------

test('IconButton requires a label prop and renders it as aria-label (no functional change)', () => {
  assert.match(iconButtonTsx, /label:\s*string;/);
  assert.match(iconButtonTsx, /aria-label=\{label\}/);
});

test('IconButton enforces the 44px touch-target token', () => {
  assert.match(iconButtonCss, /min-width:\s*var\(--size-touch-min\)/);
  assert.match(iconButtonCss, /min-height:\s*var\(--size-touch-min\)/);
});

test('IconButton has a focus-visible state and a disabled state', () => {
  assert.match(iconButtonCss, /:focus-visible\s*{/);
  assert.match(iconButtonCss, /:disabled\s*{/);
});

test('IconButton defaults type to "button" (existing contract, unchanged)', () => {
  assert.match(iconButtonTsx, /type = 'button'/);
});

// --- (D) Button primitive tests -------------------------------------------

test('Button preserves its existing 3 variant keys — no mass-created new variants', () => {
  assert.match(buttonTsx, /type ButtonVariant = 'primary' \| 'ghost' \| 'dangerSm';/);
});

test('Button now defaults type to "button" (safe default, 0 consumers affected)', () => {
  assert.match(buttonTsx, /type = 'button'/);
});

test('Button is wired to canonical brand/ink tokens, not the legacy --accent/--muted set', () => {
  assert.match(buttonCss, /background:\s*var\(--color-brand-600\)/);
  assert.match(buttonCss, /color:\s*var\(--color-ink-700\)/);
  assert.doesNotMatch(buttonCss, /var\(--accent\)/);
  assert.doesNotMatch(buttonCss, /var\(--muted\)/);
});

test('Button has a focus-visible ring and a disabled state', () => {
  assert.match(buttonCss, /\.btn:focus-visible\s*{/);
  assert.match(buttonCss, /\.btn:disabled\s*{/);
});

test('Button meets the 44px touch-target minimum via the shared token', () => {
  assert.match(buttonCss, /min-height:\s*var\(--size-touch-min\)/);
});

test('Button does NOT add a loading state (no existing API supported one)', () => {
  assert.doesNotMatch(buttonTsx, /loading/i);
});
