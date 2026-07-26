# PHASE1-NARAN-PLATFORM-SHELL-001 Implementation Evidence

- Task ID: `PHASE1-NARAN-PLATFORM-SHELL-001`
- author/agent: `Codex`
- observed_at: `2026-07-26`
- git_ref: `9cce458f75df2a251176dc0628da1c152a98098e`
- environment: `local macOS workspace; isolated runtime only`
- secrets_redacted: `true`
- Verification: `PASS`
- Self-check only: `true`
- Independent QA: `complete — PASS (independent read-only Shell QA)`
- Git repository is SSOT.

## Scope

Naran Shell, Family Context selection/reset, permission-view rules, legacy
MarkPoint route compatibility, responsive layout, and representative Shell
journeys. No final PASS is claimed by the implementation session.

## Self-check results

| Check | Result |
| --- | --- |
| Volta Node 20.19.0 / npm 10.8.2 `npm run lint` | PASS — 0 errors, 0 warnings |
| Volta Node 20.19.0 / npm 10.8.2 `npm run build` | PASS |
| `npx playwright test --config playwright.naran.config.ts` | PASS — 25/25 Chromium-emulated Shell checks |
| Existing `playwright.config.ts` suite | PASS — 9/9 |
| `python3 -m pytest -q` in `backend/` | PASS — 6/6 |
| `python3 tests/api/phase1_rbac_api_test.py` | PASS — API + DB authorization matrix |
| `python3 tests/api/legacy_auth_boundary_test.py` | PASS — legacy authorization regression |
| `python3 agent-system/tools/check_all.py` and `check_closeout.py` | PASS — warning 0, exit 0 |

The UI baseline is Chromium viewport emulation only. Physical-device Safari,
standalone PWA, keyboard, Android Back, and Push are not claimed.

## Independent QA verdict

`PASS` after clean synthetic reseeding. The independent reviewer reran the
Shell suite only and observed `25/25 PASS` in 13.4 seconds. An earlier run
started after the deliberately mutating RBAC API suite had closed the synthetic
Alpha Family, so its Family-switch failure was rejected as fixture-state
contamination rather than a product finding. No files were modified by QA.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE1-NARAN-PLATFORM-SHELL-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE1-NARAN-PLATFORM-SHELL-001.md`
- Independent QA: `complete`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `E2E-NARAN-SHELL-001 indexes executed Shell tests and the capture manifest.`
- CLOSEOUT GATE: `PASS`
