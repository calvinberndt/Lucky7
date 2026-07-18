#!/usr/bin/env python3
"""Weekly SEO health check for lucky7towingtransport.com.

Verifies the live site still carries the SEO-critical elements shipped in
July 2026 (PR #3): title keywords, NAP data, structured data with the USDOT
identifier, robots.txt, and sitemap. Exits non-zero if anything regressed so
the GitHub Action can open an issue.
"""

import json
import re
import sys
import urllib.request

SITE = "https://lucky7towingtransport.com"
PHONE_DIGITS = "853-8513"
STREET = "N3026 State Hwy 47"
USDOT = "1237637"

failures = []


def fetch(path):
    req = urllib.request.Request(
        SITE + path, headers={"User-Agent": "Lucky7-SEO-HealthCheck/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def check(name, ok, detail=""):
    print(f"{'OK  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def main():
    status, html = fetch("/")
    check("homepage returns 200", status == 200, f"got {status}")

    title_match = re.search(r"<title>(.*?)</title>", html, re.S)
    title = title_match.group(1).strip() if title_match else ""
    check("title carries brand", "Lucky 7" in title, title or "no <title>")
    check(
        "title carries towing keyword",
        ("Tow Truck" in title) or ("Towing" in title),
        title,
    )
    check("phone number on page", PHONE_DIGITS in html)
    check("street address on page", STREET in html)
    check("meta description present", 'name="description"' in html)

    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    )
    check("JSON-LD blocks present", len(blocks) >= 2, f"found {len(blocks)}")

    business = None
    parse_ok = True
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            parse_ok = False
            check("JSON-LD parses", False, str(exc))
            continue
        types = data.get("@type") or []
        if "AutomotiveBusiness" in types:
            business = data
    if parse_ok:
        check("JSON-LD parses", True)

    if business is None:
        check("business schema block found", False)
    else:
        identifier = business.get("identifier") or {}
        address = business.get("address") or {}
        check("schema keeps USDOT identifier", identifier.get("value") == USDOT)
        check(
            "schema keeps street address",
            str(address.get("streetAddress", "")).startswith("N3026"),
        )
        check("schema keeps telephone", business.get("telephone") == "+17158538513")
        check(
            "schema keeps EmergencyService type",
            "EmergencyService" in (business.get("@type") or []),
        )

    status, robots = fetch("/robots.txt")
    check("robots.txt returns 200", status == 200)
    check("robots.txt references sitemap", "sitemap.xml" in robots.lower())

    status, sitemap = fetch("/sitemap.xml")
    check("sitemap returns 200", status == 200)
    check("sitemap looks valid", "<urlset" in sitemap and "<loc>" in sitemap)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        sys.exit(1)
    print("All SEO health checks passed.")


if __name__ == "__main__":
    main()
