#!/usr/bin/env python3
"""Notify IndexNow about the deployed public pages; default is an offline preview.

Run --submit --url URL (repeat --url for each changed page) after a release is live.
The public verification file,
sitemap, and every submitted page must match this checkout before any POST.
An accepted notification is not proof of indexing or ranking.
"""

import argparse
import http.client
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

SITE = "https://lucky7towingtransport.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_FILE = "indexnow-key.txt"
ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def build_payload(root, selected_urls=None):
    """Use the canonical sitemap and intentionally public ownership proof."""
    key = (root / KEY_FILE).read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise ValueError("Invalid IndexNow verification file format")
    tree = ET.fromstring((root / "sitemap.xml").read_bytes())
    if tree.tag != NAMESPACE + "urlset":
        raise ValueError("Expected a sitemap URL set")
    urls = [node.text or "" for node in tree.findall(f"{NAMESPACE}url/{NAMESPACE}loc")]
    if not 1 <= len(urls) <= 10000 or len(urls) != len(set(urls)):
        raise ValueError("Sitemap must contain 1–10000 distinct URLs")
    for url in urls:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.netloc != urlsplit(SITE).netloc
                or parsed.query or parsed.fragment or not parsed.path.endswith("/")):
            raise ValueError("Submit only canonical HTTPS page URLs on the Lucky7 domain")
        source = (root / unquote(parsed.path).lstrip("/") / "index.html").resolve()
        if not source.is_relative_to(root.resolve()) or not source.is_file():
            raise ValueError("A sitemap page is missing from this checkout")
    if selected_urls is not None:
        if (not selected_urls or len(selected_urls) != len(set(selected_urls))
                or not set(selected_urls).issubset(urls)):
            raise ValueError("Select distinct changed URLs from the canonical sitemap")
        urls = selected_urls
    return {"host": urlsplit(SITE).netloc, "key": key,
            "keyLocation": f"{SITE}/{KEY_FILE}", "urlList": urls}


def verify_live(root, payload):
    """Refuse to notify engines about an undeployed or stale checkout."""
    resources = [(payload["keyLocation"], root / KEY_FILE),
                 (f"{SITE}/sitemap.xml", root / "sitemap.xml")]
    resources.extend((url, root / unquote(urlsplit(url).path).lstrip("/") / "index.html")
                     for url in payload["urlList"])
    for url, source in resources:
        request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError("A public verification resource did not return a direct HTTP 200")
            if response.read() != source.read_bytes():
                raise ValueError(f"Production differs from this checkout: {urlsplit(url).path}")


def submit_urls(root, payload):
    """Verify first, then send one notification without automatic write retries."""
    verify_live(root, payload)
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 202):
            raise ValueError(f"Unexpected IndexNow HTTP status: {response.status}")
        return response.status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submit", action="store_true", help="verify production and notify IndexNow")
    parser.add_argument("--url", action="append", help="changed canonical URL; repeat for each changed page")
    args = parser.parse_args(argv)
    try:
        if args.submit and not args.url:
            raise ValueError("--submit requires --url for each changed page")
        payload = build_payload(ROOT, args.url)
        for url in payload["urlList"]:
            print(url)
        if not args.submit:
            print("Preview only: no network requests. Use --submit --url URL for changed pages after deployment.")
            return 0
        status = submit_urls(ROOT, payload)
    except urllib.error.HTTPError as exc:
        print(f"IndexNow operation failed: HTTP {exc.code}. No indexing claim can be made.", file=sys.stderr)
        exc.close()
        return 1
    except (OSError, urllib.error.URLError, http.client.HTTPException,
            ValueError, ET.ParseError) as exc:
        print(f"IndexNow operation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if status == 202:
        print("HTTP 202: notification received; provider key validation is pending. Indexing is not confirmed.")
    else:
        print("HTTP 200: notification received. Indexing and ranking are not confirmed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
