import pytest

from app.domains.doran.rules import canonical_direct_pair, can_write, visible_range


def test_direct_pair_is_canonical_and_rejects_self():
    assert canonical_direct_pair(9, 2) == (2, 9)
    with pytest.raises(ValueError):
        canonical_direct_pair(2, 2)


def test_visibility_preserves_left_upper_bound_and_denies_removed():
    assert visible_range(11, 27, "left") == (11, 27)
    assert visible_range(11, 27, "active") == (11, None)
    with pytest.raises(PermissionError):
        visible_range(11, None, "removed")


def test_write_requires_active_subscription_room_and_participant():
    assert can_write(True, "active", "active") is True
    assert can_write(False, "active", "active") is False
    assert can_write(True, "closed", "active") is False
    assert can_write(True, "active", "left") is False
