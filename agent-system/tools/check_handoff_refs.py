#!/usr/bin/env python3
"""Report-only validation of explicit active-task handoff references."""
from __future__ import annotations

import re
import sys
import os
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_SYSTEM_ROOT", Path(__file__).resolve().parents[2]))
ACTIVE = ROOT / "agent-system" / "active.md"
PREFIX = "agent-system/handoffs/active/"


def main() -> int:
    if not ACTIVE.is_file():
        print(f"ERROR missing active register: {ACTIVE}")
        return 0
    refs = re.findall(r"^- Handoff:\s*`?([^`\n]+?)`?\s*$", ACTIVE.read_text(encoding="utf-8"), re.M)
    for ref in refs:
        if not ref.startswith(PREFIX):
            print(f"WARNING handoff outside active handoff directory: {ref}")
            continue
        if not (ROOT / ref).is_file():
            print(f"WARNING missing handoff: {ref}")
    print(f"INFO handoff references checked: {len(refs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
