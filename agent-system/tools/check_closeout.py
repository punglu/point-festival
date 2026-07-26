#!/usr/bin/env python3
"""Report-only validation for Closeout Contract v1 task records."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_SYSTEM_ROOT", Path(__file__).resolve().parents[2]))
ACTIVE = ROOT / "agent-system" / "active.md"
HANDOFFS = ROOT / "agent-system" / "handoffs" / "active"
QA = ROOT / "agent-system" / "qa"
ALLOWED_ROOTS = ("agent-system/handoffs/active/", "agent-system/qa/")
AREA_VALUES = {
    "ACTIVE": {"UPDATED", "BLOCKED"},
    "HANDOFF": {"UPDATED", "BLOCKED"},
    "QA EVIDENCE": {"UPDATED", "BLOCKED"},
    "COVERAGE MAP": {"UPDATED", "NO_CHANGE_REQUIRED", "BLOCKED"},
    "CLOSEOUT GATE": {"PASS", "BLOCKED"},
}


def field(text: str, name: str) -> str:
    match = re.search(rf"^- {re.escape(name)}:\s*`?([^`\n]+?)`?\s*$", text, re.M)
    return match.group(1).strip() if match else ""


def active_entries() -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    if not ACTIVE.is_file():
        return entries
    for line in ACTIVE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- ([A-Za-z ]+):\s*`?([^`]+?)`?\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if key == "Task ID":
            current = {key: value}
            entries[value] = current
        elif current is not None:
            current[key] = value
    return entries


def warn(task_id: str, message: str) -> None:
    print(f"[WARN] {task_id}: {message}")


def permitted_path(path: str) -> bool:
    return path.startswith(ALLOWED_ROOTS) and (ROOT / path).is_file()


def find_task_file(directory: Path, task_id: str) -> Path | None:
    direct = directory / f"{task_id}.md"
    return direct if direct.is_file() else None


def check_task(task_id: str, active: dict[str, str], handoff: Path | None, evidence: Path | None) -> None:
    handoff_text = handoff.read_text(encoding="utf-8") if handoff else ""
    evidence_text = evidence.read_text(encoding="utf-8") if evidence else ""
    contract = field(handoff_text, "Closeout Contract") or field(evidence_text, "Closeout Contract") or active.get("Closeout Contract", "")
    has_closeout = "## Closeout Synchronization" in handoff_text
    if contract != "v1":
        warn(task_id, "Closeout Contract: v1 is missing")
        return
    if not active:
        warn(task_id, "active record is missing")
    elif not active.get("Lifecycle") or not active.get("Verification") or not active.get("Execution"):
        warn(task_id, "active record is missing lifecycle, verification, or execution state")
    if not handoff:
        warn(task_id, "task handoff is missing")
    if not evidence:
        warn(task_id, "QA evidence is missing")
    if handoff and field(handoff_text, "Task ID") != task_id:
        warn(task_id, "Task ID does not match handoff")
    if evidence and field(evidence_text, "Task ID") != task_id:
        warn(task_id, "Task ID does not match QA evidence")
    if not has_closeout:
        warn(task_id, "Closeout Synchronization block is missing")
        return
    statuses = {name: field(handoff_text, name) for name in AREA_VALUES}
    for name, allowed in AREA_VALUES.items():
        if statuses[name] not in allowed:
            warn(task_id, f"{name} has invalid or missing value: {statuses[name] or 'empty'}")
    reason = field(handoff_text, "COVERAGE MAP Reason")
    if statuses["COVERAGE MAP"] == "NO_CHANGE_REQUIRED" and not reason:
        warn(task_id, "COVERAGE MAP is NO_CHANGE_REQUIRED but reason is empty")
    if statuses["CLOSEOUT GATE"] == "PASS":
        for name in ("ACTIVE", "HANDOFF", "QA EVIDENCE"):
            if statuses[name] != "UPDATED":
                warn(task_id, f"CLOSEOUT GATE is PASS while {name} is {statuses[name] or 'missing'}")
        if any(value == "BLOCKED" for value in statuses.values()):
            warn(task_id, "CLOSEOUT GATE is PASS while a closeout area is BLOCKED")
        block = handoff_text[handoff_text.find("## Closeout Synchronization"):]
        if re.search(r"(?:Closeout|CLOSEOUT) Gate PASS.{0,80}(?:QA PASS|Independent QA PASS)", block, re.I):
            warn(task_id, "CLOSEOUT GATE PASS is described as independent QA PASS")
    handoff_path = field(handoff_text, "HANDOFF Path")
    evidence_path = field(handoff_text, "QA Evidence Path")
    if not handoff_path:
        warn(task_id, "HANDOFF Path is missing")
    elif not permitted_path(handoff_path):
        warn(task_id, f"HANDOFF Path is not an allowed repository path: {handoff_path}")
    if not evidence_path:
        warn(task_id, "QA Evidence Path is missing")
    elif not permitted_path(evidence_path):
        warn(task_id, f"QA Evidence Path is not an allowed repository path: {evidence_path}")
    if evidence and field(evidence_text, "Independent from implementer").lower() == "true":
        verdict = field(evidence_text, "Verdict")
        if verdict not in {"PASS", "CONDITIONAL", "BLOCKED", "HUMAN_GATE"}:
            warn(task_id, "independent QA evidence is missing a valid Verdict")


def main() -> int:
    active = active_entries()
    candidates: set[str] = {task_id for task_id, entry in active.items() if entry.get("Closeout Contract") == "v1"}
    for directory in (HANDOFFS, QA):
        if directory.is_dir():
            for path in directory.glob("*.md"):
                text = path.read_text(encoding="utf-8")
                if field(text, "Closeout Contract") == "v1" or "## Closeout Synchronization" in text:
                    task_id = field(text, "Task ID")
                    if task_id:
                        candidates.add(task_id)
    for task_id in sorted(candidates):
        check_task(task_id, active.get(task_id, {}), find_task_file(HANDOFFS, task_id), find_task_file(QA, task_id))
    print(f"INFO closeout v1 tasks checked: {len(candidates)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
