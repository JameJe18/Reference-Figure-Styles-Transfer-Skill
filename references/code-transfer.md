# Code-Native Style Transfer

Use this guide after a validated style profile exists and the user wants an
existing scientific figure restyled.

## 1. Preflight

Record:

- profile path and revision;
- target figure files and output paths;
- active plotting entry points;
- source data paths;
- existing validators/tests;
- output size, DPI, formats, and variant mechanism.

Read enough code to identify:

- shared configuration;
- palette sources;
- typography/rcParams;
- figure creation and panel geometry;
- helper functions for bars, points, heatmaps, legends, and annotations;
- export path and overwrite behavior.

Do not edit archived, deprecated, or unrelated plotting files.

## 2. Freeze Science

Before style changes, record invariants:

- row/sample counts and statistical values;
- axis limits and transformations;
- panel order and scientific labels;
- statistically meaningful line types or annotations;
- reference/control groups;
- output filename contract.

If a label is clipped or a legend overlaps, fix placement without changing its
meaning. If a target figure needs a different panel count or data content, ask or
route to a scientific figure redesign workflow.

## 3. Map Figure Types

Use explicit mappings:

```text
Target F1 workflow       -> conceptual_framework
Target F2 multi-panel   -> statistical_results
Target F3 schematic+plot -> hybrid rule
```

For a first draft, add a variant suffix/directory. Keep accepted outputs intact.

## 4. Implement in the Owning Source

Modify the original plotting files. A separate post-processing script that
recreates or overlays the final figure is not the default.

Prefer a centralized style block when one already exists. Otherwise add narrowly
scoped style constants/helpers in the figure scripts.

Good changes:

- one shared palette and typography configuration;
- named semantic color roles;
- reusable panel-title, pale-fill, marker, or legend helpers;
- corrected axes insets and explicit reserved label bands;
- deterministic output variant selection.

Avoid:

- replacing data arrays with visual approximations;
- changing thresholds to produce cleaner plots;
- deleting annotations because they collide;
- rewriting the whole plotting architecture during a style-only pass;
- adding a second hidden palette or one-off colors in multiple files.

## 5. Matplotlib Transfer Patterns

These are patterns, not mandatory constants. Take actual values from the profile.

### Typography and axes

```python
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "axes.linewidth": 0.65,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
})
```

Use sans-serif when the target maps to a sans-serif reference family.

### Framework diagram

- white canvas;
- flat pale semantic fills;
- same-hue darker outlines and headings;
- open dashed group containers;
- small arrowheads and thin connectors;
- one dominant central region;
- no shadows, 3D, gradients, or full-area saturation.

### Bars and stacked bars

When the reference uses bordered pale bars:

```python
facecolor=[tint(c, 0.38) for c in colors]
edgecolor=colors
linewidth=0.6
```

Keep direct values and category order. Do not change bar widths so much that
category membership becomes ambiguous.

### Scatter and strip plots

- use small pale background marks;
- reserve strong hue/size for the focal subset;
- pair color with marker shape;
- keep reference lines dotted and subordinate;
- avoid marker sizes that merge categories.

### Heatmaps

- use a diverging map only for signed values around zero;
- use a sequential map for nonnegative counts/scores;
- keep zero centered where required;
- preserve vmin/vmax and transformation semantics;
- use white or very pale neutral only when it has a defined midpoint.

### Legends and labels

- place one compact legend per panel or one shared legend if the reference does;
- move collisions into reserved bands rather than covering data;
- keep full scientific labels; shorten only with an explicit glossary.

## 6. Layout and Spacing

Check that new typography and legends still fit the existing canvas.

Typical failure:

- a font switch increases glyph width;
- a serif title collides with a note;
- an external legend overlaps subplot titles;
- long y tick labels clip at the left canvas edge.

Reserve explicit bands for titles, notes, legends, and rotated labels. Recalculate
panel rectangles when the old spacing was tuned for a different content density.

## 7. Render and Verify

Run every changed script. Then:

1. Check warnings and errors.
2. Run the project's numeric/data validator.
3. Compare image dimensions and output format.
4. Check four canvas edges for clipping.
5. Inspect at original detail.
6. Verify fonts in SVG or PDF metadata when available.
7. Check the final palette tokens.
8. Generate a before/after sheet.

Do not call a style transfer complete from successful execution alone.

## 8. Delivery

Report:

- files changed;
- figure outputs and their variant status;
- scientific invariants checked;
- style tokens/families used;
- tests and visual checks;
- residual uncertainty.
