# MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001

- Task ID: `MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001`
- Parent: `MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `2243aa83d3a0e527e83483651d10c2879026c704` (unchanged start → end)
- environment: repository root; disposable volume-less PostgreSQL 16.9; throwaway backend image; a real `uvicorn --workers 2` container for the runtime check; isolated `mc_phase1` for E2E
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
MULTIWORKER_IMMEDIATE_FANOUT_COMPLETE
LISTEN_NOTIFY_ADAPTER_COMPLETE
LISTENER_LIFECYCLE_AND_RECOVERY_COMPLETE
CURSOR_POLLING_FALLBACK_PRESERVED
WAVE_3_REGRESSION_PASS
READY_FOR_WAVE_3_INDEPENDENT_QA
```

The one infrastructure slice PM held Wave 3 open for is closed. No new
infrastructure was introduced — PostgreSQL `LISTEN/NOTIFY` only, as approved.

## 2. Scope

Exactly what PM specified, and nothing beyond it: the `LISTEN/NOTIFY` adapter,
per-worker listener lifecycle, the dispatcher wake-up publish, the connection
from that into the process-local WebSocket registry, listener reconnection, the
preserved cursor fallback, a two-worker integration test, and the Wave 3
regression.

## 3. Design

```text
1. Dispatcher processes an Outbox event (unchanged)
2. publish() delivers to THIS worker's connections, then emits pg_notify
3. Every other ASGI worker LISTENs on `wagle_realtime`
4. Each listener hands the envelope to its own local registry
5. Missed / duplicated / reordered notifications are recovered by the
   per-connection durable cursor catch-up, which is unchanged and still runs
```

**NOTIFY is a wake-up signal and nothing else.** Every one of PM's prohibitions
is structural rather than a rule someone has to remember:

| Prohibition | How it is prevented |
|---|---|
| NOTIFY payload as message SSOT | The payload has no body field to read; the client renders from the durable history. |
| Message body in the payload | `_notify()` builds a fixed identifier-only dict; a test pins its exact key set. Also physically impossible at scale — PostgreSQL caps NOTIFY at 8000 bytes, so a content-carrying design would fail on the longest messages. |
| NOTIFY success as user delivery | Nothing reads the return of `pg_notify`; no delivery state is derived from it. |
| Removing the polling fallback | The catch-up loop is untouched, and a test asserts recovery **with no NOTIFY emitted at all**. |
| Global ordering | Order is still per `(FamilyGroup, Room)` by room sequence; NOTIFY arrival order is never relied on. |
| exactly-once | Duplicate notifications are expected and tested; dedup stays on `(room_id, room_sequence)` / `message_id`. |

**`origin_id`** — each worker stamps its notifications with its own process
identity and its listener drops what it recognises, so the publishing worker
does not deliver its own event twice. Client dedup would have masked it, but
creating a duplicate the server knows about and leaving the client to clean it
up is the wrong default.

**Degradation is deliberate and one-directional.** `publish()` delivers locally
**first and unconditionally**, then notifies inside a `try`. If the database is
briefly unreachable, this worker's clients are still served and the others fall
back to their catch-up. A notification failure can never become a delivery
failure. Likewise, a worker that cannot attach a listener at startup logs and
continues — it loses instant cross-worker delivery, not correctness.

## 4. Listener Lifecycle

A dedicated raw asyncpg connection (a pooled SQLAlchemy connection must not be
held open for the life of a process), attached in the FastAPI lifespan and
released on shutdown. The loop reconnects with capped exponential backoff and
polls `is_closed()` every 5s, because a listener that dies quietly is the worst
outcome here: the worker would look healthy while silently serving only its own
traffic. **Nothing is replayed on reconnect** — events missed while down are the
durable cursor's job, which keeps one recovery mechanism instead of two that can
disagree.

## 5. Test Results

```text
tests/test_wagle_multiworker_fanout.py   -> 10 passed
backend collect / full suite             -> 238 collected, 238 passed, 0 failed
frontend tsc --noEmit                    -> EXIT=0
frontend eslint                          -> clean
playwright (isolated mc_phase1)          -> 121 passed, 0 failed, 4 skipped, 0 retries
```

Against PM's required completion conditions:

| Required | Result |
|---|---|
| Two workers, each with a WebSocket connection | Two independent registry+listener pairs, each with its own asyncpg connection |
| Worker A's event → delivered to Worker B's connection | **PASS** — worker A has no local subscriber, so everything B received crossed PostgreSQL |
| NOTIFY duplicate → client dedup safe | **PASS** — both copies carry the same `message_id` and `room_sequence` |
| NOTIFY loss → durable cursor recovery | **PASS** — asserted with no NOTIFY emitted at all |
| Listener restart → later events received | **PASS** — connection killed the way a blip would, reconnects, resumes, replays nothing |
| Session/Membership revoke contract intact | **PASS** — unchanged; covered by the 15 gateway tests inside the 238 |
| DB/Outbox still SSOT | **PASS** — payload key set pinned; no body field exists |
| Docker production `workers=2` verified | **PASS** — see §6 |

Also asserted: subscribers in another Family or another room are not woken (the
same room id in a different family must not match), and a publish failure never
suppresses local delivery.

## 6. Runtime `--workers 2` Verification

A real container, `uvicorn app.main:app --workers 2`, against the disposable
database:

```text
health                                -> {"status":"ok"}
processes running app.main            -> 2
backends holding LISTEN "wagle_realtime" -> 2   (pid 153, pid 154)
WebSocket handshake on /api/me/wagle/ws  -> HTTP 101 (upgrade accepted)
```

**Stated precisely so it is not over-read.** This confirms that under real
`--workers 2` each worker independently attaches its own listener and the
gateway is served — which is the part multi-process adds. The delivery
behaviour itself (A publishes → B's socket receives) is proven by the ten
functional tests, which exercise the identical code path with two independent
listener/registry pairs over a real PostgreSQL NOTIFY. What a single test
process cannot reproduce is OS-level process isolation; that is why the two
pieces of evidence are reported separately rather than merged into one claim.

## 7. Defects Found

None in this task. No product defect was introduced or discovered; the Wave 3
suite, the Playwright suite and the frontend checks all pass unchanged.

## 8. Changed-file Manifest

**New (2)** — `backend/app/domains/wagle/realtime_notify.py`,
`backend/tests/test_wagle_multiworker_fanout.py`
**Modified (2)** — `backend/app/main.py` (listener lifecycle; the pump now
publishes through the notify fan-out),
`engineering/phase2/MONGLE_IMPLEMENTATION_BACKLOG.md` (PM's Push-row correction)
**Records** — this report, its handoff, `active.md`, `relay/current.md`,
`COVERAGE_MAP.md`

No frontend product code changed: the client already deduplicates and already
runs its cursor recovery, which is exactly why NOTIFY could be added underneath
it without touching it.

## 9. Backlog Correction Applied

`MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001` moved from
`DEFERRED_TO_RELEVANT_TASK_START_GATE` to
`IMPLEMENTED_AWAITING_INDEPENDENT_QA`, with PM's split recorded in the row
itself: subscription lifecycle and delivery infrastructure proceed
independently; user-visible payload content and preview policy stay blocked
until `D6-P1`. **No duplicate Push task was created** — the implemented and
deferred halves live in the one row, as instructed.

## 10. Five-Gate Review

- **환각** — every number is from a command in this session; the `--workers 2` evidence is a real container and a real `pg_stat_activity` query, and §6 states exactly what it does and does not prove.
- **누락** — adapter, listener lifecycle, dispatcher publish, registry fan-out, reconnect recovery, preserved fallback, two-worker test, Wave 3 regression: all present.
- **오작업** — no Redis/Kafka/NATS; NOTIFY carries no content and is never SSOT; polling fallback intact; no global ordering; no exactly-once; no user-facing delivery state; no Markpoint code touched.
- **축혼동** — wake-up signal vs durable event; local delivery vs cross-worker delivery; listener reconnect vs message recovery; NOTIFY success vs user receipt.
- **신선도·오탈자** — HEAD `2243aa8`, Alembic head `0009` unchanged (this task adds no migration), `git diff --check` clean.

## 11. Lifecycle

`IMPLEMENTED_AWAITING_INDEPENDENT_QA`. Nothing graduated. Wave 3 is now
complete on the infrastructure axis and ready for
`MONGLE-W3-WAGLE-INDEPENDENT-QA-001`.

## 12. Final Verdict

```text
MULTIWORKER_IMMEDIATE_FANOUT_COMPLETE
WAVE_3_IMPLEMENTATION_COMPLETE
READY_FOR_WAVE_3_INDEPENDENT_QA
```

Residual, unchanged from the parent task: `D6-P1`–`D6-P8` undecided (7 Backlog
rows not started), browser Web Push E2E not runnable without VAPID keys, and the
message-level realtime UI journey blocked on Wave 6
`MONGLE-W5-TARGET-UI-001`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: one new source-backed row for cross-worker realtime fan-out.
- CLOSEOUT GATE: `PASS`
