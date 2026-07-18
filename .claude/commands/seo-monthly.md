---
description: Monthly Lucky 7 SEO audit — pull Search Console + Business Profile numbers, compare competitors, update the scorecard
---

Run the monthly SEO scorecard for Lucky 7 Towing (lucky7towingtransport.com).
Prerequisite: the Claude Chrome extension must be connected and the browser
signed into the Google account that manages the "Lucky 7 Towing" Business
Profile. If the browser isn't available, say so and stop — don't guess numbers.

Business facts: Lucky 7 Towing (DBA Lucky 7 Transport), N3026 State Hwy 47,
Bonduel, WI 54107, (715) 853-8513, USDOT 1237637. Review share link:
https://g.page/r/CW4OS5cVuNBqEBM/review

Steps:

1. **Search Console** (search.google.com/search-console, domain property
   lucky7towingtransport.com): from the last-28-days Performance report,
   record total clicks, impressions, average CTR, and average position, plus
   the top 10 queries. Note position movement on "towing near me",
   "tow truck near me", "towing service shawano wi", and "shawano towing"
   versus the previous scorecard entry.
2. **Business Profile** (google.com/maps search "Lucky 7 Towing" while signed
   in, or the merchant panel on google.com search): record review count,
   rating, review velocity since last month, unanswered reviews (reply to any
   new positive ones in Matt's short, warm voice; draft-only for anything
   negative or complicated), profile views/interactions if visible, and
   whether pending edits (categories, address) have gone live.
3. **Competitor pulse**: on Google Maps (public data only, no login needed),
   record American Towing's (Shawano) review count and rating for the
   comparison column.
4. **Site spot-check**: run `python3 scripts/seo_health_check.py` from the
   repo root and note the result.
5. **Scorecard**: append one dated row/section to `docs/seo/scorecards.md`
   (create the file with a short header table if it doesn't exist):
   date · GSC clicks · impressions · avg position · review count · review
   velocity · American Towing review count · health-check pass/fail.
   Commit on a `chore/seo-scorecard-<yyyy-mm>` branch and open a PR.
6. **Close with the monthly verdict** in plain language for Matt: 3 wins,
   1 problem, and the single most important action for next month, with the
   review link ready to copy.

Never scrape Google search result pages for rankings, never log into any
account, and never fabricate numbers — if a metric is unavailable, record it
as "not available" with the reason.
