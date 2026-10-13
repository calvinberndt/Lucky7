"""Keep previews offline and notifications tied to verified deployed content."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from scripts import submit_indexnow as indexnow


class IndexNowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / indexnow.KEY_FILE).write_text("example-proof-1234\n")
        (self.root / "index.html").write_text("<h1>Lucky 7 Towing</h1>")
        self.write_sitemap([indexnow.SITE + "/"])

    def write_sitemap(self, urls):
        content = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        content += "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>"
        (self.root / "sitemap.xml").write_text(content)

    def live_response(self, request, timeout):
        path = request.full_url.removeprefix(indexnow.SITE + "/") or "index.html"
        response = MagicMock()
        response.status = 200
        response.geturl.return_value = request.full_url
        response.read.return_value = (self.root / path).read_bytes()
        response.__enter__.return_value = response
        return response

    def test_payload_uses_canonical_sitemap(self):
        payload = indexnow.build_payload(self.root)
        self.assertEqual(payload["urlList"], [indexnow.SITE + "/"])
        self.assertEqual(payload["keyLocation"], indexnow.SITE + "/" + indexnow.KEY_FILE)
        self.assertEqual(payload["host"], "lucky7towingtransport.com")

    def test_key_length_and_character_boundaries(self):
        for key, valid in [("a" * 7, False), ("a" * 8, True), ("a" * 128, True),
                           ("a" * 129, False), ("has spaces", False), ("safe-key-123", True)]:
            with self.subTest(length=len(key), valid=valid):
                (self.root / indexnow.KEY_FILE).write_text(key)
                if valid:
                    indexnow.build_payload(self.root)
                else:
                    with self.assertRaises(ValueError):
                        indexnow.build_payload(self.root)

    def test_selection_only_accepts_distinct_sitemap_members(self):
        home = indexnow.SITE + "/"
        self.assertEqual(indexnow.build_payload(self.root, [home])["urlList"], [home])
        for selected in [[], [home, home], [indexnow.SITE + "/unknown/"], ["https://example.com/"]]:
            with self.subTest(selected=selected), self.assertRaises(ValueError):
                indexnow.build_payload(self.root, selected)

    def test_submit_requires_explicit_changed_urls(self):
        with patch.object(indexnow, "ROOT", self.root), patch.object(
                indexnow.urllib.request, "urlopen") as fetch, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(indexnow.main(["--submit"]), 1)
        fetch.assert_not_called()

    def test_rejects_noncanonical_external_missing_and_duplicate_urls(self):
        cases = [[], [indexnow.SITE + "/"] * 2, ["https://example.com/"],
                 [indexnow.SITE.replace("https", "http") + "/"],
                 [indexnow.SITE + "/?q=test"], [indexnow.SITE + "/#contact"],
                 [indexnow.SITE + "/missing/"], [indexnow.SITE + "/../"],
                 [indexnow.SITE + "/%2e%2e/"], [indexnow.SITE + "/index.html"]]
        for urls in cases:
            with self.subTest(urls=urls):
                self.write_sitemap(urls)
                with self.assertRaises(ValueError):
                    indexnow.build_payload(self.root)

    def test_live_proof_sitemap_and_page_must_match(self):
        payload = indexnow.build_payload(self.root)
        with patch.object(indexnow.urllib.request, "urlopen", side_effect=self.live_response) as fetch:
            indexnow.verify_live(self.root, payload)
        self.assertEqual(fetch.call_count, 3)

    def test_live_redirect_or_non_200_prevents_post(self):
        for status, redirect in [(200, True), (202, False)]:
            with self.subTest(status=status, redirect=redirect):
                response = MagicMock()
                response.status = status
                response.geturl.return_value = "https://example.com/" if redirect else indexnow.SITE + "/" + indexnow.KEY_FILE
                response.__enter__.return_value = response
                with patch.object(indexnow.urllib.request, "urlopen", return_value=response) as fetch:
                    with self.assertRaisesRegex(ValueError, "direct HTTP 200"):
                        indexnow.submit_urls(self.root, indexnow.build_payload(self.root))
                self.assertEqual(fetch.call_count, 1)
                self.assertEqual(fetch.call_args.args[0].get_method(), "GET")

    def test_sitemap_url_count_upper_boundary(self):
        for count in [9999, 10000, 10001]:
            with self.subTest(count=count):
                self.write_sitemap([f"{indexnow.SITE}/page-{n}/" for n in range(count)])
                with patch.object(Path, "is_file", return_value=True):
                    if count <= 10000:
                        self.assertEqual(len(indexnow.build_payload(self.root)["urlList"]), count)
                    else:
                        with self.assertRaises(ValueError):
                            indexnow.build_payload(self.root)

    def test_stale_live_resource_prevents_post(self):
        for stale_path in [indexnow.KEY_FILE, "sitemap.xml", ""]:
            with self.subTest(path=stale_path):
                def stale_response(request, timeout):
                    response = self.live_response(request, timeout)
                    if request.full_url == indexnow.SITE + "/" + stale_path:
                        response.read.return_value = b"old deployment"
                    return response
                with patch.object(indexnow.urllib.request, "urlopen", side_effect=stale_response) as fetch:
                    with self.assertRaisesRegex(ValueError, "Production differs"):
                        indexnow.submit_urls(self.root, indexnow.build_payload(self.root))
                self.assertTrue(all(call.args[0].get_method() == "GET" for call in fetch.call_args_list))

    def test_notification_status_is_not_indexing_success(self):
        for status in [200, 202, 204]:
            with self.subTest(status=status):
                response = MagicMock()
                response.status = status
                response.__enter__.return_value = response
                with patch.object(indexnow, "verify_live"), patch.object(
                        indexnow.urllib.request, "urlopen", return_value=response) as send:
                    if status in (200, 202):
                        self.assertEqual(indexnow.submit_urls(self.root, indexnow.build_payload(self.root)), status)
                    else:
                        with self.assertRaises(ValueError):
                            indexnow.submit_urls(self.root, indexnow.build_payload(self.root))
                self.assertEqual(send.call_count, 1)
                self.assertEqual(send.call_args.args[0].get_method(), "POST")

    def test_default_preview_makes_no_network_requests_or_key_disclosure(self):
        output = io.StringIO()
        with patch.object(indexnow, "ROOT", self.root), patch.object(
                indexnow.urllib.request, "urlopen") as fetch, contextlib.redirect_stdout(output):
            self.assertEqual(indexnow.main([]), 0)
        fetch.assert_not_called()
        self.assertIn("Preview only", output.getvalue())
        self.assertNotIn("example-proof-1234", output.getvalue())

    def test_cli_reports_pending_validation_and_provider_failure(self):
        for result in [202, urllib.error.HTTPError(indexnow.ENDPOINT, 403, "Forbidden", {}, None)]:
            output = io.StringIO()
            with patch.object(indexnow, "ROOT", self.root), patch.object(
                    indexnow, "submit_urls", side_effect=[result]), contextlib.redirect_stdout(output), \
                    contextlib.redirect_stderr(output):
                code = indexnow.main(["--submit", "--url", indexnow.SITE + "/"])
            self.assertEqual(code, 0 if result == 202 else 1)
            self.assertIn("validation is pending" if result == 202 else "HTTP 403", output.getvalue())


if __name__ == "__main__":
    unittest.main()
