"""Doran use cases. Each mutating public function owns one transaction."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family import service as family_service
from app.domains.family.models import FamilyGroup, FamilyMembership, MembershipRoleAssignment, Permission, Role, RolePermission, ServiceSubscription
from app.domains.doran.models import DoranDirectPair, DoranMessage, DoranParticipant, DoranParticipantReadState, DoranRoom, DoranServiceAuditLog, DoranServiceBinding, ServicePrincipal
from app.domains.doran.rules import canonical_direct_pair, visible_range
from app.domains.doran.service_actor import issue_credential

SERVICE_CODE = "doran"
READ = "doran.messages.read"; SEND = "doran.messages.send"; CREATE = "doran.rooms.create"; MANAGE_ROOM = "doran.rooms.manage"; MANAGE_PARTICIPANTS = "doran.participants.manage"


def denied(detail: str = "Doran 권한이 없습니다") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def context(db: AsyncSession, user: dict, family_id: int):
    account = await family_service.resolve_current_account(db, user)
    membership = await family_service.get_active_membership(db, account.id, family_id)
    return account, membership


async def subscription_active(db: AsyncSession, family_id: int) -> bool:
    return (await db.execute(select(ServiceSubscription.id).where(ServiceSubscription.family_group_id == family_id, ServiceSubscription.service_code == SERVICE_CODE, ServiceSubscription.status == "active"))).scalar_one_or_none() is not None


async def _room(db: AsyncSession, family_id: int, room_id: UUID) -> DoranRoom:
    room = (await db.execute(select(DoranRoom).where(DoranRoom.id == room_id, DoranRoom.family_group_id == family_id, DoranRoom.deleted_at.is_(None)))).scalars().first()
    if room is None: raise HTTPException(status_code=404, detail="Room을 찾을 수 없습니다")
    return room


async def _participant(db: AsyncSession, room: DoranRoom, membership: FamilyMembership) -> DoranParticipant:
    participant = (await db.execute(select(DoranParticipant).where(DoranParticipant.room_id == room.id, DoranParticipant.family_membership_id == membership.id).order_by(DoranParticipant.created_at.desc()))).scalars().first()
    if participant is None or participant.status == "removed": raise denied("Room 참여자 권한이 필요합니다")
    return participant


async def _require_permission(db: AsyncSession, membership: FamilyMembership, code: str) -> None:
    # A participant is still the resource boundary; permission is an additional capability gate.
    # Retained read access deliberately does not disappear merely because the
    # Doran subscription became suspended/cancelled.
    if code == READ:
        retained = (await db.execute(select(Permission.id).join(RolePermission, RolePermission.permission_id == Permission.id).join(Role, Role.id == RolePermission.role_id).join(MembershipRoleAssignment, MembershipRoleAssignment.role_id == Role.id).where(MembershipRoleAssignment.membership_id == membership.id, MembershipRoleAssignment.revoked_at.is_(None), Role.is_active.is_(True), Permission.code == READ))).scalar_one_or_none()
        if retained is not None:
            return
    if code not in await family_service.effective_permissions(db, membership): raise denied()


async def list_rooms(db, user, family_id):
    _, membership = await context(db, user, family_id)
    await _require_permission(db, membership, READ)
    rows = await db.execute(select(DoranRoom).join(DoranParticipant, DoranParticipant.room_id == DoranRoom.id).where(DoranRoom.family_group_id == family_id, DoranRoom.deleted_at.is_(None), DoranParticipant.family_membership_id == membership.id, DoranParticipant.status.in_(("active", "left"))).order_by(DoranRoom.updated_at.desc()))
    return list(rows.scalars())


async def create_room(db: AsyncSession, user: dict, family_id: int, data):
    account, membership = await context(db, user, family_id)
    await _require_permission(db, membership, CREATE)
    if not await subscription_active(db, family_id): raise denied("Doran subscription is read-only")
    if data.room_type == "DIRECT":
        target = await db.get(FamilyMembership, data.target_membership_id)
        if target is None or target.family_group_id != family_id or target.status != "active" or target.deleted_at is not None: raise HTTPException(status_code=422, detail="활성 같은 가족 구성원이 필요합니다")
        try: low, high = canonical_direct_pair(membership.id, target.id)
        except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc))
        existing = (await db.execute(select(DoranRoom).join(DoranDirectPair, DoranDirectPair.room_id == DoranRoom.id).where(DoranDirectPair.family_group_id == family_id, DoranDirectPair.membership_low_id == low, DoranDirectPair.membership_high_id == high, DoranDirectPair.is_active.is_(True)))).scalars().first()
        if existing: return existing, False
        try:
            room = DoranRoom(family_group_id=family_id, room_type="DIRECT", status="active", created_by_actor_type="ACCOUNT", created_by_account_id=account.id)
            db.add(room); await db.flush()
            db.add(DoranDirectPair(room_id=room.id, family_group_id=family_id, membership_low_id=low, membership_high_id=high, is_active=True))
            db.add_all([DoranParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=membership.id, room_role="room_admin", status="active", joined_sequence=0), DoranParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=target.id, room_role="member", status="active", joined_sequence=0)])
            await db.commit()
            return room, True
        except IntegrityError:
            await db.rollback()
            existing = (await db.execute(select(DoranRoom).join(DoranDirectPair, DoranDirectPair.room_id == DoranRoom.id).where(DoranDirectPair.family_group_id == family_id, DoranDirectPair.membership_low_id == low, DoranDirectPair.membership_high_id == high, DoranDirectPair.is_active.is_(True)))).scalars().one()
            return existing, False
    if data.room_type == "SERVICE": raise HTTPException(status_code=422, detail="SERVICE Room creation is not available in v1")
    ids = set(data.participant_membership_ids); ids.add(membership.id)
    targets = list((await db.execute(select(FamilyMembership).where(FamilyMembership.id.in_(ids), FamilyMembership.family_group_id == family_id, FamilyMembership.status == "active", FamilyMembership.deleted_at.is_(None)))).scalars())
    if len(targets) != len(ids): raise HTTPException(status_code=422, detail="모든 참여자는 활성 같은 가족 구성원이어야 합니다")
    room = DoranRoom(family_group_id=family_id, room_type="GROUP", title=data.title, status="active", created_by_actor_type="ACCOUNT", created_by_account_id=account.id); db.add(room); await db.flush()
    db.add_all([DoranParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=item.id, room_role="room_admin" if item.id == membership.id else "member", status="active", joined_sequence=0) for item in targets])
    await db.commit()
    return room, True


async def list_messages(db, user, family_id, room_id, after_sequence, before_sequence, limit):
    if after_sequence is not None and before_sequence is not None: raise HTTPException(status_code=422, detail="after_sequence and before_sequence cannot be combined")
    _, membership = await context(db, user, family_id); await _require_permission(db, membership, READ); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    low, high = visible_range(participant.joined_sequence, participant.left_sequence, participant.status)
    stmt = select(DoranMessage).where(DoranMessage.room_id == room.id, DoranMessage.sequence >= low)
    if high is not None: stmt = stmt.where(DoranMessage.sequence <= high)
    if after_sequence is not None: stmt = stmt.where(DoranMessage.sequence > after_sequence).order_by(DoranMessage.sequence.asc()).limit(limit + 1)
    else:
        if before_sequence is not None: stmt = stmt.where(DoranMessage.sequence < before_sequence)
        stmt = stmt.order_by(DoranMessage.sequence.desc()).limit(limit + 1)
    items = list((await db.execute(stmt)).scalars()); more = len(items) > limit; items = items[:limit]
    if after_sequence is None: items.reverse()
    return items, {"oldest_sequence": items[0].sequence if items else None, "newest_sequence": items[-1].sequence if items else None, "has_more_before": more if after_sequence is None else False, "has_more_after": more if after_sequence is not None else False}


async def send_message(db, user, family_id, room_id, data):
    account, membership = await context(db, user, family_id); await _require_permission(db, membership, SEND); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    if participant.status != "active" or room.status != "active" or not await subscription_active(db, family_id): raise denied("Doran subscription 또는 Room이 read-only입니다")
    # Capture plain scalar identifiers up front. Session.rollback() expires
    # every previously-loaded ORM object's attributes (expire_on_commit=False
    # only suppresses the equivalent behavior on commit) - touching room.id /
    # participant.id again after the rollback() below would trigger a
    # synchronous lazy-load outside any awaited context and crash with
    # MissingGreenlet under exactly the concurrent-collision case this
    # except branch exists to handle.
    room_pk = room.id
    participant_pk = participant.id
    existing = (await db.execute(select(DoranMessage).where(DoranMessage.room_id == room_pk, DoranMessage.sender_participant_id == participant_pk, DoranMessage.client_message_id == data.client_message_id))).scalars().first()
    if existing:
        if existing.body != data.body: raise HTTPException(status_code=409, detail="client_message_id payload conflict")
        return existing
    try:
        sequence = (await db.execute(update(DoranRoom).where(DoranRoom.id == room_pk, DoranRoom.family_group_id == family_id).values(next_message_sequence=DoranRoom.next_message_sequence + 1).returning(DoranRoom.next_message_sequence))).scalar_one()
        message = DoranMessage(family_group_id=family_id, room_id=room_pk, sequence=sequence, sender_participant_id=participant_pk, message_type="TEXT", client_message_id=data.client_message_id, body=data.body)
        db.add(message); await db.flush(); await db.commit()
        return message
    except IntegrityError:
        await db.rollback()
        existing = (await db.execute(select(DoranMessage).where(DoranMessage.room_id == room_pk, DoranMessage.sender_participant_id == participant_pk, DoranMessage.client_message_id == data.client_message_id))).scalars().one()
        if existing.body != data.body: raise HTTPException(status_code=409, detail="client_message_id payload conflict")
        # The re-query happens after rollback; explicitly load scalar fields so
        # response serialization never lazy-loads an expired pre-rollback row.
        await db.refresh(existing)
        return existing


async def delete_message(db, user, family_id, room_id, message_id):
    account, membership = await context(db, user, family_id); room = await _room(db, family_id, room_id); participant = await _participant(db, room, membership)
    message = (await db.execute(select(DoranMessage).where(DoranMessage.id == message_id, DoranMessage.room_id == room.id))).scalars().first()
    if message is None: raise HTTPException(status_code=404, detail="Message를 찾을 수 없습니다")
    if message.message_type != "TEXT": raise HTTPException(status_code=409, detail="Only TEXT messages can be deleted")
    if message.sender_participant_id != participant.id: raise denied("작성자만 삭제할 수 있습니다")
    if participant.status != "active" or not await subscription_active(db, family_id): raise denied("Doran subscription 또는 participant가 read-only입니다")
    if message.deleted_at is None:
        message.deleted_at = datetime.now(timezone.utc); message.deleted_by_account_id = account.id; await db.commit()
    return message


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
        upsert = pg_insert(DoranParticipantReadState).values(
            participant_id=participant.id, last_read_sequence=requested
        )
        upsert = upsert.on_conflict_do_update(
            index_elements=[DoranParticipantReadState.participant_id],
            set_={
                "last_read_sequence": func.greatest(
                    DoranParticipantReadState.last_read_sequence, upsert.excluded.last_read_sequence
                ),
                "updated_at": func.now(),
            },
        )
        await db.execute(upsert)
        await db.commit()
    state = await db.get(DoranParticipantReadState, participant.id)
    if state is None:
        state = DoranParticipantReadState(participant_id=participant.id, last_read_sequence=0); db.add(state); await db.commit()
    # db.get() can return an identity-mapped instance with a server-onupdate
    # column (updated_at) left expired from the write above; refresh here so
    # the router's response serialization never triggers an un-awaited lazy
    # load outside the session's async context.
    await db.refresh(state)
    unread = (await db.execute(select(func.count(DoranMessage.id)).where(DoranMessage.room_id == room.id, DoranMessage.sequence >= low, DoranMessage.sequence <= maximum, DoranMessage.sequence > state.last_read_sequence, DoranMessage.sender_participant_id != participant.id))).scalar_one()
    return participant, state, unread


async def add_participant(db, user, family_id, room_id, membership_id, room_role):
    _, actor_membership = await context(db, user, family_id); await _require_permission(db, actor_membership, MANAGE_PARTICIPANTS)
    room = await _room(db, family_id, room_id); actor = await _participant(db, room, actor_membership)
    if actor.status != "active" or actor.room_role != "room_admin": raise denied("Room admin 권한이 필요합니다")
    if room.room_type == "DIRECT" or not await subscription_active(db, family_id): raise denied("DIRECT 또는 read-only Room에서는 참여자를 관리할 수 없습니다")
    target = await db.get(FamilyMembership, membership_id)
    if target is None or target.family_group_id != family_id or target.status != "active" or target.deleted_at is not None: raise HTTPException(status_code=422, detail="활성 같은 가족 구성원이 필요합니다")
    active_count = (await db.execute(select(func.count(DoranParticipant.id)).where(DoranParticipant.room_id == room.id, DoranParticipant.status == "active"))).scalar_one()
    if active_count >= 50: raise HTTPException(status_code=422, detail="GROUP active participant limit is 50")
    item = DoranParticipant(family_group_id=family_id, room_id=room.id, family_membership_id=target.id, room_role=room_role, status="active", joined_sequence=room.next_message_sequence + 1); db.add(item); await db.flush(); await db.commit()
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
    target = await db.get(DoranParticipant, participant_id)
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
# (no HTTP surface) - see service_actor.py and DORAN_SECURITY_AND_AUTHORIZATION.md.

async def _audit(db, event_type, service_principal_id, family_group_id, room_id, result_code, detail=None):
    db.add(DoranServiceAuditLog(
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


async def create_service_binding(db: AsyncSession, service_principal_id: int, family_id: int, allowed_actions: list[dict]) -> tuple[DoranServiceBinding, DoranRoom]:
    """Creates the SERVICE Room and its Binding atomically. A SERVICE Room has
    no other creation path - it always exists because a Binding exists."""
    principal = await db.get(ServicePrincipal, service_principal_id)
    if principal is None or principal.status != "active":
        raise HTTPException(status_code=422, detail="활성 Service Principal이 필요합니다")
    family = await db.get(FamilyGroup, family_id)
    if family is None or family.status != "active" or family.deleted_at is not None:
        raise HTTPException(status_code=422, detail="활성 Family가 필요합니다")
    room = DoranRoom(family_group_id=family_id, room_type="SERVICE", status="active", created_by_actor_type="SERVICE", created_by_account_id=None)
    db.add(room)
    await db.flush()
    binding = DoranServiceBinding(service_principal_id=service_principal_id, family_group_id=family_id, room_id=room.id, allowed_actions=allowed_actions, status="active")
    db.add(binding)
    await db.flush()
    await _audit(db, "binding_created", service_principal_id, family_id, room.id, "success")
    await db.commit()
    await db.refresh(binding); await db.refresh(room)
    return binding, room


async def set_service_binding_status(db: AsyncSession, binding_id: int, new_status: str) -> DoranServiceBinding:
    if new_status not in ("active", "inactive"): raise HTTPException(status_code=422, detail="유효하지 않은 상태입니다")
    binding = await db.get(DoranServiceBinding, binding_id)
    if binding is None: raise HTTPException(status_code=404, detail="Binding을 찾을 수 없습니다")
    if binding.status != new_status:
        binding.status = new_status
        await _audit(db, "binding_activated" if new_status == "active" else "binding_deactivated", binding.service_principal_id, binding.family_group_id, binding.room_id, "success")
        await db.commit(); await db.refresh(binding)
    return binding


def _same_service_event(existing: DoranMessage, room_pk, schema_version: int, action_type: str, snapshot: dict) -> bool:
    payload = existing.service_payload or {}
    return (
        existing.room_id == room_pk
        and existing.service_payload_version == schema_version
        and payload.get("action_type") == action_type
        and payload.get("snapshot") == snapshot
    )


async def publish_service_action(db: AsyncSession, principal: ServicePrincipal, family_id: int, data) -> DoranMessage:
    # Capture plain scalars up front - see send_message()'s comment on why
    # touching an ORM object's attributes after db.rollback() is unsafe.
    principal_id = principal.id
    room_id = data.room_id

    binding = (await db.execute(select(DoranServiceBinding).where(
        DoranServiceBinding.service_principal_id == principal_id,
        DoranServiceBinding.room_id == room_id,
        DoranServiceBinding.family_group_id == family_id,
    ))).scalars().first()
    if binding is None or binding.status != "active":
        await _audit(db, "permission_denied", principal_id, family_id, room_id, "denied", "binding_not_found_or_inactive")
        await db.commit()
        raise HTTPException(status_code=404, detail="발행 대상을 찾을 수 없습니다")

    room = (await db.execute(select(DoranRoom).where(
        DoranRoom.id == room_id, DoranRoom.family_group_id == family_id, DoranRoom.deleted_at.is_(None),
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
    existing = (await db.execute(select(DoranMessage).where(
        DoranMessage.service_principal_id == principal_id,
        DoranMessage.source == data.source,
        DoranMessage.source_event_id == data.source_event_id,
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
        sequence = (await db.execute(update(DoranRoom).where(DoranRoom.id == room_pk, DoranRoom.family_group_id == family_id).values(next_message_sequence=DoranRoom.next_message_sequence + 1).returning(DoranRoom.next_message_sequence))).scalar_one()
        message = DoranMessage(
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
        existing = (await db.execute(select(DoranMessage).where(
            DoranMessage.service_principal_id == principal_id,
            DoranMessage.source == data.source,
            DoranMessage.source_event_id == data.source_event_id,
        ))).scalars().one()
        if not _same_service_event(existing, room_pk, data.schema_version, data.action_type, data.snapshot):
            await _audit(db, "permission_denied", principal_id, family_id, room_pk, "conflict", "source_event_id_payload_conflict")
            await db.commit()
            raise HTTPException(status_code=409, detail="source_event_id payload conflict")
        await db.refresh(existing)
        await _audit(db, "replay_detected", principal_id, family_id, room_pk, "idempotent")
        await db.commit()
        return existing
