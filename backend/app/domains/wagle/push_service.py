"""Wagle Web Push: subscription lifecycle, delivery port, policy seam.

**Push is a hint, not a delivery guarantee.** It is a fast background
notification and nothing more. A dropped, delayed or duplicated Push loses no
message, because every message is recoverable from `wagle_messages`. Equally, a
successful Push is not evidence the user received anything — so nothing here
may be surfaced as a user-facing `DELIVERED` state.

**The payload is deliberately empty of content, and that is a policy block, not
a design choice.** `D6-P1` (how much of a message body a notification may
disclose) is undecided. `build_payload()` below is the single seam where the
approved answer will land; until then it emits identifiers only. Putting a body
in a test fixture and letting it become the default is exactly the failure this
separation prevents, so the fixture path and the production path share one
function rather than diverging.

The subscription belongs to an **Account on a device**, never to a Family. One
Account can reach several Families; a per-Family row would make one physical
phone look like several subscribers and would have to be expired N times when
the browser rotates its endpoint.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domains.wagle.realtime import RealtimeEnvelope
from app.domains.wagle.realtime_models import WaglePushDeliveryAttempt, WaglePushSubscription


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PushDeliveryResult:
    """Outcome of one attempt against one endpoint."""

    SENT = "SENT"
    # The browser told us this endpoint is permanently gone (404/410). Retrying
    # is not just useless, it is harmful: it keeps a dead row in the fan-out set
    # forever. This deactivates the subscription.
    EXPIRED = "EXPIRED_ENDPOINT"
    # Anything transient — network, 429, 5xx. Worth another attempt.
    TRANSIENT = "TRANSIENT"


class PushTransportPort(Protocol):
    """The seam to an actual Web Push service.

    A port, not a direct call, for two reasons that both bit this project
    before: tests must never depend on an external push service being
    reachable, and the production adapter needs VAPID configuration that does
    not exist yet. The contract is narrow enough that a real adapter is a
    drop-in.
    """

    async def send(self, *, endpoint: str, p256dh: str, auth: str, payload: dict) -> str: ...


class NullPushTransport:
    """Default transport: accepts and discards.

    Chosen as the default over a real adapter because production Push requires
    VAPID keys that are not configured, and over raising because a missing key
    must not turn into an Outbox row retrying forever. It returns SENT so the
    delivery bookkeeping is exercised end to end; what it does *not* do is
    claim a user was notified.
    """

    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send(self, *, endpoint: str, p256dh: str, auth: str, payload: dict) -> str:
        self.sent.append({"endpoint": endpoint, "payload": payload})
        return PushDeliveryResult.SENT


_transport: PushTransportPort = NullPushTransport()


def set_transport(transport: PushTransportPort) -> None:
    """Install the transport. Used by the composition root and by tests."""
    global _transport
    _transport = transport


def get_transport() -> PushTransportPort:
    return _transport


# --------------------------------------------------------------------------
# Payload — the D6-P1 seam
# --------------------------------------------------------------------------

# Explicit marker so a reader (and a test) can tell the difference between
# "policy says minimal" and "someone forgot to add the body".
PAYLOAD_POLICY = "IDENTIFIERS_ONLY_PENDING_D6_P1"


def build_payload(envelope: RealtimeEnvelope) -> dict:
    """Notification payload for one event.

    Identifiers only. No body, no sender name, no room title — every one of
    those is a disclosure decision reserved to `D6-P1`, and a notification is
    rendered on a lock screen, outside the app's authentication context, which
    is precisely why that decision exists.

    The client uses these identifiers to deep-link; the content is then fetched
    through the authenticated API, which re-checks Session, Account state,
    membership, family scope and room permission before showing anything.
    """
    return {
        "policy": PAYLOAD_POLICY,
        "event_id": envelope.event_id,
        "event_type": envelope.event_type,
        "family_id": envelope.family_id,
        "room_id": envelope.room_id,
        "message_id": envelope.message_id,
        "room_sequence": envelope.room_sequence,
        "occurred_at": envelope.occurred_at,
        "actor_type": envelope.actor_type,
    }


# --------------------------------------------------------------------------
# Subscription lifecycle
# --------------------------------------------------------------------------


async def register_subscription(
    db: AsyncSession,
    account_id: int,
    *,
    device_id: str,
    endpoint: str,
    p256dh_key: str,
    auth_secret: str,
) -> WaglePushSubscription:
    """Register or replace this device's push endpoint.

    Two revocations happen first, and both matter:

    - Any other **active row for this same endpoint**, even under a different
      Account. A shared or re-issued browser endpoint must not keep pushing one
      Account's notifications to whoever is signed in now. This is the Account
      switch case.
    - Any other active row for this **(account, device)** pair, so a device
      that re-subscribes replaces itself rather than accumulating endpoints.
    """
    device = (device_id or "").strip()
    if not device or len(device) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="기기 식별자가 올바르지 않습니다")
    if not endpoint or not p256dh_key or not auth_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="구독 정보가 올바르지 않습니다")

    await db.execute(
        update(WaglePushSubscription)
        .where(
            WaglePushSubscription.status == "active",
            WaglePushSubscription.endpoint == endpoint,
        )
        .values(status="revoked", revoked_at=_now(), revoked_reason="endpoint_reassigned")
    )
    await db.execute(
        update(WaglePushSubscription)
        .where(
            WaglePushSubscription.status == "active",
            WaglePushSubscription.account_id == account_id,
            WaglePushSubscription.device_id == device,
        )
        .values(status="revoked", revoked_at=_now(), revoked_reason="device_resubscribed")
    )

    row = WaglePushSubscription(
        account_id=account_id,
        device_id=device,
        endpoint=endpoint,
        p256dh_key=p256dh_key,
        auth_secret=auth_secret,
    )
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        # Two tabs registered the same endpoint at once; the partial unique
        # index caught the loser. Return the winner rather than failing the
        # user-visible action, which is idempotent from their point of view.
        await db.rollback()
        existing = (
            await db.execute(
                select(WaglePushSubscription).where(
                    WaglePushSubscription.endpoint == endpoint,
                    WaglePushSubscription.status == "active",
                )
            )
        ).scalars().first()
        if existing is None:
            raise
        return existing
    await db.refresh(row)
    return row


async def list_subscriptions(db: AsyncSession, account_id: int) -> list[WaglePushSubscription]:
    return list(
        (
            await db.execute(
                select(WaglePushSubscription).where(
                    WaglePushSubscription.account_id == account_id,
                    WaglePushSubscription.status == "active",
                )
            )
        ).scalars()
    )


async def revoke_for_device(db: AsyncSession, account_id: int, device_id: str, *, reason: str) -> int:
    """Withdraw push authority for one device of one Account.

    Called on logout, device unlink and explicit deactivation. Scoped to the
    calling Account's own rows — an Account can never revoke another's.
    """
    result = await db.execute(
        update(WaglePushSubscription)
        .where(
            WaglePushSubscription.status == "active",
            WaglePushSubscription.account_id == account_id,
            WaglePushSubscription.device_id == device_id,
        )
        .values(status="revoked", revoked_at=_now(), revoked_reason=reason[:40])
    )
    await db.commit()
    return int(result.rowcount or 0)


async def revoke_for_account(db: AsyncSession, account_id: int, *, reason: str) -> int:
    """Withdraw every push authority for an Account (suspension, full logout)."""
    result = await db.execute(
        update(WaglePushSubscription)
        .where(
            WaglePushSubscription.status == "active",
            WaglePushSubscription.account_id == account_id,
        )
        .values(status="revoked", revoked_at=_now(), revoked_reason=reason[:40])
    )
    await db.commit()
    return int(result.rowcount or 0)


async def _expire_subscription(db: AsyncSession, subscription: WaglePushSubscription) -> None:
    subscription.status = "expired"
    subscription.last_failure_at = _now()
    subscription.last_error_code = "endpoint_gone"


# --------------------------------------------------------------------------
# Delivery
# --------------------------------------------------------------------------


async def deliver_event(
    db: AsyncSession,
    envelope: RealtimeEnvelope,
    *,
    outbox_event_id: int,
    recipient_account_ids: list[int],
) -> dict:
    """Push one event to every active endpoint of the given recipients.

    Failure isolation is per endpoint, by construction: each attempt is its own
    try/except and its own row, so one dead device cannot stop delivery to
    another device, another Account, or another Family.

    Idempotency is the unique `(outbox_event_id, subscription_id)` row, checked
    in the database rather than in memory — the dispatcher WILL reprocess this
    event (that is what at-least-once means), and without the constraint that
    is a second buzz on the user's phone for the same message.
    """
    if not recipient_account_ids:
        return {"attempted": 0, "sent": 0, "expired": 0, "failed": 0, "skipped_duplicate": 0}

    subscriptions = list(
        (
            await db.execute(
                select(WaglePushSubscription).where(
                    WaglePushSubscription.account_id.in_(recipient_account_ids),
                    WaglePushSubscription.status == "active",
                )
            )
        ).scalars()
    )

    payload = build_payload(envelope)
    transport = get_transport()
    stats = {"attempted": 0, "sent": 0, "expired": 0, "failed": 0, "skipped_duplicate": 0}

    for subscription in subscriptions:
        existing = (
            await db.execute(
                select(WaglePushDeliveryAttempt).where(
                    WaglePushDeliveryAttempt.outbox_event_id == outbox_event_id,
                    WaglePushDeliveryAttempt.subscription_id == subscription.id,
                )
            )
        ).scalars().first()
        if existing is not None and existing.status in ("SENT", "EXPIRED_ENDPOINT"):
            stats["skipped_duplicate"] += 1
            continue
        if existing is not None and int(existing.attempt_count) >= settings.WAGLE_PUSH_MAX_ATTEMPTS:
            stats["skipped_duplicate"] += 1
            continue

        attempt = existing or WaglePushDeliveryAttempt(
            outbox_event_id=outbox_event_id,
            subscription_id=subscription.id,
            family_group_id=envelope.family_id,
        )
        if existing is None:
            db.add(attempt)

        stats["attempted"] += 1
        try:
            outcome = await transport.send(
                endpoint=subscription.endpoint,
                p256dh=subscription.p256dh_key,
                auth=subscription.auth_secret,
                payload=payload,
            )
        except Exception:
            outcome = PushDeliveryResult.TRANSIENT

        attempt.attempt_count = int(attempt.attempt_count or 0) + 1
        if outcome == PushDeliveryResult.SENT:
            attempt.status = "SENT"
            attempt.delivered_at = _now()
            attempt.last_error_code = None
            stats["sent"] += 1
        elif outcome == PushDeliveryResult.EXPIRED:
            attempt.status = "EXPIRED_ENDPOINT"
            # Never store the endpoint or key material in the error field — the
            # whole point of the capability is that it stays out of logs.
            attempt.last_error_code = "endpoint_gone"
            await _expire_subscription(db, subscription)
            stats["expired"] += 1
        else:
            attempt.status = "FAILED"
            attempt.last_error_code = "transient"
            subscription.last_failure_at = _now()
            subscription.last_error_code = "transient"
            stats["failed"] += 1

    await db.commit()
    return stats
