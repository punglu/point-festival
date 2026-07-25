#!/usr/bin/env python3
"""Report-only consistency checks for decision records and the compact index."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_SYSTEM_ROOT", Path(__file__).resolve().parents[2]))
DECISIONS = ROOT / "agent-system" / "decisions"


def main() -> int:
    records: dict[str, list[Path]] = {}
    supersedes_by_path: dict[Path, tuple[str, str]] = {}
    for path in sorted(DECISIONS.glob("*.md")):
        if path.name == "index.md":
            continue
        match = re.search(r"^- Decision ID:\s*`?([^`\n]+?)`?\s*$", path.read_text(encoding="utf-8"), re.M)
        if not match:
            print(f"WARNING decision record missing Decision ID: {path.relative_to(ROOT)}")
            continue
        decision_id = match.group(1)
        records.setdefault(decision_id, []).append(path)
        supersedes = re.search(r"^- Supersedes:\s*`?([^`\n]+?)`?\s*$", path.read_text(encoding="utf-8"), re.M)
        if supersedes:
            supersedes_by_path[path] = (decision_id, supersedes.group(1))
    for decision_id, paths in records.items():
        if len(paths) > 1:
            print(f"WARNING duplicate Decision ID {decision_id}: {', '.join(path.name for path in paths)}")
    decision_ids = set(records)
    for path, (decision_id, supersedes_id) in supersedes_by_path.items():
        if supersedes_id.lower() in {"none", "—", "-"}:
            continue
        if supersedes_id == decision_id:
            print(f"WARNING {decision_id} self-supersedes: {path.name}")
        elif supersedes_id not in decision_ids:
            print(f"WARNING {decision_id} supersedes missing record: {supersedes_id}")
    index = (DECISIONS / "index.md")
    index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
    index_ids = set(re.findall(r"^\|\s*`([^`]+)`\s*\|", index_text, re.M))
    for decision_id in decision_ids - index_ids:
        print(f"WARNING decision absent from index: {decision_id}")
    for decision_id in index_ids - decision_ids:
        print(f"WARNING index references missing decision record: {decision_id}")
    print(f"INFO decision records checked: {len(records)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
