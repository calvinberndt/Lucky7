// Optional call-click measurement. The phone links never depend on this file.
(function () {
  'use strict';

  // Public GA4 destination, not a credential. Verified in the web stream settings.
  var MEASUREMENT_ID = 'G-30ML7H1C2E';
  var CHOICE_KEY = 'lucky7_analytics_v1';
  var SITE_ORIGIN = 'https://lucky7towingtransport.com';
  var PAGES = {
    '/': 'Home',
    '/towing-shawano-wi/': 'Shawano',
    '/towing-pulaski-wi/': 'Pulaski',
    '/towing-bonduel-wi/': 'Bonduel'
  };
  var path = window.location.pathname.replace(/index\.html$/, '');
  var production = window.location.protocol === 'https:' &&
    /^(www\.)?lucky7towingtransport\.com$/.test(window.location.hostname);
  var configured = /^G-[A-Z0-9]+$/.test(MEASUREMENT_ID);
  var privacySignal = navigator.globalPrivacyControl === true ||
    /^(1|yes)$/.test(navigator.doNotTrack || window.doNotTrack || '');
  var active = false;
  var tagStarted = false;
  var tagFailed = false;
  var storageAvailable = true;
  var choice = null;
  var panel = document.querySelector('[data-analytics-panel]');
  var status = document.querySelector('[data-analytics-status]');
  var allow = document.querySelector('[data-analytics-allow]');
  var settings = document.querySelector('[data-analytics-settings]');

  function readChoice() {
    try {
      var stored = window.localStorage.getItem(CHOICE_KEY);
      return stored === 'granted' || stored === 'denied' ? stored : null;
    } catch (_) {
      storageAvailable = false;
      return null;
    }
  }

  function clearCookies() {
    // Preview hosts cannot own the production cookies; Firefox rejects those writes.
    if (!production || !configured) return;
    var names = ['_ga', '_ga_' + MEASUREMENT_ID.slice(2)];
    try {
      names.forEach(function (name) {
        ['', '; domain=' + window.location.hostname, '; domain=lucky7towingtransport.com']
          .forEach(function (domain) {
            document.cookie = name + '=; Max-Age=0; path=/' + domain + '; SameSite=Lax';
          });
      });
    } catch (_) {
      // The opt-out flag is already set; restricted cookie storage must not break calls.
      console.warn('Analytics is off; this browser did not allow cookie removal.');
    }
  }

  function stopMeasurement() {
    active = false;
    window['ga-disable-' + MEASUREMENT_ID] = true;
    clearCookies();
  }

  function gtag() {
    window.dataLayer.push(arguments);
  }

  function startMeasurement() {
    if (!production || !configured || !PAGES[path] || privacySignal || !storageAvailable) return;
    active = true;
    window['ga-disable-' + MEASUREMENT_ID] = false;
    if (tagStarted) return;
    tagStarted = true;
    tagFailed = false;
    window.dataLayer = window.dataLayer || [];
    // No advertising storage or advertising features are enabled.
    gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    gtag('js', new Date());
    gtag('config', MEASUREMENT_ID, {
      send_page_view: false,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_domain: 'lucky7towingtransport.com',
      cookie_expires: 2592000,
      cookie_update: false,
      page_location: SITE_ORIGIN + path,
      page_title: 'Lucky 7 Towing — ' + PAGES[path],
      page_referrer: safeReferrer()
    });
    gtag('event', 'page_view');
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    tag.onerror = function () {
      stopMeasurement();
      tagStarted = false;
      tagFailed = true;
      // This tag never loaded: discard its pending events rather than replaying a
      // stale visit/call queue if the visitor deliberately retries later.
      window.dataLayer.length = 0;
      tag.remove();
      renderChoice();
    };
    try {
      document.head.appendChild(tag);
    } catch (_) {
      // Optional measurement must not interrupt this page if script insertion is blocked.
      tag.onerror();
    }
  }

  function safeReferrer() {
    try {
      var referrer = new URL(document.referrer);
      return /^https?:$/.test(referrer.protocol) ? referrer.origin + '/' : '';
    } catch (_) {
      return '';
    }
  }

  function renderChoice() {
    if (!panel) return;
    panel.hidden = choice !== null && !(choice === 'granted' && tagFailed);
    if (allow) allow.disabled = privacySignal || !storageAvailable;
    if (settings) settings.hidden = false;
    if (!status) return;
    status.textContent = privacySignal ? 'Analytics is off because your browser requests privacy.' :
      !storageAvailable ? 'Analytics is off because this browser cannot save your choice.' :
      choice === 'granted' && tagFailed ? 'Analytics could not load. Calling and browsing still work. Choose Allow analytics to retry, or keep it off.' :
      choice === 'granted' ? 'Optional analytics allowed. You can turn it off below.' :
      'Optional analytics is off. Calling works either way.';
  }

  function saveChoice(nextChoice) {
    try {
      window.localStorage.setItem(CHOICE_KEY, nextChoice);
      choice = nextChoice;
    } catch (_) {
      storageAvailable = false;
      choice = null;
    }
    if (choice === 'granted') startMeasurement();
    else stopMeasurement();
    renderChoice();
  }

  function placement(link) {
    if (link.classList.contains('floating-call-btn')) return 'floating';
    if (link.classList.contains('topbar-phone')) return 'topbar';
    if (link.closest('.site-nav')) return 'navigation';
    if (link.closest('.site-header')) return 'header';
    if (link.closest('.hero-cta')) return 'hero';
    if (link.closest('.cta-band')) return 'contact';
    if (link.closest('#faq')) return 'faq';
    return 'content';
  }

  choice = readChoice();
  if (choice === 'granted' && !privacySignal) startMeasurement();
  else stopMeasurement();
  renderChoice();

  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || !target.closest) return;
    if (target.closest('[data-analytics-allow]')) saveChoice('granted');
    else if (target.closest('[data-analytics-decline]')) saveChoice('denied');
    else if (target.closest('[data-analytics-settings]') && panel) {
      panel.hidden = false;
      panel.scrollIntoView({ block: 'center' });
      panel.focus({ preventScroll: true });
    }
    var link = target.closest('a[href="tel:7158538513"]');
    if (active && link && !event.defaultPrevented) {
      gtag('event', 'phone_click', { page_name: PAGES[path], link_placement: placement(link) });
    }
  });

  // A preference change in another tab takes effect here too.
  window.addEventListener('storage', function (event) {
    if (event.key !== CHOICE_KEY && event.key !== null) return;
    choice = readChoice();
    if (choice === 'granted') startMeasurement();
    else stopMeasurement();
    renderChoice();
  });
})();
