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

  // --- service-area dispatch map: the truck patrols, and towns are tappable ---
  (function () {
    var panel = document.querySelector('.map-panel');
    if (!panel) return;
    var truckEl = panel.querySelector('.map-truck');
    var flipEl = panel.querySelector('.truck-flip');
    var statusEl = panel.querySelector('.map-status');
    if (!truckEl || !flipEl || !statusEl) return;

    // Coordinates mirror the SVG; edges mirror the drawn roads (Hwy 29 + spokes).
    var NODES = {
      Wittenberg: [70, 137], Gresham: [342, 108], Keshena: [451, 80],
      Gillett: [685, 70], Cecil: [581, 155], Shawano: [468, 184],
      Bonduel: [585, 229], Pulaski: [730, 300], Navarino: [512, 350]
    };
    var EDGES = [
      ['Wittenberg', 'Shawano'], ['Shawano', 'Bonduel'], ['Bonduel', 'Pulaski'],
      ['Shawano', 'Gresham'], ['Shawano', 'Keshena'], ['Shawano', 'Cecil'],
      ['Cecil', 'Gillett'], ['Cecil', 'Bonduel'], ['Bonduel', 'Navarino']
    ];
    var SPEED = 110; // svg units per second

    function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }

    var adj = {};
    Object.keys(NODES).forEach(function (n) { adj[n] = []; });
    EDGES.forEach(function (e) {
      var d = dist(NODES[e[0]], NODES[e[1]]);
      adj[e[0]].push({ to: e[1], d: d });
      adj[e[1]].push({ to: e[0], d: d });
    });

    function route(from, to) { // Dijkstra over 9 nodes
      var best = {}, prev = {}, left = Object.keys(NODES);
      left.forEach(function (n) { best[n] = Infinity; });
      best[from] = 0;
      while (left.length) {
        left.sort(function (a, b) { return best[a] - best[b]; });
        var cur = left.shift();
        if (cur === to) break;
        adj[cur].forEach(function (e) {
          if (best[cur] + e.d < best[e.to]) { best[e.to] = best[cur] + e.d; prev[e.to] = cur; }
        });
      }
      var path = [to];
      while (path[0] !== from) path.unshift(prev[path[0]]);
      return path;
    }

    var at = 'Bonduel';
    var driving = false;
    var pending = null;
    var idleTimer = null;
    var mapVisible = false;

    function setTruck(x, y) { truckEl.setAttribute('transform', 'translate(' + x + ' ' + y + ')'); }
    function say(msg) { statusEl.textContent = msg; }
    function pulse(name) {
      var g = panel.querySelector('.town[data-town="' + name + '"]');
      if (!g) return;
      g.classList.remove('stop-pulse');
      requestAnimationFrame(function () { g.classList.add('stop-pulse'); });
      setTimeout(function () { g.classList.remove('stop-pulse'); }, 900);
    }

    function drive(to) {
      if (driving) { if (to !== at) { pending = to; say('Rolling — next stop: ' + to); } return; }
      if (to === at) { pulse(to); return; }
      var nodes = route(at, to);
      var segs = [], i;
      for (i = 0; i < nodes.length - 1; i++) {
        var a = NODES[nodes[i]], b = NODES[nodes[i + 1]];
        segs.push({ a: a, b: b, d: dist(a, b) });
      }
      var total = segs.reduce(function (s, x) { return s + x.d; }, 0);
      driving = true;
      say('Rolling: ' + at + ' → ' + to);
      var t0 = null;
      function frame(ts) {
        if (t0 === null) t0 = ts;
        var gone = (ts - t0) / 1000 * SPEED;
        if (gone >= total) {
          var last = segs[segs.length - 1];
          setTruck(last.b[0], last.b[1]);
          at = to; driving = false;
          pulse(to);
          say(to === 'Bonduel' ? 'Back home at HQ — tap a town to roll again.'
                               : 'Made it to ' + to + ' — tap another town.');
          var next = pending; pending = null;
          if (next) drive(next); else scheduleIdle();
          return;
        }
        var acc = 0, seg = segs[0], local = 0;
        for (var j = 0; j < segs.length; j++) {
          if (gone < acc + segs[j].d) { seg = segs[j]; local = (gone - acc) / segs[j].d; break; }
          acc += segs[j].d;
        }
        flipEl.setAttribute('transform', seg.b[0] < seg.a[0] ? 'scale(-1 1)' : 'scale(1 1)');
        setTruck(seg.a[0] + (seg.b[0] - seg.a[0]) * local,
                 seg.a[1] + (seg.b[1] - seg.a[1]) * local);
        requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    // gentle patrol loop while the map is on screen
    var PATROL = ['Shawano', 'Keshena', 'Gresham', 'Wittenberg', 'Shawano', 'Cecil',
                  'Gillett', 'Cecil', 'Bonduel', 'Navarino', 'Bonduel', 'Pulaski', 'Bonduel'];
    var patrolIx = 0;
    function scheduleIdle() {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(function () {
        if (!mapVisible || driving || document.hidden) { scheduleIdle(); return; }
        var next = PATROL[patrolIx % PATROL.length];
        patrolIx++;
        if (next === at) { scheduleIdle(); return; }
        drive(next);
      }, 2800);
    }

    function onTown(e) {
      var g = e.target.closest ? e.target.closest('.town') : null;
      if (!g) return false;
      var name = g.getAttribute('data-town');
      if (!motionOK) {
        at = name; pending = null;
        setTruck(NODES[name][0], NODES[name][1]);
        pulse(name);
        say('Truck sent to ' + name + '.');
      } else {
        drive(name);
      }
      return true;
    }
    panel.addEventListener('click', onTown);
    panel.addEventListener('keydown', function (e) {
      if ((e.key === 'Enter' || e.key === ' ') && onTown(e)) e.preventDefault();
    });

    if (motionOK && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        mapVisible = entries[0].isIntersecting;
        if (mapVisible) scheduleIdle(); else clearTimeout(idleTimer);
      }, { threshold: 0.35 }).observe(panel);
    }
  })();

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
