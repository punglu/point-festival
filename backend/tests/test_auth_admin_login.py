"""RE-QA-F-ADMIN-LOGIN-BCRYPT regression
(`agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md`).

`authenticate_admin` called `bcrypt.checkpw` with no length guard: a
password over 72 bytes made `bcrypt` raise `ValueError` instead of
returning False, so any unauthenticated caller who knew or guessed a valid
admin username (`dad`/`mom` in `database/init.sql`) could trigger a 500.
Fixed with the same fail-closed `try/except (ValueError, TypeError)`
pattern `family/auth_service.py::verify_password` already uses.

Seeds its own `AdminAuth` row (`player_id=None`, the column is nullable)
rather than depending on `database/init.sql`'s `dad`/`mom` rows surviving:
`conftest.reset_db`'s `TRUNCATE ... CASCADE` on `players` cascades into
`admin_auth` (it has an FK to `players.id`) before every test, so those
seed rows cannot be relied on to still exist here.
"""
from __future__ import annotations

import bcrypt
import pytest_asyncio

from app.domains.auth.models import AdminAuth
from app.domains.auth.schema import AdminLoginRequest

ADMIN_USERNAME = "qa_bcrypt_admin"
ADMIN_PASSWORD = "correct-horse-battery-staple"


@pytest_asyncio.fixture
async def seeded_admin(db):
    password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    admin = AdminAuth(username=ADMIN_USERNAME, password=password_hash, display_name="QA Admin", player_id=None)
    db.add(admin)
    await db.commit()
    return admin


async def test_01_admin_login_oversized_ascii_password_is_401_not_500(client, seeded_admin):
    resp = await client.post(
        "/api/auth/admin/login",
        json={"username": ADMIN_USERNAME, "password": "a" * 100},
    )
    assert resp.status_code == 401, resp.text


async def test_02_admin_login_oversized_multibyte_password_is_401_not_500(client, seeded_admin):
    # bcrypt's limit is 72 *bytes*, not 72 characters -- a >72-byte
    # multi-byte (Korean) password is a genuinely different code path than
    # the pure-ASCII case above (each character is 3 UTF-8 bytes here).
    resp = await client.post(
        "/api/auth/admin/login",
        json={"username": ADMIN_USERNAME, "password": "가나다라" * 20},
    )
    assert resp.status_code == 401, resp.text


async def test_03_admin_login_oversized_password_unknown_username_is_401(client):
    resp = await client.post(
        "/api/auth/admin/login",
        json={"username": "no_such_admin", "password": "b" * 200},
    )
    assert resp.status_code == 401, resp.text


async def test_04_admin_login_correct_password_still_succeeds(client, seeded_admin):
    resp = await client.post(
        "/api/auth/admin/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"]
    assert body["display_name"] == "QA Admin"


async def test_05_admin_login_incorrect_normal_length_password_is_401(client, seeded_admin):
    resp = await client.post(
        "/api/auth/admin/login",
        json={"username": ADMIN_USERNAME, "password": "wrong-password"},
    )
    assert resp.status_code == 401, resp.text


def test_06_admin_login_request_schema_still_accepts_a_long_password():
    # No max_length was added to the schema itself -- the fix is at the
    # bcrypt call site, not input rejection, so a long password must still
    # reach authenticate_admin (and fail closed there), not be rejected
    # earlier as a 422.
    request = AdminLoginRequest(username="dad", password="c" * 500)
    assert len(request.password) == 500
