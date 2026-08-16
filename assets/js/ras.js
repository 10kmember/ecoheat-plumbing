/* EcoHeat -- Ras, the site assistant.
 *
 * Everything Ras knows is in the KNOWLEDGE table below. There is no network
 * call and no model behind it: an incoming message is scored against each
 * topic's keywords, the best match wins, and one of that topic's replies is
 * chosen at random. The last reply used per topic is remembered, so asking the
 * same question twice gets a different answer rather than an echo.
 *
 * The pause before an answer is deliberate. It is scaled to the length of the
 * reply so a one-liner comes back quickly and a longer explanation takes a
 * beat, which reads as consideration rather than a lookup.
 *
 * Ras never quotes a price or invents a fact. Anything that depends on the
 * property, the survey or a commercial decision is handed to the phone number
 * or the relevant page, because getting that wrong on a real trading site
 * costs the business more than a chat widget is worth.
 */
(function () {
  "use strict";

  var mount = document.getElementById("ras");
  if (!mount) return;

  var ROOT = mount.getAttribute("data-root") || "";

  function link(href, text) {
    return '<a href="' + ROOT + href + '">' + text + "</a>";
  }
  var TEL = '<a href="tel:+441934440290">01934 440290</a>';

  /* ================= knowledge base ================= */
  /* weight 3 = decisive term, 2 = strong, 1 = supporting. */

  var KNOWLEDGE = [
    {
      id: "greeting",
      keywords: { hello: 3, hi: 3, hey: 3, morning: 2, afternoon: 2,
                  evening: 2, greetings: 3, yo: 2, "good day": 3 },
      replies: [
        "Hello. I'm Ras, and I look after questions on this site. Boilers, heat pumps, grants, bathrooms, what we charge for, where we travel to. What are you after?",
        "Hi there. Ask me anything about the work EcoHeat does. I'm best on heat pumps and the grant, but I'll have a go at most things.",
        "Morning, afternoon, or whenever this is. I'm Ras. What can I help you work out?"
      ]
    },
    {
      id: "heatpump",
      keywords: { "heat pump": 3, "air source": 3, ashp: 3, renewable: 2,
                  "heat pumps": 3, cop: 2, scop: 2, refrigerant: 2 },
      replies: [
        "Air source heat pumps are the bulk of our renewables work. The part that decides whether yours will be cheap to run isn't the badge on the unit, it's the heat loss survey: measure every room, work out the flow temperature the house can live with, then size the unit and the radiators to that. We do that survey free. " + link("services/air-source-heat-pumps/", "Full detail is here") + ".",
        "Short version: a heat pump is efficient when it runs cool. Design to a low flow temperature, upsize the few radiators that need it, set the weather compensation properly on commissioning, and it behaves. Guess at any of those and it's noisy and expensive. " + link("services/air-source-heat-pumps/", "More on our approach") + ".",
        "Worth knowing before you go further: eligible properties get " + link("grants/", "£7,500 off through the Boiler Upgrade Scheme") + ", and we apply for it so it comes off your quote rather than you claiming it back. Happy to talk through whether your place is a good candidate on " + TEL + "."
      ]
    },
    {
      id: "grant",
      keywords: { grant: 4, grants: 4, "boiler upgrade": 4, bus: 2,
                  funding: 3, ofgem: 3, "7500": 3, "7,500": 3, subsidy: 3,
                  eco4: 4, voucher: 3, epc: 3 },
      replies: [
        "The Boiler Upgrade Scheme pays £7,500 towards an air source heat pump on eligible properties in England and Wales. It's a grant, not a loan. You never pay it out and reclaim it: we apply on your behalf and deduct it from the quotation. " + link("grants/", "The whole process is set out here") + ".",
        "Eligibility usually comes down to three things: a domestic property in England or Wales, a valid EPC with no outstanding loft or cavity wall insulation recommendations, and a fossil fuel system being replaced. We check your EPC before quoting and tell you honestly where you stand. " + link("grants/", "Details") + ".",
        "Grant rules are set by government and do change, so I'd rather you had it in writing than from me. What I can say is we handle the Ofgem application end to end, and there's no charge for the eligibility check. " + link("contact/", "Send us a postcode") + " and we'll look it up."
      ]
    },
    {
      id: "boiler",
      keywords: { boiler: 3, combi: 3, "new boiler": 3, install: 1,
                  worcester: 2, vaillant: 2, ideal: 2, baxi: 2, viessmann: 2,
                  lpg: 2, oil: 2, "back boiler": 3, gas: 1 },
      replies: [
        "We fit gas, LPG and oil boilers, and we're not tied to a manufacturer, so the recommendation comes from the appliance and the warranty rather than a supplier target. Sizing is done from a room-by-room heat loss calculation, not by matching whatever was on the wall before. " + link("services/boiler-installation/", "More here") + ".",
        "A straight combi swap in the same position is usually a day. Moving it, converting from a conventional system, or taking out a back boiler is more like two to three, and we put that in writing with the quote so you know which days you're without hot water. " + link("services/boiler-installation/", "Boiler installation") + ".",
        "One thing worth checking on any quote, ours included: what's actually in the price. Ours covers the boiler and flue, controls, a magnetic filter, the flush, Building Regulations notification and the warranty registration. " + link("services/boiler-installation/", "The full list is here") + "."
      ]
    },
    {
      id: "pressure",
      keywords: { pressure: 4, "losing pressure": 4, "loses pressure": 4,
                  "topping up": 3, repressurise: 4, "cold radiator": 4,
                  "cold radiators": 4, bleed: 3, airlock: 3, "air lock": 3 },
      replies: [
        "Pressure loss is almost always one of two things: a small leak somewhere on the system, or a failed expansion vessel. Dropping over weeks points at a leak; dropping over hours points at the vessel or the pressure relief valve. " + link("services/boiler-servicing-and-repairs/", "Either is diagnosable in one visit") + ".",
        "Whatever you do, don't just keep topping it up and carrying on. Repeated repressurising forces fresh oxygenated water into the system, which corrodes radiators from the inside. Worth getting the cause found: " + TEL + ".",
        "Cold at the top of a radiator is usually air, cold at the bottom is usually sludge, and a whole radiator cold is usually the valve. The first you can bleed yourself; the other two want a power flush or a valve change. " + link("services/boiler-servicing-and-repairs/", "Repairs") + "."
      ]
    },
    {
      id: "servicing",
      keywords: { service: 3, servicing: 4, "annual service": 4, cp12: 4,
                  "gas safety": 4, certificate: 3, landlord: 3,
                  "power flush": 4, flush: 3, maintain: 2, "how often": 3 },
      replies: [
        "Once every twelve months, and it matters more than people expect: manufacturers make an annual service a warranty condition, so a missed one can void a ten-year warranty exactly when you need to claim on it. " + link("services/boiler-servicing-and-repairs/", "What a service covers") + ".",
        "A proper service is flue gas analysis against the manufacturer's own figures, seals and combustion chamber, gas rate and working pressure, safety devices, condensate and vessel, plus a written record. Not a look at the front panel. " + link("services/boiler-servicing-and-repairs/", "Details") + ".",
        "For landlords, CP12 certificates usually inside a few working days, several properties in one visit if that suits, and we diary the renewal so nothing lapses. " + link("services/boiler-servicing-and-repairs/", "Servicing and certificates") + "."
      ]
    },
    {
      id: "breakdown",
      keywords: { repair: 3, broken: 4, "not working": 4, fault: 3,
                  breakdown: 4, lockout: 4, "error code": 4, "wont fire": 4,
                  "won\'t fire": 4, noisy: 3, banging: 3, kettling: 4 },
      replies: [
        "We diagnose before we quote, which sounds obvious and often isn't. If a repair isn't economic on an old appliance we'll say so plainly rather than replacing parts one at a time until you give up. " + link("services/boiler-servicing-and-repairs/", "Repairs and diagnostics") + ".",
        "If you have an error code on the display, note it down before you reset anything, and send it over on WhatsApp. Half the time it tells us what we'll need to bring, which saves a second visit. " + TEL + ".",
        "Banging or kettling usually means limescale or sludge in the heat exchanger rather than the boiler being finished. Worth having looked at before it becomes a replacement. " + link("services/boiler-servicing-and-repairs/", "Get it diagnosed") + "."
      ]
    },
    {
      id: "emergency",
      keywords: { emergency: 3, urgent: 3, leak: 3, leaking: 3, burst: 3,
                  flood: 3, flooding: 3, "no heating": 3, "no hot water": 3,
                  "smell gas": 3, "gas leak": 3, now: 1, today: 2 },
      replies: [
        "If you can smell gas, stop reading this: leave the property, don't touch light switches, and call the National Gas Emergency Service on 0800 111 999 first. For water, find the stop tap and turn it off, then call us on " + TEL + ".",
        "For a burst or a leak, the thirty seconds it takes to shut off the stop tap is the difference between a wet floor and a new ceiling. Do that first, then ring " + TEL + " and you'll get a straight answer about when we can be there. " + link("services/emergency-plumbing/", "What counts as an emergency") + ".",
        "No heating or hot water in cold weather counts as urgent and we prioritise it, service-plan customers first. Ring " + TEL + " rather than sending a form for anything like this. " + link("services/emergency-plumbing/", "Emergency call-outs") + "."
      ]
    },
    {
      id: "bathroom",
      keywords: { bathroom: 3, shower: 3, tap: 3, taps: 3, toilet: 3,
                  basin: 3, "wet room": 3, ensuite: 3, "en-suite": 3,
                  tiling: 2, cylinder: 2, "underfloor heating": 3,
                  plumbing: 2, plumber: 2 },
      replies: [
        "We do complete bathrooms with one team from strip-out to snagging, which mostly means you have one person to chase rather than four trades. Typical family bathroom is five to ten working days, and you get a day-by-day schedule before we start. " + link("services/plumbing-and-bathrooms/", "Bathrooms and plumbing") + ".",
        "If you're buying your own suite, send us the spec before you order. The most common problem by a distance is a shower or tap the property's water pressure simply can't run properly, and that's far cheaper to catch before delivery than after tiling. " + link("services/plumbing-and-bathrooms/", "More here") + ".",
        "Beyond bathrooms we do the everyday stuff too: taps, stop taps, waste and soil pipework, outside taps, immersion heaters, pumps, unvented cylinders and wet underfloor heating. " + link("services/plumbing-and-bathrooms/", "The full list") + "."
      ]
    },
    {
      id: "price",
      keywords: { price: 4, cost: 4, quote: 4, quotation: 4, "how much": 4,
                  cheap: 2, expensive: 2, estimate: 3, charge: 2, fee: 2,
                  deposit: 2, pay: 1, payment: 2 },
      replies: [
        "I'm not going to guess a number at you, because the honest answer depends on the property and that's exactly what the survey is for. What I can tell you is the survey is free, the quote is fixed and itemised, and it's valid for 30 days. " + link("contact/", "Ask for one here") + " or ring " + TEL + ".",
        "The structure, at least, is straightforward: free survey, one fixed written price with any grant already deducted, a deposit covering materials, and the balance only on completion and commissioning. Nothing gets added that you haven't agreed in writing first.",
        "Fixed price means fixed. The only things that move it are you asking for extra work, or something genuinely hidden turning up once panels are off, and in that case we stop and re-quote before carrying on rather than putting it on the invoice. " + link("contact/", "Request a quote") + "."
      ]
    },
    {
      id: "plans",
      keywords: { plan: 3, plans: 3, "service plan": 3, cover: 2,
                  subscription: 2, "direct debit": 3, monthly: 2, annual: 2,
                  maintenance: 2 },
      replies: [
        "There are three plans: Essential, Complete and Renewables. All can be paid monthly by Direct Debit or annually in one payment, and paying annually saves the equivalent of one instalment. " + link("services/annual-service-plans/", "What each one covers is here") + ".",
        "A plan does two useful things. It makes sure the annual service actually happens, which is what keeps a manufacturer warranty valid, and it puts you ahead of non-plan customers in the week everyone's heating fails at once. " + link("services/annual-service-plans/", "The comparison") + ".",
        "Plans run twelve months, renew only with your agreement, and you can cancel with 30 days' notice with no exit fee. For current pricing ring " + TEL + ", since I'd rather you had a figure from a person than from me. " + link("services/annual-service-plans/", "Inclusions") + "."
      ]
    },
    {
      id: "finance",
      keywords: { finance: 3, credit: 3, loan: 3, "pay monthly": 3,
                  interest: 3, apr: 3, instalments: 3, borrow: 2,
                  affordable: 2, spread: 2 },
      replies: [
        "Finance is available on qualifying installations through an FCA-authorised provider, subject to status. Interest-free over shorter terms, or longer terms with interest. " + link("finance/", "Options are set out here") + ".",
        "Grant and finance work together: the £7,500 comes off the quotation first, then finance is arranged on the balance, so you're only ever financing what you actually have to pay. " + link("finance/", "Finance") + ".",
        "We'll always show you the total amount repayable next to the monthly figure, so you're comparing like with like. And if paying outright is better for you, we'll say so. " + link("finance/", "More detail") + "."
      ]
    },
    {
      id: "areas",
      keywords: { area: 3, areas: 3, cover: 2, travel: 3, where: 2,
                  local: 2, taunton: 3, bridgwater: 3, cheddar: 3,
                  wells: 3, clevedon: 3, nailsea: 3, burnham: 3,
                  "weston-super-mare": 3, weston: 3, somerset: 2,
                  postcode: 2, near: 2, distance: 2 },
      replies: [
        "We're based at Edingworth, between Weston-super-Mare and Burnham-on-Sea, and work across Somerset and North Somerset. Roughly a 30 mile radius, with the M5 corridor covered daily. " + link("areas-we-cover/", "Full list of towns") + ".",
        "Emergency response is honest about distance: same day, usually within hours, around Weston, Burnham, Highbridge and Brent Knoll; same or next working day out to Taunton, Wells, Clevedon and Nailsea. " + link("areas-we-cover/", "The breakdown") + ".",
        "If you're just outside, ring and ask rather than wondering. We'd rather give you a straight no than quote for a job we can't service properly afterwards. " + TEL + "."
      ]
    },
    {
      id: "trust",
      keywords: { "gas safe": 3, registered: 2, qualified: 3, insured: 3,
                  insurance: 2, certified: 3, mcs: 3, accredited: 3,
                  "company number": 3, legit: 2, trust: 2, reviews: 3,
                  review: 3, checkatrade: 2 },
      replies: [
        "Gas Safe registered under number 952210, which you can verify yourself at gassaferegister.co.uk. Registered in England and Wales, company number 15532701, and we carry public liability insurance. " + link("about/", "About us") + ".",
        "On heat pumps specifically: the installation is designed, commissioned and certified with our MCS-accredited partner, and that accreditation is what makes the £7,500 grant payable. The certificate is issued in your name. " + link("grants/", "How that works") + ".",
        "We're a young company and we'd rather show you nothing than testimonials we wrote ourselves, so the " + link("reviews/", "reviews page") + " points at our actual Facebook page. Genuine reviews go up there as they come in."
      ]
    },
    {
      id: "booking",
      keywords: { book: 3, booking: 3, appointment: 3, survey: 3,
                  visit: 2, contact: 3, phone: 3, call: 2, email: 3,
                  "get in touch": 3, arrange: 2, speak: 2 },
      replies: [
        "Quickest is the phone: " + TEL + ", and you'll get an engineer rather than a call centre. For anything less urgent the " + link("contact/", "enquiry form") + " reaches the same people and we aim to reply the same working day.",
        "Surveys are free and carry no obligation, so there's no reason not to get one booked. " + link("contact/", "Send us the details") + " or ring " + TEL + ".",
        "If it helps, send a photo of the boiler, the leak or the error code over WhatsApp. It often saves a visit entirely. Details are on the " + link("contact/", "contact page") + "."
      ]
    },
    {
      id: "hours",
      keywords: { open: 3, hours: 3, "what time": 3, weekend: 3,
                  saturday: 3, sunday: 3, availability: 2, closed: 2 },
      replies: [
        "Monday to Friday 07:30 to 17:30, Saturday 08:00 to 13:00. Sundays are emergency call-outs only.",
        "Office hours are 07:30 to 17:30 on weekdays and Saturday mornings, but burst pipes and total loss of heating get answered outside those. " + TEL + ".",
        "Weekdays 07:30 to 17:30, Saturdays until one. Outside that, ring " + TEL + " if it's an actual emergency and someone will tell you honestly when they can be with you."
      ]
    },
    {
      id: "about-ras",
      keywords: { "who are you": 3, "real person": 4, "are you real": 3,
                  bot: 3, robot: 3, chatbot: 4, "your name": 3, ras: 3,
                  human: 3, ai: 3, person: 2, machine: 2, automated: 3,
                  "who am i talking to": 4, scripted: 3 },
      replies: [
        "I'm Ras, and I'm a script. Everything I say is written into this page in advance, chosen by matching a few keywords in what you type. No model, no server, nothing sent anywhere. For anything that needs judgement, ring " + TEL + " and you'll get an engineer.",
        "Honest answer: not human. I'm a small piece of JavaScript with a fixed set of answers about EcoHeat's work. I try to pick a useful one, but I can't see your property, price a job, or promise a date.",
        "Ras, site assistant, entirely scripted. My value is that I know which page you probably want. My limit is that I don't know anything that isn't already written on this site."
      ]
    },
    {
      id: "thanks",
      keywords: { thanks: 3, "thank you": 3, cheers: 3, ta: 2, "great": 1,
                  bye: 3, goodbye: 3, "see you": 2, brilliant: 2, perfect: 2 },
      replies: [
        "Any time. If it turns into a real job, " + TEL + " gets you an engineer.",
        "You're welcome. Come back if something else comes up.",
        "Glad that helped. Good luck with it."
      ]
    }
  ];

  var FALLBACK = [
    "I don't have a scripted answer for that one, and I'd rather admit it than invent something. Try me on heat pumps, grants, boilers, bathrooms, service plans, areas we cover or how we price. Or ring " + TEL + " and ask a person.",
    "That's outside what I've been taught, I'm afraid. The " + link("faq/", "FAQ page") + " covers a fair bit more, and " + TEL + " covers the rest.",
    "Not something I know. I'm scripted rather than clever, so anything specific to your property needs an actual engineer: " + TEL + ".",
    "Can you put that another way? I match on keywords, so words like heat pump, grant, boiler, bathroom, plan, finance or areas will get you further than I just did."
  ];

  var CHIPS = [
    "How does the £7,500 grant work?",
    "Do I need a new boiler?",
    "Which areas do you cover?",
    "How much does it cost?",
    "Are you Gas Safe registered?",
    "Are you a real person?"
  ];

  /* ================= matching ================= */

  function normalise(s) {
    return (" " + s.toLowerCase() + " ").replace(/[^a-z0-9£,\s-]/g, " ")
      .replace(/\s+/g, " ");
  }

  function score(text, topic) {
    var total = 0;
    for (var key in topic.keywords) {
      if (!Object.prototype.hasOwnProperty.call(topic.keywords, key)) continue;
      // Word-boundary match, so "gas" does not fire inside "gasket".
      if (text.indexOf(" " + key + " ") !== -1 ||
          text.indexOf(" " + key + ",") !== -1 ||
          new RegExp("\\b" + key.replace(/[-\s]/g, "[-\\s]") + "\\b").test(text)) {
        total += topic.keywords[key];
      }
    }
    return total;
  }

  var lastUsed = {};   // topic id -> index of the reply last given

  function pick(list, id) {
    if (list.length === 1) return list[0];
    var prev = lastUsed[id];
    var i;
    do { i = Math.floor(Math.random() * list.length); } while (i === prev);
    lastUsed[id] = i;
    return list[i];
  }

  function answer(input) {
    var text = normalise(input);
    var best = null, bestScore = 0;
    for (var i = 0; i < KNOWLEDGE.length; i++) {
      var s = score(text, KNOWLEDGE[i]);
      if (s > bestScore) { bestScore = s; best = KNOWLEDGE[i]; }
    }
    // A single supporting keyword is not enough to claim a topic.
    if (!best || bestScore < 2) return pick(FALLBACK, "fallback");
    return pick(best.replies, best.id);
  }

  /* ================= interface ================= */

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  mount.innerHTML =
    '<button class="ras__launch" type="button" aria-expanded="false" ' +
    'aria-controls="ras-panel">' +
    '<span class="ras__avatar" aria-hidden="true">R</span>' +
    '<span class="ras__launch-label">Ask Ras</span></button>' +
    '<div class="ras__panel" id="ras-panel" role="dialog" ' +
    'aria-label="Chat with Ras, the EcoHeat site assistant" hidden>' +
    '<div class="ras__head">' +
    '<span class="ras__avatar" aria-hidden="true">R</span>' +
    '<div><b>Ras</b><span>Scripted site assistant</span></div>' +
    '<button class="ras__close" type="button" aria-label="Close chat">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" aria-hidden="true">' +
    '<path d="M18 6 6 18M6 6l12 12"/></svg></button></div>' +
    '<div class="ras__log" id="ras-log" role="log" aria-live="polite" ' +
    'aria-atomic="false"></div>' +
    '<div class="ras__chips" id="ras-chips"></div>' +
    '<form class="ras__form">' +
    '<label class="visually-hidden" for="ras-input">Your message to Ras' +
    "</label>" +
    '<input id="ras-input" type="text" autocomplete="off" ' +
    'placeholder="Ask about heat pumps, grants, boilers…">' +
    '<button type="submit" aria-label="Send message">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ' +
    'aria-hidden="true"><path d="m4 20 16-8L4 4v6l10 2-10 2Z"/></svg>' +
    "</button></form></div>";

  var launch = mount.querySelector(".ras__launch");
  var panel = mount.querySelector(".ras__panel");
  var closeBtn = mount.querySelector(".ras__close");
  var log = mount.querySelector(".ras__log");
  var chips = mount.querySelector(".ras__chips");
  var form = mount.querySelector(".ras__form");
  var input = mount.querySelector("#ras-input");

  var opened = false;
  var busy = false;

  function bubble(who, content, asText) {
    var el = document.createElement("div");
    el.className = "ras__msg ras__msg--" + who;
    // Anything the visitor typed goes in as text, never as markup.
    if (asText) el.textContent = content; else el.innerHTML = content;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function think(reply) {
    busy = true;
    var dots = document.createElement("div");
    dots.className = "ras__msg ras__msg--ras ras__typing";
    dots.innerHTML = reduce.matches
      ? "Ras is typing"
      : '<span></span><span></span><span></span>';
    dots.setAttribute("aria-label", "Ras is typing");
    log.appendChild(dots);
    log.scrollTop = log.scrollHeight;

    // Longer answers take longer to arrive. Reading time, roughly.
    var plain = reply.replace(/<[^>]+>/g, "");
    var wait = Math.min(2600, 620 + plain.length * 9) + Math.random() * 260;

    setTimeout(function () {
      dots.remove();
      bubble("ras", reply);
      busy = false;
    }, reduce.matches ? 400 : wait);
  }

  function ask(text) {
    if (busy || !text.trim()) return;
    bubble("you", text, true);
    think(answer(text));
  }

  CHIPS.forEach(function (q) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "ras__chip";
    b.textContent = q;
    b.addEventListener("click", function () {
      input.value = "";
      ask(q);
    });
    chips.appendChild(b);
  });

  function open() {
    if (opened) return;
    opened = true;
    panel.removeAttribute("hidden");
    launch.setAttribute("aria-expanded", "true");
    if (!log.childNodes.length) {
      think("Hello. I'm Ras, EcoHeat's site assistant. I'm scripted rather " +
        "than clever, but I know this site well. Ask me about heat pumps, the " +
        "£7,500 grant, boilers, bathrooms, service plans, or where we travel.");
    }
    input.focus();
  }

  function close() {
    opened = false;
    panel.setAttribute("hidden", "");
    launch.setAttribute("aria-expanded", "false");
    launch.focus();
  }

  launch.addEventListener("click", function () {
    if (opened) close(); else open();
  });
  closeBtn.addEventListener("click", close);

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var v = input.value;
    input.value = "";
    ask(v);
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && opened) {
      ev.stopPropagation();
      close();
    }
  }, true);
})();
