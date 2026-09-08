#!/usr/bin/env python3
"""Parity tests for mirrored LaTeX build files.

The repository keeps two copies of the CUMCM latexmkrc on purpose: the root
one used by the primary pipeline and the one bundled with the latex-alt
fallback class. This test pins that they stay in sync, and that the canonical
templates/latex/<comp>/main.tex tree used by scripts/render_paper.py exists
for every competition.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETITIONS = ("cumcm", "mcm", "diangong")


class MirrorParityTest(unittest.TestCase):
    def test_cumcm_latexmkrc_parity(self) -> None:
        root_rc = ROOT / "latexmkrc"
        alt_rc = ROOT / "templates" / "latex-alt" / "cumcm" / "latexmkrc"
        self.assertTrue(root_rc.is_file())
        self.assertTrue(alt_rc.is_file())
        self.assertEqual(
            root_rc.read_text(encoding="utf-8"),
            alt_rc.read_text(encoding="utf-8"),
            "root latexmkrc and latex-alt/cumcm/latexmkrc drifted apart",
        )

    def test_canonical_template_tree_present(self) -> None:
        # render_paper.py assembles only templates/latex/<comp>/main.tex.
        for comp in COMPETITIONS:
            main = ROOT / "templates" / "latex" / comp / "main.tex"
            with self.subTest(comp=comp):
                self.assertTrue(
                    main.is_file(), f"canonical template missing: {main.relative_to(ROOT)}"
                )
                self.assertGreater(main.stat().st_size, 500)


if __name__ == "__main__":
    unittest.main()
