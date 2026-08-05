# Handoff — MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001

- Task ID: MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001
- Role: QA (read-only). Full narrative, per-domain evidence, and the 3
  defects found: see this task's own QA evidence file,
  `agent-system/qa/MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001.md`.
  This handoff is a summary pointer only.

## Independence (headline finding, see QA evidence §1 for full reasoning)

`INDEPENDENT_QA_PARTIALLY_ESTABLISHED`. Wagle and Admin were already
committed at this session's own starting HEAD (implemented by a genuinely
separate prior session) — real independence holds for those two. Auth,
Family, and Markpoint were implemented by this exact conversation earlier
in the same session — their results here are rigorous self-verification,
explicitly not Independent QA, disclosed throughout rather than silently
claimed as independent.

## What this task did

- Re-derived and independently re-verified the 64-row Matrix's integrity
  (0 duplicates, write-once columns byte-unchanged vs. HEAD, confirmed via
  a fresh script, not the implementers' own claims).
- **Wagle (`1d`)**: first-ever real browser runtime check for this
  integration (the implementer's own handoff disclosed none was possible
  in their environment) — created a real room + message via the actual
  HTTP API, confirmed the canonical Screen renders it correctly. Found and
  disclosed 1 real backend defect (Wagle permission-check crash on
  overlapping role grants).
- **Admin**: also the first-ever real browser runtime attempt — blocked by
  2 real, pre-existing, high-severity defects (neither caused by any of
  the 5 W7.4 domain tasks) that make `/admin` currently unreachable for
  any session type with the standard admin-account shape. Fell back to
  code-level verification, which supports the implementer's own claims.
- **Auth**: reproduced the previously-never-verified locked-profile guard
  live with a disposable locked test player — genuinely closes that
  disclosed gap.
- **Family/Markpoint**: re-confirmed denominators, spot-checked fixture-
  vs-real classifications (re-confirming 2 corrections the implementer
  already made — `2f`/`2p`/`3i` still fixture, `2y` genuinely real — and
  finding no new ones), re-confirmed the Markpoint CSS-bug fix holds and
  the protected weekly-DOM-contract JSX is still 0-diff.
- Cross-domain: confirmed all 55 extracted canonical Screens have exactly
  2 real consumers (Product+Preview), 0 orphans, 0 Product→Preview
  imports, `AdminDataGrid` genuinely screen-local.
- Added append-only `Cross_Domain_QA_*` columns to all 64 Matrix rows;
  added 3 new Coverage Map rows (2 defect-tracking, 1 summary).

## Files changed (QA-owned only; 0 product code)

- `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
  (4 new append-only columns, all 64 rows; write-once columns re-verified
  byte-unchanged both before and after).
- `agent-system/qa/COVERAGE_MAP.md` (3 new rows).
- `agent-system/active.md`, `agent-system/relay/current.md` (this task's
  own entries).
- This handoff and its QA evidence file.

One stray throwaway script (`tests/e2e/wagle_smoke.local.mjs`, left by a
timed-out mid-task command) was caught by this task's own final `git
status` review and removed before completion.

## Database

All QA-owned seeding this task was additive-only, created via the real
service layer or real HTTP API wherever practical, scoped by explicit
recorded IDs, and fully removed afterward. Final state: `accounts=0
family_groups=0 players=4(pre-existing) admin_auth=2(pre-existing)
wagle_rooms=0`. `git status --short backend/` clean throughout. The 2
pre-existing real `admin_auth` rows and 4 pre-existing legacy `players`
rows were read but never modified or deleted.

## Defects found (not fixed — read-only QA)

1. **DEFECT-001 (HIGH)**: `/admin` route guard accepts only the legacy
   `isAdmin` flag, which the real Account-native login never sets — Admin
   is unreachable via the intended real login path.
2. **DEFECT-002 (HIGH)**: legacy admin JWTs fail `/api/account-context`
   resolution whenever `admin_auth.player_id` is `null` (the normal case),
   due to a `"player_id" in user` presence check that should test
   non-null value instead — compounds DEFECT-001 (even the one path that
   passes the route guard doesn't reliably work either).
3. **DEFECT-003 (MEDIUM)**: Wagle's permission-check crashes
   (`500 MultipleResultsFound`) when a membership holds 2+ roles that both
   grant the same permission — a realistic, schema-unprevented shape.

All three are pre-existing (confirmed untouched by any of the 5 W7.4
domain tasks' own diffs), not regressions from this wave's work. Full
reproduction evidence in the QA evidence file's §14 and in the two new
Coverage Map GAP rows.

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001.md

## Next Action

1. Open a dedicated remediation task for DEFECT-001/002 (Admin real-access
   blockers) — likely the single highest-priority follow-up given it
   affects real usability of the entire Admin integration surface, not
   just this QA's own ability to verify it.
2. Open or fold DEFECT-003 into Wagle's own existing hardening lineage.
3. A genuinely independent QA session (separate operator/session) should
   re-verify Auth/Family/Markpoint specifically, since this pass's own
   results for those three are disclosed self-verification only.
4. W7.6 should not start until DEFECT-001/002 are resolved or explicitly
   triaged, and the already-open PM/design/infrastructure decision list
   (§15 of the QA evidence) is reviewed by PM.

No commit, push, merge, or rebase was performed by this task.
