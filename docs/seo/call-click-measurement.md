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
- Advertising features/signals are disabled. No customer names, phone numbers,
  job references, user IDs, or message content belong in analytics parameters.
- `page_location` uses only the fixed canonical route, and `page_referrer` only
  the referring origin. Queries/fragments never enter these fields.
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

```sh
node --check analytics.js
node --test tests/analytics.test.cjs
uv run --no-project python -m unittest discover -s tests -v
uv run --no-project python scripts/seo_health_check.py --local
```

Node tests simulate the external tag queue and browser DOM/storage. They do not
contact Google. They exercise consent, decline, persisted choice, revocation,
cross-tab changes, blocked loading/storage, privacy signals, safe event fields,
placement labels, local-host exclusion, and native phone navigation. The CI runs
these checks before building GitHub Pages.

For browser verification, serve locally and use the in-app browser on desktop and
a narrow phone viewport. Verify the consent panel, footer reopening, phone access,
and console. Local previews intentionally do not send to the production property.

After deployment, allow analytics in the production site, activate one phone link,
and observe `phone_click` in GA4 Realtime with its expected page and placement.
Opening a phone handler is sufficient; do not place an unnecessary test call.
Record the observed provider evidence separately from local test results. A queued
JavaScript event alone is not proof that Google received it. Finally revoke
permission and verify the site's analytics disable flag/cookies, without claiming
that an absence in a delayed report proves opt-out.

## Official implementation references

- [Set up events](https://developers.google.com/analytics/devguides/collection/ga4/events)
- [GA4 configuration reference](https://developers.google.com/analytics/devguides/collection/ga4/reference/config)
- [Disable Google Analytics](https://developers.google.com/tag-platform/security/guides/privacy#disable-analytics)

Current documentation was verified in the in-app browser on November 9, 2026.
