#!/usr/bin/env python3
"""Report-only checks for the explicit Task fields in agent-system/active.md."""
from __future__ import annotations

import re
import sys
import os
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_SYSTEM_ROOT", Path(__file__).resolve().parents[2]))
ACTIVE = ROOT / "agent-system" / "active.md"
REQUIRED = ("Lifecycle", "Decision", "Verification", "Execution", "Handoff")


def main() -> int:
    if not ACTIVE.is_file():
        print(f"ERROR missing active register: {ACTIVE}")
        return 0
    lines = ACTIVE.read_text(encoding="utf-8").splitlines()
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines:
        match = re.match(r"^- (Task ID|Lifecycle|Decision|Verification|Execution|Handoff):\s*`?([^`]+?)`?\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if key == "Task ID":
            current = {key: value}
            entries.append(current)
        elif current is not None:
            current[key] = value
    seen: set[str] = set()
    for entry in entries:
        task_id = entry["Task ID"]
        if task_id in seen:
            print(f"WARNING duplicate active Task ID: {task_id}")
        seen.add(task_id)
        missing = [key for key in REQUIRED if not entry.get(key)]
        if missing:
            print(f"WARNING {task_id} missing fields: {', '.join(missing)}")
        if entry.get("Lifecycle") in {"COMPLETED", "ARCHIVED"}:
            print(f"WARNING {task_id} is {entry['Lifecycle']} but remains active")
    print(f"INFO active entries checked: {len(entries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
