# PHASE1-NARAN-PLATFORM-SHELL-001

- Task ID: `PHASE1-NARAN-PLATFORM-SHELL-001`
- author/agent: `Codex`
- created_at: `2026-07-26`
- git_ref: `9cce458f75df2a251176dc0628da1c152a98098e`
- environment: `local macOS workspace; isolated runtime only`
- secrets_redacted: `true`
- Lifecycle: `COMPLETED`
- Decision: `DESIGN_APPROVED`
- Verification: `PASS`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev`
- Start HEAD: `9cce458f75df2a251176dc0628da1c152a98098e`
- End HEAD: `1f3b839a3c6147e0bb1d03cd231daa1e396f7ba4`
- Final Commit: `1f3b839a3c6147e0bb1d03cd231daa1e396f7ba4`

## Scope

Implement the Naran platform Shell, Account/Family bootstrap state, namespaced
Family selection, permission-based UX navigation, responsive/safe-area layout,
and legacy MarkPoint route compatibility. Add representative Shell tests and
evidence. Existing backend authorization remains the final authority.

## Existing Dirty State

User-owned `CLAUDE.md` modification and root/docs deletions; start unstaged
SHA-256 `eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`.

## Forbidden Scope

No operating DB/NAS access, schema/migration, auth/JWT cutover, legacy
`/dashboard` removal, MarkPoint business/API changes, Doran messaging,
WebSocket, Push, multi-device Session, explicit grant/deny, or user dirty work.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-07/PHASE1-NARAN-PLATFORM-SHELL-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE1-NARAN-PLATFORM-SHELL-001.md`
- Independent QA: `complete — PASS (independent read-only Shell QA)`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `E2E-NARAN-SHELL-001 records the isolated runtime Shell journey and capture baseline.`
- CLOSEOUT GATE: `PASS`

## Implementation Evidence

- Frontend lint and production build: PASS using Volta Node `20.19.0` / npm `10.8.2`.
- Isolated `mc_phase1` Shell Playwright: 25/25 PASS across Desktop, iPhone 390, iPad, Android tablet portrait, and Android tablet landscape Chromium emulation.
- Existing Phase 0 Playwright: 9/9 PASS on the isolated `mc_phase0` runtime.
- Backend pytest: 6/6 PASS; Phase 1 RBAC API+DB and legacy authorization suites: PASS.
- Static Agent checks: warning 0 / exit 0.
- Capture manifest: `tests/e2e/naran-shell-capture-manifest.md`; ten synthetic PNGs are at `/tmp/phase1-naran-shell-captures`.

## Independent QA

Independent read-only QA initially observed a failed Shell run after a mutable
Phase 1 API suite had deliberately closed the synthetic Alpha Family. The
writer restored the explicit synthetic seed; QA then reran only the Shell suite
against that clean baseline and recorded `25/25 PASS`. The failure was fixture
state contamination, not a Family-switch implementation defect.
