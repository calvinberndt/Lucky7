# Lucky7 browser and search coverage — October 12, 2026

Safari and Firefox are browsers; their users choose a search engine. A site can
work in a browser without being indexed by its chosen search engine, and a map
listing can exist independently of the website's organic search results.

## Website changes

- Keep universal `robots.txt` access and the existing canonical sitemap.
- Check Googlebot, Bingbot, DuckDuckBot, and Applebot crawl access. Check
  documented Google/Bing/Apple indexing directives separately. Honor Apple's
  Googlebot robots fallback when no Applebot group exists.
- Provide an offline-first IndexNow notification tool. Before a POST, the public
  ownership file, sitemap, and every submitted page must match the checkout.
  Submission requires explicit changed URLs selected from the canonical sitemap.
  IndexNow shares notifications with participating engines, including Bing;
  it does not prove indexing or cover every search provider.
- Link the verified Apple Maps place and Bing Maps business search from the
  homepage contact section. Preserve the primary call action and Google reviews.
- Verify actual Firefox and WebKit engines in addition to Chromium. WebKit is
  Safari's engine; automated WebKit evidence is not a test of every Safari/iPhone
  version or native Maps app.

## Existing listings: claim, do not duplicate

Public listings were inspected on October 12, 2026. No accounts were created,
listings edited, or owner verification completed during inspection.

| Provider | Observed public details | Owner action |
| --- | --- | --- |
| [Apple Maps place](https://maps.apple.com/place?place-id=I988AF5C8937E9B1D) | Lucky 7 Towing; Towing Service; N3026 WIS-47, Bonduel WI 54107; correct website. The web details did not expose phone/hours; other Apple surfaces were not inspected. | [Claim this existing listing](https://business.apple.com/?claimId=10991868082367929117). |
| [Bing Maps search](https://www.bing.com/maps/search?q=Lucky+7+Transport+Bonduel+WI) | Lucky 7 Towing; N3026 WI-47, Bonduel WI 54107; (715) 853-8513; correct website; open 24 hours with holiday caveat. | [Manage this existing listing](https://www.bingplaces.com/DashBoard/Edit?Id=YN7EA992F01A5EEDD0&market=en-US&src=SERPIC). |

If a deep link changes, start at [Apple Business](https://business.apple.com/)
or [Bing for Business](https://www.bing.com/forbusiness/), search for the existing
place, and claim it. Do not create a second location. Apple Business Connect is
now called Apple Business. Owner sign-in and provider verification are required.

### Business brief from the current website

| Field | Current value |
| --- | --- |
| Primary name | Lucky 7 Towing |
| Established alternate name | Lucky 7 Transport |
| Website | https://lucky7towingtransport.com/ |
| Phone | +1 715-853-8513 |
| Public email | mattslucky7@gmail.com |
| Address | N3026 State Hwy 47, Bonduel, WI 54107, United States |
| Hours | 24 hours daily |
| Services | Towing, roadside assistance, flatbed towing, vehicle lockouts, flat tire changes, jump starts, fuel delivery, winch-outs/recovery, long-distance transport. |
| Website service towns | Shawano, Bonduel, Wittenberg, Navarino, Gresham, Pulaski, Cecil, Keshena, Gillett, and surrounding rural communities. |

Confirm with the owner whether customers can visit the address before choosing
storefront versus service-area options. Use the nearest category actually offered
by each provider; Apple's existing listing uses Towing Service. Keep the name,
phone, website, hours, address, and approved photos consistent. Do not add arrival
guarantees, prices, or unsupported service areas.

## Measurement and limits

Public map listings are confirmed. Organic indexing is not confirmed: DuckDuckGo
presented a human CAPTCHA and Bing's organic queries were inconclusive. That is
not proof the website is absent. Bing Webmaster Tools can provide verified
indexing/crawl data after owner sign-in and provider-issued website verification.
Never invent verification tokens or use obsolete anonymous sitemap ping URLs.

Release tests, production checks, and the exact IndexNow response belong in the
release PR. Search improvements require recrawling and measurement over time;
neither a passing crawler check nor an accepted notification proves ranking gains.

## Current primary references

- [Safari search settings](https://support.apple.com/en-gb/guide/safari/sfria1042d31/mac)
- [Firefox search settings](https://support.mozilla.org/en-US/kb/change-your-default-search-settings-firefox)
- [DuckDuckGo result sources](https://duckduckgo.com/duckduckgo-help-pages/results/sources): ordinary links and images largely come from Bing.
- [DuckDuckGo map partner](https://duckduckgo.com/duckduckgo-help-pages/company/ads-by-yelp-on-duckduckgo-private-search): Apple Maps.
- [Applebot search and robots behavior](https://support.apple.com/en-us/119829)
- [Apple Business transition](https://support.apple.com/guide/apple-business-connect/apple-business-connect-is-now-apple-business-abcb205640e7/web)
- [Apple location claiming](https://support.apple.com/guide/business/add-a-single-location-abcb98816a34/1/web/1)
- [Bing eligibility and business management](https://www.bing.com/forbusiness/help/modernExperience?setlang=en)
- [Bing Webmaster Tools verification](https://www.bing.com/webmasters/help/add-and-verify-site-12184f8b)
- [IndexNow protocol](https://www.indexnow.org/documentation) and [FAQ](https://www.indexnow.org/faq)
- [Brave crawler](https://search.brave.com/help/brave-search-crawler): follows Googlebot crawl access; no separate advertised Bravebot token.
