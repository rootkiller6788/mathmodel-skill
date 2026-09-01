# Third-party notices

The original code, documentation, and LaTeX assembly templates in this repository are available under the root [MIT License](./LICENSE).

## Upstream skill provenance

This repository merges the core content of three MIT-licensed open-source skills. Each retains its own MIT copyright notice in its original upstream repository:

- [mathmodel-skill](https://github.com/handsomeZR-netizen/mathmodel-skill) (v6.1, © handsomeZR-netizen) — 10-stage workflow, L1–L4 feedback layers, competition packs, `decision_log.json` state, scoring scripts.
- [math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) (v1.2, © XiaoMaColtAI) — three-role engine (建模手/编程手/论文手), five-gate QA, algorithm assets, and the `tools/` toolchain.
- [mathmodel-latex-skill](https://github.com/wangling-miao/mathmodel-latex-skill) (v1.0.8, © wangling-miao) — LaTeX compile preflight, anonymity checks, and CUMCM excellent-paper style rules.

The merged repository is distributed under its own MIT license (see [LICENSE](./LICENSE)); the upstream components remain subject to their original MIT notices and are not relicensed.

## CUMCM template provenance

The CUMCM electronic-paper template at `templates/latex/cumcm/main.tex` was independently written for this repository from the public competition-format requirements. It does not copy or redistribute the source code, documentation, examples, or binary assets of `latexstudio/CUMCMThesis`; those files are not included in this release.

The template is an assembly aid, not an official CUMCM template or an endorsement by the contest organizer. The current official rules always take precedence.

## Runtime dependencies

Tools and libraries such as Python, Pandoc, TeX Live, MiKTeX, XeLaTeX, pdfLaTeX, CTeX, Fandol, and the Python packages listed in the requirements files are installed separately by the user. They are not vendored by this repository and remain subject to their own licenses.

## External research material

Competition rules, linked papers, datasets, websites, trademarks, and other external sources are not relicensed by this repository's MIT License. Links, provenance notes, and derived descriptive statistics do not transfer ownership or redistribution rights. Users remain responsible for checking the terms that apply to any material they download or submit.
