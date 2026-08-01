# MONGLE-W1-START-GATE-AND-DB-CONTRACT-VERIFICATION-001

- Task ID: `MONGLE-W1-START-GATE-AND-DB-CONTRACT-VERIFICATION-001`
- Task Type: READ-ONLY START GATE / DB CONTRACT VERIFICATION
- Target: Mongle Wave 1
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `da7ea7403aefef33a90d622940724b0c53ee8873`
- environment: local worktree `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; read-only (file reads, grep, `git show`/`log`/`diff`, `alembic heads`/`history` only — no DB connection, no Docker, no migration execution)
- secrets_redacted: `true`

> **PM 판정 접수 및 정정 (2026-08-01) — 본문을 읽기 전 §25 PM Correction
> Addendum을 먼저 확인할 것.** PM이 이 검증 결과를 `CONDITIONAL — ACCEPTED`로
> 접수하면서 본 보고서의 readiness 표현 1건과 Task 판정 1건을 정정했다.
> 원문 프로즈는 증거 보존을 위해 수정하지 않고 그대로 두며, 정정 내용은
> §25에 기록한다. §19의 판정표 중
> `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` 행과 §1/§22의
> "즉시 구현 가능" 표현은 §25에 의해 **superseded**된다.

## 1. Executive Verdict

```text
WAVE_1_START_GATE_CONDITIONAL
DB_CONTRACT_REQUIRES_CORRECTION
NOT_READY_FOR_FULL_WAVE_1
```

All 5 Wave 1 `READY_FOR_IMPLEMENTATION` tasks are real, correctly scoped, and
their named D-decisions are `APPROVED`. Direct source reads (Section 5)
confirm the documents' own "NOT_IMPLEMENTED" claims are accurate — there is
**no** Account-native Credential or Session table, and **no** Account-native
login path anywhere in the current codebase; every current auth mechanism is
legacy `player_id`/`admin_auth`-based. This matches, rather than contradicts,
what `MONGLE_TARGET_TABLE_DICTIONARY.md` and `MONGLE_TARGET_COLUMN_DICTIONARY.md`
already say. The blocker is not a false claim in the documents — it is that
the two schema sketches those documents provide are explicitly self-labelled
`VALID_HISTORICAL_REFERENCE`, **not an approved schema**, and are missing
elements the approved D3 contract itself requires (refresh-token mechanics,
per-device identity for device unlink). Physical schema design is correctly
deferred to the Wave 1 task itself — but that means a concrete Credential/
Session/Device table design does not yet exist anywhere, which is real,
un-invented implementation work standing between "decisions frozen" and
"code can be written." This is a `NEEDS_DICTIONARY_COMPLETION`-class gap, not
a `NEEDS_PM_DECISION` gap — no reopened decision is required, only schema
design work that Wave 1 itself is supposed to do at its own Start Gate.

Two of the five READY tasks (`MONGLE-W1-ACCOUNT-CREDENTIAL-001`,
`MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001`) cannot begin implementation until this
schema design step happens; the other three
(`MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001`,
`MONGLE-W1-SCOPED-RBAC-001`, `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001`) sit on
top of the existing, already-correct Account/FamilyGroup/FamilyMembership/
Role/Permission Foundation and are closer to ready, but functionally depend on
Credential/Session existing first for any real end-to-end test. See Section 19
for the exact per-task readiness call.

## 2. Environment / Git Baseline

| Command | Result |
|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` |
| `git branch --show-current` | `dev-newmarkp` |
| `git rev-parse HEAD` | `da7ea7403aefef33a90d622940724b0c53ee8873` |
| `git status --short --untracked-files=all` | 28 modified tracked files, 32 untracked entries — **identical set to the immediately prior verification task's baseline** (`MONGLE-FREEZE-DECOMPOSITION-INDEPENDENT-VERIFICATION-001`), plus that task's own report file now present as untracked. No new dirty state appeared between that task and this one. |
| `git diff --name-status` | unchanged from the prior verification (28 files; see that task's QA evidence file for the full hash-verified list — not re-derived here to avoid duplicate work) |
| `git diff --check` | clean |
| In-progress git operation (`MERGE_HEAD` etc.) | none |

Ownership of the pre-existing dirty state is not re-derived here since it was
already independently hash-verified in
`agent-system/qa/MONGLE-FREEZE-DECOMPOSITION-INDEPENDENT-VERIFICATION-001.md`
(Section 2 of that report) in this same session; this task adds no new
attribution claim, only confirms the diff set is unchanged.

## 3. Authoritative Documents

| Document | Path | Axis |
|---|---|---|
| Target Decision Freeze | `engineering/phase2/MONGLE_TARGET_DECISION_FREEZE.md` | `APPROVED_TARGET_CONTRACT` |
| Domain Boundary Map | `engineering/phase2/MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md` | `APPROVED_TARGET_CONTRACT` |
| Business Glossary | `engineering/phase2/MONGLE_TARGET_BUSINESS_GLOSSARY.md` | `APPROVED_TARGET_CONTRACT` |
| Table Dictionary (Target) | `engineering/phase2/MONGLE_TARGET_TABLE_DICTIONARY.md` | `APPROVED_TARGET_CONTRACT` + `CURRENT_IMPLEMENTATION_FACT` per row |
| Column Dictionary (Target) | `engineering/phase2/MONGLE_TARGET_COLUMN_DICTIONARY.md` | Same |
| API Inventory (Target) | `engineering/phase2/MONGLE_TARGET_API_INVENTORY.md` | Same |
| Role Matrix | `engineering/phase2/MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md` | `APPROVED_TARGET_CONTRACT` + open items |
| Epic/Feature Decomposition | `engineering/phase2/MONGLE_EPIC_FEATURE_DECOMPOSITION.md` | Planning |
| Dependency & Wave Plan | `engineering/phase2/MONGLE_DEPENDENCY_AND_WAVE_PLAN.md` | Planning |
| Implementation Backlog | `engineering/phase2/MONGLE_IMPLEMENTATION_BACKLOG.md` | Planning (authoritative Wave column) |
| DoD & Test Matrix | `engineering/phase2/MONGLE_DOD_AND_TEST_MATRIX.md` | Planning |
| Reset/Cutover Backlog | `engineering/phase2/MONGLE_MIGRATION_CUTOVER_BACKLOG.md` | Planning |
| Realtime Messaging Contract | `engineering/phase2/MONGLE_REALTIME_MESSAGING_CONTRACT.md` | `APPROVED_TARGET_CONTRACT` |
| Markpoint on Mongle Contract | `engineering/phase2/MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md` | `APPROVED_TARGET_CONTRACT` |
| Task register | `agent-system/active.md` | `CURRENT_IMPLEMENTATION_FACT` (Agent System state) |

**Not confused with Target documents** (`CURRENT_IMPLEMENTATION_FACT` / `LEGACY_OR_HISTORICAL_REFERENCE` only, Axis A): `MONGLE_CURRENT_TABLE_DICTIONARY.md`, `MONGLE_CURRENT_COLUMN_DICTIONARY.md`, `MONGLE_BACKEND_API_CONTRACT_INVENTORY.md`. The Target Column Dictionary itself explicitly delegates unchanged `KEEP_AS_IS` columns to the Current Column Dictionary (line 5) rather than duplicating them — this is intentional, not a missing-authoritative-source defect.

No ambiguity requiring resolution was found this pass — this same document
set was already independently identified in the prior verification task this
session, and no new document with a colliding name appeared.

## 4. Wave 1 READY Task Inventory

Re-extracted directly from `MONGLE_IMPLEMENTATION_BACKLOG.md` table rows (not
copied from the prior verification report, though the count matches it):

| Task ID | Status | Dependencies | Change area |
|---|---|---|---|
| `MONGLE-W1-ACCOUNT-CREDENTIAL-001` | `READY_FOR_IMPLEMENTATION` | D2 | BE: Account credential store, login/logout |
| `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001` | `READY_FOR_IMPLEMENTATION` | D2, D4 | BE: FamilyAdmin-provisioned Account issuance |
| `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001` | `READY_FOR_IMPLEMENTATION` | D1, D3, D7 | BE: persistent Session, `AuthorizedFamilySet` |
| `MONGLE-W1-SCOPED-RBAC-001` | `READY_FOR_IMPLEMENTATION` | D4 | BE: FamilyMembership-scoped role bindings |
| `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` | `READY_FOR_IMPLEMENTATION` | D7 | BE: `/families/{familyId}/...` / `/me/...` revalidation |
| (8 further Wave 1 rows) | `BLOCKED_BY_DEPENDENCY` (5) / `DEFERRED_TO_RELEVANT_TASK_START_GATE` (3) | various | all FE UI slices |

**Confirmed exactly 5 `READY_FOR_IMPLEMENTATION` rows, all in Wave 1, all
Backend.** No dependency is missing a row in the Decision Freeze; all cited
IDs (D1, D2, D3, D4, D7) are `APPROVED` (re-confirmed directly against
`MONGLE_TARGET_DECISION_FREEZE.md` lines 30–37 this pass, not assumed from the
prior report).

**Scope-axis check:** all 5 READY tasks are within the expected Wave 1 axes
(Account, Credential, Session, `AuthorizedFamilySet`, Scoped RBAC). No Wagle
durable messaging, Wagle realtime/Push, Markpoint mission/ledger, Target UI, or
cutover/retirement item is mixed into the READY set — those are all correctly
`BLOCKED_BY_DEPENDENCY` in Waves 2–7.

## 5. Existing Foundation Reality

Read directly: `backend/app/domains/family/models.py` (full file, 107 lines),
`backend/app/domains/auth/models.py` (full file, 35 lines),
`backend/app/domains/auth/service.py` (full file, 239 lines),
`backend/app/domains/auth/dependencies.py` (full file, 108 lines),
`backend/app/domains/family/service.py` (lines 1–90),
`backend/alembic/versions/0001_account_family_rbac_foundation.py` (full file).

| Component | Code exists | Migration exists | Test exists | Target-reusable | Gap |
|---|---:|---:|---:|---:|---|
| Account | YES — `family/models.py:6-11` | YES — `0001` upgrade | not verified this pass (out of scope: no test execution) | YES, `KEEP_AS_IS` | No credential/login field on the model at all — `id`, `display_name`, `status` only |
| FamilyGroup | YES — `family/models.py:14-19` | YES — `0001` | not verified | YES | none found |
| FamilyMembership | YES — `family/models.py:22-35` | YES — `0001` | not verified | YES | none found |
| Role | YES — `family/models.py:38-51` | YES — `0001` (seeds 4 FAMILY + 3 SERVICE roles) | not verified | YES | Role/Permission **code strings** are seeded but their finality is `REQUIRES_PM_REVIEW` (non-blocking, confirmed at Wave 1 RBAC Start Gate per the Wave Plan itself) |
| Permission | YES — `family/models.py:54-58` | YES — `0001` (seeds 10 permission codes) | not verified | YES | `family.ownership.manage` permission code is seeded but **no API route enforces it anywhere** (grepped; see Section 12) |
| RoleAssignment (`membership_role_assignments`) | YES — `family/models.py:68-75` | YES — `0001`, with a **partial unique index on `(membership_id, role_id) WHERE revoked_at IS NULL`** (line 90 of the migration) | not verified | YES | none found — this index is exactly what "last-admin protection" style invariants need |
| ServiceSubscription | YES — `family/models.py:78-89` | YES — `0001` | not verified | YES | none found |
| LegacyIdentityMapping | YES — `family/models.py:92-106` | YES — `0001` | not verified | `CURRENT_STATE_EVIDENCE_NOT_TARGET_CONTRACT` (per Table Dictionary, correctly) | **Currently the ONLY way `resolve_current_account` maps any request to an Account** — see below. This is real production-path current-state, not a documentation artifact. |
| **Account Credential store** | **NO** | **NO** | n/a | n/a | Confirmed `NOT_IMPLEMENTED` as the Table/Column Dictionaries state |
| **Account Session store** | **NO** | **NO** | n/a | n/a | Confirmed `NOT_IMPLEMENTED` |

**Critical current-implementation fact, independently verified by direct code
read (not restated from any document):** `backend/app/domains/family/service.py:37-86`
(`resolve_current_account`) is the **only** function anywhere in the codebase
that turns an authenticated request into an `Account` row, and it does so
**exclusively through `LegacyIdentityMapping`** — it takes the legacy
`get_current_user`/`get_current_admin` JWT payload (`player_id` or admin
`sub`), looks up a matching `PlayerAuth`/`AdminAuth` row, then joins through
`legacy_identity_mappings` (`mapping_status == 'linked'`) to find the `Account`.
There is no Account-native credential check anywhere in this path. This is
called from `family/router.py` (`/api/account-context`, family CRUD, member/role
routes — 3 call sites), `mission/service.py:330` (mission ownership resolution),
and `doran/service.py:25` (Doran identity resolution) — **i.e. the Foundation,
Doran, and Mission domains all currently sit on top of the Legacy bridge, not
on any Account-native mechanism.** This is exactly the state
`MONGLE_MIGRATION_CUTOVER_BACKLOG.md`/`MONGLE_TARGET_TABLE_DICTIONARY.md`
describe (`legacy_identity_mappings` = `CURRENT_STATE_EVIDENCE_NOT_TARGET_CONTRACT`,
"not a Target Auth mechanism... not a prerequisite for creating new Accounts")
— the documents are accurate, not overstated.

`backend/app/domains/auth/service.py`/`dependencies.py` (full read): current
login is 100% legacy — `authenticate_player` (PIN + `player_id`) and
`authenticate_admin` (`admin_auth.username`/`password`, itself FK'd to
`player_id`, not `account_id`) both issue a stateless JWT with no server-side
session record; `logout()` is a documented no-op (`# Phase 2에서 토큰 블랙리스트
또는 login_log 기록 추가 예정`, i.e. explicitly deferred, never built).
`get_current_user`/`get_current_admin`/`get_current_chat_user` in
`auth/dependencies.py` decode this JWT directly with no DB-backed revocation
check. **No refresh, no revoke, no expiry-beyond-JWT-`exp`, no device concept
exists today.** This confirms the Column Dictionary's own admission (line 67-70)
that even its historical sketch is missing refresh/device-unlink/Push-revocation
elements the approved D3 contract requires.

## 6. Table Dictionary Findings

Read `MONGLE_TARGET_TABLE_DICTIONARY.md` in full (66 lines) and cross-checked
every cited evidence line number against the actual model file.

**All cited evidence line ranges are accurate**: `family/models.py:6-11`
(Account), `:14-19` (FamilyGroup), `:22-35` (FamilyMembership), `:38-51`
(Role), `:54-58` (Permission), `:62-65` (RolePermission), `:68-75`
(MembershipRoleAssignment), `:78-89` (ServiceSubscription), `:92-106`
(LegacyIdentityMapping) — every one matches the real file exactly, no drift
found. This is a meaningfully strong signal: the Table Dictionary was written
against real code, not invented.

No `DOCUMENTED_BUT_NOT_IN_CODE` or `IN_CODE_BUT_UNDOCUMENTED` table was found
for the Wave 1 scope. `service_outbox_events` (`service_outbox/models.py`) is
correctly flagged `KEEP_AS_IS` with the caveat that its transaction-boundary
sharing with message persistence "requires verification before accepting
reuse" — appropriately hedged, not a documentation defect.

## 7. Column Dictionary Findings

Read `MONGLE_TARGET_COLUMN_DICTIONARY.md` in full (71 lines). The document
correctly delegates all `KEEP_AS_IS` table columns to the Current Column
Dictionary and only lists actual deltas (the 7 MarkPoint `TRANSFORM` FK swaps,
1 new `family_memberships.total_earned` column, and 2 explicitly-historical
Credential/Session sketches). No column-name, FK-target, or nullability
mismatch was found between this document and the live `family/models.py`.

The two "sketches" are explicitly labelled non-authoritative
(`VALID_HISTORICAL_REFERENCE`, not `NOT_IMPLEMENTED`'s design source) — see
Sections 8–9 below for what is and is not actually specified.

## 8. Credential Contract

| Required design element (per this task's checklist) | Status in current documents |
|---|---|
| `account_id` | Present in historical sketch (`account_id` FK, UNIQUE 1:1) |
| login identifier | Present — `username`, UNIQUE, explicitly **not** email/phone per D2 |
| password hash | Present — `password_hash`, bcrypt convention stated |
| credential status | **ABSENT** — no active/locked/disabled column in the sketch |
| initial credential / `must_change_password` | **ABSENT** — not mentioned anywhere; relevant because `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001`'s own DoD requires "initial-password reset" |
| `password_changed_at` | **ABSENT** |
| reset/revoke info | **ABSENT** at the credential level (Session has `revoked_at`, Credential does not) |
| failed-attempt / lock policy | **ABSENT** — the legacy `player_auth.login_attempts`/`lock_until` pattern is not carried into the sketch, and no explicit decision says whether Account credentials get the same lockout behaviour |
| `created_by` actor | **ABSENT** — relevant because `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001` needs to record which FamilyAdmin issued a credential |

**Verdict for this axis: `NEEDS_DICTIONARY_COMPLETION`.** Not a re-opened PM
decision (D2's `아이디+비밀번호`, no email/phone, is settled) — but the
Credential table as currently sketched cannot support the DoD/Test Matrix's
own required journey ("a FamilyAdmin provisions an independent Account...
initial-password reset", `MONGLE_DOD_AND_TEST_MATRIX.md:65-72`) without adding
at minimum a credential-status/must-change-password field and an issuing-actor
reference. This is exactly the kind of physical schema design the Wave Plan
already says belongs to the Wave 1 task itself, not a blocker requiring new PM
input — flagged so the implementer does not silently invent it either.

## 9. Session Contract

| Required design element | Status |
|---|---|
| session ID | Present (`id`, UUID or Integer — undecided which, acceptable at sketch stage) |
| `account_id` | Present, explicitly Account-scoped per D3 |
| token / refresh-token hash | **ABSENT.** The sketch has no token-hash column at all — meaning, taken literally, the sketch does not show how a client's bearer credential maps back to this row. The document's own closing line (67-70) admits this: "missing... refresh... which is why the Wave 1 task designs the real schema" |
| device identification policy | **ABSENT** — column dictionary sketch has an optional `device_label?` mentioned only in the Table Dictionary's one-line summary (line 23), not in the Column Dictionary's actual column table; the two documents are inconsistent with each other on this point (Table Dictionary implies a device column exists in the sketch, Column Dictionary's own sketch table does not list one) |
| `issued_at` | Present |
| `expires_at` | Present, required by D3 |
| `last_seen_at` | **ABSENT** |
| `revoked_at` | Present |
| revocation reason | **ABSENT** |
| credential/session version (for mass-invalidation) | **ABSENT** |
| IP/User-Agent storage | **ABSENT** — not decided either way; worth flagging only because if omitted, revocation auditing (`role changes are audited` DoD item, applied by analogy to session revocation) has no forensic trail |
| soft delete | **N/A per design** — a Session is revoked, not soft-deleted; no conflict found |
| Raw access token stored in plaintext? | **Not applicable to the sketch as written** — the sketch has no token column at all, so the specific FAIL condition this task asks to check for (plaintext token storage) does not currently exist in the documents. This is better than a wrong design, but is not the same as a correct one — the design is simply not there yet. |

**Verdict for this axis: `NEEDS_DICTIONARY_COMPLETION`.** Same reasoning as
Section 8. The device-unlink requirement in D3 (`per-device unlink`) and the
Wave 1 DoD's own required test ("device unlink") **cannot be implemented
against the current sketch** because there is no device-identifying column in
it at all — this is a real, concrete gap between the approved contract text
and the schema that would need to exist to satisfy it, not a restatement of
what the documents already flag.

## 10. ActiveFamilyContext Contract

Grepped `ActiveFamilyContext` across `MONGLE_TARGET_DECISION_FREEZE.md`,
`MONGLE_TARGET_COLUMN_DICTIONARY.md`, `MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md`
(13 hits). Every hit is consistent and none uses `ActiveFamilyContext` as an
authorization source — e.g. `MONGLE_TARGET_DECISION_FREEZE.md:275`: "서버는
URL 또는 client가 전달한 `familyId`를 그대로 신뢰하지 않고 Account Session,
FamilyMembership 및 상태... 를 교차 검증한다" (the server never trusts a
client-supplied `familyId`; it cross-verifies Session/Membership/Role every
time). **No FAIL condition found** — `ActiveFamilyContext` is consistently
described as client/foreground-navigation convenience state, not a DB-backed
authorization table, and there is no proposal anywhere to store or trust it as
one. Because it is deliberately not a server authority, its "storage location"
not being specified in the Column Dictionary is correct, not a gap — it is
`CONTRACT_SUFFICIENT_FOR_IMPLEMENTATION` as a client-local/ephemeral concept.
`AuthorizedFamilySet`, by contrast, **is** server-derived (from `ACTIVE`
`family_memberships` rows) and requires no new storage — it is a query, not a
table — also `CONTRACT_SUFFICIENT_FOR_IMPLEMENTATION`.

## 11. Scoped RBAC Contract

Verified against `family/models.py` + `family/service.py` (`effective_permissions`,
`require_permission`, `_active_owner_count`, `_lock_family_for_owner_change` —
function names read from the earlier `grep -n "def "` pass in Section 5's
Foundation check, bodies not fully re-read this pass since Table Dictionary
line-evidence already confirms their existence and the migration confirms the
underlying constraints):

- Role is `FamilyMembership` scope: confirmed structurally — `MembershipRoleAssignment.membership_id` FKs to `family_memberships.id`, never directly to `account_id`. Correct.
- FamilyAdmin/ServiceAdmin separable: the seeded roles include `FAMILY`-scope `owner`/`admin`/`member`/`restricted_member` and `SERVICE`-scope (`service_code='markpoint'`) `participant`/`mission_manager`/`point_admin` — structurally separable by `scope_type`+`service_code`, confirmed by the `0001` migration's CHECK constraint (`ck_roles_scope_service`, line 50 of the migration). No code path found this pass that would auto-grant a `SERVICE` role from a `FAMILY` `admin` role — consistent with "no automatic ServiceAdmin grant."
- Last-admin protection: `family/service.py` has `_active_owner_count`/`_lock_family_for_owner_change` functions (names only, confirmed present; body correctness not re-verified this pass — would require a full function-body read plus a live-DB behavioral test, out of scope for a read-only Start Gate check).
- Audit: `MembershipRoleAssignment.assigned_by_account_id`/`assigned_at`/`revoked_at` columns exist (`family/models.py:73-75`) — an audit trail is structurally present.

**No FAIL condition found for RBAC.** This axis is the closest to
`IMPLEMENTATION_READY` of the four (Credential/Session/ActiveFamilyContext/RBAC)
— its underlying tables, constraints, and service functions already exist and
match the Target contract; what remains is genuinely implementation work
(wiring `MONGLE-W1-SCOPED-RBAC-001`'s own DoD tests), not missing design.

## 12. API Inventory Findings

Read `MONGLE_TARGET_API_INVENTORY.md` in full (39 lines) and cross-checked its
central claim against code: "Auth/Session... does not exist for Account today.
Every current login route... issues a JWT shaped around legacy identity" —
confirmed accurate by the Section 5 code read (`auth/service.py`/`dependencies.py`
have zero Account-aware paths). The `/api/account-context`, `/api/families/*`
claim ("auth today runs through the legacy `get_current_user`... the
Group-scoped permission checks are already Mongle-native") is also confirmed —
`family/router.py`'s 13 routes all take `user: dict = Depends(get_current_user)`
then immediately call `family_service.resolve_current_account`/`require_permission`,
matching the document's description exactly.

`family.ownership.manage` route-existence check (independently re-run, not
copied): `grep -rn "family.ownership.manage" backend/app/` returns only its
**seed-migration INSERT** (`0001_account_family_rbac_foundation.py:124`) and
its Role Matrix mention — **zero route or service-layer enforcement code**
found anywhere. The permission code is seeded into the DB but nothing checks
it. This independently confirms the document's own "none found today" claim
(`MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md:60`) rather than merely restating it.

## 13. PM_DECISION_REQUIRED 3건 판정

| # | Location | Summary | D1–D8 재오픈 여부 | 연결 Task | Wave 1 Blocker | 판정 |
|---|---|---|---|---|---|---|
| 1 | `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md:60` | `family.ownership.manage`에 대응하는 실제 API route가 필요한지 미정 | NO — D4(RBAC 프레임워크)는 이미 APPROVED, 이 항목은 그 프레임워크 안의 라우트 존재 여부 하나만 미정 | 어떤 Wave 1 Task도 이 route를 요구/전제하지 않음 — `MONGLE-W1-SCOPED-RBAC-001`, `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` 모두 이 permission code의 route 신설을 요구/전제로 삼지 않는다 | **NO — non-blocking for Wave 1.** 향후 소유권 이전(ownership transfer) UI/API가 추가될 때만 관련 |
| 2 | `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md:61` | Role 표시명(한국어 UI copy)이 seed의 `name` 컬럼 그대로인지, 별도 문구가 필요한지 미정 | NO — 순수 카피/라벨 문제, RBAC 구조와 무관 | 어떤 Wave 1 Task도 UI copy 확정을 DoD/Start Gate 조건으로 명시하지 않음 | **NO — non-blocking for Wave 1.** FE UI 슬라이스(Wave 1의 `BLOCKED_BY_DEPENDENCY`/`DEFERRED` 행들) 작업 시점에만 관련 — BE의 5개 READY Task는 UI 카피에 의존하지 않는다 |
| 3 | `MONGLE_TARGET_API_INVENTORY.md:32` | `/api/admin/*` (31 routes)의 정확한 target permission-per-route 매핑이 미정 | NO — D4는 APPROVED, 이 항목은 admin 서브라우트별 세부 매핑값 하나만 미정 | **`MONGLE-W5-...`/Markpoint 계열 (Wave 4/5) — `/api/admin/*`은 mission/daily_point 등 MarkPoint 도메인 delegate이며, `MONGLE_TARGET_API_INVENTORY.md` 자신이 이를 Wave 4/5의 TRANSFORM 대상으로 명시** | **NO — not a Wave 1 blocker.** Wave 1 READY 5건 중 어느 것도 `/api/admin/*`을 소유하거나 수정하지 않는다(직접 코드 확인: `mission/router.py`, `daily_point/router.py`, `notification/router.py`는 모두 `app.dependencies.get_current_player`/`require_admin`을 쓰며 `family`/`auth` 도메인 파일이 아니다). **해당 Task(Wave 4/5, MarkPoint auth TRANSFORM) 자신의 Start Gate에서는 blocking**이다 |

**결론:** 잔존 `PM_DECISION_REQUIRED` 3건 전부 D1–D8 재오픈이 아니며, 전부 Wave 1의
5개 READY Task를 blocking하지 않는다. 다만 #3은 Wave 4/5(Markpoint TRANSFORM)
자신의 Start Gate에서는 실제 blocker이므로, "Decomposition 전체에는
non-blocking"이라는 이전 검증 보고서의 표현이 Wave 1 한정으로는 정확하지만
Wave 4/5까지 일반화하면 부정확해질 수 있다는 점을 이번 pass에서 명확히 한다.

## 14. PHASE0 Task Overlap

| Task | 현재 상태 | Wave 1 관계 |
|---|---|---|
| `PHASE0-AUTOMATED-GAP-CLOSEOUT-001` | `SUSPENDED` / `Verification: BLOCKED` / `Execution: FAILED` — 측정된 결함: `GET /api/missions/?player_id=2` 무인증 200, Player A가 Player B의 mission을 생성/삭제, `daily-points/summary`·`notifications` 무인증 200 | **`DEPENDENCY_ONLY`, `NO_OVERLAP`(파일 수준).** 결함이 위치한 파일(`mission/router.py`, `daily_point/router.py`, `notification/router.py`)은 모두 `app/dependencies.py`의 `get_current_player`/`require_admin`을 사용하며, Wave 1의 5개 READY Task는 전부 `family/`·`auth/` 도메인 파일만 다룬다 — 코드 레벨 파일 겹침 없음(직접 확인). 다만 `get_current_player`는 `auth/dependencies.py`의 `get_current_user`를 감싸는 얇은 wrapper이므로, Wave 1이 `get_current_user`를 교체하면 이 결함의 근본 원인(무엇을 신뢰할지)도 함께 바뀐다 — 그러나 `mission`/`daily_point`/`notification` 라우터 자체의 TRANSFORM은 Wave 4/5 몫으로 문서에 이미 명시돼 있다. "Wave 1이 정확히 그 표면을 재구축한다"는 Wave Plan 문구는 **인증 계층(식별)** 을 가리키는 것이지 **인가 라우터(mission/daily_point/notification)** 자체를 가리키는 것이 아니며, 문자 그대로 같은 파일을 수정하는 것은 아니다 — 정밀화된 판정 |
| `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001` | `active.md` 미등록 (재확인: `grep` 결과 없음) — `Execution: SUCCEEDED`(조사 완료), 등록 자체는 `active.md` single-writer lock으로 `BLOCKED` | Wave 1과 직접 파일 겹침 없음(문서/등록 감사 성격) — `NO_OVERLAP` |
| `PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001` | `active.md`에 정상 등록, `IN_PROGRESS` | Wave 1과 직접 관련 없음(OpenAPI 생성 baseline 성격) — `NO_OVERLAP` |

**전체 판정: `DEPENDENCY_ONLY`.** `CONCURRENT_EXECUTION_FORBIDDEN`에 해당하는
동일 파일·동일 DB 테이블 동시 수정 사례는 발견되지 않았다. 다만
`PHASE0-AUTOMATED-GAP-CLOSEOUT-001`은 여전히 `SUSPENDED` 상태로 PM triage가
없었고, mission/daily_point/notification 라우터의 인가 결함은 Wave 4/5 시작
전에 반드시 별도로 해소되거나 그 Wave 범위에 명시적으로 포함돼야 한다 — Wave 1
자체의 Start Gate 조건은 아니다.

## 15. Doran Commit Verification

```bash
git merge-base --is-ancestor 0393971 HEAD   # exit 0 — is ancestor
git merge-base --is-ancestor 91eb98e HEAD   # exit 0 — is ancestor
git show --name-only 0393971 | grep -E "domains/(family|auth)/"   # no match
git show --name-only 91eb98e | grep -E "domains/(family|auth)/"   # no match
```

| Commit | Branch 포함 여부 | 추가/수정 파일 | Account/Family/RBAC 직접 관련 여부 | Doran/Wagle 전용 여부 | Authoritative 문서 반영 | Wave 1 선행 dependency 여부 |
|---|---|---|---|---|---|---|
| `0393971` (service principal/room binding) | YES, ancestor of HEAD | `doran/models.py`, `doran/router.py`, `doran/schemas.py`, migration `0003`, `service_actor.py` | **NO** — `family/`, `auth/` 도메인 파일 미포함(직접 grep 확인, 0 hits) | YES, Doran 전용 | 부분적으로: `DORAN_FOUNDATION_GAP_ANALYSIS.md`에 R2-B1로 문서화됨(Task-ID 등록은 아님) | **NO** |
| `91eb98e` (reliable service event delivery) | YES, ancestor of HEAD | `doran/*`, `service_outbox/*`, `workers/service_outbox.py`, migration `0004`, **`mission/service.py`**(+57줄, `_emit_mission_completed_event`) | 부분적 — `mission/service.py`를 건드리지만 `family/`·`auth/` 도메인은 미포함 | 아니오 — Doran+MarkPoint 이벤트 연동 지점 포함 | 동일 | **NO** (Wave 5의 MarkPoint→Wagle 시스템 이벤트 릴레이, `MONGLE-W4-MARKPOINT-SYSTEM-EVENT-RELAY-001` 관련) |

두 커밋 모두 `HEAD`에 실제로 병합돼 있음이 재확인됐다(`git merge-base
--is-ancestor`). 그러나 둘 다 `family/`·`auth/` 도메인을 건드리지 않으므로
Wave 1의 5개 READY Task와 파일 수준에서 겹치지 않으며, Wave 1의 선행조건도
아니다. `NOT_VERIFIED`로 보고할 항목 없음 — 두 커밋 모두 접근 가능했고 완전히
확인됐다.

## 16. active.md Single-Writer State

```text
Current relay writer: MONGLE-APPROVED-DECISIONS-FREEZE-AND-DECOMPOSITION-001
Lock scope: agent-system/active.md, engineering/phase2/ 의사결정·분해 문서 세트
Lock status: 아직 해제되지 않음 (relay/current.md 재확인, 동일 문구 유지)
```

| Task | active.md 등록 여부 |
|---|---|
| `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001` | **미등록** (재확인, grep 결과 없음) |
| `MONGLE-FREEZE-DECOMPOSITION-INDEPENDENT-VERIFICATION-001` | **미등록** — 이전 검증 Task 자신도 "active.md 임의 수정 금지" 원칙에 따라 스스로 등록하지 않았음(그 Task 보고서의 Closeout note 참조) |

**Wave 1 시작 조건 충족 여부: `BLOCKED_BY_ACTIVE_REGISTER_INCONSISTENCY`.**
`MONGLE-APPROVED-DECISIONS-FREEZE-AND-DECOMPOSITION-001`이 `active.md`의
single-writer를 여전히 보유한 채 `IN_PROGRESS`이므로, Wave 1의 5개 READY
Task를 정식으로 `active.md`에 등록하려면 먼저 이 lock이 해제되거나 PM이
명시적으로 병행 등록을 허가해야 한다. 이는 Wave 1 Task 자체의 설계/코드
문제가 아니라 순수한 Agent System 등록 절차 문제다.

## 17. Migration Readiness

```bash
cd backend && python3 -m alembic heads      # 0004_doran_reliable_slice (head) — 단일 head
python3 -m alembic history                  # 0000 -> 0001 -> 0002 -> 0003 -> 0004, 선형, branch 없음
```

- 복수 head 없음. 선형 체인 확인됨.
- Wave 1 신규 migration의 예상 parent: `0004_doran_reliable_slice` (현재 head).
- 기존 dirty migration 파일 없음 (`git status`에 `backend/alembic/versions/` 항목 없음).
- D8 RESET 위반 후보(Legacy backfill/변환)는 어떤 문서에도 Wave 1 스코프로 제안되지 않음 — Section 5-9에서 검토한 Credential/Session 스켈레톤 어디에도 legacy row를 읽거나 변환하는 로직이 없음.
- fresh schema/새 Account bootstrap 방향과 일치.
- test fixture와 production bootstrap 분리 여부는 마이그레이션 파일 자체로는 판단 불가(코드 미작성) — `NOT_APPLICABLE_YET`.

**판정: `MIGRATION_READY`** (계획 수립 관점에서; 실제 마이그레이션 파일은 아직 작성되지 않음 — 이는 정상, Wave 1 구현 자체의 산출물).

## 18. DoD/Test Readiness

`MONGLE_DOD_AND_TEST_MATRIX.md`의 "Required Target journeys" 절(51-105행)을
Wave 1 5개 READY Task의 "Required tests"(Wave Plan 67행)와 대조:

- **Credential**: DoD "D2/D3/D4 identity" 절이 login success/no-legacy-identity, FamilyAdmin issuance boundary, password/PIN read 거부, last-admin protection, audit를 명시 — Wave Plan의 Wave 1 "Required tests"와 일치. 단, Section 8에서 지적한 credential-status/lockout 설계 공백은 DoD 문서에도 반영되지 않음 — DoD가 "구현될 기능"을 전제로 테스트를 나열할 뿐, 스키마 공백 자체를 별도로 지적하지는 않는다(정상적인 역할 분리이지 결함은 아님).
- **Session**: "Session survives PWA restart... expiry, refresh, revoke and device unlink" 명시 — 그러나 Section 9에서 확인했듯 현재 스케치에는 refresh/device 컬럼이 없으므로, 이 DoD 항목은 스키마가 먼저 보완되지 않으면 테스트 자체를 작성할 수 없다. **`DOD_INCOMPLETE`는 아니다** — DoD 문구 자체는 명확하고 Task와 잘 연결돼 있다; 문제는 DoD가 아니라 그 DoD를 충족시킬 스키마가 아직 없다는 것.
- **Family Context**: multi-membership, authorized list, active switch, 분리, cross-family denial 전부 D1/D7 절에 명시 — Wave 1 Required tests와 일치.
- **RBAC**: FamilyAdmin/ServiceAdmin, last-admin, membership-scoped role, revoke, cross-family denial 전부 명시 — 일치.

**전체 판정: DoD 문서 자체는 완전하고 Task와 잘 연결돼 있다(`DOD_INCOMPLETE`
아님). 실행 가능성이 막힌 지점은 Credential/Session 스키마 공백이다(Section
8-9), DoD 누락이 아니다.**

## 19. Task-by-Task Readiness

| Task ID | 판정 | 근거 |
|---|---|---|
| `MONGLE-W1-ACCOUNT-CREDENTIAL-001` | `BLOCKED_BY_SCHEMA_CONTRACT` | D2 승인됐으나 Credential 테이블 스케치가 `VALID_HISTORICAL_REFERENCE`일 뿐이고 status/lockout/issuer 컬럼이 없음(Section 8) — 구현 시작 전 스키마 설계가 먼저 필요 |
| `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001` | `BLOCKED_BY_SCHEMA_CONTRACT` | D1/D3/D7 승인됐으나 Session 스케치에 refresh-token/device 컬럼이 없어 D3가 요구하는 refresh·device-unlink를 설계대로 구현 불가(Section 9) |
| `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001` | `BLOCKED_BY_DEPENDENCY` | 자체 설계는 D2/D4로 충분히 커버되나, "초기 비밀번호 재설정" DoD가 Credential 테이블의 존재를 전제 — `MONGLE-W1-ACCOUNT-CREDENTIAL-001` 완료 후 사실상 순차 진행 필요 |
| `MONGLE-W1-SCOPED-RBAC-001` | `READY_AFTER_DOCUMENT_CORRECTION` | 기반 테이블/제약(Role/Permission/Assignment)이 이미 존재하고 Target 계약과 일치(Section 11) — 유일하게 열린 항목은 "seeded role/permission code strings" 최종 확정(`REQUIRES_PM_REVIEW`, non-blocking, 자체 Start Gate에서 확인 예정이라고 이미 명시됨). 구현 착수 자체는 가능 |
| `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` | `READY_AFTER_DOCUMENT_CORRECTION` | D7 승인, 기존 `require_permission`/`resolve_current_account` 패턴이 이미 존재 — 다만 `resolve_current_account`를 Account-native 방식으로 교체하는 작업이 선행돼야 최종 완성(사실상 Credential/Session Task와 연동) |

**등록 관점의 공통 조건 — 5건 전부 `BLOCKED_BY_ACTIVE_REGISTER_INCONSISTENCY`도 동시에 적용됨**(Section 16): active.md single-writer lock이 해제되지 않는 한 정식 Task 등록 자체가 불가능하다. 이는 설계 문제가 아니라 절차 문제이므로 별도 축으로 기록한다.

## 20. 6-Gate Review

- **Gate 1 (환각 방지):** 이 보고서의 모든 코드 관련 주장은 실제 파일 읽기(`family/models.py`, `auth/models.py`, `auth/service.py`, `auth/dependencies.py`, `family/service.py` 발췌, `0001` migration 전문)로 검증됐다. 어떤 테스트도 PASS로 기록하지 않았다(테스트 실행 자체를 하지 않았음을 명시). DB 컬럼은 문서에 없는 것을 임의로 채우지 않고 전부 "ABSENT"로 표기했다.
- **Gate 2 (누락 방지):** Wave 1 READY 5건, Credential, Session, Family Context, RBAC, API, Migration, DoD/Test, active writer, PHASE0 overlap — 전항목 확인 완료.
- **Gate 3 (오작업 방지):** 이 보고서는 Legacy credential backfill, FamilyAdmin 자동 ServiceAdmin 부여, ActiveFamilyContext 기반 authorization, plaintext token 저장, 가족 탈퇴 시 전체 Session 종료를 유발하는 어떤 설계도 제안하지 않았다 — 오히려 그런 설계가 현재 문서에 없다는 것을 확인만 했다. 기존 dirty 파일은 정리하지 않았다.
- **Gate 4 (축혼동 방지):** `CURRENT_IMPLEMENTATION_FACT`(코드 실측)와 `APPROVED_TARGET_CONTRACT`(D1-D8)와 `VALID_HISTORICAL_REFERENCE`(스케치)를 각 절에서 명시적으로 구분했다. Wave 1과 Wagle/Markpoint/Cutover 구현을 섞지 않았다 — Doran 커밋 분석에서도 family/auth 도메인 미포함을 근거로 명확히 분리했다.
- **Gate 5 (문서 신선도):** `MONGLE_TARGET_*` 문서만 authoritative로 사용했고 `MONGLE_CURRENT_*`/Axis A 문서는 배경 참고로만 인용했다. `MONGLE_TARGET_DECISION_FREEZE_AND_DECOMPOSITION_REPORT.md` 같은 superseded 문서는 사용하지 않았다.
- **Gate 6 (근거 정합):** 모든 핵심 판정에 파일 경로+행 번호(또는 `git`/`alembic` 명령 결과)를 첨부했다.

## 21. Exact Blockers

```text
BLOCKER 1 — SCHEMA
Account Credential 테이블 물리 설계 부재 (status/lockout/issuer 컬럼 없음)
영향: MONGLE-W1-ACCOUNT-CREDENTIAL-001, MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001

BLOCKER 2 — SCHEMA
Account Session 테이블 물리 설계 부재 (refresh-token/device 컬럼 없음)
영향: MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001, MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001(간접)

BLOCKER 3 — PROCESS (코드 무관)
agent-system/active.md single-writer lock이 MONGLE-APPROVED-DECISIONS-FREEZE-AND-DECOMPOSITION-001에
여전히 귀속돼 있어 Wave 1 Task의 정식 등록 불가
영향: Wave 1 READY 5건 전체 (등록 축에 한함, 설계/코드 축과 무관)
```

`BLOCKED_BY_PM_DECISION`/`BLOCKED_BY_ARCHITECTURE_DECISION`에 해당하는 항목은
발견되지 않았다 — D1-D8 재오픈이 필요한 사안은 없다.

## 22. Recommended Next Execution Scope

```text
즉시 구현 가능(스키마 설계 선행 후):
  MONGLE-W1-SCOPED-RBAC-001 — 기존 테이블로 착수 가능, seed code string 확정만 병행

보정 후 구현 가능:
  MONGLE-W1-ACCOUNT-CREDENTIAL-001 — Credential 테이블에 status/lockout/issuer 컬럼 추가 설계 먼저
  MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001 — Session 테이블에 refresh-token/device 컬럼 추가 설계 먼저
  MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001 — Session 설계 완료 후 사실상 병행 가능
  MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001 — Credential 설계 완료 후 사실상 병행 가능

PM 결정이 필요한 항목: 없음 (D1-D8 전부 APPROVED, 재오픈 불필요)

dependency로 막힌 항목:
  Wave 1 전체의 active.md 정식 등록 — MONGLE-APPROVED-DECISIONS-FREEZE-AND-DECOMPOSITION-001의
  single-writer lock 해제 또는 PM의 명시적 병행 등록 허가 필요
```

권고 순서: (1) Credential/Session 물리 스키마를
`MONGLE-W1-ACCOUNT-CREDENTIAL-001`/`MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001`
자신의 Start Gate 산출물로 먼저 확정 (2) 그 설계를 골자로 5개 Task를 한 번에
`active.md`에 등록 요청 (3) `MONGLE-W1-SCOPED-RBAC-001`은 스키마 설계와
병행 착수 가능.

## 23. Final Verdict

```text
WAVE_1_START_GATE_CONDITIONAL
DB_CONTRACT_REQUIRES_CORRECTION
NOT_READY_FOR_FULL_WAVE_1
```

## 24. Changed File Manifest

이 Task가 생성한 파일은 다음 1개뿐이다:

```text
agent-system/qa/MONGLE-W1-START-GATE-AND-DB-CONTRACT-VERIFICATION-001.md
```

종료 검증 결과는 아래 콘솔 응답의 Git 절 참조. `agent-system/active.md`,
`relay/current.md`, `AGENTS.md`, `CLAUDE.md`, 공통 Agent/System Prompt는
수정하지 않았다. 기존 dirty 파일 28건은 손대지 않았다(정리/되돌리기 없음).
제품 코드, 테스트 코드, DB model, migration, seed/fixture는 전부 읽기만
했고 어떤 파일도 쓰기 대상이 아니었다.

(§25 애덤덤 추가로 이 파일 자체는 최초 생성 이후 1회 갱신됐다. 여전히 이
Task가 만들거나 수정한 파일은 이 1개뿐이다.)

## 25. PM Correction Addendum (2026-08-01)

PM이 본 검증을 접수하며 내린 판정과 정정 사항. 원문 프로즈는 보존하고
여기에만 기록한다(이 저장소의 기존 관행 — `active.md`의 Wave 6.1 closeout
사례와 동일한 방식).

### 25.1 PM 최종 판정

```text
WAVE_1_START_GATE:            CONDITIONAL — ACCEPTED
FULL_WAVE_1_IMPLEMENTATION:   NO-GO
IMMEDIATELY_EXECUTABLE_TASKS: 0
```

### 25.2 정정 1 — readiness 표현 (논리축/운영축 혼동)

본 보고서 §1·§19·§22 및 최종 콘솔 응답이 사용한 `Implementation-ready: 2건`
표현은 **논리적 준비 상태와 운영적 착수 가능 상태를 혼동**한 것이다. 5건
전부가 `active.md` 등록 불일치(§16, BLOCKER 3)에 공통 차단되어 있으므로
현 시점에 실제로 착수 가능한 Task는 0건이다. 정정된 표현:

```text
SCHEMA/DEPENDENCY_READY_AFTER_DOCUMENT_CORRECTION: 2건
OPERATIONALLY_READY_TO_START:                      0건
```

본 보고서가 §19에서 등록 축을 "별도 축으로 기록한다"고 분리해 둔 것 자체는
맞지만, 요약 표현에서 그 축을 반영하지 않아 오해를 유발했다. 요약에서도
두 축을 결합한 값을 제시했어야 한다.

### 25.3 정정 2 — `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` 판정 하향

§19에서 이 Task를 `READY_AFTER_DOCUMENT_CORRECTION`으로 판정한 것은
**과대평가**였다. PM 지적에 따라 백로그 원문을 재확인한 결과, 이 Task의
자체 스코프 정의가 Session 존재를 전제한다:

> `MONGLE_IMPLEMENTATION_BACKLOG.md:43` — "the server never trusts a URL or
> client `familyId` and **revalidates Session**, membership and status, owner
> scope or entitlement, role/permission and resource ownership. Tests:
> substituted `familyId` deny, revoked-membership stale-route deny,
> personal/family route separation, **multi-tab isolation**"

`revalidates Session`과 `multi-tab isolation` 테스트 모두 Account-native
Session이 존재해야 성립한다. Session 부재 상태에서 이 Task를 통째로
착수하면 HTTP 인증 의존성이 다시 `LegacyIdentityMapping`(§5에서 실측한
현재 유일 경로)에 종속되며, 이는 D8 RESET 방향과 반대로 레거시 결합을
오히려 강화한다. **따라서 이 Task는 내부 범위 분할이 선행돼야 한다:**

| 분할 | 내용 | 선행 가능 여부 |
|---|---|---|
| 선행 가능 | RBAC permission evaluation, membership-scoped evaluation, cross-family denial, last-admin invariant, service/unit test | YES — Session 불요 |
| Session 이후 | HTTP current-account dependency 교체, family-scoped route authorization wiring, `LegacyIdentityMapping` 비정본화 | NO — Wave 1E 이후 |

대조 확인: `MONGLE-W1-SCOPED-RBAC-001`(`백로그:42`)의 스코프는 "Role
bindings with default deny; FamilyAdmin and ServiceAdmin separated; role
changes audited; roles end on membership leave/suspension; last-admin
protection", 테스트는 "default deny, cross-family deny, admin separation,
last-admin protection, audit record"로 **Session을 요구하는 항목이 하나도
없다.** 따라서 RBAC Task의 선행 착수 가능 판정은 유지되며, 두 Task를 같은
등급으로 묶었던 §19의 처리가 부정확했던 것으로 확정한다.

### 25.4 확인 3 — 후속 작업의 성격 (PM 재결정 아님)

§13·§21의 결론이 재확인됐다. Credential/Session 컬럼 공백은 제품 정책
미결정이 아니라 **이미 승인된 D2/D3를 물리 DB 구조로 구체화하지 못한
상태**다. 따라서 후속은 PM 의사결정 요청이 아니라 Architecture/DB Contract
작성 작업이다.

```text
승인된 D2·D3 → Credential/Session 물리 모델 → Table/Column Dictionary 갱신
→ API·DoD·Migration 계약 → 구현
```

### 25.5 승인된 Wave 1 재구성

| 단계 | 범위 |
|---|---|
| Wave 1A — Governance Closeout | Freeze Task active lock 종료; 미등록 verification/audit Task closeout; `active.md` single-writer 정상화 |
| Wave 1B — DB Contract Correction | Credential·Session 물리 스키마; Device/refresh-token 정책; Table/Column Dictionary; API Inventory; Migration plan; DoD/Test Matrix |
| Wave 1C — Scoped RBAC Foundation | Role/Permission seed code 확정; membership-scoped evaluation; last-admin 보호; cross-family denial; audit 계약 |
| Wave 1D — Account Credential | Credential model/migration; password hashing; 상태·잠금·reset; 초기 자격증명; 테스트 |
| Wave 1E — Session and Family Context | Session model/migration; persistent session; refresh/revoke/expiry; `AuthorizedFamilySet`; `ActiveFamilyContext`; account-native resolver; `LegacyIdentityMapping` 비정본화 |
| Wave 1F — Route Authorization and Issuance | family-scoped route wiring; permission-per-route enforcement; FamilyAdmin Account issuance; 통합 테스트 |

이 재구성은 §22의 권고 순서를 대체한다. 특히 FamilyAdmin 발급이
Credential → Session 이후(1F)로 배치된 점은 §19의 `BLOCKED_BY_DEPENDENCY`
판정과 일치하며, 그 이유(초기 비밀번호 저장 위치, 최초 로그인 변경 강제
여부, 발급자 기록, 재발급 시 기존 Session 폐기 여부, 초기 자격증명 재조회
가능 여부를 임의 결정하게 됨)가 PM에 의해 명시적으로 확인됐다.

### 25.6 다음 Task

```text
MONGLE-W1-CREDENTIAL-SESSION-DB-CONTRACT-CORRECTION-001
```

확정해야 할 산출물: Credential table, Session table, Device 식별 방식,
Refresh token 저장·회전 방식, Password reset 모델, Initial credential
issuance 모델, Revoke·expiry 정책, 필수 FK/Unique/Check/Index, Table
Dictionary, Column Dictionary, API Inventory, Migration Plan, DoD/Test
Matrix.

선행 또는 병행 조건: active writer lock 정상 종료(Wave 1A).

### 25.7 최종 상태 스탬프

```text
TARGET_DECISIONS_FROZEN
DECOMPOSITION_ACCEPTED_WITH_CORRECTION
WAVE_1_START_GATE_CONDITIONAL
FOUNDATION_RBAC_SCHEMA_READY
CREDENTIAL_SESSION_SCHEMA_BLOCKED
ACTIVE_REGISTER_BLOCKED
FULL_WAVE_1_NOT_READY
```
