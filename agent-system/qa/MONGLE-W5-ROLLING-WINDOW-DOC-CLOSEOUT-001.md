# MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001

- Task ID: `MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001`
- Kind: documentation-only closeout (no product logic)
- Predecessors: `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`, `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840` (unchanged start → end)
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
MONGLE_W5_ROLLING_WINDOW_DOC_CLOSEOUT_PASS
WAVE_5_DOCUMENTATION_GATE_CLOSED
WAVE_5_INDEPENDENT_QA_EFFECTIVE_PASS
MARKPOINT_APPROVED_CORE_LIFECYCLE_COMPLETE
READY_FOR_WAVE_6_START_REVIEW
```

```text
TARGET_ROLLING_WINDOW_DOCSTRING_CORRECTED
LEGACY_ROLLING_WINDOW_DOCSTRING_CORRECTED
COVERAGE_MATRIX_MP_M03_CURRENT
ROLLING_WINDOW_LOGIC_UNCHANGED
STALE_CONTRADICTION_TEXT_ZERO_IN_CURRENT_DOCS
TARGETED_TEST_PASS
FIVE_GATES_PASS
```

## 2. Git Baseline

| | Start | End |
|---|---|---|
| branch | `dev-newmarkp` | `dev-newmarkp` |
| HEAD | `25c8d0c` | same |
| `git diff --check` | clean | clean |
| stash | 0 | 0 |
| commit/push/merge/rebase/PR | none | none |

The preceding Wave 5 and audit tasks' uncommitted work was present at start and
is preserved.

## 3. PM Contract

```text
TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE

start        = today
this_sunday  = today + (6 - today.weekday())
end          = this_sunday + 7 days
both endpoints inclusive
```

Verified against the code, not assumed:

```text
Monday   2026-03-30 -> 2026-04-12   14 inclusive dates
Saturday 2026-04-04 -> 2026-04-12    9 inclusive dates
Sunday   2026-04-05 -> 2026-04-12    8 inclusive dates
```

The Target and legacy implementations were compared across **400 consecutive
start dates** and agree on every one — so the legacy docstring could be given
the same contract wording rather than a hedge.

## 4. Files Inspected

`backend/app/domains/markpoint_target/service.py` (`rolling_window`),
`backend/app/domains/mission_template/service.py` (`get_rolling_window`),
`engineering/phase2/MONGLE_MARKPOINT_FUNCTIONAL_COVERAGE_MATRIX.md`,
`agent-system/qa/MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001.md` (its §24 names both
defects), plus `active.md`, `relay/current.md`, `graduated/2026-08.md` and the
Wave 5 handoffs.

## 5. Target Docstring Correction

Removed: the "two examples, only one matches the code / the contradiction is
reported rather than silently resolved" framing.

Now states the canonical identifier, all three worked examples, and — kept
deliberately — the reason narrowing it is a product decision: halving a
Monday's window would halve how many missions that day generates. It also
records that the legacy function computes the same window, so the two
docstrings cannot drift apart again without one of them contradicting a stated
cross-reference.

## 6. Legacy Docstring Correction

Removed: `예) 오늘이 월요일(3/30)이면 → 3/30(월) ~ 4/5(일) = 7일간 (이번 주만)`
— the reading PM's decision rejected, and the sentence most likely to make a
future developer "fix" the code back to a one-week window.

Now marked a **legacy reference implementation** whose actual calculation
matches the approved Target contract, with all three examples corrected
(월 14일 / 토 9일 / 일 8일) and an explicit note that inclusive endpoints are
why the counts are not multiples of seven. Kept in Korean to match the file.

## 7. Coverage Matrix Correction

`MP-M03` no longer says the docstring "contradicts itself and the code was kept
— see the report". It now states the contract, its PM approval date, that code
and docstrings are aligned, and the 400-date cross-check. **Status unchanged at
`COVERED_TARGET`**; nothing else in the row was touched, and no other row was
touched at all.

## 8. Logic-diff Proof

Both Python files were parsed before and after, every docstring node stripped
from every module/class/function, and the resulting ASTs hashed:

```text
before:
  5976ca603ea474dfa1d50d4981e3b218e47f71f1d7606bac3bdc38a323e917a5  markpoint_target/service.py
  0bc9810435e82608cd7890ce8deb5b77a89d45f1b0f04a78c3989950d961f322  mission_template/service.py

after:  identical to before (diff empty)
```

So the change is provably docstring-only: no statement, signature, import or
default value differs. `python -m py_compile` passes on both.

```text
function body changed   : no
signature changed       : no
imports changed         : no
Migration changed       : no
API changed             : no
Test files changed      : no
```

## 9. Targeted Test

The full 312-test suite was **not** re-run, and is not reported as if it had
been. The product logic is provably unchanged (§8), so this task's evidence is
the AST proof plus the tests that actually exercise the window:

```text
test_rolling_window_preserves_the_implemented_legacy_behaviour  PASSED
-k "rolling or materializ"                                      6 passed, 48 deselected
python -m py_compile (both files)                               PASS
git diff --check                                                clean
```

The `312/312` figure belongs to `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001` and is
cited as that task's result, not re-claimed as this one's.

## 10. Stale-text Zero Gate

```bash
grep -RniE "7일간|이번 주만|unresolved contradiction|contradiction is reported|only one matches|code preserved pending|docstring contradiction" \
  backend/app/domains/markpoint_target/service.py \
  backend/app/domains/mission_template/service.py \
  engineering/phase2/MONGLE_MARKPOINT_FUNCTIONAL_COVERAGE_MATRIX.md
-> 0 matches
```

`TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE` now appears in the Target docstring,
the Matrix `MP-M03` row and this report, alongside the pre-existing occurrences
in `active.md` and the independent QA records.

Historical QA reports were excluded from the gate by instruction and by
principle — a report that records a defect it found must keep saying so.

## 11. Lifecycle Synchronization

```text
Independent QA original verdict : CONDITIONAL — preserved verbatim
Follow-up correction            : documentation-only closeout PASS
Effective Wave 5 verdict        : PASS after the required documentation correction
```

The independent QA report was **not** rewritten to PASS. A short
`## 23-A. Correction reference` block was inserted above its §24 pointing at
this task; its findings, its §24 defect list and both occurrences of
`WAVE_5_INDEPENDENT_QA_CONDITIONAL` are untouched. Overwriting the verdict
would erase the record that the gap existed and was found — the effective
verdict lives here and in `graduated/2026-08.md` instead.

## 12. Recursive Review

**Pass 1 (before).** Located both docstrings and read the actual arithmetic in
each. Confirmed the two functions compute the same window across 400 start
dates rather than assuming it from their similar shape. Captured the AST
fingerprints that would later prove the edit was docstring-only.

**Pass 2 (after the edits).** AST fingerprints identical; `py_compile` passes;
`MP-M03` current with its status untouched; the independent QA's own findings
intact.

**Pass 3 (after lifecycle).** No task appears in both `active.md` and
`graduated/`; each graduated handoff moved to `handoffs/archive/2026-08/`;
`relay/current.md` no longer claims a live Wave 5 writer; the deferred rows
(MP-U01, MP-S01–S03, legacy `configs.point_cycle`) are carried forward
unchanged rather than closed.

## 13. Five-Gate Review

- **환각** — the contract was recomputed from the code before any prose was written; the 14/9/8 counts and the 400-date agreement are command output; the 312 figure is attributed to the QA that ran it and is not re-claimed.
- **누락** — Target docstring, legacy docstring, Coverage Matrix, `active.md`, relay, `graduated/2026-08.md`, the handoffs and the QA correction reference: all present.
- **오작업** — no date arithmetic, function body, signature, migration, API or test file was changed; the window was not narrowed to 7 days or to this week's Sunday; `COVERED_TARGET` was not altered; PM-decision rows untouched.
- **축혼동** — kept distinct: the code's actual contract; the prose describing it; the historical QA result; the current lifecycle result; legacy reference vs Target authority.
- **신선도·오탈자** — canonical identifier present in all three required places; 월 14일 / 토 9일 / 일 8일 stated consistently; stale matches 0; `git diff --check` clean; no broken Markdown (the Matrix table still parses to the same row count).

## 14. Changed-file Manifest

**Modified (3 + records)** —
`backend/app/domains/markpoint_target/service.py` (docstring only),
`backend/app/domains/mission_template/service.py` (docstring only),
`engineering/phase2/MONGLE_MARKPOINT_FUNCTIONAL_COVERAGE_MATRIX.md` (`MP-M03` row),
`agent-system/qa/MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001.md` (correction
reference added; findings untouched), `active.md`, `relay/current.md`,
`graduated/2026-08.md`, the Wave 5 handoffs moved to archive.

**New (2)** — this report and its handoff.

No test file, migration, schema, API, permission or frontend file was changed.

## 15. Residual item, reported rather than silently fixed

`backend/tests/test_markpoint_core_gap_wave5.py::test_rolling_window_preserves_the_implemented_legacy_behaviour`
still carries a docstring describing the contradiction as open ("Legacy
`get_rolling_window`'s own docstring contradicts its code… the contradiction is
reported"), and its name says "preserves the implemented legacy behaviour".

That is now stale in exactly the way this task exists to prevent. It was **not**
corrected here because this task's own constraints forbid modifying test files
and require `테스트 변경 0` as a verification — changing it would fail my own
Gate 3. Flagged for PM: a one-line docstring refresh in that test, or an
explicit exemption, closes it. Its assertions are correct and unaffected.

## 16. Final Verdict

```text
MONGLE_W5_ROLLING_WINDOW_DOC_CLOSEOUT_PASS
WAVE_5_DOCUMENTATION_GATE_CLOSED
WAVE_5_INDEPENDENT_QA_EFFECTIVE_PASS
MARKPOINT_APPROVED_CORE_LIFECYCLE_COMPLETE
READY_FOR_WAVE_6_START_REVIEW
```

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/graduated/2026-08.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001.md`
- Independent QA: `not_required` — documentation-only; the product claim it closes was independently verified by `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001`, and this task changed no executable statement (AST-proven).
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: no test path, tier, journey or execution evidence changed; MP-M03 stays COVERED_TARGET with the same tests.
- CLOSEOUT GATE: `PASS`
