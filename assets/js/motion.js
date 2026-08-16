/* EcoHeat -- motion layer.
 *
 * Scroll reveals, a scroll progress rail, pointer-tracked glass highlights,
 * magnetic call-to-action buttons and count-up stats.
 *
 * Everything here is additive. The `js-motion` class is only set once this
 * file runs, and every hidden-then-revealed state is scoped to that class, so
 * with JavaScript off nothing is ever hidden and the page reads normally.
 * `prefers-reduced-motion` short-circuits the whole file except the header
 * state, which is a colour change rather than movement.
 */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var fine = window.matchMedia("(pointer: fine)");

  /* ---- sticky header: solid glass once the page has moved ---- */

  var header = document.querySelector(".header");
  var rail = document.querySelector(".progress__bar");

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var y = window.scrollY || window.pageYOffset;
      if (header) header.classList.toggle("is-stuck", y > 24);
      if (rail) {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        rail.style.transform = "scaleX(" + (max > 0 ? y / max : 0) + ")";
      }
      ticking = false;
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (reduce.matches) return;
  root.classList.add("js-motion");

  /* ---- scroll reveals ---- */

  var groups = [
    ".hero__inner > *",
    ".pagehead .wrap > *",
    ".section > .wrap > *",
    ".section > .wrap > .grid > *",
    ".section > .wrap > div > .grid > *",
    ".plans > *",
    ".trustbar li"
  ];

  var targets = [];
  groups.forEach(function (sel) {
    Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
      if (targets.indexOf(el) === -1) targets.push(el);
    });
  });

  targets.forEach(function (el) { el.classList.add("reveal"); });

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        // Stagger siblings so a row of cards arrives as a wave, not a block.
        var sibs = el.parentNode ? el.parentNode.children : [el];
        var i = Array.prototype.indexOf.call(sibs, el);
        el.style.transitionDelay = Math.min(i, 5) * 70 + "ms";
        el.classList.add("is-in");
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    targets.forEach(function (el) { io.observe(el); });
  } else {
    targets.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---- pointer-tracked highlight on glass surfaces ---- */

  if (fine.matches) {
    var lit = document.querySelectorAll(".card, .plan, .callout, .glass");
    Array.prototype.forEach.call(lit, function (el) {
      el.addEventListener("pointermove", function (ev) {
        var r = el.getBoundingClientRect();
        el.style.setProperty("--mx", ((ev.clientX - r.left) / r.width * 100) + "%");
        el.style.setProperty("--my", ((ev.clientY - r.top) / r.height * 100) + "%");
      }, { passive: true });
      el.addEventListener("pointerleave", function () {
        el.style.removeProperty("--mx");
        el.style.removeProperty("--my");
      }, { passive: true });
    });

    /* ---- magnetic buttons ---- */

    var mag = document.querySelectorAll(".btn--primary, .header__cta");
    Array.prototype.forEach.call(mag, function (el) {
      var raf = 0, tx = 0, ty = 0, cx = 0, cy = 0, active = false;

      function tick() {
        cx += (tx - cx) * 0.18;
        cy += (ty - cy) * 0.18;
        el.style.transform = "translate(" + cx.toFixed(2) + "px," + cy.toFixed(2) + "px)";
        if (active || Math.abs(cx) > 0.1 || Math.abs(cy) > 0.1) {
          raf = requestAnimationFrame(tick);
        } else {
          el.style.transform = "";
          raf = 0;
        }
      }

      el.addEventListener("pointermove", function (ev) {
        var r = el.getBoundingClientRect();
        // Pull is capped well below the button's own padding, so the hit area
        // never runs away from the cursor.
        tx = (ev.clientX - (r.left + r.width / 2)) * 0.22;
        ty = (ev.clientY - (r.top + r.height / 2)) * 0.30;
        active = true;
        if (!raf) raf = requestAnimationFrame(tick);
      }, { passive: true });

      el.addEventListener("pointerleave", function () {
        tx = ty = 0;
        active = false;
        if (!raf) raf = requestAnimationFrame(tick);
      }, { passive: true });
    });
  }

  /* ---- count-up stats ---- */

  var stats = document.querySelectorAll("[data-count]");
  if (stats.length && "IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        co.unobserve(el);
        var target = parseFloat(el.getAttribute("data-count"));
        var prefix = el.getAttribute("data-prefix") || "";
        var t0 = performance.now();
        (function step(now) {
          var k = Math.min((now - t0) / 1100, 1);
          var eased = 1 - Math.pow(1 - k, 3);
          el.textContent = prefix + Math.round(target * eased).toLocaleString("en-GB");
          if (k < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.5 });
    Array.prototype.forEach.call(stats, function (el) { co.observe(el); });
  }
})();
