# Lucky 7 Towing — SEO Enhancement Design

**Date:** 2026-07-18
**Branch:** `claude/google-seo-audit-prompts-14e06a`
**Status:** Implemented on this branch; draft PR is the approval gate.

## Context

Single-page static site (Bootstrap 5, GitHub Pages + Cloudflare DNS) for Lucky 7 Towing,
a 24/7 towing and roadside assistance business serving Shawano, Bonduel, Wittenberg,
Navarino, Gresham, Pulaski, Cecil, Keshena, Gillett, and rural Northeastern Wisconsin.
AAA-approved provider. Phone (715) 853-8513. Domain: lucky7towingtransport.com.

The user supplied a 20-prompt local-SEO audit framework (GBP, reviews, citations,
keywords, entity optimization) and asked to enhance SEO. Framework preferences honored:
quick wins first, impact-ranked recommendations, real data over guesses.

## Audit findings (from repo + public search)

**On-site issues (fixable in this repo):**

1. JSON-LD `@type` is `AutoRepair` — inaccurate (no repair services). Weakens entity match
   for towing queries.
2. Entity-collision risk: at least four unrelated "Lucky 7 Towing" businesses exist
   (CO, AK, FL, NY). Schema lacks `@id` and disambiguating signals.
3. Hero/LCP image `lucky7_redtowtruck.png` is 1.7 MB; all photos 1.0–1.7 MB PNGs;
   favicon is a 1 MB JPEG referenced 5×. Core Web Vitals (LCP) badly degraded.
4. H1 is brand-only ("Lucky 7 Towing") — no service/location keywords.
5. Meta keywords tag stuffed with irrelevant terms (staff names, "website design") —
   ignored by Google, spam-signal risk elsewhere.
6. Meta description ~182 chars (truncates at ~160).
7. `sameAs` self-references the site (useless); no external profiles linked.
8. `openingHours` string form instead of `openingHoursSpecification` for 24/7.
9. Thin content: no FAQ, minimal service-area depth.
10. "Gillet" typo in contact section (correct: Gillett).
11. Missing `twitter:title`/`twitter:description`; og:image is the 1 MB square logo
    (spec wants 1200×630).
12. No `width`/`height` on images (CLS risk); navbar togglers lack aria-labels.

**Off-site issues (require owner action — documented in the action plan, not this PR):**

- No Google Business Profile, Facebook, Yelp, or directory citation found for the
  Shawano Lucky 7 — the website is currently its only citation on the web.
- Local organic competitor: American Towing (americantowingwi.com, Shawano); rest of
  SERP is lead-gen aggregators (24hr-towing.com, truetowing.com, etc.).

## Approaches considered

1. **Full stack now** — also generate 9 per-city landing pages. Rejected for this pass:
   without owner-supplied local facts/photos, mass city pages risk doorway-page
   thinness and fabricated local claims. Roadmapped instead.
2. **Metadata-only pass** — head tags + schema only. Rejected: leaves the LCP disaster
   and thin content untouched; misses the largest measurable wins.
3. **Deep single-page optimization (chosen)** — fix schema/entity, metadata, headings,
   FAQ content, images/performance, sitemap; ship as one reviewable PR; deliver the
   off-site plan as a document.

## Design

### Structured data (index.html JSON-LD)

- `@type`: `["AutomotiveBusiness", "EmergencyService"]` (accurate parent type + 24/7
  emergency nature; schema.org has no TowingService type).
- Add `"@id": "https://lucky7towingtransport.com/#business"` and keep
  `alternateName: "Lucky 7 Transport"`; retain founder Matthew Torphy (disambiguation).
- 24/7 via `openingHoursSpecification` (all days, 00:00–23:59).
- Keep `areaServed` city list; keep region-level address (service-area business; no
  street address published — owner input needed before adding one).
- Drop self-referencing `sameAs`; add real profiles later when owner creates them.
- No `aggregateRating` (no published reviews — fabrication prohibited).
- Add a `FAQPage` entity for the new FAQ section (no rich-result expectation; content
  relevance only).

### Head metadata

- Keep title (already strong). Meta description trimmed ≤160 chars, keeps
  cities + AAA + phone.
- Remove meta keywords tag entirely.
- Add `twitter:title`, `twitter:description`; point og:image at generated 1200×630 image.
- `preconnect` to cdn.jsdelivr.net; favicon links point at real 32/192/512 PNGs.

### Content and semantics

- H1 becomes brand + service + region, styled to preserve current visual hierarchy
  (brand line stays `display-3`; keyword line styled like current lead).
- Section H2s gain natural keyword/location context; contact typo fixed.
- New FAQ section (5 Q&As) using only facts already published on the site: service
  area, 24/7 availability, AAA coverage, roadside services list, long-distance towing.
- Alt text enriched with honest descriptors; `width`/`height` + `loading`/`decoding`
  attributes; aria-labels on nav togglers.

### Images and performance

- Recompress/resize photos with `sips` into `images/` web variants (~1200px wide JPEG
  ~80 quality); hero gets a dedicated variant; originals retained.
- Generate favicon-32/192/512 PNGs and og-image 1200×630 from the logo.
- Update styles.css hero-bg URL and HTML img srcs.

### Sitemap

- `lastmod` updated to ship date.

## Out of scope (roadmapped in the action plan doc)

Per-city landing pages, GBP creation/optimization, citation building, review program,
backlink outreach, analytics/Search Console wiring. These need owner accounts,
owner facts, or logged-in tools.

## Verification

- Local static serve; desktop + mobile screenshots vs. current design (no visual
  regressions beyond intended copy changes).
- JSON-LD blocks parse as valid JSON; schema types spot-checked.
- Image payload before/after measured.
