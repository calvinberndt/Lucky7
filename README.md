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
| `index.html` | Homepage markup, inline SVG artwork, business contact details, page metadata, and two JSON-LD structured-data blocks. |
| `styles.css` | Shared visual system and responsive styles for the homepage and city pages. |
| `script.js` | Mobile navigation, scroll/reveal behavior, animated fleet and service-area sections, routeable town map, and stat counters. |
| `towing-shawano-wi/index.html` | Shawano search landing page with Service and breadcrumb structured data. |
| `towing-bonduel-wi/index.html` | Bonduel search landing page with Service and breadcrumb structured data. |
| `towing-pulaski-wi/index.html` | Pulaski search landing page with Service and breadcrumb structured data. |
| `images/` | Approved brand, truck, fleet, owner, social-share, and favicon assets used by the static pages. |
| `robots.txt` and `sitemap.xml` | Crawler instructions and the homepage/city-page URL list. |
| `CNAME` | The GitHub Pages custom domain: `lucky7towingtransport.com`. |
| `scripts/seo_health_check.py` | Live-site check for page availability, indexability, metadata, structured data, and sitemap coverage. |
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

`styles.css` is shared by the homepage and city pages. A class rename or token
change can therefore affect every public route. Review the homepage and all three
city pages after shared style changes.

## SEO and live-site checks

The production monitor requests the real public site. It checks the homepage,
all city pages, `robots.txt`, and `sitemap.xml`, including indexability, canonical
URLs, metadata, required JSON-LD, business identity, and city-page schema.

Run it manually after a deployment or a material SEO/content change:

```bash
python3 scripts/seo_health_check.py
```

The scheduled GitHub Action runs the same check every Monday at 13:00 UTC. A
failure creates a new GitHub issue or adds a report to the existing open SEO
health issue. Because this test checks the live domain, it is a post-deployment
verification, not a replacement for the local preview.

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

## Design and SEO references

- [Redesign specification](docs/superpowers/specs/2026-07-18-lucky7-redesign-design.md)
- [SEO enhancement specification](docs/superpowers/specs/2026-07-18-lucky7-seo-enhancement-design.md)
- [SEO audit and plan](docs/seo/2026-07-lucky7-seo-audit-and-plan.md)
