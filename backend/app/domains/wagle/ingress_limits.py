"""Request-size backstop for the Wagle Service ingress only. Deliberately not
a global ASGI middleware: a future attachment/upload API must not inherit
this 32KB cap - see WAGLE_FOUNDATION_GAP_ANALYSIS.md.
"""
from fastapi import HTTPException, Request, status

MAX_SERVICE_INGRESS_BYTES = 32 * 1024


async def enforce_service_body_limit(request: Request) -> None:
    """Reads the request body as a bounded stream and rejects it the moment
    actual received bytes exceed the cap - never trusting Content-Length
    alone, since it can be absent (chunked transfer) or simply wrong. The
    collected bytes are cached back onto the request so FastAPI's own body
    parsing (for the route's Pydantic model) reads from this buffer instead
    of re-consuming an already-exhausted stream."""
    total = 0
    chunks: list[bytes] = []
    async for chunk in request.stream():
        total += len(chunk)
        if total > MAX_SERVICE_INGRESS_BYTES:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="요청 본문이 너무 큽니다")
        chunks.append(chunk)
    request._body = b"".join(chunks)
