# Lucky 7 SEO audit and improvements — October 12, 2026

Scope: the homepage and the existing Shawano, Bonduel, and Pulaski pages.
Three independent audits covered content/search intent, technical SEO, and
performance/runtime behavior, followed by implementation and independent review.

## Evidence and changes

| Finding | Improvement |
| --- | --- |
| Homepage H1 was only a slogan | Descriptive 24/7 towing H1 naming Bonduel and Shawano; slogan retained above it, with service details and Pulaski in the lead. |
| Visitors lacked practical call/quote details | Added questions about pickup location, vehicle/destination, recovery, costs, and current availability. No prices or arrival guarantees invented. |
| City copy implied unverified speed or photo location | Removed timing/damage guarantees and the unsupported Shawano destination caption; retained each page's existing local context. |
| Home/city social metadata varied | Unique page descriptions with consistent Open Graph and Twitter cards. |
| Schema included Appleton without visible coverage | Aligned schema to the nine visible service-area towns. Corrected City state containment, added WebSite name/alternate name, and removed metadata-only payment/price claims. |
| FAQ rich-result assumptions were obsolete | Kept and expanded helpful visible FAQs; removed duplicate FAQPage markup. Google retired FAQ rich results in May 2026. |
| Hero reveal effects delayed primary content | Hero text, calls, and photos now appear without entrance delays. Other progressive motion remains. |
| Cross-origin font stylesheet blocked rendering | Self-hosted the same eight licensed Latin font faces with `font-display: swap`; retained family, style, and weight. |
| Full-size JPEGs sent to small screens | WebP photos with responsive candidates and JPEG fallbacks. Original photos remain available. |
| Call plate exceeded a 320px viewport | Reduced narrow-screen call padding/type size; kept the phone number readable. Moved decorative badge inside the mobile viewport. |
| Internal audit notes were published on the domain | Jekyll excludes docs, scripts, tests, and root runbooks. Build CI checks the exclusions. |
| Monitor falsely passed blocked indexing/crawling | Checks all applicable robots directives, duplicate canonicals, XML sitemap integrity, actual visible contact copy, and source links/assets. |

## Verification and measurement

Baseline mobile Lighthouse 12.8.2 on production, default simulated mobile settings:
performance **83**, accessibility **100**, best practices **100**, SEO **100**;
FCP **3.3s**, LCP **3.6s**, TBT **0ms**, CLS **0**.
These are a single lab run, not field Core Web Vitals or Google ranking evidence.
Production results and release evidence are recorded in the pull request.

Local checks cover source and structured data, unit regression tests, JavaScript
syntax, responsive browser behavior, and linked assets. PR CI additionally builds
the actual Jekyll artifact and validates its public pages and exclusions. After
deployment, run the live SEO monitor, browser checks, and the same Lighthouse command:

```bash
npx --yes lighthouse@12.8.2 https://lucky7towingtransport.com/ \
  --only-categories=performance,accessibility,best-practices,seo \
  --chrome-flags='--headless' --output=json \
  --output-path=/tmp/lucky7-lighthouse-mobile.json --quiet
```

## Measurement limits and next steps

No ranking, traffic, call-volume, review-count, or backlink gains are inferred from
these code changes. The historical July audit contains old measurements and a
retracted claim that the Google Business Profile did not exist; those are not a
current baseline. This release does not publish Google Business posts or change
business-profile facts, approvals, or the operational database.

After Google recrawls the site, compare Search Console clicks, impressions, CTR,
queries, and pages over comparable periods. Distinguish branded traffic from
local service searches and keep seasonal changes in mind. Use original job
photography and owner-confirmed details for future service content; do not add
near-identical town pages merely to target more locations.

## Primary references checked

- [Google title links](https://developers.google.com/search/docs/appearance/title-link)
- [Google site names and WebSite structured data](https://developers.google.com/search/docs/appearance/site-names)
- [Google Search documentation updates, FAQ retirement](https://developers.google.com/search/updates)
- [Google people-first content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google crawlable links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)
- [Google sitemap modification dates](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [GitHub Pages and Jekyll exclusions](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll)
