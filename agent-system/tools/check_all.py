#!/usr/bin/env python3
"""Run Agent System v0.1 report-only checks without mutating repository files."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    for name in ("check_active.py", "check_handoff_refs.py", "check_decision_ids.py"):
        print(f"== {name} ==", flush=True)
        subprocess.run([sys.executable, str(HERE / name)], check=False)
    print("INFO report-only mode complete; exit code remains 0 by design")
    return 0


if __name__ == "__main__":
    sys.exit(main())
