// Lucky 7 Towing — progressive enhancement (menu, header state, scroll reveals)
// Smooth anchor scrolling is handled in CSS (scroll-behavior + scroll-padding-top).

document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', function () {
  var header = document.querySelector('.site-header');
  var nav = document.getElementById('site-nav');
  var menuBtn = document.querySelector('.menu-btn');

  // --- mobile menu ---
  function setMenu(open) {
    nav.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }

  menuBtn.addEventListener('click', function () {
    setMenu(!nav.classList.contains('open'));
  });

  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) setMenu(false);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav.classList.contains('open')) {
      setMenu(false);
      menuBtn.focus();
    }
  });

  document.addEventListener('click', function (e) {
    if (nav.classList.contains('open') &&
        !nav.contains(e.target) && !menuBtn.contains(e.target)) {
      setMenu(false);
    }
  });

  // --- header shadow once the page is scrolled ---
  function onScroll() {
    header.classList.toggle('scrolled', window.scrollY > 8);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // --- scrollytelling: pinned scenes driven by scroll progress (--p in [0,1]) ---
  // Sections with [data-pin] pin their stage (position: sticky in CSS) while the
  // user scrolls through the section's extra height; --p scrubs the scene.
  var pins = Array.prototype.slice.call(document.querySelectorAll('[data-pin]'));
  var motionOK = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var STEP_THRESHOLDS = [0.04, 0.45, 0.86];

  function updatePins() {
    pins.forEach(function (pin) {
      var stage = pin.firstElementChild;
      if (!stage) return;
      var range = pin.offsetHeight - stage.offsetHeight;
      if (range <= 0) return; // stage not pinned at this viewport (fallback layout)
      var p = Math.min(Math.max(-pin.getBoundingClientRect().top / range, 0), 1);
      pin.style.setProperty('--p', p.toFixed(4));

      var steps = pin.querySelectorAll('[data-step]');
      steps.forEach(function (s) {
        var i = parseInt(s.getAttribute('data-step'), 10);
        s.classList.toggle('active', p >= STEP_THRESHOLDS[i]);
      });

      var dots = pin.querySelectorAll('.deck-dot');
      if (dots.length) {
        var idx = p < 0.24 ? 0 : p < 0.76 ? 1 : 2;
        dots.forEach(function (d, j) { d.classList.toggle('active', j === idx); });
      }
    });
  }

  if (pins.length && motionOK) {
    var pinTick = false;
    function requestPinUpdate() {
      if (pinTick) return;
      pinTick = true;
      requestAnimationFrame(function () { updatePins(); pinTick = false; });
    }
    window.addEventListener('scroll', requestPinUpdate, { passive: true });
    window.addEventListener('resize', requestPinUpdate, { passive: true });
    updatePins();
  }

  // --- scroll reveals (skipped for reduced motion; CSS keeps content visible) ---
  var reveals = document.querySelectorAll('.reveal');
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReduced || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('in'); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

  reveals.forEach(function (el) { observer.observe(el); });

  // --- stat count-up (static values stay in the HTML for no-JS/reduced motion) ---
  var counters = document.querySelectorAll('.count[data-count]');
  if (counters.length) {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        countObserver.unobserve(entry.target);
        var el = entry.target;
        var target = parseFloat(el.getAttribute('data-count'));
        var decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
        var start = null;
        var DURATION = 950;
        function tick(ts) {
          if (start === null) start = ts;
          var t = Math.min((ts - start) / DURATION, 1);
          var eased = 1 - Math.pow(1 - t, 3);
          el.textContent = (target * eased).toFixed(decimals);
          if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { countObserver.observe(el); });
  }
});
