#!/usr/bin/env bash
# Runtime regression checks. Start the static server first; requires agent-browser.
set -euo pipefail
command -v agent-browser >/dev/null || { echo 'Install agent-browser to run browser checks.' >&2; exit 1; }
base_url="${1:-http://127.0.0.1:4173}"
session="lucky7-smoke-$$"
trap 'agent-browser --session "$session" close >/dev/null 2>&1 || true' EXIT

for width in 320 375 900 1440; do
  for route in / /towing-shawano-wi/ /towing-bonduel-wi/ /towing-pulaski-wi/; do
    agent-browser --session "$session" open "${base_url%/}${route}" >/dev/null
    agent-browser --session "$session" set viewport "$width" 812 >/dev/null
    agent-browser --session "$session" wait --load networkidle >/dev/null
    agent-browser --session "$session" eval "$(cat <<'JS'
(async () => {
  await document.fonts.ready;
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const visible = el => {
    const r = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && r.top >= 0 && r.bottom <= innerHeight &&
      r.left >= 0 && r.right <= innerWidth && style.visibility !== 'hidden' && style.opacity !== '0';
  };
  const calls = [...document.querySelectorAll('a[href^="tel:"]')];
  assert(calls.length > 0 && calls.every(a => a.getAttribute('href').replace(/\D/g, '').endsWith('7158538513')), 'Incorrect call link');
  const hero = document.querySelector('.hero, .page-hero');
  assert(hero && !hero.querySelector('.reveal'), 'Primary content must not wait for reveal animation');
  for (const position of [0, document.body.scrollHeight / 2, document.body.scrollHeight]) {
    window.scrollTo({top: position, behavior: 'instant'});
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    assert(document.documentElement.scrollWidth <= innerWidth, 'Page overflows horizontally');
    assert(calls.some(visible), 'No visible call action at scroll position ' + scrollY);
  }
  for (const plate of document.querySelectorAll('.phone-plate')) {
    const r = plate.getBoundingClientRect();
    assert(r.left >= 0 && r.right <= innerWidth, 'Call plate extends beyond viewport');
    assert(plate.scrollWidth <= plate.clientWidth, 'Call plate text is clipped');
  }
  window.scrollTo({top: 0, behavior: 'instant'});
  const menu = document.querySelector('.menu-btn');
  if (visible(menu)) {
    menu.click();
    assert(menu.getAttribute('aria-expanded') === 'true', 'Menu did not open');
    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
    assert(menu.getAttribute('aria-expanded') === 'false', 'Escape did not close menu');
  }
  const faq = document.querySelector('details');
  faq.querySelector('summary').click();
  assert(faq.open, 'FAQ did not open');
  faq.querySelector('summary').click();
  assert(!faq.open, 'FAQ did not close');
  assert([...document.images].filter(img => img.complete).every(img => img.naturalWidth > 0), 'Broken image');
  assert([...document.fonts].filter(font => font.status === 'error').length === 0, 'Font failed to load');
  return {path: location.pathname, width: innerWidth, result: 'PASS'};
})()
JS
)"
    errors="$(agent-browser --session "$session" errors)"
    if [[ -n "$errors" ]]; then
      echo "$errors" >&2
      exit 1
    fi
  done
done
