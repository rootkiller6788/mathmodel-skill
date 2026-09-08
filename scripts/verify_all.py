#!/usr/bin/env python3
"""One-shot repository verification for maintainers.

Runs the full verification suite from AGENTS.md and prints a per-step
PASS/FAIL summary. Exits non-zero if any step fails.

Steps (static by default; no Pandoc/TeX required):
  1. python -m compileall -q scripts templates/shared/code_starter
  2. python -m unittest discover -s tests -p 'test_*.py'
  3. python scripts/doctor.py --competition cumcm --skip-tools
  4. python scripts/doctor.py --competition mcm --skip-tools
  5. python scripts/doctor.py --competition diangong --skip-tools
  6. git diff --check

Usage:
  python scripts/verify_all.py            # default (doctor --skip-tools)
  python scripts/verify_all.py --full     # doctor without --skip-tools (needs Pandoc/TeX)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("compile", [sys.executable, "-m", "compileall", "-q", "scripts", "templates/shared/code_starter"]),
    ("unittest", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
]


def build_steps(doctor_skip_tools: bool) -> list[tuple[str, list[str]]]:
    doctor = [sys.executable, "scripts/doctor.py"]
    if doctor_skip_tools:
        doctor.append("--skip-tools")
    steps = list(STEPS)
    for comp in ("cumcm", "mcm", "diangong"):
        steps.append((f"doctor:{comp}", doctor + ["--competition", comp]))
    steps.append(("git-diff-check", ["git", "diff", "--check"]))
    return steps


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="run doctor without --skip-tools (requires Pandoc/TeX tooling)",
    )
    args = parser.parse_args()

    results = []
    for name, cmd in build_steps(doctor_skip_tools=not args.full):
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        tail = "".join(proc.stderr.splitlines()[-6:] + proc.stdout.splitlines()[-6:])
        results.append((name, proc.returncode == 0, tail))
        status = "PASS" if proc.returncode == 0 else "FAIL"
        print(f"[{status}] {name}")
        if proc.returncode != 0 and tail.strip():
            print("    " + tail.replace("\n", "\n    "))

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} steps passed")
    if failed:
        print("Failed: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
