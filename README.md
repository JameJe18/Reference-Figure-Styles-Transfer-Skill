# Reference figure styles transfer skill

A Codex skill for extracting the transferable visual grammar of scientific
figures and applying it to an existing plotting project.

The workflow keeps scientific content fixed while transferring:

- composition and panel hierarchy;
- palette roles and fill/outline behavior;
- typography character and scale;
- spacing, gutters, and panel geometry;
- marks, strokes, arrows, legends, and annotation strategy.

It is designed for two connected tasks:

1. Learn a style from a paper PDF or figure set and save a reusable
   `figure_style_profile.json`.
2. Restyle existing Matplotlib/R/plotting output by editing the original source
   files, preserving the prior outputs, and auditing scientific invariants.

## Install

The repository root is the skill directory. Clone it into your Codex skills
directory:

```text
<CODEX_HOME>/skills/reference-figure-styles-transfer/
```

On Windows PowerShell:

```powershell
git clone <REPOSITORY_URL> "$env:USERPROFILE\.codex\skills\reference-figure-styles-transfer"
```

If installing from a local archive instead, omit the `.git` directory when
copying the skill folder.

Invoke it explicitly:

```text
Use $reference-figure-styles-transfer to learn the style from paper.pdf and save a validated profile.
```

```text
Use $reference-figure-styles-transfer to apply the saved profile to my existing plotting code without changing any data or statistical wording.
```

## Included Assets

```text
reference-figure-styles-transfer/
|-- SKILL.md
|-- agents/openai.yaml
|-- references/
|   |-- audit.md
|   |-- case-study.md
|   |-- code-transfer.md
|   |-- style-extraction.md
|   `-- style-profile.schema.json
|-- scripts/
|   |-- audit_rendered_figures.py
|   |-- build_contact_sheet.py
|   |-- extract_pdf_figures.py
|   `-- validate_style_profile.py
|-- examples/example_style_profile.json
|-- tests/
|-- requirements.txt
`-- .github/workflows/ci.yml
```

No paper PDFs, third-party figure images, user project figures, or confidential
data are included.

## Quick Start

### 1. Extract candidates

```bash
python scripts/extract_pdf_figures.py paper.pdf -o style_work
```

If Poppler is unavailable, install it or use the PyMuPDF fallback:

```bash
python -m pip install -r requirements.txt
```

### 2. Build and validate the profile

Use [SKILL.md](SKILL.md) and
[references/style-extraction.md](references/style-extraction.md). The example
profile is at:

```text
examples/example_style_profile.json
```

Validate it:

```bash
python scripts/validate_style_profile.py \
  examples/example_style_profile.json
```

This template intentionally contains no local reference images, so validate it
without `--check-assets`. For a real profile with extracted assets:

```bash
python scripts/validate_style_profile.py \
  figure_style_profile.json --check-assets
```

### 3. Review the figures

```bash
python scripts/build_contact_sheet.py extracted-figures \
  -o figure_contact_sheet.jpg
```

### 4. Apply the style

Follow [references/code-transfer.md](references/code-transfer.md). The skill's
default policy is to edit the existing plotting source, keep scientific content
fixed, and render a variant before replacing accepted outputs.

### 5. Audit

```bash
python scripts/audit_rendered_figures.py \
  output/variant_style1 --profile figure_style_profile.json
```

Then complete the visual and scientific checks in
[references/audit.md](references/audit.md).

## Design Principles

- Style is learned by figure family, not averaged across unrelated figures.
- Scientific values, labels, axis limits, topology, and panel meaning remain
  fixed during a style-only pass.
- Exact fonts and vector line widths are not claimed from raster-only evidence.
- Strong color is concentrated on focal marks; large areas use restrained tints.
- Color is paired with shape, position, direct labels, or line style.
- Existing plotting files are modified; a separate decorative post-processing
  layer is not the default.
- Accepted outputs are preserved for before/after review.

## Dependencies

- Python 3.10+
- Pillow
- PyMuPDF for the embedded-image fallback
- Optional Poppler binaries: `pdfinfo`, `pdfimages`, `pdftoppm`, `pdftotext`

Matplotlib is used only by the target project, not required to validate profiles.

## Development

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/validate_style_profile.py examples/example_style_profile.json
```

## Repository Status

This folder is structured as a standalone GitHub repository and a directly
installable Codex skill. Add a license before public distribution if desired;
license choice is intentionally left to the repository owner.
