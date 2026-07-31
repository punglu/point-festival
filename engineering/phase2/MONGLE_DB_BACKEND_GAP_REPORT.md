# MONGLE_DB_BACKEND_GAP_REPORT

> **AXIS: LEGACY_CURRENT_STATE (A) — superseded as the primary Gap source.**
> PM corrected this task's central axis after this document was written:
> a difference from the legacy system is only a Gap when it fails a
> *target* Mongle requirement, not merely because it differs from today's
> behavior. The internal-consistency findings below (G3-G14: naming splits,
> a missing CHECK-constraint value, an unused column, etc.) remain valid
> factual observations about the current codebase. G1 (Doran/frontend
> disconnect) and G2 (level.thresholds/level-tiers disconnect) are
> superseded by `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md`, which restates
> them against the target architecture instead of the legacy one.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001

Every Gap below is classified into exactly one of: `NO_CHANGE_REQUIRED`, `DOCUMENTATION_ONLY`, `API_ADAPTER_REQUIRED`, `API_CHANGE_REQUIRED`, `QUERY_OR_READ_MODEL_REQUIRED`, `MIGRATION_REQUIRED`, `UNKNOWN`. No migration is written in this task regardless of classification.

## G1 — Doran (A4/와글와글) has a fully-built, tested backend and zero frontend wiring

**Classification: `API_ADAPTER_REQUIRED`** (for rooms/messages/participants/read-state) **+ `QUERY_OR_READ_MODEL_REQUIRED`** (for a batch room-list-with-preview-and-unread-count endpoint, which does not exist in any form today) **+ a separate, unbuilt Worker** (not a schema/API gap at all — an application process that does not yet exist).

Evidence: `frontend/src/platform/pages/DoranLanding.tsx` imports exclusively from `../doran/preview/*` (`doranPreviewRooms`, `doranPreviewMessagesByRoom`, `doranPreviewServiceEventsByRoom`) — confirmed by direct source read, not inference. The exact strings rendered ("엄마", "우리 가족 주말 계획", "마크포인트 알림", the deliberately-long test name) are hardcoded in `frontend/src/platform/doran/preview/rooms.ts`. Meanwhile, all 16 real Doran HTTP operations (`doran/router.py`) are implemented, migration-backed (3 of the 5 total migrations are Doran-specific), and covered by `backend/tests/test_doran_*.py` — 71 backend tests passed in this task's own isolated-DB run.

Sub-gaps:
- No endpoint returns "rooms + last message preview + unread count" in one call; a real room-list screen needs either N+1 round trips or a new aggregating read model.
- `service_outbox_events` has a real producer (`mission/service.py::_emit_mission_completed_event`, triggered on every mission completion when the player has a linked, active Family) but **no consumer was found anywhere in `backend/app`** — no worker, no cron, no scheduled task drains `PENDING` rows into a `publish_service_action` call. The mechanism the frontend's `ServiceActionCard` component was built to render (a MarkPoint mission-completion event arriving as a Doran SERVICE message) cannot happen today even if the frontend were wired to the real Doran API, because nothing ever publishes it.

This is not a design-document mismatch — the design documents (`DORAN_MESSAGING_CONTRACT.md`, `DORAN_SYNC_AND_WEBSOCKET_CONTRACT.md`, etc.) were deliberately not treated as authoritative for this Gap Report (per the task's own instruction to prefer current code over historical documents); this finding stands on the code alone.

## G2 — `level.thresholds` config key does not exist; A1's pre-login level-pill fetch is structurally unfixable as written

**Classification: `API_ADAPTER_REQUIRED`** (a working fix exists without any DB/API change) **+ `DOCUMENTATION_ONLY`** (to retire the dead `level.thresholds` reference).

The real, tested, title-bearing level system is `level_tiers` + `GET /api/level-tiers/player/{id}`. A completely separate, frontend-only mechanism reads `GET /api/configs/level.thresholds` — a key that is (a) behind `PLAYER_OR_ADMIN` auth and thus always 401s when called pre-login as A1 currently does it, and (b) never seeded anywhere: confirmed absent from both `database/init.sql`'s `app_configs` seed rows and `backend/scripts/phase1_seed_synthetic.py` (neither file contains the string `level.thresholds` or `level_thresholds`). Even a fully-authenticated caller would get a 404 for this key (`config/service.py::get_config_by_key` raises 404 on a missing key). Grep of `frontend/src` for `level-tiers` (the real endpoint) returned **zero matches anywhere in the codebase** — not just on A1, on any screen.

Fix path (not applied in this task): replace the `level.thresholds` fetch with a call to `GET /api/level-tiers/player/{id}` made *after* PIN success (A1's login-error/success flow already has a natural place for this), or extend `GET /api/players` itself to include level/title fields computed server-side so even the pre-login profile cards can show a title without requiring a second authenticated call per profile. Either path requires product/PM sign-off; not decided here.

## G3 — `total_points` vs `total_earned`: two different numbers, similar names

**Classification: `DOCUMENTATION_ONLY`** (the Naming Contract already records this; no code changes proposed here).

`PlayerListItem.total_points` = `SUM(daily_points.balance)` (current spendable balance, decreases on deduction/spend). `Player.total_earned` = a separate, monotonic lifetime counter used only as the leveling input. Both are legitimately different concepts, correctly computed, and not bugs — but their names alone do not convey the difference, and this exact confusion is very plausibly why A1 (and every other screen) has never wired up the real leveling system: a reader skimming `PlayerListItem` would reasonably assume `total_points` is what feeds `level_tiers.required_points`, but it does not.

## G4 — Two functions both named `get_current_user`, different modules, different behavior

**Classification: `DOCUMENTATION_ONLY`** for now (both are correctly used at every current call site; no live bug is caused by this today) — but flagged as a `MIGRATION_REQUIRED`-adjacent maintenance risk for whoever next edits auth: a careless copy-paste import (e.g. `from app.dependencies import get_current_user` in a file that actually needed the `auth.dependencies` player-only-normalized version, or vice versa) would silently compile and silently behave differently (different accepted `role` set, different returned dict shape: `{sub,role,...}` vs `{player_id,is_admin}`). No such miswiring was found in this task's read of every current router, but the hazard is structural, not hypothetical.

## G5 — `missions.status` CHECK constraint is missing `cancelled`, which application code actively uses

**Classification: `MIGRATION_REQUIRED`** (if the intent is to keep `cancelled` as a real, permanent status) **or `DOCUMENTATION_ONLY`**/code-fix (if `cancelled` was meant to be retired and `ROLE_TRANSITIONS` is the stale side).

`database/init.sql:41-43`'s CHECK constraint for `missions.status` lists exactly: `active, completed, failed, pending_approval, proposed, rejected`. `mission/service.py`'s `ROLE_TRANSITIONS` dict (lines 146-160) defines an admin-only `"completed": ["cancelled", "active"]` transition and a `"cancelled": ["active"]` transition — i.e., application code believes `cancelled` is a valid, reachable status, but the DB itself would reject an `UPDATE missions SET status='cancelled'`. This task did not attempt a live write to confirm the exact failure mode (writing to any table is out of this task's scope), so the practical impact (does this code path get exercised in production today, or is it dead/never-hit code) is `UNKNOWN` — but the CHECK-constraint/application-code mismatch itself is a direct, source-confirmed fact, not an inference.

## G6 — `family_id` vs `family_group_id` naming split

**Classification: `DOCUMENTATION_ONLY`** (recorded in the Naming Contract; a rename would be `API_CHANGE_REQUIRED` + `MIGRATION_REQUIRED` if ever undertaken, but that decision is explicitly out of this task's scope).

## G7 — `membership_id` (family schema) vs `family_membership_id` (Doran schema, matches DB column) for the identical referent

**Classification: `DOCUMENTATION_ONLY`**, same reasoning as G6.

## G8 — 13 of 14 Family-domain API routes have no confirmed frontend consumer

**Classification: `NO_CHANGE_REQUIRED`** at the API layer (the routes are correct and tested) **+ implicitly `API_ADAPTER_REQUIRED`** whenever a Family-management UI is eventually built.

Only `GET /api/account-context` is confirmed called (`familyApi.ts`). Member invite/manage, role assign/revoke, and service-subscription toggle all have complete, permission-checked, tested server implementations but no UI anywhere in the current frontend (confirmed by grep of `frontend/src` for each route's literal path fragment). This is consistent with, and directly explained by, `FamilyLanding.tsx`'s own placeholder text (see Screen Data Contract Matrix, A2).

## G9 — `GET /api/players` has no authentication at all

**Classification: `NO_CHANGE_REQUIRED`** (this is confirmed intentional, per the route's own docstring: "Auth 페이지 PlayerSelector용, admin 제외" — it exists specifically to populate the pre-login A1 profile selector) — recorded here as a Gap-Report entry only because it is a genuine, security-relevant fact a PM should be aware of (unauthenticated callers can read every player's name, lock status, and current point balance), not because the current behavior is wrong for its stated purpose. No change proposed; flagged for awareness only.

## G10 — `doran_rooms`/`accounts`/`family_groups` all have both a `status='deleted'`-style string value **and** a separate `deleted_at` timestamp column — two ways to represent "this row is gone"

**Classification: `DOCUMENTATION_ONLY`**. Not confirmed to cause an active bug (no code path was found that sets one without the other, and no query was found that checks only one and misses rows where only the other is set) — recorded as a structural redundancy worth a future decision (pick one lifecycle representation per table), not an active defect.

## G11 — `doran_messages.reply_to_message_id` has no FK constraint at either the DB or ORM level

**Classification: `MIGRATION_REQUIRED`** if reply-integrity should be DB-enforced; `UNKNOWN` whether this is intentional (e.g. to allow replying to a message that was later hard-deleted, if that ever happens) or an oversight, since no code path in this task's scope reads or writes this column at all (grep of `doran/service.py` for `reply_to_message_id` found it only in the model declaration, never referenced in any service function).

## G12 — `doran_rooms.version` column exists but has no confirmed read/write site

**Classification: `UNKNOWN`**. Declared as an `Integer, server_default="1"` — looks like it was intended as an optimistic-concurrency-control column, but no `UPDATE ... WHERE version = :expected` pattern or any other reference to `.version` was found in `doran/service.py` during this task's read of the full file. Not confirmed dead, only confirmed unused within this task's scope.

## G13 — Test dependencies (`pytest`, `pytest-asyncio`, `httpx`) are not listed in `backend/requirements.txt`

**Classification: `DOCUMENTATION_ONLY`**. Confirmed by direct grep of `requirements.txt` (no match for `pytest` or `httpx`) despite `backend/tests/` requiring both to run at all; this task had to `pip install` them separately into a throwaway venv to execute the suite. Not a blocking defect (CI/dev setup evidently already knows to install them some other way, e.g. a separate dev-requirements file was not found either, so the exact mechanism is itself `UNKNOWN`), but worth a documentation note for anyone else reproducing this task's verification steps.

## G14 — Migration filename/revision-id mismatches (cosmetic)

**Classification: `DOCUMENTATION_ONLY`**. `0001_account_family_rbac_foundation.py` has `revision = "0001_account_family_rbac"` (filename has a `_foundation` suffix the revision id lacks). `0004_doran_reliable_service_slice.py` has `revision = "0004_doran_reliable_slice"` (filename says `_service_slice`, revision says `_reliable_slice`). Neither breaks Alembic (confirmed — the full chain applied cleanly in this task's isolated-DB run) since Alembic resolves the chain by revision id, not filename; recorded only as a minor maintenance-clarity note.

## Summary table

| Gap | Classification | Blocking? |
|---|---|---|
| G1 Doran frontend/backend disconnect | API_ADAPTER_REQUIRED + QUERY_OR_READ_MODEL_REQUIRED | Yes, for any real A4 work |
| G2 `level.thresholds` dead config key | API_ADAPTER_REQUIRED + DOCUMENTATION_ONLY | Yes, for A1/A3 level display |
| G3 total_points vs total_earned naming | DOCUMENTATION_ONLY | No |
| G4 duplicate `get_current_user` names | DOCUMENTATION_ONLY | No (latent risk only) |
| G5 `missions.status` missing `cancelled` in CHECK | MIGRATION_REQUIRED or code-fix | Unknown impact, confirmed mismatch |
| G6 `family_id`/`family_group_id` split | DOCUMENTATION_ONLY | No |
| G7 `membership_id`/`family_membership_id` split | DOCUMENTATION_ONLY | No |
| G8 Family UI mostly unbuilt | NO_CHANGE_REQUIRED (API) | No (API is fine, UI is simply absent) |
| G9 `GET /api/players` unauthenticated | NO_CHANGE_REQUIRED (by design) | No |
| G10 dual delete-representation | DOCUMENTATION_ONLY | No |
| G11 `reply_to_message_id` no FK | MIGRATION_REQUIRED (if desired) | No (unused today) |
| G12 `doran_rooms.version` unused | UNKNOWN | No |
| G13 test deps not in requirements.txt | DOCUMENTATION_ONLY | No |
| G14 migration filename/revision mismatches | DOCUMENTATION_ONLY | No |
