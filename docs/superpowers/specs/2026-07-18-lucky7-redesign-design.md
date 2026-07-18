# Lucky 7 Towing & Transport — Website Redesign Spec

**Date:** 2026-07-18 · **Author:** Claude (with Calvin Berndt) · **Status:** Implemented on branch `claude/lucky-7-transport-redesign-efeee5` for review

## 1. Purpose & audience

Single-page marketing site for Lucky 7 Towing / Lucky 7 Transport (Matt Torphy, Bonduel WI).
Two audiences, in priority order:

1. **Stranded driver on a phone** (rural Northeastern Wisconsin, often poor signal). Job: get the
   phone number tappable within seconds, build instant "these are real local people" confidence.
2. **Planner/researcher** (scheduled tow, equipment transport, AAA member comparing providers).
   Job: trust signals — AAA approval, 20+ years, 5.0★ Google rating, US DOT number, real photos.

**Success criteria:** phone number visible and tappable from every scroll position; page loads fast
on 1-bar LTE (was ~6MB of images; target < 1MB total); the design feels like *their* brand
(vintage clover badge on the trucks), not a Bootstrap template.

## 2. Evidence gathered

- **Codebase:** Bootstrap 5.3.3 template, generic `#28a745` greens, red→green gradient contact
  card, 1.7MB hero PNG (preloaded), 1MB JPG used as favicon, desktop navbar shows a stray
  hamburger (toggler visibility bug), "Gillet" typo, © 2025.
- **Artwork:** vintage badge logo (deep green field, cream lettering, brick-red 7, black ribbon);
  red C5500 flatbed "Pete" already cut out on black (unused!); red Freightliner hauling a classic
  Morgan; yellow trucks on AAA dispatch + winter bus recovery.
- **Google Business listing (public):** "Lucky 7 Towing", 5.0★ × 7 reviews, Towing service,
  Open 24 hours, correct phone/site links, owner responds to reviews, operates out of Bonduel.
  Three usable review quotes captured (Kimberly M., Brett B., Ben B.).

## 3. Approaches considered

- **A. Restyle Bootstrap in place.** Fast, low risk; but keeps ~200KB framework for one page,
  caps design quality at "nicer template," constant `!important` fights.
- **B. Custom rebuild on a vintage-roadside design system.** *(Chosen.)* Drop Bootstrap; small
  hand-rolled CSS system + vanilla JS; custom SVG artwork (icons, service-area map, badges);
  layered hero from the existing truck cutout; real Google review testimonials; performance
  overhaul. Most work, but the site is one page — tractable, and it's the only option that
  delivers "enhance the artwork."
- **C. Full rebrand (new logo/photography/motion).** Rejected: the clover badge is on their
  physical trucks; the web should amplify the existing brand, not replace it.

## 4. Design direction — "Vintage American roadside service"

Derived from their own logo and trucks, not imposed taste.

**Palette** (CSS custom properties):
- Greens: `#0d1710` (near-black), `#15271b`, `#1e3d26`, `#2d5937` (brand), `#3f7a4e` (clover)
- Cream/paper: `#faf5e8` page, `#f1e8d2` panels, `#e6d8b8` borders, `#f4edda` text-on-dark
- Brick red: `#b3272e` primary CTA (logo "7"), `#8f1f25` hover/deep
- Beacon amber: `#e9a23b` sparing accents (hazard stripes, star ratings, highlights)
- Ink: `#181f19` body text on cream
- Contrast: body ink-on-cream ≈ 13:1; cream-on-green-900 ≥ 9:1; cream-on-red ≥ 5:1 (large/bold only).

**Type:** Alfa Slab One (display; Clarendon-slab kin to the logo lettering) + Barlow /
Barlow Condensed (body/UI; US-highway-signage DNA). Fluid scale via `clamp()`.

**Signature artwork** (all inline SVG / CSS — no new raster assets):
1. Layered hero: near-black green with SVG grain + giant 4%-opacity clover watermark; the
   black-background truck cutout feathered in with a CSS radial `mask-image`; amber
   hazard-stripe divider at the base.
2. Custom 6-icon service set (tow hook, tire/wrench, route shield, collision, fuel can, bolt) —
   one 24px stroke grid, round caps, replaces bootstrap-icons font.
3. Service-area map: SVG with the nine towns plotted from real relative lat/lon, dashed county
   roads, clover pin on Bonduel HQ, "not to scale" note.
4. Badge chips: AAA APPROVED / OPEN 24-7 / 20+ YEARS / US DOT 1237637 as stamped outlines;
   5.0★ Google rating plate.
5. Slab numerals 1-2-3 for "How it works", styled like the logo's red 7 (cream keyline).
6. Photo wall treatment for fleet/about shots: cream mats, slight alternating rotation,
   caption plates; straighten on hover.

**Voice:** confident, local, lightly playing the luck theme. Hero: "When your luck runs out,
ours rolls in." Keyword-rich supporting copy retains towing/roadside/Shawano terms for SEO.

## 5. Page flow (single page, revised IA)

1. **Sticky header** — text lockup (LUCKY 7 + clover SVG + "Towing & Transport"), anchor nav,
   always-visible red call button (number visible on desktop; icon+"24/7" on mobile).
2. **Hero (dark)** — eyebrow, display headline, subhead with service region, giant phone plate,
   trust chip row (AAA · 5.0★ Google · 20+ years · 24/7), layered truck art.
3. **How it works (cream)** — 3 steps: call → tell us where you are → we roll out.
4. **Services (cream)** — 6 cards, custom icons, tightened copy.
5. **Trust band (green)** — stats: 20+ years, 24/7, 9 communities, AAA approved, US DOT.
6. **About (cream)** — story + Morgan classic-car photo; owner-operated by Matt Torphy.
7. **Fleet (cream)** — 3 framed photos with honest captions.
8. **Service area (cream/paper)** — SVG map + town list + long-distance note.
9. **Reviews (green)** — 3 real Google quotes, 5.0★ badge, "read all / leave a review" links.
10. **Contact (near-black)** — giant number, email, AAA note, DOT, towns recap.
11. **Footer** — copyright 2026, licensed & insured, small site credit.
12. **Floating call button** — mobile only, brand red, reduced-motion-aware pulse.

## 6. Technical plan

- **Drop Bootstrap CSS/JS and bootstrap-icons** (CDN). Replace with one custom `styles.css`
  (design tokens + components) and small vanilla `script.js` (menu toggle, IntersectionObserver
  reveals, header state). Google Fonts via CDN with `preconnect` + `display=swap`.
- **Images:** `sips`-generated derivatives in `images/` (originals kept): hero cutout ~1400w
  JPEG, gallery ~900w JPEGs, square favicon set (32/180/192/512) cropped from the badge logo,
  1200×630 OG JPEG. `width`/`height` attributes everywhere (no CLS); below-fold `loading="lazy"`.
- **SEO:** keep title/description/canonical/OG/Twitter (og:image → new file). JSON-LD: type →
  `AutomotiveBusiness`, `addressLocality` → Bonduel (matches GBP), fix Gillett spelling, keep
  areaServed/offer catalog. No `aggregateRating` markup (third-party reviews; against policy) —
  stars shown visually instead.
- **Accessibility:** skip link, landmarks, single h1, focus-visible rings, `prefers-reduced-motion`
  disables pulse/reveals, ≥44px tap targets, alt text audit, contrast per palette table.
- **No build step** — stays a plain static GitHub Pages site.

## 7. Out of scope

Logo redesign; multi-page split; booking/forms (call-first business); GBP management actions
(photo uploads, posts — require Calvin's signed-in Google session); analytics.

## 8. Verification

Drive the site in the browser at 1280×800 and 375×812: all anchors, tel:/mailto: links, menu
toggle, reveal animations, console clean; visual pass against this spec; before/after screenshots
in the PR.
