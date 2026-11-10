# Website phone-button measurement

## What it answers

Which marketing pages and call controls start phone calls among visitors who allow
analytics? A `phone_click` is call intent only: it is not a connected call, call
duration, recording, qualified lead, or booked tow. Keep the real business number;
there is no forwarding-number service or paid call-tracking subscription.

## Configuration

- Google Analytics 4 destination: `G-30ML7H1C2E`, the public `MEASUREMENT_ID`
  constant in `analytics.js`. Account `415621697`, property `563450829`, web stream
  `16308617758`, Chicago reporting time. An empty ID disables collection.
- Production hosts only: `lucky7towingtransport.com` and its `www` alias over HTTPS.
- Routes measured: homepage, Shawano, Pulaski, and Bonduel. No review or privacy
  page measurement.
- Keep **Enhanced measurement off** in the web stream. This implementation sends
  the intended page view and phone event explicitly; automatic link/form/search
  measurement would collect extra events outside this scope.
- This account's Google tag is managed by container `GTM-PLPR9CLB`. Its settings
  are separate from the web stream: keep automatic event detection and
  user-provided data collection off there too. Set the destination initializer's
  `send_page_view` to `false`; it must not send a default page view before the
  site's explicit event. Keep its advertising and cookie settings aligned with
  `analytics.js` (`cookie_expires: 2592000`, `cookie_update: false`,
  `allow_google_signals: false`, `allow_ad_personalization_signals: false`).
- Advertising features/signals are disabled. No customer names, phone numbers,
  job references, user IDs, or message content belong in analytics parameters.
- The website queues `gtag('set', ...)` before `gtag('js', ...)` for shared page
  and privacy settings. It does not depend on deprecated `gtag('config')` calls:
  the managed destination can ignore them as duplicate configuration.
- Every intentional event also sets its destination, canonical `page_location`,
  fixed `page_title`, and origin-only `page_referrer` directly. Event-scoped values
  take precedence over provider defaults. Queries/fragments never enter these fields.
- GA cookies have a 30-day lifetime without rolling renewal. Preference choice
  persists in `localStorage` as `lucky7_analytics_v1` (`granted` or `denied`).

## Consent and call reliability

No Google tag is requested until permission is granted. A footer control reopens
the in-flow preference panel. Opting out sets Google's documented disable flag,
removes this property's cookies, and propagates to other open site tabs through a
storage event. Previously sent data is not retroactively erased.

Global Privacy Control, Do Not Track, or failed storage keep analytics disabled.
The UI explains these states. Failed tag loading disables collection without
affecting the link, keeps the failure visible, and lets the visitor retry with
**Allow analytics**. A retry starts a fresh queue; events from the failed attempt
are discarded. Cookie cleanup runs only on the production domain, avoiding
invalid-domain errors in local previews. The click handler never calls `preventDefault`, never changes
the number, and never waits for analytics delivery before opening the phone app.

## Events and reporting

| Event/parameter | Meaning |
| --- | --- |
| `page_view` | Consenting visit to a supported marketing page. |
| `phone_click` | Activation of the business's `tel:7158538513` link. |
| `page_name` | `Home`, `Shawano`, `Pulaski`, or `Bonduel`. |
| `link_placement` | `topbar`, `navigation`, `header`, `hero`, `contact`, `faq`, `floating`, or `content`. |

GA4 has event-scoped custom dimensions **Call page** (`page_name`) and **Call button
placement** (`link_placement`). `phone_click` is a key event counted once per event,
with no monetary value assigned. Those admin
settings do not create or prove delivery of an event. Standard reports/custom
dimensions may take time to populate; use Realtime for initial receipt verification.

## Verification

The five HTML references to `analytics.js` (four marketing pages and privacy)
include `?v=` followed by the first 12 characters of the script's SHA-256 hash.
After changing the script, run `shasum -a 256 analytics.js` and update those five
references in the same commit. The Node test rejects missing or stale hashes.
This gives changed code a new asset URL instead of waiting for a browser's cached
copy to expire; a visitor still needs to navigate or reload an already open page.

```sh
node --check analytics.js
node --test tests/analytics.test.cjs
uv run --no-project python -m unittest discover -s tests -v
uv run --no-project python scripts/seo_health_check.py --local
```

Node tests simulate the external tag queue and browser DOM/storage. They do not
contact Google. They exercise consent, decline, persisted choice, revocation,
cross-tab changes, blocked loading/storage, privacy signals, safe event fields,
placement labels, local-host exclusion, native phone navigation, and a managed
initializer that ignores later legacy configuration. The fixture proves command
ordering and event payloads, not the provider's live startup timing. The CI runs
these checks before building GitHub Pages.

For browser verification, serve locally and use the in-app browser on desktop and
a narrow phone viewport. Verify the consent panel, footer reopening, phone access,
and console. Local previews intentionally do not send to the production property.

After deployment, allow analytics in the production site, activate one phone link,
and observe `phone_click` in GA4 Realtime with its expected page and placement.
Opening a phone handler is sufficient; do not place an unnecessary test call.
Use only one open marketing tab for the count check: allowing analytics also
starts other open eligible tabs through the storage event. For one fresh page,
verify exactly one received `page_view`, a fixed page title, canonical location
without a benign validation query, and no raw referring URL. Check the same clean
page fields on the received phone event. If the browser tool blocks `tel:`
navigation, let the owner click; do not bypass that restriction.
Record the observed provider evidence separately from local test results. A queued
JavaScript event alone is not proof that Google received it. Finally revoke
permission and verify the site's analytics disable flag/cookies, without claiming
that an absence in a delayed report proves opt-out.

## Official implementation references

- [Set up events](https://developers.google.com/analytics/devguides/collection/ga4/events)
- [GA4 configuration reference](https://developers.google.com/analytics/devguides/collection/ga4/reference/config)
- [Current Google tag API and parameter scope](https://developers.google.com/tag-platform/gtagjs/reference)
- [Disable Google Analytics](https://developers.google.com/tag-platform/security/guides/privacy#disable-analytics)

Current documentation was verified in the in-app browser on November 9, 2026.
