#!/usr/bin/env python3
"""Report-only consistency checks for decision records and the compact index."""
from __future__ import annotations

import re
import sys
import os
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_SYSTEM_ROOT", Path(__file__).resolve().parents[2]))
DECISIONS = ROOT / "agent-system" / "decisions"


def main() -> int:
    records: dict[str, Path] = {}
    for path in sorted(DECISIONS.glob("*.md")):
        if path.name == "index.md":
            continue
        match = re.search(r"^- Decision ID:\s*`?([^`\n]+?)`?\s*$", path.read_text(encoding="utf-8"), re.M)
        if not match:
            print(f"WARNING decision record missing Decision ID: {path.relative_to(ROOT)}")
            continue
        decision_id = match.group(1)
        if decision_id in records:
            print(f"WARNING duplicate Decision ID {decision_id}: {records[decision_id].name}, {path.name}")
        records[decision_id] = path
        supersedes = re.search(r"^- Supersedes:\s*`?([^`\n]+?)`?\s*$", path.read_text(encoding="utf-8"), re.M)
        if supersedes and supersedes.group(1).lower() not in {"none", "—", "-"} and supersedes.group(1) not in records:
            candidates = [p for p in DECISIONS.glob("*.md") if supersedes.group(1) in p.read_text(encoding="utf-8")]
            if not candidates:
                print(f"WARNING {decision_id} supersedes missing record: {supersedes.group(1)}")
    index = (DECISIONS / "index.md")
    index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
    for decision_id in records:
        if decision_id not in index_text:
            print(f"WARNING decision absent from index: {decision_id}")
    print(f"INFO decision records checked: {len(records)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
