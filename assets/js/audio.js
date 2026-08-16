/* EcoHeat -- Web Audio layer for the yard.
 *
 * A quiet ambient drone plus impact and boost cues, synthesised on the fly --
 * no audio files, so nothing extra to download. Impacts are panned by where
 * they happened on the canvas and voiced by how hard they landed.
 *
 * Off until asked for. The context is not even created until the visitor
 * presses the sound button, which also satisfies the browser's requirement
 * that audio start from a user gesture.
 *
 * Exposes window.EcoAudio = { on, toggle, hit(strength, pan), boost() }.
 */
window.EcoAudio = (function () {
  "use strict";

  var Ctx = window.AudioContext || window.webkitAudioContext;
  var ctx = null, master = null, drone = null, voices = [];
  var on = false;
  var lastHit = 0;

  function build() {
    ctx = new Ctx();

    master = ctx.createGain();
    master.gain.value = 0;
    master.connect(ctx.destination);

    // Ambient bed: three slightly detuned oscillators under a lowpass, with a
    // very slow LFO opening and closing the filter. Reads as room tone.
    drone = ctx.createGain();
    drone.gain.value = 0.055;

    var filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 320;
    filter.Q.value = 3.5;

    var lfo = ctx.createOscillator();
    var lfoGain = ctx.createGain();
    lfo.frequency.value = 0.045;
    lfoGain.gain.value = 165;
    lfo.connect(lfoGain).connect(filter.frequency);
    lfo.start();

    [55, 82.4, 110.3].forEach(function (hz, i) {
      var osc = ctx.createOscillator();
      osc.type = i === 2 ? "triangle" : "sawtooth";
      osc.frequency.value = hz;
      osc.detune.value = (i - 1) * 7;
      var g = ctx.createGain();
      g.gain.value = i === 0 ? 0.5 : 0.22;
      osc.connect(g).connect(filter);
      osc.start();
      voices.push(osc);
    });

    filter.connect(drone).connect(master);
  }

  function ramp(to) {
    if (!ctx) return;
    var now = ctx.currentTime;
    master.gain.cancelScheduledValues(now);
    master.gain.setValueAtTime(master.gain.value, now);
    master.gain.linearRampToValueAtTime(to, now + (to > 0 ? 0.7 : 0.35));
  }

  return {
    get on() { return on; },

    toggle: function () {
      if (!Ctx) return false;
      if (!ctx) build();
      on = !on;
      if (on && ctx.state === "suspended") ctx.resume();
      ramp(on ? 0.9 : 0);
      return on;
    },

    /* strength 0..1, pan -1..1 */
    hit: function (strength, pan) {
      if (!on || !ctx) return;
      var now = ctx.currentTime;
      // Rate limit: a pile-up can produce dozens of contacts in one frame and
      // stacking them all is both ugly and loud.
      if (now - lastHit < 0.035) return;
      lastHit = now;

      var s = Math.max(0.06, Math.min(1, strength));

      var osc = ctx.createOscillator();
      osc.type = "triangle";
      // Harder knocks ring lower and louder, like something heavier landing.
      var f0 = 760 - s * 420;
      osc.frequency.setValueAtTime(f0, now);
      osc.frequency.exponentialRampToValueAtTime(f0 * 0.45, now + 0.13);

      var g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, now);
      g.gain.exponentialRampToValueAtTime(0.16 * s, now + 0.006);
      g.gain.exponentialRampToValueAtTime(0.0001, now + 0.16 + s * 0.12);

      var node = osc;
      if (ctx.createStereoPanner) {
        var p = ctx.createStereoPanner();
        p.pan.value = Math.max(-1, Math.min(1, pan || 0));
        g.connect(p).connect(master);
      } else {
        g.connect(master);
      }
      node.connect(g);
      osc.start(now);
      osc.stop(now + 0.4);
    },

    boost: function () {
      if (!on || !ctx) return;
      var now = ctx.currentTime;
      var osc = ctx.createOscillator();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(180, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.28);

      var filter = ctx.createBiquadFilter();
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(500, now);
      filter.frequency.exponentialRampToValueAtTime(2400, now + 0.28);
      filter.Q.value = 6;

      var g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, now);
      g.gain.exponentialRampToValueAtTime(0.09, now + 0.05);
      g.gain.exponentialRampToValueAtTime(0.0001, now + 0.34);

      osc.connect(filter).connect(g).connect(master);
      osc.start(now);
      osc.stop(now + 0.4);
    }
  };
})();
