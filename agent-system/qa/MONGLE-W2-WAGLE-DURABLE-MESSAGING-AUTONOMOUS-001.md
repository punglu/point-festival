# MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001

- Task ID: `MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001` (Lane A)
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged start → end)
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; tests against a disposable volume-less PostgreSQL 16.9 container on `127.0.0.1:15435`
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Verdict

```text
WAGLE_NAMING_CONTRACT_PASS
TRACK_A_IMPLEMENTATION_COMPLETE
TRACK_A_TESTS_PASS
TRACK_A_SELF_QA_COMPLETE
TRACK_A_READY_FOR_INDEPENDENT_QA
PARENT_BUNDLE_IN_PROGRESS
```

### Verdict history — this Lane was rejected once and corrected

| Round | Verdict | Cause |
|---|---|---|
| 1 | `TRACK_A_IMPLEMENTATION_COMPLETE` | Self-assessed. Emitted `owner_service="doran"`, `event_type="doran.message.created"`, `aggregate_type="doran_message"`. |
| — | `REJECTED_PENDING_NAMING_CORRECTION` / `TESTS_INVALIDATED_FOR_AFFECTED_ASSERTIONS` / `INDEPENDENT_QA_BLOCKED` | **PM rejection.** New Target contracts must not inherit the historical `doran` name. |
| 2 | current | Corrected under `MONGLE-W2-WAGLE-NAMING-CONTRACT-CORRECTION-001`; full suite re-run from a freshly created database. |

**The rejected reasoning, recorded so it is not repeated.** Round 1 argued that
reusing the registered `SERVICE_CODE` avoided minting a second identifier for
one service. That inverted the rule: the Data Naming Contract warns against
uncontrolled renaming of *existing* data, not against new Target contracts using
the Target name. Emitting `doran` into a brand-new event contract would have
made Target and legacy names coexist permanently in the delivery layer — the
exact split the rule exists to prevent. The correction is accepted, not
rationalised.

## 2. Environment / Git

| Measurement | Start | End |
|---|---|---|
| repo root | `/Users/mac/mac_Project/mongle_ui` | same |
| branch | `dev-newmarkp` | `dev-newmarkp` |
| HEAD | `0d9280c` | `0d9280c` (no commit) |
| working tree at start | clean (0 uncommitted) | 4 files (3 modified, 1 new) |
| `git diff --check` | clean | clean |

**Worktree note, reported rather than assumed.** The task brief asks Track A to
use a worktree separate from Track B. Track B does not exist yet — no session,
no worktree — and the PM instructed this session to work in the repository
root. Track A therefore runs in the root, which means **Track B must not use
the root** while Lane A is open. This is recorded in the parent bundle entry so
Track B inherits the constraint rather than discovering it. The only other
worktree on disk is the historical detached `data-backend-contract-worktree`
under `/private/tmp/...` (audit finding F7), which is untouched and is not
Track B's.

## 3. Wave 1 baseline verification

Verified against HEAD itself, not against the Wave 1 report's PASS wording:

```
git merge-base --is-ancestor 2f1c354 HEAD          -> exit 0 (Wave 1 is an ancestor)
git cat-file -e HEAD:backend/alembic/versions/0005_account_credential_session.py  -> present
git cat-file -e HEAD:backend/alembic/versions/0006_family_service_separation.py   -> present
git cat-file -e HEAD:backend/app/domains/family/auth_service.py                   -> present
git cat-file -e HEAD:backend/app/domains/family/dependencies.py                   -> present
git cat-file -e HEAD:backend/tests/test_account_auth_wave1.py                     -> present
git cat-file -e HEAD:agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md              -> present
git show HEAD:backend/app/domains/family/models.py | grep -c "class Account(Credential|Session)" -> 2
```

Alembic head at start: single, `0006_family_service_separation`. Baseline is
materialized in commits, not merely present as another worktree's uncommitted
diff. **Not** `BLOCKED_BASELINE_NOT_MATERIALIZED`.

## 4. Backlog task inventory (extracted, not invented)

| Task ID | Status before | DB impact | API impact | Reality found |
|---|---|---|---|---|
| `MONGLE-W2-WAGLE-DURABLE-COMMAND-001` | `BLOCKED_BY_DEPENDENCY` | none | none | **Already implemented.** `send_message` + `list_messages` with `client_message_id` idempotency, cursor pagination, room/participant rules. Verified by test, not rebuilt. |
| `MONGLE-W2-WAGLE-TRANSACTIONAL-OUTBOX-001` | `BLOCKED_BY_DEPENDENCY` | none (existing table) | none | **The real gap.** See §5. |
| `MONGLE-W2-WAGLE-ORDERING-CURSOR-001` | `BLOCKED_BY_DEPENDENCY` | none | none | **Already implemented.** Atomic `next_message_sequence` advance with `UNIQUE(room_id, sequence)`; forward-only cursor via a `GREATEST` upsert. Verified by test. |
| `MONGLE-W2-WAGLE-ROOM-LIST-READ-MODEL-001` | `BLOCKED_BY_DEPENDENCY` | none | 1 new route | **Gap.** `list_rooms` returned bare rows. |

No existing Task ID was replaced. The bundle id is a coordination label only.

## 5. Start Gate answer the Backlog explicitly asked for

> "**Start Gate:** verify whether the current implementation already shares one
> transaction."

**No.** `send_message` persisted the message and advanced the room's sequence,
then committed — and wrote **no** Outbox row at any point. The
`service_outbox_events` table existed and was already correctly designed for
caller-owned transactions (`enqueue_event` never commits and isolates its
conflict handling in a SAVEPOINT), but its only producer was Markpoint mission
completion. A human Wagle message produced nothing for Wave 3's dispatcher to
deliver.

So D6's atomicity requirement was **unmet**, not partially met — which is a
materially different finding from "the transaction boundary needs tightening",
and is why this Lane's central change is an addition rather than a refactor.

## 6. Implementation

**Outbox emission inside the send transaction.** `send_message` now calls
`_enqueue_message_event()` after `flush()` and before `commit()`. The event's
`source_event_id` is the message's own UUID, which makes the enqueue idempotent
for free and gives a dispatcher a stable key. The payload carries
`family_group_id`, `room_id`, `message_id`, `sequence`, `message_type`,
`sender_participant_id` and `occurred_at` — identifiers and a delivery hint,
never a second copy of the message's authority.

**Batch room list.** New `GET /api/families/{family_id}/doran/room-summaries`
returns each room with its last visible message preview and the caller's unread
count in one round trip, via two `LATERAL` subqueries that reuse the existing
`(room_id, sequence)` index. Added **alongside** `/rooms` rather than replacing
it, so callers needing only room identity are unaffected. Visibility is the
participant's own `joined_sequence..left_sequence` window, matching
`visible_range()` — a member who left still sees exactly the history they were
present for.

**Naming (corrected).** Everything this Lane newly emits uses the Target name:

| Emitted value | Constant | Value |
|---|---|---|
| Outbox `owner_service` | `WAGLE_SERVICE_CODE` | `wagle` |
| Outbox `event_type` | `MESSAGE_CREATED_EVENT_TYPE` | `wagle.message.created` |
| Outbox `aggregate_type` | `MESSAGE_AGGREGATE_TYPE` | `wagle_message` |

### `RUNTIME_DORAN_IDENTIFIER_COUNT` — audited, not asserted

**Newly emitted by Track A: 0.** Verified two ways — grep over the three
constants that reach the database, and a test that asserts over the *stored*
rows rather than the source, so a future edit reintroducing `doran` into an
event contract fails even if it renames the constant.

**Pre-existing, not created by Track A, deliberately unchanged — enumerated so
the remaining surface is visible rather than implied:**

| Identifier | Count | Why not changed here |
|---|---|---|
| `SERVICE_CODE = "doran"` | 1 | Lookup key for existing `service_subscriptions` and role rows seeded under that value; changing it without migrating those rows breaks every subscription and role check. |
| `doran.messages.read/send`, `doran.rooms.create/manage`, `doran.participants.manage` | 5 | Permission codes seeded by migration `0002` and bound in `role_permissions`; renaming needs a seed migration plus role remap. |
| Route prefix `/api/families/{family_id}/doran`, tag `doran` | 1 prefix / 17 routes | Moving only the one new route would create a two-prefix split for one domain — the very coexistence this correction prevents. |
| Physical tables `doran_*`, module `app.domains.doran`, classes `Doran*` | — | Physical rename explicitly not required. |

These are one coordinated migration, not a feature-Wave side effect.
Recommended follow-up, **not opened by this Lane**:
`MONGLE-WAGLE-LEGACY-IDENTIFIER-MIGRATION-001` covering the service code,
permission codes and route prefix together with the data migration for existing
subscription and role rows. Reporting the residue is deliberate: claiming a
repository-wide zero would have been false.

## 7. Migration

**None was created, and this is deliberate.** Both changes needed only the
existing `service_outbox_events` table and the existing
`ix_doran_messages_room_sequence` index. Alembic remains at a single head,
`0006_family_service_separation`, verified by `alembic heads` and `alembic
current` against a freshly migrated database.

The brief assigns Track A sole migration ownership; that ownership still holds
for Lane B. Creating an empty revision to look compliant would have added a
meaningless head to the chain, so it was not done.

Migration reproduction was still exercised end to end, because Wave 2 must not
break it: `0000 → 0006` applied cleanly to a fresh database seeded from
`database/init.sql`.

## 8. Tests

```
docker run --rm --network container:mongle-w2-testdb -v $PWD/backend:/app -w /app \
  -e DATABASE_URL=postgresql+asyncpg://mc_phase2:***@127.0.0.1:5432/mc_festival_phase2 \
  <backend-image> sh -c "pip install -q pytest pytest-asyncio httpx; python -m pytest -q"
```

Re-run in full after the naming correction, from a **container created fresh for
that run** (`database/init.sql` baseline, then all 7 revisions `0000`→`0006`) —
not the environment the first round used.

| Scope | Result |
|---|---|
| `tests/test_wagle_durable_wave2.py` | **PASS — 20 passed** (19 + 1 new naming-contract regression) |
| Lane A total | **PASS — 124 passed, 0 failed** (20 Wave 2 + 104 pre-existing) |
| Whole `backend/tests` directory as it stands | **145 passed, 0 failed** |
| `alembic upgrade head` on the fresh DB | **PASS**, 7 revisions applied, single head `0006` |

**The 145 figure is not Lane A's result and must not be read as one.** 21 of
those tests are `tests/test_markpoint_access_wave4.py`, which belongs to Track B
— see §14. Lane A's own number is 124. The full-directory run is reported
because it is what actually executed, and because it shows the two lanes'
suites currently coexist without breaking each other.

Coverage against the brief's required list: message persistence; message+Outbox
atomicity; forced-failure rollback of both **and** of the room sequence;
`client_message_id` duplicate suppression; same-id-different-body conflict;
same-room ordering; cross-room ordering independence; cross-family isolation
(read and write); inactive-membership denial; read cursor advance; cursor
regression refusal; per-membership read isolation; out-of-range cursor
rejection; room-summary preview/unread; own-message exclusion; deleted-message
body suppression; non-participant exclusion; empty-room listing.

No existing test was deleted, skipped, xfailed, or weakened. The 104
pre-existing tests ran unmodified.

## 9. Not run

| Scope | Status | Reason |
|---|---|---|
| Human actor vs ServicePrincipal actor separation | `NOT_RUN` (new tests) | Already covered by the 26 pre-existing `test_doran_service_binding.py` / `test_doran_reliable_service_slice.py` tests, which ran and passed in this session's post-correction run. Duplicating them would add no protection. |
| Unauthorized Room-binding denial | `NOT_RUN` (new tests) | Same — pre-existing coverage, re-run and passing. |
| WebSocket, Web Push, Service Worker, PIN, presence | `NOT_RUN` | Out of Wave 2 scope by contract; none of it exists. |
| Frontend lint/build, Playwright E2E | `NOT_RUN` | No frontend change; no FE consumer of these routes exists. |

## 10. Self-QA findings

| # | Finding | Disposition |
|---|---|---|
| 1 | Outbox emission missing from the send path entirely | **Fixed** — the Lane's central change |
| 2 | First draft of `room_summary_out()` called a `family_id_of(row)` helper that does not exist | **Fixed** before any test run — `family_group_id` is now selected by the query itself, which is also more self-consistent |
| 3 | First draft introduced `WAGLE_OWNER_SERVICE = "doran"`, duplicating the existing `SERVICE_CODE` constant | **Fixed** — reuse the existing constant; a second name for one value is the defect, not the fix |
| 4 | Unread count ignores SERVICE_ACTION messages (`sender_participant_id <> :pid` is NULL for them) | **Not changed, recorded.** Inherited from `read_state()`. Matching it deliberately so list and detail agree; making them disagree would be worse than either rule. The user-visible rule is D6-P4, undecided. Flagged for Wave 3. |

## 11. Recursive scope review

- **Before:** planned `doran/{service,router,schemas}.py` + a new test file; no migration expected once the Outbox table was confirmed sufficient.
- **After implementation:** `git status` shows exactly those 4 files. No Markpoint, service-ownership, frontend, migration or `agent-system`-shared product file touched.
- **After tests:** documentation matches behaviour (API Inventory, Realtime Contract, Backlog, Coverage Map all updated); no global ordering introduced; no direct cross-domain DB access added — the only new import is `service_outbox.service`, taken as a module and called through a dotted reference per the Backend Guide.

## 12. Five gates

- **환각:** every claim rests on a command, SQL result or test run in this session. The Start Gate answer came from reading `send_message` itself, not from the Backlog's expectation. No Alembic log line was accepted as proof.
- **누락:** message, room, human actor, system actor, ordering, idempotency, read state, Outbox, family isolation, migration (verified as not-needed), API, tests, documents — all addressed.
- **오작업:** no global ordering; no exactly-once claim (at-least-once with dedup, stated); Push is not treated as SSOT and is not implemented; no legacy message backfill; family human identity remains `FamilyMembership`, never the Account; no direct cross-domain DB access; no WebSocket/Push/PIN work.
- **축혼동:** current Doran implementation, approved Wagle Target, this Wave's durable output, Wave 3 realtime and the `D6-P` deferred policies are separated explicitly in the Realtime Contract table.
- **신선도:** API Inventory, Realtime Contract, Backlog and Coverage Map updated to match shipped behaviour; `git diff --check` clean; no duplicate Task ID.

## 13. Changed file manifest

**Modified (3):** `backend/app/domains/doran/service.py`,
`backend/app/domains/doran/router.py`,
`backend/app/domains/doran/schemas.py`

**New (1):** `backend/tests/test_wagle_durable_wave2.py`

**Records/docs:** `engineering/phase2/MONGLE_TARGET_API_INVENTORY.md`,
`MONGLE_REALTIME_MESSAGING_CONTRACT.md`, `MONGLE_IMPLEMENTATION_BACKLOG.md`,
`agent-system/qa/COVERAGE_MAP.md`, `agent-system/active.md`,
`agent-system/relay/current.md`, this file and its handoff.

## 14. Track B conflict assessment — corrected: Track B is running

**Round 1 of this report said "Track B has not started". That was true when
measured and is now false.** During the naming-correction re-run, a port
collision on 15435 exposed a container `mongle-w4-testdb`, up and serving. Track
B is executing **in this same repository root**, which is the parallel-safety
constraint Lane A had declared and recorded.

Track B's footprint, measured from `git status` (read only — nothing of Track
B's was modified, and its container was left running):

```
?? backend/app/domains/markpoint_access/{__init__,router,schema,service,system_event_port}.py
?? backend/tests/test_markpoint_access_wave4.py      (21 tests)
 M backend/app/main.py                               (shared file — Track B's edit)
```

**File-level conflict: none.** Lane A touched only
`backend/app/domains/doran/{service,router,schemas}.py` and its own test file;
Track B touched only `markpoint_access/**`, its own test file, and `main.py`.
The two sets are disjoint. `backend/app/main.py` is the one shared file that
materialised as a real risk — Track B edited it to register its router; Lane A
did not need it and did not touch it.

**Naming-contract check across the lane boundary (coordinator duty):** Track B's
`system_event_port.py` is contract-only, names Wagle in prose, carries **no**
`doran` runtime identifier, and explicitly defers binding to Lane A's Outbox
until Lane A passes independent QA. It uses `SERVICE_CODE = "markpoint"`, its
own service's existing registry value. Track B is therefore clean against the
PM's `wagle`-only rule for new identifiers, and its deferral means the
`owner_service` correction made here does not invalidate any Track B code.

**How the collision was handled:** Lane A's own database was restarted with **no
host port publish at all** — the runner shares the DB container's network
namespace, so the published port was never needed. Track B's container was left
untouched. This removes the collision at its source rather than by taking the
port back.

**Correction for the record:** Lane A's earlier `active.md`/relay entries state
Lane B is `NOT_STARTED` and that Lane B "must not use the root". The first is
now wrong and the second was already violated. Both are corrected in those
files. Lane A does not attempt to arbitrate Track B's placement — that is a PM
decision, surfaced here rather than acted on.

## 15. Wave 3 dependencies produced

The durable event exists and is stable. Wave 3 needs to build the consumer
(`claim_batch` already exists in `service_outbox.service`), the WebSocket
gateway, Push subscription/dispatch and reconnect-resume — none of which Wave 2
constrains beyond the envelope in §6. Each `D6-P` sub-task still requires its
own policy decision before it may start.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: three new source-backed rows for real executed tests.
- CLOSEOUT GATE: `PASS`

`CLOSEOUT GATE: PASS` covers documentation synchronization only. It is not
independent QA, not PM approval, and not parent-bundle completion — the bundle
stays open until Lane B finishes.
