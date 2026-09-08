#!/usr/bin/env python3
"""Tool-directory metadata contract.

Every tools/<tool> subtree keeps its entry SKILL.md (with non-empty name and
description frontmatter) plus a scripts/ directory, and the three tool
subdirectories that self-license keep their LICENSE.txt (see tools/README.md).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("figure", "paper_search", "docx", "xlsx", "pdf", "latex")
SELF_LICENSED = {"docx", "xlsx", "pdf"}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert m, "SKILL.md must start with YAML frontmatter"
    data = yaml.safe_load(m.group(1))
    assert isinstance(data, dict)
    return data


class ToolMetaTest(unittest.TestCase):
    def test_each_tool_has_skill_and_scripts(self) -> None:
        for tool in TOOLS:
            tool_dir = ROOT / "tools" / tool
            with self.subTest(tool=tool):
                skill = tool_dir / "SKILL.md"
                self.assertTrue(skill.is_file())
                meta = parse_frontmatter(skill.read_text(encoding="utf-8"))
                self.assertTrue(meta.get("name"))
                self.assertTrue(meta.get("description"))
                self.assertTrue((tool_dir / "scripts").is_dir())

    def test_self_licensed_tools_keep_license(self) -> None:
        for tool in SELF_LICENSED:
            with self.subTest(tool=tool):
                self.assertTrue(
                    (ROOT / "tools" / tool / "LICENSE.txt").is_file(),
                    f"{tool}/LICENSE.txt missing",
                )


if __name__ == "__main__":
    unittest.main()
