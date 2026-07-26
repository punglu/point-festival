#!/usr/bin/env python3
"""Report-only validation for Closeout Contract v1 task records.

The checker deliberately distinguishes open work from completed, archived work.
It never mutates records and always returns zero: warnings are evidence for a
writer or reviewer, not a state transition or a CI gate.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


ROOT = Path(os.environ.get("AGENT_SYSTEM_ROOT", Path(__file__).resolve().parents[2]))
SYSTEM = ROOT / "agent-system"
ACTIVE = SYSTEM / "active.md"
RELAY = SYSTEM / "relay" / "current.md"
ACTIVE_HANDOFFS = SYSTEM / "handoffs" / "active"
ARCHIVE_HANDOFFS = SYSTEM / "handoffs" / "archive"
QA = SYSTEM / "qa"
GRADUATED = SYSTEM / "graduated"
ALLOWED_ROOTS = (
    "agent-system/handoffs/active/",
    "agent-system/handoffs/archive/",
    "agent-system/qa/",
)
AREA_VALUES = {
    "ACTIVE": {"UPDATED", "BLOCKED"},
    "HANDOFF": {"UPDATED", "BLOCKED"},
    "QA EVIDENCE": {"UPDATED", "BLOCKED"},
    "COVERAGE MAP": {"UPDATED", "NO_CHANGE_REQUIRED", "BLOCKED"},
    "CLOSEOUT GATE": {"PASS", "BLOCKED"},
}


def field(text: str, name: str) -> str | None:
    """Return a list field's same-line value, ``""`` when blank, else None.

    Horizontal whitespace is accepted, while both the match and captured value
    are constrained to the current LF or CRLF line.
    """
    match = re.search(
        rf"^[ \t]*-[ \t]*{re.escape(name)}:[ \t]*`?([^\r\n`]*)`?[ \t]*\r?$",
        text,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def task_records(path: Path) -> dict[str, dict[str, str]]:
    """Read Task-ID list records from active-style Markdown files."""
    records: dict[str, dict[str, str]] = {}
    if not path.is_file():
        return records
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- ([A-Za-z ][A-Za-z ]*):\s*`?([^`]+?)`?\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if key == "Task ID":
            current = {key: value}
            records[value] = current
        elif current is not None:
            current[key] = value
    return records


def markdown_files(directory: Path, recursive: bool = False) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(directory.rglob("*.md") if recursive else directory.glob("*.md"))


def documents_by_task(directory: Path, recursive: bool = False) -> dict[str, list[Path]]:
    documents: dict[str, list[Path]] = {}
    for path in markdown_files(directory, recursive):
        task_id = field(path.read_text(encoding="utf-8"), "Task ID")
        if task_id:
            documents.setdefault(task_id, []).append(path)
    return documents


def has_contract(text: str) -> bool:
    return field(text, "Closeout Contract") == "v1" or "## Closeout Synchronization" in text


def graduated_entries(task_id: str) -> list[Path]:
    """Return graduate index files containing a task ID entry.

    Graduation is a compact index rather than a task-shaped record, so match a
    literal Task ID token, not an assumed list format.
    """
    token = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(task_id)}(?![A-Za-z0-9-])")
    return [
        path
        for path in markdown_files(GRADUATED, recursive=True)
        if token.search(path.read_text(encoding="utf-8"))
    ]


def warn(task_id: str, message: str) -> None:
    print(f"[WARN] {task_id}: {message}")


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def permitted_path(path: str) -> bool:
    return path.startswith(ALLOWED_ROOTS) and (ROOT / path).is_file()


def closeout_warnings(task_id: str, handoff: Path) -> None:
    text = handoff.read_text(encoding="utf-8")
    if "## Closeout Synchronization" not in text:
        warn(task_id, "Closeout Synchronization block is missing")
        return
    statuses = {name: field(text, name) for name in AREA_VALUES}
    for name, allowed in AREA_VALUES.items():
        if statuses[name] not in allowed:
            warn(task_id, f"{name} has invalid or missing value: {statuses[name] or 'empty'}")
    if statuses["COVERAGE MAP"] == "NO_CHANGE_REQUIRED" and not field(text, "COVERAGE MAP Reason"):
        warn(task_id, "COVERAGE MAP is NO_CHANGE_REQUIRED but reason is empty")
    if statuses["CLOSEOUT GATE"] == "PASS":
        for name in ("ACTIVE", "HANDOFF", "QA EVIDENCE"):
            if statuses[name] != "UPDATED":
                warn(task_id, f"CLOSEOUT GATE is PASS while {name} is {statuses[name] or 'missing'}")
        if any(value == "BLOCKED" for value in statuses.values()):
            warn(task_id, "CLOSEOUT GATE is PASS while a closeout area is BLOCKED")
        block = text[text.find("## Closeout Synchronization"):]
        if re.search(r"(?:Closeout|CLOSEOUT) Gate PASS.{0,80}(?:QA PASS|Independent QA PASS)", block, re.I):
            warn(task_id, "CLOSEOUT GATE PASS is described as independent QA PASS")
    handoff_path = field(text, "HANDOFF Path")
    evidence_path = field(text, "QA Evidence Path")
    if not handoff_path:
        warn(task_id, "HANDOFF Path is missing")
    elif not permitted_path(handoff_path):
        warn(task_id, f"HANDOFF Path is not an allowed repository path: {handoff_path}")
    if not evidence_path:
        warn(task_id, "QA Evidence Path is missing")
    elif not permitted_path(evidence_path):
        warn(task_id, f"QA Evidence Path is not an allowed repository path: {evidence_path}")


def check_task(
    task_id: str,
    active: dict[str, str] | None,
    active_handoffs: list[Path],
    archived_handoffs: list[Path],
    evidence: list[Path],
    graduates: list[Path],
    relay_task_id: str | None,
) -> None:
    """Validate one v1 Task graph in either OPEN or ARCHIVED lifecycle mode."""
    active = active or {}
    open_candidate = bool(active or active_handoffs)
    archived_candidate = bool(archived_handoffs or graduates)
    if open_candidate and archived_candidate:
        if active and archived_handoffs:
            warn(task_id, "archived handoff exists but active record is still present")
        if active_handoffs and archived_handoffs:
            warn(task_id, "task exists in both handoffs/active and handoffs/archive")
        if active_handoffs and graduates:
            warn(task_id, "OPEN task is registered in graduated")
        return
    if not open_candidate and not archived_candidate:
        warn(task_id, "QA evidence declares Closeout Contract v1 but no active or archived handoff exists")
        return
    if open_candidate:
        if not active:
            warn(task_id, "active record is missing")
        elif not active.get("Lifecycle") or not active.get("Verification") or not active.get("Execution"):
            warn(task_id, "active record is missing lifecycle, verification, or execution state")
        if len(active_handoffs) != 1:
            warn(task_id, "OPEN task requires exactly one active handoff")
        if archived_handoffs:
            warn(task_id, "OPEN task has archived handoff")
        if graduates:
            warn(task_id, "OPEN task is registered in graduated")
        handoffs = active_handoffs
    else:
        if active:
            warn(task_id, "ARCHIVED task still has an active record")
        if active_handoffs:
            warn(task_id, "ARCHIVED task still has an active handoff")
        if len(archived_handoffs) != 1:
            warn(task_id, "ARCHIVED task requires exactly one archived handoff")
        if len(graduates) != 1:
            warn(task_id, "archived task is missing graduated entry" if not graduates else "task has duplicate graduated entries")
        if relay_task_id == task_id:
            warn(task_id, "archived task is still declared in relay/current.md")
        handoffs = archived_handoffs
    if len(evidence) != 1:
        warn(task_id, "QA evidence is missing" if not evidence else "task has duplicate QA evidence")
    for handoff in handoffs:
        text = handoff.read_text(encoding="utf-8")
        if field(text, "Task ID") != task_id:
            warn(task_id, f"Task ID does not match handoff: {repo_relative(handoff)}")
        closeout_warnings(task_id, handoff)
    for item in evidence:
        text = item.read_text(encoding="utf-8")
        if field(text, "Task ID") != task_id:
            warn(task_id, f"Task ID does not match QA evidence: {repo_relative(item)}")
        if field(text, "Independent from implementer") == "true":
            verdict = field(text, "Verdict")
            if verdict not in {"PASS", "CONDITIONAL", "BLOCKED", "HUMAN_GATE"}:
                warn(task_id, "independent QA evidence is missing a valid Verdict")


def main() -> int:
    active = task_records(ACTIVE)
    active_handoffs = documents_by_task(ACTIVE_HANDOFFS, recursive=True)
    archived_handoffs = documents_by_task(ARCHIVE_HANDOFFS, recursive=True)
    evidence = documents_by_task(QA)
    candidates: set[str] = {task_id for task_id, entry in active.items() if entry.get("Closeout Contract") == "v1"}
    for source in (active_handoffs, archived_handoffs, evidence):
        for task_id, paths in source.items():
            if any(has_contract(path.read_text(encoding="utf-8")) for path in paths):
                candidates.add(task_id)
    relay_task_id = field(RELAY.read_text(encoding="utf-8"), "Task ID") if RELAY.is_file() else None
    for task_id in sorted(candidates):
        check_task(
            task_id,
            active.get(task_id),
            active_handoffs.get(task_id, []),
            archived_handoffs.get(task_id, []),
            evidence.get(task_id, []),
            graduated_entries(task_id),
            relay_task_id,
        )
    print(f"INFO closeout v1 tasks checked: {len(candidates)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
