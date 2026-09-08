#!/usr/bin/env python3
"""Plugin attribution contract.

The LICENSE copyright owner and .codex-plugin/plugin.json attribution fields
must stay aligned (regression guard for a past drift where plugin.json still
pointed at the upstream author). Provenance of upstream merges belongs in
SOURCES.md, not in the fork's plugin identity.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = "rootkiller6788"


class PluginMetadataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.meta = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

    def test_author_points_at_fork_owner(self) -> None:
        self.assertEqual(self.meta["author"]["name"], OWNER)
        self.assertIn(OWNER, self.meta["author"]["url"])

    def test_repository_and_homepage_point_at_fork(self) -> None:
        self.assertIn(f"github.com/{OWNER}", self.meta["homepage"])
        self.assertIn(f"github.com/{OWNER}", self.meta["repository"])

    def test_interface_identity_aligned(self) -> None:
        ui = self.meta["interface"]
        self.assertEqual(ui["developerName"], OWNER)
        self.assertIn(OWNER, ui["websiteURL"])

    def test_license_owner_aligned(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn(OWNER, license_text)

    def test_skills_discovery_intact(self) -> None:
        skills_dir = ROOT / "skills" / "mathmodel-skill"
        self.assertTrue((skills_dir / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
