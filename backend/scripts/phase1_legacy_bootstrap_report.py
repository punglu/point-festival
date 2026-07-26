#!/usr/bin/env python3
"""Emit a read-only, non-identifying legacy bootstrap inventory.

This tool intentionally does not create Accounts, mappings, or Family roles.
It is for a synthetic/local database or a separately authorized operational
review only.  The output contains aggregate counts, never credentials, PINs,
usernames, or display names; an explicit reviewed mapping remains required
before any operational bootstrap.
"""
import asyncio
import json

from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.domains.auth.models import AdminAuth, PlayerAuth
from app.domains.family.models import LegacyIdentityMapping
from app.domains.player.models import Player


async def count(session, statement) -> int:
    return int((await session.scalar(statement)) or 0)


async def main() -> None:
    async with AsyncSessionLocal() as db:
        active_players = await count(
            db, select(func.count()).select_from(Player).where(Player.deleted_at.is_(None))
        )
        deleted_players = await count(
            db, select(func.count()).select_from(Player).where(Player.deleted_at.is_not(None))
        )
        player_auth_without_player = await count(
            db,
            select(func.count())
            .select_from(PlayerAuth)
            .outerjoin(Player, Player.id == PlayerAuth.player_id)
            .where(Player.id.is_(None)),
        )
        linked_mappings = await count(
            db,
            select(func.count())
            .select_from(LegacyIdentityMapping)
            .where(LegacyIdentityMapping.mapping_status == "linked"),
        )
        ambiguous_mappings = await count(
            db,
            select(func.count())
            .select_from(LegacyIdentityMapping)
            .where(LegacyIdentityMapping.mapping_status == "ambiguous"),
        )
        player_auth_records = await count(db, select(func.count()).select_from(PlayerAuth))
        admin_auth_records = await count(db, select(func.count()).select_from(AdminAuth))

    report = {
        "tool": "phase1_legacy_bootstrap_report",
        "mode": "read_only",
        "legacy_inventory": {
            "active_players": active_players,
            "soft_deleted_players": deleted_players,
            "player_auth_records": player_auth_records,
            "admin_auth_records": admin_auth_records,
            "player_auth_orphans": player_auth_without_player,
        },
        "mapping_inventory": {
            "linked": linked_mappings,
            "ambiguous": ambiguous_mappings,
        },
        "controls": [
            "No Account, Family Group, Membership, Role, or mapping is created.",
            "No relationship or Owner is inferred from a name, username, or role.",
            "Operational bootstrap requires explicit reviewed Owner and identity mapping input.",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
