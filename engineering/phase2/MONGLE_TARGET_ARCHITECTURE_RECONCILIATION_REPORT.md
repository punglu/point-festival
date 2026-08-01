# MONGLE_TARGET_ARCHITECTURE_RECONCILIATION_REPORT

> **PARTIALLY_SUPERSEDED:** current-code inventory is retained; Target readiness and ownership follow the Decision Freeze. D5-B is approved without a separate MarkpointParticipant, and D8 RESET supersedes this historical report's Legacy data-migration/backfill alternatives.

```text
Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001
Worktree: /Users/mac/mac_Project/mongle_ui-data-backend-worktree (isolated)
Branch: data-backend-contract-reconciliation
Exact HEAD: 6c633679c6708a21920f0e4b306bc1e36a2ea72d (unchanged, same as the
  prior Axis-A report in this same worktree — no product/DB code was ever
  touched across either phase of this task)
Start status (this phase): clean tracked tree, 7 Axis-A documents already
  present (untracked) from the prior phase
End status: clean tracked tree, 17 total documents present (untracked); no
  commits made in either phase

Correction context: PM redirected this task's central axis mid-flight
(2026-07-31), after the Axis-A ("LEGACY_CURRENT_STATE") phase had already
reached a "READY_FOR_DATA_BACKEND_CONTRACT_PM_FREEZE" verdict on its own
terms. The correction: Mongle is a new platform owning Account/Group/
Membership/Role/Permission/Auth/Session; 와글와글 is a new realtime messenger
on Mongle; 마크포인트 잔치 is a new service built on Mongle's user/group/
permission/session structure. The legacy point-festival system is reference
material only, never the SSOT. This report covers the second (Axis B,
"TARGET_MONGLE_ARCHITECTURE") phase and supersedes the prior report's verdict
without repeating its still-valid execution evidence (migration-chain
verification, 71/71 backend tests, git/diff-check state — all cited by
reference from `MONGLE_DATA_BACKEND_CONTRACT_RECONCILIATION_REPORT.md`,
retained and banner-marked as superseded/Axis-A-only, not deleted).

Documents created (Axis B, this phase):
  MONGLE_TARGET_BUSINESS_GLOSSARY.md
  MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md
  MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md
  MONGLE_TARGET_TABLE_DICTIONARY.md
  MONGLE_TARGET_COLUMN_DICTIONARY.md
  MONGLE_TARGET_API_INVENTORY.md
  MONGLE_REALTIME_MESSAGING_CONTRACT.md
  MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md
  MONGLE_LEGACY_TO_TARGET_MAPPING.md
  MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md
  MONGLE_TARGET_ARCHITECTURE_RECONCILIATION_REPORT.md (this file)
Documents modified (banner-only, content preserved): all 7 Axis-A documents
  from the prior phase received a short "AXIS: LEGACY_CURRENT_STATE"
  banner pointing to their Axis-B successor; no factual content in any of
  them was rewritten or deleted.

Key finding, stated once here because it changes how every other document
should be read: a substantial part of what PM described as new
Mongle-platform-owned structure **already exists**, built before this
correction, as the Foundation layer registered under
`PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001` (Account/FamilyGroup/
FamilyMembership/Role/Permission/RolePermission/MembershipRoleAssignment/
ServiceSubscription) and the Doran messaging domain
(Room/Participant/Message/ReadState/ServicePrincipal/ServiceBinding). This
work is not legacy and not being replaced by this reconciliation — it is
confirmed, by direct source read, to already be target-shaped. The two
genuinely missing platform capabilities are Account-native Authentication/
Session (does not exist in any form) and MarkPoint's re-hosting onto
Membership ownership (exists, but still points at legacy Player identity
throughout).

Verified domains (target-axis classification applied to all 17 domains from
  the Axis-A pass): player, auth (both REFERENCE_ONLY/DEPRECATE), mission,
  mission_template, level_tier, daily_point, deduction (all TRANSFORM,
  REUSE_LOGIC_ONLY), cheer (TRANSFORM), feedback (mixed TRANSFORM/
  KEEP_AS_IS), chat (DEPRECATE), notification (TRANSFORM), config
  (KEEP_AS_IS mechanism, UNDECIDED scoping), login_log (REFERENCE_ONLY),
  admin (TRANSFORM auth dependency, KEEP_AS_IS delegation structure),
  family (KEEP_AS_IS, already target), doran (KEEP_AS_IS, already target),
  service_outbox (KEEP_AS_IS, already target).

Naming conflicts: the 4 found in the Axis-A phase remain valid (see
  MONGLE_DATA_NAMING_CONTRACT_V0_1.md §4); none are resolved by the axis
  correction, since none depended on which axis is authoritative.
Table grouping conflicts: none, per the Axis-A alignment check (unaffected
  by this correction — table *naming* was already sound, only table
  *ownership* needed reconsideration).
Column synonym conflicts: total_points/total_earned ambiguity carries
  forward into the target schema (total_earned re-homed to
  family_memberships, but the naming ambiguity itself is a naming problem,
  not an ownership problem, so it survives the transform unchanged).
Stale contracts found: the single largest one, per this corrected framing,
  is that MarkPoint's entire persistence/authorization layer was built
  before — and never updated to match — the Account/Group/Membership/Role/
  Permission Foundation that already exists one commit-family away in the
  same repository. This is the reconciliation's central finding.

NO_CHANGE_REQUIRED: family/doran domains' schema and API (already
  target-shaped); level_tiers (not player-scoped today, no transform
  needed); feedback_replies (scoped transitively).
DOCUMENTATION_ONLY: the 4 naming conflicts (Axis A); migration filename/
  revision-id mismatches; test-dependency listing gap.
API_ADAPTER_REQUIRED: 와글와글 frontend wiring (GT2); MarkPoint's own
  level-display wiring for A1/A3 (Axis A's G2, still valid — the *correct*
  API to wire to, `level-tiers`, is unaffected by the axis correction).
API_CHANGE_REQUIRED: MarkPoint's auth-dependency swap across ~70 routes
  (GT3); Account-native Auth/Session routes (GT1, net-new); possibly a
  real-time transport (GT4, scope UNKNOWN pending a product decision).
QUERY_OR_READ_MODEL_REQUIRED: 와글와글's batch room-list-with-preview
  endpoint (GT2, unchanged from Axis A).
MIGRATION_REQUIRED: MarkPoint's ownership-FK transform across 7 tables plus
  a new scope column on `cheer_messages` (GT3); a new Account-credential/
  Session store, contract approved by D2/D3 with physical shape as Wave 1
  design work (GT1) — and note that under D8 RESET the Markpoint entry means
  newly created Target records, never conversion of legacy rows; the
  pre-existing `missions.status` CHECK-constraint gap (Axis A G5, still
  open, unaffected by this correction).
UNKNOWN: `doran_rooms.version` column's read/write site (Axis A G12,
  unaffected); GT4's exact scope pending a real-time-transport product
  decision; GT5/GT6's cutover-sequencing consequences (data-loss risk if
  handled incorrectly, but the risk's *existence* is confirmed, only its
  resolution is undecided).

Product code changed: NONE (identical to the Axis-A phase — this entire
  reconciliation, across both phases, produced documentation only)
Database changed: NONE
Production DB accessed: NEVER
Commit/push/PR: NONE performed in either phase

Gate 1 — 환각: PASS. Every KEEP_AS_IS classification in the Target Table/
  Column/API Inventory documents cites the specific model/migration file
  that already implements it — none are asserted from the corrected
  framing's description alone. Every UNDECIDED/PM_DECISION_REQUIRED item is
  presented with real options and reasoning, never silently resolved to a
  single invented answer (Group-vs-Family naming, Auth/Session model choice,
  MarkPoint's URL-scoping convention, and the two data-migration questions
  are all left open with the evidence for a PM to decide, not settled here).
Gate 2 — 누락: PASS. All 10 required Axis-B documents were produced; every
  legacy table/route/auth-mechanism from the Axis-A inventory received an
  explicit classification in the Legacy-to-Target Mapping (summarized:
  3 KEEP_AS_IS, 7 TRANSFORM, 1 MIGRATE_DATA, 3 DEPRECATE, 1 DELETE_CANDIDATE,
  1 REFERENCE_ONLY, plus one UNDECIDED scoping question) — none were left
  unclassified.
Gate 3 — 오작업: PASS. Confirmed via `git status`/`git diff --check` above:
  only documentation files exist across both phases; zero product code,
  migration, or DB file was created or modified; the 7 Axis-A documents were
  edited only to prepend a short banner, their factual content is byte-for-
  byte otherwise unchanged (confirmed by having made only `Edit` calls that
  inserted text before the existing `Task:` line, never touching content
  after it).
Gate 4 — 중심축: PASS. This is the gate the PM's correction was specifically
  about, and every new document keeps current-DB-fact (Axis A, by reference)
  visibly separate from target-proposal (Axis B, this phase) — no document
  conflates "this is how it works today" with "this is what Mongle should
  be." Every proposed target name for an *already-implemented* Mongle
  element is that element's actual current name (no invented parallel
  naming); every genuinely new proposal (Session table shape, Auth
  credential shape) is explicitly marked provisional/UNDECIDED, not
  presented as decided.
Gate 5 — Stale: PASS. Re-verified this correction did not require
  re-measuring HEAD/dirty-state (unchanged since the Axis-A phase, confirmed
  above) since no code was touched in between. Design documents
  (DORAN_MESSAGING_CONTRACT.md and siblings) remain deliberately untreated
  as ground truth for any classification in this phase either — every
  KEEP_AS_IS/TRANSFORM/DEPRECATE classification traces to current code, not
  to what an older design document once proposed.

Final Verdict: READY_FOR_DATA_BACKEND_CONTRACT_PM_FREEZE
  (superseding the prior Axis-A verdict; the underlying execution evidence
  it was based on remains valid and is not re-earned, only re-framed)

Next authorized action: PM review of the 10 new Axis-B documents,
  specifically the open PM_DECISION_REQUIRED items: (1) whether "Group"
  stays Family-specific or generalizes; (2) the Account-native Auth/Session
  model (three candidate options presented in the Business Glossary); (3)
  whether the already-seeded Role/Permission codes are final under this
  corrected framing; (4) MarkPoint's target URL-scoping convention; (5) the
  two data-migration questions (existing identities, existing point/mission
  history). No FE<->API<->DB vertical wiring for A1/A3/A4/A5, and no
  MarkPoint TRANSFORM work, should start before these are resolved and a
  Contract Freeze is issued — this repeats, unchanged, the standing
  instruction already recorded in the main worktree's agent-system/
  active.md entry for this Task ID.
```
