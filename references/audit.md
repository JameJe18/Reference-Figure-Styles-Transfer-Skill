# Render and Style Audit

Audit scientific preservation first, then visual fidelity.

## Required Evidence

For every final figure, record:

- output path and format;
- image dimensions and DPI for raster output;
- source script and render command;
- profile used;
- reference figure family;
- whether it is a draft variant or accepted output.

## Checks

### 1. Scientific invariants

- Required components and panels are present.
- Arrows retain source, target, direction, and meaning.
- Labels and captions retain scientific meaning.
- Data counts, axes, units, transformations, thresholds, and annotations are
  unchanged.
- No reference-paper content was copied accidentally.

### 2. Typography and hierarchy

- Panel letters are consistent and readable.
- Titles, axes, ticks, legends, and annotations preserve hierarchy.
- Required text is present and not clipped.
- Font character matches the mapped reference family.
- Exact font claims are not made without metadata.

### 3. Layout

- Reading order remains clear.
- No panels overlap.
- No legends cover focal data.
- Long labels remain inside the canvas.
- Gutter and margin changes are intentional.
- A thumbnail-size check preserves the main comparison.

### 4. Marks and palette

- Colors follow the profile's semantic roles.
- Strong saturation is reserved for focal data.
- Neutral/control categories remain visually subordinate.
- Category distinctions use color plus shape/line/label.
- Black/gray axes are not replaced by a new decorative palette.
- Background, error, and uncertainty treatments match the profile.

### 5. Export integrity

- PNG is opaque where white is required.
- DPI and canva dimensions match the target contract.
- No transparent checkerboard or unintended crop.
- SVG/PDF text remains editable where the pipeline supports it.
- Legacy palette tokens are absent unless intentionally preserved.

### 6. Programmatic checks

Run:

```bash
python scripts/audit_rendered_figures.py OUTPUT_DIR \
  --profile figure_style_profile.json
```

The script checks edge ink, raster metadata, and visible SVG font/color tokens.
It does not replace visual inspection or scientific validation.

PNG DPI metadata may reflect the exporter default rather than the effective
placement resolution of an embedded PDF image. Report both when they differ.

## Verdict

Use:

- `pass`: no critical/major issue remains;
- `fail`: scientific content changed, text is unreadable, legends/data collide, or
  the style family is clearly wrong;
- `unverified`: a required asset or visual check could not be completed.

Minor spacing polish may remain if it does not alter meaning or readability.
