# Handoff — MONGLE-W7-5-CODE-DEFECT-HARDENING-CLOSEOUT-001

- Task ID: MONGLE-W7-5-CODE-DEFECT-HARDENING-CLOSEOUT-001
- Kind: governance closeout only — no product/test code, no new
  implementation, no new independent QA run. Declares the W7.5
  code-defect/Hardening axis closed based on already-existing independent
  QA evidence, and registers a newly-found non-blocking test-infrastructure
  gap. Does not touch product code, test code, migrations, seed, or
  Playwright specs/assertions.

## Baseline

```text
worktree: /appl/point-festival
branch:   dev-newmarkp
HEAD:     328d877c162e300ffafbbc566a70d36bba4f3a2d (unchanged start -> end)
git diff --check: clean, start and end
stash: empty
```

Start dirty state: the same accumulated set from this session's prior tasks
(Markpoint closeout lineage, Active→Graduated sweep, native E2E launcher
lineage) — none owned by this closeout task, all preserved unchanged.

## Evidence chain reviewed (read from the actual repository, not summarized
from memory)

| Finding | Task lineage | Independent QA disposition |
| --- | --- | --- |
| Board-room duplicate-creation race | `MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` | Migration `0021` unique-invariant + atomic get-or-create; `API-W7-5-BOARD-ROOM-RACE-HARDENING-001` (Coverage Map) — 5×10 concurrency, always 1 room |
| Migration 0021 participant/read-state semantics | `MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001` (fixing `HARDENING-QA-F-001`) | `API-W7-5-MIGRATION-0021-PARTICIPANT-MERGE-MATRIX-001` — 10/10 real-Postgres cases, including the exact reported reproduction shape |
| Admin bcrypt 72-byte 500 | `MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` (fixing `RE-QA-F-ADMIN-LOGIN-BCRYPT`) | `API-W7-5-ADMIN-LOGIN-BCRYPT-HARDENING-001` — 6/6, oversized ASCII/multi-byte both 401 not 500 |
| Popular Posts SQL interval defect | `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` Phase I (F1) | `API-W7-5-BOARD-REACTIONS-001` — 7 new regression tests, revert-and-reconfirm proof |
| E2E runner repository-boundary / readiness flake | `MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001` (`HARDENING-QA-F-002`), `..-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` (`RE-QA-F-2T-RUNNER-FLAKY`) | `E2E-W7-5-2T-RUNNER-READINESS-001` — 4/4 consecutive back-to-back clean |
| Markpoint KST/UTC date-boundary defect | `MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001` (`RE-QA-F-003`) | `MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001` — `CONDITIONAL` (3 disclosed findings, none product) |
| — QA-F-001 (commit/push doc staleness), QA-F-002 (deducted-side test gap), QA-F-003 (pre-existing test OS-TZ fragility) | `MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001` | Developer self-check: commit-scope re-audited clean, deducted-side test added (3/3), the two fragile tests fixed and re-verified under 3 OS timezones, backend 405/405 twice consecutively. Its own E2E scope item deferred to the runtime-reproducibility lineage below. |
| Playwright/Chromium fixed-runtime reproducibility | `MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001` | Own verdict `FAIL` (own scope: runtime fixed and reproducible, but the *native launcher* it tried to pair with released services early) — preserved verbatim, not rewritten; the finding it names (`E2E-RUNTIME-F-001`) is the one this closeout formally resolves below |
| Native E2E launcher process lifecycle | `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001` | Developer self-check 10/10 (1 run) |
| Native E2E launcher — Independent QA | `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001` | Initial `CONDITIONAL` (Run 1 8 failed/2 passed — browser-executable-level, not `E2E-RUNTIME-F-001`'s own defect shape; Run 2 10/10 clean; lifecycle contract itself confirmed held in both runs). **Append-only correction, same file**: a second, concurrent Independent QA session's own corroborating pass, run after confirming no contention remained, produced two further clean consecutive pairs (4/4 runs, all 10/10). Revised: `E2E-RUNTIME-F-001`'s own lifecycle contract AND the two-consecutive-clean-runs gate both independently satisfied. |

Every row above was read from its own actual file in this repository this
session (`agent-system/qa/COVERAGE_MAP.md`, the named QA evidence files,
and `agent-system/active.md`'s own current entries) — not asserted from
this task's own brief.

## Native E2E final evidence, stated precisely

```text
Initial Independent QA (MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-
  INDEPENDENT-QA-001, first pass): CONDITIONAL
  Reason: Run 1 8 failed/2 passed (browser-executable-level errors, not
    E2E-RUNTIME-F-001's own defect shape — lifecycle contract itself held:
    Backend/Vite alive before and after Playwright, cleanup after
    Playwright, exit code preserved, in BOTH the passing and failing run).
  Run 2: 10 passed / 0 failed / 0 skipped.
  Root confound identified: a second, concurrently-running Claude Code
    session was independently invoking the identical launcher with the
    same fixed DB name (mc_w75_native_runner) and ports (18096/5195)
    during this exact window -- confirmed via live process-tree inspection
    and a captured mid-sequence "database ... being accessed by 6 other
    sessions" collision.

Additional uncontended Independent QA (same QA evidence file, append-only
  correction section, second session's own corroborating pass, run after
  confirming via direct process/DB/port checks that no contention
  remained):
  Pair A -- Run 1: 10/10. Run 2 (immediately following): 10/10.
  Pair B (fully uncontended) -- Run 1: 10/10. Run 2: 10/10.
  4/4 runs clean, 0 failures once outside the collision window.

Combined, final verdict for E2E-RUNTIME-F-001's own scope: CLOSED.
  Both the lifecycle contract (never in doubt after Run 1's own PID
  evidence) and the two-consecutive-clean-runs gate (satisfied twice over
  by the corroborating pass) are independently verified.
```

## W7.5 status (this closeout's own declaration)

```text
W7.5 code-defect hardening (Board-room race, migration 0021 semantics,
  admin bcrypt, Popular Posts SQL, Markpoint KST/UTC boundary, Playwright
  fixed runtime, native E2E launcher lifecycle): CLOSED

W7.5 overall: CONDITIONAL / HUMAN_GATE (unchanged -- PM/design decision
  gates, the infrastructure storage decision (GATE-2B), and W7.4's own
  live-consumer-integration audit remain open; this closeout does not
  touch any of them)

W7.4: REOPENED, LIVE_CONSUMER_INTEGRATION_AUDIT PENDING (unchanged)

W7.6: BLOCKED (unchanged -- was blocked on the board-room race and admin
  bcrypt defects, both now closed above, but W7.6 readiness was never
  solely gated on the code-defect axis; W7.4's own reopened scope and the
  PM/design decision gates remain separate, unresolved blockers)
```

This closeout does **not** declare `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_
PASS`, `FULL_PRODUCT_BEHAVIOR_WIRING_COMPLETE`, `PM_DECISIONS_RESOLVED`,
`W7_4_LIVE_CONSUMER_INTEGRATION_PASS`, or `READY_FOR_W7_6_COMMON_
COMPONENT_EXTRACTION`.

## Registered gap

`NATIVE-E2E-FIXED-RESOURCE-CONTENTION-GAP-001` registered in `active.md`
under a new "NON-BLOCKING TEST INFRASTRUCTURE DEBT" section, explicitly
separated from the W7.5 code-defect axis (per this task's own Section 9
instruction) — `OPEN` / `MEDIUM` / non-blocking. Full detail in that
entry itself; not duplicated here beyond the summary in this handoff's own
table above.

## Documents touched by this closeout

```text
agent-system/active.md:
  - new "NON-BLOCKING TEST INFRASTRUCTURE DEBT" section /
    NATIVE-E2E-FIXED-RESOURCE-CONTENTION-GAP-001 (new entry)
  - no other active.md entry rewritten; the lineage tasks listed in the
    Evidence Chain table above keep their own existing records exactly as
    they already stand (several already carry their own append-only
    corrections from prior sessions) -- this closeout does not re-open,
    graduate, or edit any of them individually; it only declares the axis
    closed at the umbrella level, in this task's own record and in
    relay/current.md's own pointer below
agent-system/relay/current.md:
  - this task's own current-writer section
  - "Next authoritative task" pointer updated to
    MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001
agent-system/qa/COVERAGE_MAP.md:
  - already corrected by the corroborating Independent QA pass itself
    (PARTIAL -> COVERED for E2E-W7-5-NATIVE-RUNNER-LIFECYCLE-001) --
    verified current and accurate, not re-touched by this closeout
agent-system/graduated/2026-08.md:
  - new row for this closeout task itself (not for the W7.5 umbrella)
this handoff and this task's own QA-evidence-equivalent record
```

## Closeout Synchronization (Closeout Contract v1)

ACTIVE was updated with only the new gap-registration entry; no existing
entry was rewritten. HANDOFF is this file. QA EVIDENCE is this handoff
itself, serving as the record — a pure governance-declaration task
synthesizing already-existing independent QA evidence has no new test
execution of its own to report separately. COVERAGE MAP required no change:
already corrected by the corroborating Independent QA pass itself, and
independently re-read and confirmed accurate by this closeout without
needing an edit.

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: NO_CHANGE_REQUIRED
- COVERAGE MAP Reason: already corrected by the prior corroborating Independent QA pass; re-read and confirmed accurate, no edit needed
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/archive/2026-08/MONGLE-W7-5-CODE-DEFECT-HARDENING-CLOSEOUT-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-CODE-DEFECT-HARDENING-CLOSEOUT-001.md

This is a governance/documentation closeout, not a product QA PASS
declaration — no independent QA run was performed by this task itself; it
synthesizes and formally closes based on QA evidence that already exists
in the repository, per this task's own explicit brief (Section 4).

## Baseline integrity

```text
product code touched:      0
test code touched:         0
migration touched:         0
seed touched:               0
Playwright spec/assertion touched: 0
existing dirty damage:      0
other task's own record rewritten: 0 (only this closeout's own new records
  and the new gap-registration entry were added; every lineage task's
  existing entry, including its own prior append-only corrections, was
  read and left exactly as-is)
commit/push/merge/rebase:   none performed
```

No commit, push, merge, or rebase was performed by this task.
