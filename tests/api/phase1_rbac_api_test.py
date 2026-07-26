#!/usr/bin/env python3
"""API + database assertions for the isolated Phase 1 RBAC Foundation.

Run only after the Phase 1 synthetic seed script.  Tokens and credentials are
never printed.  The script uses known synthetic IDs and no operating data.
"""
import json
import os
import subprocess
import sys
from typing import Optional

import requests


BASE_URL = os.environ.get("PHASE1_API_BASE_URL", "http://localhost:18001")
COMPOSE_FILE = os.environ.get("PHASE1_COMPOSE_FILE", "docker-compose.phase1.yml")
DB_USER = os.environ.get("PHASE1_DB_USER", "mc_phase0")
DB_NAME = os.environ.get("PHASE1_DB_NAME", "mc_festival_phase0")


def fail(message: str) -> None:
    raise AssertionError(message)


def call(method: str, path: str, *, token: Optional[str] = None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers = {**headers, "Authorization": f"Bearer {token}"}
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=10, **kwargs)


def expect(label: str, response: requests.Response, expected: int):
    if response.status_code != expected:
        fail(f"{label}: expected {expected}, got {response.status_code}: {response.text[:250]}")
    print(f"PASS {label}: {expected}")
    return response


def player_token(player_id: int) -> str:
    response = expect(
        f"player {player_id} login",
        call("POST", "/api/auth/login", json={"player_id": player_id, "pin": "1234", "remember_me": False}),
        200,
    )
    return response.json()["access_token"]


def admin_token() -> str:
    response = expect(
        "admin login",
        call("POST", "/api/auth/admin/login", json={"username": "dad", "password": "admin1234"}),
        200,
    )
    return response.json()["access_token"]


def db_scalar(sql: str) -> str:
    command = [
        "docker", "compose", "-p", "mc_phase1", "--env-file", ".env.phase0.example", "-f", COMPOSE_FILE,
        "exec", "-T", "db", "psql", "-U", DB_USER, "-d", DB_NAME, "-Atc", sql,
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def db_execute(sql: str) -> None:
    db_scalar(sql)


def family_for(context: dict, name: str) -> dict:
    for family in context["families"]:
        if family["name"] == name:
            return family
    fail(f"family {name} absent from account context")


def role_assignment(assignments: list, code: str) -> dict:
    for assignment in assignments:
        if assignment["role"]["code"] == code:
            return assignment
    fail(f"role assignment {code} absent")


def main() -> int:
    owner_a = player_token(1)
    owner_b = player_token(2)
    other_family = player_token(3)
    participant = player_token(4)
    admin = admin_token()

    expect("anonymous account context", call("GET", "/api/account-context"), 401)
    context_a = expect("owner A account context", call("GET", "/api/account-context", token=owner_a), 200).json()
    alpha = family_for(context_a, "Synthetic Family Alpha")
    alpha_id = alpha["id"]
    if "family.roles.assign" not in alpha["permissions"]:
        fail("owner A lacks family.roles.assign")
    context_other = expect("other family context", call("GET", "/api/account-context", token=other_family), 200).json()
    beta = family_for(context_other, "Synthetic Family Beta")
    if beta["id"] == alpha_id:
        fail("synthetic families are not isolated")

    expect("other family reads Alpha", call("GET", f"/api/families/{alpha_id}", token=other_family), 403)
    expect("participant default deny family read", call("GET", f"/api/families/{alpha_id}", token=participant), 403)
    expect(
        "admin cannot close Alpha family",
        call("PATCH", f"/api/families/{alpha_id}", token=admin, json={"status": "closed"}),
        403,
    )
    if db_scalar("SELECT status FROM family_groups WHERE id=%s" % alpha_id) != "active":
        fail("rejected admin family closure changed family status")
    members = expect("owner A reads Alpha members", call("GET", f"/api/families/{alpha_id}/members", token=owner_a), 200).json()
    owner_a_membership = next(member for member in members if member["account_id"] == context_a["account_id"])
    context_b = expect("owner B account context", call("GET", "/api/account-context", token=owner_b), 200).json()
    owner_b_membership = next(member for member in members if member["account_id"] == context_b["account_id"])
    context_participant = expect("participant context with active service", call("GET", "/api/account-context", token=participant), 200).json()
    participant_family = family_for(context_participant, "Synthetic Family Alpha")
    participant_membership = participant_family["membership"]
    if "markpoint.own.read" not in participant_family["permissions"]:
        fail("active MarkPoint participant lacks service permission")
    expect(
        "cross-family membership role assignment denied",
        call(
            "POST",
            f"/api/families/{alpha_id}/members/{beta['membership']['id']}/roles",
            token=owner_a,
            json={"role_code": "member"},
        ),
        404,
    )

    before_owner_count = db_scalar("SELECT count(*) FROM membership_role_assignments a JOIN roles r ON r.id=a.role_id JOIN family_memberships m ON m.id=a.membership_id WHERE m.family_group_id=%s AND r.code='owner' AND a.revoked_at IS NULL" % alpha_id)
    expect(
        "admin cannot self-escalate owner",
        call("POST", f"/api/families/{alpha_id}/members/{owner_a_membership['id']}/roles", token=admin, json={"role_code": "owner"}),
        403,
    )
    if db_scalar("SELECT count(*) FROM membership_role_assignments a JOIN roles r ON r.id=a.role_id JOIN family_memberships m ON m.id=a.membership_id WHERE m.family_group_id=%s AND r.code='owner' AND a.revoked_at IS NULL" % alpha_id) != before_owner_count:
        fail("rejected admin escalation changed owner assignments")

    assignment = expect(
        "owner assigns participant mission manager",
        call("POST", f"/api/families/{alpha_id}/members/{participant_membership['id']}/roles", token=owner_a, json={"role_code": "mission_manager", "service_code": "markpoint"}),
        201,
    ).json()
    if assignment["role"]["scope_type"] != "SERVICE":
        fail("mission manager was not a service role")
    context_participant = expect("participant multirole union", call("GET", "/api/account-context", token=participant), 200).json()
    permissions = family_for(context_participant, "Synthetic Family Alpha")["permissions"]
    if not {"markpoint.own.read", "markpoint.missions.manage"}.issubset(permissions):
        fail("service-role permission union is incomplete")

    expect(
        "admin suspends Alpha MarkPoint subscription",
        call("PATCH", f"/api/families/{alpha_id}/services/markpoint", token=admin, json={"status": "suspended"}),
        200,
    )
    permissions_after_suspend = family_for(expect("participant context after suspension", call("GET", "/api/account-context", token=participant), 200).json(), "Synthetic Family Alpha")["permissions"]
    if "markpoint.missions.manage" in permissions_after_suspend or "markpoint.own.read" in permissions_after_suspend:
        fail("inactive subscription still grants service permissions")

    db_execute("UPDATE players SET deleted_at = NOW() WHERE id = 4")
    expect("soft-deleted legacy player adapter denied", call("GET", "/api/account-context", token=participant), 403)
    db_execute("UPDATE players SET deleted_at = NULL WHERE id = 4")
    db_execute("UPDATE admin_auth SET deleted_at = NOW() WHERE id = 1")
    expect("soft-deleted legacy admin adapter denied", call("GET", "/api/account-context", token=admin), 403)
    db_execute("UPDATE admin_auth SET deleted_at = NULL WHERE id = 1")

    owner_b_assignments = expect("owner A reads owner B roles", call("GET", f"/api/families/{alpha_id}/members/{owner_b_membership['id']}/roles", token=owner_a), 200).json()
    owner_b_assignment = role_assignment(owner_b_assignments, "owner")
    expect("owner A removes second owner", call("DELETE", f"/api/families/{alpha_id}/members/{owner_b_membership['id']}/roles/{owner_b_assignment['id']}", token=owner_a), 204)
    owner_a_assignments = expect("owner A reads own roles", call("GET", f"/api/families/{alpha_id}/members/{owner_a_membership['id']}/roles", token=owner_a), 200).json()
    owner_a_assignment = role_assignment(owner_a_assignments, "owner")
    expect("last owner removal denied", call("DELETE", f"/api/families/{alpha_id}/members/{owner_a_membership['id']}/roles/{owner_a_assignment['id']}", token=owner_a), 409)
    if db_scalar("SELECT count(*) FROM membership_role_assignments a JOIN roles r ON r.id=a.role_id JOIN family_memberships m ON m.id=a.membership_id WHERE m.family_group_id=%s AND r.code='owner' AND a.revoked_at IS NULL" % alpha_id) != "1":
        fail("last owner invariant was not preserved")

    expect("owner closes Alpha family", call("PATCH", f"/api/families/{alpha_id}", token=owner_a, json={"status": "closed"}), 200)
    if db_scalar("SELECT status FROM family_groups WHERE id=%s" % alpha_id) != "closed":
        fail("owner family closure was not persisted")
    owner_context_after_close = expect("owner context after family close", call("GET", "/api/account-context", token=owner_a), 200).json()
    if any(family["id"] == alpha_id for family in owner_context_after_close["families"]):
        fail("inactive family remains in account context")
    expect("closed family path denied", call("GET", f"/api/families/{alpha_id}", token=owner_a), 403)

    ambiguous = db_scalar("SELECT count(*) FROM legacy_identity_mappings WHERE mapping_status='ambiguous' AND account_id IS NULL")
    if ambiguous != "1":
        fail("ambiguous legacy identity fixture was not preserved")
    print("PASS ambiguous legacy mapping remains unmapped")
    print("RESULT phase1 RBAC API+DB suite: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, requests.RequestException, subprocess.CalledProcessError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
