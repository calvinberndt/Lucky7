# Lucky 7 Towing & Transport website

This repository is the static marketing website for Lucky 7 Towing / Lucky 7
Transport in Bonduel, Wisconsin. The public site is
[lucky7towingtransport.com](https://lucky7towingtransport.com).

There is no application server, database, package manager, or build step. GitHub
Pages publishes the repository root from the `master` branch; `CNAME` binds that
deployment to the custom domain. Treat `origin/master` as the source of truth for
what is deployed. Local clones and worktrees are only copies and may be behind it.

## Site structure

| Path | What it controls |
| --- | --- |
| `index.html` | Homepage markup, inline SVG artwork, business contact details, page metadata, and business/WebSite JSON-LD. |
| `styles.css` | Shared visual system and responsive styles for the homepage and city pages. |
| `fonts.css` and `fonts/` | Self-hosted versions of the existing typefaces, their source references, and licenses. |
| `script.js` | Mobile navigation, scroll/reveal behavior, animated fleet and service-area sections, routeable town map, and stat counters. |
| `towing-shawano-wi/index.html` | Shawano search landing page with Service and breadcrumb structured data. |
| `towing-bonduel-wi/index.html` | Bonduel search landing page with Service and breadcrumb structured data. |
| `towing-pulaski-wi/index.html` | Pulaski search landing page with Service and breadcrumb structured data. |
| `images/` | Approved brand, truck, fleet, owner, social-share, and favicon assets used by the static pages. |
| `robots.txt` and `sitemap.xml` | Crawler instructions and the homepage/city-page URL list. |
| `CNAME` | The GitHub Pages custom domain: `lucky7towingtransport.com`. |
| `scripts/seo_health_check.py` | Live SEO check, plus `--local` validation of source or built pages without network requests. |
| `tests/test_seo_health_check.py` | Deterministic regression tests for the SEO checker. |
| `scripts/browser_smoke.sh` | Browser checks for call access, narrow-screen overflow, menus, FAQs, images, and page errors. |
| `scripts/browser_compatibility.cjs` | Actual Chromium, Firefox, and WebKit checks, including keyboard access and no-JavaScript/reduced-motion fallbacks. |
| `.github/workflows/browser-compatibility.yml` | Runs the three-engine browser matrix using isolated, pinned development tooling. |
| `scripts/submit_indexnow.py` and `indexnow-key.txt` | Offline notification preview and deployment-verified IndexNow submission; the text file is intentionally public ownership proof. |
| `.github/workflows/seo-source.yml` | Checks every PR, builds with GitHub Pages/Jekyll, and validates the resulting artifact before release. |
| `_config.yml` | Excludes repository documentation, tests, and scripts from the public Pages artifact. |
| `.github/workflows/seo-health.yml` | Runs the live SEO check every Monday at 13:00 UTC and on manual dispatch; opens or updates a GitHub issue if it fails. |
| `docs/seo/` | SEO audit and execution notes. |
| `docs/superpowers/specs/` | Historical redesign and SEO design specifications, including before/after screenshots. |

## Work from the deployed branch

Before making a change, synchronize with the remote branch instead of relying on
an older local checkout:

```bash
git fetch origin
git switch master
git pull --ff-only origin master
git switch -c codex/<short-change-name>
```

Make and verify the change on the feature branch, then open a pull request into
`master`. Merging that pull request is the deployment: GitHub Pages rebuilds from
the repository root automatically.

## Preview locally

Serve the repository as a static site:

```bash
python3 -m http.server 4173 --directory .
```

Open [http://127.0.0.1:4173](http://127.0.0.1:4173). Check both a desktop and a
mobile-width viewport when changing layout or navigation. For a city page, use a
trailing slash, for example
[http://127.0.0.1:4173/towing-shawano-wi/](http://127.0.0.1:4173/towing-shawano-wi/).

## Updating business information

Business facts appear in more than one place. Keep the public page and the
search-engine data aligned.

### Contact email

The public email is `mattslucky7@gmail.com`. In `index.html`, update both:

1. The `mailto:` contact link in the `#contact` section.
2. The `email` field in the `AutomotiveBusiness` JSON-LD block.

After editing, review every contact-link and structured-data email usage before
shipping:

```bash
git grep -n -i 'mailto:'
git grep -n -i '"email"'
```

### Phone, address, and business identity

`index.html` holds the homepage visible values and the canonical
`AutomotiveBusiness` JSON-LD record. The city pages repeat some of the public
facts. When changing any of these, update every visible occurrence and the
matching structured-data field together:

- Phone: visible call links/text on the homepage and city pages, plus the
  JSON-LD `telephone` field.
- Street address: contact copy and the JSON-LD `address` object.
- Business name, hours, USDOT number, or services: visible copy and matching
  JSON-LD values.

Lucky 7 is no longer affiliated with AAA, as confirmed on October 12, 2026. Do
not restore provider badges, membership/coverage claims, or photos showing that
branding. The SEO checker rejects retired-affiliation references in every public
page, including metadata and structured data. Regression tests also protect the
shared CSS/JavaScript and retired photo paths. Historical specifications under
`docs/` are not current business facts or Google post templates.

The SEO monitor expects the current phone digits, address, USDOT identifier, and
business structured-data `@id`. Update `scripts/seo_health_check.py` in the same
change if one of those canonical facts legitimately changes.

### Service areas and city pages

The homepage lists the full rural service area and contains the interactive map.
The three dedicated city pages are Shawano, Bonduel, and Pulaski. Adding or
renaming a city page requires all of the following:

1. Add or update its `towing-<city>-wi/index.html` page, title, canonical URL,
   Service schema, and breadcrumbs.
2. Link it from the homepage where appropriate.
3. Add its canonical URL to `sitemap.xml`.
4. Add it to `CITY_PAGES` in `scripts/seo_health_check.py`.
5. If the homepage interactive map should route to it, update the matching town
   entry in `NODES` and `EDGES` in `script.js`.

## Images and visual changes

Use the approved assets in `images/`; do not replace them with generated stand-ins.
When replacing a photograph, create a web-sized JPEG (roughly 900–1250px wide),
retain useful alt text, and keep image `width` and `height` attributes synchronized
with the asset to avoid layout shift. The favicon files and social-share image are
also in `images/`.

Public photos use WebP derivatives in `<picture>` with the approved JPEG as a
fallback. Keep `srcset`, `sizes`, and the homepage image preload synchronized when
changing a hero image. Font files preserve Alfa Slab One, Barlow, and Barlow
Condensed; see [font sources and licenses](fonts/README.md) before replacing them.

`styles.css` is shared by the homepage and city pages. A class rename or token
change can therefore affect every public route. Review the homepage and all three
city pages after shared style changes.

## SEO and live-site checks

Before deployment, run the dependency-free checks from the repository root:

```bash
uv run --no-project python -m unittest discover -s tests -v
uv run --no-project python scripts/seo_health_check.py --local
node --check script.js
```

The PR workflow runs these checks and a GitHub Pages/Jekyll build. It checks the
built `_site` directory as well, including that internal documentation and scripts
were excluded. There is no local application compilation or package installation.

With the local preview running, use an installed `agent-browser` for runtime checks:

```bash
bash scripts/browser_smoke.sh
# The same checks can target production after deployment:
bash scripts/browser_smoke.sh https://lucky7towingtransport.com
```

This checks all four pages at 320, 375, 900, and 1440 pixels wide. Also visually
inspect desktop/mobile screenshots and check reduced-motion and no-JavaScript
behavior when changing shared styles or interactions.

For the full browser matrix, install development tooling outside the static site:

```bash
npm install --prefix /tmp/lucky7-browser-tools --no-save --package-lock=false playwright@1.64.0
PLAYWRIGHT_SKIP_BROWSER_GC=1 /tmp/lucky7-browser-tools/node_modules/.bin/playwright install chromium firefox webkit
NODE_PATH=/tmp/lucky7-browser-tools/node_modules node scripts/browser_compatibility.cjs http://127.0.0.1:4173 /tmp/lucky7-browser-results
```

Linux hosts may need Playwright's `install --with-deps`; CI installs those system
dependencies. The runner checks all four routes at 320, 375, and 1440px in each
engine, plus no-JavaScript and reduced-motion cases at 375px: 60 cases total.
Use the public site URL instead of localhost for release verification. Failures
exit nonzero and save screenshots and a JSON report. WebKit tests Safari's engine;
they do not certify every Safari release or native iPhone app. On macOS WebKit,
the keyboard check accounts for the platform's Option-Tab link navigation.

The production monitor requests the real public site. It checks the homepage,
all city pages, `robots.txt`, and `sitemap.xml`, including indexability, canonical
URLs, metadata, required JSON-LD, business identity, and city-page schema.
Crawler checks cover Googlebot, Bingbot, DuckDuckBot, and Applebot. Documented
Google, Bing, and Apple indexing directives are checked independently; an
engine-specific block must not hide behind another engine's passing result.

Run it manually after a deployment or a material SEO/content change:

```bash
python3 scripts/seo_health_check.py
```

The scheduled GitHub Action runs the same check every Monday at 13:00 UTC. A
failure creates a new GitHub issue or adds a report to the existing open SEO
health issue. Because this test checks the live domain, it is a post-deployment
verification, not a replacement for the local preview.

## Discovery beyond Google

Safari and Firefox can use different search engines. Browser compatibility,
search indexing, and map-listing ownership are separate concerns. The site's
standard HTML, canonical URLs, sitemap, and universal robots rules support
multiple engines without duplicate browser-specific pages.

After a meaningful content release is deployed, preview and then send a single
IndexNow notification for the changed canonical pages:

```bash
uv run --no-project python scripts/submit_indexnow.py
uv run --no-project python scripts/submit_indexnow.py --submit --url https://lucky7towingtransport.com/
```

Repeat `--url` for each changed page. Submission requires explicit URLs from the
canonical sitemap; do not resubmit untouched pages. The preview makes no network
requests. Submission requires the live proof file,
sitemap, and all submitted HTML pages to match this checkout, then sends one POST
to the IndexNow endpoint. HTTP 200 means received; HTTP 202 means received with
provider key validation pending. Neither means indexed or ranked. Do not run it
on a daily schedule for unchanged content. The public `indexnow-key.txt` proves
website control; it is not a private account credential. Do not replace it with
any account password, OAuth token, or private API key.

Apple Maps and Bing Maps already have Lucky7 listings. Claim the existing
listings rather than creating duplicates. Exact claim links, current evidence,
and a copyable business brief are in the
[browser and search coverage guide](docs/seo/2026-10-12-browser-search-coverage.md).
Account sign-in and ownership verification remain owner actions.

## Release checklist

1. Sync from `origin/master` and work on a feature branch.
2. Preview the changed page locally and exercise the relevant link or interaction.
3. Confirm structured data still parses when `index.html` changes.
4. Search for retired business facts so old values do not remain in metadata or
   links.
5. Open a pull request to `master`, review it, and merge it.
6. Wait for the GitHub Pages deployment to complete, then load
   [lucky7towingtransport.com](https://lucky7towingtransport.com) and verify the
   changed public behavior.
7. Run the live SEO health check when the change affects business facts, metadata,
   city pages, crawler files, or structured data.
8. After meaningful public content changes, send the verified IndexNow notification
   and record the provider response accurately in the release PR.

## Design and SEO references

- [Redesign specification](docs/superpowers/specs/2026-07-18-lucky7-redesign-design.md)
- [SEO enhancement specification](docs/superpowers/specs/2026-07-18-lucky7-seo-enhancement-design.md)
- [SEO audit and plan](docs/seo/2026-07-lucky7-seo-audit-and-plan.md)
- [October 2026 SEO audit and release evidence](docs/seo/2026-10-12-seo-improvements.md)
