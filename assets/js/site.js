/* EcoHeat Plumbing and Renewables -- progressive enhancement only.
   Every page works with JavaScript disabled: the navigation and the FAQ are
   <details> disclosures needing no script, and the contact form falls back to
   an ordinary submit. This file only upgrades the form to an inline,
   no-page-reload send when a form endpoint is configured. */
(function () {
  "use strict";

  /* ---- contact form ---- */
  var form = document.querySelector("form[data-contact-form]");
  if (!form) return;

  var status = form.querySelector(".form__status");
  var endpoint = form.getAttribute("action") || "";
  var usesMailto = endpoint.indexOf("mailto:") === 0;

  function show(kind, message) {
    if (!status) return;
    status.className = "form__status form__status--" + kind;
    status.textContent = message;
    status.setAttribute("role", "status");
    status.scrollIntoView({ block: "nearest" });
  }

  form.addEventListener("submit", function (event) {
    /* Honeypot: a real person never fills a field they cannot see. */
    var trap = form.querySelector('input[name="company_website"]');
    if (trap && trap.value !== "") {
      event.preventDefault();
      return;
    }

    /* With no configured endpoint the browser handles the mailto: submit. */
    if (usesMailto || !endpoint) return;

    event.preventDefault();
    var button = form.querySelector('button[type="submit"]');
    if (button) {
      button.disabled = true;
      button.dataset.label = button.textContent;
      button.textContent = "Sending…";
    }

    fetch(endpoint, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" }
    })
      .then(function (response) {
        if (!response.ok) throw new Error("Request failed");
        form.reset();
        show(
          "ok",
          "Thank you — your enquiry has been sent. We aim to reply the same " +
            "working day. If it is urgent, please call 01934 440290."
        );
      })
      .catch(function () {
        show(
          "err",
          "Sorry, that did not send. Please call 01934 440290 or email " +
            "info@ecoheatplumbingandrenewables.co.uk and we will pick it up."
        );
      })
      .then(function () {
        if (button) {
          button.disabled = false;
          button.textContent = button.dataset.label || "Send enquiry";
        }
      });
  });
})();
