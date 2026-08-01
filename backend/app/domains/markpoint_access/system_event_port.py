"""Markpoint -> Wagle system-actor event port (Wave 4, D5-C).

Contract-only. `MONGLE-W2-WAGLE-DURABLE-COMMAND-001`'s realtime dispatcher
(Wave 3) does not exist yet, and a parallel Wave 2 lane's Wagle durable-
messaging/Outbox interface is still under its own independent QA in this same
session window -- wiring an adapter against either right now would build
against an unconfirmed interface. This module defines the envelope and the
abstract publish contract Markpoint's own product code (Wave 5) will call,
plus a contract test double that proves the envelope/idempotency/room-binding
rules without ever importing a Wagle repository or touching its tables.

Deliberate boundaries:

- No Wagle table is written here, directly or indirectly.
- No human Membership is ever substituted as the actor -- every envelope
  carries a `service_principal_id`, never an `account_id`/`membership_id`.
- `family_group_id` and `approved_room_binding_id` are both required so an
  adapter has no path to deliver into an unapproved or cross-family room.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Protocol


class MarkpointSystemEventEnvelopeError(ValueError):
    """Raised when an envelope violates the D5-C contract before publish."""


@dataclass(frozen=True)
class MarkpointSystemEventEnvelope:
    source_event_id: str
    event_type: str
    family_group_id: int
    service_principal_id: int
    approved_room_binding_id: int
    occurred_at: datetime
    payload: dict
    payload_version: int = 1

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise MarkpointSystemEventEnvelopeError("source_event_id is required")
        if not self.event_type:
            raise MarkpointSystemEventEnvelopeError("event_type is required")
        if self.family_group_id <= 0:
            raise MarkpointSystemEventEnvelopeError("family_group_id is required")
        if self.service_principal_id <= 0:
            raise MarkpointSystemEventEnvelopeError("service_principal_id is required")
        if self.approved_room_binding_id <= 0:
            raise MarkpointSystemEventEnvelopeError(
                "approved_room_binding_id is required -- no unbound or cross-family delivery"
            )

    @property
    def idempotency_key(self) -> str:
        # One source event must never publish twice, regardless of retry.
        return f"{self.event_type}:{self.source_event_id}"


@dataclass(frozen=True)
class PublishResult:
    envelope: MarkpointSystemEventEnvelope
    deduplicated: bool


class MarkpointSystemEventPort(Protocol):
    """Adapter contract a future Wave 3/5 integration implements.

    No implementation in this module talks to a real transport. A real
    adapter (Outbox row insert, dispatcher call, etc.) is out of this task's
    scope until Wave 3's realtime dispatcher lands and Lane A's Outbox
    interface has passed its own independent QA.
    """

    async def publish(self, envelope: MarkpointSystemEventEnvelope) -> PublishResult:
        ...


class InMemoryMarkpointSystemEventPort:
    """Contract test double. Not a production adapter.

    Proves the port's dedup/idempotency and required-field rules in
    isolation, with no DB and no Wagle import.
    """

    def __init__(self) -> None:
        self._published: Dict[str, MarkpointSystemEventEnvelope] = {}

    async def publish(self, envelope: MarkpointSystemEventEnvelope) -> PublishResult:
        key = envelope.idempotency_key
        if key in self._published:
            return PublishResult(envelope=self._published[key], deduplicated=True)
        self._published[key] = envelope
        return PublishResult(envelope=envelope, deduplicated=False)

    @property
    def published_events(self) -> List[MarkpointSystemEventEnvelope]:
        return list(self._published.values())
