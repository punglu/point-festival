"""Wagle realtime delivery Worker: `python -m app.workers.wagle_realtime`.

A separate process from `app.workers.service_outbox` for the same reason that
one exists at all: an independently restartable consumer whose crash or
backpressure never affects request serving. Splitting by `owner_service` also
means a stuck Markpoint SERVICE_ACTION cannot delay a human message's
notification, and vice versa.

**Deployment note, stated rather than assumed.** Running this as its own
process means its `InProcessFanout` is not the one the web process holds, so
its WebSocket publish reaches nobody. That is fine and is the intended v1
shape: the durable Push path works from here, and connected clients get their
events from the web process's own in-process dispatch plus the per-connection
durable catch-up. When a cross-process channel is chosen (see
`InProcessFanout`'s docstring), this Worker becomes the single publisher and
the catch-up drops back to being a safety net.
"""
from __future__ import annotations

import asyncio
import signal

from app.domains.wagle import realtime_dispatcher

DEFAULT_BATCH_SIZE = 20
DEFAULT_POLL_INTERVAL_SECONDS = 1.0


async def main_loop(poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS) -> None:
    from app.database import AsyncSessionLocal

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass  # not available on every platform / test runner

    print("[wagle_realtime] worker starting")
    while not stop.is_set():
        async with AsyncSessionLocal() as db:
            result = await realtime_dispatcher.run_once(db, batch_size=DEFAULT_BATCH_SIZE)
        if result["claimed"]:
            print(f"[wagle_realtime] batch: {result}")
        if result["claimed"] == 0:
            try:
                await asyncio.wait_for(stop.wait(), timeout=poll_interval_seconds)
            except asyncio.TimeoutError:
                pass
    print("[wagle_realtime] worker stopped")


if __name__ == "__main__":
    asyncio.run(main_loop())
