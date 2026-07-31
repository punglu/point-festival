# MONGLE_MIGRATION_CUTOVER_GAP_REPORT

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Per PM's corrected framing: a Gap here means the *target* Mongle product cannot do something it needs to, not merely "this differs from the legacy system." Classified using the same taxonomy as the original Gap Report (`NO_CHANGE_REQUIRED`/`DOCUMENTATION_ONLY`/`API_ADAPTER_REQUIRED`/`API_CHANGE_REQUIRED`/`QUERY_OR_READ_MODEL_REQUIRED`/`MIGRATION_REQUIRED`/`UNKNOWN`), plus a cutover-sequencing section the original report didn't need (since it assumed no wholesale identity-model change).

## Product Gaps (target-framing)

### GT1 — No Account-native Authentication/Session exists at all

**Classification: `MIGRATION_REQUIRED` + `API_CHANGE_REQUIRED`** (new tables + new routes), blocked on PM_DECISION_REQUIRED #2 (Business Glossary).

This is the single largest gap in the entire target architecture: every other Mongle-native capability (Group/Membership/Role/Doran messaging) is reachable only by first logging in through the legacy PIN/admin-password mechanism and being bridged via `LegacyIdentityMapping`. There is no way today to create a new Account that isn't first a legacy Player/Admin. Until this is built, Mongle cannot be described as "owning" Auth/Session in any real sense — it currently borrows legacy Auth entirely.

### GT2 — 와글와글 frontend has zero wiring to its own (already-target-shaped) backend

**Classification: `API_ADAPTER_REQUIRED` + `QUERY_OR_READ_MODEL_REQUIRED`** (restated from the original Gap Report's G1 — this finding does not change under the corrected framing, since Doran's backend already **is** the target architecture, not a legacy system being replaced).

Unchanged from the original Gap Report: `DoranLanding.tsx` renders exclusively from static preview fixtures; no batch room-list-with-preview-and-unread endpoint exists; the Outbox-to-Doran relay worker does not exist. See `MONGLE_REALTIME_MESSAGING_CONTRACT.md`'s "Genuinely open items" for full detail.

### GT3 — MarkPoint's entire persistence and authorization layer still points at legacy Player identity

**Classification: `MIGRATION_REQUIRED` (schema) + `API_CHANGE_REQUIRED` (auth dependency swap)**, per `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`.

This is a target-framing-specific Gap that would not have been flagged under the original (legacy-preserving) framing at all — under that framing, MarkPoint's current behavior was "correct" because there was no different target to compare against. Under the corrected framing, this is the central, defining Gap of the whole reconciliation: MarkPoint is supposed to be "몽글의 사용자·그룹·권한·세션 구조 위에 새로 개발하는 서비스," and today it is built entirely on the pre-Mongle `players` table instead.

### GT4 — No real-time delivery transport exists for 와글와글

**Classification: `UNKNOWN` scope, likely `API_CHANGE_REQUIRED` (new WebSocket/SSE endpoint) or a product decision to accept polling** — restated from `MONGLE_REALTIME_MESSAGING_CONTRACT.md` item 5. Confirmed zero WebSocket code anywhere in `backend/app` or `frontend/src` by direct grep this task. Whether "실시간" (realtime) in the product name requires push delivery or whether a well-tuned polling interval is acceptable for launch is a product decision, not decided here.

### GT5 — Legacy cutover sequencing has a genuine bootstrapping problem

**Classification: `UNDECIDED`, product/PM sequencing decision, not a code Gap per se.**

Every currently-working login path in the entire repository is legacy (`player_auth` PIN, `admin_auth` username/password). If GT1 (Account-native Auth) is built and the legacy paths are then deprecated per the Legacy-to-Target Mapping's `DEPRECATE` classification, there must be a real migration step that either (a) auto-provisions an Account+credential for every existing legacy identity as part of a one-time backfill, or (b) requires every existing family to "re-register" under the new Auth before they can log in again. Neither is designed here; both have real UX consequences a PM must weigh. This is flagged as its own Gap specifically because "just delete the legacy auth tables" is not a safe cutover without one of these two paths existing first.

### GT6 — Data-migration decision for existing point/mission history is unmade

**Classification: `UNDECIDED`**, restated from `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`'s closing section. Whether existing `missions`/`daily_points`/`deductions`/`feedbacks`/`cheer_messages` rows get backfilled onto newly-created Memberships, or whether MarkPoint-on-Mongle launches with a clean slate, is unresolved and consequential (real families' point history either survives or doesn't).

## Findings carried forward unchanged from the original (Axis A) Gap Report

These remain valid internal-consistency findings regardless of framing — restated by reference, not re-derived:

- G3 (`total_points` vs `total_earned` naming ambiguity) — still applies once `total_earned` is re-homed to `family_memberships` (see Target Column Dictionary); the naming ambiguity itself is unaffected by which table owns the column.
- G4 (duplicate `get_current_user` function names) — both are classified `REPLACE` in the Legacy-to-Target Mapping; the naming-hazard observation itself remains a valid caution during the transition period while both still exist.
- G5 (`missions.status` CHECK constraint missing `cancelled`) — unaffected by the ownership-FK transform; still needs its own resolution (migration or code fix) independent of this reconciliation.
- G9 (`GET /api/players` has no authentication) — under the target framing, this specific route is itself `REFERENCE_ONLY`/heading toward `REPLACE` (see Legacy-to-Target Mapping), so the unauthenticated-access observation is scoped to a route that won't survive cutover anyway, not a live target-architecture concern.
- G11, G12, G13, G14 (unrelated structural/documentation notes: `reply_to_message_id` no FK, `doran_rooms.version` unused, test deps not in requirements.txt, migration filename/revision-id mismatches) — unaffected by this framing correction, still open as originally classified.

## Cutover sequencing (recommended order, not a PM-approved plan)

1. PM resolves the open PM_DECISION_REQUIRED items (Group-vs-Family naming, Auth/Session model choice, MarkPoint's Group-scoping URL convention, data-migration approach for GT6).
2. Build Account-native Auth/Session (GT1) — nothing else in this sequence can be tested end-to-end as a real user journey without it.
3. TRANSFORM MarkPoint's ownership FKs and auth dependencies (GT3), since this is the highest-volume, most mechanical change and benefits from having real Sessions to test against.
4. Wire 와글와글's frontend to its already-complete backend (GT2), build the missing batch room-list endpoint, and build the Outbox-relay worker.
5. Decide and, if needed, build real-time delivery (GT4).
6. Execute the legacy data migration/cutover (GT5/GT6) and only then deprecate the legacy PIN/admin-password/`chat_messages` paths.

This order is a recommendation grounded in dependency logic (Auth blocks everything; MarkPoint's transform is independent of 와글와글's frontend wiring and can proceed in parallel once Auth exists), not a PM-approved project plan.
