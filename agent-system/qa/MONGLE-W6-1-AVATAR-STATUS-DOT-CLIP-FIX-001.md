# MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001 Evidence

- Task ID: `MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001`
- Verification: `NOT_TESTED`
- Self-check only: `true`
- Independent QA: `pending` — shared Foundation primitive change, per PM direction
- Git repository is SSOT.

## Writer self-check (not independent QA)

- Static contract tests: `node --test frontend/src/shared/tokens/tokenContract.test.mjs`
  → **29 passed, 0 failed** (26 pre-existing + 3 new: no-`overflow:hidden`-on-`.avatar`,
  `.avatarInner` declares it instead, `avatarInner` renders before `statusDot` in JSX
  source order confirming sibling-not-parent structure).
- `npm run lint` (frontend): **PASS**, 0 errors/warnings.
- `npm run build` (`tsc -b && vite build`): **PASS**, 0 TypeScript errors, 315 modules
  transformed.
- Target E2E: `tests/e2e/specs-mongle/01-shell.spec.ts`, iphone + desktop projects,
  against a freshly rebuilt `mc_phase1` frontend image (containing this fix):
  **27 passed, 1 correctly-scoped desktop-only skip, 0 failed**.
- Manual visual regression check: screenshotted `/wagle` (4x device scale) after
  login — `RoomItem` and `ChatHeader` Avatar instances (none pass `status`) render
  as fully circular avatars, unchanged from pre-fix appearance.
- Pre-existing-environment-issue check: reproduced the `@rollup/rollup-darwin-arm64`
  build failure with this task's changes `git stash`ed out, confirming it predates
  and is unrelated to this fix; resolved for both states via a clean `npm ci`.
- NOT independently verified: a `status`-bearing Avatar's corrected (non-clipped)
  rendering was visually confirmed in the separate isolated A1 worktree (the only
  current real `status` consumer), not in this worktree, since no consumer here
  exercises that prop. Independent QA should re-verify the fix directly (e.g. a
  temporary harness render or the A1 worktree's own PlayerCard) rather than relying
  solely on this task's static assertions.
