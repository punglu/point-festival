# Doran Foundation Draft Gap Analysis Against R2

**Status:** ARCHITECTURE EVALUATION / no implementation authorization (2026-07-26)
**Evidence scope:** read-only QA and isolated-draft handoff evidence. The draft
at `/Users/mac/mac_Project/minecraft_points_festivals_doran_foundation_draft`
remains `SUSPENDED / QA_FAILED / UNCOMMITTED / UNPUSHED` and was not modified
for this analysis.

Status meanings: `MATCH` is reusable subject to tests; `PARTIAL` needs bounded
change; `CONFLICT` violates R2; `MISSING` is absent; `QA_FAILED` has a proven
failure and cannot be accepted as-is.

**R2-B1 addendum (2026-07-26):** Service Principal and Service–Room Binding
were implemented separately from this draft, in an isolated worktree, and
independently QA-passed (`PHASE2-DORAN-R2B1-FOCUSED-QA-001` = PASS: credential
security, permission boundary, real-PostgreSQL idempotency/concurrency
including an 8-worker concurrent replay with zero HTTP 500 and one converged
message, DB CHECK/unique-index integrity, and a full `0002→0003→0002→0003`
migration cycle with zero residue). Rows 30 and 31 below are updated to
reflect this; the rest of this document's draft evaluation is unchanged.

**R2-B2 addendum (2026-07-26):** the Reliable Service Slice closed the R2-B1
gaps this document had left open - a generic Transactional Outbox, one real
owning-service integration (Mark Point mission completion), a dedicated
Worker, SERVICE Room self-onboarding, the 32KB ingress body limit, a
credential-timing mitigation, and a PostgreSQL trigger backstop for
Binding/Room integrity - plus a full Mark Point -> Outbox -> Worker -> Doran
-> user-visible-message E2E path. Self-test PASS (28/28 required items,
backend 67/67, Playwright 9/9, Naran Shell 25/25, migration cycle
`0003→0004→0003→0004` zero residue); independent QA is still pending before
merge (see the Outbox operations memo and API contract sections below). Rows
39-42 are updated accordingly.

| Requirement | Current draft evidence | Status | Reusable | Required change | Risk / test required |
| --- | --- | --- | --- | --- | --- |
| Family-scoped Room and composite Family boundary | migration/router QA passed Family scope and cross-Family denial | MATCH | yes | retain only after R2 naming/permission review | PostgreSQL IDOR regression |
| canonical DIRECT pair and concurrent creation | partial unique pair and QA simultaneous requests converged | MATCH | yes | define archive/reopen behavior before API acceptance | real PostgreSQL concurrent create |
| self/cross-Family DIRECT denial | QA observed denials | MATCH | yes | keep server-derived current Membership | authorization matrix |
| Room-local sequence | atomic allocation and eight concurrent sends had unique order | MATCH | yes | ensure all error paths avoid user-visible 500 | concurrent send/load test |
| participation-period visibility | join/left/removed model exists, but comprehensive automated coverage absent | PARTIAL | conditional | complete exact left/rejoin/read-state rules and tests | API/DB visibility matrix |
| TEXT tombstone | author TEXT tombstone observed; body hidden | PARTIAL | conditional | align response sender-display and active-author policy | tombstone/idempotent-delete tests |
| subscription read-only | history/read observed, write denied | PARTIAL | conditional | apply to every mutation including delete/Room management | active/suspended/cancelled matrix |
| concurrent user idempotency | same payload/key produced HTTP 201 plus HTTP 500 after DB uniqueness conflict | QA_FAILED | no | recover/requery in a valid UoW and return existing message | simultaneous same-key HTTP/PostgreSQL test |
| changed-payload idempotency | sequential retry returned 409 | PARTIAL | conditional | make canonical-payload comparison race-safe | concurrent conflict/no-mutation test |
| migration downgrade | `0002 → 0001` left Doran permissions, roles, and mappings | QA_FAILED | no | delete registry data reversibly or explicitly block downgrade with assignments | real PostgreSQL upgrade/downgrade/re-upgrade/catalog test |
| PostgreSQL integration suite | draft contains primarily rules tests; QA had to construct separate runtime | MISSING | no | deterministic isolated fixture plus API/DB/concurrency suites | repeatable setup/run/cleanup |
| `doran.*` registry naming | draft/initial materials contain `messaging.*` references | CONFLICT | no | use only `doran.*`; historical names must not create registry entries | registry/migration catalog test |
| `doran_*` schema naming | draft uses `conversation_*` table model | CONFLICT | no | rename/rebase schema under approved migration plan; do not dual-write | migration compatibility review |
| `room_admin` role | draft uses room owner/admin terminology | CONFLICT | no | replace Room role naming; keep Family owner distinct | permission/role API test |
| Platform operator boundary | no complete Platform role model | MISSING | no | specify/implement no-bypass boundary separately | independent authorization QA |
| Service Principal and Binding | R2-B1 implemented (`ServicePrincipal`, `DoranServiceBinding`, `SERVICE_ACTION` ingress, migration `0003`); independent QA PASS | MATCH | yes | Principal/Binding management HTTP API deferred pending Platform Operator auth (PM-approved) | scope/impersonation tests passed (cross-service, cross-Family, inactive binding/subscription, non-SERVICE room) |
| service event idempotency/outbox | R2-B2: generic `service_outbox_events` Outbox (PENDING/PROCESSING/PUBLISHED/DEAD, bounded retry+backoff, `FOR UPDATE SKIP LOCKED` claim) + dedicated Worker (`app/workers/service_outbox.py`) wired to one real owning service (Mark Point `mission.completed`); self-tested for rollback-atomicity, retry-no-duplicate, concurrent-claim safety, lease recovery, and publish-then-crash convergence | MATCH | yes | none for this slice; a second owning service is just a new `ALLOWED_ACTIONS_BY_OWNER` entry | independent QA of Outbox failure-recovery and DB integrity (R2-B2 focused QA) |
| audit and privacy controls | R2-B1 audit log (secret/token/body-free) confirmed by QA; R2-B2 adds no new audit surface (Worker calls the same audited `publish_service_action`) | MATCH | yes | none | none additional |
| resource limits | R2-B2: 32KB application-level Doran Service ingress cap (streamed, not Content-Length-trusting) + matching nginx path-scoped `client_max_body_size`; full-request-size policy for any *other* future endpoint remains unset | PARTIAL | yes (Service ingress) | Approve limits for any future attachment/upload API separately - this cap is intentionally not global | boundary tests passed (at/over 32KB, length-unaware stream) |
| Dock preference backend | absent | MISSING | no | Account+Family preference and optimistic version | multi-device conflict tests |
| WebSocket/Push/UI timeline | intentionally absent | MISSING | no | later realtime/UX phases | cursor/revoke/performance QA |

## Known implementation failures

1. **BLOCKER — concurrent client idempotency.** Identical concurrent user sends
   created one DB message but returned `201 + 500`; QA traces the latter to an
   IntegrityError rollback followed by expired SQLAlchemy object access
   (`MissingGreenlet`). This breaches the required retry contract.
2. **HIGH — incomplete downgrade.** The schema objects were dropped but Doran
   permission, role, and role-permission registry data remained after downgrade.
3. **HIGH — missing automatic API/DB coverage.** DIRECT race, idempotency race,
   sequence race, cross-Family/participant lifecycle, read-state monotonicity,
   subscription state, and no-mutation denial checks were not covered by a
   deterministic in-repository PostgreSQL suite.

## Reuse decision boundary

No code in the isolated draft is approved for merge by this document. After PM
approval, Foundation R2-A starts with a file-by-file reuse decision, canonical
namespace migration design, deterministic PostgreSQL test harness, and repair
of both QA failures before new capability work.

## Contract validation passes

| Pass | Verdict | Basis |
| --- | --- | --- |
| 1. Names and namespace | PASS | R2 canonically specifies `doran.*`, `doran_*`, and `room_admin`; draft conflicts are classified |
| 2. Authority separation | PASS | Platform, Family, Room, Service, and Dock are explicitly non-transitive |
| 3. Message integrity | CONDITIONAL | R2 is explicit; draft concurrent idempotency remains QA_FAILED |
| 4. Performance and sync | PASS | cursor, virtualization, cache, cleanup, reconnect, and QA requirements are contractual and deferred |
| 5. Service Dock | PASS | seed, zero Dock, all-services entry, Account+Family SSOT, and conflict boundary are explicit |
| 6. Stale/implementation claims | PASS | isolated draft is labeled partial/failed; no deferred feature is claimed delivered |

## PM decisions recorded after R2 canonicalization

| Topic | Approved decision | Delivery boundary |
| --- | --- | --- |
| R2-A limits | TEXT 4,000 characters; page default 50/max 100; GROUP Participants 50; `client_message_id` 64 | enforce in R2-A configuration/validation |
| rate/WebSocket limits | determine from R2-B/Realtime measurement | deferred; no unbounded delivered endpoint |
| DIRECT lifecycle | archive hides; reopen same canonical Room/history; deny reopen if a counterparty left/was removed | R2-A |
| Service Action | versioned allowlist; minimum display snapshot + owning-service reference; source-event replay defence | R2-B; Service Principal/Outbox excluded from R2-A |
| retention/legal hold/break-glass | all deferred; no operator body access; no legal-hold/E2EE claim | deferred pending separate PM policy |
| Dock conflicts | integer version + required `expected_version`; mismatch 409; reload/reapply/retry; no automatic last-write-wins | R2-B/Frontend UX |

The remaining implementation-level choices are configuration wiring and API
shape consistent with these decisions, not unresolved product-policy gates.

## R2-B2 Outbox operations memo

**Running the Worker.** `python -m app.workers.service_outbox` from `backend/`
(env vars as for the API process). In `docker-compose.yml` it is the
`service-outbox-worker` service, sharing the backend image, one process -
running more than one replica is safe (see concurrency note below) but is not
required for this slice's volume.

**Claim.** Each tick claims up to 10 rows via `FOR UPDATE SKIP LOCKED` -
PENDING rows due for (re)attempt, plus PROCESSING rows whose 30s lease
expired (a Worker died mid-delivery). No process-local lock anywhere; running
multiple Worker replicas concurrently is safe by construction and is
self-tested (`test_outbox_07_two_workers_no_double_claim`,
`test_outbox_08_expired_lease_recovered`).

**Retry and backoff.** `compute_backoff_seconds(attempt) = min(30 * 2^(attempt-1), 3600)`
(30s, 60s, 120s, ... capped at 1h). After `MAX_ATTEMPTS = 8` the row moves to
`DEAD` and stops being retried. `last_error_code` records a short tag (e.g.
`http_404`, `worker_error`) - never a full exception message, payload, or
credential.

**DEAD rows.** There is no automatic requeue path in this slice - an
operator reviewing `service_outbox_events WHERE status = 'DEAD'` and deciding
whether to manually flip a row back to `PENDING` (after fixing whatever made
delivery permanently fail - e.g. activating a Family's Doran subscription) is
a deliberate Human Gate, not an oversight. Automating this is an R2-B3
candidate once real DEAD-rate data exists.

**Delivery guarantee.** At-least-once from the Worker's side; Doran's own
`source_event_id` idempotency (R2-B1) makes the visible result exactly-once.
A Worker crash between "Doran committed the message" and "Outbox row marked
PUBLISHED" is not a bug: the next attempt reuses the same stored
`source_event_id`, gets the same message back from Doran, and marks the row
PUBLISHED - see `test_outbox_09_and_10_publish_then_crash_then_converges`.

**Adding a second owning service.** Add one entry to both
`ALLOWED_ACTIONS_BY_OWNER` and `PRINCIPAL_DISPLAY_NAME_BY_OWNER` in
`app/workers/service_outbox.py`, and call `service_outbox.service.enqueue_event`
from that service's own confirmation transaction (see Mark Point's
`_emit_mission_completed_event` in `mission/service.py` for the reference
shape). No Worker, Outbox, or Doran code changes are needed.

**Known gap, stated plainly:** only `mission/service.py`'s single-mission
`update_mission_status` -> `completed` transition is wired to the Outbox.
`bulk_approve_missions` (the Admin "일괄 승인" bulk path) confirms points via
a bulk `UPDATE` that never loads individual `Mission` rows and is **not**
wired to the Outbox in this slice - completing missions through bulk-approve
today produces no Doran event. Closing this requires either looping
per-mission enqueue calls after the bulk `UPDATE ... RETURNING`, or a
deliberate product decision that bulk-approved missions are digested
differently; treat this as an R2-B3 decision point, not an accidental defect
in the code delivered here.

## R2-B2 API and payload contract for the next UI step

These two endpoints are the only Doran surface the next UI Slice needs; both
already exist and are self-tested end-to-end.

**Self-onboarding** (user JWT, once per Family member before they can see the
service's Room):
```
POST /api/families/{family_id}/doran/services/{service_code}/room
-> 200 ServiceRoomOnboardResponse { room_id, family_group_id, service_code,
                                     participant_id, room_role, status, joined_sequence }
```
Idempotent (repeat calls return the same `participant_id`, never a second
Participant row). 403 if the caller's Family membership/Doran permission/Doran
subscription isn't active; 404 if this service has no active Binding for this
Family yet (i.e. nothing to onboard into).

**Reading messages** (existing R2-A endpoint, unchanged - `SERVICE_ACTION`
items are already mixed into the same list a Room's TEXT messages come from):
```
GET /api/families/{family_id}/doran/rooms/{room_id}/messages
-> item.message_type == "SERVICE_ACTION"
   item.service_code == "mark-point"
   item.service_payload == { action_type: "mission.completed",
                              snapshot: { mission_id, mission_title, player_id,
                                          player_display_name, awarded_points,
                                          completed_at } }
```
`service_payload.snapshot` is exactly Mark Point's display-minimum snapshot -
stable field names the next UI Slice can render directly, e.g. `"{player_display_name}가 '{mission_title}' 미션을 완료하고 {awarded_points}P를 받았습니다."`
This is a payload-shape preview only, not approved UI copy.
