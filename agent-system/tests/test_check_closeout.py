#!/usr/bin/env python3
"""Regression tests for same-line Closeout Contract field parsing."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
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


class CloseoutFixtureHarness:
    """Exercise the installed checker, not a copy of its lifecycle logic."""

    task_id = "TASK-001"

    def write(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def handoff(self, location: str, closeout: str = "") -> str:
        if closeout == "missing-block":
            return f"# Handoff\n- Task ID: `{self.task_id}`\n- Closeout Contract: `v1`\n"
        coverage = "`UPDATED`"
        reason = "`lifecycle fixture`"
        if closeout == "blank-reason":
            coverage = "`NO_CHANGE_REQUIRED`"
            reason = ""
            closeout = ""
        return f"""# Handoff
- Task ID: `{self.task_id}`
- Closeout Contract: `v1`

## Closeout Synchronization
- Contract: `v1`
- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/{location}/{self.task_id}.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/{self.task_id}.md`
- Independent QA: `pending`
- COVERAGE MAP: {coverage}
- COVERAGE MAP Reason: {reason}
- CLOSEOUT GATE: `PASS`
{closeout}"""

    def evidence(self, task_id: str | None = None) -> str:
        return f"- Task ID: `{task_id or self.task_id}`\n- Closeout Contract: `v1`\n"

    def active(self) -> str:
        return f"""# Active Tasks
## {self.task_id}
- Task ID: `{self.task_id}`
- Lifecycle: `IN_PROGRESS`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
"""

    def run_case(
        self,
        *,
        active: bool = False,
        active_handoff: bool = False,
        active_handoffs: int | None = None,
        archived_handoffs: int = 0,
        graduate: bool = False,
        graduate_entries: int | None = None,
        evidence: bool = True,
        relay: bool = False,
        handoff_closeout: str = "",
        evidence_task_id: str | None = None,
        historical: bool = False,
        incomplete_active: bool = False,
        archive_months: list[str] | None = None,
    ) -> str:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            if active:
                active_text = self.active()
                if incomplete_active:
                    active_text = active_text.replace("- Execution: `SUCCEEDED`\n", "")
                self.write(root, "agent-system/active.md", active_text)
            active_handoff_count = int(active_handoff) if active_handoffs is None else active_handoffs
            for number in range(active_handoff_count):
                suffix = "" if number == 0 else f"-{number}"
                self.write(root, f"agent-system/handoffs/active/{self.task_id}{suffix}.md", self.handoff("active", handoff_closeout))
            archive_months = archive_months or ["2026-07"] * archived_handoffs
            for number in range(archived_handoffs):
                suffix = "" if number == 0 else f"-{number}"
                month = archive_months[number]
                self.write(root, f"agent-system/handoffs/archive/{month}/{self.task_id}{suffix}.md", self.handoff(f"archive/{month}", handoff_closeout))
            if evidence:
                self.write(root, f"agent-system/qa/{self.task_id}.md", self.evidence(evidence_task_id))
            graduate_count = int(graduate) if graduate_entries is None else graduate_entries
            for number in range(graduate_count):
                suffix = "" if number == 0 else f"-{number}"
                self.write(root, f"agent-system/graduated/2026-07{suffix}.md", f"- Task ID: `{self.task_id}`\n")
            if relay:
                self.write(root, "agent-system/relay/current.md", f"- Task ID: `{self.task_id}`\n")
            if historical:
                self.write(root, "agent-system/handoffs/archive/2025-01/HISTORICAL.md", "- Task ID: `HISTORICAL`\n")
            result = subprocess.run(
                [os.environ.get("PYTHON", "python3"), str(TOOL)],
                env={**os.environ, "AGENT_SYSTEM_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout


class ArchiveLifecycleTests(CloseoutFixtureHarness, unittest.TestCase):

    def test_archive_lifecycle_contract(self) -> None:
        cases = [
            ("normal open", dict(active=True, active_handoff=True), False),
            ("normal archived", dict(archived_handoffs=1, graduate=True), False),
            ("archive plus active record", dict(active=True, archived_handoffs=1, graduate=True), True),
            ("both handoff modes", dict(active=True, active_handoff=True, archived_handoffs=1), True),
            ("archive missing graduate", dict(archived_handoffs=1), True),
            ("graduate missing archive", dict(graduate=True), True),
            ("evidence only", dict(), True),
            ("archived relay", dict(archived_handoffs=1, graduate=True, relay=True), True),
            ("duplicate archive", dict(archived_handoffs=2, graduate=True), True),
            ("open graduate", dict(active=True, active_handoff=True, graduate=True), True),
            ("markerless history", dict(evidence=False, historical=True), False),
            ("archived bad closeout", dict(archived_handoffs=1, graduate=True, handoff_closeout="blank-reason"), True),
            ("archived evidence preserved", dict(archived_handoffs=1, graduate=True), False),
            ("task id mismatch", dict(active=True, active_handoff=True, evidence_task_id="TASK-OTHER"), True),
            ("second normal mode", dict(active=True, active_handoff=True), False),
        ]
        for label, kwargs, expect_warning in cases:
            with self.subTest(label=label):
                output = self.run_case(**kwargs)
                self.assertEqual("[WARN]" in output, expect_warning, output)


class PermanentCloseoutRegressionTests(CloseoutFixtureHarness, unittest.TestCase):
    """Source-backed v1 contract matrix; each case invokes the real checker."""

    def test_open_and_archived_contract_matrix(self) -> None:
        cases = [
            (
                "normal OPEN task has no warning",
                dict(active=True, active_handoff=True),
                None,
            ),
            (
                "OPEN task missing active record",
                dict(active_handoff=True),
                "active record is missing",
            ),
            (
                "OPEN task missing active handoff",
                dict(active=True),
                "OPEN task requires exactly one active handoff",
            ),
            (
                "OPEN task has incomplete active state",
                dict(active=True, active_handoff=True, incomplete_active=True),
                "active record is missing lifecycle, verification, or execution state",
            ),
            (
                "OPEN task has duplicate active handoffs",
                dict(active=True, active_handoffs=2),
                "OPEN task requires exactly one active handoff",
            ),
            (
                "OPEN task also has archive handoff",
                dict(active=True, active_handoff=True, archived_handoffs=1, graduate=True),
                "task exists in both handoffs/active and handoffs/archive",
            ),
            (
                "OPEN task is also graduated",
                dict(active=True, active_handoff=True, graduate=True),
                "OPEN task is registered in graduated",
            ),
            (
                "OPEN task has invalid closeout block",
                dict(active=True, active_handoff=True, handoff_closeout="missing-block"),
                "Closeout Synchronization block is missing",
            ),
            (
                "OPEN task has empty no-change reason",
                dict(active=True, active_handoff=True, handoff_closeout="blank-reason"),
                "COVERAGE MAP is NO_CHANGE_REQUIRED but reason is empty",
            ),
            (
                "normal ARCHIVED task has no warning",
                dict(archived_handoffs=1, graduate=True),
                None,
            ),
            (
                "ARCHIVED task has duplicate archive handoffs across months",
                dict(archived_handoffs=2, graduate=True, archive_months=["2026-06", "2026-07"]),
                "ARCHIVED task requires exactly one archived handoff",
            ),
            (
                "ARCHIVED task lacks graduated entry",
                dict(archived_handoffs=1),
                "archived task is missing graduated entry",
            ),
            (
                "ARCHIVED task has duplicate graduate entries",
                dict(archived_handoffs=1, graduate_entries=2),
                "task has duplicate graduated entries",
            ),
            (
                "ARCHIVED task retains active record",
                dict(active=True, archived_handoffs=1, graduate=True),
                "archived handoff exists but active record is still present",
            ),
            (
                "ARCHIVED task retains active handoff",
                dict(active_handoff=True, archived_handoffs=1, graduate=True),
                "task exists in both handoffs/active and handoffs/archive",
            ),
            (
                "ARCHIVED task remains in relay",
                dict(archived_handoffs=1, graduate=True, relay=True),
                "archived task is still declared in relay/current.md",
            ),
            (
                "ARCHIVED task has malformed closeout block",
                dict(archived_handoffs=1, graduate=True, handoff_closeout="missing-block"),
                "Closeout Synchronization block is missing",
            ),
            (
                "QA evidence only is not a valid task graph",
                dict(),
                "QA evidence declares Closeout Contract v1 but no active or archived handoff exists",
            ),
            (
                "markerless historical archive remains outside v1 enforcement",
                dict(evidence=False, historical=True),
                None,
            ),
            (
                "Task ID mismatch is reported",
                dict(active=True, active_handoff=True, evidence_task_id="TASK-OTHER"),
                "QA evidence is missing",
            ),
        ]
        for label, kwargs, expected_warning in cases:
            with self.subTest(label=label):
                output = self.run_case(**kwargs)
                self.assertNotIn("Traceback", output, output)
                if expected_warning is None:
                    self.assertNotIn("[WARN]", output, output)
                else:
                    self.assertIn(expected_warning, output, output)

    def test_current_repository_is_clean_for_closeout_checker(self) -> None:
        result = subprocess.run(
            [os.environ.get("PYTHON", "python3"), str(TOOL)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertNotIn("[WARN]", result.stdout, result.stdout)


if __name__ == "__main__":
    unittest.main()
