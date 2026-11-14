#!/usr/bin/env python3
"""Audit regenerated figures for clipping, metadata, fonts, and palette tokens."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path


HEX = re.compile(r"#[0-9A-Fa-f]{6}")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;\"]+)", re.IGNORECASE)


def expand_paths(paths: list[Path], recursive: bool) -> list[Path]:
    output: list[Path] = []
    for path in paths:
        path = path.expanduser().resolve()
        if path.is_file():
            if path.suffix.lower() in {".png", ".svg"}:
                output.append(path)
        elif path.is_dir():
            iterator = path.rglob("*") if recursive else path.glob("*")
            output.extend(
                item
                for item in sorted(iterator)
                if item.is_file() and item.suffix.lower() in {".png", ".svg"}
            )
    return list(dict.fromkeys(output))


def collect_hex(value: object) -> set[str]:
    colors: set[str] = set()
    if isinstance(value, dict):
        for child in value.values():
            colors.update(collect_hex(child))
    elif isinstance(value, list):
        for child in value:
            colors.update(collect_hex(child))
    elif isinstance(value, str):
        colors.update(color.upper() for color in HEX.findall(value))
    return colors


def audit_png(path: Path, band: int, ink_threshold: int) -> dict[str, object]:
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        return {"status": "unverified", "error": f"missing dependency: {exc}"}

    with Image.open(path) as image:
        source_mode = image.mode
        dpi = image.info.get("dpi")
        rgba = image.convert("RGBA")
        alpha = np.asarray(rgba.getchannel("A"))
        gray_image = image.convert("L") if source_mode != "RGBA" else rgba.convert("L")
        gray = np.asarray(gray_image)
        ink = gray < ink_threshold
        height, width = ink.shape
        edge_ink = {
            "left": int(ink[:, :band].sum()),
            "right": int(ink[:, -band:].sum()),
            "top": int(ink[:band, :].sum()),
            "bottom": int(ink[-band:, :].sum()),
        }
        corners = [
            rgba.getpixel((0, 0)),
            rgba.getpixel((width - 1, 0)),
            rgba.getpixel((0, height - 1)),
            rgba.getpixel((width - 1, height - 1)),
        ]
        return {
            "status": "pass" if sum(edge_ink.values()) == 0 else "fail",
            "width_px": width,
            "height_px": height,
            "mode": source_mode,
            "dpi": list(dpi) if isinstance(dpi, tuple) else dpi,
            "has_transparency": int(alpha.min()) < 255,
            "corner_pixels_rgba": corners,
            "edge_band_px": band,
            "edge_ink": edge_ink,
            "edge_clean": sum(edge_ink.values()) == 0,
        }


def audit_svg(path: Path, profile_colors: set[str]) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fonts = sorted(
        {
            re.sub(r"\s+", " ", match.strip())
            for match in FONT_FAMILY.findall(text)
        }
    )
    observed_colors = {color.upper() for color in HEX.findall(text)}
    matched = sorted(observed_colors & profile_colors)
    visible_text = re.findall(r"<text\b", text, flags=re.IGNORECASE)
    return {
        "status": "pass" if fonts else "unverified",
        "font_families": fonts,
        "visible_text_nodes": len(visible_text),
        "color_token_count": len(observed_colors),
        "profile_palette_matches": matched,
        "profile_palette_match_count": len(matched),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--band", type=int, default=3)
    parser.add_argument("--ink-threshold", type=int, default=250)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    files = expand_paths(args.paths, args.recursive)
    if not files:
        print(json.dumps({"ok": False, "error": "no PNG or SVG files found"}))
        return 2

    profile_colors: set[str] = set()
    profile_path = None
    if args.profile:
        profile_path = args.profile.expanduser().resolve()
        try:
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile_colors = collect_hex(profile)
        except Exception as exc:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": f"cannot load profile: {exc}",
                    }
                )
            )
            return 2

    entries: list[dict[str, object]] = []
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        common = {
            "path": str(path),
            "name": path.name,
            "sha256": digest,
            "bytes": path.stat().st_size,
        }
        if path.suffix.lower() == ".png":
            entries.append(
                {
                    **common,
                    **audit_png(path, max(1, args.band), args.ink_threshold),
                }
            )
        else:
            entries.append({**common, **audit_svg(path, profile_colors)})

    png_entries = [entry for entry in entries if entry["name"].lower().endswith(".png")]
    report = {
        "schema": "figure-style/RenderAudit@1",
        "profile": str(profile_path) if profile_path else None,
        "file_count": len(entries),
        "png_edge_clean_all": all(
            bool(entry.get("edge_clean")) for entry in png_entries
        )
        if png_entries
        else None,
        "all_required_checks_complete": all(
            entry.get("status") != "unverified" for entry in entries
        ),
        "entries": entries,
        "limitations": [
            "Programmatic checks do not verify scientific meaning or visual hierarchy.",
            "Inspect each final image at original detail before acceptance.",
        ],
    }
    if args.output:
        output = args.output.expanduser().resolve()
    else:
        first = files[0]
        output = first.parent / "render-audit.json"
        if output.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output = first.parent / f"render-audit-{stamp}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["all_required_checks_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
