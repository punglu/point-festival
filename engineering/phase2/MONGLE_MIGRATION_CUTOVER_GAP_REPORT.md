# MONGLE_MIGRATION_CUTOVER_GAP_REPORT

> **PARTIALLY_SUPERSEDED:** D8 `RESET` is approved. This report's Legacy mapping/backfill/reconciliation recommendations are historical only; Target starts empty and Legacy is retained separately read-only until PM-approved retirement.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Per PM's corrected framing: a Gap here means the *target* Mongle product cannot do something it needs to, not merely "this differs from the legacy system." Classified using the same taxonomy as the original Gap Report (`NO_CHANGE_REQUIRED`/`DOCUMENTATION_ONLY`/`API_ADAPTER_REQUIRED`/`API_CHANGE_REQUIRED`/`QUERY_OR_READ_MODEL_REQUIRED`/`MIGRATION_REQUIRED`/`UNKNOWN`), plus a cutover-sequencing section the original report didn't need (since it assumed no wholesale identity-model change).

## Product Gaps (target-framing)

### GT1 — No Account-native Authentication/Session exists at all

**Classification: `IMPLEMENTATION_REQUIRED`** (new tables + new routes). **No longer decision-blocked** — approved D2 fixes the credential (`아이디 + 플랫폼 비밀번호`, email/phone not required, FamilyAdmin may provision independent Accounts) and approved D3 fixes the persistent Account-scoped Session and the separate optional Wagle PIN. This is Wave 1 implementation scope.

Current-state fact: every other platform capability (FamilyGroup/Membership/Role/Doran messaging) is today reachable only by first logging in through the legacy PIN/admin-password mechanism and being bridged via `LegacyIdentityMapping`, and there is no way yet to create an Account that was not first a legacy Player/Admin.

**This does not make `LegacyIdentityMapping` a Target bootstrapping path.** Under D8 RESET the Wave 1 credential/Session work creates new Accounts directly; it must not be designed as a legacy-identity bridge, and the current dependency is precisely what Wave 1 removes.

### GT2 — 와글와글 frontend has zero wiring to its own (already-target-shaped) backend

**Classification: `API_ADAPTER_REQUIRED` + `QUERY_OR_READ_MODEL_REQUIRED`** (restated from the original Gap Report's G1 — this finding does not change under the corrected framing, since Doran's backend already **is** the target architecture, not a legacy system being replaced).

Unchanged from the original Gap Report: `DoranLanding.tsx` renders exclusively from static preview fixtures; no batch room-list-with-preview-and-unread endpoint exists; the Outbox-to-Doran relay worker does not exist. See `MONGLE_REALTIME_MESSAGING_CONTRACT.md`'s "Genuinely open items" for full detail.

### GT3 — MarkPoint's entire persistence and authorization layer still points at legacy Player identity

**Classification: `MIGRATION_REQUIRED` (schema) + `API_CHANGE_REQUIRED` (auth dependency swap)**, per `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`.

This is a target-framing-specific Gap that would not have been flagged under the original (legacy-preserving) framing at all — under that framing, MarkPoint's current behavior was "correct" because there was no different target to compare against. Under the corrected framing, this is the central, defining Gap of the whole reconciliation: MarkPoint is supposed to be "몽글의 사용자·그룹·권한·세션 구조 위에 새로 개발하는 서비스," and today it is built entirely on the pre-Mongle `players` table instead.

### GT4 — No real-time delivery transport exists for 와글와글

**Classification: `IMPLEMENTATION_REQUIRED`.** D6 approves WebSocket foreground realtime and Web Push background notification; polling-only Target is rejected. The current absence of a complete transport remains implementation scope, not a product-decision gap.

### GT5 — Legacy cutover sequencing

**Classification: `RESET_CUTOVER_REQUIRED`.** D8 resolves the former migration choice: no Legacy identity auto-provisioning or credential backfill occurs. Users create a new Account/FamilyGroup or newly join a family. Legacy remains read-only backup/reference and is not automatic fallback; destructive deletion requires the separate PM retirement gate.

### GT6 — Legacy point/mission history

**Classification: `RESET_APPROVED`.** Existing mission, point, balance, approval, level, reward and chat history is not imported. New Markpoint begins with a new ledger and new records; Legacy history is separately retained read-only until retirement approval.

## Findings carried forward unchanged from the original (Axis A) Gap Report

These remain valid internal-consistency findings regardless of framing — restated by reference, not re-derived:

- G3 (`total_points` vs `total_earned` naming ambiguity) — Legacy reference evidence only under D8; any new Target ledger naming is defined afresh.
- G4 (duplicate `get_current_user` function names) — both are classified `REPLACE` in the Legacy-to-Target Mapping; the naming-hazard observation itself remains a valid caution during the transition period while both still exist.
- G5 (`missions.status` CHECK constraint missing `cancelled`) — Legacy reference defect; it is not a data-import or Target migration gate under D8.
- G9 (`GET /api/players` has no authentication) — under the target framing, this specific route is itself `REFERENCE_ONLY`/heading toward `REPLACE` (see Legacy-to-Target Mapping), so the unauthenticated-access observation is scoped to a route that won't survive cutover anyway, not a live target-architecture concern.
- G11, G12, G13, G14 (unrelated structural/documentation notes: `reply_to_message_id` no FK, `doran_rooms.version` unused, test deps not in requirements.txt, migration filename/revision-id mismatches) — unaffected by this framing correction, still open as originally classified.

## Cutover sequencing (recommended order, not a PM-approved plan)

1. Use the approved D1–D8 Target contract; D8 requires an empty new-start data boundary rather than Legacy migration.
2. Build Account-native Auth/Session (GT1) — nothing else in this sequence can be tested end-to-end as a real user journey without it.
3. Build new Markpoint ownership/auth boundaries without importing or transforming Legacy operational records.
4. Wire 와글와글's frontend to its already-complete backend (GT2), build the missing batch room-list endpoint, and build the Outbox-relay worker.
5. Implement the approved D6 WebSocket/Web Push realtime contract.
6. Validate new-start journeys, freeze Legacy writes/access as planned, retain read-only backup, and retire Legacy only after PM approval.

This order is a historical dependency recommendation, not the implementation plan. The next authorized planning work is `APPROVED-DECISIONS-TO-IMPLEMENTATION-PLAN`.
