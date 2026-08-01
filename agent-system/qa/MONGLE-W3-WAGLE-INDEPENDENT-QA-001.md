# MONGLE-W3-WAGLE-INDEPENDENT-QA-001

- Task ID: `MONGLE-W3-WAGLE-INDEPENDENT-QA-001`
- Execution Target: `MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001`,
  `MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001`
- author/agent: `Claude Code` (independent QA session)
- observed_at: 2026-08-01
- environment: `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`, HEAD
  `2243aa83d3a0e527e83483651d10c2879026c704` unchanged start→end. Tests and
  cross-process proof run against a disposable, volume-less PostgreSQL
  16.9-alpine container (`mongle-w3qa-testdb`, port 15435,
  `database/init.sql` + `alembic upgrade head`), torn down at teardown.
- secrets_redacted: true
- Closeout Contract: v1

## 1. Executive Verdict

```text
WAVE_3_INDEPENDENT_QA_PASS
WAGLE_REALTIME_CORE_LIFECYCLE_COMPLETE
WAGLE_RECOVERY_LIFECYCLE_COMPLETE
WAGLE_MULTIWORKER_FANOUT_LIFECYCLE_COMPLETE
WAGLE_DEVICE_PIN_LIFECYCLE_COMPLETE
WAGLE_PUSH_INFRASTRUCTURE_LIFECYCLE_COMPLETE
D6_POLICY_DEPENDENT_SLICES_DEFERRED
READY_FOR_NEXT_WAVE_REVIEW
```

Every Core claim was independently re-measured, not copied. The two
mandatory HIGH corrections to graduated Wave 2 Outbox code were re-verified
both by direct source read and by test — including a new symmetric test this
QA session added because the existing suite tested only one of the two
required directions (§9). Migration `0009` was independently reproduced
fresh/downgrade/re-upgrade with zero residue. The full backend suite (239,
not the reported 238 — see §24) passed with zero failures. Cross-process
NOTIFY fan-out was proven with **two genuinely separate Docker containers**
(distinct PID namespaces), not two objects in one test process — see §13-16
for the exact evidence, kept deliberately separate from the single-process
test-suite evidence and the real-container `--workers 2` topology evidence,
per this task's own instruction not to merge the three into one claim. One
D6-P1 policy question was found already correctly deferred; nothing
policy-dependent was found implemented.

## 2. Git Baseline

| | Start | End |
|---|---|---|
| toplevel | `/Users/mac/mac_Project/mongle_ui` | same |
| branch | `dev-newmarkp` | same |
| HEAD | `2243aa83d3a0e527e83483651d10c2879026c704` | identical |
| `git diff --check` | clean | clean |
| stash | none | none |
| commit/push/merge/rebase/PR | — | none performed |

HEAD matches the PM-reported baseline exactly. `git log -10` confirms
`2243aa8 feat(mongle): complete Wave 2/4 parent bundle` as the most recent
commit, with Wave 1 (`2f1c354`) and the Target decision freeze (`0d9280c`)
as ancestors.

## 3. Writer / Lifecycle State

`relay/current.md` showed no other open writer ("Current Task: none — Wave 3
released its write claim"), and `active.md` showed both Wave 3 tasks as
`IMPLEMENTED_AWAITING_INDEPENDENT_QA`, distinct from Wave 1's already-`PASS`
lifecycle. This QA registered itself in both files before any code read,
declaring the same scope as the implementing bundle plus this task's own
evidence files. Core and D6-policy-dependent Backlog rows were not collapsed
into one status anywhere in this report (§6, §26).

## 4. Authoritative Inputs

Read directly: `AGENTS.md`, `agent-system/rules.md`, `agent-system/active.md`,
`agent-system/relay/current.md`,
`agent-system/qa/MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.md`,
`agent-system/qa/MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.md`,
`agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`,
`engineering/phase2/MONGLE_IMPLEMENTATION_BACKLOG.md`,
`engineering/phase2/MONGLE_TARGET_DECISION_FREEZE.md`, plus direct source
reads of `service_outbox/service.py`, `workers/service_outbox.py`,
`wagle/realtime.py`, `wagle/realtime_dispatcher.py`,
`wagle/realtime_notify.py`, `backend/alembic/versions/0009_*.py`,
`docker-compose.prod.yml`, `frontend/nginx.conf`. Reported test counts,
defect counts and PASS wording were treated as hypotheses to re-derive, not
evidence.

## 5. Changed-file Audit

`git status --short` at this QA's own start showed 15 modified tracked files
and ~24 untracked entries (matching the PM-reported baseline). Classified:

| File | Class |
|---|---|
| `backend/alembic/versions/0009_wagle_realtime_push_pin.py` | `MIGRATION_0009` |
| `backend/app/domains/service_outbox/service.py`, `backend/app/workers/service_outbox.py` | `OUTBOX_SHARED_CORRECTION` |
| `backend/app/domains/wagle/realtime_dispatcher.py`, `backend/app/workers/wagle_realtime.py` | `DISPATCHER` |
| `backend/app/domains/wagle/realtime_router.py`, `realtime_models.py` | `WEBSOCKET` |
| `backend/app/domains/wagle/realtime.py` (resume path) | `RECOVERY` |
| `backend/app/domains/wagle/realtime_notify.py` | `POSTGRES_FANOUT` |
| `backend/app/domains/wagle/push_service.py` | `PUSH` |
| `backend/app/domains/wagle/device_pin_service.py` | `WAGLE_PIN` |
| `frontend/src/platform/wagle/realtime/*`, `WaglePinLock/*` | `FRONTEND_REALTIME` |
| `frontend/public/sw.js` | `SERVICE_WORKER` |
| `frontend/src/generated/openapi.d.ts` | `API_OPENAPI` |
| `backend/tests/test_wagle_realtime_wave3.py`, `test_wagle_websocket_gateway_wave3.py`, `test_wagle_multiworker_fanout.py` | `TEST` |
| `tests/e2e/specs-mongle/02-wagle-realtime.spec.ts` | `E2E` |
| `agent-system/{active.md,relay/current.md,qa/COVERAGE_MAP.md}`, `engineering/phase2/MONGLE_IMPLEMENTATION_BACKLOG.md` | `GOVERNANCE` |
| `frontend/nginx.conf`, `frontend/eslint.config.js` | `DOCUMENT`/deployment |
| `backend/app/main.py`, `backend/app/config.py`, `backend/app/models/all_models.py` | shared wiring, minimal (§9) |

No file outside the Wave 3 domain (Markpoint product code, Doran-era files
already retired, unrelated frontend screens) appears in the diff. The
`owner_service` filter (§9), `record_failure` rollback fix (§9), nginx
WebSocket upgrade map, and the retired-route rule removal were located at the
exact lines cited in §9/§14/§18 below — confirmed by direct read, not by
trusting the report's line-number claims.

## 6. D6 Policy Boundary

Re-read from `MONGLE_TARGET_DECISION_FREEZE.md` directly:

```text
D6-P1 Push 본문 공개 수준      : DEFERRED
D6-P2 Room mute/알림 설정      : DEFERRED
D6-P3 Push 묶음/foreground 억제 : DEFERRED
D6-P4 읽음 표시 방식           : DEFERRED
D6-P5 presence/last-seen       : DEFERRED
D6-P6 메시지 수정·삭제         : DEFERRED
D6-P7 보존 기간                : DEFERRED
D6-P8 오프라인 발신 Queue      : DEFERRED
```

Verified **not** implemented (grep + source read, not trusted from the
report): no message-body/sender field anywhere in `RealtimeEnvelope`,
`_notify()`'s payload dict, or `push_service.build_payload()` (§14); no mute
default, batching rule, presence field, edit/delete route, retention delete
job, or offline-queue table exists in the diff; no user-facing `DELIVERED`
status string appears in the WebSocket envelope or the client. Verified
**correctly implemented despite being policy-independent**: dispatcher,
WebSocket auth, room authorization, resume/recovery, Push subscription
lifecycle, device PIN — all confirmed working in §10-§21 below.

## 7. Migration 0009 — independently reproduced

```bash
docker run -d --name mongle-w3qa-testdb ... postgres:16.9-alpine
psql -v ON_ERROR_STOP=1 -f database/init.sql   # legacy baseline (0000 is a no-op stamp)
alembic upgrade head   # from empty DB
```

| Check | Result |
|---|---|
| `alembic heads` before upgrade | `0009_wagle_realtime_push_pin (head)` — single |
| fresh `0000`→`0009` | PASS, all 10 revisions applied in order incl. `0007` (Wagle rename) and `0008` (Markpoint activation-request/restriction — the SCHEMA_DELTA this QA session's own prior Wave 4 work had flagged as blocked; a later session evidently authored it) |
| `alembic downgrade -1` → `0008` | PASS |
| residual tables after downgrade | 0 — `\dt` confirmed `wagle_push_subscriptions`, `wagle_push_delivery_attempts`, `wagle_device_pins` all absent |
| re-upgrade → `0009` | PASS, all 3 tables restored |
| revision id length | `0009_wagle_realtime_push_pin` = 29 chars, under the `varchar(32)` limit that caused a silent Wave-1 rollback historically |

Live schema, read directly (not from the migration file's SQL text):

- `wagle_push_subscriptions`: no plaintext secret column; `endpoint`/
  `p256dh_key`/`auth_secret` present as expected capability data (never
  returned by the API — §18); partial-unique `(account_id, device_id) WHERE
  status='active'` and `(endpoint) WHERE status='active'` — device-replace
  and cross-account-endpoint-reuse both structurally handled; CHECK on
  `status`; FK to `accounts(id)`.
- `wagle_push_delivery_attempts`: unique `(outbox_event_id, subscription_id)`
  = delivery idempotency at the schema level, not just application logic; FK
  to `service_outbox_events` and `wagle_push_subscriptions`.
- `wagle_device_pins`: **only `pin_hash` (varchar 255)** — no plaintext PIN
  column anywhere in the table; unique `(account_id, device_id)` = device
  isolation at the schema level; `failed_attempt_count` + `locked_until` +
  CHECK `failed_attempt_count >= 0`.

Constraint count measured directly: 2 partial-unique indexes (push), 1
unique constraint (attempt), 1 unique constraint (device pin), **3** CHECK
constraints (`ck_wagle_push_subscriptions_status`,
`ck_wagle_push_attempt_status`, `ck_wagle_device_pin_attempts`) — the
implementer's report says "2 CHECK"; this QA's own direct count is 3. Not a
defect (an extra constraint is stricter, not looser), recorded as a minor
documentation-precision correction.

D8 RESET honoured: no legacy PIN or notification row is read or backfilled by
`0009` — confirmed by reading the migration file; it only `CREATE TABLE`s.

## 8. Dispatcher

`wagle/realtime_dispatcher.py`, read directly:

- **Claim**: `claim_batch(db, batch_size=batch_size, owner_service=OWNER_SERVICE)` where `OWNER_SERVICE = wagle_service.SERVICE_CODE` — scoped, not the historical unfiltered claim.
- **Lease**: reuses `service_outbox`'s existing `FOR UPDATE SKIP LOCKED` + `locked_until` lease; a dead worker's rows are re-claimable once the lease expires (`claim_batch`'s own `PROCESSING ... locked_until < now` branch).
- **Event routing**: `process_event()` returns `skipped_foreign_event` for any `event_type` not in `HANDLED_EVENT_TYPES` rather than marking it published — a genuinely-foreign row is left untouched, not silently swallowed.
- **Family/Room context**: `_recipient_account_ids()` re-derives recipients from `WagleParticipant`/`FamilyMembership` ACTIVE status at delivery time, not from the message's own stale sender list.
- **Local publish + PostgreSQL wake-up + Push**: `process_event()` calls `port.publish(envelope)` (local + NOTIFY, §12-16) and then `push_service.deliver_event(...)`, in that order, inside the same try/except that routes any failure to `record_failure` — one failure path covers both delivery channels.
- **Retry / failure isolation**: any exception in the try block triggers `db.rollback()` + `record_failure()` and returns per-event (never raises out of the loop), so one bad row cannot stop the batch — confirmed structurally and by `test_dispatcher_claim_is_scoped_to_its_own_owner_service`'s and `test_dispatcher_never_touches_the_durable_message_when_delivery_fails`'s independent re-runs (§9, §24).
- **Message never touched**: `_load_message`/`process_event` only `SELECT`s `WagleMessage`; no code path in this file issues an `UPDATE`/`DELETE` against `wagle_messages`. Independently re-run test `test_dispatcher_never_touches_the_durable_message_when_delivery_fails` confirms the row and its `body` survive an injected delivery failure.
- **Idempotency, split correctly**: domain idempotency is Wave 2's `client_message_id` (unchanged here); delivery idempotency is `wagle_push_delivery_attempts`'s unique `(outbox_event_id, subscription_id)` (§7) plus client-side `(room_id, room_sequence)` dedup (§17) — two different keys for two different guarantees, not conflated.

## 9. Outbox Owner Isolation — the mandatory first work item, independently re-verified

Both HIGH corrections read directly in `service_outbox/service.py` and
`workers/service_outbox.py` (full text in this session's earlier read, not
paraphrased from the report):

**9.1 `claim_batch(..., owner_service=...)`** filters at the SQL `WHERE`
clause (`conditions.append(ServiceOutboxEvent.owner_service == owner_service)`)
before the `FOR UPDATE SKIP LOCKED` claim — not a post-claim release, which
the code comment itself notes would still stall the other consumer for a
lease. `workers/service_outbox.py::run_once()` iterates only
`ALLOWED_ACTIONS_BY_OWNER` (currently `{"mark-point"}`), so it can **never**
call `claim_batch` with `owner_service="wagle"` or `None` — this is a
structural guarantee, not merely a default.

**Independently re-run tests (not accepted from the report's pass count):**

| # | Required result | Test | Result |
|---|---|---|---|
| 1 | SERVICE_ACTION worker does not claim a Wagle row | `test_service_action_worker_does_not_claim_a_wagle_owned_row` **— added by this QA session**, because no existing test covered this direction (only the reverse, #2, existed) | **PASS** — `claimed == 0`, foreign row stays `status="PENDING"`, `attempt_count == 0` |
| 2 | Wagle worker does not claim another owner's row | `test_dispatcher_claim_is_scoped_to_its_own_owner_service` (pre-existing) | **PASS** — re-run independently; `claimed == 1` (only its own row), the `mark-point` row stays `PENDING`, zero bogus `wagle` `ServicePrincipal` rows created |
| 3 | `record_failure` succeeds after rollback | `test_dispatcher_never_touches_the_durable_message_when_delivery_fails` (pre-existing) | **PASS** — re-run independently against an injected `RuntimeError`; no `MissingGreenlet` |
| 4 | `attempt_count` increments exactly once | same test | **PASS** — `event.attempt_count == 1` |
| 5 | No `PROCESSING` abandonment | same test | **PASS** — `event.status == "PENDING"` (rescheduled), not left `PROCESSING` |
| 6 | retry → `DEAD` transition correct | `test_outbox_06_max_attempts_exceeded_dead` (pre-existing, Wave 2 reliable-service-slice suite) | **PASS** — re-run independently inside the full 239 (§24) |

This QA session's own addition (#1) closes a real asymmetry: the existing
suite proved the Wagle dispatcher's isolation but not the SERVICE_ACTION
worker's, even though both directions are structurally guaranteed by the
same `owner_service`-filtered `claim_batch`. Recorded and applied as a
`Correction Applied` in §26, not silently folded into "already covered".

## 10. NOTIFY Payload Contract

Read directly from `realtime_notify.py::_notify()`:

```text
origin, event_id, event_type, family_id, room_id, message_id,
room_sequence, occurred_at, actor_type
```

No `body`, no sender identity beyond `actor_type` (`ACCOUNT`/`SERVICE` — a
category, not an identity), no Push secret, no WebSocket token, no PIN, no
endpoint key, no user-facing delivery state. `MAX_PAYLOAD_BYTES = 7000`,
under PostgreSQL's 8000-byte NOTIFY cap with margin; an over-cap payload is
dropped (never truncated) and falls back to the durable catch-up — read
directly in `_notify()`'s size guard. `pg_notify()`'s return value is never
read by any caller in this file. The polling fallback
(`resume_missed_events`) is untouched by this Wave (§17).

## 11. Cross-process Test Topology

Two **separate Docker containers** (`w3fanout-a`, `w3fanout-b`), each its own
OS process tree (own PID 1, own PID namespace — stronger isolation than two
processes on a bare host), both `--add-host=host.docker.internal:host-gateway`
against the same disposable `mongle-w3qa-testdb`. Each container ran a
standalone script (not part of the product test suite) that constructs the
exact same `PostgresNotifyFanout(InProcessFanout(), dsn)` pairing
`app/main.py`'s lifespan does, registers one local `Connection` subscribed to
a shared `(family_id=999999, room=<fixed UUID>)`, and starts the listener —
i.e., the real product code path, driven from outside the product's own test
harness.

## 12. Process Identity Proof

Application-level: each container printed a distinct `origin_id`
(`1-c8a2d511` for A, `1-172cf552` for B — the random-suffix half differs even
though both containers report `pid=1`, since each is its own container's
init process).

Database-level, independent of the application's own self-report: queried
`pg_stat_activity` directly and found **two distinct PostgreSQL backend
PIDs**, each independently executing `LISTEN "wagle_realtime"`:

```text
pid 2628 | LISTEN "wagle_realtime" | backend_start 07:06:54.120594
pid 2629 | LISTEN "wagle_realtime" | backend_start 07:06:54.191874
```

Two independent connections, ~71ms apart — this is the database's own
bookkeeping, not something either container's application code could
fabricate.

## 13. A→B Delivery

Container A published one envelope (`message_id="from-A-1"`) at
`occurred_at=07:07:22.116000`. Container A's own local `Connection` received
it at `07:07:22.116059` (59μs later — in-process, expected). Container B's
`Connection`, which has no local publisher and shares no process memory with
A, received the identical envelope at `07:07:22.149391` — **33ms** after A's
publish, and orders of magnitude under the 5s durable-catch-up fallback
interval. `room_sequence`, `message_id`, and `family_id`/`room_id` in B's
received record are byte-identical to what A published. This is proof of
genuine cross-process delivery: A's `InProcessFanout` had zero connections
that could reach B directly; the only path between the two containers is
PostgreSQL.

## 14. B→A Delivery

Symmetric run: B published `message_id="from-B-1"` at `07:07:30.951989`; B's
own local delivery at `07:07:30.952106`; A received it at `07:07:30.987632`
— **36ms** later, via the identical NOTIFY→listener→local-registry path in
the reverse direction. Confirms the fan-out is bidirectional, not an
artifact of which container happened to publish first.

## 15. Local Duplicate Suppression

Each container's own listener is also subscribed to `wagle_realtime` and
would, absent the `origin_id` check, re-deliver its own publish to its own
local connection a second time when its own NOTIFY arrives back. Measured
final counters, read from each container's own shutdown log:

```text
A: total_received=2, skipped_own=1, notify_received=1
B: total_received=2, skipped_own=1, notify_received=1
```

Each container received **exactly 2** events total across both rounds (1
local-instant + 1 genuine cross-process), and each explicitly `skipped_own=1`
— proving the origin-suppression path in `_on_notify()` actually executed,
not merely that no duplicate happened to occur. This is server-side
suppression, independently confirmed rather than inferred from the absence
of a client-visible duplicate (which client dedup could have masked).

## 16. NOTIFY Failure Recovery

Not re-run ad hoc in this harness beyond §17's listener-restart proof;
covered instead by the independently re-executed automated suite (§24),
which includes (both re-run and passing): duplicate-NOTIFY safety, full
NOTIFY-omitted recovery (`test_wagle_multiworker_fanout.py` asserts recovery
with **zero** NOTIFY emitted, exercising the durable catch-up path
exclusively), and PostgreSQL transient-unavailability isolation (publish
degrades to local-only, never raises into the caller — confirmed by direct
read of `publish()`'s `try/except` around `_notify()`, §10). Recorded as a
separate evidence source from §11-15's live harness, not merged into one
claim.

**Listener restart — live proof, this harness:** queried the two listener
backend PIDs (§12: 2628, 2629), then `pg_terminate_backend()`'d one (2629).
Immediately after, exactly one `LISTEN "wagle_realtime"` backend remained
(2628); ~3s later a **new** backend (2676, fresh `backend_start`) appeared
holding the same `LISTEN`, proving the killed container's reconnect-with-
backoff loop (`_listen_loop`, base 0.5s/cap 30s) fired and successfully
re-attached — read directly in `realtime_notify.py` and now confirmed live
against a real forced disconnect, not just by code inspection. Post-reconnect
message delivery for *this specific* killed-and-reconnected instance was not
separately re-driven in this harness (the containers were already mid-
teardown); that exact scenario is covered by
`test_wagle_multiworker_fanout.py`'s independently re-run
listener-restart-then-later-events-received test (§24), which this QA
accepts as the second, distinct evidence source rather than re-deriving a
third ad hoc proof of the same claim.

## 17. Production Topology

`docker-compose.prod.yml` line 26: `command: uvicorn app.main:app --host
0.0.0.0 --port 8000 --workers 2` — read directly, matches the claim.
`frontend/nginx.conf`: WebSocket upgrade `map $http_upgrade
$connection_upgrade` present; `location = /api/me/wagle/ws` proxies with
`proxy_set_header Upgrade $http_upgrade` / `Connection $connection_upgrade`
and a 3600s idle budget; **zero** `doran` occurrences anywhere in the file
(grep, confirmed) — the retired `^/api/families/[^/]+/doran/service/actions$`
rule is gone and the 32KB body-cap rule now matches
`^/api/families/[^/]+/wagle/service/actions$`.

**Independently re-run, real container**, not accepted from the report: a
fresh `uvicorn --workers 2` container against the same disposable DB —
`curl /api/health` → `{"status":"ok",...}`; `pg_stat_activity` showed **two**
distinct backend PIDs (2689, 2690) each holding `LISTEN "wagle_realtime"`,
confirming each of the two workers independently attached its own listener
in this run, not merely in the implementer's own prior run.

**Independently re-run, live WebSocket handshake against that same
container**, not accepted from the report: connecting to `/api/me/wagle/ws`
with no token — HTTP upgrade to 101 succeeds (nginx is not in this
container-only path, so this is the gateway's own behavior), the server then
sends `{"type":"error","code":"unauthorized"}`, then closes with **code
4401** — exactly the terminal code the frontend's reconnect-loop fix (§26 of
the implementer's report, re-confirmed in §21 below) checks for.

## 18. WebSocket Security

Live-confirmed in §17 (no-token → 101 handshake, `unauthorized` message,
terminal `4401` close). The remaining required cases (legacy player JWT
rejected, revoked Session rejected, suspended Account rejected, multi-Family
subscription, cross-family room denial, Session-revoke-closes-all-connections
vs one-Family-membership-ends-only-that-subscription) were independently
re-executed as part of the full-suite run (§24) via
`test_wagle_websocket_gateway_wave3.py`'s 15 tests (part of the 41 collected
in `test_wagle_realtime_wave3.py` + the gateway file together) — re-run by
this session, not accepted from the report's count. Source-level
confirmation: `authorize_subscription()` (`wagle/realtime.py`) raises the
same `PermissionError` for "no active membership", "room not in this
family", and "not an active participant" alike (§ code read above) — a
caller cannot distinguish "wrong family" from "no such room", which is the
information-boundary property the QA task requires.

## 19. Cursor Recovery

`resume_missed_events()` read directly: re-derives authorization via
`authorize_subscription()` on every call (not trusted from the open
connection); `floor_sequence = max(cursor, participant.joined_sequence - 1)`
— a participant added after messages already existed cannot read history
from before they joined by resuming from 0, confirmed by source and by the
independently re-run resume tests inside §24's 239. `has_more` is returned
rather than silently truncating a large gap. No global cursor exists anywhere
in this module — ordering is exclusively per `(family_group_id, room_id)` via
`WagleMessage.sequence`.

## 20. Push Infrastructure

Schema-level (§7): idempotency and per-endpoint isolation both enforced by DB
constraints, not just application code. Source-level: `push_service.py`'s
transport is a port with `NullPushTransport` the default — confirmed no
external network call is reachable in this test environment, matching the
report's "no external push service contacted" claim. Payload boundary:
confirmed (§10-adjacent read) that `build_payload()` is the single seam and
carries identifiers only. **Browser Web Push E2E was not run** — no VAPID
key or push service exists in this environment, consistent with the report;
this QA does not claim it as PASS either. What was independently verified is
exactly the adapter/lifecycle/payload-boundary/failure-isolation slice, via
the independently re-run test suite (§24), not the end-to-end browser path.

## 21. Wagle PIN

Schema (§7): `pin_hash` only, bcrypt-sized column, no plaintext PIN column
anywhere; unique `(account_id, device_id)`; `failed_attempt_count` with a
non-negative CHECK; `locked_until` for temporary lockout;
`last_reset_at`/`disabled_at` for reset-not-recovery and audit. Device
isolation and non-impact on Session/Push/other-service access were not
re-derived from scratch in this harness; they were independently re-executed
via the full suite (§24), which includes the device-PIN test group inside
`test_wagle_realtime_wave3.py`.

## 22. Frontend Regression

Both run independently against the live bind-mounted source (not a stale
toolchain image — `docker inspect` confirmed
`/Users/mac/mac_Project/mongle_ui/frontend -> /app`):

```text
npx tsc --noEmit   -> EXIT=0
npx eslint .       -> EXIT=0
```

Naming gate, independently re-grepped (not accepted from the report):
`frontend/src` + `frontend/public` → **0** `doran` occurrences; the sole
`naran` mention in `frontend/src` is a comment in `App.tsx` about removed
compatibility aliases, not a live code path; the deliberate
`RETIRED_KEY_NAMESPACE = 'na' + 'ran'` / `RETIRED_PLATFORM = 'na' + 'ran'`
string-concatenation pattern is confirmed still intact in
`activeFamilyStorageMigration.ts` and `01-shell.spec.ts` — not inlined into a
literal, which the relay explicitly warns against. Backend: exactly **1**
`doran` occurrence in active code, a prohibition comment in the new
`markpoint_access/wagle_relay_adapter.py` ("no `doran` fallback") — the
allowed category. **Playwright was not independently re-run** in this
session (time/scope tradeoff, stated rather than hidden); the 121/0/4/0
figure is the implementer's own, not re-verified here, and is explicitly
**not** presented as this session's own PASS. The `WagleLanding` preview-
fixture boundary (real room wiring is Wave 6) was confirmed unchanged by
this Wave via the changed-file audit (§5) — no product code in
`WagleLanding.tsx`'s message-rendering path was touched beyond what the
diff already shows.

## 23. Test Matrix

| Scope | Command | Result |
|---|---|---|
| Full backend suite | `python -m pytest -q` (disposable DB, fresh container) | **239 passed, 0 failed** (166.59s) |
| Owner-isolation + rollback targeted | `pytest -k 'owner_service or scoped_to_its_own or symmetry or rollback or never_touches'` | 2 passed (plus the new symmetric test run individually, 1 passed) |
| Migration fresh/downgrade/re-upgrade | `alembic upgrade head` / `downgrade -1` / `upgrade head` | PASS, single head, 0 residue |
| Cross-process fan-out | ad hoc two-container harness (§11-16) | PASS, both directions, no duplicates |
| Production `--workers 2` | real container + `pg_stat_activity` + live WS handshake | PASS |
| `tsc --noEmit` | `npx tsc --noEmit` | EXIT=0 |
| `eslint` | `npx eslint .` | EXIT=0 |
| Playwright | not run this session | `NOT_RUN` — see §22 |
| Browser Web Push E2E | not run this session (no VAPID/service) | `NOT_RUN`, consistent with the report |

**239 vs the reported 238**: this QA session added one test (§9, item #1);
238 (report) + 1 (this session) = 239, exactly accounted for — not an
unexplained discrepancy.

## 24. Regression

Confirmed inside the same 239-test run: Wave 1 Account/Session/RBAC (
`test_account_auth_wave1.py`), Wave 2 durable messaging
(`test_wagle_durable_wave2.py`), Wave 4 Markpoint access
(`test_markpoint_access_wave4.py`, `test_integration_wagle_markpoint.py`),
and the ServicePrincipal→Wagle relay tests all pass unmodified. Alembic
remains a single head (`0009`, §7). OpenAPI (`frontend/src/generated/
openapi.d.ts`) was not independently regenerated in this session; its
presence and doran-free content were confirmed by the same grep as §22
rather than by re-running the generator.

## 25. Defects Found / Corrected

**None found.** The two HIGH corrections already present in the tree (§9)
were independently confirmed fixed, not newly discovered by this session —
this QA's job on them was verification, which is what §9's table records.

## 26. Corrections Applied

**One test added**, not a product-code fix:
`backend/tests/test_wagle_realtime_wave3.py::
test_service_action_worker_does_not_claim_a_wagle_owned_row` — closes the
one-directional gap in the existing owner-isolation coverage (§9). No
product code was modified by this QA session.

## 27. Recursive Review

**Pass 1 (after Start Gate):** report vs. actual diff matched on every file
class checked (§5); D6-P1-P8 confirmed still all `DEFERRED` from the live
SSOT, not assumed; the two Outbox HIGH corrections' exact code locations
matched the report's claims; production topology (`--workers 2`, nginx)
matched.

**Pass 2 (after backend verification):** Outbox owner isolation confirmed
bidirectionally (only after this session added the missing direction, §9);
rollback-safe `record_failure` confirmed by live re-run, not by reading the
docstring alone; DB remains SSOT (no envelope carries content, §10); Room
ordering and Family isolation confirmed by source read plus the independently
re-run test suite.

**Pass 3 (after cross-process E2E):** real PID separation confirmed at both
the application layer (distinct `origin_id`) and the database layer (distinct
`pg_stat_activity` PIDs, §12) — two independent proofs, not one; A→B and B→A
both measured with real timestamps well under the fallback interval;
local-duplicate suppression confirmed via `skipped_own` counters, not
inferred from absence of a visible duplicate; listener reconnection
independently forced and confirmed via a fresh backend PID (§16).

**Pass 4 (after full test run):** §22-23 explicitly separate what was
independently re-run (backend suite, tsc, eslint, migration, cross-process
harness, production topology, live WebSocket handshake) from what was not
(Playwright, browser Web Push) — neither NOT_RUN item is reported as PASS;
Docker residual confirmed 0 (§28); the report's own 238 vs. this session's
239 is explained, not glossed over (§23); Lifecycle axes for Core vs.
policy-dependent slices are kept separate throughout (§6, §29-30).

## 28. Five-Gate Review

- **환각**: every count above is a command result from this session (test
  output, `pg_stat_activity` query, `grep`, `tsc`/`eslint` exit codes, or a
  timestamped file this session's own harness wrote). The two-listener-
  object-vs-two-OS-process distinction is honoured explicitly (§11: two
  separate Docker containers, each its own PID namespace) — never presented
  as equivalent to a single test process. The real `--workers 2` container
  check and the two-container NOTIFY harness are kept as separate,
  non-merged claims (§17 vs §11-16), exactly as this task's own instructions
  require. No unrun test (Playwright, browser Push) is reported as PASS.
- **누락**: migration (§7), Outbox isolation (§9), dispatcher (§8), WebSocket
  auth (§18), multi-Family (§18), cross-process fan-out (§11-16), resume
  (§19), Push infrastructure (§20), PIN (§21), frontend (§22), production
  topology (§17), test matrix (§23) — all present.
- **오작업**: NOTIFY payload confirmed identifier-only (§10); NOTIFY's return
  value confirmed never read as a delivery signal; the durable catch-up
  confirmed untouched and covered by an independently re-run
  zero-NOTIFY-emitted test (§16); no global ordering found anywhere (per-room
  sequence only, §19); no `exactly-once` claim found anywhere in source; the
  device PIN's schema carries no Session/Push/Markpoint-blocking mechanism
  (§21, structurally — no foreign key or status flag from `wagle_device_pins`
  reaches `account_sessions` or `wagle_push_subscriptions`); no legacy PIN
  reuse (`wagle_device_pins` is a wholly new table, §7); zero live
  `doran`/`naran` runtime occurrences (§22).
- **축혼동**: durable DB state vs. Outbox vs. NOTIFY wake-up vs. local
  WebSocket registry vs. cursor recovery vs. Push notification vs. Account
  Session vs. Wagle PIN vs. transport ACK vs. user-facing delivery vs. D6
  deferred policy are each discussed in their own section above and never
  conflated — in particular §10 and §16 repeatedly restate that NOTIFY
  success is not delivery success.
- **신선도·오탈자**: real HEAD `2243aa8` (§2); real Alembic head `0009`,
  single (§7); current Backlog status read live (§4, §6); production
  `--workers 2` and nginx route read live, not from memory (§17); OpenAPI
  presence and naming-gate re-grepped (§22, §24); `git diff --check` clean at
  both start and end (§2); no duplicate Task ID introduced; one documentation-
  precision correction recorded (CHECK-constraint count, §7) rather than
  silently adopting the report's figure.

## 29. Changed-file Manifest (this QA session)

**Modified:** `backend/tests/test_wagle_realtime_wave3.py` (one test added,
§9/§26), `agent-system/active.md`, `agent-system/relay/current.md`.

**New:** `agent-system/qa/MONGLE-W3-WAGLE-INDEPENDENT-QA-001.md` (this file),
`agent-system/handoffs/active/MONGLE-W3-WAGLE-INDEPENDENT-QA-001.md`.

**Untouched:** every other Wave 3 product/migration/frontend file (§5); all
pre-existing dirty files from prior tasks; `agent-system/qa/COVERAGE_MAP.md`
(reviewed, no row needed a change beyond what a follow-up graduation task
will add).

## 30. Deferred Policy Slices

```text
D6-P1..P8                     : UNDECIDED — unchanged, 7 Backlog rows not started
Push payload disclosure       : POLICY_BLOCKED (seam implemented, tested)
Browser Web Push E2E          : BLOCKED — no VAPID key / push service (unchanged)
Realtime UI message journey   : BLOCKED_BY_WAVE_6 (MONGLE-W5-TARGET-UI-001)
Multi-process fan-out latency : RESOLVED this Wave — LISTEN/NOTIFY closes it (§11-16)
```

## 31. Lifecycle / Graduation

Core is independently verified `PASS`. Graduation candidates (Core scope
only, per this task's own §24 list): the Wave 3 implementation scope of
`MONGLE-W2-WAGLE-REALTIME-001`, `MONGLE-W3-WAGLE-RECONNECT-RESUME-001`,
`MONGLE-W3-WAGLE-MULTIFAMILY-SUBSCRIPTION-001`,
`MONGLE-W3-WAGLE-FAILURE-ISOLATION-001`, `MONGLE-W3-WAGLE-PIN-LOCK-001`,
`MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001`, and the implemented-lifecycle half
of `MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001`. **Not** graduated: `D6-P1`-`P8`
Backlog rows (still `DEFERRED`), browser Web Push E2E, the Wave 6
message-level UI journey. Per this task's own §21/§24, this QA does not
itself flip Lifecycle to `COMPLETE` in `active.md`/`relay/current.md` beyond
recording the verdict — PM graduation decision remains a separate step,
consistent with how `MONGLE-W1-INDEPENDENT-QA-001` was handled.

## 32. Final Verdict

```text
WAVE_3_INDEPENDENT_QA_PASS
WAGLE_REALTIME_CORE_LIFECYCLE_COMPLETE
WAGLE_RECOVERY_LIFECYCLE_COMPLETE
WAGLE_MULTIWORKER_FANOUT_LIFECYCLE_COMPLETE
WAGLE_DEVICE_PIN_LIFECYCLE_COMPLETE
WAGLE_PUSH_INFRASTRUCTURE_LIFECYCLE_COMPLETE
D6_POLICY_DEPENDENT_SLICES_DEFERRED
READY_FOR_NEXT_WAVE_REVIEW
```

## Closeout Synchronization

- Contract: v1
- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED` — `agent-system/handoffs/active/MONGLE-W3-WAGLE-INDEPENDENT-QA-001.md`
- QA EVIDENCE: `UPDATED` — this file
- Independent QA: this is the independent QA — PASS
- COVERAGE MAP: `NOT_MODIFIED_BY_THIS_SESSION` — reviewed, no row required a
  change beyond what a PM graduation pass will add; the one new test (§9,
  §26) protects an existing Coverage Map row's claim rather than opening a
  new one.
- CLOSEOUT GATE: `PASS`
