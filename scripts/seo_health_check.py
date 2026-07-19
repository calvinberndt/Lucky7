#!/usr/bin/env python3
"""Weekly SEO health check for lucky7towingtransport.com.

Verifies the live site still carries its SEO-critical elements: title keywords,
NAP data, structured data with the USDOT identifier, the city landing pages and
their Service/BreadcrumbList schema, robots.txt, and sitemap coverage. Exits
non-zero if anything regressed so the GitHub Action can open an issue.

Every page listed in PAGES is checked independently — one broken page reports
its own failures without hiding the others.
"""

import json
import re
import sys
import urllib.error
import urllib.request

SITE = "https://lucky7towingtransport.com"
PHONE_DIGITS = "853-8513"
STREET = "N3026 State Hwy 47"
USDOT = "1237637"
TELEPHONE = "+17158538513"
BUSINESS_ID = f"{SITE}/#business"
USER_AGENT = "Lucky7-SEO-HealthCheck/2.0"

# City landing pages: (path, city name used in the title and Service schema).
# Adding a page here also requires adding it to sitemap.xml — the sitemap
# coverage check below enforces that.
CITY_PAGES = [
    ("/towing-shawano-wi/", "Shawano"),
    ("/towing-bonduel-wi/", "Bonduel"),
    ("/towing-pulaski-wi/", "Pulaski"),
]

failures = []


def fetch(path):
    """Return (status, body).

    HTTP errors come back as values rather than exceptions so that a single
    404 can't abort the run and mask every check that follows it.
    """
    req = urllib.request.Request(SITE + path, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except urllib.error.URLError as exc:
        return 0, f"request failed: {exc.reason}"


def check(name, ok, detail=""):
    print(f"{'OK  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def title_of(html):
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    return match.group(1).strip() if match else ""


def canonical_of(html):
    for tag in re.findall(r"<link\b[^>]*>", html, re.I):
        if re.search(r'rel\s*=\s*["\']canonical["\']', tag, re.I):
            href = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag, re.I)
            if href:
                return href.group(1)
    return ""


def json_ld(label, html, expected_blocks):
    """Parse every JSON-LD block on the page. Returns the parsed list."""
    raw = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.S,
    )
    check(
        f"{label}: has {expected_blocks}+ JSON-LD blocks",
        len(raw) >= expected_blocks,
        f"found {len(raw)}",
    )

    parsed, parse_ok = [], True
    for block in raw:
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError as exc:
            parse_ok = False
            check(f"{label}: JSON-LD parses", False, str(exc))
    if parse_ok:
        check(f"{label}: JSON-LD parses", True)
    return parsed


def types_of(block):
    value = block.get("@type") or []
    return [value] if isinstance(value, str) else value


def check_homepage():
    label = "homepage"
    status, html = fetch("/")
    check(f"{label}: returns 200", status == 200, f"got {status}")
    if status != 200:
        return

    title = title_of(html)
    check(f"{label}: title carries brand", "Lucky 7" in title, title or "no <title>")
    check(
        f"{label}: title carries towing keyword",
        ("Tow Truck" in title) or ("Towing" in title),
        title,
    )
    check(f"{label}: canonical is the root URL", canonical_of(html) == f"{SITE}/", canonical_of(html))
    check(f"{label}: phone number on page", PHONE_DIGITS in html)
    check(f"{label}: street address on page", STREET in html)
    check(f"{label}: meta description present", 'name="description"' in html)

    business = None
    for block in json_ld(label, html, expected_blocks=2):
        if "AutomotiveBusiness" in types_of(block):
            business = block

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
    # City pages point their Service.provider at this @id; if it drifts they
    # become orphaned entities that no longer inherit the business's trust.
    check(f"{label}: business schema keeps @id anchor", business.get("@id") == BUSINESS_ID,
          str(business.get("@id")))


def check_city_page(path, city):
    label = f"{city} page"
    status, html = fetch(path)
    check(f"{label}: returns 200", status == 200, f"got {status}")
    if status != 200:
        return

    title = title_of(html)
    check(f"{label}: title names the city", city in title, title or "no <title>")
    check(
        f"{label}: title carries towing keyword",
        ("Tow Truck" in title) or ("Towing" in title),
        title,
    )
    check(
        f"{label}: canonical points at itself",
        canonical_of(html) == SITE + path,
        canonical_of(html) or "no canonical",
    )
    check(f"{label}: phone number on page", PHONE_DIGITS in html)
    check(f"{label}: meta description present", 'name="description"' in html)

    service = breadcrumb = None
    for block in json_ld(label, html, expected_blocks=2):
        block_types = types_of(block)
        if "Service" in block_types:
            service = block
        elif "BreadcrumbList" in block_types:
            breadcrumb = block

    if service is None:
        check(f"{label}: Service schema block found", False)
    else:
        area = service.get("areaServed") or {}
        provider = service.get("provider") or {}
        check(f"{label}: Service areaServed is {city}", area.get("name") == city, str(area))
        check(
            f"{label}: Service links to the business @id",
            provider.get("@id") == BUSINESS_ID,
            str(provider),
        )

    check(f"{label}: BreadcrumbList schema block found", breadcrumb is not None)


def check_robots_and_sitemap():
    status, robots = fetch("/robots.txt")
    check("robots.txt returns 200", status == 200, f"got {status}")
    check("robots.txt references sitemap", "sitemap.xml" in robots.lower())

    status, sitemap = fetch("/sitemap.xml")
    check("sitemap returns 200", status == 200, f"got {status}")
    if status != 200:
        return
    check("sitemap looks valid", "<urlset" in sitemap and "<loc>" in sitemap)
    for path, city in [("/", "homepage")] + CITY_PAGES:
        check(f"sitemap lists the {city} URL", f"<loc>{SITE}{path}</loc>" in sitemap)


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
