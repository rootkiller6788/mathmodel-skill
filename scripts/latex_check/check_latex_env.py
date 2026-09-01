#!/usr/bin/env python3
"""Check local LaTeX class availability for modeling contest templates."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


CONTEST_ALIASES = {
    "mcm": "mcm-icm",
    "icm": "mcm-icm",
    "mcm-icm": "mcm-icm",
    "mcm/icm": "mcm-icm",
    "cumcm": "cumcm",
}


def kpsewhich(filename: str) -> str | None:
    if shutil.which("kpsewhich") is None:
        return None
    result = subprocess.run(
        ["kpsewhich", filename],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    path = result.stdout.strip()
    return path if result.returncode == 0 and path else None


def find_bibtex_command() -> str | None:
    for command in ("bibtex", "bibtex.original", "bibtex8", "bibtexu"):
        path = shutil.which(command)
        if path:
            return path
    return None


def normalize_contest(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-")
    try:
        return CONTEST_ALIASES[normalized]
    except KeyError as exc:
        allowed = ", ".join(sorted({"mcm-icm", "cumcm"}))
        raise argparse.ArgumentTypeError(f"unknown contest {value!r}; expected one of: {allowed}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contest",
        required=True,
        type=normalize_contest,
        metavar="{mcm-icm,cumcm}",
        help="Contest workflow to check. MCM/ICM requires mcmthesis; CUMCM can fall back to ctexart unless --strict-class is set.",
    )
    parser.add_argument(
        "--strict-class",
        action="store_true",
        help="For CUMCM, fail if cumcmthesis.cls is missing instead of allowing the ctexart fallback.",
    )
    parser.add_argument(
        "--use-ref-bib",
        action="store_true",
        help="Also verify that BibTeX is available for ref.bib workflows.",
    )
    return parser.parse_args()


def local_skill_file(filename: str, contest: str | None = None) -> str | None:
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent.parent
    candidates: list[Path] = [Path.cwd() / filename]
    if contest == "cumcm":
        candidates.append(root / "templates" / "latex-alt" / "cumcm" / filename)
    if contest == "mcm-icm":
        candidates.append(root / "templates" / "latex-alt" / "mcm-icm" / filename)
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def find_class_file(filename: str, contest: str | None = None) -> str | None:
    return local_skill_file(filename, contest) or kpsewhich(filename)


def report_class_file(filename: str, contest: str | None = None) -> str | None:
    path = find_class_file(filename, contest)
    if path:
        print(f"OK: {filename} found at {path}")
    else:
        print(f"MISSING: {filename}")
    return path


def report_kpsewhich(filename: str) -> str | None:
    path = kpsewhich(filename)
    if path:
        print(f"OK: {filename} found at {path}")
    else:
        print(f"MISSING: {filename}")
    return path


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    if shutil.which("kpsewhich") is None:
        print("ERROR: kpsewhich not found. Install TeX Live or MiKTeX and ensure it is on PATH.")
        return 1

    if args.contest == "mcm-icm":
        if not report_class_file("mcmthesis.cls", "mcm-icm"):
            failures.append("mcmthesis.cls")
            print(
                "Hint for MCM/ICM: install the package with `tlmgr install mcmthesis` "
                "or the MiKTeX package manager."
            )

    if args.contest == "cumcm":
        if report_class_file("cumcmthesis.cls", "cumcm"):
            print("CUMCM class mode: use `templates/latex-alt/cumcm/main-cumcmthesis.tex` or `templates/latex-alt/cumcm/main.tex`.")
        elif args.strict_class:
            failures.append("cumcmthesis.cls")
            print(
                "Hint for strict CUMCM: cumcmthesis is a common template class and may not be available "
                "through tlmgr. Download/provide the CUMCMThesis template locally or install it in your TeX tree."
            )
        else:
            print(
                "WARN: cumcmthesis.cls not found. Default CUMCM workflow should use "
                "`templates/latex-alt/cumcm/main-ctexart-fallback.tex`."
            )
            if not report_kpsewhich("ctexart.cls"):
                failures.append("ctexart.cls")
                print("Hint for CUMCM fallback: install the ctex package through TeX Live or MiKTeX.")

    if args.use_ref_bib:
        bibtex_path = find_bibtex_command()
        if bibtex_path is None:
            failures.append("bibtex")
            print("MISSING: bibtex")
            print("Hint for ref.bib: install BibTeX through TeX Live, MiKTeX, or your TeX package manager.")
        else:
            print(f"OK: BibTeX command found at {bibtex_path}")
        if args.contest == "cumcm":
            if not report_kpsewhich("gbt7714.sty"):
                failures.append("gbt7714.sty")
                print("Hint for CUMCM ref.bib: install the gbt7714 package, or switch citations to cite/unsrt.")
            if not report_kpsewhich("gbt7714-numerical.bst"):
                failures.append("gbt7714-numerical.bst")
                print("Hint for CUMCM ref.bib: install the gbt7714 bibliography style, or switch bibliography style to unsrt.")

    if failures:
        print("\nFAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nPASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
