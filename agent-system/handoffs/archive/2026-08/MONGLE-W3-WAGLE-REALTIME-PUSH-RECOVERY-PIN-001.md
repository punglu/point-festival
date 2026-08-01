# MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001

- Task ID: `MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001`
- Kind: Wave 3 execution bundle over existing Backlog rows (no new Backlog task created)
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `2243aa83d3a0e527e83483651d10c2879026c704`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9; throwaway backend/frontend images; isolated Compose project `mc_phase1` for E2E
- evidence: `agent-system/qa/MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.md`
- secrets_redacted: `true`
- Lifecycle: `IMPLEMENTED_AWAITING_INDEPENDENT_QA`
- Decision: `DESIGN_APPROVED` (PM Wave 3 directive, 2026-08-01)
- Verification: `CONDITIONAL` (self-check only)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `2243aa83d3a0e527e83483651d10c2879026c704`
- End HEAD: `2243aa83d3a0e527e83483651d10c2879026c704` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Task-ID mapping

This execution ID is a **bundle**, not a new Backlog task. It implements
`MONGLE-W2-WAGLE-REALTIME-001` (Wave 3), `MONGLE-W3-WAGLE-RECONNECT-RESUME-001`,
`MONGLE-W3-WAGLE-MULTIFAMILY-SUBSCRIPTION-001`,
`MONGLE-W3-WAGLE-FAILURE-ISOLATION-001` and `MONGLE-W3-WAGLE-PIN-LOCK-001` in
full, and `MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001` /
`MONGLE-W3-WAGLE-PUSH-DEEPLINK-AUTHZ-001` partially. The seven `D6-P*`-gated
rows are untouched. No existing ID was renamed and no duplicate created.

**PM action item:** the Backlog marks `MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001`
as "must be decided before this task starts", while the directive said to build
the lifecycle and adapter with only the payload policy-blocked. The directive
was followed and the payload is identifiers-only, but the two records currently
disagree and PM should reconcile the row's status.

## Worktree and changed files

- New backend: `wagle/realtime.py`, `wagle/realtime_models.py`, `wagle/realtime_dispatcher.py`, `wagle/realtime_router.py`, `wagle/push_service.py`, `wagle/device_pin_service.py`, `workers/wagle_realtime.py`, `alembic/versions/0009_wagle_realtime_push_pin.py`, plus two test files.
- New frontend: the realtime client/hook/device API, `WaglePinLock`, `public/sw.js`, and `tests/e2e/specs-mongle/02-wagle-realtime.spec.ts`.
- Modified (minimal, shared): `app/main.py`, `app/config.py`, `all_models.py`, `service_outbox/service.py`, `workers/service_outbox.py`, `test_integration_wagle_markpoint.py`, `nginx.conf`, `eslint.config.js`, `httpClient.ts`, `WagleLanding.tsx`, `main.tsx`, `components/index.ts`, `generated/openapi.d.ts`.
- **No Markpoint Mission/Ledger product code was modified.**

## Commands and outcomes

```
alembic heads                     -> 0009_wagle_realtime_push_pin (single)
fresh upgrade / downgrade / re-up -> PASS, residual 0
backend pytest --collect-only     -> 228
backend pytest -q                 -> 228 passed, 0 failed   (was 173)
frontend tsc --noEmit             -> EXIT=0
frontend eslint                   -> clean
clean isolated production build   -> PASS (doran 0 / naran 1 / wagle 27)
OpenAPI regenerated               -> 116 paths, doran 0, naran 0
playwright (mc_phase1)            -> 125 collected, 121 passed, 0 failed,
                                     4 skipped, 0 retries
git diff --check                  -> clean
```

- Tests Not Run: browser Web Push end-to-end (no VAPID key / push service — the delivery path is covered by adapter tests, and this is **not** reported as PASS); the message-level realtime UI journey (the Wagle screen still renders preview fixtures — Wave 6); multi-worker cross-process fan-out latency (needs the broker decision below).

## Defects found and corrected

Two were **latent defects in already-graduated Wave 2/4 code**, both HIGH:

1. `claim_batch` ignored `owner_service`, so the SERVICE_ACTION Worker claimed Wagle delivery events, provisioned a bogus `wagle` ServicePrincipal, failed the action allowlist and drove the row to `DEAD`. Fixed by filtering at the claim.
2. `record_failure` raised `MissingGreenlet` because every caller reaches it right after `db.rollback()` expires the instance — the retry handler itself failed, leaving rows `PROCESSING` until lease expiry. Fixed in the shared helper, so both Workers benefit.

Two were **introduced by this task and caught by the E2E**, not by reading:

3. The PIN status probe's 401 tripped the global logout interceptor, so entering Wagle logged a legacy-session user out. `/api/me/wagle/` is now exempt: an optional feature must never end a session.
4. The realtime client treated a terminal 4401 refusal as a network blip and reconnected forever.

Two were **pre-existing deployment defects**:

5. `nginx.conf` did not proxy the WebSocket upgrade (which is what surfaced #4), and its 32 KB ingress rule still matched the retired `doran` path, so the proxy-side body cap had silently stopped applying. `/sw.js` also now has no-cache.

Plus one fragile pinned assertion (`count(*) == 7` `wagle%` tables) replaced with an explicit named set — stronger, not weaker.

Remaining known product defects: **0**.

## Known gaps / residual blocks

- `D6-P1`–`D6-P8` all remain undecided; seven Backlog rows are deliberately not started. Nothing was approximated — no Push body, no mute default, no bundling rule, no presence, no edit/delete, no retention, no offline queue, no user-facing `DELIVERED`.
- **Multi-process fan-out is a decision, not an oversight.** `docker-compose.prod.yml` runs `uvicorn --workers 2`; `InProcessFanout` reaches only its own process. No message is lost — every connection runs a durable catch-up on its own cursor — but cross-worker delivery arrives on the catch-up interval (default 5s) rather than instantly. Closing that needs PostgreSQL `LISTEN/NOTIFY` or a broker; **no infrastructure was introduced** because no approved document selects one. `RealtimeFanoutPort` is the seam.
- The Wagle screen still renders preview fixtures, so realtime subscribes to zero rooms in the UI. Wiring real rooms is `MONGLE-W5-TARGET-UI-001` (Wave 6).
- Independent QA has not run.

## Risks and Human Gate

- The `WAGLE_REALTIME_REVALIDATE_SECONDS` default (15s) is the **upper bound on how long a revoked membership can still receive events**. It is a security-relevant number; treat a change to it as a security change.
- `build_payload()` is the only D6-P1 seam. Do not add a body, sender name or room title to it, to the WebSocket envelope, or to `sw.js` — the policy is enforced on both ends deliberately.
- The device PIN must never be wired to Session revocation, Push suppression, or another service's access. Tests assert all three; they are contract, not incidental.
- Do not reuse `auth.models.pin_hash` (the legacy player login credential) for the device lock.
- No commit or push was made. Branch and HEAD unchanged.

## Next agent first action

Independent QA of this task: stand up the isolated stack, re-derive the
migration checks from a fresh database, re-run the 228 backend tests and the
Playwright suite against a fingerprint-verified current-source image, and read
the two shared-file fixes (`claim_batch` filtering, `record_failure` refresh)
critically — they change already-graduated Wave 2 behaviour and were authored by
the same session that found them.

## Forbidden Scope

Implementing any `D6-P*`-gated behaviour without its decision; introducing a
broker or other infrastructure without documentary basis; making the WebSocket
or a Push payload a source of truth; publishing before the DB commit; global
ordering; a user-facing `DELIVERED` state; ending an Account Session on one
Family's revocation or on a PIN failure; legacy PIN reuse or backfill; a
`MarkpointParticipant` aggregate; Markpoint Mission/Ledger product code; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: four new source-backed rows for the dispatcher, the WebSocket gateway, Push/PIN, and the Wave 3 browser slice.
- CLOSEOUT GATE: `PASS`
