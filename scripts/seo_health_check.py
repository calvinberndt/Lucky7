#!/usr/bin/env python3
"""SEO health check for lucky7towingtransport.com.

Verifies the live site still carries its SEO-critical elements: indexability,
title keywords, NAP data, structured data with the USDOT identifier, the city
landing pages and their Service/BreadcrumbList schema, robots.txt, and sitemap
coverage. Exits non-zero if anything regressed so the GitHub Action can alert.
Checks crawl access for Googlebot, Bingbot, DuckDuckBot, and Applebot, and the
documented Google, Bing, and Apple meta/header indexing directives.
Use --local [directory] to validate source files without making network requests;
this also checks local links, assets, fragment targets, and duplicate page titles.

Two properties this script tries hard to keep:

* One broken page reports its own failures without hiding the others - every
  page is fetched and checked independently.
* It does not cry wolf. Network blips, timeouts, and 5xx are retried before
  anything is reported, because a monitor that pages you for a transient CDN
  hiccup is a monitor you will start ignoring.
"""

import argparse
from html.parser import HTMLParser
import http.client
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

SITE = "https://lucky7towingtransport.com"
PHONE_DIGITS = "853-8513"
STREET = "N3026 State Hwy 47"
USDOT = "1237637"
TELEPHONE = "+17158538513"
BUSINESS_ID = f"{SITE}/#business"
USER_AGENT = "Lucky7-SEO-HealthCheck/2.0"

RETRIES = 3
RETRY_BACKOFF_SECONDS = 3

# City landing pages: (path, city name used in the title and Service schema).
# Adding a page here also requires adding it to sitemap.xml - the sitemap
# coverage check below enforces that.
CITY_PAGES = [
    ("/towing-shawano-wi/", "Shawano"),
    ("/towing-bonduel-wi/", "Bonduel"),
    ("/towing-pulaski-wi/", "Pulaski"),
]

# Crawl access and indexing directives are separate checks. DuckDuckGo documents
# DuckDuckBot's robots.txt support and sources most ordinary links from Bing;
# it does not document a DuckDuckBot-specific meta/X-Robots-Tag scope.
# https://duckduckgo.com/duckduckgo-help-pages/results/duckduckbot
# Brave's crawler follows Googlebot access rather than a separate Bravebot group.
# https://search.brave.com/help/brave-search-crawler
CRAWLERS = ("Googlebot", "Bingbot", "DuckDuckBot", "Applebot")
INDEXING_CRAWLERS = ("Googlebot", "Bingbot", "Applebot")

failures = []
LOCAL_ROOT = None


class Page(HTMLParser):
    """Collect source markup without treating comments or JSON-LD as visible copy."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.ids = []
        self.text = []
        self.titles = []
        self.headings = []
        self.capture = None
        self.hidden = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = {name: value or "" for name, value in attrs}
        self.tags.append((tag, attrs))
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag in ("script", "style", "title", "template"):
            self.hidden += 1
        if tag in ("title", "h1"):
            self.capture = self.titles if tag == "title" else self.headings
            self.capture.append("")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "title", "template"):
            self.hidden = max(0, self.hidden - 1)
        if tag in ("title", "h1"):
            self.capture = None

    def handle_data(self, data):
        if self.capture is not None:
            self.capture[-1] += data
        if not self.hidden:
            self.text.append(data)


def canonical_urls(html):
    return [attrs.get("href", "") for tag, attrs in Page(html).tags
            if tag == "link" and "canonical" in attrs.get("rel", "").lower().split()]


def robots_allows(robots, path, agent="googlebot"):
    """Apply named groups and longest path rules, including Apple's fallback."""
    agent = agent.lower()
    groups, agents, rules = [], [], []
    for line in robots.splitlines():
        key, separator, value = line.split("#", 1)[0].partition(":")
        if not separator:
            continue
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif key in ("allow", "disallow") and agents:
            rules.append((key, value))
    if agents:
        groups.append((agents, rules))
    specific = [rules for agents, rules in groups if agent in agents]
    # Applebot follows Googlebot's robots.txt group only when no Applebot group
    # exists. An explicit empty final group still counts as an allow-all group.
    # https://support.apple.com/en-us/119829
    if agent == "applebot" and not specific:
        specific = [rules for agents, rules in groups if "googlebot" in agents]
    selected = specific or [rules for agents, rules in groups if "*" in agents]
    matches = []
    for rules in selected:
        for kind, pattern in rules:
            if not pattern:
                continue
            expression = re.escape(pattern).replace(r"\*", ".*")
            if pattern.endswith("$"):
                expression = expression[:-2] + "$"
            if re.match(expression, path):
                matches.append((len(pattern.rstrip("$").replace("*", "")), kind == "allow"))
    return max(matches)[1] if matches else True


def fetch(path):
    """Return (status, headers, body).

    HTTP status comes back as a value rather than an exception so a single 404
    can't abort the run and mask every check that follows it. Transient
    conditions (timeout, DNS, connection reset, 5xx) are retried; only a
    persistent failure is reported. 4xx returns immediately - it is a real
    result, not a blip. Status 0 means "could not observe the site", which is
    reported distinctly from "the site is wrong".
    """
    if LOCAL_ROOT is not None:
        filename = LOCAL_ROOT / path.lstrip("/")
        if path.endswith("/"):
            filename /= "index.html"
        try:
            return 200, {}, strip_comments(filename.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return 404, {}, f"missing local file: {filename}"
    req = urllib.request.Request(SITE + path, headers={"User-Agent": USER_AGENT})
    last_error = "unknown"
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, lower_keys(resp.headers), strip_comments(
                    resp.read().decode("utf-8", "replace")
                )
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code < 500 and exc.code != 429:
                return exc.code, lower_keys(exc.headers), body
            last_error = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, OSError,
                http.client.IncompleteRead, http.client.BadStatusLine,
                http.client.LineTooLong) as exc:
            last_error = f"{exc.__class__.__name__}: {exc}"
        if attempt < RETRIES:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    return 0, {}, f"unreachable after {RETRIES} attempts ({last_error})"


def lower_keys(headers):
    """HTTP header names are case-insensitive; normalise so lookups are too."""
    result = {}
    for key, value in (headers or {}).items():
        key = str(key).lower()
        # Preserve separate robots fields: a named bot in one field does not
        # scope an unqualified directive in a later field.
        separator = "\n" if key == "x-robots-tag" else ", "
        result[key] = result[key] + separator + value if key in result else value
    return result


def strip_comments(html):
    """Drop HTML comments so commented-out markup can't satisfy a check."""
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def check(name, ok, detail=""):
    print(f"{'OK  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def title_of(html):
    titles = Page(html).titles
    return titles[0].strip() if titles else ""


def meta_content(html, name):
    for tag, attrs in Page(html).tags:
        if tag == "meta" and attrs.get("name", "").lower() == name.lower():
            return attrs.get("content", "").strip()
    return ""


def canonical_of(html):
    urls = canonical_urls(html)
    return urls[0] if urls else ""


def ld_nodes(html):
    """Every JSON-LD node on the page, or None if a block failed to parse.

    Flattens the three shapes search engines accept: a bare object, a
    top-level array, and an @graph container. Consolidating this site's blocks
    into an @graph is a legitimate future change and must not page anyone.
    """
    raw = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.S,
    )
    nodes, parse_error = [], None
    for block in raw:
        try:
            doc = json.loads(block)
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
            continue
        for candidate in doc if isinstance(doc, list) else [doc]:
            if not isinstance(candidate, dict):
                continue
            graph = candidate.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
            else:
                nodes.append(candidate)
    return len(raw), nodes, parse_error


def types_of(node):
    value = node.get("@type") or []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return []  # malformed @type: report as a missing schema, never crash


def node_of_type(nodes, wanted):
    for node in nodes:
        if wanted in types_of(node):
            return node
    return None


def check_reachable(label, status, detail=""):
    """Separate 'we could not look' from 'the site is wrong'."""
    if status == 0:
        check(f"{label}: reachable", False, detail or "no response after retries")
        return False
    check(f"{label}: returns 200", status == 200, f"got {status}")
    return status == 200


def blocks_indexing(value, header=False, agent="googlebot"):
    """Distinguish standalone robots rules from parameter values and bot scopes."""
    agent = agent.lower()
    parameter_rules = {"max-snippet", "max-image-preview", "max-video-preview", "unavailable_after"}
    for field in value.splitlines() if header else [value]:
        scope = "*"
        for group in re.split(r"[,;]", field.lower()):
            prefix = re.match(r"\s*([\w*-]+)\s*:\s*", group)
            if header and prefix and prefix.group(1) not in parameter_rules:
                scope = prefix.group(1)
                group = group[prefix.end():]
            if scope not in ("*", agent):
                continue
            for rule in re.finditer(r"([\w-]+)(?:\s*:\s*([^\s,;]+))?", group):
                if rule.group(2) is None and rule.group(1) in ("noindex", "none"):
                    return True
    return False


def check_indexable(label, headers, html):
    header_directive = headers.get("x-robots-tag", "")
    meta_tags = [(attrs.get("name", "").lower(), attrs.get("content", ""))
                 for tag, attrs in Page(html).tags if tag == "meta"]
    for crawler in INDEXING_CRAWLERS:
        agent = crawler.lower()
        directives = [value for name, value in meta_tags if name in ("robots", agent)]
        # A generic or applicable named noindex/none blocks this crawler; an
        # unrelated crawler's rules must not leak into its result.
        blocked = blocks_indexing(header_directive, header=True, agent=agent) or any(
            blocks_indexing(value, agent=agent) for value in directives)
        check(
            f"{label}: robots directives allow {crawler} indexing",
            not blocked,
            "; ".join(value for value in [header_directive] + directives if value),
        )


def check_common(label, html, expected_canonical, expect_street=False):
    page = Page(html)
    title = title_of(html)
    check(f"{label}: one non-empty title", len(page.titles) == 1 and bool(title))
    check(f"{label}: one non-empty H1", len(page.headings) == 1 and bool(page.headings[0].strip()))
    check(f"{label}: one canonical", len(canonical_urls(html)) == 1)
    check(
        f"{label}: title carries towing keyword",
        ("Tow Truck" in title) or ("Towing" in title),
        title or "no <title>",
    )
    check(
        f"{label}: canonical is {expected_canonical}",
        canonical_of(html) == expected_canonical,
        canonical_of(html) or "no canonical",
    )
    check(f"{label}: phone number in visible copy", PHONE_DIGITS in " ".join(page.text))
    call_links = [attrs.get("href", "") for tag, attrs in page.tags
                  if tag == "a" and attrs.get("href", "").startswith("tel:")]
    check(f"{label}: working phone links", bool(call_links) and all(
        re.sub(r"\D", "", href).removeprefix("1") == TELEPHONE[2:] for href in call_links))
    description = meta_content(html, "description")
    check(f"{label}: meta description non-empty", bool(description), "empty or missing")
    if expect_street:
        check(f"{label}: street address on page", STREET in html)
    return title


def check_json_ld(label, html):
    block_count, nodes, parse_error = ld_nodes(html)
    check(f"{label}: JSON-LD present", block_count >= 1, "no ld+json blocks")
    check(f"{label}: JSON-LD parses", parse_error is None, parse_error or "")
    # Required node types are asserted by the callers. Block count is
    # deliberately not asserted: one @graph block carrying every node is as
    # valid as several separate blocks.
    return nodes


def check_homepage():
    label = "homepage"
    status, headers, html = fetch("/")
    if not check_reachable(label, status, html):
        return

    check_indexable(label, headers, html)
    title = check_common(label, html, f"{SITE}/", expect_street=True)
    check(f"{label}: title carries brand", "Lucky 7" in title, title or "no <title>")

    business = node_of_type(check_json_ld(label, html), "AutomotiveBusiness")
    if business is None:
        check(f"{label}: business schema block found", False)
        return

    identifier = business.get("identifier") or {}
    address = business.get("address") or {}
    check(f"{label}: schema keeps USDOT identifier", identifier.get("value") == USDOT)
    check(
        f"{label}: schema keeps street address",
        str(address.get("streetAddress", "")).startswith("N3026"),
    )
    check(f"{label}: schema keeps telephone", business.get("telephone") == TELEPHONE)
    check(
        f"{label}: schema keeps EmergencyService type",
        "EmergencyService" in types_of(business),
    )
    # City pages point Service.provider at this @id; if the anchor drifts they
    # become orphaned entities that no longer inherit the business's trust.
    check(
        f"{label}: business schema keeps @id anchor",
        business.get("@id") == BUSINESS_ID,
        str(business.get("@id")),
    )


def check_city_page(path, city):
    label = f"{city} page"
    url = SITE + path
    status, headers, html = fetch(path)
    if not check_reachable(label, status, html):
        return

    check_indexable(label, headers, html)
    title = check_common(label, html, url)
    check(f"{label}: title names the city", city in title, title or "no <title>")

    nodes = check_json_ld(label, html)
    service = node_of_type(nodes, "Service")
    breadcrumb = node_of_type(nodes, "BreadcrumbList")

    if service is None:
        check(f"{label}: Service schema block found", False)
    else:
        area = service.get("areaServed") or {}
        provider = service.get("provider") or {}
        # These three catch the copy-paste failure mode: these pages were
        # adapted from one another, so a stale city or URL is the likely slip.
        check(f"{label}: Service areaServed is {city}", area.get("name") == city, str(area))
        check(f"{label}: Service url points at this page", service.get("url") == url,
              str(service.get("url")))
        check(
            f"{label}: Service links to the business @id",
            provider.get("@id") == BUSINESS_ID,
            str(provider),
        )

    if breadcrumb is None:
        check(f"{label}: BreadcrumbList schema block found", False)
    else:
        items = breadcrumb.get("itemListElement") or []
        last = items[-1] if items else {}
        check(f"{label}: breadcrumb ends at this page", last.get("item") == url, str(last))


def check_robots_and_sitemap():
    status, _, robots = fetch("/robots.txt")
    if check_reachable("robots.txt", status, robots):
        declared = [line.split("#", 1)[0].partition(":")[2].strip()
                    for line in robots.splitlines()
                    if line.partition(":")[0].strip().lower() == "sitemap"]
        check("robots.txt references canonical sitemap", f"{SITE}/sitemap.xml" in declared)
        for crawler in CRAWLERS:
            for path, name in [("/", "homepage")] + CITY_PAGES:
                check(f"robots.txt allows {crawler}: {name}",
                      robots_allows(robots, path, agent=crawler))

    status, _, sitemap = fetch("/sitemap.xml")
    if not check_reachable("sitemap", status, sitemap):
        return
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    try:
        root = ET.fromstring(sitemap)
    except ET.ParseError as exc:
        check("sitemap is valid XML", False, str(exc))
        return
    check("sitemap uses URL-set namespace", root.tag == namespace + "urlset")
    urls = [node.text for node in root.findall(f"{namespace}url/{namespace}loc")]
    expected = {SITE + path for path, _ in [("/", "homepage")] + CITY_PAGES}
    check("sitemap contains each public canonical URL exactly once",
          set(urls) == expected and len(urls) == len(expected), str(urls))


def srcset_urls(value):
    """Read candidate URLs without splitting embedded data-URL commas.

    Descriptors (width/density) are skipped, not validated. This checks asset
    existence for the site's static srcsets, not full browser srcset grammar.
    """
    remaining = value.strip()
    while remaining:
        remaining = remaining.lstrip(" \t\r\n\f,")
        match = re.match(r"(\S+)\s*", remaining)
        if not match:
            break
        url = match.group(1)
        yield url.rstrip(",")
        remaining = remaining[match.end():]
        if not url.endswith(","):
            remaining = remaining.partition(",")[2]


def check_stylesheet_assets(root, stylesheet):
    """Check literal CSS url() assets; no CSS escapes, variables, or imports graph.

    The site uses ordinary quoted/unquoted URL literals. Embedded data, remote
    resources, and document-local SVG fragments do not represent local files.
    """
    relative = stylesheet.relative_to(root).as_posix()
    css = re.sub(r"/\*.*?\*/", "", stylesheet.read_text(encoding="utf-8"), flags=re.S)
    for match in re.finditer(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)''', css, re.I):
        reference = next(part for part in match.groups() if part is not None).strip()
        if not reference or reference.startswith("#"):
            continue
        url = urlsplit(urljoin(f"{SITE}/{relative}", reference))
        if url.scheme not in ("http", "https") or url.netloc != urlsplit(SITE).netloc:
            continue
        target = root / unquote(url.path).lstrip("/")
        check(f"{relative}: local CSS asset exists: {reference}", target.is_file())


def check_local_links(root):
    """Check the four public routes, including source-only asset/fragment errors."""
    titles, stylesheets = [], set()
    for path, label in [("/", "homepage")] + CITY_PAGES:
        source = root / path.lstrip("/") / "index.html"
        if not source.is_file():
            continue  # fetch() already reports missing public pages.
        page = Page(source.read_text(encoding="utf-8"))
        titles.extend(page.titles)
        check(f"{label}: unique element IDs", len(page.ids) == len(set(page.ids)))
        for tag, attrs in page.tags:
            if tag not in ("a", "link", "img", "script", "source", "use"):
                continue
            attribute = "src" if tag in ("img", "script") else "href"
            references = [attrs.get(attribute, "")]
            if tag in ("img", "source"):
                references.extend(srcset_urls(attrs.get("srcset", "")))
            if tag == "link":
                references.extend(srcset_urls(attrs.get("imagesrcset", "")))
            for reference in references:
                if not reference:
                    continue
                url = urlsplit(urljoin(SITE + path, reference))
                if url.scheme not in ("http", "https") or url.netloc != urlsplit(SITE).netloc:
                    continue
                target = root / unquote(url.path).lstrip("/")
                if target.is_dir():
                    target /= "index.html"
                check(f"{label}: local target exists: {reference}", target.is_file())
                if tag == "link" and "stylesheet" in attrs.get("rel", "").lower().split() and target.is_file():
                    stylesheets.add(target)
                if url.fragment and target.is_file() and target.suffix == ".html":
                    target_page = page if target == source else Page(target.read_text(encoding="utf-8"))
                    check(f"{label}: fragment exists: {reference}", unquote(url.fragment) in target_page.ids)
    for stylesheet in sorted(stylesheets):
        check_stylesheet_assets(root, stylesheet)
    check("public page titles are distinct", len(titles) == len(set(titles)))


def main(argv=None):
    global LOCAL_ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", nargs="?", const=Path(__file__).resolve().parents[1],
                        type=Path, help="check repository files (optionally at a supplied directory)")
    args = parser.parse_args(argv)
    LOCAL_ROOT = args.local.resolve() if args.local is not None else None
    failures.clear()
    check_homepage()
    for path, city in CITY_PAGES:
        check_city_page(path, city)
    check_robots_and_sitemap()
    if LOCAL_ROOT is not None:
        check_local_links(LOCAL_ROOT)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        sys.exit(1)
    print("All SEO health checks passed.")


if __name__ == "__main__":
    main()
