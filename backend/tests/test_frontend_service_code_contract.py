"""The contract the frontend reads to decide whether Wagle is available.

`MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`.

This is the exact seam where the Wave 2/4 rename broke the UI: the frontend
compares `service_code` from a **live** `/api/account-context` response against
a literal. Migration `0007` renamed that value, and the frontend kept comparing
against the old one, so every family with an active Wagle subscription rendered
as unavailable.

A type check cannot catch that — both sides are `string`. Only asserting the
actual emitted value against the literal the frontend uses can. These tests pin
the value the API really returns so a future rename cannot silently desync the
two sides again.
"""
from __future__ import annotations

from sqlalchemy import text

from tests.conftest import create_actor, create_family, set_subscription

# The literal the frontend compares against, in
# `MongleAppShell.tsx` (`serviceStatus('wagle')`) and `WagleLanding.tsx`
# (`service.service_code === 'wagle'`). Kept as a plain literal on purpose: if
# either side is renamed without the other, this test fails.
FRONTEND_WAGLE_SERVICE_CODE = "wagle"


async def test_account_context_emits_the_service_code_the_frontend_compares(db, client):
    """End-to-end: an active subscription must reach the UI as `wagle`."""
    family_id = await create_family(db, "FE Contract Family")
    actor = await create_actor(db, family_id, name="fe-contract")
    await set_subscription(db, family_id, "active")

    resp = await client.get("/api/account-context", headers=actor.headers)
    assert resp.status_code == 200, resp.text

    families = resp.json()["families"]
    assert families, "the actor must see its own family"
    services = families[0]["services"]
    assert services, "the active subscription must be present in the payload"

    codes = {s["service_code"] for s in services}
    assert FRONTEND_WAGLE_SERVICE_CODE in codes, (
        f"the API emits {codes!r}, but the frontend looks up "
        f"{FRONTEND_WAGLE_SERVICE_CODE!r} — the two are out of sync"
    )

    # And the status the UI gates on ("is it active?") must be readable.
    wagle = next(s for s in services if s["service_code"] == FRONTEND_WAGLE_SERVICE_CODE)
    assert wagle["status"] == "active"


async def test_no_historical_service_code_reaches_the_frontend(db, client):
    """The old code must not appear in the payload at all.

    Built from parts so a repository-wide rename sweep cannot silently invert
    this assertion — that already happened once during the backend rename.
    """
    historical = "do" + "ran"
    family_id = await create_family(db, "FE Historical Check")
    actor = await create_actor(db, family_id, name="fe-historical")
    await set_subscription(db, family_id, "active")

    body = (await client.get("/api/account-context", headers=actor.headers)).json()
    assert historical not in str(body), (
        "the historical service code must not reach the frontend in any field"
    )


async def test_subscription_rows_carry_the_target_service_code(db):
    """The stored value itself, not just the serialized response."""
    family_id = await create_family(db, "FE Stored Code")
    await set_subscription(db, family_id, "active")

    codes = (
        await db.execute(text("SELECT DISTINCT service_code FROM service_subscriptions"))
    ).scalars().all()
    assert FRONTEND_WAGLE_SERVICE_CODE in codes
    assert not any("do" + "ran" == c for c in codes)
