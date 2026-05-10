# Lucky 7 Towing Website

Static marketing site for Lucky 7 Towing & Transport at `https://lucky7towingtransport.com/`.

## Current Stack

- Static HTML, CSS, and JavaScript
- Real Lucky 7 truck/logo photography
- Cloudflare Pages-ready redirects and headers
- SEO files: `robots.txt`, `sitemap.xml`, canonical metadata, and JSON-LD

## Local Preview

This site can be opened directly in a browser because it has no build step. For a local HTTP preview, serve the repository root with any static file server.

## Cloudflare Pages Setup

Use the Cloudflare dashboard to connect the GitHub repository.

- Framework preset: `None`
- Production branch: `master`
- Build command: leave blank
- Build output directory: `/`
- Root directory: `/`

Cloudflare Pages should deploy the repository root exactly as-is. The custom domain should remain `lucky7towingtransport.com`, with `www.lucky7towingtransport.com` redirected to the apex domain.

## SEO Preservation

When changing hosting providers, keep these stable:

- Domain: `https://lucky7towingtransport.com/`
- Canonical URL
- Existing root URL
- `robots.txt`
- `sitemap.xml`
- Phone-first emergency towing content
- Local service area content for Shawano and rural Northeastern Wisconsin

## Rollback

Keep GitHub Pages enabled until Cloudflare Pages is verified. If Cloudflare Pages needs to be rolled back, point the apex and `www` DNS records back to GitHub Pages and keep the existing `CNAME` file in the repository.
