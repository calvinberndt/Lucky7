const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'analytics.js'), 'utf8');
const key = 'lucky7_analytics_v1';

function fixture(options = {}) {
  const scripts = [], cookies = [], warnings = [], handlers = {}, windowHandlers = {};
  const stored = new Map(options.choice ? [[key, options.choice]] : []);
  const panel = { hidden: true, scrollIntoView() { this.scrolled = true; }, focus() { this.focused = true; } };
  const status = { textContent: '' }, allow = { disabled: false }, settings = { hidden: true };
  const nodes = { '[data-analytics-panel]': panel, '[data-analytics-status]': status,
    '[data-analytics-allow]': allow, '[data-analytics-settings]': settings };
  const document = {
    referrer: options.referrer || '',
    querySelector(selector) { return options.noPanel ? null : nodes[selector]; },
    createElement(tag) { return { tagName: tag, remove() { this.removed = true; } }; },
    head: { appendChild(node) { if (options.insertionBlocked) throw new Error('blocked'); scripts.push(node); } },
    addEventListener(type, callback) { handlers[type] = callback; },
    set cookie(value) { if (options.cookieBlocked) throw new Error('blocked'); cookies.push(value); }
  };
  const window = {
    location: new URL(options.url || 'https://lucky7towingtransport.com/towing-shawano-wi/'),
    localStorage: {
      getItem(name) { if (options.readBlocked) throw new Error('blocked'); return stored.get(name) ?? null; },
      setItem(name, value) { if (options.writeBlocked) throw new Error('blocked'); stored.set(name, value); }
    },
    addEventListener(type, callback) { windowHandlers[type] = callback; },
    doNotTrack: options.windowDnt
  };
  const measurementId = options.measurementId === undefined ? 'G-TEST123' : options.measurementId;
  const code = source.replace(/var MEASUREMENT_ID = '[^']*';/, 'var MEASUREMENT_ID = ' + JSON.stringify(measurementId) + ';');
  vm.runInNewContext(code, { window, document, URL, navigator: options.navigator || {},
    console: { warn(message) { warnings.push(message); } } });
  function click(matches, props = {}) {
    const target = { closest(selector) { return matches[selector] || null; } };
    const event = { target, defaultPrevented: false, ...props,
      preventDefault() { throw new Error('Analytics must never block native navigation'); } };
    handlers.click(event);
    return event;
  }
  function choose(value) { click({ ['[data-analytics-' + value + ']']: {} }); }
  function phone(place = {}, props = {}) {
    const link = { href: 'tel:7158538513', classList: { contains(name) { return Boolean(place[name]); } },
      closest(selector) { return place[selector] || null; } };
    click({ 'a[href="tel:7158538513"]': link }, props);
    return link;
  }
  function commands() { return (window.dataLayer || []).map(args => Array.from(args)); }
  return { scripts, cookies, warnings, handlers, windowHandlers, stored, panel, status, allow, settings,
    window, document, click, choose, phone, commands };
}

test('first visit makes no Google request and call remains native', () => {
  const f = fixture();
  assert.equal(f.scripts.length, 0);
  assert.equal(f.commands().length, 0);
  assert.equal(f.panel.hidden, false);
  assert.equal(f.phone().href, 'tel:7158538513');
  assert.equal(f.commands().length, 0);
});

test('decline persists without loading Google and settings can reopen', () => {
  const f = fixture();
  f.choose('decline');
  assert.equal(f.stored.get(key), 'denied');
  assert.equal(f.panel.hidden, true);
  assert.equal(f.scripts.length, 0);
  f.click({ '[data-analytics-settings]': {} });
  assert.equal(f.panel.hidden, false);
  assert.equal(f.panel.focused, true);
  assert.equal(f.panel.scrolled, true);
  assert.equal(fixture({ choice: 'denied' }).scripts.length, 0);
});

test('allow loads one tag, sanitized page view, and no advertising permission', () => {
  const f = fixture({ url: 'https://lucky7towingtransport.com/towing-shawano-wi/?name=private#secret',
    referrer: 'https://example.com/private/customer?phone=123#private' });
  f.choose('allow');
  f.choose('allow');
  assert.equal(f.scripts.length, 1);
  assert.equal(f.scripts[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-TEST123');
  const config = f.commands().find(c => c[0] === 'config')[2];
  assert.equal(config.page_location, 'https://lucky7towingtransport.com/towing-shawano-wi/');
  assert.equal(config.page_referrer, 'https://example.com/');
  assert.equal(config.page_title, 'Lucky 7 Towing — Shawano');
  assert.equal(config.allow_google_signals, false);
  assert.equal(config.allow_ad_personalization_signals, false);
  assert.equal(config.cookie_expires, 2592000);
  assert.equal(config.cookie_update, false);
  assert.equal(config.send_page_view, false);
  const consent = f.commands().find(c => c[0] === 'consent')[2];
  assert.equal(consent.ad_storage, 'denied');
  assert.equal(consent.ad_user_data, 'denied');
  assert.equal(consent.ad_personalization, 'denied');
  assert.equal(f.commands().filter(c => c[1] === 'page_view').length, 1);
  assert.equal(fixture({ choice: 'granted' }).scripts.length, 1);
});

test('nested icon and keyboard-style clicks report fixed placement without interrupting call', () => {
  const f = fixture({ choice: 'granted' });
  for (const [place, expected] of [
    [{ 'floating-call-btn': true }, 'floating'], [{ 'topbar-phone': true }, 'topbar'],
    [{ '.site-nav': {} }, 'navigation'], [{ '.site-header': {} }, 'header'],
    [{ '.hero-cta': {} }, 'hero'], [{ '.cta-band': {} }, 'contact'],
    [{ '#faq': {} }, 'faq'], [{}, 'content']
  ]) {
    assert.equal(f.phone(place, { detail: 0 }).href, 'tel:7158538513');
    const last = f.commands().at(-1);
    assert.equal(last[1], 'phone_click');
    assert.equal(last[2].link_placement, expected);
    assert.equal(last[2].page_name, 'Shawano');
    assert.deepEqual(Object.keys(last[2]).sort(), ['link_placement', 'page_name']);
  }
});

test('unrelated, missing-target, and already-cancelled clicks are not leads', () => {
  const f = fixture({ choice: 'granted' });
  const before = f.commands().length;
  f.click({});
  f.handlers.click({ target: null });
  f.phone({}, { defaultPrevented: true });
  assert.equal(f.commands().length, before);
});

test('revoke disables collection, clears cookies, and does not load another tag', () => {
  const f = fixture({ choice: 'granted' });
  f.phone();
  f.choose('decline');
  const before = f.commands().length;
  f.phone();
  assert.equal(f.commands().length, before);
  assert.equal(f.window['ga-disable-G-TEST123'], true);
  assert.ok(f.cookies.some(cookie => cookie.startsWith('_ga=; Max-Age=0;')));
  assert.ok(f.cookies.some(cookie => cookie.startsWith('_ga_TEST123=; Max-Age=0;')));
  f.choose('allow');
  f.phone();
  assert.equal(f.window['ga-disable-G-TEST123'], false);
  assert.equal(f.commands().at(-1)[1], 'phone_click');
  assert.equal(f.scripts.length, 1);
});

test('another tab revoking or clearing consent stops this tab', () => {
  for (const eventKey of [key, null]) {
    const f = fixture({ choice: 'granted' });
    f.stored.clear();
    f.windowHandlers.storage({ key: eventKey });
    const before = f.commands().length;
    f.phone();
    assert.equal(f.commands().length, before);
    assert.equal(f.window['ga-disable-G-TEST123'], true);
  }
  const f = fixture();
  f.stored.set(key, 'granted');
  f.windowHandlers.storage({ key: 'unrelated' });
  assert.equal(f.scripts.length, 0);
  f.windowHandlers.storage({ key });
  assert.equal(f.scripts.length, 1);
});

test('privacy signals and unavailable preference storage fail closed', () => {
  for (const options of [
    { navigator: { globalPrivacyControl: true } }, { navigator: { doNotTrack: '1' } },
    { navigator: { doNotTrack: 'yes' } }, { windowDnt: '1' }, { readBlocked: true }, { writeBlocked: true }
  ]) {
    const f = fixture({ ...options });
    f.choose('allow');
    f.phone();
    assert.equal(f.scripts.length, 0, JSON.stringify(options));
    assert.equal(f.window['ga-disable-G-TEST123'], true);
  }
  assert.equal(fixture({ choice: 'granted', navigator: { globalPrivacyControl: true } }).scripts.length, 0);
});

test('blocked script or cookie storage never prevents a call', () => {
  const f = fixture({ choice: 'granted', cookieBlocked: true });
  f.scripts[0].onerror();
  const before = f.commands().length;
  assert.equal(f.phone().href, 'tel:7158538513');
  assert.equal(f.commands().length, before);
  assert.match(f.status.textContent, /could not load/);
  assert.equal(f.warnings.length, 1);
  const insertionBlocked = fixture({ choice: 'granted', insertionBlocked: true });
  assert.equal(insertionBlocked.phone().href, 'tel:7158538513');
  assert.equal(insertionBlocked.scripts.length, 0);
  assert.equal(insertionBlocked.window['ga-disable-G-TEST123'], true);
});

test('invalid configuration and unrecognized saved preference do not enable collection', () => {
  for (const measurementId of ['', 'not-an-id', 'G-ID?private']) {
    const f = fixture({ choice: 'granted', measurementId });
    assert.equal(f.scripts.length, 0);
    f.phone();
    assert.equal(f.commands().length, 0);
  }
  const f = fixture({ choice: 'unexpected' });
  assert.equal(f.scripts.length, 0);
  assert.equal(f.panel.hidden, false);
});

test('failed tag remains visibly failed and a deliberate retry starts one fresh queue', () => {
  const f = fixture({ choice: 'granted' });
  f.phone();
  f.scripts[0].onerror();
  assert.equal(f.panel.hidden, false);
  assert.match(f.status.textContent, /could not load/);
  assert.equal(f.commands().length, 0, 'failed-attempt events must not replay on retry');
  f.click({ '[data-analytics-settings]': {} });
  assert.match(f.status.textContent, /could not load/);
  f.choose('allow');
  assert.equal(f.scripts.length, 2);
  assert.equal(f.commands().filter(c => c[1] === 'page_view').length, 1);
  assert.equal(f.commands().filter(c => c[1] === 'phone_click').length, 0);
  f.choose('allow');
  assert.equal(f.scripts.length, 2, 'a pending retry must not start another tag');
  f.phone();
  assert.equal(f.commands().at(-1)[1], 'phone_click');
});

test('only production HTTPS marketing routes collect events', () => {
  for (const url of [
    'http://127.0.0.1:4173/', 'http://lucky7towingtransport.com/',
    'https://lucky7towingtransport.com.evil.example/', 'https://preview.example/',
    'https://lucky7towingtransport.com/privacy/', 'https://lucky7towingtransport.com/review/',
    'https://lucky7towingtransport.com/customer/private/'
  ]) assert.equal(fixture({ choice: 'granted', url }).scripts.length, 0, url);
  for (const route of ['/', '/index.html', '/towing-pulaski-wi/', '/towing-bonduel-wi/']) {
    assert.equal(fixture({ choice: 'granted', url: 'https://www.lucky7towingtransport.com' + route }).scripts.length, 1);
  }
});

test('preview hosts never attempt production cookie writes, while production privacy opt-out clears cookies', () => {
  for (const url of ['http://127.0.0.1:4173/', 'https://preview.example/', 'http://lucky7towingtransport.com/']) {
    const f = fixture({ url });
    f.choose('decline');
    assert.equal(f.cookies.length, 0, url);
  }
  const f = fixture({ choice: 'granted', url: 'https://lucky7towingtransport.com/privacy/' });
  f.choose('decline');
  assert.equal(f.scripts.length, 0);
  assert.ok(f.cookies.some(cookie => cookie.includes('domain=lucky7towingtransport.com')));
});

test('malformed referrers and missing preference markup are safe', () => {
  for (const referrer of ['', 'not-a-url', 'data:text/plain,private']) {
    const f = fixture({ choice: 'granted', noPanel: true, referrer });
    assert.equal(f.commands().find(c => c[0] === 'config')[2].page_referrer, '');
    assert.equal(f.phone().href, 'tel:7158538513');
  }
});

test('every marketing page includes one local analytics file and privacy controls', () => {
  for (const file of ['index.html', 'towing-shawano-wi/index.html', 'towing-pulaski-wi/index.html', 'towing-bonduel-wi/index.html']) {
    const html = fs.readFileSync(path.join(root, file), 'utf8');
    assert.equal((html.match(/src="\/analytics\.js"/g) || []).length, 1, file);
    assert.match(html, /data-analytics-panel[^>]*hidden/);
    assert.match(html, /data-analytics-settings hidden/);
    assert.match(html, /href="\/privacy\/"/);
    assert.doesNotMatch(html, /googletagmanager\.com|google-analytics\.com/);
  }
  assert.doesNotMatch(fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8'), /privacy/);
  assert.match(fs.readFileSync(path.join(root, 'privacy/index.html'), 'utf8'), /noindex, follow/);
});
