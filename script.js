// Lucky 7 Towing — progressive enhancement (menu, header state, scroll reveals)
// Smooth anchor scrolling is handled in CSS (scroll-behavior + scroll-padding-top).

document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', function () {
  var header = document.querySelector('.site-header');
  var nav = document.getElementById('site-nav');
  var menuBtn = document.querySelector('.menu-btn');

  // --- mobile menu (guarded: a page without this chrome must not kill the rest) ---
  if (nav && menuBtn) {
    var setMenu = function (open) {
      nav.classList.toggle('open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };

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
  }

  // --- header shadow once the page is scrolled ---
  if (header) {
    var onScroll = function () {
      header.classList.toggle('scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // --- scrollytelling: pinned scenes driven by scroll progress (--p in [0,1]) ---
  // Sections with [data-pin] pin their stage (position: sticky in CSS) while the
  // user scrolls through the section's extra height; --p scrubs the scene.
  var STICKY_TOP = 60; // matches .fleet-stage / .steps-stage `top` in styles.css
  var pinScenes = Array.prototype.slice.call(document.querySelectorAll('[data-pin]'))
    .map(function (pin) {
      return {
        pin: pin,
        stage: pin.firstElementChild,
        steps: Array.prototype.slice.call(pin.querySelectorAll('[data-step]')),
        dots: Array.prototype.slice.call(pin.querySelectorAll('.deck-dot'))
      };
    })
    .filter(function (s) { return !!s.stage; });
  var motionOK = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var STEP_THRESHOLDS = [0.04, 0.45, 0.86];

  function updatePins() {
    // phase 1: all layout reads, no writes (avoids per-pin layout thrash)
    pinScenes.forEach(function (s) {
      var range = s.pin.offsetHeight - s.stage.offsetHeight - STICKY_TOP;
      s.p = range > 0
        ? Math.min(Math.max(-s.pin.getBoundingClientRect().top / range, 0), 1)
        : null; // stage not pinned at this viewport (fallback layout)
    });
    // phase 2: all writes
    pinScenes.forEach(function (s) {
      if (s.p === null) return;
      s.pin.style.setProperty('--p', s.p.toFixed(4));
      s.steps.forEach(function (el) {
        var i = parseInt(el.getAttribute('data-step'), 10);
        el.classList.toggle('active', s.p >= STEP_THRESHOLDS[i]);
      });
      if (s.dots.length) {
        var idx = s.p < 0.24 ? 0 : s.p < 0.76 ? 1 : 2;
        s.dots.forEach(function (d, j) { d.classList.toggle('active', j === idx); });
      }
    });
  }

  if (pinScenes.length && motionOK) {
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

  // --- scroll reveals (reduced motion / no IO: show everything, keep going —
  //     the dispatch map and counters below must still initialize) ---
  var reveals = document.querySelectorAll('.reveal');

  if (!motionOK || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('in'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    reveals.forEach(function (el) { observer.observe(el); });
  }

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
      if (!NODES[from] || !NODES[to]) return null;
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
      // bounded reconstruction: a disconnected graph degrades to null, never a hang
      var path = [to], guard = 0;
      while (path[0] !== from) {
        if (prev[path[0]] === undefined || guard++ > 32) return null;
        path.unshift(prev[path[0]]);
      }
      return path;
    }

    var at = 'Bonduel';
    var driving = false;
    var pending = null;
    var idleTimer = null;
    var mapVisible = false;
    var announceNext = false; // only user-initiated dispatches speak to screen readers
    var announcerEl = panel.querySelector('.map-announcer');

    function setTruck(x, y) { truckEl.setAttribute('transform', 'translate(' + x + ' ' + y + ')'); }
    function say(msg) { statusEl.textContent = msg; }
    function announce(msg) { if (announcerEl) announcerEl.textContent = msg; }
    function pulse(name) {
      var g = panel.querySelector('.town[data-town="' + name + '"]');
      if (!g) return;
      g.classList.remove('stop-pulse');
      requestAnimationFrame(function () { g.classList.add('stop-pulse'); });
      setTimeout(function () { g.classList.remove('stop-pulse'); }, 900);
    }

    function drive(to) {
      if (!NODES[to]) return;
      if (driving) { pending = to; say('Rolling — next stop: ' + to); return; }
      if (to === at) { pulse(to); scheduleIdle(); return; }
      var nodes = route(at, to);
      if (!nodes || nodes.length < 2) { // data mistake: degrade to a teleport, never a hang
        at = to;
        setTruck(NODES[to][0], NODES[to][1]);
        pulse(to);
        say('Truck sent to ' + to + '.');
        scheduleIdle();
        return;
      }
      var segs = [], i;
      for (i = 0; i < nodes.length - 1; i++) {
        var a = NODES[nodes[i]], b = NODES[nodes[i + 1]];
        segs.push({ a: a, b: b, d: dist(a, b) });
      }
      var total = segs.reduce(function (s, x) { return s + x.d; }, 0);
      driving = true;
      say('Rolling: ' + at + ' → ' + to);
      if (announceNext) announce('Truck rolling to ' + to + '.');
      var t0 = null;
      function frame(ts) {
        if (t0 === null) t0 = ts;
        var gone = (ts - t0) / 1000 * SPEED;
        if (!mapVisible) gone = total; // scrolled away: finish the route instantly
        if (gone >= total) {
          var last = segs[segs.length - 1];
          setTruck(last.b[0], last.b[1]);
          at = to; driving = false;
          pulse(to);
          say(to === 'Bonduel' ? 'Back home at HQ — tap a town to roll again.'
                               : 'Made it to ' + to + ' — tap another town.');
          var next = pending; pending = null;
          if (announceNext && !next) { announce('Truck arrived in ' + to + '.'); announceNext = false; }
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
        if (driving) return;                       // arrival re-arms
        if (!mapVisible || document.hidden) return; // visibility handlers re-arm
        var next = PATROL[patrolIx % PATROL.length];
        patrolIx++;
        if (next === at) { scheduleIdle(); return; }
        announceNext = false; // patrol legs stay silent for screen readers
        drive(next);
      }, 2800);
    }
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden && mapVisible && motionOK) scheduleIdle();
    });

    function onTown(e) {
      var g = e.target.closest ? e.target.closest('.town') : null;
      if (!g) return false;
      var name = g.getAttribute('data-town');
      if (!name || !NODES[name]) return false;
      announceNext = true;
      if (!motionOK) {
        at = name; pending = null;
        setTruck(NODES[name][0], NODES[name][1]);
        pulse(name);
        say('Truck sent to ' + name + '.');
        announce('Truck sent to ' + name + '.');
        announceNext = false;
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

    // once the entrance choreography has played, freeze it so later class
    // changes (arrival pulses) can't restart entrance animations
    if ('IntersectionObserver' in window && motionOK) {
      var readyIO = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        readyIO.disconnect();
        setTimeout(function () { panel.classList.add('map-ready'); }, 3200);
      }, { threshold: 0.2 });
      readyIO.observe(panel);
    } else {
      panel.classList.add('map-ready');
    }
  })();

  // --- stat count-up (static values stay in the HTML for no-JS/reduced motion) ---
  var counters = document.querySelectorAll('.count[data-count]');
  if (counters.length && motionOK && 'IntersectionObserver' in window) {
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
