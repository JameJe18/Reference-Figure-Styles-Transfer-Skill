# Style Extraction Guide

Use this guide when turning a paper, PDF, figure set, or screenshot into a
reusable `StyleLearningBundle`.

## 1. Inventory the Evidence

Record for every figure:

- figure number and PDF/page location;
- full caption;
- local extracted image path and native pixel size;
- whether the image is a direct embedded asset, a page render, or a crop;
- keep/drop/uncertain status and reason;
- whether the caption and visible panel labels agree.

For PDFs, prefer the embedded figure asset over a screenshot. Use page renders
when the figure contains vector shapes, page-level text, or panels split across
multiple embedded images.

Do not infer an exact scientific topology from spatial proximity alone. Read the
caption and inspect arrows, labels, and legends.

## 2. Separate Semantics From Style

Keep two ledgers for every figure.

### Semantic ledger

- components and roles;
- groups and hierarchy;
- directed, undirected, or decorative connections;
- reading order;
- legends and annotation meaning;
- scientific uncertainties or illegible content.

### Style ledger

- composition and panel geometry;
- visual family: flow, pipeline, loop, scatter, bar, box/strip, heatmap,
  matrix, forest, dumbbell, hybrid, or other;
- fills, outlines, stroke weights, connectors, arrows, markers;
- palette roles and approximate area concentration;
- typography character and hierarchy;
- whitespace, gutters, alignment, density;
- emphasis strategy;
- absent or deliberately avoided traits.

Never reuse a reference figure's scientific labels, values, or topology in a new
project unless the user explicitly asks for a faithful redraw.

## 3. Classify Figure Families

Do not force the whole paper into one family. Look for stable groups across
figures.

Likely families include:

- `conceptual_framework`: process diagrams, mechanism maps, study workflows,
  schema diagrams.
- `statistical_results`: plots with axes, distributions, comparisons, effect
  sizes, sample points, or heat maps.
- `hybrid`: a diagram panel with quantitative insets or mixed panel families.
- `editorial_illustration`: hand-drawn, painterly, or illustrated scientific
  concepts.

Record variation inside a family. For example, a paper may use sans-serif in its
workflow and serif in quantitative plots. Preserve that distinction when it is
repeatable; do not combine both within one axis system.

## 4. Sample the Palette

Start with stable, flat regions and solid markers:

1. Identify the canvas and neutral grays.
2. Sample the most frequent exact RGB values from large fills.
3. Separate fill colors from outlines and text accents.
4. Label anti-aliased or rare colors as approximate.
5. Assign semantic roles, not only hue names.

Useful roles:

- canvas;
- primary/secondary ink;
- neutral/control;
- primary comparison;
- alternate comparison;
- third series;
- highlight/leading result;
- uncertainty/background;
- exception/negative;
- framework region colors.

Record color usage rules:

- maximum number of saturated hues in a data panel;
- which hue is allowed for large areas;
- whether color must be paired with marker shape or line style;
- whether gray is reserved for controls/background;
- which colors are forbidden for neutral states.

Do not infer exact print contrast from thumbnail screenshots. If accessibility
matters, calculate contrast from sampled RGB values.

## 5. Characterize Typography

Raster pixels usually support character, not exact font identity.

Record:

- serif versus sans-serif character;
- bold/regular/italic hierarchy;
- panel letter treatment;
- title and axis label hierarchy;
- tick label orientation;
- direct-label and legend typography;
- any visible mixing of families.

State `exact_font_status: uncertain` unless fonts are available from source code,
SVG metadata, a document style sheet, or an editable figure file.

For a target paper width, provide functional point-size ranges. Do not convert
pixel heights to points without knowing the final placed width.

## 6. Measure Layout

Use normalized geometry:

- panel grid and relative panel widths;
- axis-to-axis horizontal and vertical gutters;
- outer margins;
- panel-letter offset;
- internal card padding;
- legend-to-data gap;
- density/overlap constraints.

When source axes are visible, use plot spines rather than text extents to estimate
grid gutters. Also report that long category labels can make the visual gutter
larger than the raw axis gap.

For diagram layouts, record:

- directed reading order;
- dominant region;
- asymmetry;
- nesting depth;
- open group containers;
- connector channels;
- bottom/side summary regions.

## 7. Characterize Marks and Strokes

Record the observable visual grammar:

- axes and spines;
- gridline presence and weight;
- reference/threshold lines;
- error bars and interval caps;
- dot/line/bar/box/histogram/heatmap marks;
- marker shapes and overlap policy;
- connector curvature, elbows, arrowheads, and line weights;
- corner rounding and border treatment;
- fill opacity and textures.

Use relative terms such as thin/medium/heavy and provide point-size estimates only
when the intended final width is known.

## 8. Analyze Emphasis and Density

For every family, state:

- what receives the strongest contrast;
- what remains pale or neutral;
- how the focal panel is distinguished;
- whether direct labels replace legends;
- whether the figure relies on one hero area or an evenly weighted grid;
- how dense background data is de-emphasized.

Return the paper with the final style profile.

## 9. Evidence Quality

Use:

- `high`: direct image inspection and stable source evidence;
- `partial`: legible but missing font/vector metadata or some ambiguous panels;
- `sparse`: low-resolution or partial figure evidence.

List uncertainties explicitly. Warnings are more useful than invented certainty.
