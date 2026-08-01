# MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001

- Task ID: `MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001`
- Kind: documentation-only closeout (no product logic)
- Predecessors: `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`, `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; a disposable volume-less PostgreSQL 16.9 for the targeted tests only
- evidence: `agent-system/qa/MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001.md`
- secrets_redacted: `true`
- Lifecycle: `GRADUATED`
- Decision: `DESIGN_APPROVED` (PM Wave 5 documentation closeout directive, 2026-08-01)
- Verification: `PASS`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
- End HEAD: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Origin

The independent QA's only `CONDITIONAL` cause was documentation: PM had settled
the rolling-window contract, but two docstrings still described it as an open
contradiction — the exact shape that lets a future developer reverse a decided
policy while believing they are cleaning up.

## What changed

- **Target `rolling_window` docstring** — now states `TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE`, all three worked examples, and why narrowing it is a product decision rather than a tidy-up.
- **Legacy `get_rolling_window` docstring** — the rejected `7일간 (이번 주만)` example removed; marked a legacy reference whose calculation matches the approved Target contract, with 월 14일 / 토 9일 / 일 8일.
- **Coverage Matrix `MP-M03`** — the "contradiction remains" wording replaced by the contract, its approval date and the alignment statement. Status unchanged at `COVERED_TARGET`.
- **Independent QA report** — a `## 23-A. Correction reference` block added above its §24. Its findings, its §24 defect list and both `WAVE_5_INDEPENDENT_QA_CONDITIONAL` occurrences are untouched.

## Proof that no logic moved

Both Python files were parsed before and after with every docstring node
stripped, and the resulting ASTs hashed. The fingerprints are identical, so the
change is provably docstring-only — no statement, signature, import or default
differs. `py_compile` passes on both.

```
targeted: test_rolling_window_preserves_the_implemented_legacy_behaviour PASSED
          -k "rolling or materializ"  -> 6 passed
stale-text zero gate (3 current docs) -> 0 matches
git diff --check                      -> clean
test/migration/API/schema files changed -> 0
```

The full 312-test suite was **not** re-run and is not reported as if it had
been; that figure belongs to `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001`.

## Lifecycle

```
Independent QA original : CONDITIONAL — preserved verbatim, not rewritten
Follow-up correction    : documentation-only closeout PASS
Effective Wave 5        : PASS after the required documentation correction
```

## Residual item, flagged not fixed

`test_markpoint_core_gap_wave5.py::test_rolling_window_preserves_the_implemented_legacy_behaviour`
still has a docstring calling the contradiction open, and a name to match. That
is stale in exactly the way this task exists to prevent, but this task's own
constraints forbid modifying test files and require `테스트 변경 0` — changing
it would fail its own oh-so-relevant "오작업" gate. A one-line refresh or an
explicit exemption closes it; the assertions themselves are correct.

## Risks and Human Gate

- **Do not narrow the rolling window** to 7 days or to "this week's Sunday". A Monday's window is 14 inclusive dates by approved contract; halving it halves how many missions every Monday generates.
- **Do not rewrite the independent QA's `CONDITIONAL` to PASS.** It was correct when reached; the effective verdict lives in this task's report and in `graduated/2026-08.md`.
- No commit or push. Branch and HEAD unchanged.

## Next agent first action

Wave 6 Start Review. Carried forward unchanged: `MP-U01` (Wave 6 UI),
`MP-S01`/`MP-S02`/`MP-S03` (Wave 6 product decisions), and legacy
`configs.point_cycle` retirement (Wave 7 cutover).

## Forbidden Scope

Changing the rolling-window arithmetic or either function body; modifying
tests, migrations, schema, API or permissions; altering `MP-M03`'s coverage
status; retiring or reclassifying the PM-decision rows; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/graduated/2026-08.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001.md`
- Independent QA: `not_required`
- Independent QA Reason: documentation-only; the product claim it closes was independently verified by `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001`, and this task changed no executable statement (AST-proven).
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: no test path, tier, journey or execution evidence changed; MP-M03 stays COVERED_TARGET with the same tests.
- CLOSEOUT GATE: `PASS`
