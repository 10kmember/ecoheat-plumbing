/* EcoHeat -- hero particle network.
 *
 * An organic drifting network: nodes advected by a slow flow field, linked to
 * their neighbours by lines that fade with distance, and pushed around by the
 * pointer. Rendered in WebGL2 as two draw calls (lines, then soft points) over
 * the CSS gradient, so the canvas keeps an alpha channel and the hero degrades
 * to that gradient wherever WebGL is unavailable.
 */
(function () {
  "use strict";

  var canvas = document.getElementById("hero-gl");
  if (!canvas) return;

  var gl = canvas.getContext("webgl2", {
    alpha: true, antialias: true, depth: false, stencil: false,
    premultipliedAlpha: false, powerPreference: "low-power"
  });
  if (!gl) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  var VERT = [
    "#version 300 es",
    "in vec2 a_pos;",
    "in float a_alpha;",
    "in float a_size;",
    "uniform vec2 u_res;",
    "out float v_alpha;",
    "void main(){",
    "  vec2 clip = (a_pos / u_res) * 2.0 - 1.0;",
    "  gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0);",
    "  gl_PointSize = a_size;",
    "  v_alpha = a_alpha;",
    "}"
  ].join("\n");

  var FRAG = [
    "#version 300 es",
    "precision mediump float;",
    "in float v_alpha;",
    "out vec4 outColor;",
    "uniform vec3 u_color;",
    "uniform bool u_round;",
    "void main(){",
    "  float a = v_alpha;",
    "  if (u_round) {",
    /*   Soft radial falloff so nodes read as glows, not squares. */
    "    vec2 d = gl_PointCoord - 0.5;",
    "    float r = length(d) * 2.0;",
    "    a *= smoothstep(1.0, 0.0, r);",
    "    a *= a;",
    "  }",
    "  outColor = vec4(u_color * a, a);",
    "}"
  ].join("\n");

  function shader(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
  }

  var vs = shader(gl.VERTEX_SHADER, VERT), fs = shader(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return;
  var prog = gl.createProgram();
  gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
  gl.useProgram(prog);

  var uRes = gl.getUniformLocation(prog, "u_res");
  var uColor = gl.getUniformLocation(prog, "u_color");
  var uRound = gl.getUniformLocation(prog, "u_round");

  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  var aPos = gl.getAttribLocation(prog, "a_pos");
  var aAlpha = gl.getAttribLocation(prog, "a_alpha");
  var aSize = gl.getAttribLocation(prog, "a_size");
  gl.enableVertexAttribArray(aPos);
  gl.enableVertexAttribArray(aAlpha);
  gl.enableVertexAttribArray(aSize);
  var STRIDE = 4 * 4;
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, STRIDE, 0);
  gl.vertexAttribPointer(aAlpha, 1, gl.FLOAT, false, STRIDE, 8);
  gl.vertexAttribPointer(aSize, 1, gl.FLOAT, false, STRIDE, 12);

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

  /* ---- simulation ---- */

  var COUNT = 0, LINK = 0;
  var px, py, vx, vy, seed, sizeOf;
  var pointData, lineData;
  var W = 0, H = 0, dpr = 1;
  var ptr = { x: -9999, y: -9999, active: false };

  function hash(n) { var s = Math.sin(n) * 43758.5453; return s - Math.floor(s); }

  function seedField() {
    // Density scales with area so a phone is not asked to link 160 nodes.
    var area = (W * H) / (dpr * dpr);
    COUNT = Math.max(38, Math.min(150, Math.round(area / 11000)));
    LINK = Math.min(W, H) * 0.27;

    px = new Float32Array(COUNT); py = new Float32Array(COUNT);
    vx = new Float32Array(COUNT); vy = new Float32Array(COUNT);
    seed = new Float32Array(COUNT); sizeOf = new Float32Array(COUNT);

    for (var i = 0; i < COUNT; i++) {
      px[i] = hash(i * 1.7) * W;
      py[i] = hash(i * 3.1 + 9.0) * H;
      vx[i] = 0; vy[i] = 0;
      seed[i] = hash(i * 5.9) * 6.283;
      // A few larger nodes give the network some hierarchy.
      sizeOf[i] = (hash(i * 7.3) < 0.14 ? 7.0 : 3.2) * dpr;
    }
    pointData = new Float32Array(COUNT * 4);
    lineData = new Float32Array(COUNT * 10 * 2 * 4);
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.round(canvas.clientWidth * dpr);
    var h = Math.round(canvas.clientHeight * dpr);
    if (w === W && h === H) return;
    W = canvas.width = w; H = canvas.height = h;
    gl.viewport(0, 0, W, H);
    seedField();
  }

  var t = 0;

  function step(dt) {
    t += dt;
    for (var i = 0; i < COUNT; i++) {
      // Flow field: two out-of-phase sinusoids in space and time. Cheap, and
      // it drifts like air rather than marching in a direction.
      var a = Math.sin(px[i] * 0.0016 + t * 0.22 + seed[i]) +
              Math.cos(py[i] * 0.0021 - t * 0.17 + seed[i] * 0.5);
      var ax = Math.cos(a * 1.8) * 5.5 * dpr;
      var ay = Math.sin(a * 1.6) * 5.5 * dpr;

      if (ptr.active) {
        var ddx = px[i] - ptr.x, ddy = py[i] - ptr.y;
        var d2 = ddx * ddx + ddy * ddy;
        var reach = (170 * dpr) * (170 * dpr);
        if (d2 < reach && d2 > 1) {
          var f = (1 - d2 / reach) * 260 * dpr / Math.sqrt(d2);
          ax += ddx * f; ay += ddy * f;
        }
      }

      vx[i] = (vx[i] + ax * dt) * 0.955;
      vy[i] = (vy[i] + ay * dt) * 0.955;
      px[i] += vx[i] * dt;
      py[i] += vy[i] * dt;

      // Wrap with a margin so nodes do not pop at the edges.
      var m = 40 * dpr;
      if (px[i] < -m) px[i] = W + m; else if (px[i] > W + m) px[i] = -m;
      if (py[i] < -m) py[i] = H + m; else if (py[i] > H + m) py[i] = -m;
    }
  }

  function render() {
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform2f(uRes, W, H);

    // Links first, so nodes sit on top of their own threads.
    var n = 0, cap = lineData.length - 8;
    var link2 = LINK * LINK;
    for (var i = 0; i < COUNT && n < cap; i++) {
      for (var j = i + 1; j < COUNT && n < cap; j++) {
        var dx = px[i] - px[j], dy = py[i] - py[j];
        var d2 = dx * dx + dy * dy;
        if (d2 > link2) continue;
        var alpha = (1 - Math.sqrt(d2) / LINK);
        alpha = alpha * alpha * 0.85;
        lineData[n++] = px[i]; lineData[n++] = py[i];
        lineData[n++] = alpha; lineData[n++] = 1;
        lineData[n++] = px[j]; lineData[n++] = py[j];
        lineData[n++] = alpha; lineData[n++] = 1;
      }
    }
    if (n) {
      gl.bufferData(gl.ARRAY_BUFFER, lineData.subarray(0, n), gl.DYNAMIC_DRAW);
      gl.uniform3f(uColor, 0.50, 0.82, 0.24);
      gl.uniform1i(uRound, 0);
      gl.drawArrays(gl.LINES, 0, n / 4);
    }

    for (var k = 0, o = 0; k < COUNT; k++) {
      pointData[o++] = px[k]; pointData[o++] = py[k];
      pointData[o++] = 1.0; pointData[o++] = sizeOf[k];
    }
    gl.bufferData(gl.ARRAY_BUFFER, pointData, gl.DYNAMIC_DRAW);
    gl.uniform3f(uColor, 0.70, 0.96, 0.42);
    gl.uniform1i(uRound, 1);
    gl.drawArrays(gl.POINTS, 0, COUNT);
  }

  var running = false, visible = true, last = 0;

  function frame(now) {
    if (!running) return;
    var dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    step(dt);
    render();
    requestAnimationFrame(frame);
  }

  function play() {
    if (running || !visible || reduce.matches) return;
    running = true; last = performance.now();
    requestAnimationFrame(frame);
  }
  function pause() { running = false; }

  window.addEventListener("resize", function () {
    resize();
    if (!running) { step(0.016); render(); }
  }, { passive: true });

  var host = canvas.parentNode;
  host.addEventListener("pointermove", function (ev) {
    var r = canvas.getBoundingClientRect();
    ptr.x = (ev.clientX - r.left) * dpr;
    ptr.y = (ev.clientY - r.top) * dpr;
    ptr.active = true;
  }, { passive: true });
  host.addEventListener("pointerleave", function () { ptr.active = false; },
    { passive: true });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) {
      visible = e[0].isIntersecting;
      if (visible) play(); else pause();
    }, { threshold: 0 }).observe(canvas);
  }
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) pause(); else play();
  });
  canvas.addEventListener("webglcontextlost", function (ev) {
    ev.preventDefault(); pause(); canvas.classList.remove("is-live");
  });

  resize();
  canvas.classList.add("is-live");
  if (reduce.matches) {
    // One settled frame, then nothing moves.
    for (var w = 0; w < 90; w++) step(0.033);
    render();
  } else {
    play();
  }
})();
