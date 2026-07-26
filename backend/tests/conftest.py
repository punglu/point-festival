"""Real-PostgreSQL integration/concurrency fixtures for the Doran R2-A repair suite.

Targets the dedicated, isolated Phase 2 fixture database only
(docker-compose.phase2.yml, 127.0.0.1:15435). Never points at an operating
database. Business tables are truncated before every test for determinism;
the registry tables seeded by Alembic (roles/permissions/role_permissions)
are left untouched since they are shared, migration-owned data.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Awaitable

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://mc_phase2:phase2-local-only-not-production@127.0.0.1:15435/mc_festival_phase2",
)
os.environ.setdefault("JWT_SECRET", "phase2-r2a-repair-test-secret-not-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.database as database_module
from app.domains.auth.models import PlayerAuth
from app.domains.family.models import (
    Account,
    FamilyGroup,
    FamilyMembership,
    MembershipRoleAssignment,
    Role,
    ServiceSubscription,
    LegacyIdentityMapping,
)
from app.domains.player.models import Player
from app.main import app

# The production default pool (size 5 + overflow 10) is undersized for this
# suite's concurrency tests, which legitimately open dozens of simultaneous
# requests each needing their own DB connection/session (real Postgres
# concurrency, not simulated). NullPool opens a fresh physical connection per
# checkout instead of reusing a bounded pool, so one test's cancelled/aborted
# concurrent task can never hand a corrupted pooled connection to the next
# test. app.database.get_db() resolves AsyncSessionLocal from the module
# namespace at call time, so this also governs every request the ASGI app
# itself makes.
_test_engine = create_async_engine(os.environ["DATABASE_URL"], echo=False, poolclass=NullPool)
database_module.engine = _test_engine
database_module.AsyncSessionLocal = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)
engine = database_module.engine
AsyncSessionLocal = database_module.AsyncSessionLocal

TRUNCATE_ROOTS = "players, accounts, family_groups, service_outbox_events"


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    """Deterministic setup/teardown boundary: wipe all business data, keep the
    Alembic-seeded roles/permissions/role_permissions registry intact."""
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {TRUNCATE_ROOTS} RESTART IDENTITY CASCADE"))
    yield
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {TRUNCATE_ROOTS} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def db():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://phase2-repair-test") as ac:
        yield ac


def make_token(player_id: int, name: str = "actor") -> str:
    payload = {
        "sub": str(player_id),
        "name": name,
        "role": "player",
        "is_admin": False,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=os.environ["JWT_ALGORITHM"])


def auth_headers(player_id: int, name: str = "actor") -> dict:
    return {"Authorization": f"Bearer {make_token(player_id, name)}"}


@dataclass
class Actor:
    player_id: int
    account_id: int
    membership_id: int
    family_id: int
    headers: dict


async def _create_legacy_player(db, name: str) -> int:
    player = Player(name=name, role="player")
    db.add(player)
    await db.flush()
    db.add(PlayerAuth(player_id=player.id, pin_hash="test-hash-not-a-real-bcrypt-value"))
    await db.flush()
    return player.id


async def create_family(db, name: str = "Test Family") -> int:
    family = FamilyGroup(name=name, status="active")
    db.add(family)
    await db.flush()
    return family.id


async def create_actor(
    db,
    family_id: int,
    *,
    name: str = "actor",
    service_role: str | None = None,
    membership_status: str = "active",
) -> Actor:
    """Create a fully-linked legacy player -> account -> family membership,
    optionally granting a Doran SERVICE-scope role (participant/room_admin)."""
    player_id = await _create_legacy_player(db, name)
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    db.add(
        LegacyIdentityMapping(
            account_id=account.id,
            legacy_system="markpoint",
            legacy_identity_type="player_auth",
            legacy_identity_id=str(player_id),
            mapping_status="linked",
        )
    )
    membership = FamilyMembership(
        family_group_id=family_id,
        account_id=account.id,
        relationship="unknown",
        status=membership_status,
        joined_at=datetime.now(timezone.utc) if membership_status == "active" else None,
    )
    db.add(membership)
    await db.flush()
    if service_role is not None:
        role = (
            await db.execute(
                text(
                    "SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='doran' AND code=:code"
                ),
                {"code": service_role},
            )
        ).scalar_one()
        db.add(MembershipRoleAssignment(membership_id=membership.id, role_id=role))
    await db.commit()
    return Actor(
        player_id=player_id,
        account_id=account.id,
        membership_id=membership.id,
        family_id=family_id,
        headers=auth_headers(player_id, name),
    )


async def create_bare_membership(db, family_id: int, name: str = "filler") -> int:
    """A family member with no legacy auth chain - usable as an add_participant
    target but cannot itself authenticate. Keeps bulk fixture setup cheap."""
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family_id,
        account_id=account.id,
        relationship="unknown",
        status="active",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.commit()
    return membership.id


async def set_subscription(db, family_id: int, status: str = "active") -> None:
    sub = ServiceSubscription(
        family_group_id=family_id,
        service_code="doran",
        status=status,
        started_at=datetime.now(timezone.utc) if status == "active" else None,
    )
    db.add(sub)
    await db.commit()


async def run_concurrent(factories: list[Callable[[], Awaitable]]) -> list:
    """Release every coroutine from the same asyncio.Event so their requests
    genuinely overlap instead of running strictly sequentially."""
    start = asyncio.Event()

    async def runner(factory):
        await start.wait()
        return await factory()

    tasks = [asyncio.create_task(runner(f)) for f in factories]
    await asyncio.sleep(0)
    start.set()
    return await asyncio.gather(*tasks, return_exceptions=True)


from app.domains.doran import service as doran_service  # noqa: E402


def service_headers(credential_id: str, secret: str) -> dict:
    return {"Authorization": f"Bearer {credential_id}.{secret}"}


@dataclass
class ServiceActor:
    principal_id: int
    credential_id: str
    secret: str
    headers: dict
    binding_id: int
    room_id: object


async def create_service_actor(
    db,
    family_id: int,
    *,
    service_code: str = "mission",
    name: str = "mission-service",
    allowed_actions: list[dict] | None = None,
) -> ServiceActor:
    """Issues a Service Principal and binds it to a brand-new SERVICE Room in
    the given Family, matching create_service_binding()'s Room-per-Binding
    design. Returns everything a test needs to authenticate and to know which
    Room it may publish into."""
    if allowed_actions is None:
        allowed_actions = [{"action_type": "mission_approved", "schema_version": 1}]
    principal, secret = await doran_service.create_service_principal(db, service_code, name)
    binding, room = await doran_service.create_service_binding(db, principal.id, family_id, allowed_actions)
    return ServiceActor(
        principal_id=principal.id,
        credential_id=principal.credential_id,
        secret=secret,
        headers=service_headers(principal.credential_id, secret),
        binding_id=binding.id,
        room_id=room.id,
    )


@pytest_asyncio.fixture
async def family_env(db, client):
    """One family, two linked actors: `admin` (Doran room_admin service role,
    can create/manage rooms) and `member` (Doran participant service role).
    Doran subscription active. Returns a dict for tests to extend."""
    family_id = await create_family(db)
    admin = await create_actor(db, family_id, name="admin", service_role="room_admin")
    member = await create_actor(db, family_id, name="member", service_role="participant")
    await set_subscription(db, family_id, "active")
    return {
        "family_id": family_id,
        "admin": admin,
        "member": member,
        "client": client,
        "db": db,
    }


@pytest_asyncio.fixture
async def service_env(family_env):
    """family_env plus one active Service Principal bound to a fresh SERVICE
    Room in that Family, allow-listing the 'mission_approved' v1 action."""
    actor = await create_service_actor(family_env["db"], family_env["family_id"])
    family_env["service"] = actor
    return family_env
