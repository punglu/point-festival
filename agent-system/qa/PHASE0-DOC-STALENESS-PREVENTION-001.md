# PHASE0-DOC-STALENESS-PREVENTION-001 Evidence

- Task ID: `PHASE0-DOC-STALENESS-PREVENTION-001`
- Verification: `NOT_TESTED`
- Self-check only: `true`
- Independent QA: `not_applicable` — documentation/process rule change only;
  no product code, DB, or auth boundary touched (COMMON_NORMS.md risk-based
  QA: documentation/lifecycle-only work uses self-check unless it reveals a
  product-risk defect).
- Git repository is SSOT.

## Writer self-check (not independent QA)

- Read `agent-system/rules.md` in full after editing: section order intact
  (Authority and evidence -> State model -> Invariants -> Documentation
  change routing -> Coordination -> Mandatory closeout synchronization ->
  Document grades -> Human Gate -> Prohibited actions), Invariants numbered
  1-11 with no gaps or duplicates, both markdown tables have consistent pipe
  counts per row.
- Read `agent-system/templates/handoff.md` after editing: new field sits
  under "Completed / remaining" without disturbing existing fields.
- Cross-checked new text against `agent-system/rules.md`'s pre-existing
  content to avoid restating what was already covered (ground-truth-first,
  active/graduated split, and the one-Task-ID-one-location invariant were
  already present and were not duplicated).
- Not run: no automated structural-validation script exists yet for this
  repository (see this task's handoff, Known Gaps) — the checks above were
  manual, not tool-verified.
