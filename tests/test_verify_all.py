#!/usr/bin/env python3
"""Tests for the one-shot maintainer verifier scripts/verify_all.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_verify_all():
    path = ROOT / "scripts" / "verify_all.py"
    spec = importlib.util.spec_from_file_location("mathmodel_test_verify_all", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyAllTest(unittest.TestCase):
    def test_build_steps_covers_full_suite(self) -> None:
        mod = load_verify_all()
        names = [n for n, _ in mod.build_steps(doctor_skip_tools=True)]
        for expected in (
            "compile",
            "unittest",
            "doctor:cumcm",
            "doctor:mcm",
            "doctor:diangong",
            "git-diff-check",
        ):
            self.assertIn(expected, names)
        # doctor subcommands carry --skip-tools only when asked
        cumcm_cmd = dict(mod.build_steps(doctor_skip_tools=False))["doctor:cumcm"]
        self.assertNotIn("--skip-tools", cumcm_cmd)
        cumcm_cmd_skip = dict(mod.build_steps(doctor_skip_tools=True))["doctor:cumcm"]
        self.assertIn("--skip-tools", cumcm_cmd_skip)

    def test_cli_help_succeeds(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_all.py"), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--full", proc.stdout)


if __name__ == "__main__":
    unittest.main()
