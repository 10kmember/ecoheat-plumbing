/* EcoHeat -- "the yard": a small rigid-body playground.
 *
 * A self-contained 2D physics engine (no library): semi-implicit Euler
 * integration under gravity, contact generation for circle/circle,
 * circle/box and box/world pairs, and sequential impulse resolution with
 * restitution, Coulomb friction and Baumgarte position correction. Impulses
 * scale with mass, so a full cylinder shoves the van and the van shoves a
 * radiator further than it shoves the cylinder.
 *
 * Drive with the arrow keys or A/D, boost with Shift, click to blast. Every
 * contact above a threshold feeds window.EcoAudio, panned by where on the
 * canvas it happened.
 *
 * Opt-in: nothing runs until the visitor presses Start, and reduced-motion
 * users get a still frame with the simulation never stepped.
 */
(function () {
  "use strict";

  var canvas = document.getElementById("yard");
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");

  var section = canvas.closest(".yard");
  var startBtn = section.querySelector("[data-yard-start]");
  var resetBtn = section.querySelector("[data-yard-reset]");
  var soundBtn = section.querySelector("[data-yard-sound]");
  var live = section.querySelector("[data-yard-live]");

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  // The section ships hidden so that a visitor without JavaScript never meets
  // an empty canvas and an inert Start button. Unhide before measuring, or the
  // canvas reports a client width of zero.
  section.removeAttribute("hidden");

  /* ================= engine ================= */

  var GRAVITY = 1500;      // px/s^2
  var ITERATIONS = 8;
  var SLOP = 0.5;
  var CORRECTION = 0.4;

  function Body(o) {
    this.x = o.x; this.y = o.y;
    this.vx = 0; this.vy = 0;
    this.a = o.a || 0; this.av = 0;
    this.shape = o.shape;              // "circle" | "box"
    this.r = o.r || 0;
    this.hw = o.hw || 0; this.hh = o.hh || 0;
    this.e = o.e === undefined ? 0.28 : o.e;   // restitution
    this.mu = o.mu === undefined ? 0.55 : o.mu; // friction
    this.label = o.label || "";
    this.fill = o.fill || "#2c3238";
    this.isVan = !!o.isVan;
    this.stat = !!o.stat;

    if (this.stat) {
      this.invM = 0; this.invI = 0; this.m = Infinity;
    } else {
      var m = o.m || (this.shape === "circle"
        ? Math.PI * this.r * this.r * 0.004
        : this.hw * this.hh * 0.016);
      this.m = m;
      this.invM = 1 / m;
      var I = this.shape === "circle"
        ? 0.5 * m * this.r * this.r
        : m * (this.hw * this.hw + this.hh * this.hh) * 4 / 3;
      this.invI = 1 / I;
    }
  }

  var bodies = [], contacts = [];
  var W = 0, H = 0, dpr = 1;

  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  /* ---- contact generation ---- */

  function circleCircle(A, B) {
    var dx = B.x - A.x, dy = B.y - A.y;
    var d2 = dx * dx + dy * dy;
    var rr = A.r + B.r;
    if (d2 >= rr * rr || d2 < 1e-9) return;
    var d = Math.sqrt(d2);
    var nx = dx / d, ny = dy / d;
    contacts.push({
      A: A, B: B, nx: nx, ny: ny, depth: rr - d,
      px: A.x + nx * A.r, py: A.y + ny * A.r
    });
  }

  function circleBox(C, B) {
    // Work in the box's local frame, clamp to its extent, transform back.
    var cos = Math.cos(-B.a), sin = Math.sin(-B.a);
    var dx = C.x - B.x, dy = C.y - B.y;
    var lx = dx * cos - dy * sin, ly = dx * sin + dy * cos;

    var qx = clamp(lx, -B.hw, B.hw), qy = clamp(ly, -B.hh, B.hh);
    var inside = (qx === lx && qy === ly);

    if (inside) {
      // Push out along the shallowest face.
      var dl = B.hw - Math.abs(lx), dt = B.hh - Math.abs(ly);
      if (dl < dt) qx = lx > 0 ? B.hw : -B.hw; else qy = ly > 0 ? B.hh : -B.hh;
    }

    var ox = lx - qx, oy = ly - qy;
    var d2 = ox * ox + oy * oy;
    if (!inside && d2 >= C.r * C.r) return;

    var d = Math.sqrt(d2) || 1e-6;
    var nlx = ox / d, nly = oy / d;
    if (inside) { nlx = -nlx; nly = -nly; }

    var c2 = Math.cos(B.a), s2 = Math.sin(B.a);
    var nx = nlx * c2 - nly * s2, ny = nlx * s2 + nly * c2;
    var wx = B.x + (qx * c2 - qy * s2), wy = B.y + (qx * s2 + qy * c2);

    contacts.push({
      A: B, B: C,
      nx: nx, ny: ny,
      depth: inside ? C.r + d : C.r - d,
      px: wx, py: wy
    });
  }

  function boxVerts(b) {
    var c = Math.cos(b.a), s = Math.sin(b.a), out = [];
    var sx = [-b.hw, b.hw, b.hw, -b.hw], sy = [-b.hh, -b.hh, b.hh, b.hh];
    for (var i = 0; i < 4; i++) {
      out.push({ x: b.x + sx[i] * c - sy[i] * s,
                 y: b.y + sx[i] * s + sy[i] * c });
    }
    return out;
  }

  function project(vs, ax, ay) {
    var min = Infinity, max = -Infinity;
    for (var i = 0; i < vs.length; i++) {
      var d = vs[i].x * ax + vs[i].y * ay;
      if (d < min) min = d;
      if (d > max) max = d;
    }
    return [min, max];
  }

  function insideBox(x, y, b) {
    var c = Math.cos(-b.a), s = Math.sin(-b.a);
    var dx = x - b.x, dy = y - b.y;
    var lx = dx * c - dy * s, ly = dx * s + dy * c;
    return Math.abs(lx) <= b.hw && Math.abs(ly) <= b.hh;
  }

  // Separating Axis Test over the four face normals of two oriented boxes.
  // Contact points are taken as the vertices of each box lying inside the
  // other, which is enough for stable resting stacks at eight iterations.
  function boxBox(A, B) {
    var va = boxVerts(A), vb = boxVerts(B);
    var ca = Math.cos(A.a), sa = Math.sin(A.a);
    var cb = Math.cos(B.a), sb = Math.sin(B.a);
    var axes = [[ca, sa], [-sa, ca], [cb, sb], [-sb, cb]];

    var best = Infinity, nx = 0, ny = 0;
    for (var i = 0; i < 4; i++) {
      var ax = axes[i][0], ay = axes[i][1];
      var pa = project(va, ax, ay), pb = project(vb, ax, ay);
      var overlap = Math.min(pa[1], pb[1]) - Math.max(pa[0], pb[0]);
      if (overlap <= 0) return;          // a gap on any axis means no contact
      if (overlap < best) { best = overlap; nx = ax; ny = ay; }
    }

    if ((B.x - A.x) * nx + (B.y - A.y) * ny < 0) { nx = -nx; ny = -ny; }

    var pts = [], k;
    for (k = 0; k < 4; k++) if (insideBox(vb[k].x, vb[k].y, A)) pts.push(vb[k]);
    for (k = 0; k < 4; k++) if (insideBox(va[k].x, va[k].y, B)) pts.push(va[k]);

    if (!pts.length) {
      // Edge-on-edge: fall back to B's vertex deepest along the normal.
      var deepest = vb[0], dv = Infinity;
      for (k = 0; k < 4; k++) {
        var d = vb[k].x * nx + vb[k].y * ny;
        if (d < dv) { dv = d; deepest = vb[k]; }
      }
      pts.push(deepest);
    }

    for (k = 0; k < pts.length && k < 2; k++) {
      contacts.push({ A: A, B: B, nx: nx, ny: ny, depth: best,
                      px: pts[k].x, py: pts[k].y });
    }
  }

  // Dynamic body against the static world box (floor and side walls).
  function worldBounds(b, minX, maxX, floorY) {
    var pts;
    if (b.shape === "circle") {
      pts = [{ x: b.x, y: b.y, r: b.r }];
    } else {
      var c = Math.cos(b.a), s = Math.sin(b.a), out = [];
      for (var i = 0; i < 4; i++) {
        var sx = (i === 0 || i === 3) ? -b.hw : b.hw;
        var sy = i < 2 ? -b.hh : b.hh;
        out.push({ x: b.x + sx * c - sy * s, y: b.y + sx * s + sy * c, r: 0 });
      }
      pts = out;
    }
    for (var k = 0; k < pts.length; k++) {
      var p = pts[k];
      if (p.y + p.r > floorY) {
        contacts.push({ A: null, B: b, nx: 0, ny: -1,
          depth: p.y + p.r - floorY, px: p.x, py: floorY });
      }
      if (p.x - p.r < minX) {
        contacts.push({ A: null, B: b, nx: 1, ny: 0,
          depth: minX - (p.x - p.r), px: minX, py: p.y });
      }
      if (p.x + p.r > maxX) {
        contacts.push({ A: null, B: b, nx: -1, ny: 0,
          depth: (p.x + p.r) - maxX, px: maxX, py: p.y });
      }
    }
  }

  /* ---- solver ---- */

  var onImpact = null;

  function solve(dt) {
    for (var it = 0; it < ITERATIONS; it++) {
      for (var i = 0; i < contacts.length; i++) {
        var c = contacts[i];
        var A = c.A, B = c.B;
        var invMA = A ? A.invM : 0, invIA = A ? A.invI : 0;
        var invMB = B.invM, invIB = B.invI;
        var invSum = invMA + invMB;
        if (invSum === 0) continue;

        // Contact-relative arms, for the angular part of the impulse.
        var rax = A ? c.px - A.x : 0, ray = A ? c.py - A.y : 0;
        var rbx = c.px - B.x, rby = c.py - B.y;

        var vax = A ? A.vx - A.av * ray : 0, vay = A ? A.vy + A.av * rax : 0;
        var vbx = B.vx - B.av * rby, vby = B.vy + B.av * rbx;

        var rvx = vbx - vax, rvy = vby - vay;
        var vn = rvx * c.nx + rvy * c.ny;
        if (vn > 0) continue;   // already separating

        var raCrossN = A ? rax * c.ny - ray * c.nx : 0;
        var rbCrossN = rbx * c.ny - rby * c.nx;
        var denom = invSum + raCrossN * raCrossN * invIA + rbCrossN * rbCrossN * invIB;
        if (denom <= 0) continue;

        var e = Math.min(A ? A.e : 0.2, B.e);
        // Kill restitution on slow contacts, or a stack jitters forever.
        if (vn > -60) e = 0;

        var jn = -(1 + e) * vn / denom;
        if (it === 0 && onImpact && jn > 0) onImpact(c, jn);

        var ix = c.nx * jn, iy = c.ny * jn;
        if (A) {
          A.vx -= ix * invMA; A.vy -= iy * invMA;
          A.av -= (rax * iy - ray * ix) * invIA;
        }
        B.vx += ix * invMB; B.vy += iy * invMB;
        B.av += (rbx * iy - rby * ix) * invIB;

        // Coulomb friction along the contact tangent.
        var tx = -c.ny, ty = c.nx;
        var vt = rvx * tx + rvy * ty;
        var raCrossT = A ? rax * ty - ray * tx : 0;
        var rbCrossT = rbx * ty - rby * tx;
        var denomT = invSum + raCrossT * raCrossT * invIA + rbCrossT * rbCrossT * invIB;
        if (denomT <= 0) continue;

        var jt = -vt / denomT;
        var mu = Math.sqrt((A ? A.mu : 0.6) * B.mu);
        jt = clamp(jt, -jn * mu, jn * mu);

        var fx = tx * jt, fy = ty * jt;
        if (A) {
          A.vx -= fx * invMA; A.vy -= fy * invMA;
          A.av -= (rax * fy - ray * fx) * invIA;
        }
        B.vx += fx * invMB; B.vy += fy * invMB;
        B.av += (rbx * fy - rby * fx) * invIB;
      }
    }

    // Baumgarte-style positional correction, so deep overlaps do not persist.
    for (var n = 0; n < contacts.length; n++) {
      var k = contacts[n];
      var iMA = k.A ? k.A.invM : 0, iMB = k.B.invM;
      var sum = iMA + iMB;
      if (sum === 0) continue;
      var mag = Math.max(k.depth - SLOP, 0) / sum * CORRECTION;
      if (k.A) { k.A.x -= k.nx * mag * iMA; k.A.y -= k.ny * mag * iMA; }
      k.B.x += k.nx * mag * iMB; k.B.y += k.ny * mag * iMB;
    }
  }

  /* ================= the scene ================= */

  var van = null, floorY = 0, minX = 0, maxX = 0;
  var keys = Object.create(null);
  var started = false, running = false, visible = true;

  var STOCK = [
    { label: "CYLINDER", shape: "circle", fill: "#3a4148" },
    { label: "HEAT PUMP", shape: "box", fill: "#39424a" },
    { label: "RADIATOR", shape: "box", fill: "#333a41" },
    { label: "BOILER", shape: "box", fill: "#3d454d" },
    { label: "COIL", shape: "circle", fill: "#39424a" },
    { label: "TANK", shape: "circle", fill: "#343c43" }
  ];

  function layout() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = Math.round(canvas.clientWidth * dpr);
    H = Math.round(canvas.clientHeight * dpr);
    canvas.width = W; canvas.height = H;
    floorY = H - 26 * dpr;
    minX = 8 * dpr; maxX = W - 8 * dpr;
  }

  function build() {
    layout();
    bodies = [];
    var s = dpr * Math.min(1.25, Math.max(0.62, W / (dpr * 900)));

    van = new Body({
      x: W * 0.18, y: floorY - 46 * s, shape: "box",
      hw: 58 * s, hh: 27 * s, m: 26, e: 0.16, mu: 0.85, isVan: true
    });
    bodies.push(van);

    // A stack of stock to shove about, seeded deterministically so the scene
    // is the same every time it is reset.
    var cols = W / dpr > 700 ? 5 : 3;
    for (var i = 0; i < cols * 3; i++) {
      var def = STOCK[i % STOCK.length];
      var col = i % cols, row = Math.floor(i / cols);
      var bx = W * 0.55 + col * 62 * s + (row % 2) * 18 * s;
      var by = floorY - 34 * s - row * 62 * s;
      if (def.shape === "circle") {
        bodies.push(new Body({
          x: bx, y: by, shape: "circle", r: 25 * s,
          e: 0.34, mu: 0.5, label: def.label, fill: def.fill
        }));
      } else {
        bodies.push(new Body({
          x: bx, y: by, shape: "box", hw: 27 * s, hh: 22 * s,
          e: 0.22, mu: 0.6, label: def.label, fill: def.fill
        }));
      }
    }
  }

  /* ---- step ---- */

  function step(dt) {
    var i, b;
    for (i = 0; i < bodies.length; i++) {
      b = bodies[i];
      if (b.stat) continue;
      b.vy += GRAVITY * dt;
      // Light global damping keeps the pile from fizzing indefinitely.
      b.vx *= 0.999; b.av *= 0.995;
    }

    // Drive: torque-free horizontal force, plus a nose-up pitch under boost.
    var dir = (keys.right ? 1 : 0) - (keys.left ? 1 : 0);
    if (dir !== 0) {
      var boost = keys.boost ? 2.1 : 1;
      van.vx += dir * 1150 * boost * dt;
      van.av += dir * 0.9 * dt * (keys.boost ? 2.4 : 1);
    }
    if (keys.up && Math.abs(van.y - (floorY - van.hh)) < 26 * dpr) {
      van.vy -= 520;
      keys.up = false;
      if (window.EcoAudio) window.EcoAudio.boost();
    }
    van.vx = clamp(van.vx, -900 * dpr, 900 * dpr);
    // Keep the van broadly upright; it is a van, not a stunt car.
    van.av -= van.a * 6.5 * dt;
    van.av *= 0.93;

    for (i = 0; i < bodies.length; i++) {
      b = bodies[i];
      if (b.stat) continue;
      b.x += b.vx * dt; b.y += b.vy * dt; b.a += b.av * dt;
    }

    contacts.length = 0;
    for (i = 0; i < bodies.length; i++) {
      for (var j = i + 1; j < bodies.length; j++) {
        var A = bodies[i], B = bodies[j];
        if (A.shape === "circle" && B.shape === "circle") circleCircle(A, B);
        else if (A.shape === "circle" && B.shape === "box") circleBox(A, B);
        else if (A.shape === "box" && B.shape === "circle") circleBox(B, A);
        else boxBox(A, B);
      }
      worldBounds(bodies[i], minX, maxX, floorY);
    }

    solve(dt);
  }

  var impactBudget = 0;
  onImpact = function (c, jn) {
    if (!window.EcoAudio || !window.EcoAudio.on) return;
    if (jn < 90) return;
    if (impactBudget++ > 3) return;
    window.EcoAudio.hit(Math.min(1, jn / 2600), (c.px / W) * 2 - 1);
  };

  /* ---- render ---- */

  function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function render() {
    ctx.clearRect(0, 0, W, H);

    // Ground line and hatching.
    ctx.strokeStyle = "rgba(143,220,60,.55)";
    ctx.lineWidth = 2 * dpr;
    ctx.beginPath();
    ctx.moveTo(0, floorY); ctx.lineTo(W, floorY); ctx.stroke();
    ctx.strokeStyle = "rgba(143,220,60,.16)";
    ctx.lineWidth = 1 * dpr;
    for (var gx = 0; gx < W + H; gx += 16 * dpr) {
      ctx.beginPath();
      ctx.moveTo(gx, floorY);
      ctx.lineTo(gx - 22 * dpr, floorY + 26 * dpr);
      ctx.stroke();
    }

    for (var i = 0; i < bodies.length; i++) {
      var b = bodies[i];
      ctx.save();
      ctx.translate(b.x, b.y);
      ctx.rotate(b.a);

      if (b.isVan) {
        ctx.fillStyle = "#8fdc3c";
        roundRect(-b.hw, -b.hh, b.hw * 2, b.hh * 2, 7 * dpr);
        ctx.fill();
        ctx.fillStyle = "#14171a";
        // Cab window and a suggestion of livery.
        roundRect(b.hw * 0.18, -b.hh * 0.62, b.hw * 0.62, b.hh * 0.78, 4 * dpr);
        ctx.fill();
        ctx.fillStyle = "rgba(20,23,26,.75)";
        ctx.fillRect(-b.hw * 0.82, -b.hh * 0.12, b.hw * 0.85, 3 * dpr);
        ctx.fillStyle = "#14171a";
        ctx.beginPath();
        ctx.arc(-b.hw * 0.52, b.hh, b.hh * 0.46, 0, 6.284);
        ctx.arc(b.hw * 0.55, b.hh, b.hh * 0.46, 0, 6.284);
        ctx.fill();
      } else if (b.shape === "circle") {
        ctx.fillStyle = b.fill;
        ctx.beginPath(); ctx.arc(0, 0, b.r, 0, 6.284); ctx.fill();
        ctx.strokeStyle = "rgba(143,220,60,.5)";
        ctx.lineWidth = 1.5 * dpr;
        ctx.stroke();
        ctx.strokeStyle = "rgba(143,220,60,.35)";
        ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(b.r, 0); ctx.stroke();
      } else {
        ctx.fillStyle = b.fill;
        roundRect(-b.hw, -b.hh, b.hw * 2, b.hh * 2, 4 * dpr);
        ctx.fill();
        ctx.strokeStyle = "rgba(143,220,60,.45)";
        ctx.lineWidth = 1.5 * dpr;
        ctx.stroke();
      }

      if (b.label && !b.isVan) {
        ctx.rotate(-b.a);
        ctx.fillStyle = "rgba(244,246,241,.72)";
        ctx.font = (9 * dpr) + "px Nunito, system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(b.label, 0, 0);
      }
      ctx.restore();
    }
  }

  /* ---- blast ---- */

  function blast(cx, cy) {
    var reachedAny = false;
    for (var i = 0; i < bodies.length; i++) {
      var b = bodies[i];
      if (b.stat) continue;
      var dx = b.x - cx, dy = b.y - cy;
      var d = Math.hypot(dx, dy) || 1;
      var reach = 210 * dpr;
      if (d > reach) continue;
      reachedAny = true;
      // Impulse divided by mass: heavier stock barely shifts, which is the
      // point of giving everything a mass in the first place.
      var f = (1 - d / reach) * 5200 * dpr * b.invM;
      b.vx += (dx / d) * f;
      b.vy += (dy / d) * f - 90;
      b.av += (dx / d) * 0.9;
    }
    if (reachedAny && window.EcoAudio) window.EcoAudio.boost();
  }

  /* ---- loop ---- */

  var last = 0, acc = 0;
  var FIXED = 1 / 120;

  function frame(now) {
    if (!running) return;
    var dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    acc += dt;
    impactBudget = 0;
    // Fixed timestep: a variable one makes restitution and stacking unstable.
    var guard = 0;
    while (acc >= FIXED && guard++ < 8) { step(FIXED); acc -= FIXED; }
    render();
    requestAnimationFrame(frame);
  }

  function play() {
    if (running || !started || !visible) return;
    running = true; last = performance.now(); acc = 0;
    requestAnimationFrame(frame);
  }
  function pause() { running = false; }

  /* ---- controls ---- */

  var KEYMAP = {
    ArrowLeft: "left", a: "left", A: "left",
    ArrowRight: "right", d: "right", D: "right",
    ArrowUp: "up", w: "up", W: "up",
    Shift: "boost"
  };

  function onKey(down) {
    return function (ev) {
      var k = KEYMAP[ev.key];
      if (!k || !started) return;
      // Only capture the arrows while the canvas itself has focus, so the
      // page can still be scrolled with the keyboard.
      if (document.activeElement !== canvas && ev.key.indexOf("Arrow") === 0) return;
      keys[k] = down;
      if (ev.key.indexOf("Arrow") === 0 && document.activeElement === canvas) {
        ev.preventDefault();
      }
    };
  }
  window.addEventListener("keydown", onKey(true));
  window.addEventListener("keyup", onKey(false));

  canvas.addEventListener("pointerdown", function (ev) {
    if (!started) { start(); return; }
    canvas.focus();
    var r = canvas.getBoundingClientRect();
    blast((ev.clientX - r.left) * dpr, (ev.clientY - r.top) * dpr);
  });

  function start() {
    if (started) return;
    started = true;
    section.classList.add("is-playing");
    if (startBtn) startBtn.setAttribute("hidden", "");
    if (live) live.textContent =
      "Yard simulation running. Use the left and right arrow keys to drive, " +
      "up arrow to hop, and Escape to stop.";
    canvas.setAttribute("tabindex", "0");
    canvas.focus();
    play();
  }

  window.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && started) {
      pause(); started = false;
      section.classList.remove("is-playing");
      if (startBtn) startBtn.removeAttribute("hidden");
      if (live) live.textContent = "Yard simulation stopped.";
    }
  });

  if (startBtn) startBtn.addEventListener("click", start);
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      build(); render();
      if (live) live.textContent = "Yard reset.";
    });
  }
  if (soundBtn) {
    soundBtn.addEventListener("click", function () {
      var on = window.EcoAudio && window.EcoAudio.toggle();
      soundBtn.setAttribute("aria-pressed", on ? "true" : "false");
      soundBtn.querySelector("[data-label]").textContent =
        on ? "Sound on" : "Sound off";
    });
  }

  window.addEventListener("resize", function () {
    build();
    render();
  }, { passive: true });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) {
      visible = e[0].isIntersecting;
      if (visible) play(); else pause();
    }, { threshold: 0 }).observe(canvas);
  }
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) pause(); else play();
  });

  build();
  // Settle the stack so the still frame shows a resting pile, not a mid-drop
  // one, whether or not the visitor ever presses Start.
  for (var w = 0; w < 240; w++) step(FIXED);
  render();

  if (reduce.matches && startBtn) {
    startBtn.setAttribute("hidden", "");
    if (live) {
      live.textContent =
        "Interactive yard simulation disabled because your system asks for " +
        "reduced motion. The illustration shows the yard at rest.";
    }
  }
})();
