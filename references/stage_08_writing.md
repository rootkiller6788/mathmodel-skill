---
stage: 8
name: writing
duration_h: 12-30
inputs: ["decision_log.stages.0-7", "decision_log.competition", "decision_log.task_type"]
outputs:
  - "stage.8.{section_word_counts, figures_per_subproblem, tables_per_subproblem, abstract_drafts, ai_use_log, compliance}"
  - "paper_workspace/*.md"
  - "paper.tex"
loads_reference:
  - "competitions/<competition>/current_rules.md"
  - "competitions/<competition>/winning_patterns.md"
  - "competitions/<competition>/phrase_bank.md"
  - "competitions/<competition>/empirical.json"
loads_template:
  - "competitions/<competition>/paper_skeleton.md"
  - "competitions/<competition>/abstract_template.md"
  - "templates/latex/<competition>/"
feedback: ["L1", "L2_at_end"]
next: stage_09_review
---

# Stage 8 — Assemble the paper

Turn the validated Stage 0–7 outputs into one coherent paper. Do not invent new results while writing. If the paper exposes a modeling contradiction, record it and trigger a targeted L2 backtrack.

## 1. Lock the current rules first

1. Read `competitions/<competition>/current_rules.md` when present.
2. Open the linked official rules and confirm they are still current for the contest year.
3. Record the verification date, source URL, page/font/file-size limits, anonymity rules, and AI-disclosure requirements in `decision_log.compliance.ruleset`.
4. If the repository baseline conflicts with the official source, follow the official source and flag the repository mismatch.

Do not treat empirical distributions, `winning_patterns.md`, or rubric scores as official rules. They are writing aids only.

## 2. Load only the active competition pack

Read from `competitions/<competition>/`:

- `paper_skeleton.md`
- `abstract_template.md`
- `winning_patterns.md`
- `phrase_bank.md`
- `empirical.json`

For MCM and Diangong, `empirical.json` explicitly records `n=0` and provides no numeric distribution. For CUMCM, 91 source documents were collected but only 59 text-extractable documents entered the aggregate statistics; the values are observational baselines, not award thresholds.

## 3. Write into a stable workspace contract

Create these files under `<cwd>/paper_workspace/`:

| File | Content |
|---|---|
| `01_abstract.md` | Abstract or Summary Sheet, written last |
| `02_problem_restate.md` | Problem context and restatement |
| `03_analysis.md` | Decomposition and technical route |
| `04_assumptions.md` | Supported assumptions |
| `05_notation.md` | Unique symbols and units |
| `06_models.md` | Models, algorithms, results, and interpretation |
| `07_sensitivity.md` | Robustness and failure regions |
| `08_evaluation.md` | Strengths, limitations, and transfer conditions |
| `09_references.md` | Verified references, including AI tools when required |
| `10_appendix.md` | Essential code and supporting-material manifest |
| `11_ai_use_report.md` | MCM only: Report on Use of AI after the main solution |

`01_abstract.md` contains abstract/summary content without a top-level heading because the template supplies its wrapper. Files `02`–`10` each own one clear top-level Markdown heading; the MCM/Diangong templates intentionally do not print duplicate body headings. `11_ai_use_report.md` also omits its top-level heading because the MCM template supplies it.

Write the body first, then references and appendices, and write the abstract/summary last. Every number in the abstract must point to a result already present in the body.

## 4. Keep one evidence chain

For every subproblem, preserve this chain:

`question → assumptions → formulation → solver → result → validation → interpretation`

Before moving on, verify:

- symbols match Stage 4;
- chosen models match Stage 3;
- reported values match stored results rather than regenerated prose;
- figures have readable labels, units, captions, and source paths;
- claims and citations are verifiable;
- limitations name a concrete failure mode and mitigation.

## 5. Apply the competition branch

| Competition | Current repository baseline | Renderer |
|---|---|---|
| CUMCM | 2026 electronic paper: first page abstract, no commitment/numbering page, no TOC or identity; main text ≤30 pages; paper and support archive each ≤20 MB; AI disclosure and `AI工具使用详情.pdf` when AI is used | `xelatex` |
| MCM/ICM | COMAP 2027: complete main solution ≤25 pages including summary, TOC, references, appendices and code; English, ≥12pt; `Report on Use of AI` follows outside the 25-page solution | `pdflatex` |
| Diangong | Current official baseline: cover on page 1; title, abstract and keywords on page 2 with numbering starting at 1; body starts on page 3 with no TOC and is limited to 25 pages; appendices follow; A4 with 2.5 cm margins and Chinese body text in 小四; support ZIP/RAR ≤20 MB | `xelatex` |

Problem-specific deliverables such as letters or memos also count toward the applicable page limit unless the current official problem states otherwise.

## 6. Maintain the AI-use ledger

Because this skill itself uses an AI agent, keep `decision_log.compliance.ai_usage` current. For each material use, record:

- tool, provider, and model/version;
- use date, stage, and purpose;
- key prompt and key response, or paths to those records;
- what was adopted;
- human changes and verification performed.

Use `<skill>/scripts/render_ai_usage.py` in Stage 9 to generate the contest-specific disclosure artifact. Never place API keys, tokens, private data, or credentials in the ledger.

## 7. Render without detached sections

From the user project root, call the installed script explicitly:

```bash
python <skill>/scripts/render_paper.py \
  --competition <competition> \
  --workspace paper_workspace/ \
  --output-dir paper_output/
```

The renderer assembles CUMCM directly and automatically wires MCM/Diangong section files into `main.tex`. A generated PDF with missing section inputs is a failure even if LaTeX exits successfully.

## 8. Score using the active overlay

Use the five Stage 8 dimensions from `competitions/<competition>/rubric_overlay.json` when that competition overrides the baseline. Do not reuse CUMCM's five-part abstract dimensions for MCM or Diangong.

## Exit conditions

- all required sections and problem-specific deliverables exist;
- the paper agrees with the Stage 0–7 decision log;
- the current official rules were rechecked and recorded;
- AI uses and citations are logged;
- the active competition's renderer includes every section;
- L1 passes and the final L2 consistency check has no unresolved high-severity conflict.

Then enter `stage_09_review.md`.
