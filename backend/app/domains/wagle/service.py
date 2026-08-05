"""Wagle use cases. Each mutating public function owns one transaction."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family import service as family_service
from app.domains.family.models import FamilyGroup, FamilyMembership, MembershipRoleAssignment, Permission, Role, RolePermission, ServiceSubscription
from app.domains.wagle.board_constants import FAMILY_BOARD_ROOM_TITLE
from app.domains.wagle.models import WagleDirectPair, WagleMessage, WagleMessageReaction, WagleParticipant, WagleParticipantReadState, WagleRoom, WagleServiceAuditLog, WagleServiceBinding, ServicePrincipal
from app.domains.wagle.rules import canonical_direct_pair, visible_range
from app.domains.wagle.service_actor import issue_credential
# Imported as a module and called through a dotted reference per the Backend
# Guide's decomposed-service rule, which keeps the patch seam intact.
from app.domains.service_outbox import service as outbox_service

SERVICE_CODE = "wagle"
READ = "wagle.messages.read"; SEND = "wagle.messages.send"; CREATE = "wagle.rooms.create"; MANAGE_ROOM = "wagle.rooms.manage"; MANAGE_PARTICIPANTS = "wagle.participants.manage"


def denied(detail: str = "Wagle 권한이 없습니다") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def context(db: AsyncSession, user: dict, family_id: int):
    account = await family_service.resolve_current_account(db, user)
    membership = await family_service.get_active_membership(db, account.id, family_id)
    return account, membership


async def subscription_active(db: AsyncSession, family_id: int) -> bool:
    return (await db.execute(select(ServiceSubscription.id).where(ServiceSubscription.family_group_id == family_id, ServiceSubscription.service_code == SERVICE_CODE, ServiceSubscription.status == "active"))).scalar_one_or_none() is not None


async def _room(db: AsyncSession, family_id: int, room_id: UUID) -> WagleRoom:
    room = (await db.execute(select(WagleRoom).where(WagleRoom.id == room_id, WagleRoom.family_group_id == family_id, WagleRoom.deleted_at.is_(None)))).scalars().first()
    if room is None: raise HTTPException(status_code=404, detail="Room을 찾을 수 없습니다")
    return room


async def _participant(db: AsyncSession, room: WagleRoom, membership: FamilyMembership) -> WagleParticipant:
    participant = (await db.execute(select(WagleParticipant).where(WagleParticipant.room_id == room.id, WagleParticipant.family_membership_id == membership.id).order_by(WagleParticipant.created_at.desc()))).scalars().first()
    if participant is None or participant.status == "removed": raise denied("Room 참여자 권한이 필요합니다")
    return participant


async def participant_display_name(db: AsyncSession, family_membership_id: int) -> str:
    """Resolve a Wagle participant's human-readable name via the owning
    Family Membership -> Account, through the family domain's own public
    service function rather than a raw cross-domain query (this file already
    imports `family_service`/`FamilyMembership` for the same reason)."""
    membership = await db.get(FamilyMembership, family_membership_id)
    if membership is None:
        return ""
    account = await family_service.get_account(db, membership.account_id)
    return account.display_name if account else ""


async def _require_permission(db: AsyncSession, membership: FamilyMembership, code: str) -> None:
    # A participant is still the resource boundary; permission is an additional capability gate.
    # Retained read access deliberately does not disappear merely because the
    # Wagle subscription became suspended/cancelled.
    if code == READ:
        # MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001: this is an
        # existence check ("does any currently-active role grant READ"), not a
        # lookup of a specific row -- a membership legitimately holding 2+
        # roles that each grant `wagle.messages.read` (e.g. `participant` and
        # `room_admin` both do, per migration 0002) made this query return
        # more than one row, and `scalar_one_or_none()` raised
        # `MultipleResultsFound` (uncaught -> HTTP 500) instead of the
        # intended "yes, retained" answer. `.limit(1)` makes the cardinality
        # match what `scalar_one_or_none()` actually promises to handle,
        # without changing which memberships are granted retained access.
        retained = (await db.execute(select(Permission.id).join(RolePermission, RolePermission.permission_id == Permission.id).join(Role, Role.id == RolePermission.role_id).join(MembershipRoleAssignment, MembershipRoleAssignment.role_id == Role.id).where(MembershipRoleAssignment.membership_id == membership.id, MembershipRoleAssignment.revoked_at.is_(None), Role.is_active.is_(True), Permission.code == READ).limit(1))).scalar_one_or_none()
        if retained is not None:
            return
    if code not in await family_service.effective_permissions(db, membership): raise denied()


async def list_rooms(db, user, family_id):
    _, membership = await context(db, user, family_id)
    await _require_permission(db, membership, READ)
    rows = await db.execute(select(WagleRoom).join(WagleParticipant, WagleParticipant.room_id == WagleRoom.id).where(WagleRoom.family_group_id == family_id, WagleRoom.deleted_at.is_(None), WagleParticipant.family_membership_id == membership.id, WagleParticipant.status.in_(("active", "left"))).order_by(WagleRoom.updated_at.desc()))
    return list(rows.scalars())


async def list_rooms_with_preview(db, user, family_id):
    """Batch room list: each room with its last visible message and unread count.

    -- [Query] One round trip for the room-list screen. `list_rooms` above
    -- returns bare rows, which forced a caller to issue N further requests
    -- (last message + read state) per room; that N+1 is the gap this closes.
    --
    -- Two LATERAL subqueries rather than GROUP BY: "the latest row per room"
    -- and "count since my cursor" have different shapes, and LATERAL lets both
    -- reuse the (room_id, sequence) index with a plain ORDER BY ... LIMIT 1.
    --
    -- Visibility is the participant's own window, not the whole room:
    -- joined_sequence..left_sequence, matching `visible_range()` used by
    -- list_messages. A member who left still sees the history they were
    -- present for and nothing after it.

    Unread deliberately mirrors `read_state()`'s existing semantics exactly —
    own messages excluded, and because `sender_participant_id <> :pid` is NULL
    for SERVICE_ACTION rows, service messages are not counted either. That
    second effect is inherited, not chosen here: making the list disagree with
    the per-room endpoint would be worse than either rule alone. Whether
    service messages *should* raise unread is a user-visible read-display
    question that belongs to D6-P4, which is still undecided.
    """
    _, membership = await context(db, user, family_id)
    await _require_permission(db, membership, READ)
    rows = (
        await db.execute(
            text(
                """
                SELECT r.id AS room_id, r.family_group_id, r.room_type, r.title,
                       r.status, r.next_message_sequence, r.updated_at,
                       p.id AS participant_id, p.status AS participant_status,
                       COALESCE(rs.last_read_sequence, 0) AS last_read_sequence,
                       lm.sequence AS last_sequence, lm.body AS last_body,
                       lm.message_type AS last_message_type,
                       lm.created_at AS last_created_at,
                       lm.deleted_at AS last_deleted_at,
                       COALESCE(u.unread_count, 0) AS unread_count
                  FROM wagle_rooms r
                  JOIN wagle_participants p
                    ON p.room_id = r.id
                   AND p.family_membership_id = :membership_id
                   AND p.status IN ('active', 'left')
                  LEFT JOIN wagle_participant_read_states rs
                    ON rs.participant_id = p.id
                  LEFT JOIN LATERAL (
                        SELECT m.sequence, m.body, m.message_type,
                               m.created_at, m.deleted_at
                          FROM wagle_messages m
                         WHERE m.room_id = r.id
                           AND m.sequence >= p.joined_sequence
                           AND (p.left_sequence IS NULL OR m.sequence <= p.left_sequence)
                         ORDER BY m.sequence DESC
                         LIMIT 1
                  ) lm ON TRUE
                  LEFT JOIN LATERAL (
                        SELECT count(*) AS unread_count
                          FROM wagle_messages m2
                         WHERE m2.room_id = r.id
                           AND m2.sequence >= p.joined_sequence
                           AND (p.left_sequence IS NULL OR m2.sequence <= p.left_sequence)
                           AND m2.sequence > COALESCE(rs.last_read_sequence, 0)
                           AND m2.sender_participant_id <> p.id
                  ) u ON TRUE
                 WHERE r.family_group_id = :family_id
                   AND r.deleted_at IS NULL
                 ORDER BY COALESCE(lm.created_at, r.updated_at) DESC, r.id
                """
            ),
            {"membership_id": membership.id, "family_id": family_id},
        )
    ).mappings().all()
    return rows


async def create_room(db: AsyncSession, user: dict, family_id: int, data):
    account, membership = await context(db, user, family_id)
    await _require_permission(db, membership, CREATE)
    if not await subscription_active(db, family_id): raise denied("Wagle subscription is read-only")
    if data.room_type == "DIRECT":
        target = await db.get(FamilyMembership, data.target_membership_id)
        if target is None or target.family_group_id != family_id or target.status != "active" or target.deleted_at is not None: raise HTTPException(status_code=422, detail="활성 같은 가족 구성원이 필요합니다")
        try: low, high = canonical_direct_pair(membership.id, target.id)
        except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc))
        existing = (await db.execute(select(WagleRoom).join(WagleDirectPair, WagleDirectPair.room_id == WagleRoom.id).where(WagleDirectPair.family_group_id == family_id, WagleDirectPair.membership_low_id == low, WagleDirectPair.membership_high_id == high, WagleDirectPair.is_active.is_(True)))).scalars().first()
        if existing: return existing, False
        try:
            room = WagleRoom(family_group_id=family_id, room_type="DIRECT", status="active", created_by_actor_type="ACCOUNT", created_by_account_id=account.id)
            db.add(room); await db.flush()
            db.add(WagleDirectPair(room_id=room.id, family_group_id=family_id, membership_low_id=low, membership_high_id=high, is_active=True))
            db.add_all([WagleParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=membership.id, room_role="room_admin", status="active", joined_sequence=0), WagleParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=target.id, room_role="member", status="active", joined_sequence=0)])
            await db.commit()
            return room, True
        except IntegrityError:
            await db.rollback()
            existing = (await db.execute(select(WagleRoom).join(WagleDirectPair, WagleDirectPair.room_id == WagleRoom.id).where(WagleDirectPair.family_group_id == family_id, WagleDirectPair.membership_low_id == low, WagleDirectPair.membership_high_id == high, WagleDirectPair.is_active.is_(True)))).scalars().one()
            return existing, False
    if data.room_type == "SERVICE": raise HTTPException(status_code=422, detail="SERVICE Room creation is not available in v1")
    ids = set(data.participant_membership_ids); ids.add(membership.id)
    targets = list((await db.execute(select(FamilyMembership).where(FamilyMembership.id.in_(ids), FamilyMembership.family_group_id == family_id, FamilyMembership.status == "active", FamilyMembership.deleted_at.is_(None)))).scalars())
    if len(targets) != len(ids): raise HTTPException(status_code=422, detail="모든 참여자는 활성 같은 가족 구성원이어야 합니다")
    # The reserved family-board sentinel is the only GROUP title a DB unique
    # invariant protects (migration 0021) -- ordinary GROUP rooms may still
    # legitimately share a display title, so only this branch needs the
    # find-or-create-under-race pattern the DIRECT branch above already uses.
    if data.title == FAMILY_BOARD_ROOM_TITLE:
        board_query = select(WagleRoom).where(WagleRoom.family_group_id == family_id, WagleRoom.room_type == "GROUP", WagleRoom.title == FAMILY_BOARD_ROOM_TITLE, WagleRoom.deleted_at.is_(None))
        existing = (await db.execute(board_query)).scalars().first()
        if existing: return existing, False
        try:
            room = WagleRoom(family_group_id=family_id, room_type="GROUP", title=data.title, status="active", created_by_actor_type="ACCOUNT", created_by_account_id=account.id); db.add(room); await db.flush()
            db.add_all([WagleParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=item.id, room_role="room_admin" if item.id == membership.id else "member", status="active", joined_sequence=0) for item in targets])
            await db.commit()
            return room, True
        except IntegrityError:
            await db.rollback()
            existing = (await db.execute(board_query)).scalars().one()
            return existing, False
    room = WagleRoom(family_group_id=family_id, room_type="GROUP", title=data.title, status="active", created_by_actor_type="ACCOUNT", created_by_account_id=account.id); db.add(room); await db.flush()
    db.add_all([WagleParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=item.id, room_role="room_admin" if item.id == membership.id else "member", status="active", joined_sequence=0) for item in targets])
    await db.commit()
    return room, True


async def list_messages(db, user, family_id, room_id, after_sequence, before_sequence, limit):
    if after_sequence is not None and before_sequence is not None: raise HTTPException(status_code=422, detail="after_sequence and before_sequence cannot be combined")
    _, membership = await context(db, user, family_id); await _require_permission(db, membership, READ); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    low, high = visible_range(participant.joined_sequence, participant.left_sequence, participant.status)
    stmt = select(WagleMessage).where(WagleMessage.room_id == room.id, WagleMessage.sequence >= low)
    if high is not None: stmt = stmt.where(WagleMessage.sequence <= high)
    if after_sequence is not None: stmt = stmt.where(WagleMessage.sequence > after_sequence).order_by(WagleMessage.sequence.asc()).limit(limit + 1)
    else:
        if before_sequence is not None: stmt = stmt.where(WagleMessage.sequence < before_sequence)
        stmt = stmt.order_by(WagleMessage.sequence.desc()).limit(limit + 1)
    items = list((await db.execute(stmt)).scalars()); more = len(items) > limit; items = items[:limit]
    if after_sequence is None: items.reverse()
    return items, {"oldest_sequence": items[0].sequence if items else None, "newest_sequence": items[-1].sequence if items else None, "has_more_before": more if after_sequence is None else False, "has_more_after": more if after_sequence is not None else False}


# Event contract this domain emits. The service identity itself is
# `SERVICE_CODE` above — there is exactly one, since migration 0007 moved the
# whole runtime (tables, permissions, service code, route prefix) to Wagle.
# A separate "target name" constant existed here only while the runtime still
# carried the historical name; keeping it now would be two names for one value.
MESSAGE_CREATED_EVENT_TYPE = "wagle.message.created"
MESSAGE_CREATED_EVENT_VERSION = 1
MESSAGE_AGGREGATE_TYPE = "wagle_message"


async def _enqueue_message_event(db: AsyncSession, message: WagleMessage, family_id: int, room_pk) -> None:
    """Append the delivery event for a newly persisted human message.

    Wave 2 only *records* the event durably. Consuming it — WebSocket
    broadcast, Web Push, presence — is Wave 3 and is deliberately absent here.

    `source_event_id` is the message's own UUID, which makes the enqueue
    idempotent for free: a retried send that resolves to an existing message
    never reaches this, and `enqueue_event` itself de-duplicates on
    (owner_service, source_event_id) if it somehow did.

    The envelope carries the identifiers a dispatcher needs without duplicating
    the message body's authority — the DB row stays the SSOT, and the payload
    is a delivery hint, never a second copy of the truth.
    """
    await outbox_service.enqueue_event(
        db,
        owner_service=SERVICE_CODE,
        event_type=MESSAGE_CREATED_EVENT_TYPE,
        event_version=MESSAGE_CREATED_EVENT_VERSION,
        aggregate_type=MESSAGE_AGGREGATE_TYPE,
        aggregate_id=str(message.id),
        source_event_id=str(message.id),
        family_id=family_id,
        payload={
            "family_group_id": family_id,
            "room_id": str(room_pk),
            "message_id": str(message.id),
            "sequence": message.sequence,
            "message_type": message.message_type,
            "sender_participant_id": str(message.sender_participant_id) if message.sender_participant_id else None,
            "occurred_at": message.created_at.isoformat() if message.created_at else None,
        },
    )


async def send_message(db, user, family_id, room_id, data):
    account, membership = await context(db, user, family_id); await _require_permission(db, membership, SEND); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    if participant.status != "active" or room.status != "active" or not await subscription_active(db, family_id): raise denied("Wagle subscription 또는 Room이 read-only입니다")
    # Capture plain scalar identifiers up front. Session.rollback() expires
    # every previously-loaded ORM object's attributes (expire_on_commit=False
    # only suppresses the equivalent behavior on commit) - touching room.id /
    # participant.id again after the rollback() below would trigger a
    # synchronous lazy-load outside any awaited context and crash with
    # MissingGreenlet under exactly the concurrent-collision case this
    # except branch exists to handle.
    room_pk = room.id
    participant_pk = participant.id
    existing = (await db.execute(select(WagleMessage).where(WagleMessage.room_id == room_pk, WagleMessage.sender_participant_id == participant_pk, WagleMessage.client_message_id == data.client_message_id))).scalars().first()
    if existing:
        if existing.body != data.body: raise HTTPException(status_code=409, detail="client_message_id payload conflict")
        return existing
    reply_to_message_id = None
    if data.reply_to_message_id is not None:
        # Same-room enforcement, same shape as every other cross-entity check
        # in this file: a client-supplied id must never be trusted to belong
        # to this Room without a server-side lookup, or a reply could quietly
        # forge a link to another Room's (even another Family's) Message.
        parent = (await db.execute(select(WagleMessage).where(WagleMessage.id == data.reply_to_message_id, WagleMessage.room_id == room_pk))).scalars().first()
        if parent is None:
            raise HTTPException(status_code=404, detail="답장 대상 Message를 찾을 수 없습니다")
        reply_to_message_id = parent.id
    try:
        sequence = (await db.execute(update(WagleRoom).where(WagleRoom.id == room_pk, WagleRoom.family_group_id == family_id).values(next_message_sequence=WagleRoom.next_message_sequence + 1).returning(WagleRoom.next_message_sequence))).scalar_one()
        message = WagleMessage(family_group_id=family_id, room_id=room_pk, sequence=sequence, sender_participant_id=participant_pk, message_type="TEXT", client_message_id=data.client_message_id, body=data.body, reply_to_message_id=reply_to_message_id)
        db.add(message); await db.flush()
        # [Intent] D6 durability: the message row, the room's sequence
        # advance, and the delivery event all commit together or not at all.
        # enqueue_event never commits, so the rollback below takes the Outbox
        # row with it and a caller can never observe a SENT message that has
        # no event to deliver (nor an event for a message that does not exist).
        await _enqueue_message_event(db, message, family_id, room_pk)
        await db.commit()
        return message
    except IntegrityError:
        await db.rollback()
        existing = (await db.execute(select(WagleMessage).where(WagleMessage.room_id == room_pk, WagleMessage.sender_participant_id == participant_pk, WagleMessage.client_message_id == data.client_message_id))).scalars().one()
        if existing.body != data.body: raise HTTPException(status_code=409, detail="client_message_id payload conflict")
        # The re-query happens after rollback; explicitly load scalar fields so
        # response serialization never lazy-loads an expired pre-rollback row.
        await db.refresh(existing)
        return existing


async def delete_message(db, user, family_id, room_id, message_id):
    account, membership = await context(db, user, family_id); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    message = (await db.execute(select(WagleMessage).where(WagleMessage.id == message_id, WagleMessage.room_id == room.id))).scalars().first()
    if message is None: raise HTTPException(status_code=404, detail="Message를 찾을 수 없습니다")
    if message.message_type != "TEXT": raise HTTPException(status_code=409, detail="Only TEXT messages can be deleted")
    if message.sender_participant_id != participant.id: raise denied("작성자만 삭제할 수 있습니다")
    if participant.status != "active" or not await subscription_active(db, family_id): raise denied("Wagle subscription 또는 participant가 read-only입니다")
    if message.deleted_at is None:
        message.deleted_at = datetime.now(timezone.utc); message.deleted_by_account_id = account.id; await db.commit()
    return message


async def reaction_counts_for(db: AsyncSession, message_ids: list, viewer_membership_id: int) -> dict:
    """Batch reaction count + the viewer's own reacted state, keyed by
    message id. W7.5 Phase D SLICE-WAGLE-BOARD-REACTIONS (3e)."""
    if not message_ids:
        return {}
    rows = (
        await db.execute(
            select(WagleMessageReaction.message_id, WagleMessageReaction.reactor_membership_id)
            .where(WagleMessageReaction.message_id.in_(message_ids))
        )
    ).all()
    counts: dict = {}
    mine: dict = {}
    for message_id, reactor_id in rows:
        counts[message_id] = counts.get(message_id, 0) + 1
        if reactor_id == viewer_membership_id:
            mine[message_id] = True
    return {mid: (counts.get(mid, 0), mine.get(mid, False)) for mid in message_ids}


async def react_to_message(db: AsyncSession, user: dict, family_id: int, room_id: UUID, message_id: UUID) -> tuple[int, bool]:
    """Toggle: reacting again removes the reaction. Matches a single heart
    icon with no reaction-type picker on the frozen 3c/3e Screens -- see
    the migration's own docstring for why this is not a multi-reaction
    taxonomy. Requires `SEND` (an active-interaction permission), the same
    boundary a comment (reply) already uses."""
    _, membership = await context(db, user, family_id)
    await _require_permission(db, membership, SEND)
    room = await _room(db, family_id, room_id)
    participant = await _participant(db, room, membership)
    if participant.status != "active" or not await subscription_active(db, family_id):
        raise denied("Wagle subscription 또는 Room이 read-only입니다")
    message = (await db.execute(select(WagleMessage).where(WagleMessage.id == message_id, WagleMessage.room_id == room.id, WagleMessage.deleted_at.is_(None)))).scalars().first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message를 찾을 수 없습니다")

    existing = (
        await db.execute(
            select(WagleMessageReaction).where(
                WagleMessageReaction.message_id == message_id,
                WagleMessageReaction.reactor_membership_id == membership.id,
            )
        )
    ).scalars().first()
    if existing is not None:
        await db.delete(existing)
        reacted = False
    else:
        db.add(WagleMessageReaction(message_id=message_id, family_group_id=family_id, reactor_membership_id=membership.id))
        reacted = True
    await db.commit()

    count = (
        await db.execute(select(func.count()).select_from(WagleMessageReaction).where(WagleMessageReaction.message_id == message_id))
    ).scalar_one()
    return count, reacted


_POPULAR_RANGE_DAYS = {"week": 7, "month": 30, "all": None}


async def list_popular_posts(db: AsyncSession, user: dict, family_id: int, time_range: str) -> list[dict]:
    """3e (인기 게시글) -- ranks the family board's top-level posts
    (REUSE-WAGLE-ROOMS-AS-BOARD's own sentinel-titled Room) by
    reaction_count + comment_count within the selected window. `time_range`
    is one of 'week'/'month'/'all', matching the Screen's own
    이번 주/이번 달/전체 labels exactly -- no ranking algorithm is invented
    beyond what those labels already imply."""
    _, membership = await context(db, user, family_id)
    await _require_permission(db, membership, READ)

    board_room = (
        await db.execute(
            select(WagleRoom).where(WagleRoom.family_group_id == family_id, WagleRoom.title == FAMILY_BOARD_ROOM_TITLE, WagleRoom.deleted_at.is_(None))
        )
    ).scalars().first()
    if board_room is None:
        return []
    await _participant(db, board_room, membership)  # 404s if the viewer never joined the board

    days = _POPULAR_RANGE_DAYS.get(time_range)
    since_clause = ""
    params = {"room_id": board_room.id}
    if days is not None:
        # `:days` is bound as an integer (asyncpg sends it typed, not as
        # text), so `(:days || ' days')::interval` fails at the DB level --
        # `||` has no integer/text overload. Multiplying by a literal
        # INTERVAL keeps `days` a genuine bound parameter (no string
        # formatting into the SQL) while staying valid for an int.
        since_clause = "AND m.created_at >= now() - (:days * INTERVAL '1 day')"
        params["days"] = days

    rows = (
        await db.execute(
            text(
                f"""
                SELECT m.id, m.body, m.created_at, m.sender_participant_id,
                       COALESCE(r.reaction_count, 0) AS reaction_count,
                       COALESCE(c.comment_count, 0) AS comment_count
                  FROM wagle_messages m
                  LEFT JOIN LATERAL (
                        SELECT count(*) AS reaction_count FROM wagle_message_reactions wr WHERE wr.message_id = m.id
                  ) r ON TRUE
                  LEFT JOIN LATERAL (
                        SELECT count(*) AS comment_count FROM wagle_messages cm WHERE cm.reply_to_message_id = m.id AND cm.deleted_at IS NULL
                  ) c ON TRUE
                 WHERE m.room_id = :room_id
                   AND m.reply_to_message_id IS NULL
                   AND m.deleted_at IS NULL
                   {since_clause}
                 ORDER BY (COALESCE(r.reaction_count, 0) + COALESCE(c.comment_count, 0)) DESC, m.created_at DESC
                 LIMIT 20
                """
            ),
            params,
        )
    ).all()

    results = []
    for message_id, body, created_at, sender_participant_id, reaction_count, comment_count in rows:
        author = await participant_display_name_by_participant_id(db, sender_participant_id) if sender_participant_id else "가족"
        results.append({
            "message_id": message_id, "body": body, "author_display_name": author,
            "created_at": created_at, "reaction_count": reaction_count, "comment_count": comment_count,
        })
    return results


async def participant_display_name_by_participant_id(db: AsyncSession, participant_id) -> str:
    participant = await db.get(WagleParticipant, participant_id)
    if participant is None:
        return "가족"
    return await participant_display_name(db, participant.family_membership_id)


async def search_visible_messages(db: AsyncSession, actor_membership_id: int, family_id: int, query: str) -> list:
    """Read-only, for `family_search`'s own Slice (3j) -- moved here from
    that domain's own service so it reaches these tables through this
    module's dotted reference rather than raw-SQL-querying them directly,
    per the Backend Guide's no-direct-cross-domain-DB-access rule. Only
    rooms the actor participates in, only the actor's own visible sequence
    range within each -- same rule `list_rooms_with_preview`/
    `list_messages` already use."""
    rows = (
        await db.execute(
            text(
                """
                SELECT m.body, m.created_at
                  FROM wagle_messages m
                  JOIN wagle_participants p
                    ON p.room_id = m.room_id
                   AND p.family_membership_id = :actor_id
                   AND p.status IN ('active', 'left')
                 WHERE m.family_group_id = :family_id
                   AND m.deleted_at IS NULL
                   AND m.body ILIKE :pattern
                   AND m.sequence >= p.joined_sequence
                   AND (p.left_sequence IS NULL OR m.sequence <= p.left_sequence)
                 ORDER BY m.created_at DESC
                """
            ),
            {"actor_id": actor_membership_id, "family_id": family_id, "pattern": f"%{query}%"},
        )
    ).all()
    return list(rows)


async def read_state(db, user, family_id, room_id, requested: int | None = None):
    _, membership = await context(db, user, family_id); await _require_permission(db, membership, READ); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    low, high = visible_range(participant.joined_sequence, participant.left_sequence, participant.status)
    maximum = room.next_message_sequence if high is None else high
    if requested is not None:
        if requested > maximum or requested < low:
            raise HTTPException(status_code=422, detail="read sequence is outside visible range")
        # A plain get-then-write here races under concurrent PUTs: two
        # requests can both observe the pre-update value and the later
        # commit silently regresses last_read_sequence, and a concurrent
        # first-write for the same participant can double-INSERT and raise
        # an uncaught IntegrityError. A single atomic upsert with GREATEST
        # closes both races in one round trip.
        upsert = pg_insert(WagleParticipantReadState).values(
            participant_id=participant.id, last_read_sequence=requested
        )
        upsert = upsert.on_conflict_do_update(
            index_elements=[WagleParticipantReadState.participant_id],
            set_={
                "last_read_sequence": func.greatest(
                    WagleParticipantReadState.last_read_sequence, upsert.excluded.last_read_sequence
                ),
                "updated_at": func.now(),
            },
        )
        await db.execute(upsert)
        await db.commit()
    state = await db.get(WagleParticipantReadState, participant.id)
    if state is None:
        state = WagleParticipantReadState(participant_id=participant.id, last_read_sequence=0); db.add(state); await db.commit()
    # db.get() can return an identity-mapped instance with a server-onupdate
    # column (updated_at) left expired from the write above; refresh here so
    # the router's response serialization never triggers an un-awaited lazy
    # load outside the session's async context.
    await db.refresh(state)
    unread = (await db.execute(select(func.count(WagleMessage.id)).where(WagleMessage.room_id == room.id, WagleMessage.sequence >= low, WagleMessage.sequence <= maximum, WagleMessage.sequence > state.last_read_sequence, WagleMessage.sender_participant_id != participant.id))).scalar_one()
    return participant, state, unread


async def add_participant(db, user, family_id, room_id, membership_id, room_role):
    _, actor_membership = await context(db, user, family_id); await _require_permission(db, actor_membership, MANAGE_PARTICIPANTS)
    room = await _room(db, family_id, room_id); actor = await _participant(db, room, actor_membership)
    if actor.status != "active" or actor.room_role != "room_admin": raise denied("Room admin 권한이 필요합니다")
    if room.room_type == "DIRECT" or not await subscription_active(db, family_id): raise denied("DIRECT 또는 read-only Room에서는 참여자를 관리할 수 없습니다")
    target = await db.get(FamilyMembership, membership_id)
    if target is None or target.family_group_id != family_id or target.status != "active" or target.deleted_at is not None: raise HTTPException(status_code=422, detail="활성 같은 가족 구성원이 필요합니다")
    active_count = (await db.execute(select(func.count(WagleParticipant.id)).where(WagleParticipant.room_id == room.id, WagleParticipant.status == "active"))).scalar_one()
    if active_count >= 50: raise HTTPException(status_code=422, detail="GROUP active participant limit is 50")
    item = WagleParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=target.id, room_role=room_role, status="active", joined_sequence=room.next_message_sequence + 1); db.add(item); await db.flush(); await db.commit()
    return item


async def update_room(db, user, family_id, room_id, title, room_status):
    _, membership = await context(db, user, family_id); await _require_permission(db, membership, MANAGE_ROOM)
    room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    if participant.status != "active" or participant.room_role != "room_admin" or not await subscription_active(db, family_id): raise denied("Room admin 및 active subscription 권한이 필요합니다")
    if title is not None: room.title = title
    if room_status is not None:
        room.status = room_status
        if room_status == "closed": room.closed_at = datetime.now(timezone.utc)
    await db.commit()
    return room


async def remove_participant(db, user, family_id, room_id, participant_id, voluntary=False):
    _, actor_membership = await context(db, user, family_id); room = await _room(db, family_id, room_id); actor = await _participant(db, room, actor_membership)
    target = await db.get(WagleParticipant, participant_id)
    if target is None or target.room_id != room.id: raise HTTPException(status_code=404, detail="Participant를 찾을 수 없습니다")
    if room.room_type == "DIRECT": raise HTTPException(status_code=409, detail="DIRECT leave is not supported in v1")
    if voluntary:
        if target.id != actor.id: raise denied()
    else:
        await _require_permission(db, actor_membership, MANAGE_PARTICIPANTS)
        if actor.room_role != "room_admin": raise denied("Room admin 권한이 필요합니다")
    if target.status == "active":
        target.status = "left" if voluntary else "removed"; target.left_sequence = room.next_message_sequence; target.left_at = datetime.now(timezone.utc)
        if not voluntary: target.removed_at = target.left_at
        await db.commit()
    return target


# --- R2-B1: Service Principal, Service-Room Binding, SERVICE_ACTION publish -----
# A Service Principal is not an Account: it never gets a Family Role or
# room_admin, and this module's own admin helpers are the only issuance path
# (no HTTP surface) - see service_actor.py and WAGLE_SECURITY_AND_AUTHORIZATION.md.

async def _audit(db, event_type, service_principal_id, family_group_id, room_id, result_code, detail=None):
    db.add(WagleServiceAuditLog(
        event_type=event_type, service_principal_id=service_principal_id,
        family_group_id=family_group_id, room_id=room_id, result_code=result_code, detail=detail,
    ))


async def create_service_principal(db: AsyncSession, service_code: str, display_name: str) -> tuple[ServicePrincipal, str]:
    credential_id, secret, credential_hash = issue_credential()
    principal = ServicePrincipal(service_code=service_code, display_name=display_name, credential_id=credential_id, credential_hash=credential_hash, status="active")
    db.add(principal)
    await db.flush()
    await _audit(db, "principal_created", principal.id, None, None, "success")
    await db.commit()
    await db.refresh(principal)
    return principal, secret


async def revoke_service_principal(db: AsyncSession, principal_id: int) -> ServicePrincipal:
    principal = await db.get(ServicePrincipal, principal_id)
    if principal is None: raise HTTPException(status_code=404, detail="Service Principal을 찾을 수 없습니다")
    if principal.status != "revoked":
        principal.status = "revoked"; principal.revoked_at = datetime.now(timezone.utc)
        await _audit(db, "principal_revoked", principal.id, None, None, "success")
        await db.commit(); await db.refresh(principal)
    return principal


async def create_service_binding(db: AsyncSession, service_principal_id: int, family_id: int, allowed_actions: list[dict]) -> tuple[WagleServiceBinding, WagleRoom]:
    """Creates the SERVICE Room and its Binding atomically. A SERVICE Room has
    no other creation path - it always exists because a Binding exists."""
    principal = await db.get(ServicePrincipal, service_principal_id)
    if principal is None or principal.status != "active":
        raise HTTPException(status_code=422, detail="활성 Service Principal이 필요합니다")
    family = await db.get(FamilyGroup, family_id)
    if family is None or family.status != "active" or family.deleted_at is not None:
        raise HTTPException(status_code=422, detail="활성 Family가 필요합니다")
    room = WagleRoom(family_group_id=family_id, room_type="SERVICE", status="active", created_by_actor_type="SERVICE", created_by_account_id=None)
    db.add(room)
    await db.flush()
    binding = WagleServiceBinding(service_principal_id=service_principal_id, family_group_id=family_id, room_id=room.id, allowed_actions=allowed_actions, status="active")
    db.add(binding)
    await db.flush()
    await _audit(db, "binding_created", service_principal_id, family_id, room.id, "success")
    await db.commit()
    await db.refresh(binding); await db.refresh(room)
    return binding, room


async def set_service_binding_status(db: AsyncSession, binding_id: int, new_status: str) -> WagleServiceBinding:
    if new_status not in ("active", "inactive"): raise HTTPException(status_code=422, detail="유효하지 않은 상태입니다")
    binding = await db.get(WagleServiceBinding, binding_id)
    if binding is None: raise HTTPException(status_code=404, detail="Binding을 찾을 수 없습니다")
    if binding.status != new_status:
        binding.status = new_status
        await _audit(db, "binding_activated" if new_status == "active" else "binding_deactivated", binding.service_principal_id, binding.family_group_id, binding.room_id, "success")
        await db.commit(); await db.refresh(binding)
    return binding


async def bootstrap_service_principal(db: AsyncSession, service_code: str, display_name: str) -> ServicePrincipal:
    """Idempotent get-or-create for an internal, code-only Service Principal
    such as the in-process Outbox Worker's own identity. No plaintext secret
    is minted on the get path: an in-process caller (the Worker) authenticates
    by holding this trusted ORM row directly, never a Bearer credential - see
    app/workers/service_outbox.py."""
    principal = (
        await db.execute(
            select(ServicePrincipal).where(
                ServicePrincipal.service_code == service_code, ServicePrincipal.status == "active"
            )
        )
    ).scalars().first()
    if principal is not None:
        return principal
    principal, _secret = await create_service_principal(db, service_code, display_name)
    return principal


async def ensure_canonical_service_binding(
    db: AsyncSession, principal: ServicePrincipal, family_id: int, allowed_actions: list[dict]
) -> WagleServiceBinding:
    """Idempotent get-or-create of the one canonical SERVICE Room+Binding for
    (principal, family) - never one Room per event. Safe under concurrent
    Workers: a creation race is resolved by the
    uq_wagle_service_binding_principal_family constraint the same way
    publish_service_action resolves a concurrent message race."""
    existing = (
        await db.execute(
            select(WagleServiceBinding).where(
                WagleServiceBinding.service_principal_id == principal.id,
                WagleServiceBinding.family_group_id == family_id,
            )
        )
    ).scalars().first()
    if existing is not None:
        return existing
    try:
        binding, _room = await create_service_binding(db, principal.id, family_id, allowed_actions)
        return binding
    except IntegrityError:
        await db.rollback()
        return (
            await db.execute(
                select(WagleServiceBinding).where(
                    WagleServiceBinding.service_principal_id == principal.id,
                    WagleServiceBinding.family_group_id == family_id,
                )
            )
        ).scalars().one()


async def onboard_self_into_service_room(db: AsyncSession, user: dict, family_id: int, service_code: str) -> tuple[WagleRoom, WagleParticipant]:
    """Self-onboarding only: the calling user is added as a Participant in
    their own Family's canonical SERVICE Room for `service_code`, if (and
    only if) that Binding already exists and is active. This never creates a
    Binding, never adds any other Family member, and never auto-enrolls every
    Family - a user must actually call this (e.g. opening the service's
    screen or a future Dock) before they see anything in that Room."""
    _, membership = await context(db, user, family_id)
    await _require_permission(db, membership, READ)
    if not await subscription_active(db, family_id):
        raise denied("Wagle subscription이 필요합니다")

    binding = (
        await db.execute(
            select(WagleServiceBinding).where(
                WagleServiceBinding.family_group_id == family_id,
            ).join(ServicePrincipal, ServicePrincipal.id == WagleServiceBinding.service_principal_id).where(
                ServicePrincipal.service_code == service_code,
            )
        )
    ).scalars().first()
    if binding is None or binding.status != "active":
        raise HTTPException(status_code=404, detail="이 서비스는 아직 이 가족에 연결되지 않았습니다")

    room = await _room(db, family_id, binding.room_id)
    if room.room_type != "SERVICE" or room.status != "active":
        raise HTTPException(status_code=404, detail="이 서비스는 아직 이 가족에 연결되지 않았습니다")

    existing = (
        await db.execute(
            select(WagleParticipant).where(
                WagleParticipant.room_id == room.id,
                WagleParticipant.family_membership_id == membership.id,
                WagleParticipant.status == "active",
            )
        )
    ).scalars().first()
    if existing is not None:
        return room, existing
    try:
        # Unlike a GROUP Room (where hiding pre-join history is the intended
        # social boundary - see add_participant), a SERVICE Room is a
        # broadcast log for the whole Family: onboarding late must not hide
        # events that already happened, so visibility starts from sequence 0.
        participant = WagleParticipant(
            family_group_id=family_id, room_id=room.id, family_membership_id=membership.id,
            room_role="member", status="active", joined_sequence=0,
        )
        db.add(participant)
        await db.flush()
        await db.commit()
        return room, participant
    except IntegrityError:
        await db.rollback()
        existing = (
            await db.execute(
                select(WagleParticipant).where(
                    WagleParticipant.room_id == room.id,
                    WagleParticipant.family_membership_id == membership.id,
                    WagleParticipant.status == "active",
                )
            )
        ).scalars().one()
        return room, existing


def _same_service_event(existing: WagleMessage, room_pk, schema_version: int, action_type: str, snapshot: dict) -> bool:
    payload = existing.service_payload or {}
    return (
        existing.room_id == room_pk
        and existing.service_payload_version == schema_version
        and payload.get("action_type") == action_type
        and payload.get("snapshot") == snapshot
    )


async def resolve_binding_room_id(db: AsyncSession, binding_id: int, family_id: int):
    """The Room a Service Binding authorizes, for the given family.

    -- [Query] Lets an outside caller name a *binding* — the actual unit of
    -- publish authority — instead of carrying a raw room id it would have no
    -- way to have been authorized for. Returns None when the binding does not
    -- exist, is inactive, or belongs to another family; the caller turns that
    -- into its own domain error, and `publish_service_action()` re-checks the
    -- binding regardless, so this is a convenience, not the security boundary.
    """
    stmt = select(WagleServiceBinding.room_id).where(
        WagleServiceBinding.id == binding_id,
        WagleServiceBinding.family_group_id == family_id,
        WagleServiceBinding.status == "active",
    )
    return (await db.execute(stmt)).scalars().first()


async def find_service_message_id(
    db: AsyncSession, principal_id: int, source: str, source_event_id: str
):
    """Whether a given source event has already been published by a Principal.

    -- [Query] Reads the same three columns as the partial unique index that
    -- enforces service-event idempotency, so a caller can report "this was a
    -- duplicate" without owning Wagle's tables. The guarantee is the index;
    -- this is only how an outside caller observes it.
    """
    stmt = select(WagleMessage.id).where(
        WagleMessage.service_principal_id == principal_id,
        WagleMessage.source == source,
        WagleMessage.source_event_id == source_event_id,
    )
    return (await db.execute(stmt)).scalars().first()


async def publish_service_action(db: AsyncSession, principal: ServicePrincipal, family_id: int, data) -> WagleMessage:
    # Capture plain scalars up front - see send_message()'s comment on why
    # touching an ORM object's attributes after db.rollback() is unsafe.
    principal_id = principal.id
    room_id = data.room_id

    binding = (await db.execute(select(WagleServiceBinding).where(
        WagleServiceBinding.service_principal_id == principal_id,
        WagleServiceBinding.room_id == room_id,
        WagleServiceBinding.family_group_id == family_id,
    ))).scalars().first()
    if binding is None or binding.status != "active":
        await _audit(db, "permission_denied", principal_id, family_id, room_id, "denied", "binding_not_found_or_inactive")
        await db.commit()
        raise HTTPException(status_code=404, detail="발행 대상을 찾을 수 없습니다")

    room = (await db.execute(select(WagleRoom).where(
        WagleRoom.id == room_id, WagleRoom.family_group_id == family_id, WagleRoom.deleted_at.is_(None),
    ))).scalars().first()
    if room is None or room.room_type != "SERVICE" or room.status != "active":
        await _audit(db, "permission_denied", principal_id, family_id, room_id, "denied", "room_not_service_or_inactive")
        await db.commit()
        raise HTTPException(status_code=404, detail="발행 대상을 찾을 수 없습니다")

    if not await subscription_active(db, family_id):
        await _audit(db, "permission_denied", principal_id, family_id, room_id, "denied", "subscription_inactive")
        await db.commit()
        raise HTTPException(status_code=404, detail="발행 대상을 찾을 수 없습니다")

    allowed = any(
        a.get("action_type") == data.action_type and int(a.get("schema_version", -1)) == data.schema_version
        for a in (binding.allowed_actions or [])
    )
    if not allowed:
        await _audit(db, "schema_denied", principal_id, family_id, room_id, "denied", "action_schema_not_allowed")
        await db.commit()
        raise HTTPException(status_code=422, detail="허용되지 않은 action schema입니다")

    room_pk = room.id
    existing = (await db.execute(select(WagleMessage).where(
        WagleMessage.service_principal_id == principal_id,
        WagleMessage.source == data.source,
        WagleMessage.source_event_id == data.source_event_id,
    ))).scalars().first()
    if existing:
        if not _same_service_event(existing, room_pk, data.schema_version, data.action_type, data.snapshot):
            await _audit(db, "permission_denied", principal_id, family_id, room_pk, "conflict", "source_event_id_payload_conflict")
            await db.commit()
            raise HTTPException(status_code=409, detail="source_event_id payload conflict")
        await _audit(db, "replay_detected", principal_id, family_id, room_pk, "idempotent")
        await db.commit()
        return existing

    try:
        sequence = (await db.execute(update(WagleRoom).where(WagleRoom.id == room_pk, WagleRoom.family_group_id == family_id).values(next_message_sequence=WagleRoom.next_message_sequence + 1).returning(WagleRoom.next_message_sequence))).scalar_one()
        message = WagleMessage(
            family_group_id=family_id, room_id=room_pk, sequence=sequence,
            sender_participant_id=None, message_type="SERVICE_ACTION",
            service_code=principal.service_code, service_payload_version=data.schema_version,
            service_payload={"action_type": data.action_type, "snapshot": data.snapshot},
            service_principal_id=principal_id, source=data.source, source_event_id=data.source_event_id,
        )
        db.add(message)
        await db.flush()
        await _audit(db, "publish_success", principal_id, family_id, room_pk, "success")
        await db.commit()
        return message
    except IntegrityError:
        await db.rollback()
        existing = (await db.execute(select(WagleMessage).where(
            WagleMessage.service_principal_id == principal_id,
            WagleMessage.source == data.source,
            WagleMessage.source_event_id == data.source_event_id,
        ))).scalars().one()
        if not _same_service_event(existing, room_pk, data.schema_version, data.action_type, data.snapshot):
            await _audit(db, "permission_denied", principal_id, family_id, room_pk, "conflict", "source_event_id_payload_conflict")
            await db.commit()
            raise HTTPException(status_code=409, detail="source_event_id payload conflict")
        await db.refresh(existing)
        await _audit(db, "replay_detected", principal_id, family_id, room_pk, "idempotent")
        await db.commit()
        return existing
