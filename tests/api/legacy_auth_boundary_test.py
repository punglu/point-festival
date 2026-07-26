#!/usr/bin/env python3
"""Synthetic runtime regression for the legacy containment boundaries.

Run only against the disposable Phase 0 runtime. The script asserts HTTP status
and observable DB-backed state through the protected administrator routes; it
does not print tokens or passwords.
"""

import os
import sys
from datetime import date
from typing import Optional

import requests


BASE_URL = os.environ.get("PHASE0_API_BASE_URL", "http://localhost:18000")
TARGET_DATE = os.environ.get("PHASE0_TEST_DATE", str(date.today()))
ADMIN_USERNAME = os.environ.get("PHASE0_ADMIN_USERNAME", "dad")
ADMIN_PASSWORD = os.environ.get("PHASE0_ADMIN_PASSWORD", "admin1234")


def fail(message: str) -> None:
    raise AssertionError(message)


def call(method: str, path: str, *, token: Optional[str] = None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers = {**headers, "Authorization": f"Bearer {token}"}
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=10, **kwargs)


def expect_status(label: str, response: requests.Response, expected: int) -> None:
    if response.status_code != expected:
        fail(f"{label}: expected {expected}, got {response.status_code}: {response.text[:300]}")
    print(f"PASS {label}: {expected}")


def player_token(player_id: int) -> str:
    response = call(
        "POST",
        "/api/auth/login",
        json={"player_id": player_id, "pin": "1234", "remember_me": False},
    )
    expect_status(f"player {player_id} login", response, 200)
    return response.json()["access_token"]


def admin_token() -> str:
    response = call(
        "POST",
        "/api/auth/admin/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    expect_status("admin login", response, 200)
    return response.json()["access_token"]


def main() -> int:
    admin = admin_token()
    player_a = player_token(1)
    player_b = player_token(2)
    player_c = player_token(3)

    expect_status("public health", call("GET", "/api/health"), 200)
    expect_status("public player selector", call("GET", "/api/players"), 200)

    for label, path in (
        ("anonymous mission list", f"/api/missions/?player_id=2&date={TARGET_DATE}"),
        ("anonymous point summary", f"/api/daily-points/summary?player_id=2&date={TARGET_DATE}&cycle=weekly"),
        ("anonymous notifications", "/api/notifications/"),
        ("anonymous chat partners", "/api/chat/partners"),
        ("anonymous mission delete", "/api/missions/3"),
    ):
        expect_status(label, call("GET" if "delete" not in label else "DELETE", path), 401)

    own_missions = call("GET", f"/api/missions/?player_id=1&date={TARGET_DATE}", token=player_a)
    expect_status("player A own missions", own_missions, 200)
    before_b = call("GET", f"/api/admin/missions?player_id=2&date={TARGET_DATE}", token=admin)
    expect_status("admin reads player B missions", before_b, 200)
    before_count = len(before_b.json())

    expect_status(
        "player A cross-user mission read",
        call("GET", f"/api/missions/?player_id=2&date={TARGET_DATE}", token=player_a),
        403,
    )
    expect_status(
        "player A cross-user mission create",
        call(
            "POST",
            "/api/missions/",
            token=player_a,
            json={"player_id": 2, "date": TARGET_DATE, "text": "unauthorized probe", "point": 1},
        ),
        403,
    )
    after_b = call("GET", f"/api/admin/missions?player_id=2&date={TARGET_DATE}", token=admin)
    expect_status("admin re-reads player B missions", after_b, 200)
    if len(after_b.json()) != before_count:
        fail("rejected player A mission creation changed player B mission rows")
    print("PASS rejected cross-user mission write leaves DB rows unchanged")

    expect_status(
        "player A own point summary",
        call("GET", f"/api/daily-points/summary?player_id=1&date={TARGET_DATE}&cycle=weekly", token=player_a),
        200,
    )
    expect_status(
        "player A cross-user point summary",
        call("GET", f"/api/daily-points/summary?player_id=2&date={TARGET_DATE}&cycle=weekly", token=player_a),
        403,
    )

    created_notification = call(
        "POST",
        "/api/admin/notifications",
        token=admin,
        json={"type": "phase0_test", "player_id": 2, "title": "Synthetic authorization probe", "body": None},
    )
    expect_status("admin creates player B notification", created_notification, 201)
    notification_id = created_notification.json()["id"]
    expect_status("player B own notifications", call("GET", "/api/notifications/", token=player_b), 200)
    expect_status(
        "player A reads player B notification",
        call("PATCH", f"/api/notifications/{notification_id}/read", token=player_a),
        404,
    )
    notifications = call("GET", "/api/admin/notifications", token=admin)
    expect_status("admin verifies rejected notification write", notifications, 200)
    target = next(item for item in notifications.json() if item["id"] == notification_id)
    if target["is_read"]:
        fail("rejected player A notification read changed player B notification")
    print("PASS rejected cross-user notification write leaves DB row unchanged")
    expect_status("player B reads own notification", call("PATCH", f"/api/notifications/{notification_id}/read", token=player_b), 204)

    created_mission = call(
        "POST",
        "/api/admin/missions",
        token=admin,
        json={"player_id": 2, "date": TARGET_DATE, "text": "Synthetic admin authorization probe", "point": 1},
    )
    expect_status("admin creates player B mission", created_mission, 201)
    created_mission_id = created_mission.json()["id"]
    expect_status(
        "admin deletes own synthetic mission",
        call("DELETE", f"/api/admin/missions/{created_mission_id}", token=admin),
        204,
    )
    expect_status("player token blocked from templates", call("GET", "/api/mission-templates", token=player_a), 401)
    expect_status("admin template access", call("GET", "/api/mission-templates", token=admin), 200)

    marker = "phase0-auth-chat-boundary"
    sent = call("POST", "/api/chat/send", token=player_a, json={"receiver_id": 2, "message": marker})
    expect_status("player A sends player B chat", sent, 201)
    history_b = call("GET", "/api/chat/history/1", token=player_b)
    expect_status("player B reads A/B history", history_b, 200)
    if marker not in [message["message"] for message in history_b.json()]:
        fail("player B did not receive the A/B test message")
    history_c = call("GET", "/api/chat/history/2", token=player_c)
    expect_status("player C reads only C/B pair history", history_c, 200)
    if marker in [message["message"] for message in history_c.json()]:
        fail("player C received an A/B chat message")
    print("PASS chat history is pair-filtered for third player")

    print("RESULT legacy authorization boundary suite: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, requests.RequestException) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
