# MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001 — Phase D Slice Mapping

Built before any Phase D code, per PM direction: a `SCREEN_ID → REQUIRED_
CAPABILITY → BACKEND_DOMAIN → BACKEND_SLICE_ID → QUERY/COMMAND →
SHARED_CONSUMER_SCREENS` mapping so a Slice consumed by several screens is
built once, with one set of endpoints, not once per screen. 19
`CREATE_NEW_VERTICAL_SLICE` screens map to 11 distinct Slices; 2
`REUSE_EXISTING_PRODUCT_LOGIC` screens (`3c`/`3d`) consume the existing
Wagle rooms/messages Slice instead of a new one. 21 screens total.

Every new Slice is Account-native, family-scoped
(`FamilyMembership`-owned), and follows the same authorization shape
already used everywhere else in this codebase:
`get_family_membership`/`require_permission` at the route boundary, a
Service SSOT module, a Thin Controller, additive-only migrations. No Slice
here touches a policy-undecided capability (binary file storage, account
deletion, family-invitation model) — those stay isolated per the Matrix.

## SLICE-TODO

| Field | Value |
| --- | --- |
| Screens | `1i` (할 일) |
| Backend domain | new `app/domains/family_todo/` |
| Query/Command | `GET/POST /api/families/{family_id}/todos`, `PATCH/DELETE /api/families/{family_id}/todos/{id}` |
| Shared consumers | none — single-screen Slice |
| Notes | Simplest Slice: `family_id`, `assignee_membership_id`, `title`, `status` (open/done), `due_date` (nullable). No policy blocker. |

## SLICE-FAMILY-RULES

| Field | Value |
| --- | --- |
| Screens | `1v` (가족 규칙 설정) |
| Backend domain | new `app/domains/family_rules/` |
| Query/Command | `GET /api/families/{family_id}/rules`, `PUT /api/families/{family_id}/rules` (whole-list replace, matching the Screen's own "edit the whole list" shape rather than per-row CRUD) |
| Shared consumers | none |
| Notes | `family_id`, `category`, `label`, `value_text`. Read needs `FAMILY_READ`; write needs `FAMILY_MEMBERS_MANAGE` (parent-authored rules). |

## SLICE-NOTIFICATION-PREFERENCES

| Field | Value |
| --- | --- |
| Screens | `2n` (알림 세부설정) |
| Backend domain | new `app/domains/notification_preferences/` (Account-native, self-scoped — not `family` domain, since a preference belongs to the Account, not a Membership) |
| Query/Command | `GET /api/me/notification-preferences`, `PUT /api/me/notification-preferences` |
| Shared consumers | none directly, but the *shape* (per-Account boolean toggles) is the eventual target for `SLICE-NOTIFICATION-LIST`'s own delivery preferences once that Slice exists — not built now, noted so the two are not designed to conflict later. |
| Notes | Self-service only, `get_current_account`, no permission beyond authentication (same shape as `PATCH /api/me`). |

## SLICE-SCHEDULE

| Field | Value |
| --- | --- |
| Screens | `1g` (가족 일정, list), `1o` (일정 추가, create), `2u` (일정 상세, detail/edit/delete), `3a` (가족 캘린더 공유, share settings) |
| Backend domain | new `app/domains/family_schedule/` |
| Query/Command | `GET/POST /api/families/{family_id}/schedule-events`, `GET/PATCH/DELETE /api/families/{family_id}/schedule-events/{id}` |
| Shared consumers | `1g`↔`1o`↔`2u`↔`3a` all share one `FamilyScheduleEvent` aggregate — built once. `3a`'s "share settings" is an additive field on the same row (`visibility`), not a second table. |
| Notes | `family_id`, `title`, `starts_at`, `ends_at` (nullable), `location` (nullable), `created_by_membership_id`, `visibility` (default `family`, for `3a`). No policy blocker. |

## SLICE-ALBUM-METADATA

| Field | Value |
| --- | --- |
| Screens | `1h` (앨범, list), `1p` (사진 상세, detail), `1w` (앨범 검색 결과, search), `2y` (앨범 공유설정, share settings) |
| Backend domain | new `app/domains/family_album/` |
| Query/Command | `GET/POST /api/families/{family_id}/albums`, `GET /api/families/{family_id}/albums/{id}/photos`, `POST /api/families/{family_id}/albums/{id}/photos` (metadata only — see Notes), `PATCH .../photos/{photo_id}`, `GET .../albums/search?q=` |
| Shared consumers | `1h`↔`1p`↔`1w`↔`2y` all share one `Album`/`Photo` metadata aggregate. |
| Notes | **Metadata only — no binary upload.** `Photo` rows get `caption`, `taken_at`, `uploaded_by_membership_id`, but **no image file/URL field is added**: no storage abstraction exists anywhere in `backend/app` (confirmed Phase 0/C finding, same gate as `2v`/`2z`'s avatar half). A `Photo` row this Slice creates has no picture to show — `1p`'s photo detail and `1w`'s search results render real metadata (caption/date/uploader) with an explicit "이미지 없음"-shaped empty visual, never a fabricated placeholder image pretending to be a real upload. `2v` (앨범 업로드 진행) itself is not in this Slice — it stays `POLICY_BLOCKED` until the storage decision is made, and this Slice's create endpoint is deliberately metadata-only so building it does not quietly presuppose that decision. |

## SLICE-REWARD-CATALOG

| Field | Value |
| --- | --- |
| Screens | `1l` (보상 교환), `2h` (교환 확인), `2j` (리워드샵) |
| Backend domain | new `app/domains/reward_catalog/` |
| Query/Command | `GET/POST /api/families/{family_id}/rewards` (catalog CRUD, admin-managed), `POST /api/families/{family_id}/rewards/{id}/redeem` (redemption — internally calls the **existing** `markpoint_target.service.adjust_points` for the point-debit side, does not duplicate ledger logic) |
| Shared consumers | `1l`↔`2h`↔`2j` all read/redeem from the same `Reward` catalog — built once, not three times, per the Matrix's own recommendation. |
| Notes | `family_id`, `name`, `cost`, `is_available`. Redemption is transactional with the ledger debit (all-or-nothing, matching `bulk_approve_missions`'s existing all-or-nothing precedent) — insufficient balance rejects the whole redemption, never a partial one. |

## SLICE-NOTIFICATION-LIST

| Field | Value |
| --- | --- |
| Screens | `1n` (알림 목록) |
| Backend domain | new `app/domains/account_notification/` (Account-native — deliberately **not** an extension of the legacy `notification` domain, which is `player_id`-scoped via `LegacyIdentityMapping` and excluded by D8 for Account-native users) |
| Query/Command | `GET /api/me/notifications`, `POST /api/me/notifications/{id}/read` |
| Shared consumers | none now. Future Wagle Push (`D6-P1`, deferred) and this in-app list are related-but-distinct delivery mechanisms per the Matrix's own note — this Slice does not read or write any Wagle Push table. |
| Notes | `account_id`, `title`, `body`, `read_at` (nullable), `created_at`. Self-scoped only (`get_current_account`). No write path other than the system creating rows — this task does not decide *who* triggers a notification (that is a future integration point, e.g. mission approval), only the storage/read/mark-read contract the screen needs today. |

## SLICE-FAMILY-ACTIVITY-LOG

| Field | Value |
| --- | --- |
| Screens | `2r` (가족 활동 로그) |
| Backend domain | new `app/domains/family_activity_log/` |
| Query/Command | `GET /api/families/{family_id}/activity-log` |
| Shared consumers | none, but **reads from existing sources rather than a new event-logging table**, per the Matrix's own design recommendation: `MarkpointAuditEvent` (already exists, `markpoint_target.models`) and `family_memberships`' own `created_at`/`updated_at` are UNIONed and paginated, not re-emitted into a parallel log. |
| Notes | Read-only, lowest priority of the 11 Slices. No write endpoint — nothing in this Slice can go stale relative to its sources because it never copies them. |

## SLICE-WAGLE-ATTACHMENTS

| Field | Value |
| --- | --- |
| Screens | `2b` (사진/파일 전체보기) |
| Backend domain | `wagle` (extends existing `WagleMessage`, does not create a new domain) |
| Query/Command | Would be `message_type='ATTACHMENT'` on the existing `POST .../messages` plus a `file_url`/`file_meta` field |
| Shared consumers | n/a |
| Notes | **Not buildable now — same storage-infra `POLICY_REQUIRED` gate as `2v`/`SLICE-ALBUM-METADATA`'s binary half.** Unlike Album, there is no metadata-only subset of "file viewer" that is meaningfully real without an actual file to view — listed here for completeness of the 11-Slice count, but this task does not implement it. Isolated, not blocking the rest of Phase D. |

## SLICE-WAGLE-BOARD-REACTIONS

| Field | Value |
| --- | --- |
| Screens | `3e` (인기 게시글) |
| Backend domain | `wagle` (extends the board-as-room design below) |
| Query/Command | `POST /api/families/{family_id}/wagle/rooms/{room_id}/messages/{message_id}/reactions`, `GET .../messages/{message_id}/reactions` |
| Shared consumers | depends on `3c`/`3d` (board-as-room) landing first — "popularity" needs a message to react to. |
| Notes | Lowest priority of the three board screens per the Matrix's own note. Built after `3c`/`3d` in this task's own execution order, not before. |

## SLICE-SEARCH

| Field | Value |
| --- | --- |
| Screens | `3j` (검색 전체) |
| Backend domain | new `app/domains/family_search/` (thin fan-out, no owned table) |
| Query/Command | `GET /api/families/{family_id}/search?q=` — fans out to `markpoint_target` (mission titles) and `wagle` (message bodies, participant's visible range only) |
| Shared consumers | n/a — this Slice *consumes* other Slices' data, it does not own any. |
| Notes | Scoped first pass to sources that already have real data (Markpoint missions, Wagle messages), per the Matrix's own recommendation — Album/Schedule search (`1w`'s own search is Album-internal, not this cross-entity one) is **not** included in `3j`'s first pass since those Slices may not exist yet depending on execution order; built last of the 11 because it is the only Slice with a hard dependency on others already existing. |

## REUSE-WAGLE-ROOMS-AS-BOARD (not a new Slice)

| Field | Value |
| --- | --- |
| Screens | `3c` (가족 게시판), `3d` (댓글 작성) |
| Backend domain | `wagle` (no new domain, no new table) |
| Query/Command | A "board" is a dedicated `WagleRoom` (`room_type='GROUP'`, a reserved title/flag distinguishing it as the family's board room from an ordinary chat room); a "post" is a `WagleMessage`; a "comment" is a reply via the already-shipped `reply_to_message_id` (`2g`, Phase C) |
| Shared consumers | `2g`'s reply-to capability is reused directly for `3d`'s comment-on-post semantics — no new reply concept. |
| Notes | Reuses existing family-scoping, ordering, and read-state infra instead of duplicating it in a new `Post` aggregate, per the Matrix's own recommendation. Confirmed non-destructive/additive: creating one reserved-purpose Room per Family does not alter any existing Wagle behavior. |

## Execution order for this task

1. `SLICE-TODO`, `SLICE-FAMILY-RULES`, `SLICE-NOTIFICATION-PREFERENCES` — simplest, no dependencies, no shared screens.
2. `SLICE-SCHEDULE` — 4 screens, one aggregate, no dependencies.
3. `SLICE-ALBUM-METADATA` — 4 screens, one aggregate, metadata-only (storage gate isolated).
4. `SLICE-REWARD-CATALOG` — 3 screens, one aggregate, reuses existing ledger-adjustment logic for redemption.
5. `SLICE-NOTIFICATION-LIST` — 1 screen, new Account-native domain.
6. `SLICE-FAMILY-ACTIVITY-LOG` — 1 screen, read-only, reads existing sources.
7. `REUSE-WAGLE-ROOMS-AS-BOARD` (`3c`/`3d`) — no new domain.
8. `SLICE-WAGLE-BOARD-REACTIONS` (`3e`) — depends on step 7.
9. `SLICE-SEARCH` (`3j`) — depends on steps 2-6 existing to have something to search.
10. `SLICE-WAGLE-ATTACHMENTS` (`2b`) — not implemented this task, `POLICY_REQUIRED` (storage infra).

Each step closes with the same discipline as Phase B/C: migration +
model + schema + service + router + backend tests, `openapi.d.ts`
regenerated, frontend adapter wired off its fixture, Playwright coverage
where the flow is genuinely new user-facing behavior, full backend suite
re-run, Matrix/Report/QA/Handoff updated before moving to the next step.
