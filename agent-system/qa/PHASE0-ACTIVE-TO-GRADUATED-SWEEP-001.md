# Task QA Evidence — PHASE0-ACTIVE-TO-GRADUATED-SWEEP-001

- Task ID: PHASE0-ACTIVE-TO-GRADUATED-SWEEP-001
- Kind: first run of `AGENT_SYSTEM_ACTIVE_TO_GRADUATED_SWEEP_PROMPT.md` — a
  mechanical `active.md` → `graduated/<month>.md` transition for entries
  already, in their own current text, done. Not the Integrity Audit; no
  re-verification of any task's substantive claims, no reinterpretation of
  borderline fields.
- Baseline: branch `dev-newmarkp`, HEAD `328d877` (unchanged, no commit),
  39 `##`-level sections in `active.md` at start.

## Eligibility rule applied (verbatim from the sweep prompt)

1. `Execution: SUCCEEDED`.
2. `Lifecycle` literally `COMPLETE`, or `IMPLEMENTED_AWAITING_INDEPENDENT_QA`
   with its own evidence level disclosed (self-check-only is fine, per this
   repository's own established graduation precedent).
3. Own `Next Action` does not point at unresolved follow-up for *this
   task's own* completion.
4. Not `REOPENED`/`SUSPENDED`/`HUMAN_GATE`/an unresolved PM decision gate in
   its own text.
5. Handoff (and QA Evidence, if any) files exist at their stated paths.

No field was upgraded, downgraded, or reinterpreted to make a borderline
entry eligible. Genuinely ambiguous cases were left in `active.md`.

## Full disposition table

| Task ID | Disposition | Reason |
| --- | --- | --- |
| `MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001` | left open | `Execution: BLOCKED`, `Lifecycle: SUSPENDED` |
| `MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001` | left open | `Lifecycle: IN_PROGRESS`, own `Next Action` names a genuinely outstanding item (E2E smoke) |
| `MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001` | left open | `Lifecycle: IN_PROGRESS`, `Verification: CONDITIONAL` |
| `MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001` | left open | `Lifecycle: IN_PROGRESS`, awaiting a named follow-up QA task |
| `MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001` | left open | `Lifecycle: IN_PROGRESS`, awaiting Independent Re-QA |
| `MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` | left open | `Lifecycle: IN_PROGRESS`, superseded/awaiting Re-QA |
| `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` | left open | `Execution: RUNNING` |
| `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)` | left open | explicitly `REOPENED`, rule 4 exclusion by name |
| `MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001` | left open | `Execution: RUNNING`, `Verification: NOT_TESTED` |
| `MONGLE-W7-1-SCREEN-OWNERSHIP-TOPOLOGY-FREEZE-001` | **moved** | `Lifecycle: IMPLEMENTED_AWAITING_INDEPENDENT_QA`, `Execution: SUCCEEDED`, no own-completion blocker, files exist |
| `MONGLE-W7-0-FULL-SCREEN-AUTHORITY-COVERAGE-FREEZE-001` | **moved** | same shape as the row above |
| `MONGLE-W6-R2-1C-POINT-FESTIVAL-MOBILE-VISUAL-001` | left open, flagged | `Lifecycle: COMPLETE` but no Handoff/QA Evidence file exists at any stated path (none even stated) — rule 5 fails; this is a data-integrity gap, not this sweep's to fix |
| `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001` | left open | own `Next Action`: "before BG-1 is treated as closed" — own-completion blocker |
| `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001` | left open | `Lifecycle: IN_PROGRESS` |
| `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002` | left open, ambiguous | `Lifecycle` complete-shaped, but its own paired Independent QA task is itself still open with an unresolved PM decision entangled with this task's status — judged ambiguous, not guessed |
| `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001` | left open | `Lifecycle: IN_PROGRESS` (own text says "evidence complete" but the literal field is not one of the two accepted values — not reinterpreted) |
| `MONGLE-W1-INDEPENDENT-QA-001` | left open, **flagged for PM** | `Lifecycle: IN_PROGRESS (evidence complete; PM graduation decision pending)` — own text explicitly asks for this exact decision; literal field excludes auto-move |
| `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` | left open, **flagged for PM** | sibling of the row above, same shape, explicitly joint |
| `MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001` | left open | `A1_PM_VISUAL_GATE: PENDING`, substantive re-verification still needed |
| `PHASE2-DORAN-MESSAGING-CONTRACT-001` | left open | `PM_REVIEW_REQUIRED` (substantive, not administrative) |
| `PHASE0-DOC-STALENESS-PREVENTION-001` | left open | `PM_REVIEW_PENDING` (a real content decision: whether to port a script) |
| `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2` | left open | long-standing flagged priority gap, `Independent QA: pending` |
| `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001` | left open | `PM_REVIEW_REQUIRED`, five bounded gates named |
| `PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001` | left open, **flagged for PM** | `Verification: PASS`, Independent QA complete-PASS, own text: "ready for PM closeout confirmation"; literal `Lifecycle: IN_PROGRESS` excludes auto-move |
| `PHASE0-AUTOMATED-GAP-CLOSEOUT-001` | left open | `Lifecycle: SUSPENDED`, `Execution: FAILED` |
| `PHASE0-DEV-RUNTIME-RECOVERY-001` | left open | `PM_REVIEW` pending, minor |
| `PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001` | left open | `PM_REVIEW_PENDING` |
| `PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001` | left open | `PM_REVIEW_PENDING`; also names a next task (`PHASE0-DEVICE-AND-OPERATIONS-GATE-001`) that does not exist anywhere in `active.md` — a documentation gap flagged, not fixed (Integrity Audit territory) |
| `MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001` | left open | `Independent QA: pending` |
| `MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001` | left open, ambiguous | own text hedges ("remaining open items are its own closeout, not a PM decision") plus an unresolved worktree-cleanup item; not clearly eligible, not guessed |
| `MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001` | left open, **flagged for PM** | `Lifecycle: IN_PROGRESS`, own text explicitly names the target file `graduated/2026-07.md` and two named siblings |
| `MONGLE-W6-1-E2E-HARNESS-RECOVERY-001` | left open, **flagged for PM** | sibling of the row above |
| `MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001` | left open, **flagged for PM** | third sibling of the row above |
| `MONGLE-TEST-GOVERNANCE-PORTING-001` | left open | `WAIT_FOR_DATA_A_RESULT` |
| `MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001` | left open | `WAIT_FOR_DATA_A_RESULT` |
| `MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001` | left open | `WAIT_FOR_DATA_A_RESULT` |
| `MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001` | left open | `WAIT_FOR_DATA_A_RESULT` |
| `MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001` | left open | `WAIT_FOR_DATA_A_RESULT` |
| `MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001` | left open | own text: "parked pending R8 integration" |

## Applied (strictly eligible, 2 entries)

Both moved to `agent-system/graduated/2026-08.md`, handoffs relocated to
`agent-system/handoffs/archive/2026-08/`, each handoff's own internal
self-referential `HANDOFF Path:` line corrected to match its new location
(the only content change made to either file — everything else preserved
verbatim), removed from `active.md`, and one stale `relay/current.md`
section (a leftover `MONGLE-W7-1-SCREEN-OWNERSHIP-TOPOLOGY-FREEZE-001`
block with no current occupancy claim) deleted per Invariant 3.

```text
MONGLE-W7-0-FULL-SCREEN-AUTHORITY-COVERAGE-FREEZE-001
MONGLE-W7-1-SCREEN-OWNERSHIP-TOPOLOGY-FREEZE-001
```

## Flagged for explicit PM confirmation (6 entries, not auto-moved)

These are the strongest candidates for a future sweep run, but this sweep's
own rule only auto-moves a literal `COMPLETE`/`IMPLEMENTED_AWAITING_
INDEPENDENT_QA` `Lifecycle` value — each of these six currently reads
`IN_PROGRESS` even though its own prose already asks for graduation:

```text
MONGLE-W1-INDEPENDENT-QA-001 + MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001 (pair)
MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001 +
  MONGLE-W6-1-E2E-HARNESS-RECOVERY-001 +
  MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001 (trio, target graduated/2026-07.md)
PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001
```

If PM confirms any of these, the mechanical move itself is identical to
what this pass just did for the 2 auto-eligible entries — no new judgment
required, just an explicit go-ahead per this sweep's own no-reinterpretation
rule.

## Cleanup / integrity

```text
git diff --check: clean
agent-system/tools/check_all.py: no warning for either moved task
  (re-run after fixing each handoff's own stale internal self-reference)
No product/test/migration/seed file touched.
No graduated/*.md row rewritten — append only.
No commit/push/merge/rebase.
```

## Final Declaration

```text
ACTIVE_TO_GRADUATED_SWEEP_001_COMPLETE
TWO_ENTRIES_MOVED_STRICTLY_ELIGIBLE
SIX_ENTRIES_FLAGGED_FOR_EXPLICIT_PM_CONFIRMATION
ONE_ENTRY_FLAGGED_DATA_INTEGRITY_GAP_MONGLE_W6_R2_1C
REMAINDER_GENUINELY_STILL_OPEN
NO_TASK_REINTERPRETED_OR_UPGRADED
```
