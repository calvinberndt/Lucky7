"""Deterministic regression coverage for the source and live SEO checker."""

from contextlib import redirect_stdout
from email.message import Message
import http.client
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from scripts import seo_health_check as seo


def page_html(extra=""):
    return (f'<title>Lucky 7 Towing</title><h1>Towing in Wisconsin</h1>'
            f'<link rel="canonical" href="{seo.SITE}/">'
            '<meta name="description" content="Towing and roadside help">'
            '<a href="tel:7158538513">(715) 853-8513</a>' + extra)


def sitemap_xml(urls=None):
    urls = urls if urls is not None else [seo.SITE + p for p, _ in [("/", "home")] + seo.CITY_PAGES]
    return ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>')


class SEOTests(unittest.TestCase):
    def setUp(self):
        seo.failures.clear()
        seo.LOCAL_ROOT = None
        self.output = io.StringIO()
        self.redirect = redirect_stdout(self.output)
        self.redirect.__enter__()

    def tearDown(self):
        self.redirect.__exit__(None, None, None)
        seo.LOCAL_ROOT = None

    def test_indexability_rejects_every_applicable_directive(self):
        cases = [
            ({}, '<meta name="googlebot" content="noindex">'),
            ({}, '<meta name="robots" content="none">'),
            ({}, '<meta name="robots" content="index"><meta name="robots" content="noindex">'),
            ({'x-robots-tag': 'none'}, ''),
            ({'x-robots-tag': 'googlebot: noindex'}, ''),
            ({}, '<meta name="robots" content="noindex nofollow">'),
            ({}, '<meta name="googlebot" content="index\tnoindex\nnofollow">'),
            ({'x-robots-tag': 'googlebot: noindex nofollow'}, ''),
            ({'x-robots-tag': 'otherbot: index, googlebot: noindex nofollow'}, ''),
        ]
        for headers, html in cases:
            with self.subTest(headers=headers, html=html):
                seo.failures.clear()
                seo.check_indexable('fixture', headers, html)
                self.assertTrue(seo.failures)

    def test_indexability_ignores_comments_and_image_preview_limits(self):
        seo.check_indexable('fixture', {'x-robots-tag': 'max-image-preview: none'},
                            '<!-- <meta name="robots" content="noindex"> -->'
                            '<meta name="robots" content="index, follow">')
        self.assertEqual(seo.failures, [])

    def test_duplicate_header_directives_are_preserved(self):
        headers = Message()
        headers.add_header('X-Robots-Tag', 'noindex')
        headers.add_header('X-Robots-Tag', 'follow')
        self.assertEqual(seo.lower_keys(headers)['x-robots-tag'], 'noindex\nfollow')
        scoped = Message()
        scoped.add_header('X-Robots-Tag', 'otherbot: noindex')
        scoped.add_header('X-Robots-Tag', 'noindex nofollow')
        seo.check_indexable('fixture', seo.lower_keys(scoped), '')
        self.assertTrue(seo.failures)

    def test_indexability_keeps_parameter_values_and_other_bot_rules_separate(self):
        for header in ['max-image-preview:none', 'max-image-preview: none',
                       'otherbot: noindex, none', 'otherbot: noindex, googlebot: index follow']:
            with self.subTest(header=header):
                seo.failures.clear()
                seo.check_indexable('fixture', {'x-robots-tag': header},
                                    '<meta name="robots" content="index follow max-image-preview: none">'
                                    '<meta name="otherbot" content="noindex">')
                self.assertEqual(seo.failures, [])

    def test_common_accepts_current_contact_markup(self):
        seo.check_common('fixture', page_html(), seo.SITE + '/')
        self.assertEqual(seo.failures, [])

    def test_duplicate_canonical_is_rejected_even_when_first_is_correct(self):
        seo.check_common('fixture', page_html('<link rel="canonical" href="https://wrong.example/">'), seo.SITE + '/')
        self.assertIn('fixture: one canonical', seo.failures)

    def test_phone_in_json_ld_does_not_count_as_visible_contact(self):
        html = page_html().replace('<a href="tel:7158538513">(715) 853-8513</a>',
                                   '<script type="application/ld+json">{"telephone":"853-8513"}</script>')
        seo.check_common('fixture', html, seo.SITE + '/')
        self.assertIn('fixture: phone number in visible copy', seo.failures)
        self.assertIn('fixture: working phone links', seo.failures)

    def test_wrong_phone_link_is_rejected(self):
        seo.check_common('fixture', page_html().replace('tel:7158538513', 'tel:7150000000'), seo.SITE + '/')
        self.assertIn('fixture: working phone links', seo.failures)

    def test_h1_boundaries(self):
        for heading in ['', '<h1></h1>', '<h1>A</h1><h1>B</h1>']:
            with self.subTest(heading=heading):
                seo.failures.clear()
                html = page_html().replace('<h1>Towing in Wisconsin</h1>', heading)
                seo.check_common('fixture', html, seo.SITE + '/')
                self.assertIn('fixture: one non-empty H1', seo.failures)

    def test_parser_handles_case_entities_nested_heading_and_quoted_angle(self):
        page = seo.Page('<TITLE>Towing &amp; Help</TITLE><h1>Call <span>now</span></h1>'
                        '<a id="call" title="a > b" href="#call">phone</a>')
        self.assertEqual(page.titles, ['Towing & Help'])
        self.assertEqual(page.headings, ['Call now'])
        self.assertEqual(page.ids, ['call'])
        self.assertEqual(seo.meta_content('<META CONTENT="A &amp; B" NAME="description">', 'description'), 'A & B')
        self.assertEqual(seo.canonical_of('<LINK HREF="https://example.com/" REL="canonical">'), 'https://example.com/')

    def test_robots_longest_path_allow_tie_and_wildcards(self):
        cases = [
            ('User-agent: *\nDisallow: /', '/', False),
            ('User-agent: *\nAllow: /\nDisallow: /towing-', '/towing-shawano-wi/', False),
            ('User-agent: *\nDisallow: /\nAllow: /towing-', '/towing-shawano-wi/', True),
            ('User-agent: *\nDisallow: /\nAllow: /', '/', True),
            ('User-agent: *\nDisallow: /*wi/$', '/towing-shawano-wi/', False),
            ('User-agent: *\nDisallow: /*wi/$', '/towing-shawano-wi/extra', True),
            ('User-agent: *\nDisallow:', '/', True),
            ('User-agent: *\nDisallow: /town/', '/town', True),
        ]
        for robots, path, expected in cases:
            with self.subTest(robots=robots, path=path):
                self.assertEqual(seo.robots_allows(robots, path), expected)

    def test_robots_specific_groups_override_wildcard_and_merge(self):
        robots = ('User-agent: *\nDisallow: /\nUser-agent: Googlebot\nAllow: /\n'
                  'User-agent: googlebot\nDisallow: /blocked/')
        self.assertTrue(seo.robots_allows(robots, '/'))
        self.assertFalse(seo.robots_allows(robots, '/blocked/'))

    def check_crawlers(self, robots, sitemap):
        with patch.object(seo, 'fetch', side_effect=[(200, {}, robots), (200, {}, sitemap)]):
            seo.check_robots_and_sitemap()

    def test_crawlers_accept_valid_files(self):
        self.check_crawlers(f'User-agent: *\nAllow: /\nSitemap: {seo.SITE}/sitemap.xml', sitemap_xml())
        self.assertEqual(seo.failures, [])

    def test_robots_disallow_all_is_reported(self):
        self.check_crawlers(f'User-agent: *\nDisallow: /\nSitemap: {seo.SITE}/sitemap.xml', sitemap_xml())
        self.assertIn('robots.txt allows Googlebot: homepage', seo.failures)

    def test_malformed_sitemap_cannot_pass_by_containing_expected_strings(self):
        self.check_crawlers(f'Sitemap: {seo.SITE}/sitemap.xml', sitemap_xml()[:-9])
        self.assertIn('sitemap is valid XML', seo.failures)

    def test_sitemap_exact_canonical_coverage(self):
        expected = [seo.SITE + p for p, _ in [("/", "home")] + seo.CITY_PAGES]
        for urls in [expected[:-1], expected + [expected[0]], expected + ['https://wrong.example/']]:
            with self.subTest(urls=urls):
                seo.failures.clear()
                self.check_crawlers(f'Sitemap: {seo.SITE}/sitemap.xml', sitemap_xml(urls))
                self.assertIn('sitemap contains each public canonical URL exactly once', seo.failures)

    def test_local_fetch_never_requests_network(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(seo.urllib.request, 'urlopen') as network:
            seo.LOCAL_ROOT = Path(directory)
            (seo.LOCAL_ROOT / 'index.html').write_text('<!-- comment -->hello')
            self.assertEqual(seo.fetch('/'), (200, {}, 'hello'))
            self.assertEqual(seo.fetch('/missing/')[0], 404)
            network.assert_not_called()

    def test_network_retry_then_success(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        response.status, response.headers = 200, {}
        response.read.return_value = b'<h1>Ready</h1>'
        with patch.object(seo.urllib.request, 'urlopen', side_effect=[urllib.error.URLError('timeout'), response]) as network, patch.object(seo.time, 'sleep') as sleep:
            self.assertEqual(seo.fetch('/')[0], 200)
            self.assertEqual(network.call_count, 2)
            sleep.assert_called_once()

    def test_incomplete_response_retries_then_succeeds(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        response.status, response.headers = 200, {}
        response.read.side_effect = [http.client.IncompleteRead(b'partial', 50), b'<h1>Ready</h1>']
        with patch.object(seo.urllib.request, 'urlopen', return_value=response) as network, patch.object(seo.time, 'sleep') as sleep:
            self.assertEqual(seo.fetch('/'), (200, {}, '<h1>Ready</h1>'))
            self.assertEqual(network.call_count, 2)
            sleep.assert_called_once_with(seo.RETRY_BACKOFF_SECONDS)

    def test_incomplete_response_exhaustion_reports_unreachable(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        response.status, response.headers = 200, {}
        response.read.side_effect = http.client.IncompleteRead(b'partial', 50)
        with patch.object(seo.urllib.request, 'urlopen', return_value=response) as network, patch.object(seo.time, 'sleep') as sleep:
            status, headers, detail = seo.fetch('/')
            self.assertEqual((status, headers), (0, {}))
            self.assertIn('IncompleteRead', detail)
            self.assertIn(f'after {seo.RETRIES} attempts', detail)
            self.assertEqual(network.call_count, seo.RETRIES)
            self.assertEqual(sleep.call_count, seo.RETRIES - 1)

    def test_local_links_cover_relative_root_asset_and_fragment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'images').mkdir()
            (root / 'images/truck.jpg').write_bytes(b'image fixture')
            (root / 'index.html').write_text(page_html('<img src="images/truck.jpg">'
                '<div id="contact"></div><a href="/#contact">Contact</a>'
                '<a href="https://external.example/">External</a>'))
            seo.check_local_links(root)
            self.assertEqual(seo.failures, [])
            (root / 'index.html').write_text(page_html('<img src="images/missing.jpg">'
                '<a href="#missing">Broken</a><div id="repeat"></div><div id="repeat"></div>'))
            seo.check_local_links(root)
            self.assertIn('homepage: local target exists: images/missing.jpg', seo.failures)
            self.assertIn('homepage: fragment exists: #missing', seo.failures)
            self.assertIn('homepage: unique element IDs', seo.failures)

    def test_main_uses_local_mode_and_clears_previous_failures(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(seo, 'check_homepage'), patch.object(seo, 'check_city_page'), patch.object(seo, 'check_robots_and_sitemap'), patch.object(seo, 'check_local_links') as links:
            seo.failures.append('stale run')
            seo.main(['--local', directory])
            links.assert_called_once_with(Path(directory).resolve())
            self.assertEqual(seo.failures, [])

    def test_every_responsive_image_candidate_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'fallback.jpg').write_bytes(b'fallback')
            (root / 'small.webp').write_bytes(b'small')
            (root / 'index.html').write_text(page_html(
                '<picture><source srcset="small.webp 640w, missing.webp 1000w">'
                '<img src="fallback.jpg" srcset="small.webp 1x, retina.webp 2x"></picture>'
                '<link rel="preload" as="image" href="fallback.jpg" '
                'imagesrcset="small.webp 640w, preload.webp 1000w">'))
            seo.check_local_links(root)
            for reference in ['missing.webp', 'retina.webp', 'preload.webp']:
                self.assertIn(f'homepage: local target exists: {reference}', seo.failures)
            for reference in ['missing.webp', 'retina.webp', 'preload.webp']:
                (root / reference).write_bytes(b'responsive image fixture')
            seo.failures.clear()
            seo.check_local_links(root)
            self.assertEqual(seo.failures, [])

    def test_linked_css_assets_resolve_relative_to_stylesheet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'css/fonts').mkdir(parents=True)
            (root / 'images').mkdir()
            (root / 'images/truck.webp').write_bytes(b'photo')
            (root / 'css/site.css').write_text(
                '@font-face { src: url("fonts/local.woff2") format("woff2"); }'
                '.truck { background: url(../images/truck.webp); }'
                '.remote { background: url(https://cdn.example/remote.webp); }'
                '.data { background: url("data:image/svg+xml,%3Csvg%3E"); }'
                '.filter { filter: url(#svg-filter); }'
                '/* url(missing-but-commented.webp) */')
            (root / 'index.html').write_text(page_html('<link rel="stylesheet" href="css/site.css">'))
            seo.check_local_links(root)
            self.assertEqual(seo.failures, ['css/site.css: local CSS asset exists: fonts/local.woff2'])
            (root / 'css/fonts/local.woff2').write_bytes(b'font fixture')
            seo.failures.clear()
            seo.check_local_links(root)
            self.assertEqual(seo.failures, [])

    def test_srcset_preserves_data_urls_and_descriptorless_candidates(self):
        self.assertEqual(list(seo.srcset_urls(
            'one.webp, two.webp 2x, data:image/png;base64,AA== 3x, /four.webp 4x')),
            ['one.webp', 'two.webp', 'data:image/png;base64,AA==', '/four.webp'])


if __name__ == '__main__':
    unittest.main()
