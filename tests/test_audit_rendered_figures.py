from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RenderAuditTests(unittest.TestCase):
    def test_white_png_has_clean_edges(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")
        module = load_module("audit_rendered_figures", "scripts/audit_rendered_figures.py")
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "white.png"
            Image.new("RGB", (120, 80), "white").save(image_path, dpi=(300, 300))
            result = module.audit_png(image_path, band=3, ink_threshold=250)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["edge_clean"])
        self.assertEqual(result["width_px"], 120)

    def test_edge_ink_is_detected(self) -> None:
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self.skipTest("Pillow is not installed")
        module = load_module("audit_rendered_figures_edge", "scripts/audit_rendered_figures.py")
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "edge.png"
            image = Image.new("RGB", (120, 80), "white")
            draw = ImageDraw.Draw(image)
            draw.line((0, 0, 119, 0), fill="black", width=2)
            image.save(image_path, dpi=(300, 300))
            result = module.audit_png(image_path, band=3, ink_threshold=250)
        self.assertEqual(result["status"], "fail")
        self.assertGreater(result["edge_ink"]["top"], 0)


if __name__ == "__main__":
    unittest.main()
