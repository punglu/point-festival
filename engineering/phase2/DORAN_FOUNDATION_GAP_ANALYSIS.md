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
| service event idempotency/outbox | consumer-side `source_event_id` idempotency implemented and QA-passed (sequential + 8-worker concurrent replay, conflicting-payload 409); producer-side Transactional Outbox still absent | PARTIAL | yes (idempotency) / no (outbox) | Transactional Outbox and owning-service delivery integration | R2-B2: outbox delivery-guarantee and failure/replay tests |
| audit and privacy controls | no complete audit design/implementation | MISSING | no | R2-B audit without body/credential leakage | audit redaction tests |
| resource limits | no approved resource-limit implementation | MISSING | no | approve values then enforce page/body/rate/caps | boundary/load tests |
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
