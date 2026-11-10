"""Check the invitation and independently decode the QR actually shipped in SVGs."""
import base64
import importlib.util
import io
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from scripts import generate_review_assets as assets

ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"
HAS_QR_TOOLS = all(importlib.util.find_spec(name) for name in ("qrcode", "PIL", "zxingcpp"))


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class ReviewPageTests(unittest.TestCase):
    def test_review_link_is_direct_and_page_remains_optional(self):
        html = (ROOT / "review/index.html").read_text()
        page = Page(html)
        links = [attrs for tag, attrs in page.elements if tag == "a"]
        self.assertEqual(sum(link.get("href") == "https://g.page/r/CW4OS5cVuNBqEBM/review"
                             for link in links), 1)
        self.assertTrue(any(link.get("href") == "tel:7158538513" for link in links))
        self.assertIn("completely optional", html)
        self.assertIn("honest review", html)
        self.assertFalse(any(tag in ("form", "input", "select", "script") for tag, _ in page.elements))
        self.assertEqual(sum(tag == "h1" for tag, _ in page.elements), 1)
        self.assertTrue(any(tag == "main" and attrs.get("id") == "main" for tag, attrs in page.elements))

    def test_utility_page_has_canonical_noindex_and_local_assets(self):
        page = Page((ROOT / "review/index.html").read_text())
        self.assertIn(("meta", {"name": "robots", "content": "noindex, follow"}), page.elements)
        self.assertIn(("link", {"rel": "canonical", "href": assets.DESTINATION}), page.elements)
        self.assertNotIn(assets.DESTINATION, (ROOT / "sitemap.xml").read_text())
        for tag, attrs in page.elements:
            local = attrs.get("src") or (attrs.get("href") if tag == "link" else None)
            if local and local.startswith("/"):
                with self.subTest(path=local):
                    self.assertTrue((ROOT / local.lstrip("/")).is_file())
        card = next(attrs for tag, attrs in page.elements
                    if tag == "a" and "download" in attrs)
        self.assertTrue((ROOT / card["href"].lstrip("/")).is_file())

    def test_downloaded_card_embeds_approved_logo_and_readable_url(self):
        card = ET.parse(ROOT / "review/review-card.svg").getroot()
        self.assertEqual((card.get("width"), card.get("height")), ("5in", "3in"))
        logo = card.find(SVG + "image").get("href")
        self.assertEqual(base64.b64decode(logo.split(",", 1)[1]),
                         (ROOT / "images/brand-112.jpg").read_bytes())
        text = " ".join(card.itertext())
        self.assertIn("lucky7towingtransport.com/review/", text)
        self.assertIn("Leaving a review is optional.", text)

    def test_header_overrides_shared_icon_only_phone_button(self):
        # Shared mobile styles collapse call buttons to a 48px icon. This
        # utility page keeps the entire number visible, including at 700–899px.
        css = (ROOT / "review/review.css").read_text()
        header_rule = re.search(r"\.review-header \.call-btn\s*\{([^}]+)\}", css).group(1)
        self.assertRegex(header_rule, r"width:\s*auto\s*;")
        self.assertRegex(header_rule, r"min-height:\s*48px\s*;")
        self.assertRegex(header_rule, r"padding:\s*[^;]+;")


@unittest.skipUnless(HAS_QR_TOOLS, "QR tooling required; see review-asset-checks workflow")
class ReviewQRTests(unittest.TestCase):
    def test_both_actual_svg_codes_decode_to_canonical_review_page(self):
        import zxingcpp
        from PIL import Image, ImageDraw

        for filename in ("review-qr.svg", "review-card.svg"):
            with self.subTest(file=filename):
                document = ET.parse(ROOT / "review" / filename).getroot()
                qr = next(node for node in document.iter(SVG + "svg")
                          if node.get("id") == "review-qr-code")
                size = int(qr.get("viewBox").split()[-1])
                image = Image.new("RGB", (size * 10, size * 10), "white")
                drawing = ImageDraw.Draw(image)
                path = qr.find(SVG + "path").get("d")
                modules = re.findall(r"M(\d+),(\d+)h1v1h-1z", path)
                self.assertEqual("".join(f"M{x},{y}h1v1h-1z" for x, y in modules), path)
                for x, y in modules:
                    x, y = int(x), int(y)
                    self.assertTrue(4 <= x < size - 4 and 4 <= y < size - 4)
                    drawing.rectangle((x * 10, y * 10, x * 10 + 9, y * 10 + 9), fill="black")
                decoded = zxingcpp.read_barcode(image)
                self.assertIsNotNone(decoded)
                self.assertEqual(decoded.text, assets.DESTINATION)

    def test_generated_assets_are_reproducible(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(assets.main(["--check"]), 0)

    def test_check_rejects_missing_or_changed_assets_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "images").mkdir()
            (root / "images/brand-112.jpg").write_bytes((ROOT / "images/brand-112.jpg").read_bytes())
            with patch.object(assets, "ROOT", root), redirect_stdout(io.StringIO()):
                self.assertEqual(assets.main(["--check"]), 1)
                self.assertFalse((root / "review").exists())
                self.assertEqual(assets.main([]), 0)
                self.assertEqual(assets.main(["--check"]), 0)
                (root / "review/review-qr.svg").write_text("changed")
                self.assertEqual(assets.main(["--check"]), 1)
                self.assertEqual((root / "review/review-qr.svg").read_text(), "changed")
