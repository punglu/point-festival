# PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001 Implementation Evidence

- Task ID: `PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001`
- author/agent: `Codex`
- observed_at: `2026-07-26`
- git_ref: `83aad8198610fe3c3a442e9d51320f34a395142e`
- secrets_redacted: `true`
- Verification: `QA_PENDING`
- Self-check only: `true`
- Independent QA: `conditional — only if core code changes`
- Git repository is SSOT.

## Starting measurement

- Existing isolated runtime implementation: `e8f597a`, Node/npm pin: `5bfa862`, latest guide: `83aad81`.
- Existing external containers on ports 5432/8000/5173 are `outlook-hub` and out of scope.
- Current Phase 0 runtime is not running at task start.

## Planned execution evidence

Record exact commands, HEAD, exit codes, synthetic-data boundary, test counts, screen-capture paths, and unrun device/operating-DB gates after execution.

## Executed evidence

- Isolated Compose `mc_phase0`: PostgreSQL 15432, API 18000, frontend 13000; separate volume/network; existing `outlook-hub` containers untouched.
- Runtime health and OpenAPI: exit 0; 71 OpenAPI paths; frontend HTTP 200.
- Frontend Node/npm via Volta: Node 20.19.0, npm 10.8.2.
- `npm run lint`, `npm run build`, and `npm ci --dry-run`: exit 0.
- `npm run generate:api` against isolated OpenAPI: exit 0; generated type output stable.
- `backend python3 -m pytest -q`: exit 0; 6 passed.
- `tests/api/test_weekly_api.sh`: exit 0; 6/6 PASS.
- `tests/api/e2e_scenario_test_v2.py`: exit 0; 87/87 PASS against synthetic data.
- `tests/e2e npm test`: exit 0; 9 passed.
- Viewport evidence: 15 PNGs in `/tmp/phase0-screen-captures` for desktop, iPhone 390, iPad 1024, Android tablet portrait, and Android tablet landscape; each includes login, user dashboard, and admin dashboard.

## Unrun / Human Gate

- Physical iPhone, iPad, and Android-tablet interaction.
- Standalone PWA, Push permission/delivery, keyboard and system Back behavior.
- Operating DB backup/restore rehearsal, schema comparison, and initial Alembic stamp.

## Closeout review

- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- QA EVIDENCE: `UPDATED`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: measured isolated API/journey and viewport baseline evidence was added.
- CLOSEOUT GATE: `PASS`
