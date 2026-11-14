#!/usr/bin/env python3
"""Build a labeled review contact sheet from local figure images."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}


def expand_inputs(inputs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(
                path
                for path in sorted(item.iterdir())
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
            )
        elif item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES:
            files.append(item)
        else:
            raise FileNotFoundError(f"not an image or image directory: {item}")
    return list(dict.fromkeys(path.resolve() for path in files))


def load_font(size: int):
    from PIL import ImageFont

    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--max-cell-width", type=int, default=1800)
    parser.add_argument("--max-cell-height", type=int, default=1200)
    parser.add_argument("--title", default="Figure style reference")
    parser.add_argument("--labels", nargs="*", default=None)
    args = parser.parse_args()

    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "Pillow is required: pip install Pillow",
                }
            )
        )
        return 2

    files = expand_inputs([path.expanduser().resolve() for path in args.images])
    if not files:
        print(json.dumps({"ok": False, "error": "no images found"}))
        return 2
    columns = max(1, args.columns)
    rows = math.ceil(len(files) / columns)
    margin = 70
    gap = 42
    title_height = 100
    label_height = 56
    cell_width = args.max_cell_width
    cell_height = args.max_cell_height + label_height
    canvas_width = 2 * margin + columns * cell_width + (columns - 1) * gap
    canvas_height = (
        title_height
        + 2 * margin
        + rows * cell_height
        + (rows - 1) * gap
    )
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(32)
    label_font = load_font(24)
    draw.text((margin, 30), args.title, fill="#202020", font=title_font)

    labels = args.labels or [path.stem for path in files]
    if len(labels) != len(files):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "--labels must match the number of images",
                }
            )
        )
        return 2

    entries: list[dict[str, object]] = []
    for index, (path, label) in enumerate(zip(files, labels)):
        row, column = divmod(index, columns)
        x = margin + column * (cell_width + gap)
        y = title_height + margin + row * (cell_height + gap)
        with Image.open(path) as source:
            image = source.convert("RGB")
            width, height = image.size
            thumb = ImageOps.contain(
                image,
                (cell_width - 30, args.max_cell_height - 20),
                Image.Resampling.LANCZOS,
            )
        draw.rounded_rectangle(
            (x, y, x + cell_width, y + cell_height),
            radius=18,
            outline="#D4D7DA",
            width=2,
        )
        draw.text((x + 18, y + 12), label, fill="#404040", font=label_font)
        image_x = x + (cell_width - thumb.width) // 2
        image_y = y + label_height + (args.max_cell_height - thumb.height) // 2
        canvas.paste(thumb, (image_x, image_y))
        entries.append(
            {
                "path": str(path),
                "label": label,
                "source_size": [width, height],
                "row": row,
                "column": column,
            }
        )

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() in {".jpg", ".jpeg"}:
        canvas.save(output, quality=92, optimize=True)
    else:
        canvas.save(output)
    print(
        json.dumps(
            {
                "ok": True,
                "output": str(output),
                "size": [canvas.width, canvas.height],
                "images": entries,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
