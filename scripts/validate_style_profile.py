#!/usr/bin/env python3
"""Validate a figure-style StyleLearningBundle and optional local assets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


EXPECTED_SCHEMA = "figure-style/StyleLearningBundle@1"
LEGACY_SCHEMA = "academic-figure/StyleLearningBundle@1"
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def resolve_asset(base: Path, value: str | None) -> Path | None:
    if not value or is_url(value):
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def collect_color_strings(value: object, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(collect_color_strings(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(collect_color_strings(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if re.search(r"#[0-9A-Fa-f]{6}", value):
            found.append((path, value))
    return found


def validate(profile: dict[str, object], profile_path: Path, check_assets: bool) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    schema = profile.get("schema")
    if schema == LEGACY_SCHEMA:
        warnings.append(
            "legacy academic-figure/StyleLearningBundle@1 accepted; "
            "new profiles should use figure-style/StyleLearningBundle@1"
        )
    elif schema != EXPECTED_SCHEMA:
        errors.append(
            f"schema must be {EXPECTED_SCHEMA!r} "
            f"(or legacy {LEGACY_SCHEMA!r})"
        )
    if not isinstance(profile.get("version"), str) or not profile.get("version"):
        if schema == LEGACY_SCHEMA:
            warnings.append("legacy profile has no version; inferred compatibility mode")
        else:
            errors.append("version must be a non-empty string")

    source = profile.get("source_document")
    if not isinstance(source, dict) or not source.get("absolute_path"):
        errors.append("source_document.absolute_path is required")
        source = {}

    inventory = profile.get("inventory")
    if not isinstance(inventory, dict):
        errors.append("inventory must be an object")
        inventory = {}
    figure_count = inventory.get("figure_count")
    inventory_figures = inventory.get("figures")
    if schema == LEGACY_SCHEMA:
        if figure_count is None:
            figure_count = inventory.get("main_figures_found")
        if inventory_figures is None:
            inventory_figures = inventory.get("figure_list")
    if not isinstance(figure_count, int) or figure_count < 0:
        errors.append("inventory.figure_count must be a non-negative integer")
    if not isinstance(inventory_figures, list):
        errors.append("inventory.figures must be an array")
        inventory_figures = []
    if isinstance(figure_count, int) and figure_count != len(inventory_figures):
        errors.append(
            "inventory.figure_count does not match inventory.figures length"
        )

    shared = profile.get("shared_style_model")
    required_shared = [
        "design_positioning",
        "style_families",
        "palette",
        "typography",
        "geometry_and_spacing",
        "marks_and_strokes",
        "avoid",
    ]
    if not isinstance(shared, dict):
        errors.append("shared_style_model must be an object")
        shared = {}
    for key in required_shared:
        legacy_equivalent = (
            schema == LEGACY_SCHEMA
            and key == "marks_and_strokes"
            and "line_and_shape_grammar" in shared
        )
        if key not in shared and not legacy_equivalent:
            errors.append(f"shared_style_model.{key} is required")
    families = shared.get("style_families")
    if not isinstance(families, dict) or not families:
        errors.append("shared_style_model.style_families must be a non-empty object")
    else:
        required_family_fields = [
            "composition",
            "regions",
            "marks",
            "strokes",
            "fills",
            "color_roles",
            "typography",
            "emphasis",
            "avoid",
        ]
        for family, grammar in families.items():
            if not isinstance(grammar, dict):
                errors.append(f"style family {family!r} must be an object")
                continue
            for field in required_family_fields:
                if field not in grammar:
                    errors.append(f"style family {family!r} is missing {field!r}")

    transfer = profile.get("transfer_policy")
    if not isinstance(transfer, dict):
        errors.append("transfer_policy must be an object")
        transfer = {}
    for key in ("reuse", "do_not_copy"):
        value = transfer.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"transfer_policy.{key} must be a non-empty array")

    figures = profile.get("figures")
    if not isinstance(figures, list) or not figures:
        errors.append("figures must be a non-empty array")
        figures = []
    seen_ids: set[str] = set()
    for index, figure in enumerate(figures):
        prefix = f"figures[{index}]"
        if not isinstance(figure, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if figure.get("schema") not in {
            "academic-figure/ReferenceAnalysis@1",
            "figure-style/ReferenceAnalysis@1",
        }:
            errors.append(
                f"{prefix}.schema must be "
                "'academic-figure/ReferenceAnalysis@1'"
            )
        reference_id = figure.get("reference_id")
        if not isinstance(reference_id, str) or not reference_id:
            errors.append(f"{prefix}.reference_id is required")
        elif reference_id in seen_ids:
            errors.append(f"duplicate reference_id: {reference_id}")
        else:
            seen_ids.add(reference_id)
        for key in (
            "source",
            "semantic_structure",
            "style_grammar",
            "transfer_policy",
        ):
            if not isinstance(figure.get(key), dict):
                errors.append(f"{prefix}.{key} must be an object")
        if figure.get("confidence") not in {"high", "partial", "sparse"}:
            errors.append(f"{prefix}.confidence must be high, partial, or sparse")

    for path, value in collect_color_strings(shared):
        for token in re.findall(r"#[0-9A-Fa-f]{6}", value):
            if not HEX_COLOR.fullmatch(token):
                errors.append(f"invalid color token at {path}: {token}")

    if "TODO" in json.dumps(profile, ensure_ascii=False):
        errors.append("profile still contains TODO placeholders")

    assets_checked: list[dict[str, object]] = []
    if check_assets:
        candidates: list[tuple[str, str | None]] = [
            ("source_document.absolute_path", source.get("absolute_path")),
            ("inventory.contact_sheet", inventory.get("contact_sheet")),
        ]
        for index, item in enumerate(inventory_figures):
            if isinstance(item, dict):
                candidates.append(
                    (
                        f"inventory.figures[{index}].image_path",
                        item.get("image_path") or item.get("file"),
                    )
                )
        for index, figure in enumerate(figures):
            if isinstance(figure, dict) and isinstance(figure.get("source"), dict):
                candidates.append(
                    (
                        f"figures[{index}].source.local_absolute_path",
                        figure["source"].get("local_absolute_path"),
                    )
                )
        for label, value in candidates:
            if not isinstance(value, str) or not value:
                continue
            resolved = resolve_asset(profile_path.parent, value)
            if resolved is None:
                continue
            exists = resolved.is_file()
            assets_checked.append(
                {"field": label, "path": str(resolved), "exists": exists}
            )
            if not exists:
                errors.append(f"asset does not exist at {label}: {resolved}")

    if not check_assets:
        warnings.append("asset paths were not checked; rerun with --check-assets")

    return {
        "schema": "figure-style/ProfileValidation@1",
        "profile": str(profile_path),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "inventory_figures": len(inventory_figures),
            "reference_analyses": len(figures),
            "style_families": len(families) if isinstance(families, dict) else 0,
            "assets_checked": len(assets_checked),
        },
        "assets_checked": assets_checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--check-assets", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    path = args.profile.expanduser().resolve()
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        result = {
            "schema": "figure-style/ProfileValidation@1",
            "profile": str(path),
            "valid": False,
            "errors": [f"cannot read JSON: {exc}"],
            "warnings": [],
        }
    else:
        result = validate(profile, path, args.check_assets)

    if not args.quiet:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
