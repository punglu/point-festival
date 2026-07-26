#!/usr/bin/env python3
"""Regression tests for same-line Closeout Contract field parsing."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[1] / "tools" / "check_closeout.py"
SPEC = importlib.util.spec_from_file_location("check_closeout", TOOL)
assert SPEC is not None and SPEC.loader is not None
CHECK_CLOSEOUT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CLOSEOUT)


class FieldParsingTests(unittest.TestCase):
    def test_absent_field_is_none(self) -> None:
        self.assertIsNone(CHECK_CLOSEOUT.field("- Other: value\n", "Field"))

    def test_empty_field_is_empty_string(self) -> None:
        self.assertEqual(CHECK_CLOSEOUT.field("- Field:\n", "Field"), "")

    def test_space_only_field_is_empty_string(self) -> None:
        self.assertEqual(CHECK_CLOSEOUT.field("- Field:    \n", "Field"), "")

    def test_next_field_is_not_consumed(self) -> None:
        text = "- COVERAGE MAP Reason:\n- CLOSEOUT GATE: PASS\n"
        self.assertEqual(CHECK_CLOSEOUT.field(text, "COVERAGE MAP Reason"), "")

    def test_same_line_value_is_returned(self) -> None:
        self.assertEqual(CHECK_CLOSEOUT.field("- Field: value\n", "Field"), "value")

    def test_value_is_trimmed(self) -> None:
        self.assertEqual(CHECK_CLOSEOUT.field("- Field:  value \t\n", "Field"), "value")

    def test_lf_is_supported(self) -> None:
        self.assertEqual(CHECK_CLOSEOUT.field("- Field: value\n- Next: x\n", "Field"), "value")

    def test_crlf_is_supported(self) -> None:
        self.assertEqual(CHECK_CLOSEOUT.field("- Field: value\r\n- Next: x\r\n", "Field"), "value")

    def test_gate_on_next_line_does_not_fill_reason(self) -> None:
        text = "- COVERAGE MAP Reason:\n- CLOSEOUT GATE: PASS\n"
        self.assertEqual(CHECK_CLOSEOUT.field(text, "COVERAGE MAP Reason"), "")

    def test_arbitrary_body_on_next_line_is_not_consumed(self) -> None:
        text = "- Field:\nA following paragraph is not a field.\n"
        self.assertEqual(CHECK_CLOSEOUT.field(text, "Field"), "")


if __name__ == "__main__":
    unittest.main()
