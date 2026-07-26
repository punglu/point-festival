from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.domains.doran import service
from app.domains.doran.schemas import MessageCreate, MessageListResponse, MessageResponse, ParticipantCreate, ParticipantResponse, ReadStateResponse, ReadStateUpdate, RoomCreate, RoomResponse, RoomUpdate, ServiceActionPublish, ServiceRoomOnboardResponse
from app.domains.doran.service_actor import get_current_service_principal
from app.domains.doran.models import ServicePrincipal
from app.domains.doran.ingress_limits import enforce_service_body_limit

router = APIRouter(prefix="/api/families/{family_id}/doran", tags=["doran"])

def room_out(room): return RoomResponse.model_validate(room)
def participant_out(item): return ParticipantResponse.model_validate(item)
def message_out(item):
    payload = item.service_payload or {}
    return MessageResponse(
        id=item.id, room_id=item.room_id, sequence=item.sequence, sender_participant_id=item.sender_participant_id,
        message_type=item.message_type, body=None if item.deleted_at else item.body, created_at=item.created_at,
        deleted_at=item.deleted_at, deleted=item.deleted_at is not None, tombstone="Message deleted" if item.deleted_at else None,
        service_code=item.service_code, service_payload_version=item.service_payload_version,
        service_payload=payload if item.message_type == "SERVICE_ACTION" else None,
    )

@router.get("/rooms", response_model=list[RoomResponse])
async def list_rooms(family_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return [room_out(x) for x in await service.list_rooms(db, user, family_id)]

@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(family_id: int, data: RoomCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    room, created = await service.create_room(db, user, family_id, data)
    return room_out(room)

@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(family_id: int, room_id: UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rooms = await service.list_rooms(db, user, family_id)
    for room in rooms:
        if room.id == room_id: return room_out(room)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Room을 찾을 수 없습니다")

@router.patch("/rooms/{room_id}", response_model=RoomResponse)
async def patch_room(family_id: int, room_id: UUID, data: RoomUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return room_out(await service.update_room(db, user, family_id, room_id, data.title, data.status))

@router.get("/rooms/{room_id}/participants", response_model=list[ParticipantResponse])
async def participants(family_id: int, room_id: UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    room = await service._room(db, family_id, room_id); _, membership = await service.context(db, user, family_id); await service._require_permission(db, membership, service.READ); await service._participant(db, room, membership)
    from sqlalchemy import select
    from app.domains.doran.models import DoranParticipant
    return [participant_out(x) for x in (await db.execute(select(DoranParticipant).where(DoranParticipant.room_id == room_id))).scalars()]

@router.post("/rooms/{room_id}/participants", response_model=ParticipantResponse, status_code=201)
async def add_participant(family_id: int, room_id: UUID, data: ParticipantCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return participant_out(await service.add_participant(db, user, family_id, room_id, data.family_membership_id, data.room_role))

@router.delete("/rooms/{room_id}/participants/{participant_id}", response_model=ParticipantResponse)
async def remove_participant(family_id: int, room_id: UUID, participant_id: UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return participant_out(await service.remove_participant(db, user, family_id, room_id, participant_id))

@router.post("/rooms/{room_id}/leave", response_model=ParticipantResponse)
async def leave(family_id: int, room_id: UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    room = await service._room(db, family_id, room_id); _, membership = await service.context(db, user, family_id); participant = await service._participant(db, room, membership)
    return participant_out(await service.remove_participant(db, user, family_id, room_id, participant.id, voluntary=True))

@router.get("/rooms/{room_id}/messages", response_model=MessageListResponse)
async def messages(family_id: int, room_id: UUID, after_sequence: int | None = Query(None, ge=0), before_sequence: int | None = Query(None, ge=1), limit: int = Query(50, ge=1, le=100), user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items, cursor = await service.list_messages(db, user, family_id, room_id, after_sequence, before_sequence, limit)
    return MessageListResponse(items=[message_out(x) for x in items], cursor=cursor)

@router.post("/rooms/{room_id}/messages", response_model=MessageResponse, status_code=201)
async def send(family_id: int, room_id: UUID, data: MessageCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return message_out(await service.send_message(db, user, family_id, room_id, data))

@router.delete("/rooms/{room_id}/messages/{message_id}", response_model=MessageResponse)
async def delete_message(family_id: int, room_id: UUID, message_id: UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return message_out(await service.delete_message(db, user, family_id, room_id, message_id))

@router.get("/rooms/{room_id}/read-state", response_model=ReadStateResponse)
async def get_read_state(family_id: int, room_id: UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    participant, state, unread = await service.read_state(db, user, family_id, room_id)
    return ReadStateResponse(participant_id=participant.id, last_read_sequence=state.last_read_sequence, unread_count=unread, updated_at=state.updated_at)

@router.put("/rooms/{room_id}/read-state", response_model=ReadStateResponse)
async def put_read_state(family_id: int, room_id: UUID, data: ReadStateUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    participant, state, unread = await service.read_state(db, user, family_id, room_id, data.last_read_sequence)
    return ReadStateResponse(participant_id=participant.id, last_read_sequence=state.last_read_sequence, unread_count=unread, updated_at=state.updated_at)

@router.post("/service/actions", response_model=MessageResponse, status_code=201, dependencies=[Depends(enforce_service_body_limit)])
async def publish_service_action(
    family_id: int,
    data: ServiceActionPublish,
    principal: ServicePrincipal = Depends(get_current_service_principal),
    db: AsyncSession = Depends(get_db),
):
    return message_out(await service.publish_service_action(db, principal, family_id, data))

@router.post("/services/{service_code}/room", response_model=ServiceRoomOnboardResponse, status_code=200)
async def onboard_service_room(family_id: int, service_code: str, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    room, participant = await service.onboard_self_into_service_room(db, user, family_id, service_code)
    return ServiceRoomOnboardResponse(
        room_id=room.id, family_group_id=room.family_group_id, service_code=service_code,
        participant_id=participant.id, room_role=participant.room_role,
        status=participant.status, joined_sequence=participant.joined_sequence,
    )
