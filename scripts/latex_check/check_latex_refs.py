#!/usr/bin/env python3
r"""Check LaTeX \ref/\eqref labels and \cite keys for math modeling papers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REF_COMMANDS = ("ref", "eqref", "pageref", "autoref", "nameref", "cref", "Cref")
CITE_RE = re.compile(r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear)(?:\[[^\]]*\])*\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
BIBITEM_RE = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}")
BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)", re.MULTILINE)


def strip_verbatim(text: str) -> str:
    # Ignore examples inside verbatim-like content so placeholders such as
    # \verb|\cite{...}| are not mistaken for real citations.
    text = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\\verb(.).*?\1", "", text)
    return text


def strip_comments(text: str) -> str:
    text = strip_verbatim(text)
    out: list[str] = []
    for line in text.splitlines():
        i = 0
        cut = len(line)
        while True:
            j = line.find('%', i)
            if j == -1:
                break
            # Count immediately preceding backslashes. Odd means escaped percent.
            bs = 0
            k = j - 1
            while k >= 0 and line[k] == '\\':
                bs += 1
                k -= 1
            if bs % 2 == 0:
                cut = j
                break
            i = j + 1
        out.append(line[:cut])
    return "\n".join(out)


def read_tex_recursive(path: Path, seen: set[Path] | None = None) -> str:
    if seen is None:
        seen = set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = path.read_text(encoding="utf-8")
    base = path.parent

    def replace_input(match: re.Match[str]) -> str:
        name = match.group(2).strip()
        child = base / name
        if child.suffix == "":
            child = child.with_suffix(".tex")
        if child.exists():
            return "\n" + read_tex_recursive(child, seen) + "\n"
        return match.group(0)

    return re.sub(r"\\(input|include)\{([^{}]+)\}", replace_input, text)


def split_keys(raw: str) -> list[str]:
    return [k.strip() for k in raw.split(',') if k.strip()]


def parse_bib_files(tex_path: Path, text: str, explicit_bibs: list[str]) -> set[str]:
    bib_files: list[Path] = []
    for bib in explicit_bibs:
        p = Path(bib)
        if not p.is_absolute():
            p = tex_path.parent / p
        if p.suffix == "":
            p = p.with_suffix(".bib")
        bib_files.append(p)
    for match in re.finditer(r"\\bibliography\{([^{}]+)\}", text):
        for name in split_keys(match.group(1)):
            p = tex_path.parent / name
            if p.suffix == "":
                p = p.with_suffix(".bib")
            bib_files.append(p)

    keys: set[str] = set(BIBITEM_RE.findall(text))
    missing_files: list[Path] = []
    for bib in bib_files:
        if not bib.exists():
            missing_files.append(bib)
            continue
        keys.update(BIB_ENTRY_RE.findall(bib.read_text(encoding="utf-8")))
    if missing_files:
        print("MISSING BIB FILES:")
        for bib in missing_files:
            print(f"- {bib}")
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", help="Main .tex file")
    parser.add_argument("--bib", action="append", default=[], help="Additional .bib file to check, e.g. --bib ref.bib")
    args = parser.parse_args()

    tex_path = Path(args.tex).resolve()
    if not tex_path.exists():
        print(f"ERROR: tex file not found: {tex_path}")
        return 2

    raw_text = read_tex_recursive(tex_path)
    text = strip_comments(raw_text)

    labels = LABEL_RE.findall(text)
    label_set = set(labels)
    duplicate_labels = sorted({x for x in labels if labels.count(x) > 1})

    ref_uses: list[str] = []
    for cmd in REF_COMMANDS:
        ref_uses.extend(re.findall(rf"\\{cmd}\{{([^{{}}]+)\}}", text))
    ref_keys = sorted({k for raw in ref_uses for k in split_keys(raw)})
    missing_labels = [k for k in ref_keys if k not in label_set]

    cite_keys = sorted({k for raw in CITE_RE.findall(text) for k in split_keys(raw)})
    bib_keys = parse_bib_files(tex_path, text, args.bib)
    missing_cites = [k for k in cite_keys if k not in bib_keys]

    ok = True
    if duplicate_labels:
        ok = False
        print("DUPLICATE LABELS:")
        for key in duplicate_labels:
            print(f"- {key}")
    if missing_labels:
        ok = False
        print("MISSING LABEL TARGETS:")
        for key in missing_labels:
            print(f"- {key}")
    if missing_cites:
        ok = False
        print("MISSING CITATION KEYS:")
        for key in missing_cites:
            print(f"- {key}")
    if not ok:
        print("\nFAILED")
        return 1

    print(f"PASSED: {len(label_set)} labels, {len(ref_keys)} cross-references, {len(cite_keys)} citation keys checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
