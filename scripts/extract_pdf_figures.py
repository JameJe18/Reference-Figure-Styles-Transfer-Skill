#!/usr/bin/env python3
"""Inventory figures, captions, embedded images, and page renders from a PDF.

The script produces evidence for style extraction. It is not a figure classifier:
the agent must still inspect the assets and decide which candidates are figures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_pdfinfo(pdf: Path) -> dict[str, object]:
    binary = shutil.which("pdfinfo")
    if not binary:
        return {}
    proc = run([binary, str(pdf)])
    if proc.returncode != 0:
        return {}
    fields: dict[str, object] = {}
    for line in proc.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if key in {"pages", "page_size"}:
            fields[key] = value
        elif key in {"title", "author", "subject", "keywords"}:
            fields[key] = value
    pages = fields.get("pages")
    if isinstance(pages, str) and pages.isdigit():
        fields["pages"] = int(pages)
    return fields


def read_pdf_text(pdf: Path) -> str:
    binary = shutil.which("pdftotext")
    if binary:
        proc = run([binary, "-layout", "-enc", "UTF-8", str(pdf), "-"])
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
    try:
        import fitz  # type: ignore
    except ImportError:
        return ""
    try:
        with fitz.open(pdf) as document:
            return "\f".join(page.get_text("text") for page in document)
    except Exception:
        return ""


def parse_captions(text: str) -> list[dict[str, object]]:
    """Extract likely figure captions while preserving page separators."""
    if not text:
        return []
    pattern = re.compile(
        r"(?im)^\s*(?:Figure|Fig\.)\s+(\d+)\s*[.:]\s*"
    )
    results: list[dict[str, object]] = []
    pages = text.split("\f")
    for page_index, page_text in enumerate(pages, start=1):
        matches = list(pattern.finditer(page_text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else None
            chunk = page_text[match.start():end].strip()
            # A figure caption is normally one paragraph. Stop before the first
            # blank line so body text/headings are not absorbed into the caption.
            paragraph_end = re.search(r"\n\s*\n", chunk)
            if paragraph_end:
                chunk = chunk[:paragraph_end.start()].strip()
            chunk = re.sub(r"(?<=[A-Za-z])-\s*\n\s*(?=[A-Za-z])", "", chunk)
            chunk = re.sub(r"(?<=[–—])\s*\n\s*", "", chunk)
            chunk = re.sub(r"\s+", " ", chunk)
            if len(chunk) > 1800:
                chunk = chunk[:1800].rsplit(" ", 1)[0] + "..."
            results.append(
                {
                    "figure_number": int(match.group(1)),
                    "page": page_index,
                    "caption": chunk,
                }
            )
    # PDF text order can repeat captions across columns. Keep the longest copy.
    deduplicated: dict[tuple[int, int], dict[str, object]] = {}
    for item in results:
        key = (int(item["figure_number"]), int(item["page"]))
        current = deduplicated.get(key)
        if current is None or len(str(item["caption"])) > len(str(current["caption"])):
            deduplicated[key] = item
    return sorted(deduplicated.values(), key=lambda item: (item["page"], item["figure_number"]))


def parse_pdfimages_list(pdf: Path) -> list[dict[str, object]]:
    binary = shutil.which("pdfimages")
    if not binary:
        return []
    proc = run([binary, "-list", str(pdf)])
    if proc.returncode != 0:
        return []
    rows: list[dict[str, object]] = []
    for line in proc.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("page", "-")):
            continue
        match = re.match(
            r"^(\d+)\s+(\d+)\s+"
            r"(image|smask|stencil)?\s*"
            r"(\d+)\s+(\d+)\s+",
            stripped,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        rows.append(
            {
                "page": int(match.group(1)),
                "index": int(match.group(2)),
                "type": (match.group(3) or "image").lower(),
                "width": int(match.group(4)),
                "height": int(match.group(5)),
            }
        )
    return rows


def image_size(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.width, image.height
    except Exception:
        return None, None


def reset_child_directory(parent: Path, name: str, overwrite: bool) -> Path:
    child = (parent / name).resolve()
    parent_resolved = parent.resolve()
    if parent_resolved not in child.parents:
        raise ValueError(f"Unsafe output path: {child}")
    if child.exists() and any(child.iterdir()):
        if not overwrite:
            raise FileExistsError(
                f"{child} is not empty; choose another output directory or pass --overwrite"
            )
        shutil.rmtree(child)
    child.mkdir(parents=True, exist_ok=True)
    return child


def extract_with_pdfimages(
    pdf: Path, output_dir: Path, overwrite: bool
) -> list[dict[str, object]]:
    binary = shutil.which("pdfimages")
    if not binary:
        return []
    embedded_dir = reset_child_directory(output_dir, "embedded", overwrite)
    prefix = embedded_dir / "image"
    proc = run([binary, "-all", str(pdf), str(prefix)])
    if proc.returncode != 0:
        proc = run([binary, "-png", str(pdf), str(prefix)])
    if proc.returncode != 0:
        return []

    files = sorted(
        path
        for path in embedded_dir.iterdir()
        if path.is_file() and path.name.startswith("image")
    )
    metadata = parse_pdfimages_list(pdf)
    results: list[dict[str, object]] = []
    for index, path in enumerate(files):
        meta = metadata[index] if index < len(metadata) else {}
        width, height = image_size(path)
        results.append(
            {
                "path": str(path.resolve()),
                "page": meta.get("page"),
                "index": meta.get("index", index),
                "width": meta.get("width", width),
                "height": meta.get("height", height),
                "backend": "pdfimages",
            }
        )
    return results


def extract_with_pymupdf(
    pdf: Path, output_dir: Path, overwrite: bool
) -> list[dict[str, object]]:
    try:
        import fitz  # type: ignore
    except ImportError:
        return []
    embedded_dir = reset_child_directory(output_dir, "embedded", overwrite)
    results: list[dict[str, object]] = []
    with fitz.open(pdf) as document:
        for page_number, page in enumerate(document, start=1):
            for image_index, image_info in enumerate(page.get_images(full=True)):
                xref = image_info[0]
                try:
                    pixmap = fitz.Pixmap(document, xref)
                    if pixmap.n - pixmap.alpha > 3:
                        pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
                    path = embedded_dir / (
                        f"image-p{page_number:03d}-{image_index:03d}.png"
                    )
                    pixmap.save(str(path))
                    results.append(
                        {
                            "path": str(path.resolve()),
                            "page": page_number,
                            "index": image_index,
                            "width": pixmap.width,
                            "height": pixmap.height,
                            "backend": "pymupdf",
                        }
                    )
                except Exception as exc:
                    results.append(
                        {
                            "path": None,
                            "page": page_number,
                            "index": image_index,
                            "error": str(exc),
                            "backend": "pymupdf",
                        }
                    )
    return results


def rasterize_pages(
    pdf: Path, output_dir: Path, pages: str, dpi: int, overwrite: bool
) -> list[dict[str, object]]:
    binary = shutil.which("pdftoppm")
    if not binary or pages.lower() in {"", "none"}:
        return []
    pages_dir = reset_child_directory(output_dir, "pages", overwrite)
    prefix = pages_dir / "page"
    cmd = [binary, "-png", "-r", str(dpi)]
    if pages.lower() != "all":
        if re.fullmatch(r"\d+", pages):
            cmd.extend(["-f", pages, "-l", pages])
        elif re.fullmatch(r"\d+\s*-\s*\d+", pages):
            first, last = re.split(r"\s*-\s*", pages)
            cmd.extend(["-f", first, "-l", last])
        else:
            raise ValueError("--pages accepts 'all', N, or N-M")
    proc = run([*cmd, str(pdf), str(prefix)])
    if proc.returncode != 0:
        return []
    results: list[dict[str, object]] = []
    for path in sorted(pages_dir.glob("page-*.png")):
        match = re.search(r"(\d+)$", path.stem)
        page = int(match.group(1)) if match else None
        width, height = image_size(path)
        results.append(
            {
                "path": str(path.resolve()),
                "page": page,
                "width": width,
                "height": height,
                "backend": "pdftoppm",
            }
        )
    return results


def filter_candidates(
    items: list[dict[str, object]], min_side: int, min_pixels: int
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    kept: list[dict[str, object]] = []
    dropped: list[dict[str, object]] = []
    for item in items:
        if not item.get("path"):
            dropped.append({**item, "filter": "extract_failed"})
            continue
        width = item.get("width")
        height = item.get("height")
        if not isinstance(width, int) or not isinstance(height, int):
            kept.append({**item, "filter": "unknown_size_kept"})
            continue
        if width < min_side or height < min_side or width * height < min_pixels:
            dropped.append(
                {
                    **item,
                    "filter": f"too_small ({width}x{height}, {width * height}px)",
                }
            )
        else:
            kept.append({**item, "filter": "size_ok"})
    return kept, dropped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument(
        "--backend",
        choices=["auto", "pdfimages", "pymupdf"],
        default="auto",
    )
    parser.add_argument(
        "--pages",
        default="all",
        help="Also rasterize all pages, one page, or an inclusive range",
    )
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--min-side", type=int, default=300)
    parser.add_argument("--min-pixels", type=int, default=90_000)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    pdf = args.pdf.expanduser().resolve()
    if not pdf.is_file():
        print(json.dumps({"ok": False, "error": f"PDF not found: {pdf}"}))
        return 2

    output_dir = args.output.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tools = {
        "pdfinfo": bool(shutil.which("pdfinfo")),
        "pdfimages": bool(shutil.which("pdfimages")),
        "pdftoppm": bool(shutil.which("pdftoppm")),
        "pdftotext": bool(shutil.which("pdftotext")),
        "pymupdf": False,
    }
    try:
        import fitz  # noqa: F401

        tools["pymupdf"] = True
    except ImportError:
        pass

    embedded: list[dict[str, object]] = []
    backend_used = None
    if args.backend in {"auto", "pdfimages"} and tools["pdfimages"]:
        embedded = extract_with_pdfimages(pdf, output_dir, args.overwrite)
        backend_used = "pdfimages" if embedded else None
    if not embedded and args.backend in {"auto", "pymupdf"} and tools["pymupdf"]:
        embedded = extract_with_pymupdf(pdf, output_dir, args.overwrite)
        backend_used = "pymupdf" if embedded else None

    pages = rasterize_pages(
        pdf,
        output_dir,
        str(args.pages),
        args.dpi,
        args.overwrite,
    )
    text = read_pdf_text(pdf)
    captions = parse_captions(text)
    kept, dropped = filter_candidates(
        [item for item in embedded if item.get("path")],
        args.min_side,
        args.min_pixels,
    )

    report = {
        "schema": "figure-style/PdfExtractionReport@1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": bool(kept or pages),
        "pdf": {
            "absolute_path": str(pdf),
            "sha256": sha256(pdf),
            **parse_pdfinfo(pdf),
        },
        "tools": tools,
        "backend_used": backend_used,
        "counts": {
            "embedded_extracted": len([item for item in embedded if item.get("path")]),
            "embedded_kept_by_size": len(kept),
            "embedded_dropped": len(dropped),
            "pages_rasterized": len(pages),
            "captions_detected": len(captions),
        },
        "captions": captions,
        "embedded_candidates": kept,
        "dropped_candidates": dropped,
        "page_renders": pages,
        "next_steps": [
            "Visually inspect candidates at original detail.",
            "Match embedded candidates to captions using page, dimensions, and content.",
            "Crop page renders only for figures that cannot be extracted intact.",
        ],
    }
    report_path = output_dir / "extract-report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
