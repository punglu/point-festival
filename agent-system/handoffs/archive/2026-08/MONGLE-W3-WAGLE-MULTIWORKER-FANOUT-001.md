# MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001

- Task ID: `MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001`
- Parent: `MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `2243aa83d3a0e527e83483651d10c2879026c704`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9; a real `uvicorn --workers 2` container; isolated `mc_phase1` for E2E
- evidence: `agent-system/qa/MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.md`
- secrets_redacted: `true`
- Lifecycle: `IMPLEMENTED_AWAITING_INDEPENDENT_QA`
- Decision: `DESIGN_APPROVED` (PM approved PostgreSQL LISTEN/NOTIFY, 2026-08-01)
- Verification: `PASS` (self-check only)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `2243aa83d3a0e527e83483651d10c2879026c704`
- End HEAD: `2243aa83d3a0e527e83483651d10c2879026c704` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Origin

PM held Wave 3 open for one infrastructure slice: under
`docker-compose.prod.yml`'s `uvicorn --workers 2`, a client attached to one
worker did not get immediate fan-out for an event handled by another — only the
5s durable catch-up. PostgreSQL `LISTEN/NOTIFY` was approved as the mechanism;
Redis, Kafka and NATS were not.

## Worktree and changed files

- New: `backend/app/domains/wagle/realtime_notify.py`, `backend/tests/test_wagle_multiworker_fanout.py`.
- Modified: `backend/app/main.py` (listener lifecycle; the pump publishes through the notify fan-out), `engineering/phase2/MONGLE_IMPLEMENTATION_BACKLOG.md` (PM's Push-row correction).
- **No frontend product code changed** — the client already deduplicates and already runs cursor recovery, which is why NOTIFY could be added underneath it untouched.
- No migration: `0009` remains head.

## Commands and outcomes

```
tests/test_wagle_multiworker_fanout.py -> 10 passed
backend pytest --collect-only          -> 238
backend pytest -q                      -> 238 passed, 0 failed
frontend tsc --noEmit / eslint         -> EXIT=0 / clean
playwright (mc_phase1)                 -> 121 passed, 0 failed, 4 skipped, 0 retries
runtime uvicorn --workers 2            -> 2 app.main processes,
                                          2 backends holding LISTEN "wagle_realtime",
                                          WS handshake HTTP 101
git diff --check                       -> clean
```

## Completed / remaining

- All eight of PM's required completion conditions are met; §5 of the report maps each one to its evidence.
- **Evidence boundary, stated rather than blurred:** the runtime `--workers 2` check proves each worker independently attaches its own listener and serves the gateway. The delivery behaviour itself (A publishes → B's socket receives) is proven by the ten functional tests over a real PostgreSQL NOTIFY with two independent listener/registry pairs. A single test process cannot reproduce OS-level process isolation, so the two are reported separately rather than merged.
- Known Gaps (unchanged from the parent task, none introduced here): `D6-P1`–`D6-P8` undecided (7 Backlog rows not started); browser Web Push E2E not runnable without VAPID keys; message-level realtime UI journey blocked on Wave 6 `MONGLE-W5-TARGET-UI-001`.
- Defects found or introduced in this task: **0**.

## Risks and Human Gate

- **Do not remove the cursor catch-up now that NOTIFY exists.** It is what makes NOTIFY optional; a test asserts recovery with no NOTIFY emitted at all. Deleting it would turn a lost notification into a lost message.
- **Do not put message content in the NOTIFY payload.** `D6-P1` has decided no disclosure level, and PostgreSQL caps the payload at 8000 bytes — a content-carrying design would fail on exactly the longest messages. A test pins the exact key set.
- `origin_id` is what stops a publishing worker from delivering its own event twice. Removing it does not break correctness (the client dedupes) but does mean the server knowingly emits duplicates.
- `publish()` delivers locally **before** notifying, inside a `try`. Reordering it would let a database blip become a delivery failure for clients already attached to that worker.
- No commit or push was made. Branch and HEAD unchanged.

## Next agent first action

`MONGLE-W3-WAGLE-INDEPENDENT-QA-001`. Beyond the Wave 3 matrix, PM's mandatory
re-derivations are: the SERVICE_ACTION Worker must not claim Wagle Outbox rows
and vice versa; `record_failure` must complete after a rollback with
`attempt_count` incrementing exactly once; no `PROCESSING` row may be left until
lease expiry; and the retry → `DEAD`/re-processing transitions must match
contract. Those two fixes change already-graduated Wave 2 behaviour and were
authored by the session that found them.

## Forbidden Scope

Introducing Redis/Kafka/NATS or any other broker; making the NOTIFY payload a
source of truth or adding message content to it; treating NOTIFY success as user
delivery; removing the polling fallback; claiming global ordering or
exactly-once; implementing any `D6-P*`-gated behaviour; Markpoint Mission/Ledger
product code; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: one new source-backed row for cross-worker realtime fan-out.
- CLOSEOUT GATE: `PASS`
