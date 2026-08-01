"""Composition-root adapter: Markpoint system events -> Wagle (Wave 4, D5-C).

This is the only place the two domains meet, and it meets them at the
**application-service** boundary, never the data one:

    Markpoint domain
      -> MarkpointSystemEventPort (a Protocol it owns)
      -> this adapter
      -> wagle.service.publish_service_action()

Markpoint never imports a Wagle model, table or repository. Reverse the arrows
and Markpoint would own a second copy of Wagle's authorization rules; keeping
the call at the service boundary means room binding, family match, subscription
state, action allow-listing, dedup and the audit trail are all enforced once, by
the domain that owns them.

What this adapter deliberately does **not** do:

- It does not re-check the binding itself. `publish_service_action()` already
  denies a missing, inactive, cross-family or non-SERVICE-room binding, and a
  second check here would drift from the real one.
- It does not write a Wagle table.
- It does not accept a human actor. The envelope carries a
  `service_principal_id`; there is no code path here that takes an
  `account_id`/`membership_id` and no way to post under a person's name.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.markpoint_access.system_event_port import (
    MarkpointSystemEventEnvelope, MarkpointSystemEventEnvelopeError, PublishResult,
)
# Imported as a module and called through a dotted reference, per the Backend
# Guide's cross-service rule — it preserves the patch seam and makes the
# dependency direction obvious at the call site.
from app.domains.wagle import service as wagle_service

# The service this adapter targets. Wagle is the Target name; there is no
# `doran` fallback and no translation map — migration 0007 moved the whole
# runtime, so a second identifier would be a regression, not compatibility.
TARGET_SERVICE = "wagle"
SOURCE_SERVICE = "markpoint"


@dataclass(frozen=True)
class _PublishInput:
    """Matches `ServiceActionPublish`'s attribute surface.

    `publish_service_action()` reads its input by attribute, so a plain frozen
    dataclass satisfies it without importing Wagle's Pydantic schema — which
    would pull Wagle's wire contract into Markpoint's dependency graph for no
    benefit.
    """

    room_id: UUID
    action_type: str
    schema_version: int
    source: str
    source_event_id: str
    snapshot: dict


class WagleMarkpointSystemEventAdapter:
    """Publishes an approved Markpoint system event into its family's Wagle room.

    Constructed at the composition root with the DB session and the Markpoint
    `ServicePrincipal`; Markpoint's own code holds only the port Protocol.
    """

    def __init__(self, db: AsyncSession, principal) -> None:
        # `principal` is a Wagle ServicePrincipal. Deliberately untyped here:
        # importing the model for an annotation would put a Wagle table class
        # in Markpoint's import graph, which is the boundary this module exists
        # to hold. The object is only ever passed straight back to Wagle.
        self._db = db
        self._principal = principal

    async def publish(self, envelope: MarkpointSystemEventEnvelope) -> PublishResult:
        """Relay one envelope. Idempotent per `(principal, source, source_event_id)`.

        Wagle's own partial unique index on those three columns is what makes a
        retry return the original message instead of posting twice, so dedup is
        enforced by the database rather than by this adapter's memory.
        """
        if envelope.service_principal_id != self._principal.id:
            # The envelope names a different actor than this adapter was built
            # for; publishing anyway would post under the wrong identity.
            raise ValueError(
                "envelope.service_principal_id does not match the adapter's principal"
            )

        # The envelope names an approved *binding*, not a raw room. Markpoint has
        # no way to have been authorized for a bare room id, so resolving it here
        # is what keeps "which room may this event reach" answerable only by the
        # domain that owns the binding.
        room_id = await wagle_service.resolve_binding_room_id(
            self._db, envelope.approved_room_binding_id, envelope.family_group_id
        )
        if room_id is None:
            raise MarkpointSystemEventEnvelopeError(
                "approved_room_binding_id does not resolve to an active binding in this family"
            )

        before = await self._existing_message_id(envelope)
        message = await wagle_service.publish_service_action(
            self._db,
            self._principal,
            envelope.family_group_id,
            _PublishInput(
                room_id=room_id,
                action_type=envelope.event_type,
                schema_version=envelope.payload_version,
                source=SOURCE_SERVICE,
                source_event_id=envelope.source_event_id,
                snapshot=envelope.payload,
            ),
        )
        return PublishResult(envelope=envelope, deduplicated=before == message.id)

    async def _existing_message_id(self, envelope: MarkpointSystemEventEnvelope):
        """Whether this exact source event was already published.

        Goes through Wagle's own query function rather than selecting from its
        tables here — an earlier draft of this file imported `WagleMessage`
        directly, which is exactly the boundary violation this module's docstring
        forbids. Used only to report `deduplicated` honestly; the guarantee
        itself is Wagle's unique index.
        """
        return await wagle_service.find_service_message_id(
            self._db, self._principal.id, SOURCE_SERVICE, envelope.source_event_id
        )
