"""주간 아키텍처 핵심 로직 테스트"""
import pytest
from datetime import date
from app.domains.mission.service import get_week_range, is_same_week


class TestWeekRange:
    def test_monday_returns_same_monday(self):
        # 월요일 입력 → 같은 월요일 시작
        d = date(2026, 3, 30)  # 월요일
        start, end = get_week_range(d)
        assert start == date(2026, 3, 30)
        assert end == date(2026, 4, 5)

    def test_sunday_returns_same_week(self):
        # 일요일 입력 → 해당 주 월요일 시작
        d = date(2026, 4, 5)  # 일요일
        start, end = get_week_range(d)
        assert start == date(2026, 3, 30)
        assert end == date(2026, 4, 5)

    def test_wednesday_returns_correct_range(self):
        d = date(2026, 4, 1)  # 수요일
        start, end = get_week_range(d)
        assert start == date(2026, 3, 30)
        assert end == date(2026, 4, 5)


class TestIsSameWeek:
    def test_same_week_monday_sunday(self):
        assert is_same_week(date(2026, 3, 30), date(2026, 4, 5)) is True

    def test_different_weeks(self):
        assert is_same_week(date(2026, 3, 29), date(2026, 3, 30)) is False

    def test_same_day(self):
        assert is_same_week(date(2026, 4, 4), date(2026, 4, 4)) is True
