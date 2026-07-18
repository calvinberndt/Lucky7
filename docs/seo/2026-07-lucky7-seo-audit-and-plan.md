# Lucky 7 Towing — SEO Audit & 90-Day Action Plan

**Date:** July 18, 2026 · **Site:** lucky7towingtransport.com · **Branch:** [PR #3](https://github.com/calvinberndt/Lucky7/pull/3)

Adapted from the 20-prompt Google-presence audit framework. Everything below is grounded
in the repo, the live site, public search results, and the federal FMCSA carrier registry —
no guessed data. Per your working preferences: quick wins first, impact level and
time-to-results on every recommendation.

---

## Executive summary

The website was in decent on-page shape and is now in very good shape (PR #3). **The
business's real problem is off-site: Lucky 7 has essentially zero Google presence beyond
the website itself.** A phone-number search for (715) 853-8513 returns exactly one
result — the website. No Google Business Profile surfaced in search, no Facebook, no
Yelp, no directory citations. Meanwhile at least four unrelated "Lucky 7 Towing"
companies exist (Colorado, Alaska, Florida, New York), so Google has to guess which
Lucky 7 is which.

For a towing company, the Google Map Pack drives the overwhelming majority of calls —
someone stranded on WI-29 searches "towing near me" and calls whoever appears. Without
a Google Business Profile, Lucky 7 cannot appear there at all. **Creating and verifying
the GBP is worth more than everything else in this plan combined.**

The good news: the local competitive field is thin. Only one real Shawano-area
competitor (American Towing) shows organically; the rest of page 1 is lead-gen
aggregator sites. A verified GBP + steady reviews + the now-solid website is a
realistic path to owning this market's map pack.

---

## What shipped today (on-site, PR #3)

| Fix | Impact | Time to results |
|---|---|---|
| Hero/LCP image 1.67 MB → 246 KB; all photos compressed 79–92% | High (Core Web Vitals → rankings + fewer bounced callers on rural cell service) | 1–4 weeks after merge |
| JSON-LD business type corrected (`AutoRepair` → Automotive + Emergency) with USDOT 1237637 identifier + FMCSA registry link | High (entity disambiguation vs. the four other Lucky 7s) | 2–8 weeks |
| Verified city-level address (Bonduel, WI 54107) in schema, contact, footer | High (local relevance previously region-only) | 2–8 weeks |
| Keyword-bearing H1 + location-rich headings | Medium-high | 2–6 weeks |
| New FAQ section + FAQPage schema (5 Q&As, facts only) | Medium (long-tail queries, AI-overview eligibility) | 4–12 weeks |
| Meta description ≤160 chars; spammy meta-keywords removed; Twitter/OG cards completed; real favicons; 1200×630 share image | Medium (CTR + share appearance) | Immediate on merge |
| Gillett typo, aria-labels, width/height CLS guards | Low-medium hygiene | Immediate |

**Verified business identity used throughout** (source: FMCSA SAFER, phone-number match):
legal DBA **"Lucky 7 Transport"**, Bonduel, WI 54107, USDOT **1237637**, active carrier,
3 power units, owners Matt & Tabitha Torphy.

---

## Competitive picture (public search, July 2026)

| Business | Domain | Notes from public results |
|---|---|---|
| **American Towing** | americantowingwi.com | The only real local competitor ranking organically. Shawano + Menominee counties, 20+ years, has a Facebook page, dedicated service pages (e.g. light/medium vehicle towing). |
| Klein GM / Klein CDJR | kleingm.com / kleindodge.net | Dealership towing pages, Clintonville/Waupaca — edge of your area. |
| 24hr-towing.com, truetowing.com, superior-towing-service.com, 4roadservice.com | — | National lead-gen aggregators with "Shawano" landing pages. They rank because no local business is contesting the space. They resell calls. |
| **Lucky 7 Towing** | lucky7towingtransport.com | Ranks for brand + appears in generic towing results. No GBP/citations found. |

Read on the aggregators: their presence is a *signal of weak local competition*. Real
local sites with real GBPs typically displace them.

*(Per your framework's spreadsheet preference — once your GBP exists, the review-velocity
and category-gap comparisons vs. American Towing become possible; prompts below.)*

---

## 90-day plan, ranked

### Week 1 — Create the Google Business Profile ⚡ highest-impact action available

**Impact: very high · Results: 1–3 weeks after verification · Owner must do this (requires your Google account)**

1. Go to business.google.com → "Add business".
2. **Name:** must be your real-world name per Google rules — the name on your trucks
   ("Lucky 7 Transport"). See *Decision 1* below before creating.
3. **Type:** Service-area business (hide address if it's your residence — towing SABs
   routinely do this). Service area: Shawano, Bonduel, Wittenberg, Navarino, Gresham,
   Pulaski, Cecil, Keshena, Gillett + surrounding.
4. **Primary category:** "Towing service". Then in the category picker, search and add
   every secondary that genuinely applies (look for roadside-assistance and
   transport-related options — add only what you actually do).
5. Phone (715) 853-8513, site lucky7towingtransport.com, 24/7 hours.
6. Verify (video verification is common for SABs), then immediately: upload 10–15 real
   job photos (you already have great ones), fill the services list (mirror the site's
   six services + descriptions), write the description (adapt the site's), enable
   messaging if you'll answer it.

### Weeks 1–2 — Core citations (NAP consistency)

**Impact: high · Results: 2–6 weeks · ~2 hours total, owner accounts needed**

Use the *identical* name/phone/city everywhere (whatever you decide in Decision 1):

- Bing Places (can import from GBP), Apple Business Connect
- Facebook business page (this also unlocks community-group word of mouth — rural
  Wisconsin runs on Facebook)
- Yelp, BBB, Nextdoor, Yellow Pages
- AAA's provider locator: you're an approved provider — ask your AAA territory manager
  what public listings exist and that your info is correct. An AAA-affiliated citation
  is a trust signal competitors can't fake.

### Weeks 2–8 — Review engine

**Impact: very high (the #1 map-pack ranking + conversion factor) · Results: continuous**

- After each job, text the customer your Google review link (GBP gives you a short
  link once live). Towing customers are *grateful* — ask while the gratitude is fresh.
- Ask happy customers to mention the town and service naturally ("jump start in
  Pulaski") — review text is a ranking signal.
- Respond to every review within 48h, mentioning service + area naturally. Template:
  - 5★: "Thanks [name]! Glad we could get your [vehicle] moving again out in [town].
    We're here 24/7 whenever you need us. — Matt"
  - Negative: thank → own it → take it offline ("call me directly at (715) 853-8513").
- Target: steady 2–4 reviews/month beats a one-time burst. Once live, check American
  Towing's count/velocity on their GBP and set the catch-up target (your framework's
  prompt 3 — now runnable).

### Weeks 4–8 — GBP activity cadence

**Impact: medium · Results: 4–8 weeks**

- 1–2 GBP posts/week: job-of-the-week photo with town mentioned ("Flatbed recovery
  outside Gresham this morning"), seasonal safety notes (winter dead-battery season is
  your Super Bowl), AAA reminders.
- 3–5 photos/week from real jobs. Consistency beats volume — steady uploads signal an
  active business.

### Weeks 6–12 — Website expansion (I can build these when you're ready)

**Impact: medium-high compounding · Results: 2–4 months**

- **Service+city pages**, starting with the anchor towns: `/towing-shawano-wi`,
  `/towing-pulaski-wi`, `/towing-bonduel-wi`. Each needs 2–3 real local details to
  avoid doorway-page thinness — a job photo taken in that town, roads you actually
  patrol, response-time reality. Send me one voice memo of local notes per town and
  I'll draft them.
- **Search Console + GA4**: verify the domain in Search Console (DNS TXT via
  Cloudflare), submit sitemap.xml, add GA4. Without this, we're flying blind on
  which queries convert. I can walk you through it or do it in an interactive
  session with your browser signed in.

### Monthly — 15-minute scorecard (your framework's prompt 20, right-sized)

Calls from GBP · direction requests · review count/velocity · Search Console clicks
and top queries · map-pack position for "towing shawano wi" (check in an incognito
window from a local IP). Three wins, one problem, one action for next month.

---

## Decisions only you can make

1. **Business name for GBP/citations: "Lucky 7 Transport" (trucks, DBA, USDOT) vs
   "Lucky 7 Towing" (website brand).** Google requires the real-world name; mismatched
   names across listings is the classic NAP trap. My recommendation: use **Lucky 7
   Transport** everywhere official (it's what's on the trucks and the federal record),
   keep "towing" in the website title/tagline for search — that's compliant and
   consistent. If AAA dispatch paperwork says "Lucky 7 Towing", tell me and we'll flip it.
2. **Publish the street address?** I kept it city-level (Bonduel, WI 54107) since the
   registered address may be your home. GBP as a service-area business doesn't need it
   public either. Say the word if you want it shown.
3. **Founding year** — "20+ years" is on the site; an exact year ("Since 200X") is a
   stronger trust line for the footer and GBP.
4. **Does a Facebook page already exist?** None surfaced in search. If one exists under
   a different name, we link it in `sameAs` instead of creating new.

---

## Framework prompts: what applies when

Your 20-prompt stack assumes an existing GBP + paid tool logins. Status for Lucky 7:

- **Runnable now (no GBP needed):** ✅ done in this session — citation audit (15),
  entity optimization (18), money-page/on-page audit (10), services/description
  optimization (6, 7), photo audit (8, on-site portion).
- **Runnable once GBP is live:** category audit (1), attributes (2), review teardown
  vs American Towing (3), response strategy (4), posts strategy (5, 19) — run these in
  an interactive session; I'll pull competitor GBP data through the browser.
- **Needs tool accounts you don't have yet:** keyword gap (9), GSC analysis (12),
  backlink audit (14), intent mapping (16), content gap (17) — Search Console is free
  (set it up in weeks 6–12 above); Ahrefs/SEMrush are optional at this market size.
  Note: I can't log into accounts or handle credentials — you stay signed in in your
  browser and I work through it with you.

---

*Prepared with Claude Code · sources: repo history, lucky7towingtransport.com,
FMCSA SAFER snapshot (USDOT 1237637), public web search July 2026.*
