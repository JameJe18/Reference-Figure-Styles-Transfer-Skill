from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProfileValidationTests(unittest.TestCase):
    def test_example_profile_is_valid(self) -> None:
        module = load_module("validate_style_profile", "scripts/validate_style_profile.py")
        path = ROOT / "examples" / "example_style_profile.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        result = module.validate(profile, path, check_assets=False)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["counts"]["inventory_figures"], 2)
        self.assertEqual(result["counts"]["reference_analyses"], 2)

    def test_wrong_schema_fails(self) -> None:
        module = load_module("validate_style_profile_bad", "scripts/validate_style_profile.py")
        path = ROOT / "examples" / "example_style_profile.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        profile["schema"] = "wrong"
        result = module.validate(profile, path, check_assets=False)
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
