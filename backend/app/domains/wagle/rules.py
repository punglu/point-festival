"""Pure Wagle policy helpers."""
from __future__ import annotations


def canonical_direct_pair(first: int, second: int) -> tuple[int, int]:
    if first == second:
        raise ValueError("self DIRECT room is not permitted")
    return (first, second) if first < second else (second, first)


def visible_range(joined_sequence: int, left_sequence: int | None, status: str) -> tuple[int, int | None]:
    if status == "removed":
        raise PermissionError("removed participant")
    return joined_sequence, left_sequence if status == "left" else None


def can_write(subscription_active: bool, room_status: str, participant_status: str) -> bool:
    return subscription_active and room_status == "active" and participant_status == "active"
