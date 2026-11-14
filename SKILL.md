---
name: reference-figure-styles-transfer
description: Learn transferable visual style from scientific paper figures and apply it to existing plotting code or outputs without changing the science. Use for 论文配图风格学习、配色/字体/间距/形状提取、可复用风格档案、证据图的代码美化与风格保真检查. Do not use it to invent missing data, scientific topology, or a prompt-only AI illustration workflow.
metadata:
  version: "1.0.0"
  short-description: Learn paper figure style and transfer it to plotting code
---

# Reference figure styles transfer skill

Turn reference figures into a machine-readable style profile, then apply that
profile to existing scientific figures. Separate visual grammar from scientific
content so a restyled figure remains the same result.

## Invariants

- Preserve data values, axes and units, statistical annotations, scientific
  labels, panel count, topology, and output filenames unless the user explicitly
  requests a semantic change.
- Learn from figures by type. Do not average a conceptual flow diagram and a
  quantitative result plot into a fictitious single style.
- Transfer observable grammar: composition, hierarchy, palette roles, typography
  character, spacing, marks, strokes, fills, legends, and annotation strategy.
  Do not copy the reference paper's claims, labels, metrics, or method topology.
- Treat exact font family, true vector stroke width, and off-white colors in
  raster images as uncertain unless source metadata proves them.
- Update the project's existing plotting source files. Do not create a parallel
  "beautify.py" that owns the final figure.
- Preserve the prior outputs. Generate a named variant or backup before a first
  draft overwrites accepted artifacts.
- If the source contains both diagram and statistical styles, retain both
  families and apply the matching one to each target figure.

## Route the Request

Choose one mode from the user's goal; several modes may run in sequence.

### Learn style only

Produce an evidence-grounded style profile and extracted figure assets. Stop
after validation if the user did not ask to restyle a target.

1. Inventory the source and identify every main figure, caption, page, and source
   image. For a PDF, run:

   ```bash
   python <skill-root>/scripts/extract_pdf_figures.py PAPER.pdf -o STYLE_OUTPUT
   ```

2. Review the extracted assets at original detail. If a figure is vector-only or
   split across the page, inspect a full-page render and crop only after recording
   the page and figure number.

3. Read [style-extraction.md](references/style-extraction.md) before classifying
   layouts or building the profile.

4. Create one `figure_style_profile.json` using
   [style-profile.schema.json](references/style-profile.schema.json). Record a
   per-figure `ReferenceAnalysis` plus a shared but type-specific style model.

5. Build a contact sheet for review:

   ```bash
   python <skill-root>/scripts/build_contact_sheet.py figures/ \
     -o figure_contact_sheet.jpg
   ```

6. Validate the profile and all local asset paths:

   ```bash
   python <skill-root>/scripts/validate_style_profile.py figure_style_profile.json \
     --check-assets
   ```

### Apply a learned style

Read the saved profile first, then inspect the target project. Do not reopen
style selection unless the profile is missing or conflicts with the user's
explicit instruction.

1. Map target figures to reference families:
   conceptual workflow to `conceptual_framework`; quantitative panels to
   `statistical_results`; mixed output to explicit panel-level mapping.

2. Locate the active plotting source for each figure. Inspect configuration,
   data loading, figure layout, and the final output path before editing.

3. Read [code-transfer.md](references/code-transfer.md). Prefer a centralized
   style block when the project already has a shared plotting config. Otherwise
   add narrowly scoped helpers inside the owning plotting files.

4. Apply the smallest coherent style delta. Keep the scientific content and
   panel order fixed. A first draft should normally be rendered to a variant
   directory for side-by-side review.

5. Re-run every modified plotting script. If the project has a result validator,
   run it before and after the style change.

6. Inspect each regenerated figure at original detail and run:

   ```bash
   python <skill-root>/scripts/audit_rendered_figures.py OUTPUT_DIR \
     --profile figure_style_profile.json
   ```

7. Read [audit.md](references/audit.md) and report only evidence-backed checks.

### Audit an existing style transfer

Use the same audit script and checklist. Compare content-preservation first,
style fidelity second. A visually attractive image that changed labels,
statistics, edges, or panel meaning fails.

## Evidence Rules

- Record exact hex values only for observed stable fills or marks. Label
  anti-aliased or sampled edge colors as approximate.
- Infer font character, not an exact family, from raster-only figures.
- Use relative ranges for spacing and line weight when final print dimensions are
  unknown. Convert to point sizes only when the intended publication width is
  known.
- Record every per-figure uncertainty and a `confidence` value.
- Store source and extracted local paths in the profile. A GitHub repository may
  contain the workflow, but should not publish a third-party paper or user data
  without permission.

## Deliver

For learning, deliver the profile, extracted figure assets, contact sheet, and a
short statement of style families and limitations.

For application, deliver:

- the modified original plotting source files;
- a variant output or preserved before/after set;
- the style profile used;
- render paths in PNG/PDF/SVG when supported;
- validation results, including scientific-number checks and edge/clipping checks;
- residual font, color, layout, or reproduction limitations.

Read [case-study.md](references/case-study.md) only when a worked example would
help decide how a dual family (`workflow + statistical plots`) should be handled.
