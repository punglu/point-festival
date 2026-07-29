# E2E Coverage Map V2

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Section 22). Full data: `e2e_coverage_map_v2.csv` (23 rows: 14 from `specs-mongle/01-shell.spec.ts` + 9 from the legacy `specs/*.spec.ts`). Analysis is **static only** — no test suite was executed this session, per the brief's explicit prohibition on running the full E2E suite.

## Two independent Playwright configs found

1. `tests/e2e/playwright.config.ts` — `testDir: './specs'` (the 4 legacy files: `01-login`, `02-mission`,
   `03-admin`, `04-flow`, 9 tests total), single implicit project, `webServer.command` points at
   `docker compose ... -f ../../docker-compose.phase0.yml up`. **`docker-compose.phase0.yml` does not
   exist in this repository** (confirmed: `ls docker-compose.phase0.yml` → "No such file or directory").
   These 9 tests are therefore classified `CURRENT_TEMPORARY` — not proven broken, but **not currently
   runnable** with this config as-is. Not claimed as passing.
2. `tests/e2e/playwright.mongle.config.ts` — `testDir: './specs-mongle'` (currently just `01-shell.spec.ts`,
   14 tests), 5 explicit projects (`desktop`, `iphone`, `ipad`, `android-tablet-portrait`,
   `android-tablet-landscape`), `webServer.command: ./scripts/start-mongle-phase1.sh` (a real, present
   script — not verified to succeed this session, since running it would violate the "no Docker/E2E
   execution" prohibition, but the script file and its referenced `docker-compose.phase1.yml` both exist
   on disk, unlike the phase0 file above).

## Exact reconciliation of the "4 intentional skipped" baseline figure

`grep -n "test.skip\|\.skip("` across both spec directories found **exactly one** conditional skip, in
`specs-mongle/01-shell.spec.ts`'s "internal Dock/nav clicks produce canonical URLs" test:
`test.skip(testInfo.project.name !== 'desktop', ...)`. With 5 projects configured and this skip firing on
the 4 non-desktop ones, this single line produces exactly 4 skipped test-instances across a full run —
matching the reported baseline ("4 intentional skipped") exactly, and explaining *why* precisely: desktop-
only assertion about a shared nav landmark that behaves identically on mobile via the Dock. With 14 tests
× 5 projects = 70 instances − 4 skipped = 66 executed, also matching the reported "66 passed" figure. This
reconciliation was derived from code, not assumed from the brief's stated baseline.

## Coverage themes

- **Route/storage migration** (canonical vs. `/naran/*` legacy, `mongle.activeFamily.*` vs.
  `naran.activeFamily.*`) is very thoroughly covered — 9 of the 14 `specs-mongle` tests exist specifically
  for this, including console-error assertions and explicit Back-button loop checks.
- **Approved-screen visual reconstruction coverage is effectively zero.** No current test asserts on
  layout, color, spacing, or any visual property corresponding to the approved design's measurements —
  every assertion found is text/heading-presence, URL-shape, or storage-key-presence. This means **any**
  future visual recomposition work (Wave 6.1+) starts with no visual-regression safety net beyond the
  existing `Visual Delta 0` baseline claim (which is itself about the *current* app's own consistency
  across runs, not about matching the approved design).
- Legacy `specs/*.spec.ts` tests were not read past their titles this session (time budget); their
  assertion detail is `NOT_VERIFIED`, and their current runnability is `CURRENT_TEMPORARY`/blocked pending
  the missing `docker-compose.phase0.yml`.

No test was reported as passing or failing in this document — only what each test asserts and whether its
own config can currently execute at all, per the brief's "미실행 테스트를 PASS라고 쓰지 않는다" instruction.
