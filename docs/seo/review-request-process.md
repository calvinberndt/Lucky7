# Review requests for a small, staff-run shop

Staff handle each request after a real completed job. The website supplies the
link and printable card; it has no customer database, form, message sender, or
scheduled follow-up. Hermes can prepare the message when asked, but the staff
member decides when to hand over the card or send it through the channel they
already use with that customer.

## Everyday process

1. Finish the service and any immediate customer conversation.
2. Offer the same optional invitation to customers regardless of how you expect
   them to rate the experience. Do not screen for satisfaction first.
3. Hand over the card, or send the following text through the customer's existing
   conversation. Check that someone else at the shop has not already asked.
4. Leave the choice with the customer. Do not offer a reward, request a particular
   rating, write a review for them, or send automatic reminders.

> Thank you for choosing Lucky 7 Towing. If you'd like to share your experience,
> you're welcome to leave an honest Google review:
> https://lucky7towingtransport.com/review/
> Leaving a review is completely optional.

This invitation is separate from the existing Hermes workflow for replying to
reviews and publishing Google posts. It does not approve or publish either one.

## Card and QR

- Customer landing page: `https://lucky7towingtransport.com/review/`
- Direct Google destination: `https://g.page/r/CW4OS5cVuNBqEBM/review`
- Printable card: `https://lucky7towingtransport.com/review/review-card.svg`
- Standalone QR: `https://lucky7towingtransport.com/review/review-qr.svg`

The SVG card is 5 × 3 inches and embeds the approved badge; it has no external
image or font dependency. Open the downloaded SVG in a browser or print layout
tool. Print at actual size on white paper, check that the complete card is
visible, and scan a physical proof before printing a batch. Keep the white QR
border intact and avoid scaling the card down. Browser font fallbacks may vary.

Both QR codes encode the permanent website page, rather than a tracking redirect
or a vendor account. The page offers one direct Google review link with no
rating gate. If Google changes its link, update that link and its test while
keeping `/review/` stable so printed cards continue to work. Verify the actual
Google business and review screen after any destination change.

The landing page is a utility for existing customers, not a city search landing
page. It has `noindex, follow` and intentionally does not appear in `sitemap.xml`.
Keep it crawlable so search engines can read `noindex`. It does not collect
customer information or load tracking scripts.

## Rebuild and verify

QR generation and independent decoding are development-only tools. The public
site serves static HTML, CSS, and SVG without these Python dependencies.

```sh
uv run --no-project --with qrcode==8.2 python scripts/generate_review_assets.py
uv run --no-project --with qrcode==8.2 python scripts/generate_review_assets.py --check
uv run --no-project --with qrcode==8.2 --with pillow==12.0.0 --with zxing-cpp==2.3.0 python -m unittest discover -s tests -p test_review_assets.py -v
```

The dedicated `Review invitation assets` workflow runs all seven checks, including
ZXing decoding of the actual SVG modules. Standard dependency-free test runs
check the HTML, links, indexing choice, card, and embedded badge; they skip the
three QR-tooling checks when those tools are absent.

Before release, inspect `/review/` at desktop and narrow mobile widths, including
keyboard focus, the persistent call link, downloaded card, and Google destination.
After deployment, repeat those checks on the public domain. A decoded QR or an
HTTP response is not proof that a customer completed a review.
