# PHASE0-DEV-RUNTIME-RECOVERY-001 Implementation Evidence

- Task ID: `PHASE0-DEV-RUNTIME-RECOVERY-001`
- author/agent: `Codex`
- observed_at: `2026-07-26`
- git_ref: `bcef1a4c00d41bf37719596af0c8876a236ff129`
- environment: `macOS local development environment`
- secrets_redacted: `true`
- Verification: `QA_PENDING`
- Closeout Contract: `v1`
- Independent from implementer: `false`
- Independent QA: `not_applicable — tooling and isolated runtime self-check`

## Scope reviewed

Frontend Node/npm and ESLint contract, lint/build results, isolated Compose runtime, and existing Playwright runtime configuration.

## Commands, exit codes, and results

- Node/npm selected through Volta: Node `20.19.0`, npm `10.8.2`.
- Frontend dependency installation: exit 0; ESLint Flat Config dependencies added to the lockfile.
- `npm run lint`: exit 0 after one unused-expression repair and two dependency-safe Hook repairs.
- `npm run build`: exit 0; Vite 6.4.1 built production assets.
- `npm ci --dry-run`: exit 0.
- Phase 0 Compose config and startup: exit 0 with project `mc_phase0`, host ports 15432/18000/13000, a dedicated volume/network, and synthetic seed data.
- Backend `/api/health` and `/openapi.json`: exit 0; OpenAPI reported 71 paths.
- Frontend `/`: HTTP 200.
- `cd backend && python3 -m pytest -q`: 6 passed, exit 0.
- Playwright Chromium cache installation: exit 0. First execution established the browser prerequisite; final `npm test`: 9 passed, exit 0.

## Findings

- The prior lint failure was a missing ESLint/configuration contract, not a partial node_modules installation.
- The original E2E configuration placed `baseURL` outside Playwright's `use` block, so relative `page.goto('/')` was invalid. The current configuration provides the isolated runtime URL under `use.baseURL`.
- Existing E2E selectors expected text inputs for PIN entry and a historical `data-testid`; they were updated to match the current keypad and CSS module structure without weakening assertions.
- Playwright Chromium was absent locally and is now available in the user cache, not the repository.

## Closeout review

- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- QA EVIDENCE: `UPDATED`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: measured lint/build/backend/E2E evidence is now reflected in existing Coverage Map entries.
- CLOSEOUT GATE: `PASS`
