from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CaptionParsingTests(unittest.TestCase):
    def test_parses_page_and_caption(self) -> None:
        module = load_module("extract_pdf_figures", "scripts/extract_pdf_figures.py")
        text = (
            "Page one text.\n"
            "Figure 1. First caption continues here with a corre-\n"
            "lation example and an mRNA–\n"
            "miRNA pair.\n"
            "\n"
            "2. Materials and Methods\n"
            "This body text must not be part of the caption.\n"
            "\fFigure 2: Second caption.\n"
        )
        captions = module.parse_captions(text)
        self.assertEqual([item["figure_number"] for item in captions], [1, 2])
        self.assertEqual([item["page"] for item in captions], [1, 2])
        self.assertIn("First caption", captions[0]["caption"])
        self.assertIn("correlation example", captions[0]["caption"])
        self.assertIn("mRNA–miRNA", captions[0]["caption"])
        self.assertNotIn("Materials and Methods", captions[0]["caption"])
        self.assertIn("Second caption", captions[1]["caption"])


if __name__ == "__main__":
    unittest.main()
