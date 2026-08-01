# MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001

- Task ID: `MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001`
- Kind: Wave 3 execution bundle over existing Backlog rows (see §3)
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `2243aa83d3a0e527e83483651d10c2879026c704` (unchanged start → end)
- environment: repository root; disposable volume-less PostgreSQL 16.9; throwaway backend/frontend Docker images with container-only dependency trees; isolated Compose project `mc_phase1` for E2E
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
WAGLE_REALTIME_CORE_COMPLETE
WAGLE_RECOVERY_COMPLETE
WAGLE_DEVICE_PIN_COMPLETE
POLICY_DEPENDENT_PUSH_OR_UI_SLICE_DEFERRED
WAVE_3_CONDITIONAL
NOT_READY_FOR_WAVE_3_LIFECYCLE_CLOSEOUT
```

Core is implemented and executed: dispatcher, WebSocket gateway, multi-Family
subscription, resume/recovery, failure isolation, Push subscription lifecycle
and adapter, and the device PIN. What remains is **not** product defect — it is
`D6-P1`–`D6-P8`, all still undecided, plus a Wave 6 UI dependency. Both are
stated as blocks, not as work quietly skipped.

## 2. Git / Materialized Baseline

| | Start | End |
|---|---|---|
| branch | `dev-newmarkp` | `dev-newmarkp` |
| HEAD | `2243aa83d3a0e527e83483651d10c2879026c704` | same |
| worktree | clean | task-owned changes only |
| `git diff --check` | clean | clean |
| stash | 0 | 0 |
| commit/push/merge/rebase/PR | none | none |

The W2/W4 materialization commit is present (`2243aa8`), Wave 2 durable
messaging and Wave 4 Markpoint access are in the tree, frontend Wagle naming and
Naran retirement are done, and Alembic had a single head at `0008`.

## 3. Task-ID Mapping

**No new Backlog task was created and no existing ID was renamed.** The current
authoritative Backlog (`MONGLE_IMPLEMENTATION_BACKLOG.md`) already carries
**ten** Wave 3 rows; this execution ID is a bundle over them.

| Backlog ID | Prior status | This task |
|---|---|---|
| `MONGLE-W2-WAGLE-REALTIME-001` (Wave 3) | `BLOCKED_BY_DEPENDENCY` | **IMPLEMENTED** — dispatcher + gateway |
| `MONGLE-W3-WAGLE-RECONNECT-RESUME-001` | `BLOCKED_BY_DEPENDENCY` | **IMPLEMENTED** |
| `MONGLE-W3-WAGLE-MULTIFAMILY-SUBSCRIPTION-001` | `BLOCKED_BY_DEPENDENCY` | **IMPLEMENTED** |
| `MONGLE-W3-WAGLE-FAILURE-ISOLATION-001` | `BLOCKED_BY_DEPENDENCY` | **IMPLEMENTED** |
| `MONGLE-W3-WAGLE-PIN-LOCK-001` | `BLOCKED_BY_DEPENDENCY` | **IMPLEMENTED** |
| `MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001` | `DEFERRED` (**D6-P1**) | **PARTIAL** — see the conflict note below |
| `MONGLE-W3-WAGLE-PUSH-DEEPLINK-AUTHZ-001` | `BLOCKED_BY_DEPENDENCY` | **PARTIAL** — service-worker click routes to the event's own family; server re-authorization on arrival is Wave 6 UI |
| `-NOTIFICATION-SETTINGS-001` (D6-P2), `-PUSH-BUNDLING-001` (D6-P3), `-READ-DISPLAY-001` (D6-P4), `-PRESENCE-001` (D6-P5), `-MESSAGE-MUTATION-001` (D6-P6), `-RETENTION-001` (D6-P7), `-OFFLINE-QUEUE-001` (D6-P8) | `DEFERRED` | **NOT STARTED** — policy undecided |

**A conflict worth surfacing rather than resolving silently.** The Backlog says
`MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001` "must be decided before this task
starts", while this task's directive says to build the subscription lifecycle
and adapter and keep only the payload policy-blocked. The directive is the
newer instruction and its narrowing honours the Backlog's actual concern
(payload disclosure), so it was followed: lifecycle and transport exist, and
`build_payload()` emits identifiers only. PM should confirm the Backlog row's
status rather than leave the two records disagreeing.

## 4. Writer / File Ownership

Registered as the active writer in `relay/current.md` before the first product
edit. No other writer was active. Shared files were touched minimally:
`app/main.py` (router + pump), `app/models/all_models.py`, `app/config.py`,
`service_outbox/service.py` and `workers/service_outbox.py` (both for measured
defects — §26), `httpClient.ts` (measured regression), `nginx.conf`,
`eslint.config.js`, `generated/openapi.d.ts`. **No Markpoint Mission/Ledger
product code was modified.**

## 5. Authoritative Inputs

`AGENTS.md`, `CLAUDE.md`, `agent-system/rules.md`, `active.md`,
`relay/current.md`, `graduated/2026-08.md`,
`MONGLE_IMPLEMENTATION_BACKLOG.md`, `MONGLE_TARGET_DECISION_FREEZE.md`,
`MONGLE_REALTIME_MESSAGING_CONTRACT.md`, `MONGLE_TARGET_API_INVENTORY.md`,
plus the Wave 2/4 source itself (`wagle/models.py`, `wagle/service.py`,
`service_outbox/*`, `workers/service_outbox.py`, `family/*`).

## 6. D6-P1–P8 Status

Read from the current SSOT, not inferred:

```text
D6-P1 Push 본문 공개 수준     : DEFERRED  (undecided)
D6-P2 Room mute/알림 설정     : DEFERRED
D6-P3 Push 묶음/foreground 억제: DEFERRED
D6-P4 읽음 표시 방식          : DEFERRED
D6-P5 presence/last-seen      : DEFERRED
D6-P6 메시지 수정·삭제        : DEFERRED
D6-P7 보존 기간               : DEFERRED
D6-P8 오프라인 발신 Queue     : DEFERRED
```

**Not implemented because policy is undecided** — and deliberately not
approximated: message body in a Push payload, per-room mute defaults, Push
batching rules, presence/last-seen disclosure, edit/delete, retention deletion,
offline send queue, and any user-facing `DELIVERED` state.

**Implemented because it is policy-independent**: the dispatcher, WebSocket
authentication, room authorization, per-room ordered delivery, resume/recovery,
duplicate-replay protection, failure isolation, the Push subscription port and
adapter contract, and the device PIN.

The payload seam is a single function, `push_service.build_payload()`, marked
`PAYLOAD_POLICY = "IDENTIFIERS_ONLY_PENDING_D6_P1"`, and a test asserts no
content key can appear. Both the fixture and production paths call it, so a
test payload cannot quietly become the default.

## 7. Existing Capability Audit

Searched, then read the source — not assumed:

| Capability | Finding |
|---|---|
| Durable message, room-local sequence, read cursor | `TARGET_REUSABLE` — Wave 2. Reused as-is; **no second message/cursor table was created.** |
| Transactional Outbox with claim/lease/backoff/DEAD | `TARGET_REUSABLE` — `service_outbox`. Reused, with one defect fixed (§26). |
| WebSocket / connection manager | `MISSING` — only two comments saying it is Wave 3. |
| Push subscription / webpush | `MISSING`. |
| Service worker | `MISSING` — `manifest.json` existed, no `sw.js`. |
| Resume cursor / delivery attempt | `MISSING`. |
| Device PIN | `LEGACY_ONLY` — `auth.models.pin_hash` is the legacy MarkPoint **player login** credential. Deliberately **not** reused: sharing it would turn a screen lock into a credential. A test asserts the two stay in separate tables. |

## 8. Deployment Topology

Measured, and it changed the design:

```text
docker-compose.yml       backend: uvicorn (1 process) + separate `service_outbox` worker
docker-compose.prod.yml  backend: uvicorn --workers 2
docker-compose.phase1.yml backend: uvicorn (1 process)   [E2E]
```

Production is **multi-process**, so an in-memory registry alone cannot be
declared complete — and it is not. The design is:

- `RealtimeFanoutPort` (seam) + `InProcessFanout` (v1 implementation).
- The dispatcher also runs **inside the web process** (`main.py` lifespan pump)
  so a locally-connected client is notified promptly.
- Every connection additionally runs a **durable catch-up** against
  `resume_missed_events()` on its own cursor.

The consequence, stated plainly: under `--workers 2` a message committed on
worker A does not fan out to a client on worker B *instantly*, but it is **not
lost** — the catch-up delivers it within `WAGLE_REALTIME_CATCHUP_SECONDS`
(default 5s). Correctness holds; latency degrades. Closing that gap needs a
cross-process channel (PostgreSQL `LISTEN/NOTIFY` or a broker); **no
infrastructure was introduced**, because no approved document selects one.
Recorded as a residual decision, not silently absorbed.

## 9. Schema Delta

Three tables, and three deliberate absences.

**Added** — `wagle_push_subscriptions` (Account+device owned, never
Family-duplicated), `wagle_push_delivery_attempts` (unique
`(outbox_event_id, subscription_id)` = delivery idempotency + per-endpoint
failure isolation), `wagle_device_pins` (unique `(account_id, device_id)` =
device isolation).

**Not added, on purpose** — no message/sequence table (Wave 2 owns it), no
realtime cursor table (resume is a query over the durable sequence; a parallel
cursor could disagree with the read state it shadows), no Family-scoped Push row
(the subscription owns the device, the event carries the Family).

## 10. Migration

`0009_wagle_realtime_push_pin` — id kept short because
`alembic_version.version_num` is `varchar(32)` and a 36-char id silently rolled
back in Wave 1.

```text
alembic heads            -> 0009_wagle_realtime_push_pin (head)   [single]
fresh 0000 -> head       -> PASS
downgrade -1             -> 0008; residual tables 0, residual indexes 0
re-upgrade               -> 0009; all 3 tables restored
constraints created      -> 2 partial unique (push), 1 unique (attempt),
                            1 unique (device pin), 2 CHECK, 3 index
```

D8 RESET honoured: no legacy PIN, message or notification row is backfilled.

## 11. Dispatcher

`wagle/realtime_dispatcher.py` + `workers/wagle_realtime.py`.

- **Claim** — reuses `claim_batch` (`FOR UPDATE SKIP LOCKED`), now filtered by `owner_service` (§26 defect 1).
- **Lease/recovery** — a worker that dies mid-delivery has its lease expire and its rows re-claimed. Asserted.
- **Retry** — reuses the existing bounded exponential backoff → `DEAD`; no second retry scheme.
- **Idempotency** — domain (one message per `client_message_id`) and delivery (one Push per event+endpoint) are kept separate and both asserted by running the operation twice.
- **Failure isolation** — per event, per Family, per endpoint; one bad row/endpoint never stops the batch.
- **The message is never touched.** A forced fan-out failure is asserted to leave `wagle_messages` intact and the Outbox row `PENDING` with `attempt_count=1`.

## 12. WebSocket Authentication

`/api/me/wagle/ws`. Account-native Session only: the token must decode as an
Account token, name a live Session, agree with the Account it claims, and the
Account must be active. Asserted denials: no token, **legacy player JWT**,
revoked Session, suspended Account. The token travels as a query parameter
because the browser WebSocket API cannot set headers — which is why all four
checks are re-done server-side rather than trusting the handshake.

## 13. Subscription / Family Isolation

Account-scoped, not Family-scoped: one logical subscription spans the whole
server-derived `AuthorizedFamilySet` (D1). `activeFamilyId` from the client is
never an authorization input — a spoofed `family_id: 99999` is denied.

Every subscribe re-derives three independent things (ACTIVE membership → room
exists *in that family* → ACTIVE participant), all raising the same
`PermissionError` so a caller cannot distinguish "no such room" from "not
allowed" and confirm another family's room exists.

Multiple physical sockets per Session are supported and asserted (2 sockets, 2
deliveries) — the Realtime Messaging Contract forbids an invariant against them.

Revocation is asymmetric by design and by test: **Session revoked → every
connection closes; one Family's membership ended → only that Family's
subscriptions go, every other Family keeps working.**

## 14. Resume / Recovery

`resume_missed_events()` — the same query the live path resolves against, so
"live" and "recovered" cannot render differently.

Asserted: ascending room order, replay-safe (running it twice is identical),
pagination via `has_more` rather than silent truncation, cross-family denial,
and — a case that is easy to miss — **a participant added late cannot read the
room's history from before it joined** by resuming from 0.

The client mirrors this: per-room cursor, dedup on `message_id`, gap detection
when a sequence jumps past `cursor + 1`, and `primeCursor()` so history the UI
already loaded is not re-emitted as new after a reconnect.

## 15. Push Subscription / Delivery

Lifecycle asserted: register/replace per device; re-registering the **same
endpoint under another Account revokes the first** (the Account-switch case);
revoke per device (logout/unlink) and per Account (suspension); `410` expires
only that subscription; a transient failure does **not** expire it; delivery is
idempotent per `(event, endpoint)`.

The API never echoes `endpoint`, `p256dh_key` or `auth_secret` — together they
are a capability to push to that browser, and the client already has them.
Asserted on the serialized response body.

Transport is a port with a `NullPushTransport` default. **No external push
service is contacted in any test.**

## 16. Wagle Device PIN

Account+device scoped, bcrypt-hashed (reusing the Account credential hashing,
so there is one security posture rather than two), attempt-limited with a
temporary lock, reset-not-recovery.

Asserted: the hash is never the PIN and is never returned; there is no
`get_pin`/`read_pin` function at all; a correct PIN does **not** bypass an
active lockout; locking one device leaves the Account's other device usable;
reset clears the lockout and bumps `pin_version` so a stale client "unlocked"
flag cannot survive; format follows config, not a hard-coded policy; it is not
Family-scoped; it does not reuse the legacy player PIN; **and a lockout leaves
the Account active and Push subscriptions intact.**

## 17. Frontend Integration

`wagleRealtimeClient.ts` (connect, backoff reconnect, re-subscribe with cursors,
resume paging, dedup, gap detection), `useWagleRealtime.ts`,
`wagleDeviceApi.ts`, `WaglePinLock`, and `public/sw.js`.

**Honest scope boundary.** `WagleLanding` still renders **preview fixtures**,
not API rooms. Wiring those is `MONGLE-W5-TARGET-UI-001` (Wave 6), whose own
Start Gate forbids claiming integration while rendering from fixtures. So the
socket connects and its state is real and observable, but it subscribes to zero
rooms — there are no real room ids on this screen yet. This is why no
message-level realtime UI journey is claimed in §24.

The service worker shows **no message content**: `D6-P1` is undecided, the
server sends identifiers only, and the worker does not render a body even if one
arrived — the policy is enforced on both ends rather than trusted from one.

## 18. API / OpenAPI

7 new personal routes under `/api/me/wagle/*` (D7: personal, not family
property) plus one family-scoped `/rooms/{room_id}/resume`. Regenerated from the
live schema: **116 paths, doran 0, naran 0**; `openapi.d.ts` regenerated, `tsc`
EXIT=0.

## 19. Test Environment

Backend: throwaway image from `requirements-dev.txt`, disposable volume-less
PostgreSQL 16.9 seeded with `database/init.sql` (`psql -v ON_ERROR_STOP=1`,
readiness proven by three consecutive queries) and migrated to head.
Frontend: `mongle-frontend-toolchain` for typecheck/lint, throwaway image for
the clean build. E2E: isolated `mc_phase1` with the current-source fingerprint
guard from the previous task.

## 20–24. Results

```text
backend collected                 : 228
backend passed                    : 228   (0 failed)   [was 173 before Wave 3]
  new Wave 3 realtime/push/PIN    : 40
  new WebSocket gateway           : 15
migration fresh/downgrade/re-up   : PASS, single head 0009
frontend tsc --noEmit             : EXIT=0
frontend eslint                   : clean
clean isolated production build   : PASS
  artifact doran 0 / naran 1 (migration source) / wagle 27
playwright (isolated mc_phase1)   : 125 collected, 121 passed, 0 failed,
                                    4 skipped, 0 retries
```

WebSocket results are from **the real handler coroutine** driven by a scripted
socket — same auth, same subscribe/resume loop, same registry; only network
framing is stubbed, and the reason is recorded in the test file (TestClient runs
the app in another event loop from the asyncpg connections). Browser framing is
covered by Playwright.

**NOT_RUN, stated as such:**

| Scope | Reason |
|---|---|
| Browser Web Push end-to-end | Needs VAPID keys and a real push service; neither exists in the isolated stack. Delivery is covered by the adapter tests. **Not reported as PASS.** |
| Message-level realtime UI journey (send here → receive there) | `WagleLanding` renders preview fixtures; real room wiring is Wave 6. |
| Multi-worker cross-process fan-out latency | Requires a broker decision (§8). Correctness under multi-worker is covered by the durable catch-up; the latency path is not exercised. |

## 25. Regression

Wave 1 Account/Session/RBAC, Wave 2 durable messaging, Wave 4 Markpoint access
and the ServicePrincipal → Wagle relay all pass inside the 228. Naming gates:
active frontend Doran 0, `'doran'` literal 0, generated OpenAPI doran 0, active
`/naran` route 0, active Naran storage write 0, backend active naran 0. The one
remaining backend `doran` occurrence is a prohibition comment ("no `doran`
fallback"), an allowed category.

## 26. Defects Found / Corrected

**1. Outbox claim ignored `owner_service` — latent Wave 2/4 defect, HIGH.**
`claim_batch` claimed every pending row, and `workers/service_outbox.py`
processed all of them. Once Wave 2 began writing `owner_service="wagle"` rows,
that Worker would claim a human message's delivery event, provision a bogus
`wagle` ServicePrincipal and canonical binding, fail the action allowlist, and
retry the row to `DEAD` — losing the delivery event for a message that is itself
intact. Fixed by filtering at the claim (releasing after claiming would still
stall the other consumer for a lease). Regression test asserts the foreign row
stays `PENDING` and that zero `wagle` ServicePrincipals are created.

**2. `record_failure` broke on its own failure path — latent Wave 2 defect,
HIGH.** Every caller reaches it from an `except` block that just called
`db.rollback()`, which expires attached instances; touching `attempt_count` then
triggered a lazy reload and raised `MissingGreenlet`. The failure handler
itself failed, leaving the row `PROCESSING` until its lease expired instead of
being scheduled for retry. Fixed with a refresh, in the shared helper so both
Workers get it. Found by testing the dispatcher's failure path.

**3. An optional-feature probe could log the user out — introduced here, caught
by E2E.** The PIN gate calls `/api/me/wagle/device-pin`; a legacy-player session
gets 401; the global interceptor treated that as an expired session and
redirected to `/`. Entering Wagle logged the user out. Fixed by exempting
`/api/me/wagle/` from the global logout: an optional feature must never be able
to end a session. E2E regression test added.

**4. Realtime client reconnected forever on a terminal refusal — introduced
here, caught by E2E.** A 4401 close was treated as a network blip, so every
browser with a non-Account session reopened the socket every 500 ms→15 s
indefinitely. Fixed: `unauthorized` is terminal. E2E asserts it stays settled.

**5. nginx did not proxy the WebSocket upgrade, and the 32 KB ingress rule still
matched the retired name — pre-existing deployment defects.** Without the
upgrade map the handshake never reached the backend and the browser saw an
ordinary 1006 close, which is what surfaced defect 4. Separately,
`location ~ ^/api/families/[^/]+/doran/service/actions$` was left behind by
migration `0007`, so the proxy-side body cap silently stopped applying to the
route it protects. Both fixed; `/sw.js` also given no-cache so a stale worker
cannot outlive its source.

**6. A pinned `count(*) == 7` assertion was fragile and weak.** Wave 3 legitimately
added three `wagle%` tables. Replaced with an explicit named set — **stronger**
(any seven tables satisfied the count) and stable as the domain grows. Not a
weakening: the claim it makes is larger than before.

Also corrected: four of my own test-setup bugs (fabricated FK ids, an invalid
membership status, a synthetic session id, a fabricated room id) — each is noted
in the test file where it happened, because each one initially looked like a
product failure and was not.

**Remaining: 0 known product defects.**

## 27. Recursive Review

**Pass 1 (before).** Read the Wave 2 source rather than its reports; found the
Outbox is genuinely reusable and that no realtime/Push/PIN code exists; measured
`--workers 2` in prod, which forced the port/adapter split; confirmed the legacy
`pin_hash` must not be reused.

**Pass 2 (after backend).** DB stays SSOT (envelope carries identifiers only);
message untouched on delivery failure (asserted); at-least-once with both
idempotency kinds separated; per-room ordering with no global counter;
Family isolation and asymmetric revocation asserted. Found defects 1 and 2 here.

**Pass 3 (after frontend).** `activeFamily` is not an authorization input;
reconnect restores the whole subscription set with cursors; dedup on
`message_id`; PIN does not block Session/Push/other services. Found defects 3
and 4 here — both only visible by running the E2E, not by reading.

**Pass 4 (after tests).** No unexecuted test is reported as PASS (§20–24 lists
three NOT_RUN scopes); 0 retries configured and 0 occurred; E2E ran against a
fingerprint-verified current-source image; Docker residual 0; OpenAPI
regenerated from the live schema; Coverage Map updated.

## 28. Five-Gate Review

- **환각** — every count is a command result from this session; the existing-capability audit is from reading source, not reports; no `exactly-once` claim anywhere; D6 policies recorded as `DEFERRED` from the SSOT, not assumed approved.
- **누락** — dispatcher, WS auth, room authorization, multi-Family, resume/recovery, duplicate replay, Session revoke, Membership revoke, Push lifecycle, failure isolation, PIN, frontend, migration, OpenAPI, Playwright: all present.
- **오작업** — transport never SSOT; nothing published before the DB commit; no global ordering; no user-facing `DELIVERED`; one Family's revocation never ends the Session; PIN never replaces login and never blocks Push or Markpoint; no legacy PIN backfill; no Doran/Naran revival; no Markpoint product code touched; no broker introduced.
- **축혼동** — kept distinct: durable message vs realtime transport vs Push; read cursor vs resume cursor; transport ACK vs user-facing state; Account Session vs device PIN; current Target vs historical legacy vs deferred policy.
- **신선도·오탈자** — real HEAD `2243aa8`, real Alembic head `0009` (single), OpenAPI current, no duplicate Task ID created, `git diff --check` clean.

## 29. Changed-file Manifest

**New (10)** — `wagle/realtime.py`, `wagle/realtime_models.py`,
`wagle/realtime_dispatcher.py`, `wagle/realtime_router.py`,
`wagle/push_service.py`, `wagle/device_pin_service.py`,
`workers/wagle_realtime.py`, `alembic/versions/0009_wagle_realtime_push_pin.py`,
`tests/test_wagle_realtime_wave3.py`,
`tests/test_wagle_websocket_gateway_wave3.py`
**New frontend (6)** — `wagle/realtime/wagleRealtimeClient.ts`,
`wagle/realtime/useWagleRealtime.ts`, `wagle/realtime/wagleDeviceApi.ts`,
`wagle/components/WaglePinLock/{WaglePinLock.tsx,.module.css,index.ts}`,
`public/sw.js`, `tests/e2e/specs-mongle/02-wagle-realtime.spec.ts`
**Modified (10)** — `app/main.py`, `app/config.py`, `app/models/all_models.py`,
`service_outbox/service.py`, `workers/service_outbox.py`,
`tests/test_integration_wagle_markpoint.py`, `frontend/nginx.conf`,
`frontend/eslint.config.js`, `shared/api/httpClient.ts`,
`platform/pages/WagleLanding.tsx`, `main.tsx`,
`wagle/components/index.ts`, `generated/openapi.d.ts`

## 30. Residual Policy Blocks

```text
D6-P1..P8                     : UNDECIDED — 7 Backlog rows not started
Push payload disclosure       : POLICY_BLOCKED (seam implemented and tested)
Browser Web Push E2E          : BLOCKED — no VAPID key / push service
Realtime UI message journey   : BLOCKED_BY_WAVE_6 (MONGLE-W5-TARGET-UI-001)
Multi-process fan-out latency : DECISION_REQUIRED (broker vs LISTEN/NOTIFY)
Backlog row status conflict   : PM to confirm MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001
```

## 31. Lifecycle Status

`IMPLEMENTED_AWAITING_INDEPENDENT_QA` / `WAVE_3_CONDITIONAL`. Nothing graduated.

## 32. Final Verdict

```text
WAGLE_REALTIME_CORE_COMPLETE
WAGLE_RECOVERY_COMPLETE
WAGLE_DEVICE_PIN_COMPLETE
POLICY_DEPENDENT_PUSH_OR_UI_SLICE_DEFERRED
WAVE_3_CONDITIONAL
NOT_READY_FOR_WAVE_3_LIFECYCLE_CLOSEOUT
```

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
