# Active Tasks

Only open tasks belong here. Lifecycle, decision, verification, and execution
are separate axes.

## MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001

- Task ID: MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: A1_IMPLEMENTATION: COMPLETE / A1_PM_VISUAL_GATE: PENDING /
  A1_INTEGRATION: PENDING / A1_FINAL: CONDITIONAL (PM verdict, 2026-07-31). All
  code and evidence live in an isolated worktree, never committed to this
  branch: `/Users/mac/mac_Project/mongle_ui-a1-visual-worktree`, branch
  `w6-2-a1-visual`, both branched from and still pinned at HEAD `9bcd1a5`. PM
  directed 5 follow-up items: settings icon wired to the existing admin-login
  entry (DONE, re-verified — lint/build/target-E2E PASS, click-through
  confirmed), lock-notice copy kept generic with no invented counts/times
  (already satisfied pre-PM-decision), level/job-title/lock-detail kept as
  documented DATA gaps rather than hardcoded (already satisfied), the Avatar
  status-dot clip NOT worked around in A1 files (already satisfied — see
  MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001, handled as its own task instead).
- Handoff: engineering/phase2/MONGLE_W6_2_A1_MOBILE_VISUAL_PUBLISHING_REPORT.md,
  MONGLE_W6_2_A1_VISUAL_DELTA.md, MONGLE_W6_2_A1_TOKEN_PRIMITIVE_GAPS.md
  (all inside the isolated A1 worktree, not this one; no
  agent-system/handoffs/active/ file exists for this task since none of its
  artifacts are in this worktree)
- QA Evidence: none in this worktree — self-check only, recorded in the three
  reports above
- Independent QA: not started — gated behind A1_PM_VISUAL_GATE and the Avatar
  fix's own independent QA
- Next Action: PM Visual Gate review of the three A1 reports (Visual Delta's
  remaining sign-off items: pre-login level-pill 401, missing job-title/lock-
  detail API fields, rewritten lock-notice copy); once approved AND the Avatar
  fix passes independent QA, integrate A1 into this authoritative worktree,
  re-run lint/build/target-E2E/auth-flows/admin-entry/screenshot/console here,
  and only then remove the isolated worktree and branch
  (`git worktree remove` + branch delete + `git worktree prune`, verified gone)

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
- Execution: RUNNING
- Phase Note: SELF_CHECKED / INDEPENDENT_QA_PENDING — registration gap found and
  corrected 2026-07-31 (task existed in handoffs/qa since commit `a1575e0`,
  2026-07-26, but was never added here). Later commits `0393971` (service
  principal and room binding) and `91eb98e` (reliable service event delivery)
  extended the Doran domain with no agent-system task record at all; the
  "remaining work" list in the handoff is stale relative to current code.
- Handoff: agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md
- QA Evidence: agent-system/qa/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md
- Independent QA: pending — mandatory for security, DB, and service boundaries
- Next Action: PM triage — decide whether to register/re-scope the untracked
  follow-up Doran work (`0393971`, `91eb98e`) as its own task(s), update the R2
  handoff's checkpoint to match current code, then run independent QA before
  any completion or push claim

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
- Lifecycle: PLANNED
- Decision: NOT_REVIEWED
- Verification: NOT_TESTED
- Execution: NOT_STARTED
- Phase Note: RESULT_NOT_YET_REPORTED — placeholder registered 2026-07-31 per PM
  direction to keep this DB/Backend real-measurement, dictionary, and contract
  proposal session (running in a separate isolated worktree,
  `.../data-backend-contract-worktree`) explicitly distinct from the Wave 6.1
  Foundation/A1 frontend-visual task family above. This is not a report of
  that session's actual findings — none have been reported to this session yet.
- Handoff: not yet created — to be filed by that session on its own report
- QA Evidence: not yet created
- Independent QA: not_applicable yet — no result to review
- Next Action: FE<->API<->DB vertical wiring (A1 and any A3/A5 parallel slice)
  MUST NOT START until this task reports its DB/API contract result and the
  PM issues a Contract Freeze; do not infer or invent table/column/DTO names
  from this placeholder

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
- Next Action: PM decision on (a) graduating these three tasks, (b) the Wave 6.1
  governance-only commit (docs + these Agent System records, explicitly excluding the
  separate Avatar-fix code and any A1 code — the latter lives only in its own isolated
  worktree), and (c) whether to keep or remove the `mongle-frontend-toolchain` container.
