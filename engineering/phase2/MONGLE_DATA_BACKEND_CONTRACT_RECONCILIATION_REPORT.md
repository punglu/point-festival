# MONGLE_DATA_BACKEND_CONTRACT_RECONCILIATION_REPORT

> **SUPERSEDED — retained as the Axis-A (LEGACY_CURRENT_STATE) closeout
> record only.** PM corrected this task's central axis after this report
> was written and its "READY_FOR_DATA_BACKEND_CONTRACT_PM_FREEZE" verdict
> was given: the legacy players/admin_auth/PIN structure this report treated
> as reconciliation-ready is explicitly not the target architecture. The
> execution evidence in this report (migration-chain verification, 71/71
> backend tests, git/diff-check state) remains true and is not repeated —
> it is cited from the new final report,
> `MONGLE_TARGET_ARCHITECTURE_RECONCILIATION_REPORT.md`, which carries the
> current verdict. Do not treat this file's verdict as current.

```text
Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001
Worktree: /Users/mac/mac_Project/mongle_ui-data-backend-worktree (isolated)
Branch: data-backend-contract-reconciliation
Exact HEAD: 6c633679c6708a21920f0e4b306bc1e36a2ea72d (unchanged start->end)
Start status: clean at 6c63367 (worktree freshly created from this commit)
End status: clean tracked tree; 6 new untracked documentation files; no commits made

Note on the reported baseline: the task prompt reported "HEAD prefix: 9bcd1a5"
and "승인된 untracked 문서 3개만 존재" (only 3 approved untracked docs). Both were
re-measured and found stale by the time this task actually started: the main
worktree had advanced one commit (6c63367, a Wave 6.1 governance-only doc
commit made by a separate task in this same session) past 9bcd1a5, and that
same commit had already committed the three previously-untracked
MONGLE_W6_1_E2E_* docs into git history, so they no longer appear as
untracked. Per this task's own Gate 5 instruction ("이 목록과 실제 상태가 다르면
수정하지 말고 보고한다"), this is reported as a discrepancy, not silently
corrected or hidden.

Also relevant to this task's Start Gate: a prior attempt at this exact Task ID
(a separately-launched agent session working in
/private/tmp/.../scratchpad/data-backend-contract-worktree, detached at
9bcd1a5) stalled due to a token-limit conflict before completing. That
worktree was left untouched by this task (read-only `git status` only, to
confirm nothing there needed rescuing) — it had produced 5 of this task's 7
required documents as untracked files, but this task did not adopt them
sight-unseen; each document here was independently re-derived from source and
happens to reach substantially the same conclusions in places, which is
expected given both attempts read the same repository, not evidence that one
copied the other.

Documents created:
  engineering/phase2/MONGLE_DATA_NAMING_CONTRACT_V0_1.md
  engineering/phase2/MONGLE_CURRENT_TABLE_DICTIONARY.md
  engineering/phase2/MONGLE_CURRENT_COLUMN_DICTIONARY.md
  engineering/phase2/MONGLE_BACKEND_API_CONTRACT_INVENTORY.md
  engineering/phase2/MONGLE_SCREEN_DATA_CONTRACT_MATRIX.md
  engineering/phase2/MONGLE_DB_BACKEND_GAP_REPORT.md
  engineering/phase2/MONGLE_DATA_BACKEND_CONTRACT_RECONCILIATION_REPORT.md (this file)
Documents modified: none

Current tables: 33 application tables (15 legacy, from database/init.sql; 18
  Foundation/Doran/Outbox, from 4 Alembic revisions on top of a no-op legacy-
  baseline stamp revision) + alembic_version = 34 relations, confirmed by a
  live `\dt` against an isolated PostgreSQL 16.9 instance built by applying
  init.sql then running `alembic upgrade head` to completion with zero errors
  and zero branch points in the revision chain.
Current columns: every column of all 33 tables is itemized in
  MONGLE_CURRENT_COLUMN_DICTIONARY.md, each cross-checked against its ORM
  model source.
Current API operations: 88 distinct HTTP operations across 16 domain routers
  + 1 health check, itemized in MONGLE_BACKEND_API_CONTRACT_INVENTORY.md with
  method/route/auth-dependency/service/tables/consumer status for each.
Verified domains: player, auth, mission, mission_template, level_tier,
  daily_point, deduction, cheer, feedback, chat, notification, config,
  login_log, admin (aggregator, no own tables), family, doran, service_outbox
  — all 17 read directly (models + routers + schemas + at least one service
  file each; deeper service-layer reads for family/doran/mission/player/
  level_tier/config given their higher complexity and cross-cutting role).

Naming conflicts: 4 found and recorded in MONGLE_DATA_NAMING_CONTRACT_V0_1.md
  §4 — family_id vs family_group_id (same value, two names depending on
  layer); membership_id vs family_membership_id (same referent, two schema-
  level names); two functions both literally named get_current_user in
  different modules with different accepted roles and different return
  shapes; the frontend's Doran preview fixture's own `kind` field vs the real
  API's `room_type` field (not yet a live mismatch only because nothing calls
  the real API yet).
Table grouping conflicts: none found. All 33 tables sort alphabetically into
  exactly their correct domain families with zero manual regrouping needed
  (see MONGLE_CURRENT_TABLE_DICTIONARY.md's alignment-check section) — every
  table already has a real, correctly-scoped, single-Aggregate name.
Column synonym conflicts: total_points (derived, SUM(daily_points.balance),
  current spendable balance) vs total_earned (players column, lifetime,
  leveling input only) — legitimately different concepts, but named closely
  enough to invite confusion; recorded as the likely root cause of A1/A3
  never having wired up the real level system (see Gap G2/G3).
Stale contracts found: the frontend's entire Doran/와글와글 (A4) UI renders
  from static preview fixtures (platform/doran/preview/*.ts), not any live
  API call — confirmed by direct source read of DoranLanding.tsx's import
  list, not inference from a design document. A1's login-screen level badge
  fetches a config key (level.thresholds) that is never seeded anywhere and
  is behind auth it doesn't have at that point in the flow, instead of the
  real, working, tested level_tiers/level-tiers API (which itself has zero
  frontend callers anywhere in the app, on any screen).

NO_CHANGE_REQUIRED: G6, G7, G8 (API layer only), G9, G10 (see Gap Report for
  full list and reasoning per item)
DOCUMENTATION_ONLY: G3, G4, G6, G7, G10, G13, G14
API_ADAPTER_REQUIRED: G1 (rooms/messages/participants/read-state wiring),
  G2 (level display wiring)
API_CHANGE_REQUIRED: none classified as strictly required (G1's batch-
  room-list gap is classified QUERY_OR_READ_MODEL_REQUIRED instead, since no
  existing endpoint needs to change, a new one needs to be added)
QUERY_OR_READ_MODEL_REQUIRED: G1 (batch room-list-with-preview-and-unread
  endpoint does not exist in any form today)
MIGRATION_REQUIRED: G5 (missions.status CHECK constraint missing `cancelled`,
  which application code already references) — conditionally, pending a
  product decision on whether `cancelled` should be a real, permanent status
  or whether the application-code reference to it is the stale side instead;
  G11 (reply_to_message_id has no FK) — conditionally, pending a decision on
  whether reply integrity should be DB-enforced
UNKNOWN: G12 (doran_rooms.version column has no confirmed read/write site
  anywhere in doran/service.py)

Product code changed: NONE (git status confirms zero changes under
  backend/**, frontend/**, database/** in this worktree — see Start/End
  status above)
Database changed: NONE (no migration created or modified; the isolated
  PostgreSQL instance used for verification was a throwaway standalone
  Docker container, never the tracked docker-compose.phase1.yml stack, and
  was destroyed at the end of this task)
Production DB accessed: NEVER — this task never held credentials for, and
  never attempted to reach, any operating/NAS/production database
Commit/push/PR: NONE performed (git log confirms HEAD unchanged; no
  git add/commit/push/merge/rebase/reset/restore/clean/stash was run)

Gate 1 — 환각: PASS. Every table/column/API/naming claim in all 7 documents
  cites a specific file path and, where a claim could be verified by
  execution, an actual command result (34-relation `\dt` output, 71/71
  pytest pass, a real 401 reproduced empirically in the prior A1 task and
  re-confirmed here by source-reading the exact auth dependency that causes
  it). Distinguished `current` fact from `proposed`/`canonical` naming
  throughout — the Naming Contract and Table Dictionary both keep separate
  columns for "as it exists" vs "canonical proposed name," and every
  proposed name in this pass is identical to the current name (no invented
  target names beyond what direct evidence already supports).
Gate 2 — 누락: PASS. All 5 Alembic migrations and all 17 domains' models
  were read in full; all 5 required screens (A1/A2/A3/A4/A5) have a
  completed row-by-row data-contract pass; PK/FK/constraint/index/status/
  permission columns are itemized per table in the Column Dictionary;
  4 naming conflicts and their synonyms are recorded explicitly rather than
  silently resolved.
Gate 3 — 오작업: PASS. Confirmed via `git status`/`git diff --check` above:
  only new documentation files exist; zero migration files created or
  edited; zero ORM/router/service/schema files touched; zero frontend files
  touched; the standalone verification Postgres container and Python venv
  used for migration/test verification were both destroyed at the end of
  this task (`docker rm -f`, `rm -rf` of the venv), confirmed by a follow-up
  `docker ps -a` filter returning empty. Every rename candidate in the Table
  Dictionary is explicitly classified KEEP with a stated reason, never
  written as an implicit instruction to rename now.
Gate 4 — 중심축: PASS. No screen implementation, no FE type file, no
  ViewModel component code was written — only documentation describing what
  a future ViewModel/ATA could look like. Current-DB-fact and future-DB-
  proposal are kept in visibly separate columns throughout (current_
  physical_name vs canonical_proposed_name; 현재 제공 여부 vs API/DB 변경 필요
  여부). No product/physical/API/FE-ViewModel term was conflated — the
  Naming Contract's Business Glossary table has a dedicated column for each
  layer's own term precisely to keep them distinguishable.
Gate 5 — Stale: PASS. Re-measured HEAD and dirty-state independently rather
  than trusting the task prompt's reported values (see the Note above — a
  real, material discrepancy was found and reported, not silently
  reconciled). Design documents (DORAN_MESSAGING_CONTRACT.md and siblings)
  were deliberately not treated as ground truth for any Gap or Screen-
  Matrix finding — every finding in this report traces to current code,
  current migrations, or a command actually run this task, per the
  document's own stated priority order.

Final Verdict: READY_FOR_DATA_BACKEND_CONTRACT_PM_FREEZE

Next authorized action: PM review of the 6 content documents above,
  particularly: (1) the Doran frontend-disconnect finding (G1) and whether
  wiring A4 to the real API is the next Wave's priority; (2) the
  level.thresholds/level-tiers gap (G2) and which fix path to authorize;
  (3) the missions.status CHECK-constraint/application-code mismatch (G5)
  and whether a migration is warranted; (4) whether to authorize a PM
  Contract Freeze on the naming/table/column contracts as currently
  documented, per this task's own stated purpose as the prerequisite for
  future FE<->API<->DB vertical-slice work. No FE<->API<->DB vertical wiring
  should start before that Freeze decision, per this task's own scope and
  per the standing instruction already recorded in the main worktree's
  agent-system/active.md placeholder for this Task ID.
```
