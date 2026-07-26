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


class ArchiveLifecycleTests(unittest.TestCase):
    """Exercise the installed checker, not a copy of its lifecycle logic."""

    task_id = "TASK-001"

    def write(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def handoff(self, location: str, closeout: str = "") -> str:
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
        archived_handoffs: int = 0,
        graduate: bool = False,
        evidence: bool = True,
        relay: bool = False,
        handoff_closeout: str = "",
        evidence_task_id: str | None = None,
        historical: bool = False,
    ) -> str:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            if active:
                self.write(root, "agent-system/active.md", self.active())
            if active_handoff:
                self.write(root, f"agent-system/handoffs/active/{self.task_id}.md", self.handoff("active", handoff_closeout))
            for number in range(archived_handoffs):
                suffix = "" if number == 0 else f"-{number}"
                self.write(root, f"agent-system/handoffs/archive/2026-07/{self.task_id}{suffix}.md", self.handoff("archive/2026-07", handoff_closeout))
            if evidence:
                self.write(root, f"agent-system/qa/{self.task_id}.md", self.evidence(evidence_task_id))
            if graduate:
                self.write(root, "agent-system/graduated/2026-07.md", f"- Task ID: `{self.task_id}`\n")
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


if __name__ == "__main__":
    unittest.main()
