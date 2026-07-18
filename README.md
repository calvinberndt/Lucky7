# Lucky 7 Towing & Transport — Website

Single-page marketing site for Lucky 7 Towing / Lucky 7 Transport (Bonduel, WI), live at
[lucky7towingtransport.com](https://lucky7towingtransport.com) via GitHub Pages (see `CNAME`).

## Design

Custom "vintage American roadside" design system derived from the company's clover badge
logo and truck decals — no CSS framework. See the full design spec at
[`docs/superpowers/specs/2026-07-18-lucky7-redesign-design.md`](docs/superpowers/specs/2026-07-18-lucky7-redesign-design.md).

- **Palette:** deep greens `#15271b`/`#1e3d26`/`#2d5937`, cream `#faf5e8`, brick red `#b3272e`,
  beacon amber `#e9a23b` — defined as CSS custom properties at the top of `styles.css`.
- **Type:** Alfa Slab One (display) + Barlow / Barlow Condensed (body/UI), loaded from
  Google Fonts.
- **Artwork:** inline SVG throughout — clover mark, custom service icons, and the
  schematic service-area map (town positions projected from real lat/lon).

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole site: markup, inline SVG artwork, JSON-LD structured data |
| `styles.css` | Design tokens + all styling, responsive + reduced-motion aware |
| `script.js` | Mobile menu, header shadow, scroll reveals, pinned-scene scrubbing (fleet deck + steps road), the dispatch map (road graph, Dijkstra routing, patrol), stat count-ups |
| `images/` | Originals (`lucky7_*.png/.jpg`) plus optimized derivatives used by the site |

## Working on the site

No build step. Serve statically and open the port the server prints:

```bash
python3 -m http.server 4173 --directory .
```

### Images

Derivatives are generated from the originals with `sips` (macOS). If you replace a photo,
re-derive a web-sized JPEG (~900–1250px wide, quality ~70) and keep `width`/`height`
attributes in `index.html` in sync to avoid layout shift. Favicons come from the badge logo.

### Updating facts

- **Phone number** appears in `tel:` links and visible text — search for `853-8513`.
- **Reviews** in the Reviews section are real quotes from the Google Business listing;
  refresh them from the listing rather than inventing copy.
- **Towns / service area:** update the text lists, the SVG map town groups in
  `index.html`, the `areaServed` array in the JSON-LD block, **and** the `NODES`
  coordinates + `EDGES` road connections in `script.js` — every clickable town in
  the SVG must have a matching `NODES` entry and at least one `EDGES` entry, or
  the dispatch truck can't route there (it will fall back to teleporting).

## SEO

Title/description/canonical/OG tags plus `AutomotiveBusiness` JSON-LD live in `index.html`.
The Google Business Profile ("Lucky 7 Towing", Bonduel WI) links here — keep name, phone,
and hours consistent between the two.
