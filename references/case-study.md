# Sanitized Case Study: Workflow Plus Result Panels

This case summarizes the workflow that led to the skill without including the
source paper, third-party figures, or project result images.

## Situation

- A reference paper contained one conceptual workflow figure and several
  quantitative result figures.
- The target project contained one workflow figure plus four multi-panel result
  figures.
- The target figures were already scientifically reviewed; the requested change
  was style only.

## Style Findings

The reference did not have one uniform style.

### Conceptual family

- white canvas;
- pale semantic region fills;
- darker same-hue outlines and headings;
- rounded cards inside dashed group containers;
- thin arrows with small heads;
- sans-serif typography;
- central model/decision region visually dominant.

### Statistical family

- white canvas and minimal chart chrome;
- thin left/bottom axes;
- serif typography;
- blue/orange/teal categorical vocabulary;
- gray for controls and backgrounds;
- color plus marker shape;
- pale background points with strong focal marks;
- compact legends and direct annotations;
- 1x2, 1x3, or 2x2 panel grids.

## Application Pattern

1. Map the target workflow to the conceptual family.
2. Map each target multi-panel result to the statistical family.
3. Update shared color and typography configuration.
4. Keep all data and panel meanings unchanged.
5. Render a named variant rather than overwriting accepted figures.
6. Fix newly exposed collisions caused by longer serif labels and added notes.
7. Run the project's numeric validator.
8. Check edge clipping, fonts in SVG, old palette absence, output sizes, and
   before/after images.

## Useful Lessons

- A style transfer can expose pre-existing layout defects. Fix spacing, not
  science.
- A title note and legend need explicit bands; neither should share a baseline
  with panel titles.
- A global palette change can affect supplementary figures later. Document that
  scope and rerun their validators before publication.
- A first draft should preserve prior outputs; promotion to official filenames
  should follow user acceptance.
