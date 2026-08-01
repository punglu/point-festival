# Active Tasks

Only open tasks belong here. Lifecycle, decision, verification, and execution
are separate axes.

## MONGLE-W6-R2-1C-POINT-FESTIVAL-MOBILE-VISUAL-001

- Task ID: MONGLE-W6-R2-1C-POINT-FESTIVAL-MOBILE-VISUAL-001
- Lifecycle: COMPLETE
- Decision: DESIGN_APPROVED (PM canonical screen direction, 2026-08-01)
- Verification: GPT_VISUAL_GATE_PASS / SOURCE_SEPARATION_PASS
- Execution: SUCCEEDED
- Closeout Contract: v1
- Scope: mobile-only, presentation-only preview route `/__wave6/1c` for
  canonical screen `1c` / `포인트 잔치`; no dashboard replacement or API/session
  connection.
- A1 protection: required — no A1 source, route, or screenshot mutation.
- Measured evidence: 1c GPT visual review and zero-change source separation both
  passed. The three 375/390/430 post-move PNG hashes are byte-identical to the
  pre-move captures; browser audit remains API/WebSocket/storage/navigation 0.
  1e admin canonical measurement is next; tablet remains not started.

## Approved Target decision baseline (D1–D8)

`engineering/phase2/MONGLE_TARGET_DECISION_FREEZE.md` is the Target product
contract SSOT. **D1–D8 are `APPROVED` / `FROZEN` (PM, 2026-08-01).** No task may
record D1–D8 as its blocker, and no task may reopen, narrow or widen them
without a new PM decision. An approved decision is binding design, not evidence
that anything implementing it exists.

## D6-P1–D6-P8 — deferred Wagle implementation policies

- Status: `DEFERRED_TO_RELEVANT_TASK_START_GATE`
- Current default: **none — no default value has been chosen for any row.** Do
  not infer one from legacy behaviour, from another product, or from an existing
  fixture.
- Decision deadline: before the Start Gate of the related implementation task.
- If undecided: that task **cannot start** and must not be promoted to
  `READY_FOR_IMPLEMENTATION`.
- Decomposition impact: `NON_BLOCKING_FOR_DECOMPOSITION` — the D6 core contract,
  the Wave plan and every unrelated task proceed normally.

| Decision ID | Deferred policy | Blocks the Start Gate of |
|---|---|---|
| D6-P1 | Push 알림 본문 공개 수준 | PWA Push subscription/payload task |
| D6-P2 | Room별 mute 및 알림 설정 | Room notification-settings task |
| D6-P3 | Push 묶음 기준(foreground 억제 포함) | Push dispatch task |
| D6-P4 | 읽음 표시 방식 | Read-state UI task |
| D6-P5 | 온라인 상태·마지막 접속 공개 여부 | Presence task |
| D6-P6 | 메시지 수정·삭제 정책 | Message mutation task |
| D6-P7 | 메시지·시스템 이벤트 보존 기간 | Retention task |
| D6-P8 | 오프라인 발신 Queue의 v1 포함 여부 | Offline outbound queue task |

## MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001
- Kind: backend fix + regression tests — registers, root-cause-fixes and
  hardens the previously uncommitted/unregistered credential-surface change
  that closes backend gap "BG-1" (`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`'s
  `BLOCKED` finding)
- Lifecycle: IMPLEMENTED_AWAITING_INDEPENDENT_QA
- Decision: DESIGN_APPROVED (PM, via "그래" — item 5 of the 5 reviewed PM
  decision items, then "근본적 해결을해라 / 임시 해결말고" directing a
  root-cause fix rather than a documented workaround)
- Verification: SELF_CHECK_PASS / INDEPENDENT_QA_BLOCKED_THEN_CORRECTED /
  INDEPENDENT_RE_QA_CONDITIONAL (targeted repair evidence PASS twice; complete
  independent full-suite regression NOT_RUN_TO_COMPLETION)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md
- Result: the pre-existing uncommitted fix in `app/dependencies.py` /
  `family/service.py` (widened `get_current_user` role set to
  `{player, admin, account}`) was re-measured live and confirmed working
  (`/api/account-context` 401→200 for an Account token), then root-cause
  corrected: its Account-branch had duplicated
  `family/dependencies.py::get_current_account`'s Session-liveness check
  verbatim (own docstring admitted it). Extracted to one shared function,
  `auth_service.resolve_account_from_session_claim`, now the single call
  site both entry points delegate to. All 38 `Depends(get_current_user)`
  usages across 8 files enumerated for unsafe direct `user["sub"]`
  extraction (the identity-confusion/IDOR risk an `account`-role `sub`
  being an `account_id`, not a `player_id`, could create) — none found;
  the one direct-extraction site (`feedback/router.py`) sits behind an
  explicit role gate that rejects `account` tokens first.
- Test evidence: 33/33 Wave 1 account-auth tests, 41/41 Wagle/family tests,
  5/5 new regression tests (`test_bg1_credential_surface_unification.py`),
  full suite 317 passed / 0 failed / 0 errors (re-run twice; an
  interleaved first run's 3 failed/11 errors traced to pre-existing
  cross-file batch DB-connection contention unrelated to this change —
  same files 86/86 clean standalone).
- Environment: disposable `postgres:16.9-alpine` (port 15435, matches
  `tests/conftest.py`), `database/init.sql` + `alembic upgrade head` →
  `0011`, throwaway Python 3.11 venv (system default 3.9 cannot import this
  codebase). Container and venv torn down after use, zero residue.
- **Correction applied 2026-08-01** after
  `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001` (verdict
  `BLOCKED`, below): a validly-signed Account token with a non-numeric
  `sid` reached `resolve_account_from_session_claim`'s unguarded
  `int(session_id)` and raised an unhandled `ValueError` (500) instead of
  401. Pre-existed in both original duplicated copies; carried forward, not
  introduced, by the consolidation — still had to be fixed before BG-1
  closes. Fixed with the same `try`/`except (TypeError, ValueError)` → 401
  pattern already used for `sub` two lines below. Added regression test 6
  (`test_non_numeric_sid_is_rejected_as_401_not_a_server_error`), confirmed
  via `git stash` to fail pre-fix and pass post-fix. Full suite re-run
  clean on a freshly recreated disposable DB. Detail in the handoff's own
  "Correction applied after independent QA" section and QA evidence §8.
- Next Action: complete an uncontended independent full-backend regression
  before BG-1 is treated as closed for Wave 6 Target UI purposes. The `sid`
  repair itself passed independent targeted QA twice; no lifecycle closure is
  inferred from that bounded result.

## MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: CONDITIONAL
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- Handoff Path: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md

## PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002

- Task ID: PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002
- Kind: second execution of the `AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md` brief.
  A new ID because `-001` is already in `graduated/2026-08.md` with its handoff
  archived, and Invariant #1 forbids one Task ID resolving to both an open and
  a closed location. That graduated row itself names "a separate future task"
  as the owner of findings F1–F4; this is it.
- Lifecycle: IMPLEMENTED_AWAITING_INDEPENDENT_QA
- Decision: DESIGN_APPROVED (standing PM brief, re-issued 2026-08-01)
- Verification: CONDITIONAL (self-check) / INDEPENDENT_QA_PENDING
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002.md
- QA Evidence: agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002.md
- Baseline: `dev-newmarkp` @ `25c8d0c`, unchanged start → end. No commit.
- Clean: Invariant #1 violations 0; graduated rows with a dead git ref 0 (29
  checked); missing archived handoffs 0; `SUCCEEDED` handoffs declaring absent
  files 0; `CLAUDE.md` still a 46-line thin pointer with no re-accumulated
  state. The predecessor's two named untracked commits (`0393971`, `91eb98e`)
  are now traceable — that finding is closed by evidence, not assertion.
- Applied (registration/consistency only, no status raised): the **9 F1–F4
  registrations** (block above, all `NOT_TESTED`); three Closeout blocks whose
  field values shared a line with their explanations and so parsed as empty;
  two graduated Wave 3 handoffs still declaring `handoffs/active/` paths.
  `check_closeout.py` warnings **14 → 6**.
- **A correction to my own finding, kept visible rather than replaced:** F-B was
  first recorded as "gate PASS while handoff and QA evidence do not exist". That
  was wrong — both files exist and the gate is properly backed; the defect was
  that the checker could not parse the block. I had reported a checker message
  as a fact about the repository without opening the files it named, which is
  the exact failure this audit exists to catch.
- Concurrent writer: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001` was added to this
  file by another writer **during** the audit. My edit was verified purely
  additive (62 insertions, their section intact). Their files were not touched.
- Open findings left for their owners: F-A (2 docs-only untraceable commits),
  F-C (that task's handoff/QA carry no `- Task ID:` line), F-D (3 open tasks
  with no handoff), and the long-standing `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`
  gap.
- Independent QA: **complete — CONDITIONAL** (2026-08-01,
  `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001`, see
  below). Every clean-finding claim (Invariant #1: 0 violations,
  re-checked directly against the current file set; graduated git refs:
  spot-checked, all exist; row-count reconciliation: 29 at this task's own
  snapshot = 18 in `2026-08.md` + 11 in `2026-07.md`, both independently
  recounted) re-confirmed true. **One new registration gap found that
  post-dates this task's own git_ref snapshot and could not have been
  caught by it**: `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001` (below) —
  the same failure shape this audit exists to catch, recurring immediately
  after the previous pass. Registered as part of the independent QA's own
  in-scope registration-fix authority, following this task's own F1–F4
  precedent.
- PM Disposition (2026-08-01): items 1 (F-C) and 2 (nine F1–F4 tasks) are
  resolved — item 1 self-resolved, item 2 graduated as historical to
  `graduated/2026-08.md` (self-reported only, not independently QA'd).
  Item 3 (`42fa4ae`/`9220859`) resolved as `NO_RETROACTIVE_TASK_ID` /
  `PRE_SYSTEM`. Full disposition text in this task's own QA evidence.
- Next Action: item 4 (`PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`, flagged
  as next priority) remains open. Item 5's re-verification is **complete —
  see `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001`** below: the BG-1 fix was
  found already present but unregistered, root-cause corrected (a
  duplicated security check consolidated into one shared function), and
  regression-tested; independent QA of that task is the new open item.

## PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001

- Task ID: PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001
- Kind: independent QA of `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002`,
  re-running the `AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md` brief's own 8-step
  method against current repository state rather than re-reading -002's
  report as evidence.
- Lifecycle: IN_PROGRESS (evidence complete; PM decision pending)
- Decision: DESIGN_APPROVED (process task)
- Verification: CONDITIONAL
- Verification detail: `INVARIANT_1_CLEAN` (re-confirmed), `GRADUATED_REFS_
  CLEAN` (re-confirmed), `NEW_UNREGISTERED_TASK_FOUND_AND_FIXED`
  (`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Branch / Start HEAD: `dev-newmarkp` / `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
  (unchanged end, no commit)
- Result: -002's own claims re-verified against the live repository, not
  accepted from its report: Invariant #1 (0 overlap between `active.md`
  headers and `graduated/*.md` rows, re-extracted and `comm -12`'d
  directly); 4 graduated git refs spot-checked via `git cat-file -e` (all
  exist); `check_closeout.py`/`check_active.py`/`check_handoff_refs.py`
  re-run live (not read from a prior log) — confirmed -002's F-B/F-C format
  fixes are actually in effect (those specific warnings no longer appear);
  confirmed `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`'s QA-evidence and
  Closeout-block gaps are still present, unchanged (2 checker warnings).
  **New finding**: `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001` has real
  product code (10 new + 6 modified frontend files, matching this session's
  own `git status` exactly), a real QA report with an honest `BLOCKED`
  verdict (no false PASS), but was registered in **neither** `active.md`
  nor `graduated/` — and its own Closeout Synchronization block falsely
  claimed `ACTIVE: UPDATED` and a specific `HANDOFF Path` that did not
  exist, independently confirmed by `check_closeout.py`'s own live output
  ("QA evidence declares Closeout Contract v1 but no active or archived
  handoff exists"), not merely by this session's manual grep. Fixed: task
  registered in `active.md` (below), the missing handoff synthesized from
  its own already-real QA evidence content (no fabrication — every claim in
  the handoff traces to a section of the existing report), and the QA
  report's own Closeout Synchronization block corrected to match what is
  now actually true. The task's own substantive verdict (`BLOCKED` on
  backend gap BG-1) was **not** touched or re-judged — that is product
  verification, out of this registration-integrity audit's scope.
- Handoff: agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001.md (QA evidence serves as handoff, same convention as MONGLE-W1-INDEPENDENT-QA-001)
- QA Evidence: agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001.md
- Next Action: PM decision on whether `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`'s
  `BLOCKED` verdict (backend credential-surface gap "BG-1") is accepted as
  the accurate current Wave 6 blocker, and whether independent QA of its
  substantive frontend/backend-gap claims is warranted before the
  recommended follow-up (a backend task unifying the credential surface) is
  opened.

## MONGLE-W1-INDEPENDENT-QA-001 (independent QA of Wave 1)

- Task ID: MONGLE-W1-INDEPENDENT-QA-001
- Kind: independent QA / test / minimal defect correction
- Execution Target: MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001 (six Wave 1
  Backlog tasks: `MONGLE-W1-CREDENTIAL-SESSION-DB-CONTRACT-CORRECTION-001`,
  `MONGLE-W1-SCOPED-RBAC-001`, `MONGLE-W1-ACCOUNT-CREDENTIAL-001`,
  `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001`,
  `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001`,
  `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001`)
- Lifecycle: IN_PROGRESS (evidence complete; PM graduation decision pending,
  per the same pattern as `MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001`)
- Decision: DESIGN_APPROVED (this QA task itself is process, not a new
  product decision; D1–D8 remain frozen and out of scope for re-approval)
- Verification: PASS
- Execution: SUCCEEDED
- Closeout Contract: v1
- Result: `WAVE_1_INDEPENDENT_QA_PASS` / `WAVE_1_LIFECYCLE_COMPLETE` /
  `READY_FOR_WAVE_2_START_REVIEW`. All six Wave 1 Backlog tasks and the
  `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` bundle independently re-verified:
  104/104 backend tests reproduced from a freshly created disposable Postgres
  16.9 container (not the implementer's leftover environment), migration
  `0000`→`0006` fresh-upgrade / `downgrade -1`+re-upgrade / full downgrade-to-
  `0004`+re-upgrade all confirmed by direct SQL (zero residue/duplicates), the
  8 new API routes exercised at real HTTP level, token/session/RBAC/
  cross-family/last-admin/FamilyAdmin-issuance boundaries independently
  re-checked against source. No new defect found; the pre-existing
  `0001`-seed FamilyAdmin→ServiceAdmin auto-grant (already fixed by the
  implementer's migration `0006`) was independently confirmed fixed, not
  merely re-read. Two minor test-coverage gaps recorded, not defects (see QA
  Evidence §10/§15/§26). git_ref unchanged, no commit/push.
- Branch / Start HEAD: `dev-newmarkp` / `da7ea7403aefef33a90d622940724b0c53ee88` — re-measured at start, see relay
- Start dirty state: 34 modified tracked files + untracked entries carried
  over from prior sessions (Wave 1 bundle's own changes plus pre-existing
  unrelated dirty files). Preserved, not reset/restored/cleaned/stashed.
- Allowed file areas (defect-correction scope, Wave 1 approval boundary
  only): `backend/app/domains/family/**`, `backend/app/domains/auth/**`,
  `backend/alembic/versions/0005*`, `backend/alembic/versions/0006*`,
  `backend/app/models/all_models.py`, `backend/app/config.py`,
  `backend/tests/**`, the Target Table/Column/API/Role Matrix docs already
  owned by Wave 1, `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`,
  `agent-system/qa/COVERAGE_MAP.md`, `agent-system/active.md`,
  `agent-system/relay/current.md`.
- Forbidden: re-opening D1–D8; scope beyond the six Wave 1 tasks; Doran/Wagle/
  Markpoint domain code; frontend source; `database/init.sql`; migrations
  `0000`–`0004`; any Legacy backfill; commit/push/merge/rebase/PR; touching
  the 33 other pre-existing dirty files unrelated to Wave 1.
- Test environment: disposable, volume-less PostgreSQL container (never the
  persistent `mc-db` dev runtime).
- Defect-correction condition: only confirmed Wave 1 defects, minimal fix,
  targeted + regression re-test, no scope creep.
- PASS/FAIL exit condition: per the task's own Lifecycle section (§23) —
  PASS requires all six Wave 1 tasks' requirements, migration reproduction,
  new-API HTTP tests, session security, multi-family isolation, RBAC,
  FamilyAdmin issuance and regression all independently verified, five gates
  clean.
- QA Evidence: `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`
- Next Action: PM decision on graduating this task and
  `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` (plus the six Backlog tasks it
  executed) to `graduated/`; separately, PM review of the `0006` RBAC
  registry correction on its own merits (process review of an
  already-independently-verified-correct fix). Wave 2 Start Review is
  unblocked by this PASS.

## MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001 (execution bundle)

- Task ID: MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001
- Kind: execution bundle — an identifier for one single-writer session, **not** a
  new product task. It does not replace or supersede any Backlog Task ID.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM autonomous-execution directive, 2026-08-01)
- Verification: PASS (self-check, now independently confirmed — see below)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Result: all six Wave 1 Backlog tasks implemented. 33 new tests, **104/104**
  backend suite passing, zero regressions, HEAD unchanged, no commit. Verdict
  `WAVE_1_IMPLEMENTATION_COMPLETE` / `WAVE_1_TESTS_PASS` /
  `WAVE_1_QA_CONDITIONAL` / `NOT_READY_FOR_WAVE_2` **superseded by independent
  QA PASS below.**
- Security finding (fixed): the `0001` seed auto-granted
  `markpoint.missions.manage`/`markpoint.points.adjust` to FAMILY `owner`/`admin`,
  violating D4's no-automatic-ServiceAdmin rule and bypassing the
  ServiceSubscription gate. Removed in migration `0006`. Current product impact
  verified nil (no route reads those codes yet); it would have activated at the
  Wave 4/5 Markpoint authorization transform.
- QA Evidence: agent-system/qa/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md
- Independent QA: **complete — PASS** (2026-08-01, `MONGLE-W1-INDEPENDENT-QA-001`,
  see `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`). Security, DB and
  authorization boundaries, and the `0006` RBAC registry correction were all
  independently re-verified against source and a freshly created disposable
  DB, not accepted from this bundle's own report.
- Branch / Start HEAD: `dev-newmarkp` / `da7ea7403aefef33a90d622940724b0c53ee8873`
- Start dirty state: 28 modified tracked files + 65 untracked entries, all owned
  by prior sessions/tasks. Preserved, not reset/restored/cleaned/stashed.
- Backlog Tasks executed by this bundle, in fixed order:
  `MONGLE-W1-CREDENTIAL-SESSION-DB-CONTRACT-CORRECTION-001` (1B),
  `MONGLE-W1-SCOPED-RBAC-001` (1C),
  `MONGLE-W1-ACCOUNT-CREDENTIAL-001` (1D),
  `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001` (1E),
  `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` (1F-1),
  `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001` (1F-2).
- Allowed file areas: `backend/app/domains/family/**`,
  `backend/app/domains/auth/**` (new Account-native modules only),
  `backend/alembic/versions/**` (new revisions only),
  `backend/app/models/all_models.py`, `backend/tests/**`,
  `engineering/phase2/MONGLE_TARGET_{TABLE,COLUMN}_DICTIONARY.md`,
  `MONGLE_TARGET_API_INVENTORY.md`, `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md`,
  `MONGLE_IMPLEMENTATION_BACKLOG.md`, `MONGLE_DOD_AND_TEST_MATRIX.md`,
  `agent-system/qa/**` (this bundle's own evidence + Coverage Map),
  `agent-system/active.md`, `agent-system/relay/current.md`.
- Forbidden areas: the 28 pre-existing dirty files not listed above; Wagle/Doran
  domain code; Markpoint domain code (`mission`, `daily_point`, `deduction`,
  `cheer`, `feedback`, `notification`, `level_tier`, `admin`); frontend source;
  `database/init.sql`; existing migrations `0000`–`0004`; any Legacy data
  backfill; commit/push/merge/rebase/PR.
- Next Action: independent QA **complete — PASS** (2026-08-01). Remaining:
  PM review of the `0006` RBAC registry correction on its own merits, and PM
  decision on graduating this bundle plus the six Backlog tasks to
  `graduated/`. The five Wave 1 FE slices and Wave 2 are unblocked by this QA
  PASS to proceed to their own Start Gates / Start Review.

## MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001

- Task ID: MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: A1_IMPLEMENTATION: COMPLETE / A1_PM_VISUAL_GATE: PENDING /
  A1_INTEGRATION: **DONE — see location correction below** / A1_FINAL:
  CONDITIONAL (PM verdict, 2026-07-31).
  **Location correction (MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001, 2026-08-01,
  originally found by PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001 F6):** the
  previous sentence here claimed this task's code and evidence "live in an
  isolated worktree, never committed to this branch"
  (`/Users/mac/mac_Project/mongle_ui-a1-visual-worktree`, branch
  `w6-2-a1-visual`, pinned at HEAD `9bcd1a5`). That is no longer true and is
  retained above only as the superseded claim. Merge commit `a1fe979`
  (`merge: integrate A1 mobile visual publishing candidate`) already landed the
  A1 reports and real product code into this branch, and the named worktree path
  is confirmed absent from disk (`git worktree list` + direct path check,
  2026-08-01). **This corrects only "where the files are", not the task's
  Verification/Decision status** — A1_PM_VISUAL_GATE and independent QA remain
  outstanding exactly as before. PM
  directed 5 follow-up items: settings icon wired to the existing admin-login
  entry (DONE, re-verified — lint/build/target-E2E PASS, click-through
  confirmed), lock-notice copy kept generic with no invented counts/times
  (already satisfied pre-PM-decision), level/job-title/lock-detail kept as
  documented DATA gaps rather than hardcoded (already satisfied), the Avatar
  status-dot clip NOT worked around in A1 files (already satisfied — see
  MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001, handled as its own task instead).
- Handoff: engineering/phase2/MONGLE_W6_2_A1_MOBILE_VISUAL_PUBLISHING_REPORT.md,
  MONGLE_W6_2_A1_VISUAL_DELTA.md, MONGLE_W6_2_A1_TOKEN_PRIMITIVE_GAPS.md
  (all three are now present in **this** worktree via `a1fe979`; the earlier
  "inside the isolated A1 worktree, not this one" note is superseded — see the
  Location correction in the Phase Note. No `agent-system/handoffs/active/`
  file exists for this task; its reports serve as the handoff.)
- QA Evidence: none in this worktree — self-check only, recorded in the three
  reports above
- Independent QA: not started — gated behind A1_PM_VISUAL_GATE and the Avatar
  fix's own independent QA
- Next Action: PM Visual Gate review of the three A1 reports (Visual Delta's
  remaining sign-off items: pre-login level-pill 401, missing job-title/lock-
  detail API fields, rewritten lock-notice copy). **Revised 2026-08-01:** the
  "integrate A1 into this authoritative worktree ... then remove the isolated
  worktree" steps are already done (`a1fe979`; path confirmed absent), so what
  remains is the PM Visual Gate plus re-running
  lint/build/target-E2E/auth-flows/admin-entry/screenshot/console **here**
  against the merged code, gated behind the Avatar fix's own independent QA.

## PHASE2-DORAN-MESSAGING-CONTRACT-001

- Task ID: PHASE2-DORAN-MESSAGING-CONTRACT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_REQUIRED
- Handoff: agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-CONTRACT-001.md
- QA Evidence: agent-system/qa/PHASE2-DORAN-MESSAGING-CONTRACT-001.md
- Independent QA: not_applicable — contract design; implementation QA required
- Next Action: PM review of five bounded Doran messaging gates before Foundation implementation
- PM Decision Snapshot (2026-08-01): `D6: APPROVED` — WebSocket foreground realtime, PWA Web Push, durable DB SSOT, transactional Outbox, at-least-once delivery, idempotent deduplication, per-Room ordering, reconnect recovery, multi-family Push and failure isolation are mandatory implementation contract. `D6-P1` through `D6-P8`: `DEFERRED_TO_RELEVANT_TASK_START_GATE` and `NON_BLOCKING_FOR_DECOMPOSITION`; each directly related task must resolve its policy at its own Start Gate. Register: the D6-P table at the top of this file.

## PHASE0-DOC-STALENESS-PREVENTION-001

- Task ID: PHASE0-DOC-STALENESS-PREVENTION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-DOC-STALENESS-PREVENTION-001.md
- QA Evidence: agent-system/qa/PHASE0-DOC-STALENESS-PREVENTION-001.md
- Independent QA: not_applicable — documentation/process rule change; no
  product code, DB, or auth touched
- Next Action: PM review of the new Documentation change routing tiers,
  Invariants 9-11, and Prohibited actions list in rules.md; decide whether to
  port the source template's structural-validation script into
  agent-system/tools/

## PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2

- Task ID: PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: SELF_CHECKED / INDEPENDENT_QA_PENDING — registration gap found and
  corrected 2026-07-31 (task existed in handoffs/qa since commit `a1575e0`,
  2026-07-26, but was never added here). Later commits `0393971` (service
  principal and room binding), `91eb98e` (reliable service event delivery) and
  `779cc70` (`fix(mission): serialize point-bearing status transitions`, the
  direct child of `91eb98e`, which adds
  `backend/tests/test_doran_reliable_service_slice.py`) extended the Doran
  domain with no `active.md`/`graduated/` task record; the "remaining work"
  list in the handoff is stale relative to current code. `779cc70` was added to
  this list by MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001 (2026-08-01), per
  PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001 finding F5; all three commits
  are confirmed ancestors of HEAD `da7ea74`. Precision note: technical
  documentation for this work does exist at
  `engineering/phase2/DORAN_FOUNDATION_GAP_ANALYSIS.md` (including a named
  independent-QA reference `PHASE2-DORAN-R2B1-FOCUSED-QA-001` = PASS) — what is
  missing is the Agent System **registration**, not all documentation.
- Handoff: agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md
- QA Evidence: agent-system/qa/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md
- Independent QA: pending — mandatory for security, DB, and service boundaries
- Next Action: PM triage — decide whether to register/re-scope the unregistered
  follow-up Doran work (`0393971`, `91eb98e`, `779cc70`) as its own task(s),
  update the R2 handoff's checkpoint to match current code, then run
  independent QA before any completion or push claim. Wave 2 depends on this
  domain, so its actual state must be verified from source rather than from
  the stale handoff.

## PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001

- Task ID: PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_REQUIRED
- Handoff: agent-system/handoffs/active/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md
- QA Evidence: agent-system/qa/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md
- Independent QA: not_applicable — contract design; Foundation implementation requires independent QA
- Next Action: PM review of five bounded Phase 1 architecture gates before Foundation implementation

## PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001

- Task ID: PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: PHASE0 LEGACY CONTAINMENT COMPLETE / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md
- QA Evidence: agent-system/qa/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md
- Independent QA: complete — PASS (independent read-only security QA)
- Next Action: Phase 0 automated baseline is ready for PM closeout confirmation; push is authorized by this task's passing conditions

## PHASE0-AUTOMATED-GAP-CLOSEOUT-001

- Task ID: PHASE0-AUTOMATED-GAP-CLOSEOUT-001
- Lifecycle: SUSPENDED
- Decision: DESIGN_APPROVED
- Verification: BLOCKED
- Execution: FAILED
- Phase Note: BLOCKED / CORE DEFECT — CURRENT USER OWNERSHIP AND MUTATION AUTHORIZATION
- Handoff: agent-system/handoffs/active/PHASE0-AUTOMATED-GAP-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/PHASE0-AUTOMATED-GAP-CLOSEOUT-001.md
- Independent QA: required for a follow-up core authorization/ownership fix
- Next Action: PM triage and a bounded core authorization/ownership repair task; do not resume automated closeout or push first

## PHASE0-DEV-RUNTIME-RECOVERY-001

- Task ID: PHASE0-DEV-RUNTIME-RECOVERY-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / SELF_CHECKED
- Handoff: agent-system/handoffs/active/PHASE0-DEV-RUNTIME-RECOVERY-001.md
- QA Evidence: agent-system/qa/PHASE0-DEV-RUNTIME-RECOVERY-001.md
- Independent QA: not_applicable — tooling and isolated runtime self-check
- Next Action: PM review; retain the isolated runtime volume only if follow-up regression work needs it

## PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001

- Task ID: PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md
- QA Evidence: agent-system/qa/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md
- Independent QA: not_applicable — documentation localization; PM review required
- Next Action: PM review of localized engineering contracts and five bounded gates

## PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001

- Task ID: PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: PHASE0 AUTOMATED BASELINE COMPLETE / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md
- Independent QA: not_applicable — implementation changed docs, tooling, generated API types, and tests only; no core code or contract behavior changed
- Next Action: PM review, then PHASE0-DEVICE-AND-OPERATIONS-GATE-001 for physical-device and operating-DB rehearsal gates

## MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001

- Task ID: MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: SELF_CHECKED / INDEPENDENT_QA_PENDING — fix implemented (overflow
  clip moved from `.avatar` to a new `.avatarInner` wrapper; `statusDot` is now
  an unclipped sibling). Self-check: 29/29 static contract tests pass (26
  pre-existing + 3 new), lint PASS, build PASS, target E2E
  (specs-mongle/01-shell.spec.ts, iphone+desktop) 27 passed/1 correctly-scoped
  skip/0 failed against a freshly rebuilt image containing the fix, manual
  visual regression check of existing non-status consumers (RoomItem/
  ChatHeader on /wagle) confirmed unchanged. PM-directed 2026-07-31, split out
  of the A1 mobile visual publishing
  task. The shared `Avatar` primitive's `.avatar` rule sets `overflow: hidden`
  to clip its image/fallback to a circle, but `.statusDot` is positioned at
  `right:0; bottom:0` on the same element, so the clip cuts the status dot
  into a quarter-circle instead of a full ringed dot. Zero existing consumers
  (`ChatHeader`/`MessageBubble`/`RoomItem`/`DoranLanding`) pass the `status`
  prop today; A1's `PlayerCard` (isolated worktree, not yet integrated) is the
  first real caller to expose this. PM directed this be fixed as its own task
  rather than worked around in A1's files, per Frontend Development Guide and
  Test Policy (preserve primitive contract, use tokens, verify all Avatar
  size/status combinations, lint/build, component/static tests, A1 target
  Playwright, existing-consumer regression; no test deletion/skip/loosening).
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md
- Independent QA: pending — shared Foundation primitive change
- Next Action: implement the fix in the main worktree, verify against every
  Avatar size/status combination and every existing consumer, then hand off
  for independent QA before A1 integration proceeds

## MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001

- Task ID: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: SELF_CHECKED / READY_FOR_PM_CONTRACT_FREEZE (2026-07-31,
  corrected framing). PM redirected this task's central axis mid-flight,
  after the first pass (Axis A, see below) had already reached its own
  ready-for-freeze verdict: Mongle is a new platform owning Account/Group/
  Membership/Role/Permission/Auth/Session; 와글와글 is a new realtime
  messenger on Mongle; 마크포인트 잔치 is a new service built on Mongle's
  user/group/permission/session structure; the legacy point-festival system
  is reference material only, never the SSOT. HEAD unchanged at `6c63367`
  throughout both phases — no code was touched by the correction, only
  documentation framing.
  Phase 1 (Axis A, LEGACY_CURRENT_STATE — retained, not discarded): full
  DB/backend inventory (5 migrations, 17 domain models, 34 live-verified
  relations, 71/71 backend tests passed against a throwaway isolated
  Postgres instance) — see the 7 documents listed below, now banner-marked
  as Axis A.
  Phase 2 (Axis B, TARGET_MONGLE_ARCHITECTURE — the corrected work, 10 new
  documents): key finding — a substantial part of what PM described as new
  platform-owned structure **already exists**, built before this correction
  as the `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001` Foundation
  (Account/FamilyGroup/FamilyMembership/Role/Permission/ServiceSubscription)
  and the Doran messaging domain (Room/Participant/Message/ReadState/
  ServicePrincipal/ServiceBinding) — both confirmed KEEP_AS_IS, not legacy
  being replaced. The two genuinely missing platform capabilities:
  Account-native Authentication/Session (does not exist in any form — 3
  candidate designs proposed, none decided) and MarkPoint's re-hosting onto
  Membership ownership (business logic 100% reusable per direct source
  read; 7 tables need an ownership-FK TRANSFORM from `player_id` to
  `family_membership_id`; ~70 routes need an auth-dependency swap from
  legacy PLAYER_ONLY/ADMIN_ONLY to Group Role/Permission checks). Every
  legacy table/route/auth-mechanism classified
  (REFERENCE_ONLY/KEEP_AS_IS/REUSE_LOGIC_ONLY/MIGRATE_DATA/TRANSFORM/
  REPLACE/DEPRECATE/DELETE_CANDIDATE/UNDECIDED) with evidence; no
  user-group/role/permission name was invented — 5 explicit
  PM_DECISION_REQUIRED items recorded instead (Group-vs-Family generalization,
  Auth/Session model choice among 3 options, whether the already-seeded
  Role/Permission codes are final, MarkPoint's target URL-scoping
  convention, and two data-migration questions for existing identities and
  point/mission history).
- Handoff: engineering/phase2/MONGLE_TARGET_ARCHITECTURE_RECONCILIATION_REPORT.md
  (current final report). Axis A (7 docs, retained/banner-marked, not
  superseded in content): MONGLE_DATA_BACKEND_CONTRACT_RECONCILIATION_REPORT.md
  (superseded verdict only), MONGLE_DATA_NAMING_CONTRACT_V0_1.md,
  MONGLE_CURRENT_TABLE_DICTIONARY.md, MONGLE_CURRENT_COLUMN_DICTIONARY.md,
  MONGLE_BACKEND_API_CONTRACT_INVENTORY.md, MONGLE_SCREEN_DATA_CONTRACT_MATRIX.md,
  MONGLE_DB_BACKEND_GAP_REPORT.md.
  Axis B (10 new docs):
  MONGLE_TARGET_BUSINESS_GLOSSARY.md, MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md,
  MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md, MONGLE_TARGET_TABLE_DICTIONARY.md,
  MONGLE_TARGET_COLUMN_DICTIONARY.md, MONGLE_TARGET_API_INVENTORY.md,
  MONGLE_REALTIME_MESSAGING_CONTRACT.md, MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md,
  MONGLE_LEGACY_TO_TARGET_MAPPING.md, MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md.
  **Location correction (MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001, 2026-08-01,
  originally found by PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001 F6):** this
  entry previously stated all 18 documents "live inside the isolated
  data-backend worktree (`/Users/mac/mac_Project/mongle_ui-data-backend-worktree`,
  branch `data-backend-contract-reconciliation`), not this one." That is no
  longer true. Merge commit `da7ea74`
  (`merge: integrate data backend contract reconciliation`) landed all 18
  documents into **this** worktree, and the named path is confirmed absent from
  disk (`git worktree list` + direct path check, 2026-08-01). Note that a
  *different*, undocumented external worktree remains on disk at
  `/private/tmp/claude-501/.../scratchpad/data-backend-contract-worktree`
  (detached HEAD `9bcd1a5`) — flagged as F7 by the same audit, **not touched**,
  and requiring PM direction under `DEC-2026-005` rather than unilateral
  cleanup. No `agent-system/handoffs/active/` file exists for this task; its
  reports serve as the handoff. **This corrects only "where the files are",
  not this task's Verification/Decision status.**
- QA Evidence: none in this worktree — self-check only across both phases
  (migration-chain execution + 71/71 pytest pass + `git diff --check`/
  `git status` clean after every document write are real executed evidence)
- Independent QA: not started
- Contract Freeze outcome (2026-08-01): **the Freeze was issued.** PM approved
  D1–D8 in `engineering/phase2/MONGLE_TARGET_DECISION_FREEZE.md`, which resolves
  4 of this task's 5 `PM_DECISION_REQUIRED` items: Group-vs-Family
  generalization (D1 — family platform, `family_groups`/`family_memberships`
  retained, generic Group rejected), the Auth/Session model (D2/D3 — id +
  platform password, FamilyAdmin-provisioned Accounts, Account-scoped
  persistent Session, optional Account+Device Wagle PIN), Markpoint's target
  URL scoping (D7 — `/families/{familyId}/markpoint` with server-side
  revalidation), and both data-migration questions (D8 RESET — no Legacy
  identity or point/mission history import). The 5th item, whether the seeded
  Role/Permission **code strings** are final, remains `REQUIRES_PM_REVIEW` /
  `NON_BLOCKING` and is confirmed at the Wave 1 scoped-RBAC Start Gate. For the
  frozen documents and the recalculated plan see
  `MONGLE-APPROVED-DECISIONS-FREEZE-AND-DECOMPOSITION-001`, which graduated
  2026-08-01 — its record is now in `agent-system/graduated/2026-08.md` and its
  report is `engineering/phase2/MONGLE_APPROVED_DECISIONS_FREEZE_AND_DECOMPOSITION_REPORT.md`
  (reference updated by MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001; the previous
  "above" pointer became dangling when that section left this file).
- Next Action: this task's Freeze dependency is satisfied; the remaining open
  items are its own closeout, not a PM decision. FE<->API<->DB vertical wiring
  and any Markpoint ownership work now follow the recalculated Wave plan and
  each task's own Start Gate — a passed Freeze is not by itself implementation
  authorization. Independent QA of this
  task's own claims is a secondary open item, not a blocker for the Freeze
  decision. Once PM has reviewed, the isolated data-backend worktree/branch
  should be cleaned up the same way as A1's (do not remove before that
  review, do not leave it dangling after). MONGLE-TEST-GOVERNANCE-PORTING-001
  below is waiting specifically on this Next Action.

## MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001

- Task ID: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED (commit `0c2a040`) / INDEPENDENT_QA_PASS (2026-07-31) — this
  task's own report retains its self-assigned CONDITIONAL verdict/sentinel verbatim
  (preserved, not edited); a separate agent session independently verified the Foundation
  commit's exact file diff and token values against the live repository and found no
  discrepancy (see `agent-system/qa/MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001.md`). The
  Closeout Addendum in `MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md` now reads
  `FINAL_VERIFICATION: PASS`. This is the Closeout Contract's documentation-sync gate, not
  a PM graduation decision — Lifecycle stays IN_PROGRESS pending the PM's own decision on
  whether to graduate this task.
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001.md
- Independent QA: complete — PASS (2026-07-31, separate agent session; see QA Evidence)
- Next Action: PM decision on whether to graduate this task (and its two siblings below)
  now that independent QA has passed; if so, move all three to `graduated/2026-07.md` and
  their handoffs to `handoffs/archive/2026-07/` per the normal graduation procedure.

## MONGLE-W6-1-E2E-HARNESS-RECOVERY-001

- Task ID: MONGLE-W6-1-E2E-HARNESS-RECOVERY-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: READ_ONLY_CHECK_COMPLETE / INDEPENDENT_QA_PASS (2026-07-31) — retracted a
  prior turn's "missing script" claim as a path-lookup error:
  `tests/e2e/scripts/start-mongle-phase1.sh` was present, tracked, executable, and
  byte-identical to its origin commit (`7f1ce9e`) the whole time; no restoration was needed
  or performed. Independently re-verified (SHA-256, `git diff`, `shellcheck`/`bash -n`) by a
  separate agent session as part of the bundled Wave 6.1 QA pass.
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-E2E-HARNESS-RECOVERY-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-E2E-HARNESS-RECOVERY-001.md
- Independent QA: complete — PASS (2026-07-31, separate agent session; see QA Evidence)
- Next Action: PM decision on whether to graduate this task alongside its two siblings.

## MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001

- Task ID: MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: INDEPENDENT_QA_PASS (2026-07-31) — self-check evidence (lint PASS, build
  PASS, two independent cold-start Playwright rounds both 66 passed / 0 failed / 4
  intentional skipped with an identical test-identity set, before/after visual diff
  0.000%-0.022% fully attributable to a dynamic seed timestamp, 0 dimension changes, 0
  unexpected console errors, Docker cleanup confirmed at every teardown) was independently
  re-verified by a separate agent session: two fresh cold-start rounds (also 66/0/4,
  identical test-identity set), lint/build re-run, Docker teardown re-confirmed, HEAD/dirty
  state and commit ancestry cross-checked. One correction: the seed-timestamp root cause was
  misattributed to `phase1_seed_synthetic.py` (that script has no Mission-table code; the
  actual source is the `Mission` model's `server_default=func.now()`) — the broader
  conclusion is unaffected; recorded in the Closeout Addendum and `COVERAGE_MAP.md` rather
  than editing this report's original prose.
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001.md
- Independent QA: complete — PASS (2026-07-31, separate agent session; see QA Evidence)
- PM_EVIDENCE_ACCEPTANCE: APPROVED (2026-07-31) — see the Closeout Addendum in
  `engineering/phase2/MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md`, now reading
  `FINAL_VERIFICATION: PASS`.
- Next Action: the Wave 6.1 governance-only commit landed as `6c63367` (docs +
  these Agent System records; Avatar-fix code and any A1 code were correctly
  excluded, per plan). Remaining PM decisions: (a) whether to graduate these
  three tasks now that independent QA has passed, (b) whether to keep or
  remove the `mongle-frontend-toolchain` container.

## MONGLE-TEST-GOVERNANCE-PORTING-001

- Task ID: MONGLE-TEST-GOVERNANCE-PORTING-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTATION_COMPLETE / SELF_CHECK_COMPLETE — documentation-only
  test-governance port. No product/test code, package script, CI, Docker, E2E,
  DB, Foundation re-verification, Avatar QA, A1 integration, or DATA-A work was
  performed. Existing Agent System locations remain the policy/Coverage Map
  SSOT; `tests/README.md` is the command/artifact SSOT. The repository
  bootstrap and Claude entrypoint link thinly to the Test Policy and applicable
  FE/BE guide compliance rules.
- Handoff: agent-system/handoffs/active/MONGLE-TEST-GOVERNANCE-PORTING-001.md
- QA Evidence: agent-system/qa/MONGLE-TEST-GOVERNANCE-PORTING-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001

- Task ID: MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: Documentation-only minimal guide supplement. Frontend page
  responsibility/source-growth rules and API-schema-first type wording are in
  scope; existing backend giant-source/UoW rules are retained without
  duplication.
- Handoff: agent-system/handoffs/active/MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001.md
- QA Evidence: agent-system/qa/MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001

- Task ID: MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: PM decision recorded before feature development: reserve
  `e2e_tester` as a logical synthetic-E2E identity; require isolated data and
  feature event-branch matrices. No account, credential, fixture, DB row, CI,
  or test implementation is created by this documentation task.
- Handoff: agent-system/handoffs/active/MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001.md
- QA Evidence: agent-system/qa/MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001

- Task ID: MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: Plan-only enforcement decision: CI/Alembic/dotted-call guard,
  new-spec naming, and synthetic E2E fixture provisioning are reserved as
  separate tasks after DATA-A/A1 contract review; no implementation is
  authorized by this plan.
- Handoff: agent-system/handoffs/active/MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001.md
- QA Evidence: agent-system/qa/MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001

- Task ID: MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: Absolute prohibition on agent-created project material outside
  the Git worktree, including `/tmp`, repository-adjacent directories, and
  external worktrees. Historical external paths are documentation only.
- Handoff: agent-system/handoffs/active/MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001.md
- QA Evidence: agent-system/qa/MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT
## MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001

- Task ID: MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS (recovery baseline only; not visual QA)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001.md
- Result: canonical archive remeasured; noncanonical connected UI routes detached;
  API, session, authorization, and realtime code parked pending R8 integration.
