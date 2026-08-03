"""Wave 5 Core Gap Closeout — the seven Coverage Matrix rows, closed by test.

Each section names the Matrix row it exists to close. What these tests are
trying to catch, so a reader can judge whether they do it:

- **Guards are server-side.** Every guard is exercised through the service (and
  the HTTP matrix through real requests), never by asserting that a condition
  would have been checked.
- **Concurrency is run, not reasoned about.** Duplicate-prevention and
  bulk/single races use separate sessions and `asyncio.gather`, because a
  check-then-insert passes every single-threaded test ever written.
- **Family isolation is asserted from the other side too.** It is not enough
  that Family A sees its own rows; a second Family must be present and must
  stay unaffected, or the test cannot tell a scoped query from an unscoped one.
- **Append-only means the original row is re-read afterwards** and asserted
  unchanged, not merely that a new row appeared.
"""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text

from app.domains.family import auth_service
from app.domains.family.models import (
    Account,
    FamilyGroup,
    FamilyMembership,
    MembershipRoleAssignment,
    ServiceSubscription,
)
from app.domains.level_tier.service import calculate_level
from app.domains.level_tier.schema import LevelTierResponse
from app.domains.markpoint_target import service
from app.domains.markpoint_target.models import (
    MarkpointBalanceProjection,
    MarkpointFamilyConfig,
    MarkpointLedgerEntry,
    MarkpointMission,
    MarkpointMissionTemplate,
)

PASSWORD = "Str0ngPassw0rd!"


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


async def _family(db, name="core"):
    f = FamilyGroup(name=name, status="active")
    db.add(f)
    await db.flush()
    db.add(
        ServiceSubscription(
            family_group_id=f.id,
            service_code="markpoint",
            status="active",
            started_at=datetime.now(timezone.utc),
        )
    )
    await db.flush()
    return f


async def _member(db, family_id, name, *, status="active"):
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    member = FamilyMembership(
        family_group_id=family_id,
        account_id=account.id,
        relationship="unknown",
        status=status,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(member)
    await db.flush()
    return member


async def _grant(db, member, code):
    role = (
        await db.execute(
            text(
                "SELECT id FROM roles WHERE scope_type='SERVICE' "
                "AND service_code='markpoint' AND code=:code"
            ),
            {"code": code},
        )
    ).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=member.id, role_id=role))
    await db.commit()


async def _template(db, family_id, manager, assignee, **kw):
    defaults = dict(
        title="daily chore",
        reward_amount=5,
        cycle_type="daily",
        start_date=date(2026, 1, 1),
        end_date=None,
        day_of_week=None,
    )
    defaults.update(kw)
    return await service.create_template(
        db, family_id, manager, assignee_id=assignee.id, **defaults
    )


async def _token(db, client, account_id: int, username: str, device="dev-1") -> str:
    """A real Account credential + login, so the HTTP matrix exercises the token
    production actually issues rather than a hand-forged one."""
    await auth_service.create_credential(db, account_id, username, PASSWORD)
    await db.commit()
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": username, "password": PASSWORD, "device_id": device},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# MP-S04 — cycle configuration, Guard A, Guard B
# ===========================================================================


async def test_cycle_config_defaults_then_persists_per_family(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    await _grant(db, manager, "mission_manager")

    initial = await service.read_family_config(db, family.id, manager)
    assert initial["configured"] is False
    assert initial["cycle_type"] == service.DEFAULT_CYCLE

    saved = await service.update_family_config(
        db, family.id, manager, cycle_type="monthly", today=date(2026, 3, 15)
    )
    assert saved["configured"] is True and saved["cycle_type"] == "monthly"
    assert saved["effective_from"] == date(2026, 3, 1)
    assert saved["effective_to"] == date(2026, 3, 31)


async def test_one_family_config_does_not_move_another_familys_period(db):
    """The whole reason this is per-Family rather than the legacy global row."""
    a = await _family(db, "A")
    b = await _family(db, "B")
    ma = await _member(db, a.id, "ma")
    mb = await _member(db, b.id, "mb")
    await _grant(db, ma, "mission_manager")
    await _grant(db, mb, "mission_manager")

    await service.update_family_config(db, a.id, ma, cycle_type="yearly", today=date(2026, 5, 1))
    b_config = await service.read_family_config(db, b.id, mb)
    assert b_config["configured"] is False
    assert b_config["cycle_type"] == service.DEFAULT_CYCLE


async def test_guard_a_blocks_change_while_the_current_cycle_is_running(db):
    from fastapi import HTTPException

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    await _grant(db, manager, "mission_manager")

    await service.update_family_config(
        db, family.id, manager, cycle_type="monthly", today=date(2026, 3, 10)
    )
    # Still inside March: refused, with the remaining days stated.
    with pytest.raises(HTTPException) as exc:
        await service.update_family_config(
            db, family.id, manager, cycle_type="weekly", today=date(2026, 3, 20)
        )
    assert exc.value.status_code == 409
    assert "2026-03-31" in exc.value.detail

    # April: the March period has ended, so the change is allowed.
    changed = await service.update_family_config(
        db, family.id, manager, cycle_type="weekly", today=date(2026, 4, 1)
    )
    assert changed["cycle_type"] == "weekly"


async def test_guard_a_does_not_block_a_non_cycle_field(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    await _grant(db, manager, "mission_manager")
    await service.update_family_config(
        db, family.id, manager, cycle_type="monthly", today=date(2026, 3, 10)
    )
    # A label has no effect on period boundaries, so blocking it would make the
    # guard feel arbitrary without making anything safer.
    renamed = await service.update_family_config(
        db, family.id, manager, display_name="우리집 규칙", today=date(2026, 3, 20)
    )
    assert renamed["display_name"] == "우리집 규칙"
    assert renamed["cycle_type"] == "monthly"


async def test_guard_b_blocks_change_while_an_active_template_exists(db):
    from fastapi import HTTPException

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    template = await _template(db, family.id, manager, child)

    with pytest.raises(HTTPException) as exc:
        await service.update_family_config(
            db, family.id, manager, cycle_type="monthly", today=date(2026, 3, 10)
        )
    assert exc.value.status_code == 409
    assert "템플릿" in exc.value.detail

    await service.deactivate_template(db, family.id, manager, template.id)
    ok = await service.update_family_config(
        db, family.id, manager, cycle_type="monthly", today=date(2026, 3, 10)
    )
    assert ok["cycle_type"] == "monthly"


async def test_guard_b_is_scoped_to_the_familys_own_templates(db):
    """Family A's template must never block Family B — the failure this
    would-be-global guard is most likely to have."""
    a = await _family(db, "A")
    b = await _family(db, "B")
    ma = await _member(db, a.id, "ma")
    ca = await _member(db, a.id, "ca")
    mb = await _member(db, b.id, "mb")
    await _grant(db, ma, "mission_manager")
    await _grant(db, mb, "mission_manager")
    await _template(db, a.id, ma, ca)  # ACTIVE template in A only

    changed = await service.update_family_config(
        db, b.id, mb, cycle_type="quarterly", today=date(2026, 3, 10)
    )
    assert changed["cycle_type"] == "quarterly"


async def test_no_force_override_exists(db):
    """No approved contract defines one, so none is offered — an override is
    the natural place for a guard to quietly stop meaning anything."""
    assert not any(
        name for name in dir(service) if "override" in name.lower() or "force" in name.lower()
    )


async def test_unsupported_cycle_value_is_rejected(db):
    from fastapi import HTTPException

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    await _grant(db, manager, "mission_manager")
    with pytest.raises(HTTPException) as exc:
        await service.update_family_config(db, family.id, manager, cycle_type="fortnightly")
    assert exc.value.status_code == 422
    # The value set is the legacy one; `get_cycle_range` can only compute
    # periods for these six.
    assert set(service.SUPPORTED_CYCLES) == {
        "daily", "weekly", "biweekly", "monthly", "quarterly", "yearly"
    }


# ===========================================================================
# MP-M03 — rolling materialization
# ===========================================================================


def test_rolling_window_preserves_the_implemented_legacy_behaviour():
    """`today` → the Sunday after this week's Sunday.

    Legacy `get_rolling_window`'s own docstring contradicts its code: it claims
    a Monday yields 7 days ("이번 주만") while the code always adds a further
    week. The code is preserved and the contradiction is reported, because
    adopting the docstring would change how many missions every Monday
    generates.
    """
    monday = date(2026, 3, 30)
    saturday = date(2026, 4, 4)
    assert service.rolling_window(monday) == (monday, date(2026, 4, 12))  # 14 days
    assert service.rolling_window(saturday) == (saturday, date(2026, 4, 12))  # 9 days


async def test_materialization_targets_only_the_templates_named_assignee(db):
    """Never every ACTIVE membership, never everyone with Markpoint access,
    never the FamilyAdmin by default."""
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    named = await _member(db, family.id, "named")
    bystander = await _member(db, family.id, "bystander")
    await _grant(db, manager, "mission_manager")
    await _template(db, family.id, manager, named, cycle_type="daily")

    result = await service.materialize_rolling_window(
        db, family.id, manager, today=date(2026, 3, 30)
    )
    assert result["missions_created"] > 0

    assignees = {
        m.assignee_membership_id
        for m in (await db.execute(select(MarkpointMission))).scalars()
    }
    assert assignees == {named.id}
    assert bystander.id not in assignees
    assert manager.id not in assignees


async def test_materialization_is_idempotent_across_overlapping_windows(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    await _template(db, family.id, manager, child, cycle_type="daily")

    first = await service.materialize_rolling_window(db, family.id, manager, today=date(2026, 3, 30))
    second = await service.materialize_rolling_window(db, family.id, manager, today=date(2026, 3, 30))
    assert second["missions_created"] == 0
    assert second["missions_skipped_existing"] == first["missions_created"]

    total = (await db.execute(select(text("count(*)")).select_from(MarkpointMission))).scalar_one()
    assert total == first["missions_created"]


async def test_concurrent_materialization_creates_no_duplicates(db):
    """A check-then-insert passes every single-threaded test; this is the one
    that would catch it."""
    from app.database import AsyncSessionLocal

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    template = await _template(db, family.id, manager, child, cycle_type="daily")
    await db.commit()

    async def run():
        async with AsyncSessionLocal() as s:
            actor = await s.get(FamilyMembership, manager.id)
            return await service.materialize_rolling_window(
                s, family.id, actor, template_id=template.id, today=date(2026, 3, 30)
            )

    results = await asyncio.gather(run(), run(), return_exceptions=True)
    assert any(not isinstance(r, Exception) for r in results), results

    rows = list((await db.execute(select(MarkpointMission))).scalars())
    pairs = [(m.template_id, m.scheduled_for) for m in rows]
    assert len(pairs) == len(set(pairs)), "duplicate (template, date) materialized"


async def test_materialization_skips_inactive_templates_and_respects_end_date(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")

    inactive = await _template(db, family.id, manager, child, title="off", cycle_type="daily")
    await service.deactivate_template(db, family.id, manager, inactive.id)
    # Ends inside the window: must not generate past its own life.
    await _template(
        db, family.id, manager, child, title="ends", cycle_type="daily",
        start_date=date(2026, 3, 30), end_date=date(2026, 4, 1),
    )

    result = await service.materialize_rolling_window(db, family.id, manager, today=date(2026, 3, 30))
    rows = list((await db.execute(select(MarkpointMission))).scalars())
    assert {m.title for m in rows} == {"ends"}
    assert max(m.scheduled_for for m in rows) == date(2026, 4, 1)
    assert result["missions_created"] == 3


async def test_materialization_does_not_touch_another_family(db):
    a = await _family(db, "A")
    b = await _family(db, "B")
    ma = await _member(db, a.id, "ma")
    ca = await _member(db, a.id, "ca")
    mb = await _member(db, b.id, "mb")
    cb = await _member(db, b.id, "cb")
    await _grant(db, ma, "mission_manager")
    await _grant(db, mb, "mission_manager")
    await _template(db, a.id, ma, ca, cycle_type="daily")
    await _template(db, b.id, mb, cb, cycle_type="daily")

    await service.materialize_rolling_window(db, a.id, ma, today=date(2026, 3, 30))
    families = {
        m.family_group_id for m in (await db.execute(select(MarkpointMission))).scalars()
    }
    assert families == {a.id}


async def test_weekday_pinned_template_generates_only_on_that_weekday(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    # Wednesday == 2
    await _template(db, family.id, manager, child, cycle_type="weekly", day_of_week=2)

    await service.materialize_rolling_window(db, family.id, manager, today=date(2026, 3, 30))
    rows = list((await db.execute(select(MarkpointMission))).scalars())
    assert rows and all(m.scheduled_for.weekday() == 2 for m in rows)


# ===========================================================================
# MP-M04 / MP-P02 — weekly detail and daily/weekly projection
# ===========================================================================


async def test_weekly_detail_reports_every_date_including_empty_ones(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    anchor = date(2026, 4, 1)  # Wednesday
    await service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="a", scheduled_for=anchor, reward_amount=5
    )

    detail = await service.own_weekly_detail(db, family.id, child, anchor=anchor)
    assert detail["period_start"] == date(2026, 3, 30)
    assert detail["period_end"] == date(2026, 4, 5)
    # An empty day is explicit rather than inferred from a gap.
    assert len(detail["days"]) == 7
    assert [d["date"] for d in detail["days"]][0] == date(2026, 3, 30)
    assert detail["remaining_missions"] == 1
    assert detail["expected_points"] == 5


async def test_projection_derives_every_figure_from_the_ledger(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    await _grant(db, manager, "point_admin")
    anchor = date.today()

    mission = await service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="m", scheduled_for=anchor, reward_amount=30
    )
    await service.submit_mission(db, family.id, child, mission.id)
    await service.approve_mission(db, family.id, manager, mission.id)
    await service.adjust_points(db, family.id, manager, child.id, -12, "penalty", "p1")

    proj = await service.own_projection(db, family.id, child, anchor=anchor)
    assert proj["today_earned"] == 30
    # Debits are stored negative and reported as a positive magnitude, so a
    # caller never has to remember the sign convention.
    assert proj["today_deducted"] == 12
    assert proj["weekly_earned"] == 30
    assert proj["weekly_deducted"] == 12
    assert proj["current_balance"] == 18
    assert proj["lifetime_earned"] == 30
    assert proj["lifetime_spent"] == 12


async def test_projection_period_follows_the_configured_cycle(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    await service.update_family_config(
        db, family.id, manager, cycle_type="monthly", today=date(2026, 3, 10)
    )
    proj = await service.own_projection(db, family.id, child, anchor=date(2026, 3, 20))
    assert proj["cycle_type"] == "monthly"
    assert (proj["period_start"], proj["period_end"]) == (date(2026, 3, 1), date(2026, 3, 31))


async def test_projection_reflects_a_reversal(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    anchor = date.today()
    mission = await service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="m", scheduled_for=anchor, reward_amount=40
    )
    await service.submit_mission(db, family.id, child, mission.id)
    await service.approve_mission(db, family.id, manager, mission.id)
    await service.reverse_mission_reward(db, family.id, manager, mission.id, "mistake")

    proj = await service.own_projection(db, family.id, child, anchor=anchor)
    assert proj["current_balance"] == 0
    assert proj["lifetime_earned"] == 0, "a reversed reward must not keep inflating lifetime EXP"


async def test_projection_isolates_date_boundaries(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")
    today = date.today()
    # A yesterday-dated entry, inserted directly with its own `occurred_at`.
    #
    # An earlier draft created it via the service and then backdated it with an
    # UPDATE. The database refused: `markpoint ledger is append-only` comes
    # from a trigger, so the append-only guarantee is enforced by the schema
    # and not merely by the service layer. That refusal is the product working,
    # so the test was changed rather than the guard.
    db.add(
        MarkpointLedgerEntry(
            family_group_id=family.id,
            family_membership_id=child.id,
            amount=10,
            entry_type="MANUAL_CREDIT",
            source_type="manual_adjustment",
            source_identifier="yesterday",
            idempotency_key="manual:yesterday",
            created_by_membership_id=manager.id,
            occurred_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
    )
    await db.commit()
    await service.adjust_points(db, family.id, manager, child.id, 7, "now", "t2")

    proj = await service.own_projection(db, family.id, child, anchor=today)
    assert proj["today_earned"] == 7


# ---------------------------------------------------------------------------
# RE-QA-F-003 regression — MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-
# REMEDIATION-001. Independent Re-QA reproduced `today_earned`/
# `today_deducted` measuring 0 instead of the ledger's real total: `anchor`
# defaulted to the server process's OS-local `date.today()` while
# `_sum_ledger` compared `occurred_at` (UTC) under the DB session's own UTC
# date, silently disagreeing for roughly nine hours out of every day. Fixed
# by anchoring both sides to the Family-facing KST business calendar date
# (`service.KST`, the same convention `daily_point/service.py` already
# uses), never the ambient server timezone. These tests use explicit,
# deterministic UTC timestamps chosen to fall on *different* UTC and KST
# calendar dates, so they fail on the old behavior and pass on the fix
# regardless of what real time they happen to run at -- unlike the two
# tests above, which only failed during an actual live UTC/KST divergence
# window.
# ---------------------------------------------------------------------------


def _utc_at_kst_date(kst_date: date, kst_hour: int) -> datetime:
    """A UTC instant that falls on `kst_date` at `kst_hour` local KST time."""
    naive = datetime(kst_date.year, kst_date.month, kst_date.day, kst_hour, 0, 0)
    return naive.replace(tzinfo=service.KST).astimezone(timezone.utc)


async def test_projection_kst_boundary_independent_of_server_local_timezone(db):
    """00:30 KST is still 15:30 the previous UTC day -- a naive `func.date()`
    on the raw UTC timestamp would attribute this entry to the wrong
    calendar day. Chosen deterministically, not tied to the real clock."""
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")

    kst_today = date(2026, 3, 11)
    kst_yesterday = date(2026, 3, 10)
    early_morning_kst = _utc_at_kst_date(kst_today, 0)  # 2026-03-10 15:00 UTC
    assert early_morning_kst.date() == kst_yesterday, "sanity: this instant really is the previous UTC calendar day"

    db.add(
        MarkpointLedgerEntry(
            family_group_id=family.id,
            family_membership_id=child.id,
            amount=15,
            entry_type="MANUAL_CREDIT",
            source_type="manual_adjustment",
            source_identifier="kst-midnight-entry",
            idempotency_key="manual:kst-midnight",
            created_by_membership_id=manager.id,
            occurred_at=early_morning_kst,
        )
    )
    await db.commit()

    proj_kst_today = await service.own_projection(db, family.id, child, anchor=kst_today)
    assert proj_kst_today["today_earned"] == 15, "the entry belongs to its KST calendar day, not the UTC one"

    proj_kst_yesterday = await service.own_projection(db, family.id, child, anchor=kst_yesterday)
    assert proj_kst_yesterday["today_earned"] == 0, "the entry must not double-count on the UTC-adjacent day"


async def test_projection_different_anchor_dates_isolate_correctly(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")

    day1, day2 = date(2026, 5, 4), date(2026, 5, 5)
    db.add(MarkpointLedgerEntry(
        family_group_id=family.id, family_membership_id=child.id, amount=20,
        entry_type="MANUAL_CREDIT", source_type="manual_adjustment", source_identifier="day1",
        idempotency_key="manual:day1", created_by_membership_id=manager.id,
        occurred_at=_utc_at_kst_date(day1, 12),
    ))
    db.add(MarkpointLedgerEntry(
        family_group_id=family.id, family_membership_id=child.id, amount=9,
        entry_type="MANUAL_CREDIT", source_type="manual_adjustment", source_identifier="day2",
        idempotency_key="manual:day2", created_by_membership_id=manager.id,
        occurred_at=_utc_at_kst_date(day2, 12),
    ))
    await db.commit()

    assert (await service.own_projection(db, family.id, child, anchor=day1))["today_earned"] == 20
    assert (await service.own_projection(db, family.id, child, anchor=day2))["today_earned"] == 9


async def test_projection_repeated_calls_same_db_return_identical_figures(db):
    """Same ledger, same anchor, called twice in a row -- must not depend on
    a persisted/cached figure from the first call (RE-QA-F-003's own
    symptom: correct once, then wrong on a subsequent read)."""
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")
    # `adjust_points` records `occurred_at` as the real current instant (the
    # model's own `server_default=func.now()`), so the anchor here is left
    # to its own default (real "today" in KST) rather than a fixed date that
    # would never match a real ledger write.
    await service.adjust_points(db, family.id, manager, child.id, 25, "reward", "once")

    first = await service.own_projection(db, family.id, child)
    second = await service.own_projection(db, family.id, child)
    assert first == second
    assert second["today_earned"] == 25


async def test_projection_cross_family_isolation_for_today_earned(db):
    family_a = await _family(db, "family-a")
    family_b = await _family(db, "family-b")
    manager_a = await _member(db, family_a.id, "manager-a")
    child_a = await _member(db, family_a.id, "child-a")
    manager_b = await _member(db, family_b.id, "manager-b")
    child_b = await _member(db, family_b.id, "child-b")
    await _grant(db, manager_a, "point_admin")
    await _grant(db, manager_b, "point_admin")

    anchor = date(2026, 7, 15)
    db.add(MarkpointLedgerEntry(
        family_group_id=family_a.id, family_membership_id=child_a.id, amount=50,
        entry_type="MANUAL_CREDIT", source_type="manual_adjustment", source_identifier="a",
        idempotency_key="manual:a", created_by_membership_id=manager_a.id,
        occurred_at=_utc_at_kst_date(anchor, 12),
    ))
    await db.commit()

    proj_a = await service.own_projection(db, family_a.id, child_a, anchor=anchor)
    proj_b = await service.own_projection(db, family_b.id, child_b, anchor=anchor)
    assert proj_a["today_earned"] == 50
    assert proj_b["today_earned"] == 0, "Family B must never see Family A's ledger entries"


async def test_projection_empty_ledger_returns_zero_not_error(db):
    family = await _family(db)
    child = await _member(db, family.id, "child")
    proj = await service.own_projection(db, family.id, child, anchor=date(2026, 9, 1))
    assert proj["today_earned"] == 0
    assert proj["today_deducted"] == 0
    assert proj["current_balance"] == 0
    assert proj["lifetime_earned"] == 0
    assert proj["lifetime_spent"] == 0


# ===========================================================================
# MP-P03 — deduction correction (append-only)
# ===========================================================================


async def test_deduction_correction_reverses_and_replaces_without_editing(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")

    original = await service.adjust_points(db, family.id, manager, child.id, -100, "broke a plate", "d1")
    result = await service.correct_deduction(
        db, family.id, manager, entry_id=original.id, new_amount=-80, reason="overcharged"
    )

    rows = list(
        (await db.execute(select(MarkpointLedgerEntry).order_by(MarkpointLedgerEntry.id))).scalars()
    )
    assert [r.amount for r in rows] == [-100, 100, -80]
    # The original is re-read and asserted untouched — a new row appearing is
    # not by itself evidence that the old one survived intact.
    assert rows[0].id == original.id and rows[0].amount == -100 and rows[0].reason == "broke a plate"
    assert rows[1].reversal_of_entry_id == original.id
    assert result["reversal_entry_id"] == rows[1].id
    assert result["replacement_entry_id"] == rows[2].id

    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == -80


async def test_deduction_cancellation_is_reversal_only(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")

    original = await service.adjust_points(db, family.id, manager, child.id, -50, "wrong", "d1")
    result = await service.correct_deduction(
        db, family.id, manager, entry_id=original.id, new_amount=None, reason="cancelled"
    )
    assert result["replacement_entry_id"] is None
    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == 0


async def test_a_deduction_cannot_be_corrected_twice(db):
    from fastapi import HTTPException

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")
    original = await service.adjust_points(db, family.id, manager, child.id, -30, "x", "d1")
    await service.correct_deduction(db, family.id, manager, entry_id=original.id, new_amount=-10, reason="fix")

    with pytest.raises(HTTPException) as exc:
        await service.correct_deduction(
            db, family.id, manager, entry_id=original.id, new_amount=-5, reason="again"
        )
    assert exc.value.status_code == 409


async def test_deduction_history_exposes_the_correction_lineage(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")
    original = await service.adjust_points(db, family.id, manager, child.id, -60, "first", "d1")
    await service.correct_deduction(db, family.id, manager, entry_id=original.id, new_amount=-20, reason="fix")

    history = await service.deduction_history(db, family.id, child)
    by_id = {h["id"]: h for h in history}
    assert by_id[original.id]["corrected"] is True
    assert any(h["reversal_of_entry_id"] == original.id for h in history)


async def test_correcting_another_familys_entry_is_not_found(db):
    from fastapi import HTTPException

    a = await _family(db, "A")
    b = await _family(db, "B")
    ma = await _member(db, a.id, "ma")
    ca = await _member(db, a.id, "ca")
    mb = await _member(db, b.id, "mb")
    await _grant(db, ma, "point_admin")
    await _grant(db, mb, "point_admin")
    entry = await service.adjust_points(db, a.id, ma, ca.id, -10, "x", "d1")

    with pytest.raises(HTTPException) as exc:
        await service.correct_deduction(db, b.id, mb, entry_id=entry.id, new_amount=-5, reason="nope")
    # 404 rather than 403: confirming the id exists elsewhere is a disclosure.
    assert exc.value.status_code == 404


async def test_a_mission_reward_is_not_correctable_as_a_deduction(db):
    from fastapi import HTTPException

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    await _grant(db, manager, "point_admin")
    mission = await service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="m", scheduled_for=date.today(), reward_amount=9
    )
    await service.submit_mission(db, family.id, child, mission.id)
    await service.approve_mission(db, family.id, manager, mission.id)
    reward = (
        await db.execute(select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.amount == 9))
    ).scalars().one()

    with pytest.raises(HTTPException) as exc:
        await service.correct_deduction(db, family.id, manager, entry_id=reward.id, new_amount=-1, reason="x")
    assert exc.value.status_code == 409


# ===========================================================================
# MP-L01 — level boundary matrix
# ===========================================================================


def _tiers(pairs):
    return [
        LevelTierResponse(
            id=i + 1, job_code="COMMON", level=i + 1, title=title, required_points=pts,
            icon=None, color=None,
        )
        for i, (pts, title) in enumerate(pairs)
    ]


@pytest.mark.parametrize(
    "total,expected_level,note",
    [
        (0, 1, "floor"),
        (-25, 1, "negative balance never drops below the first tier"),
        (99, 1, "just below the second tier"),
        (100, 2, "exact match on a defined tier"),
        (150, 2, "between tiers"),
        (299, 2, "just below the last tier"),
        (300, 3, "exact match on the LAST defined tier"),
        # Auto-extension is `extra_levels = excess // last_gap`, and last_gap
        # here is 300-100=200. So 400 is only 100 past the last tier — half a
        # gap — and stays level 3 with a generated title. An earlier draft of
        # this table expected 4, 5 and 48601; that was my arithmetic, not a
        # product defect, and the real values are pinned instead.
        (400, 3, "half a gap past the last tier — still level 3, generated title"),
        (500, 4, "exactly one full gap past"),
        (700, 5, "two full gaps past"),
        (10_000_000, 50_001, "very large value stays computable"),
    ],
)
def test_level_boundary_matrix(total, expected_level, note):
    """The legacy `calculate_level` contract, pinned at every boundary.

    `total` is **lifetime earned**, not current balance — the two diverge the
    moment anything is spent, and using the balance would make a level fall
    when a child spends their points.
    """
    tiers = _tiers([(0, "씨앗"), (100, "새싹"), (300, "나무")])
    info = calculate_level(total, tiers)
    assert info.level == expected_level, note


def test_level_exact_last_tier_keeps_its_defined_title():
    """`excess == 0` is its own branch in the legacy algorithm: landing exactly
    on the last defined tier keeps the curated title rather than switching to
    the generated one."""
    tiers = _tiers([(0, "씨앗"), (100, "새싹"), (300, "나무")])
    exact = calculate_level(300, tiers)
    assert exact.title == "나무" and "자동" not in exact.title
    beyond = calculate_level(301, tiers)
    assert "자동" in beyond.title


def test_level_progress_is_clamped_and_thresholds_are_ordered():
    tiers = _tiers([(0, "씨앗"), (100, "새싹"), (300, "나무")])
    for total in (0, 50, 100, 299, 300, 450, 1000):
        info = calculate_level(total, tiers)
        assert 0 <= info.progress_percent <= 100
        assert info.next_threshold > info.current_threshold


def test_level_with_no_tiers_falls_back_without_crashing():
    info = calculate_level(500, [])
    assert info.level == 1 and info.next_threshold == 100


async def test_level_uses_lifetime_earned_and_survives_a_reversal(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    await _grant(db, manager, "point_admin")

    mission = await service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="m", scheduled_for=date.today(), reward_amount=120
    )
    await service.submit_mission(db, family.id, child, mission.id)
    await service.approve_mission(db, family.id, manager, mission.id)
    balance, _ = await service.own_level(db, family.id, child)
    assert balance.lifetime_earned == 120

    # Spending must not reduce lifetime earned — otherwise a level would fall
    # when a child uses their points, which is not the contract.
    await service.adjust_points(db, family.id, manager, child.id, -50, "spend", "s1")
    balance, _ = await service.own_level(db, family.id, child)
    assert balance.lifetime_earned == 120 and balance.current_balance == 70

    # A reversal *does* reduce it: the reward is being undone, not spent.
    await service.reverse_mission_reward(db, family.id, manager, mission.id, "mistake")
    balance, _ = await service.own_level(db, family.id, child)
    assert balance.lifetime_earned == 0


# ===========================================================================
# MP-A01 — admin filters and bulk approval
# ===========================================================================


async def _pending(db, family_id, manager, child, title, day_offset=0, reward=10):
    mission = await service.create_mission(
        db, family_id, manager,
        assignee_id=child.id, title=title,
        scheduled_for=date.today() + timedelta(days=day_offset), reward_amount=reward,
    )
    await service.submit_mission(db, family_id, child, mission.id)
    return mission


async def test_admin_filters_narrow_within_the_family_only(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    one = await _member(db, family.id, "one")
    two = await _member(db, family.id, "two")
    await _grant(db, manager, "mission_manager")
    await _pending(db, family.id, manager, one, "a")
    await _pending(db, family.id, manager, two, "b", day_offset=3)

    other = await _family(db, "other")
    om = await _member(db, other.id, "om")
    oc = await _member(db, other.id, "oc")
    await _grant(db, om, "mission_manager")
    await _pending(db, other.id, om, oc, "foreign")

    everything = await service.admin_list_missions(db, family.id, manager)
    assert {m.title for m in everything} == {"a", "b"}, "another Family must not appear"

    by_assignee = await service.admin_list_missions(db, family.id, manager, assignee_membership_id=one.id)
    assert {m.title for m in by_assignee} == {"a"}

    by_status = await service.admin_list_missions(db, family.id, manager, mission_status="completed")
    assert by_status == []

    by_date = await service.admin_list_missions(
        db, family.id, manager, date_from=date.today() + timedelta(days=1)
    )
    assert {m.title for m in by_date} == {"b"}


async def test_bulk_approval_pays_each_reward_exactly_once(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    a = await _pending(db, family.id, manager, child, "a", reward=10)
    b = await _pending(db, family.id, manager, child, "b", day_offset=1, reward=20)

    result = await service.bulk_approve_missions(db, family.id, manager, [a.id, b.id, a.id])
    assert result["requested"] == 2  # duplicate id collapsed
    assert set(result["approved"]) == {a.id, b.id}

    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == 30
    rewards = list(
        (
            await db.execute(
                select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.entry_type == "MISSION_REWARD")
            )
        ).scalars()
    )
    assert len(rewards) == 2


async def test_bulk_approval_is_all_or_nothing_on_an_ineligible_mission(db):
    from fastapi import HTTPException

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    good = await _pending(db, family.id, manager, child, "good")
    # `active` — never submitted, so not approvable.
    bad = await service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="bad",
        scheduled_for=date.today(), reward_amount=5,
    )
    # Capture the ids *before* the rollback. A rollback expires every attached
    # instance, so reading `good.id` afterwards triggers a lazy reload and
    # raises `MissingGreenlet` under the async driver — the same trap that
    # broke `record_failure` in Wave 3.
    good_id, bad_id = good.id, bad.id

    with pytest.raises(HTTPException) as exc:
        await service.bulk_approve_missions(db, family.id, manager, [good_id, bad_id])
    assert exc.value.status_code == 409
    await db.rollback()

    # No half-applied batch: the eligible mission was not paid either.
    assert (await db.execute(select(MarkpointLedgerEntry))).scalars().all() == []
    # Read the status with a fresh query rather than `db.get` on an instance the
    # rollback expired — touching an expired attribute triggers a lazy load and
    # raises `MissingGreenlet` under the async driver.
    status_after = (
        await db.execute(
            text("SELECT status FROM markpoint_missions WHERE id = :id"), {"id": good_id}
        )
    ).scalar_one()
    assert status_after == "pending_approval"


async def test_bulk_approval_refuses_a_foreign_mission_as_not_found(db):
    from fastapi import HTTPException

    a = await _family(db, "A")
    b = await _family(db, "B")
    ma = await _member(db, a.id, "ma")
    ca = await _member(db, a.id, "ca")
    mb = await _member(db, b.id, "mb")
    cb = await _member(db, b.id, "cb")
    await _grant(db, ma, "mission_manager")
    await _grant(db, mb, "mission_manager")
    mine = await _pending(db, a.id, ma, ca, "mine")
    foreign = await _pending(db, b.id, mb, cb, "foreign")

    with pytest.raises(HTTPException) as exc:
        await service.bulk_approve_missions(db, a.id, ma, [mine.id, foreign.id])
    assert exc.value.status_code == 404
    await db.rollback()
    assert (await db.execute(select(MarkpointLedgerEntry))).scalars().all() == []


async def test_bulk_and_single_approval_race_pays_once(db):
    from app.database import AsyncSessionLocal

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "contested", reward=15)
    await db.commit()

    async def bulk():
        async with AsyncSessionLocal() as s:
            actor = await s.get(FamilyMembership, manager.id)
            return await service.bulk_approve_missions(s, family.id, actor, [mission.id])

    async def single():
        async with AsyncSessionLocal() as s:
            actor = await s.get(FamilyMembership, manager.id)
            return await service.approve_mission(s, family.id, actor, mission.id)

    results = await asyncio.gather(bulk(), single(), return_exceptions=True)
    assert any(not isinstance(r, Exception) for r in results), results

    rewards = list(
        (
            await db.execute(
                select(MarkpointLedgerEntry).where(
                    MarkpointLedgerEntry.source_identifier == str(mission.id)
                )
            )
        ).scalars()
    )
    assert len(rewards) == 1, "the reward must be paid exactly once under a race"
    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == 15


async def test_bulk_approval_of_an_already_completed_mission_is_skipped_not_repaid(db):
    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "once", reward=25)
    await service.approve_mission(db, family.id, manager, mission.id)

    result = await service.bulk_approve_missions(db, family.id, manager, [mission.id])
    assert result["skipped_already_completed"] == [mission.id]
    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == 25


# ===========================================================================
# Transaction / failure injection
# ===========================================================================


async def test_outbox_and_ledger_commit_or_roll_back_together(db):
    """The Outbox row is only durable if the reward is. A rollback after the
    ledger insert must leave neither."""
    from app.database import AsyncSessionLocal

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "rollback", reward=8)
    await db.commit()

    async with AsyncSessionLocal() as s:
        actor = await s.get(FamilyMembership, manager.id)
        m = await s.get(MarkpointMission, mission.id)
        entry, _ = await service._entry(
            s, family_id=family.id, member_id=child.id, amount=8,
            entry_type="MISSION_REWARD", source_type="mission_approval",
            source_identifier=str(m.id), idempotency_key=f"mission-approved:{m.id}",
            actor_id=actor.id,
        )
        m.status = "completed"
        await s.rollback()  # forced post-persist failure

    # Seen from a second session: nothing survived.
    assert (await db.execute(select(MarkpointLedgerEntry))).scalars().all() == []
    assert (
        await db.execute(text("SELECT count(*) FROM service_outbox_events WHERE owner_service='markpoint'"))
    ).scalar_one() == 0
    refreshed = await db.get(MarkpointMission, mission.id)
    await db.refresh(refreshed)
    assert refreshed.status == "pending_approval"


async def test_approve_and_cancel_race_leaves_a_consistent_balance(db):
    from app.database import AsyncSessionLocal

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "race", reward=12)
    await db.commit()

    async def approve():
        async with AsyncSessionLocal() as s:
            actor = await s.get(FamilyMembership, manager.id)
            return await service.approve_mission(s, family.id, actor, mission.id)

    async def cancel():
        async with AsyncSessionLocal() as s:
            actor = await s.get(FamilyMembership, manager.id)
            return await service.cancel_mission(s, family.id, actor, mission.id, "stop")

    await asyncio.gather(approve(), cancel(), return_exceptions=True)

    rewards = list(
        (
            await db.execute(
                select(MarkpointLedgerEntry).where(
                    MarkpointLedgerEntry.source_identifier == str(mission.id),
                    MarkpointLedgerEntry.entry_type == "MISSION_REWARD",
                )
            )
        ).scalars()
    )
    assert len(rewards) <= 1
    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().first()
    if balance is not None:
        reversals = list(
            (
                await db.execute(
                    select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.entry_type == "REVERSAL")
                )
            ).scalars()
        )
        expected = sum(r.amount for r in rewards) + sum(r.amount for r in reversals)
        assert balance.current_balance == expected


async def test_concurrent_identical_deduction_correction_applies_once(db):
    from app.database import AsyncSessionLocal

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "point_admin")
    original = await service.adjust_points(db, family.id, manager, child.id, -40, "x", "d1")
    await db.commit()

    async def correct():
        async with AsyncSessionLocal() as s:
            actor = await s.get(FamilyMembership, manager.id)
            return await service.correct_deduction(
                s, family.id, actor, entry_id=original.id, new_amount=-10, reason="fix"
            )

    await asyncio.gather(correct(), correct(), return_exceptions=True)

    reversals = list(
        (
            await db.execute(
                select(MarkpointLedgerEntry).where(
                    MarkpointLedgerEntry.reversal_of_entry_id == original.id
                )
            )
        ).scalars()
    )
    assert len(reversals) == 1, "the idempotency key must collapse a concurrent double-correction"


# ===========================================================================
# Wagle relay — Markpoint's side of the boundary
# ===========================================================================


async def test_markpoint_never_touches_a_wagle_table_directly(db):
    """The relay goes through the Outbox and the adapter. Markpoint importing a
    Wagle model would make two services share one schema."""
    import pathlib

    root = pathlib.Path(service.__file__).parent
    for path in root.glob("*.py"):
        source = path.read_text()
        assert "from app.domains.wagle.models" not in source, path
        assert "wagle_messages" not in source, path
        assert "wagle_rooms" not in source, path


async def test_relay_failure_never_rolls_back_an_approved_mission(db):
    """A delivery failure is not a data-loss event: the reward and the ledger
    entry stay, and only the Outbox row carries the failure state."""
    from app.domains.service_outbox import service as outbox_service
    from app.domains.service_outbox.models import ServiceOutboxEvent

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "relayed", reward=14)
    await service.approve_mission(db, family.id, manager, mission.id)

    event = (
        await db.execute(
            select(ServiceOutboxEvent).where(ServiceOutboxEvent.owner_service == "markpoint")
        )
    ).scalars().one()
    await outbox_service.record_failure(db, event, "relay_transient")

    await db.refresh(event)
    assert event.status == "PENDING" and event.attempt_count == 1
    assert event.locked_until is None, "a failed row must not stay leased"

    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == 14
    refreshed = await db.get(MarkpointMission, mission.id)
    await db.refresh(refreshed)
    assert refreshed.status == "completed"


async def test_repeated_relay_failure_reaches_a_terminal_state_without_touching_markpoint(db):
    from app.domains.service_outbox import service as outbox_service
    from app.domains.service_outbox.models import ServiceOutboxEvent

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "dead", reward=6)
    await service.approve_mission(db, family.id, manager, mission.id)

    event = (
        await db.execute(
            select(ServiceOutboxEvent).where(ServiceOutboxEvent.owner_service == "markpoint")
        )
    ).scalars().one()
    for _ in range(outbox_service.MAX_ATTEMPTS):
        await outbox_service.record_failure(db, event, "relay_down")
    await db.refresh(event)
    assert event.status == "DEAD"

    balance = (await db.execute(select(MarkpointBalanceProjection))).scalars().one()
    assert balance.current_balance == 6, "a dead relay row must not reverse the reward"


async def test_outbox_event_is_deduplicated_by_source_event_id(db):
    from app.domains.service_outbox.models import ServiceOutboxEvent

    family = await _family(db)
    manager = await _member(db, family.id, "manager")
    child = await _member(db, family.id, "child")
    await _grant(db, manager, "mission_manager")
    mission = await _pending(db, family.id, manager, child, "dedup", reward=4)
    await service.approve_mission(db, family.id, manager, mission.id)
    await service.approve_mission(db, family.id, manager, mission.id)

    events = list(
        (
            await db.execute(
                select(ServiceOutboxEvent).where(ServiceOutboxEvent.owner_service == "markpoint")
            )
        ).scalars()
    )
    assert len(events) == 1
