"""Service Principal identity: credential issuance/verification and the
service-ingress authentication dependency. Deliberately separate from
app/dependencies.py's user-JWT scheme - a Service Principal is never a user
Account and never carries or reuses a user JWT (see DORAN_SECURITY_AND_
AUTHORIZATION.md, "Actors and credential boundaries").

No operational issuance/rotation UI is built here. create_service_principal()
is the only issuance path - a safe management primitive callable from a
trusted script or test fixture, not a public HTTP surface.
"""
from __future__ import annotations

import secrets
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.doran.models import ServicePrincipal

service_security = HTTPBearer(auto_error=False)

# Computed once at import, never per-request: a fixed dummy hash so an
# unknown or revoked credential_id pays the same bcrypt verification cost as
# a wrong-secret check against a real hash. This narrows, but does not claim
# to eliminate, the timing gap between "no such credential" and "wrong
# secret" - bcrypt cost dominates request latency far more than the
# microsecond-scale variance a real timing side channel would need.
_DUMMY_CREDENTIAL_HASH = bcrypt.hashpw(secrets.token_bytes(32), bcrypt.gensalt()).decode("utf-8")


def issue_credential() -> tuple[str, str, str]:
    """Returns (credential_id, secret, credential_hash). The secret is
    returned exactly once by the caller; only the hash is ever persisted."""
    credential_id = secrets.token_urlsafe(24)
    secret = secrets.token_urlsafe(32)
    credential_hash = bcrypt.hashpw(secret.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return credential_id, secret, credential_hash


async def get_current_service_principal(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(service_security),
    db: AsyncSession = Depends(get_db),
) -> ServicePrincipal:
    """Authenticates the service-ingress Bearer token
    ``<credential_id>.<secret>``. A user JWT never matches this shape and is
    rejected the same way an unknown credential is - both are a plain 401
    with no detail that would help distinguish "unknown" from "wrong secret"
    from "not a credential at all"."""
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 서비스 인증입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or "." not in credentials.credentials:
        raise invalid
    credential_id, _, secret = credentials.credentials.partition(".")
    if not credential_id or not secret:
        raise invalid
    principal = (
        await db.execute(select(ServicePrincipal).where(ServicePrincipal.credential_id == credential_id))
    ).scalars().first()
    if principal is None or principal.status != "active":
        bcrypt.checkpw(secret.encode("utf-8"), _DUMMY_CREDENTIAL_HASH.encode("utf-8"))
        raise invalid
    if not bcrypt.checkpw(secret.encode("utf-8"), principal.credential_hash.encode("utf-8")):
        raise invalid
    return principal
