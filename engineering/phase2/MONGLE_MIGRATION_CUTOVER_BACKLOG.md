# Reset and Cutover Backlog

> **D8 `RESET` is approved and frozen.** No Legacy operational data is migrated,
> transformed, backfilled, reconciled into Target, or used as a fallback.
> `RESET` means "not migrated into the new Target" — it does **not** mean
> immediate destructive deletion. Until the new system is stabilised, verified
> and PM has approved retirement, Legacy may be retained as a read-only backup.

This backlog is Wave 7 in `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`. Every row is a
plan record, not implementation authorization, and **no row may begin before
Wave 6 Target journey E2E passes**. Wave 7 runs single-writer.

## Superseded migration work

`SUPERSEDED_BY_APPROVED_DECISION`. Retained as historical planning records and
never implemented. Superseding these plans does **not** erase the current-state
fact that legacy tables and a `LegacyIdentityMapping` bridge exist in the
repository today — that fact stays documented in
`MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md` and
`MONGLE_LEGACY_TO_TARGET_MAPPING.md`. These items are simply removed from the
release-critical path.

| Former task / data class | Status | Replacement reset/cutover work |
|---|---|---|
| MONGLE-W6-IDENTITY-MAPPING-001 / legacy identity and credentials | `SUPERSEDED_BY_APPROVED_DECISION` | MONGLE-W6-EMPTY-TARGET-SCHEMA-001 |
| MONGLE-W6-GROUP-MEMBERSHIP-001 / legacy family and membership | `SUPERSEDED_BY_APPROVED_DECISION` | MONGLE-W6-NEW-FAMILY-ONBOARDING-001 |
| MONGLE-W6-MARKPOINT-LEDGER-001 / legacy ledger and balance | `SUPERSEDED_BY_APPROVED_DECISION` | MONGLE-W6-INITIAL-LEDGER-INVARIANT-001 |
| MONGLE-W6-HISTORY-RETENTION-001 / legacy mission, approval and chat history | `SUPERSEDED_BY_APPROVED_DECISION` | MONGLE-W6-LEGACY-READONLY-BACKUP-001 |
| MONGLE-W6-LEGACY-RETIREMENT-001 / legacy routes, APIs and credentials | `REDEFINED_BY_APPROVED_DECISION` | MONGLE-W6-LEGACY-WRITE-FREEZE-001, MONGLE-W6-NEW-SERVICE-CUTOVER-001, MONGLE-W6-POST-CUTOVER-VERIFICATION-001, MONGLE-W6-LEGACY-RETIREMENT-APPROVAL-001 |

Also superseded outside this document: `MONGLE-W3-MARKPOINT-OWNERSHIP-ADAPTER-001`,
whose legacy backfill/adapter framing D8 prohibits. See
`MONGLE_IMPLEMENTATION_BACKLOG.md`.

## Replacement cutover work

| Task ID | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|
| MONGLE-W6-EMPTY-TARGET-SCHEMA-001 | `BLOCKED_BY_DEPENDENCY` | fresh Target schema validation | Wave 6 E2E pass | Verify the Target schema starts empty, with no legacy Player/Admin auto-provisioning and no implicit legacy-identity path into an Account. `MIGRATION_GUARD` tests |
| MONGLE-W6-SEED-FIXTURE-SEPARATION-001 | `BLOCKED_BY_DEPENDENCY` | production seed and fixture separation | MONGLE-W6-EMPTY-TARGET-SCHEMA-001 | Prove test, fixture, preview and synthetic E2E data cannot become Target operational data, and that operational seeding is explicit and reviewable. `MIGRATION_GUARD` tests |
| MONGLE-W6-NEW-FAMILY-ONBOARDING-001 | `BLOCKED_BY_DEPENDENCY` | new Account and family bootstrap from empty | MONGLE-W6-EMPTY-TARGET-SCHEMA-001; Wave 1 | Validate creating a new Account, FamilyGroup and FamilyMembership and reaching a usable state from a genuinely empty system, including the empty-state onboarding path and the FamilyAdmin-provisioned-Account path |
| MONGLE-W6-INITIAL-LEDGER-INVARIANT-001 | `BLOCKED_BY_DEPENDENCY` | new Markpoint ledger opening invariant | MONGLE-W6-NEW-FAMILY-ONBOARDING-001; Wave 5 | Validate that a new ledger opens at its defined zero/start state with **no legacy opening balance** and no imported history |
| MONGLE-W6-LEGACY-WRITE-FREEZE-001 | `BLOCKED_BY_DEPENDENCY` | Legacy write freeze and access control | explicit PM authorization | Stop legacy writes and restrict access, with a verifiable freeze point. **Non-destructive** — freezing is not deleting |
| MONGLE-W6-LEGACY-READONLY-BACKUP-001 | `BLOCKED_BY_DEPENDENCY` | Legacy read-only archive and backup | MONGLE-W6-LEGACY-WRITE-FREEZE-001 | Retain Legacy separately as a verified read-only archive/backup for reference and audit. No Target history import; Legacy is never an automatic fallback or SSOT |
| MONGLE-W6-NEW-SERVICE-CUTOVER-001 | `BLOCKED_BY_DEPENDENCY` | Target cutover | write freeze, archive, and Wave 6 E2E pass; explicit PM authorization | Cut over to the Target system. Outward-facing and hard to reverse, so it requires its own PM go/no-go with a rollback position stated in advance |
| MONGLE-W6-POST-CUTOVER-VERIFICATION-001 | `BLOCKED_BY_DEPENDENCY` | post-cutover verification | MONGLE-W6-NEW-SERVICE-CUTOVER-001 | Re-verify Target journeys on the live system, confirm no Legacy fallback occurred, and confirm no Legacy or fixture data contaminated operational data |
| MONGLE-W6-LEGACY-RETIREMENT-APPROVAL-001 | `BLOCKED_BY_DEPENDENCY` | PM-authorized Legacy retirement | MONGLE-W6-POST-CUTOVER-VERIFICATION-001; **explicit PM approval** | The **only** task under which destructive Legacy deletion may occur, and only after explicit PM approval. Until it is approved and executed, Legacy stays read-only |

## Prohibitions

- **No task in this backlog may delete Legacy data as a consequence of D8 RESET.** Destructive deletion happens only under `MONGLE-W6-LEGACY-RETIREMENT-APPROVAL-001` after explicit PM approval.
- No legacy identity, credential, PIN, family, role, mission, point, balance, level, reward, message or notification record is imported, converted or backfilled.
- No legacy point balance becomes a Target opening balance.
- No legacy PIN or credential becomes a platform password or a Wagle PIN.
- Legacy is never an automatic fallback or an SSOT for Target operation.
- Legacy UI, routes, APIs and auth mechanisms are not Target compatibility requirements.
- Cutover does not begin before Wave 6 Target journey E2E passes.
