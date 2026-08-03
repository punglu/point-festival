"""Family Search service (W7.5 Phase D SLICE-SEARCH). Scoped first pass to
sources that already have real data end-to-end (Markpoint missions, Wagle
messages), per the Phase D Slice Mapping's own recommendation -- Album/
Schedule search is deliberately not folded in here even though those
Slices now exist, to keep this Slice's own declared scope from silently
growing mid-implementation.

Read-only fan-out: this module owns no table of its own, and never mutates
either source domain."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family.models import FamilyMembership
from app.domains.markpoint_access import service as markpoint_access_service
from app.domains.markpoint_target import service as markpoint_service
from app.domains.wagle import service as wagle_service


async def search(db: AsyncSession, family_id: int, actor: FamilyMembership, query: str) -> list[dict]:
    results: list[dict] = []

    # Markpoint missions -- requires Markpoint access, same boundary every
    # other `own_*`/admin Markpoint read uses. A member with no Markpoint
    # access simply gets no mission results, not a 403 for the whole search.
    access_status = await markpoint_access_service.get_access_status(db, actor)
    if access_status["has_default_access"]:
        missions = await markpoint_service.search_missions_by_title(db, family_id, query)
        for mission in missions:
            results.append({
                "source": "mission",
                "title": mission.title,
                "meta": f"+{mission.reward_amount}P · {mission.status}",
                "occurred_at": mission.created_at,
            })

    # Wagle messages -- only rooms the actor participates in, only the
    # actor's own visible sequence range within each (same rule
    # `list_rooms_with_preview` and `list_messages` already use).
    message_rows = await wagle_service.search_visible_messages(db, actor.id, family_id, query)
    for body, created_at in message_rows:
        results.append({"source": "message", "title": body, "meta": "가족 대화", "occurred_at": created_at})

    results.sort(key=lambda r: r["occurred_at"], reverse=True)
    return results
