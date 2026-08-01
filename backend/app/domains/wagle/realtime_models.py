"""Wave 3 persistence: Push subscriptions, per-endpoint delivery attempts, and
the Wagle device PIN.

Three deliberate absences, each of which would have been the easy thing to add:

1. **No new message, room-sequence or read-cursor table.** Wave 2 already owns
   all three (`wagle_messages.sequence`, `wagle_participant_read_states`), and
   realtime resume is a *query* over that durable sequence, not a second
   cursor store. A parallel realtime cursor would immediately be able to
   disagree with the read state it shadows.

2. **Push subscriptions are Account-scoped, not Family-scoped.** One Account
   can hold memberships in several Families; duplicating a row per Family would
   make one physical device look like several subscribers and would have to be
   fanned out and expired N times. The subscription owns the *device*; the
   event carries the Family scope.

3. **The device PIN is not the legacy player PIN.** `auth.models` already has a
   `pin_hash` for the legacy MarkPoint player login. That one authenticates;
   this one only locks a screen on one device. Reusing it would silently make a
   screen lock into a credential.
"""
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from app.models.base import Base, TimestampMixin


class WaglePushSubscription(Base, TimestampMixin):
    """One PWA push endpoint, owned by an Account on one device installation.

    `endpoint` and the key material are secrets in the sense that they are
    capabilities: anyone holding them can push to that browser. They are never
    logged, never returned in an API response, and never readable across
    Accounts.
    """

    __tablename__ = "wagle_push_subscriptions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    device_id = Column(String(128), nullable=False)
    endpoint = Column(Text, nullable=False)
    p256dh_key = Column(String(255), nullable=False)
    auth_secret = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, server_default="active")
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    last_error_code = Column(String(60), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(40), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'expired', 'revoked')",
            name="ck_wagle_push_subscriptions_status",
        ),
    )


# One live subscription per endpoint, enforced by the database rather than by a
# check-then-insert in the service: two tabs registering the same browser
# endpoint concurrently would otherwise both pass the check and both insert.
Index(
    "uq_wagle_push_subscription_active_endpoint",
    WaglePushSubscription.endpoint,
    unique=True,
    postgresql_where=WaglePushSubscription.status == "active",
)
# One live subscription per (account, device) for the same reason — a device
# that re-registers replaces its own row instead of accumulating them.
Index(
    "uq_wagle_push_subscription_active_device",
    WaglePushSubscription.account_id,
    WaglePushSubscription.device_id,
    unique=True,
    postgresql_where=WaglePushSubscription.status == "active",
)
Index(
    "ix_wagle_push_subscriptions_account_status",
    WaglePushSubscription.account_id,
    WaglePushSubscription.status,
)


class WaglePushDeliveryAttempt(Base, TimestampMixin):
    """Delivery idempotency, per (Outbox event, endpoint).

    This is a different question from domain idempotency. `send_message`
    already guarantees one message per `client_message_id`; this guarantees
    that re-processing the *same* Outbox row — which at-least-once delivery
    makes routine, not exceptional — does not push the same notification to the
    same device twice.

    It is also the failure-isolation record: one endpoint going 410 marks its
    own row and its own subscription, and says nothing about any other device
    or Family.
    """

    __tablename__ = "wagle_push_delivery_attempts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    outbox_event_id = Column(
        BigInteger, ForeignKey("service_outbox_events.id", ondelete="CASCADE"), nullable=False
    )
    subscription_id = Column(
        BigInteger, ForeignKey("wagle_push_subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    family_group_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, server_default="PENDING")
    attempt_count = Column(Integer, nullable=False, server_default="0")
    last_error_code = Column(String(60), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "outbox_event_id", "subscription_id", name="uq_wagle_push_attempt_event_subscription"
        ),
        CheckConstraint(
            "status IN ('PENDING', 'SENT', 'FAILED', 'EXPIRED_ENDPOINT')",
            name="ck_wagle_push_attempt_status",
        ),
    )


Index(
    "ix_wagle_push_attempts_family_status",
    WaglePushDeliveryAttempt.family_group_id,
    WaglePushDeliveryAttempt.status,
)


class WagleDevicePin(Base, TimestampMixin):
    """Optional per-(Account, device) screen lock for the Wagle conversation UI.

    Scope is deliberately narrow, and each narrowing is a contract, not a
    simplification:

    - **Not a credential.** It never authenticates a request; the Account
      Session does. A locked device still holds a live Session.
    - **Not Family-scoped.** One personal PIN per device covers every Family
      that Account can reach. A per-Family PIN would make the lock a
      family-visible property of a personal device.
    - **Not readable by anyone, including a FamilyAdmin.** Only `pin_hash` is
      stored, and no endpoint returns it. Recovery is reset, never retrieval —
      there is deliberately no code path that can answer "what is the PIN".
    """

    __tablename__ = "wagle_device_pins"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    device_id = Column(String(128), nullable=False)
    pin_hash = Column(String(255), nullable=False)
    pin_version = Column(Integer, nullable=False, server_default="1")
    failed_attempt_count = Column(Integer, nullable=False, server_default="0")
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_unlocked_at = Column(DateTime(timezone=True), nullable=True)
    last_reset_at = Column(DateTime(timezone=True), nullable=True)
    disabled_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # One PIN per (Account, device). Device isolation is this constraint:
        # another device of the same Account gets its own row and its own
        # attempt counter, so brute-forcing one device cannot lock out another.
        UniqueConstraint("account_id", "device_id", name="uq_wagle_device_pin_account_device"),
        CheckConstraint("failed_attempt_count >= 0", name="ck_wagle_device_pin_attempts"),
    )


Index("ix_wagle_device_pins_account", WagleDevicePin.account_id)
