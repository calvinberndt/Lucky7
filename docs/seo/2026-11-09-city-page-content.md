# Shawano and Pulaski content improvements — November 9, 2026

The existing city pages now give callers more practical information before they
arrange towing or roadside assistance. The pages keep the same design, contact
details, real photographs, metadata, and Service/BreadcrumbList structured data.

## Content changes

- Shawano has visible pickup guidance for Highway 29, Shawano Lake, county roads,
  and parking lots, plus clearer recovery, quote, and planned-transport answers.
- Pulaski explains how to arrange transport to a chosen repair shop, including
  pickup information, vehicle condition, destination details, and after-hours
  receiving instructions. Its FAQs now cover quote factors and roadside help.
- Both pages explicitly identify Bonduel as the business base and keep current
  availability and arrival estimates tied to a phone call. Only the two changed
  sitemap entries receive a November 9 modification date.

The additions use services and local context already published on the homepage
and these city pages. They introduce no new coverage areas, prices, arrival
promises, customer stories, ratings, or claimed job-photo locations. The dispatch
sections are static HTML and reuse existing styles; they add no network requests
or JavaScript behavior.

## Release verification

Local source verification passed:

- `uv run --no-project python -m unittest discover -s tests -v`: 47 tests passed.
- `uv run --no-project python scripts/seo_health_check.py --local`: all checks
  passed, including phone links, local targets, structured data, and crawler files.
- `node --check script.js` and `git diff --check`: passed.
- The IndexNow preview selected only Shawano and Pulaski and made no network
  requests.

Review both changed pages at desktop and narrow phone widths, including their
FAQs, local links, and persistent call controls. The PR workflow also validates
the GitHub Pages/Jekyll artifact. Runtime and public deployment checks are separate
from the source checks above and belong in the release PR.

After merging, verify both public pages and run the live SEO health check. Send
the deployment-verified IndexNow notification once for the two changed canonical
URLs. Record the actual check results and provider response in the release PR.

These content changes do not establish an increase in rankings, calls, or
traffic. Compare Search Console page and query performance over comparable
periods after recrawling, alongside the separate call-tracking work.
