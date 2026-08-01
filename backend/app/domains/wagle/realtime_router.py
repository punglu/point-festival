"""Wave 3 HTTP/WebSocket surface: realtime gateway, resume, Push, device PIN.

Route placement follows D7 as the rest of the codebase applies it:

- Anything scoped to a Family sits under `/api/families/{family_id}/wagle/...`.
- Anything that belongs to the calling Account or one of its devices sits under
  `/api/me/wagle/...`, alongside the existing `/api/me/sessions` and
  `/api/me/devices/{device_id}`. Push subscriptions and the device PIN are
  personal, not family property, so a family-scoped path would be wrong even
  though the feature is a Wagle feature.

The WebSocket is Account-scoped rather than Family-scoped on purpose: one
logical subscription covers the whole AuthorizedFamilySet (D1). Putting it
under a family path would have forced one socket per family and made
"ActiveFamilyContext" load-bearing, which D1 forbids.
"""
from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal, get_db
from app.domains.family import auth_service
from app.domains.family.dependencies import get_current_account
from app.domains.family.models import Account
from app.domains.wagle import device_pin_service, push_service, realtime

router = APIRouter(tags=["wagle-realtime"])


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------


class PushSubscriptionCreate(BaseModel):
    device_id: str = Field(..., max_length=128)
    endpoint: str = Field(..., max_length=2000)
    p256dh_key: str = Field(..., max_length=255)
    auth_secret: str = Field(..., max_length=255)


class PushSubscriptionResponse(BaseModel):
    """Deliberately excludes `endpoint`, `p256dh_key` and `auth_secret`.

    Those three together are a capability to push to that browser. Echoing them
    back would put them in logs, proxies and browser history for no benefit —
    the client already has the values it just sent.
    """

    id: int
    device_id: str
    status: str


class DevicePinSet(BaseModel):
    device_id: str = Field(..., max_length=128)
    pin: str = Field(..., max_length=32)


class DevicePinVerify(BaseModel):
    device_id: str = Field(..., max_length=128)
    pin: str = Field(..., max_length=32)


class DevicePinStatusResponse(BaseModel):
    configured: bool
    locked: bool
    locked_until: str | None = None
    remaining_attempts: int | None = None
    pin_version: int | None = None


# --------------------------------------------------------------------------
# Resume / recovery (REST) — the durable recovery path
# --------------------------------------------------------------------------


@router.get("/api/families/{family_id}/wagle/rooms/{room_id}/resume")
async def resume_room(
    family_id: int,
    room_id: str,
    after_sequence: int = Query(0, ge=0),
    limit: int = Query(realtime.MAX_RESUME_BATCH, ge=1, le=realtime.MAX_RESUME_BATCH),
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Events durably recorded after `after_sequence`.

    This is the recovery contract: reconnect, server restart, device sleep, PWA
    relaunch and a lost Push all resolve here, against the database, not
    against any transport buffer. It is safe to call with a cursor the client
    already covered — replay is expected, and duplicates are removed by
    `(room_id, room_sequence)`.
    """
    try:
        return await realtime.resume_missed_events(
            db, account, family_id, room_id, after_sequence, limit
        )
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")


@router.get("/api/me/wagle/realtime-context")
async def realtime_context(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """The server-derived AuthorizedFamilySet for this Account.

    The client uses it to know what it may subscribe to. It is advisory: the
    WebSocket re-derives the same set server-side on every subscribe, so a
    client that ignores this and asks for something else is simply denied.
    """
    family_ids = sorted(await realtime.authorized_family_ids(db, account.id))
    return {"account_id": account.id, "authorized_family_ids": family_ids}


# --------------------------------------------------------------------------
# Push subscriptions (Account + device)
# --------------------------------------------------------------------------


@router.post(
    "/api/me/wagle/push-subscriptions",
    response_model=PushSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_push_subscription(
    data: PushSubscriptionCreate,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    row = await push_service.register_subscription(
        db,
        account.id,
        device_id=data.device_id,
        endpoint=data.endpoint,
        p256dh_key=data.p256dh_key,
        auth_secret=data.auth_secret,
    )
    return PushSubscriptionResponse(id=row.id, device_id=row.device_id, status=row.status)


@router.get("/api/me/wagle/push-subscriptions", response_model=list[PushSubscriptionResponse])
async def list_push_subscriptions(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Only ever this Account's own rows — `account.id` comes from the verified
    Session, never from a query parameter, so there is no id to tamper with."""
    rows = await push_service.list_subscriptions(db, account.id)
    return [PushSubscriptionResponse(id=r.id, device_id=r.device_id, status=r.status) for r in rows]


@router.delete("/api/me/wagle/push-subscriptions/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_push_subscription(
    device_id: str,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    await push_service.revoke_for_device(db, account.id, device_id, reason="client_request")
    return None


# --------------------------------------------------------------------------
# Wagle device PIN
# --------------------------------------------------------------------------


@router.get("/api/me/wagle/device-pin", response_model=DevicePinStatusResponse)
async def get_device_pin_status(
    device_id: str = Query(..., max_length=128),
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    return DevicePinStatusResponse(**await device_pin_service.get_status(db, account.id, device_id))


@router.put("/api/me/wagle/device-pin", response_model=DevicePinStatusResponse)
async def set_device_pin(
    data: DevicePinSet,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    return DevicePinStatusResponse(
        **await device_pin_service.set_pin(db, account.id, data.device_id, data.pin)
    )


@router.post("/api/me/wagle/device-pin/verify")
async def verify_device_pin(
    data: DevicePinVerify,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Unlock this device's Wagle screen.

    Failing here locks a screen. It does not revoke the Session, does not touch
    another device, and does not stop Push — all three of which would be
    plausible-looking and all three of which are forbidden.
    """
    return await device_pin_service.verify_pin(db, account.id, data.device_id, data.pin)


@router.post("/api/me/wagle/device-pin/reset", response_model=DevicePinStatusResponse)
async def reset_device_pin(
    data: DevicePinSet,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Recovery is replacement. There is no endpoint that reads a PIN back."""
    return DevicePinStatusResponse(
        **await device_pin_service.reset_pin(db, account.id, data.device_id, data.pin)
    )


@router.post("/api/me/wagle/device-pin/disable", response_model=DevicePinStatusResponse)
async def disable_device_pin(
    data: DevicePinVerify,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    return DevicePinStatusResponse(
        **await device_pin_service.disable_pin(db, account.id, data.device_id, data.pin)
    )


# --------------------------------------------------------------------------
# WebSocket gateway
# --------------------------------------------------------------------------


async def _authenticate_socket(db: AsyncSession, token: str | None) -> tuple[Account, int]:
    """Account-native Session only.

    A WebSocket cannot carry an `Authorization` header from the browser API, so
    the token arrives as a query parameter. That is the standard workaround and
    it is why the checks below are done in full rather than trusting the
    handshake: the token must decode, name a Session, that Session must still be
    live, and it must agree with the Account it claims. A legacy player/admin
    token fails at `decode_access_token`, which only accepts the Account role.
    """
    if not token:
        raise PermissionError("token required")
    payload = auth_service.decode_access_token(token)
    session_id = payload.get("sid")
    if session_id is None:
        raise PermissionError("session missing")
    session_row = await auth_service.load_active_session(db, int(session_id))
    account_id = int(payload["sub"])
    if session_row.account_id != account_id:
        raise PermissionError("session mismatch")
    account = await db.get(Account, account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        raise PermissionError("account unusable")
    return account, int(session_id)


@router.websocket("/api/me/wagle/ws")
async def wagle_realtime_socket(websocket: WebSocket, token: str | None = Query(default=None)):
    """One logical subscription across every authorized Family.

    Multiple physical sockets per Session are legitimate (tabs, reconnects,
    connection replacement) and are **not** treated as an error — the Realtime
    Messaging Contract states no invariant may forbid them. Each gets its own
    `connection_id` and its own lifecycle.

    Two background loops run per connection, and the difference between them is
    the difference between security and availability:

    - **revalidate**: re-derives authority from the database. This is the upper
      bound on how long a revoked membership keeps receiving events.
    - **catch-up**: replays anything durable this socket did not hear. This is
      what makes a missed fan-out — including one that happened on a different
      uvicorn worker — a latency event rather than a lost message.
    """
    await websocket.accept()

    async with AsyncSessionLocal() as db:
        try:
            account, session_id = await _authenticate_socket(db, token)
        except Exception:
            await websocket.send_json({"type": "error", "code": "unauthorized"})
            await websocket.close(code=4401)
            return
        authorized = sorted(await realtime.authorized_family_ids(db, account.id))

    connection = realtime.Connection(
        connection_id=str(uuid.uuid4()),
        account_id=account.id,
        session_id=session_id,
        device_id=None,
        send=websocket.send_json,
    )
    await realtime.fanout.register(connection)

    # Per-room cursor this socket has already emitted, so the catch-up loop
    # replays a gap once instead of on every tick.
    cursors: dict[tuple[int, str], int] = {}
    stop = asyncio.Event()

    await websocket.send_json(
        {
            "type": "connected",
            "connection_id": connection.connection_id,
            "account_id": account.id,
            "authorized_family_ids": authorized,
            "revalidate_seconds": settings.WAGLE_REALTIME_REVALIDATE_SECONDS,
            "catchup_seconds": settings.WAGLE_REALTIME_CATCHUP_SECONDS,
        }
    )

    async def revalidate_loop() -> None:
        while not stop.is_set():
            try:
                await asyncio.wait_for(
                    stop.wait(), timeout=settings.WAGLE_REALTIME_REVALIDATE_SECONDS
                )
                return
            except asyncio.TimeoutError:
                pass
            async with AsyncSessionLocal() as loop_db:
                result = await realtime.revalidate_connection(loop_db, connection)
            if result.get("terminate"):
                await websocket.send_json(
                    {"type": "session_revoked", "reason": result.get("reason", "session")}
                )
                stop.set()
                return
            for family_id in result.get("revoked_families", []):
                # Only this family goes. Every other family on this same socket
                # keeps working — losing one membership is not a logout.
                for key in [k for k in cursors if k[0] == family_id]:
                    cursors.pop(key, None)
                await websocket.send_json(
                    {"type": "subscription_revoked", "family_id": family_id, "reason": "membership"}
                )
            for family_id, room_id in result.get("revoked_rooms", []):
                cursors.pop((family_id, room_id), None)
                await websocket.send_json(
                    {
                        "type": "subscription_revoked",
                        "family_id": family_id,
                        "room_id": room_id,
                        "reason": "room",
                    }
                )

    async def catchup_loop() -> None:
        while not stop.is_set():
            try:
                await asyncio.wait_for(
                    stop.wait(), timeout=settings.WAGLE_REALTIME_CATCHUP_SECONDS
                )
                return
            except asyncio.TimeoutError:
                pass
            pairs = list(realtime.subscribed_pairs(connection))
            for family_id, room_id in pairs:
                cursor = cursors.get((family_id, room_id), 0)
                async with AsyncSessionLocal() as loop_db:
                    try:
                        result = await realtime.resume_missed_events(
                            loop_db, account, family_id, room_id, cursor
                        )
                    except Exception:
                        # Authority may have just been withdrawn; the
                        # revalidate loop owns that transition. One room's
                        # failure must not stop the others' catch-up.
                        continue
                for event in result["events"]:
                    await websocket.send_json({"type": "event", **event})
                if result["events"]:
                    cursors[(family_id, room_id)] = result["next_sequence"]

    tasks = [asyncio.create_task(revalidate_loop()), asyncio.create_task(catchup_loop())]

    try:
        while not stop.is_set():
            raw = await websocket.receive_json()
            action = raw.get("action")

            if action == "subscribe":
                family_id = raw.get("family_id")
                room_id = raw.get("room_id")
                async with AsyncSessionLocal() as sub_db:
                    try:
                        await realtime.authorize_subscription(
                            sub_db, account, int(family_id), str(room_id)
                        )
                    except Exception:
                        # One denial does not close the socket: a client with
                        # three families and one stale room should keep the
                        # other two working.
                        await websocket.send_json(
                            {
                                "type": "subscribe_denied",
                                "family_id": family_id,
                                "room_id": room_id,
                            }
                        )
                        continue
                connection.subscriptions.setdefault(int(family_id), set()).add(str(room_id))
                after = int(raw.get("after_sequence") or 0)
                cursors[(int(family_id), str(room_id))] = after
                await websocket.send_json(
                    {"type": "subscribed", "family_id": int(family_id), "room_id": str(room_id)}
                )

            elif action == "unsubscribe":
                family_id = int(raw.get("family_id"))
                room_id = str(raw.get("room_id"))
                connection.drop_room(family_id, room_id)
                cursors.pop((family_id, room_id), None)
                await websocket.send_json(
                    {"type": "unsubscribed", "family_id": family_id, "room_id": room_id}
                )

            elif action == "resume":
                family_id = int(raw.get("family_id"))
                room_id = str(raw.get("room_id"))
                after = int(raw.get("after_sequence") or 0)
                async with AsyncSessionLocal() as resume_db:
                    try:
                        result = await realtime.resume_missed_events(
                            resume_db, account, family_id, room_id, after
                        )
                    except Exception:
                        await websocket.send_json(
                            {"type": "resume_denied", "family_id": family_id, "room_id": room_id}
                        )
                        continue
                cursors[(family_id, room_id)] = result["next_sequence"]
                await websocket.send_json({"type": "resume", **result})

            elif action == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({"type": "error", "code": "unknown_action"})

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        stop.set()
        for task in tasks:
            task.cancel()
        await realtime.fanout.unregister(connection.connection_id)
