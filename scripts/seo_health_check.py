#!/usr/bin/env python3
"""Weekly SEO health check for lucky7towingtransport.com.

Verifies the live site still carries its SEO-critical elements: indexability,
title keywords, NAP data, structured data with the USDOT identifier, the city
landing pages and their Service/BreadcrumbList schema, robots.txt, and sitemap
coverage. Exits non-zero if anything regressed so the GitHub Action can alert.

Two properties this script tries hard to keep:

* One broken page reports its own failures without hiding the others - every
  page is fetched and checked independently.
* It does not cry wolf. Network blips, timeouts, and 5xx are retried before
  anything is reported, because a monitor that pages you for a transient CDN
  hiccup is a monitor you will start ignoring.
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request

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

failures = []


def fetch(path):
    """Return (status, headers, body).

    HTTP status comes back as a value rather than an exception so a single 404
    can't abort the run and mask every check that follows it. Transient
    conditions (timeout, DNS, connection reset, 5xx) are retried; only a
    persistent failure is reported. 4xx returns immediately - it is a real
    result, not a blip. Status 0 means "could not observe the site", which is
    reported distinctly from "the site is wrong".
    """
    req = urllib.request.Request(SITE + path, headers={"User-Agent": USER_AGENT})
    last_error = "unknown"
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code < 500:
                return exc.code, dict(exc.headers or {}), body
            last_error = f"HTTP {exc.code}"
        except Exception as exc:  # timeout, DNS, TLS, reset - all retryable
            last_error = f"{exc.__class__.__name__}: {exc}"
        if attempt < RETRIES:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    return 0, {}, f"unreachable after {RETRIES} attempts ({last_error})"


def check(name, ok, detail=""):
    print(f"{'OK  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def title_of(html):
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    return match.group(1).strip() if match else ""


def attr_of(tag, attr):
    match = re.search(rf'{attr}\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return match.group(1) if match else ""


def meta_content(html, name):
    for tag in re.findall(r"<meta\b[^>]*>", html, re.I):
        if re.search(rf'name\s*=\s*["\']{name}["\']', tag, re.I):
            return attr_of(tag, "content").strip()
    return ""


def canonical_of(html):
    for tag in re.findall(r"<link\b[^>]*>", html, re.I):
        if re.search(r'rel\s*=\s*["\']canonical["\']', tag, re.I):
            return attr_of(tag, "href")
    return ""


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
    return [value] if isinstance(value, str) else value


def node_of_type(nodes, wanted):
    for node in nodes:
        if wanted in types_of(node):
            return node
    return None


def check_reachable(label, status):
    """Separate 'we could not look' from 'the site is wrong'."""
    if status == 0:
        check(f"{label}: reachable", False, "no response after retries")
        return False
    check(f"{label}: returns 200", status == 200, f"got {status}")
    return status == 200


def check_indexable(label, headers, html):
    header_directive = headers.get("X-Robots-Tag", "")
    check(
        f"{label}: no noindex in X-Robots-Tag",
        "noindex" not in header_directive.lower(),
        header_directive,
    )
    meta_robots = meta_content(html, "robots")
    check(
        f"{label}: meta robots allows indexing",
        "noindex" not in meta_robots.lower(),
        meta_robots or "(none)",
    )


def check_common(label, html, expected_canonical, expect_street=False):
    title = title_of(html)
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
    check(f"{label}: phone number on page", PHONE_DIGITS in html)
    description = meta_content(html, "description")
    check(f"{label}: meta description non-empty", bool(description), "empty or missing")
    if expect_street:
        check(f"{label}: street address on page", STREET in html)
    return title


def check_json_ld(label, html, expected_blocks):
    block_count, nodes, parse_error = ld_nodes(html)
    check(
        f"{label}: has {expected_blocks}+ JSON-LD blocks",
        block_count >= expected_blocks,
        f"found {block_count}",
    )
    check(f"{label}: JSON-LD parses", parse_error is None, parse_error or "")
    return nodes


def check_homepage():
    label = "homepage"
    status, headers, html = fetch("/")
    if not check_reachable(label, status):
        return

    check_indexable(label, headers, html)
    title = check_common(label, html, f"{SITE}/", expect_street=True)
    check(f"{label}: title carries brand", "Lucky 7" in title, title or "no <title>")

    business = node_of_type(check_json_ld(label, html, expected_blocks=2), "AutomotiveBusiness")
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
    if not check_reachable(label, status):
        return

    check_indexable(label, headers, html)
    title = check_common(label, html, url)
    check(f"{label}: title names the city", city in title, title or "no <title>")

    nodes = check_json_ld(label, html, expected_blocks=2)
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
    if check_reachable("robots.txt", status):
        check("robots.txt references sitemap", "sitemap.xml" in robots.lower())

    status, _, sitemap = fetch("/sitemap.xml")
    if not check_reachable("sitemap", status):
        return
    check("sitemap looks valid", "<urlset" in sitemap and "<loc>" in sitemap)
    for path, name in [("/", "homepage")] + CITY_PAGES:
        check(f"sitemap lists the {name} URL", f"<loc>{SITE}{path}</loc>" in sitemap)


def main():
    check_homepage()
    for path, city in CITY_PAGES:
        check_city_page(path, city)
    check_robots_and_sitemap()

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        sys.exit(1)
    print("All SEO health checks passed.")


if __name__ == "__main__":
    main()
