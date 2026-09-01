# Figure contract before plotting

A publication-quality scientific figure is a visual argument, not an isolated pretty plot. Every figure starts from a claim, an evidence hierarchy, and a review-risk check before code or aesthetics. Before generating or editing code, establish the contract below.

## Backend selection follows the modeling language

This skill supports **Python** and **MATLAB** as plotting backends. The backend is determined by the modeling language already chosen in the pipeline (编程手 selects Python or MATLAB in step 1). Do not ask the user to choose a plotting language separately—reuse the modeling language already in use for that question.

- If the task uses Python for modeling, plot with the Python toolchain (`setup_style.py`, `export_figure.py`, `visual_qa.py`).
- If the task uses MATLAB for modeling, plot with the MATLAB toolchain (`apply_publication_style.m`, `export_publication_figure.m`).

There is no R backend in this skill. Any reference to R, `nature_figure_backend.py set r`, or `backend-selection.md` in upstream documents is obsolete and must be ignored.

## The selected backend is exclusive

Once Python or MATLAB is selected, every plotting script, preview image, SVG/PDF/PNG export, QA render, and visual workaround must be produced by that same backend. Do not use Python to draw a preview for a MATLAB figure, and do not use MATLAB to draw a preview for a Python figure, even if the selected runtime or packages are missing locally. The non-selected language may only be used for non-visual file inspection or data conversion when it does not open a graphics device, import plotting libraries, create image/vector files, or change the final visual appearance.

## Missing runtime/package rule

After the backend is selected, check the selected runtime early (MATLAB toolboxes for MATLAB; Python and required plotting packages for Python). If the selected runtime or required packages are unavailable, stop before rendering and report the exact blocker. You may provide a selected-backend script and installation commands, or ask permission to install dependencies, but you must not fall back to the other language to make a substitute figure.

## Data-integrity gate

Use all user-provided observations and requested variables unless an exclusion has a scientific or statistical justification or the user explicitly requests a subset. Never reduce data merely to make a plot easier or faster to render. For large point clouds, prefer rasterized marks, hexbin/density representations, aggregation with a stated rule, or another backend-native rendering strategy.

If any row, column, replicate, image, or category is excluded, record the before/after counts, the exact rule, and the reason in the QA notes. Preserve the unmodified source data and never silently select convenient columns to satisfy a template.

## The five-point contract

1. **Core conclusion**: write the one-sentence claim the figure must defend.
2. **Evidence chain**: map each planned panel to the claim, and drop panels that do not carry a unique piece of evidence.
3. **Archetype**: classify the figure as `quantitative grid`, `schematic-led composite`, `image plate + quant`, or `asymmetric mixed-modality figure`.
4. **Backend**: use the explicit Python/MATLAB track exclusively for all figure drawing, previewing, exporting, and visual QA. Do not cross-render with the other language.
5. **Journal/export contract**: set final dimensions, editable text, source data, statistics, image-integrity notes, and export formats before styling.

The highest-priority rule is: **the chart serves the scientific logic**. Aesthetic polish, template matching, and complex layout are subordinate to making the core conclusion clear, defensible, and reviewable.

For the full method to convert a request into core conclusion, evidence hierarchy, panel map, and review-risk checks, open `references/figure-contract.md`.
