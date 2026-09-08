#!/usr/bin/env python3
"""Contract tests for competition packs.

Guards the maintainer invariants documented in AGENTS.md:
each competition directory keeps its full common-core artifact set, and
current_rules.md carries a verified-on ISO date plus an official source URL.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETITIONS = ("cumcm", "mcm", "diangong")

# Present in every competition pack (beyond its own extra files).
COMMON_CORE = (
    "abstract_template.md",
    "anti_patterns.md",
    "current_rules.md",
    "empirical.json",
    "empirical_notes.md",
    "paper_skeleton.md",
    "phrase_bank.md",
    "rubric_overlay.json",
    "topic_specs.json",
    "winning_patterns.md",
)

VERIFIED_MARKERS = ("Last verified", "最近核对")


class CompetitionPackContractTest(unittest.TestCase):
    def test_common_core_files_present(self) -> None:
        for comp in COMPETITIONS:
            comp_dir = ROOT / "competitions" / comp
            self.assertTrue(comp_dir.is_dir(), f"missing competition dir {comp}")
            for name in COMMON_CORE:
                with self.subTest(comp=comp, file=name):
                    self.assertTrue(
                        (comp_dir / name).is_file(),
                        f"{comp}/{name} missing from common-core set",
                    )

    def test_current_rules_have_verified_date_and_source(self) -> None:
        iso = re.compile(r"\d{4}-\d{2}-\d{2}")
        url = re.compile(r"https?://")
        for comp in COMPETITIONS:
            text = (ROOT / "competitions" / comp / "current_rules.md").read_text(
                encoding="utf-8"
            )
            with self.subTest(comp=comp):
                self.assertTrue(iso.search(text), f"{comp}: no ISO date")
                self.assertTrue(
                    any(m in text for m in VERIFIED_MARKERS),
                    f"{comp}: missing verified-on marker",
                )
                self.assertTrue(url.search(text), f"{comp}: no official source URL")

    def test_json_artifacts_parse(self) -> None:
        for comp in COMPETITIONS:
            for name in ("topic_specs.json", "rubric_overlay.json", "empirical.json"):
                with self.subTest(comp=comp, file=name):
                    json.loads(
                        (ROOT / "competitions" / comp / name).read_text(
                            encoding="utf-8"
                        )
                    )

    def test_anti_patterns_not_empty(self) -> None:
        for comp in COMPETITIONS:
            text = (ROOT / "competitions" / comp / "anti_patterns.md").read_text(
                encoding="utf-8"
            )
            self.assertGreater(
                len([ln for ln in text.splitlines() if ln.strip()]),
                10,
                f"{comp}: anti_patterns.md looks empty",
            )


if __name__ == "__main__":
    unittest.main()
