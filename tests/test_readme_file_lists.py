#!/usr/bin/env python3
"""README ↔ file-listing contract for competition packs.

Every bare `*.md` / `*.json` name referenced in a competition README (its
"文件清单"/file-listing tables and prose) must resolve to a real file inside
that same competition directory. Catches stale rows after renames or deletions.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETITIONS = ("cumcm", "mcm", "diangong")
TOKEN = re.compile(r"`([A-Za-z0-9_\-]+\.(?:md|json))`")


class ReadmeFileListTest(unittest.TestCase):
    def test_readme_referenced_files_exist(self) -> None:
        for comp in COMPETITIONS:
            comp_dir = ROOT / "competitions" / comp
            text = (comp_dir / "README.md").read_text(encoding="utf-8")
            referenced = sorted({m for m in TOKEN.findall(text)})
            self.assertGreaterEqual(
                len(referenced), 8, f"{comp}: README file list looks too thin"
            )
            for name in referenced:
                with self.subTest(comp=comp, file=name):
                    self.assertTrue(
                        (comp_dir / name).is_file(),
                        f"{comp}/README.md references missing {name}",
                    )


if __name__ == "__main__":
    unittest.main()
