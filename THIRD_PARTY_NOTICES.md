# Third-party notices

The original code, documentation, and LaTeX assembly templates in this repository are available under the root [MIT License](./LICENSE).

## Upstream skill provenance

This repository merges the core content of three MIT-licensed open-source skills. Full authorship, version, and contribution details are in [SOURCES.md](./SOURCES.md).

The merged repository is distributed under its own MIT license (see [LICENSE](./LICENSE)); the upstream components remain subject to their original MIT notices and are not relicensed.

## CUMCM template provenance

The CUMCM electronic-paper template at `templates/latex/cumcm/main.tex` was independently written for this repository from the public competition-format requirements. It does not copy or redistribute the source code, documentation, examples, or binary assets of `latexstudio/CUMCMThesis`; those files are not included in this release.

The template is an assembly aid, not an official CUMCM template or an endorsement by the contest organizer. The current official rules always take precedence.

## Sub-tool licenses

Several `tools/<tool>/` subdirectories carry their own license from their upstream source, which takes precedence over the root MIT license for the files inside that subtree:

- `tools/docx/LICENSE.txt` and `tools/xlsx/LICENSE.txt` — see the terms in each file.
- `tools/pdf/LICENSE.txt` — `tools/pdf/SKILL.md` additionally declares a Proprietary license in its frontmatter; read the full terms before distributing or reusing those files.
- `tools/figure`, `tools/paper_search`, and `tools/latex` commit no separate license file in this repository; confirm their distribution terms against the upstream provenance in [SOURCES.md](./SOURCES.md) before reuse rather than assuming the root MIT license applies to every file in those subtrees.

See [tools/README.md](./tools/README.md) for the tool index.

## Runtime dependencies

Tools and libraries such as Python, Pandoc, TeX Live, MiKTeX, XeLaTeX, pdfLaTeX, CTeX, Fandol, and the Python packages listed in the requirements files are installed separately by the user. They are not vendored by this repository and remain subject to their own licenses.

## External research material

Competition rules, linked papers, datasets, websites, trademarks, and other external sources are not relicensed by this repository's MIT License. Links, provenance notes, and derived descriptive statistics do not transfer ownership or redistribution rights. Users remain responsible for checking the terms that apply to any material they download or submit.
