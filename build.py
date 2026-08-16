#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator for ecoheatplumbingandrenewables.co.uk.

    python3 build.py            build the site into the repository root
    python3 build.py --check    rebuild into a temp dir and diff (used by CI)

All content lives in src/content.py. Every internal link is relative, so the
output works both at a domain root and under a GitHub Pages project path.
"""

from __future__ import annotations

import html
import os
import re
import shutil
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import content as C  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DATE = date.today().isoformat()

# Where the contact form posts. Leave empty and the form degrades to a mailto:
# submission that opens the visitor's mail client -- no third-party processor,
# so nothing extra to declare in the privacy policy. Set it to an HTTPS form
# endpoint (Formspree, Netlify, Basin, a bespoke handler) and the form posts
# by fetch() with an inline success message. If you set one, name the provider
# in the privacy policy's "Who we share your data with" section.
FORM_ENDPOINT = ""

# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------

_ICON_BODY = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
    "mail": '<path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z"/><path d="m22 6-10 7L2 6"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "flame": '<path d="M12 22c4 0 7-2.7 7-6.5 0-4.5-4-6.5-4-10.5-2 1-3 3-3 5 0-1-1-2.5-2-3-1 2-3 4-3 8.5C7 19.3 8 22 12 22Z"/>',
    "boiler": '<rect x="4" y="3" width="16" height="14" rx="2"/><path d="M8 7h8M8 11h4M9 17v4M15 17v4"/>',
    "spanner": '<path d="M14.7 6.3a4 4 0 0 0 5 5l-9.4 9.4a2.8 2.8 0 0 1-4-4Z"/><path d="m19.7 11.3 1.6-1.6a4 4 0 0 0-5.2-5.2l-1.6 1.6"/>',
    "heatpump": '<rect x="2" y="5" width="20" height="12" rx="2"/><path d="M12 8v6M9.5 9.5l5 3M14.5 9.5l-5 3M6 20h12"/>',
    "tap": '<path d="M9 4h6v4H9zM12 8v5"/><path d="M6 13h12a0 0 0 0 1 0 0v3a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4v-3a0 0 0 0 1 0 0Z"/>',
    "alert": '<path d="M12 2 1 21h22L12 2Z"/><path d="M12 9v5M12 18h.01"/>',
    "pound": '<path d="M6 20h12M8 20v-6H6M8 14h7M8 14V8a4 4 0 0 1 7.5-2"/>',
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2Z"/><circle cx="12" cy="13" r="4"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8-6.2-3.3-6.2 3.3L7 14.2l-5-4.9 6.9-1Z"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M9 15h6M9 11h2"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "sound": '<path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/>',
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-4-.9L3 21l1.9-4.6A8.4 8.4 0 0 1 12 3a8.4 8.4 0 0 1 9 8.5Z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9"/>',
}


def icon(name: str, cls: str = "") -> str:
    body = _ICON_BODY[name]
    fill = "none"
    return (
        '<svg viewBox="0 0 24 24" fill="{f}" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false"{c}>{b}</svg>'
    ).format(f=fill, b=body, c=(' class="%s"' % cls) if cls else "")


def e(text: str) -> str:
    return html.escape(text, quote=True)


# --------------------------------------------------------------------------
# site map / navigation
# --------------------------------------------------------------------------

SERVICE_BY_SLUG = {s["slug"]: s for s in C.SERVICES}

# path -> short label, used for related-link cards outside /services/.
EXTRA_LINKS = {
    "grants": ("Boiler Upgrade Scheme grants",
               "How the {} grant works and whether your property qualifies."
               .format(C.BUS_GRANT)),
    "finance": ("Finance options",
                "Spread the cost of an installation over 2 to 10 years."),
}

NAV = [
    ("Services", "services/", [(x["nav"], "services/%s/" % x["slug"])
                               for x in C.SERVICES]),
    ("Renewables", "grants/", []),
    ("Work", "projects/", []),
    ("Contact", "contact/", []),
]


def rel(depth: int) -> str:
    return "../" * depth


# --------------------------------------------------------------------------
# shared chrome
# --------------------------------------------------------------------------

def tel_link(cls: str = "", label: str | None = None) -> str:
    return '<a href="tel:{e}"{c}>{i}{l}</a>'.format(
        e=C.BUSINESS["phone_e164"],
        c=(' class="%s"' % cls) if cls else "",
        i=icon("phone"),
        l=e(label or C.BUSINESS["phone"]),
    )


def header(r: str, current: str) -> str:
    out = []
    for label, path, children in NAV:
        active = current == path or (
            children and any(current == c[1] for c in children))
        aria = ' aria-current="page"' if current == path else ""
        if children:
            sub = "".join(
                '<li><a href="{r}{p}"{a}>{l}</a></li>'.format(
                    r=r, p=p, l=e(l),
                    a=' aria-current="page"' if current == p else "")
                for l, p in children
            )
            # On small screens the sub-items are simply listed under the
            # parent; on wide screens CSS turns them into a hover/focus
            # dropdown. No JavaScript and no toggle button either way.
            out.append(
                '<li><a href="{r}{p}"{a}>{l}</a>'
                '<ul class="nav__sub" aria-label="{l}">{sub}</ul></li>'.format(
                    r=r, p=path, l=e(label), a=aria, sub=sub)
            )
        else:
            out.append('<li><a href="{r}{p}"{a}>{l}</a></li>'.format(
                r=r, p=path, l=e(label), a=aria))

    # A <details> disclosure rather than a scripted button: the menu opens on
    # small screens with JavaScript disabled, and CSS unfolds it into a
    # horizontal bar on wide screens.
    return (
        '<header class="header"><div class="wrap">'
        '<a class="brand" href="{r}index.html" aria-label="{name} home">'
        '<img src="{r}assets/img/ecoheat-logo.png" width="460" height="374" '
        'alt="{name} logo"></a>'
        '<details class="nav" id="primary-nav">'
        '<summary class="nav-toggle">{menu}Menu</summary>'
        '<nav class="nav__panel" aria-label="Primary"><ul>{items}</ul></nav>'
        "</details>"
        '<a class="header__cta" href="tel:{tel}">{phone}{num}</a>'
        "</div></header>"
    ).format(r=r, name=e(C.BUSINESS["name"]), menu=icon("menu"),
             items="".join(out), tel=C.BUSINESS["phone_e164"],
             phone=icon("phone"), num=e(C.BUSINESS["phone"]))


def footer(r: str) -> str:
    services = "".join(
        '<li><a href="{r}services/{s}/">{n}</a></li>'.format(
            r=r, s=s["slug"], n=e(s["nav"]))
        for s in C.SERVICES
    )
    company = "".join(
        '<li><a href="{r}{p}">{n}</a></li>'.format(r=r, p=p, n=e(n))
        for n, p in [
            ("About EcoHeat", "about/"),
            ("Areas we cover", "areas-we-cover/"),
            ("Projects & case studies", "projects/"),
            ("Reviews", "reviews/"),
            ("Grants", "grants/"),
            ("Finance options", "finance/"),
            ("FAQs", "faq/"),
            ("Contact", "contact/"),
        ]
    )
    hours = "".join(
        "<li>{d} <span>{h}</span></li>".format(d=e(d), h=e(h))
        for d, h in C.BUSINESS["opening"]
    )
    return (
        '<footer class="footer"><div class="wrap">'
        '<div class="footer__grid">'
        '<div class="footer__brand">'
        '<img src="{r}assets/img/ecoheat-logo.png" width="460" height="374" '
        'alt="{name} logo">'
        "<p>Plumbing, heating and renewable energy across Somerset and "
        "North Somerset.</p>"
        '<p><a href="{fb}" rel="noopener">Follow us on Facebook</a></p>'
        "</div>"
        "<div><h3>Services</h3><ul>{services}</ul></div>"
        "<div><h3>Company</h3><ul>{company}</ul></div>"
        "<div><h3>Get in touch</h3><ul>"
        '<li><a href="tel:{tel}">{phone}</a></li>'
        '<li><a href="mailto:{mail}">{mail}</a></li>'
        "<li>{street},<br>{town}, {pc}</li>"
        "</ul><h3 style=\"margin-top:1.5rem\">Opening hours</h3>"
        "<ul>{hours}</ul></div>"
        "</div>"
        '<div class="footer__legal">'
        "<p>{legal} trading as {name}. Registered in England &amp; Wales, "
        "company number {cno}. Registered office: {office}. "
        "Gas Safe register number {gs}.</p>"
        '<p><a href="{r}legal/privacy-policy/">Privacy policy</a> · '
        '<a href="{r}legal/terms-of-service/">Terms of service</a> · '
        '<a href="{r}legal/cookie-policy/">Cookie policy</a> · '
        '<a href="{r}sitemap.xml">Sitemap</a></p>'
        "<p>&copy; {year} {legal}. All rights reserved.</p>"
        "</div></div></footer>"
    ).format(
        r=r, name=e(C.BUSINESS["name"]), legal=e(C.BUSINESS["legal_name"]),
        fb=e(C.BUSINESS["facebook"]), services=services, company=company,
        tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]),
        mail=e(C.BUSINESS["email"]), street=e(C.BUSINESS["street"]),
        town=e(C.BUSINESS["town"]), pc=e(C.BUSINESS["postcode"]),
        hours=hours, cno=e(C.BUSINESS["company_number"]),
        office=e(C.BUSINESS["registered_office"]),
        gs=e(C.BUSINESS["gas_safe_number"]), year=BUILD_DATE[:4],
    )


def glass_defs(r: str) -> str:
    """Inline SVG filters that give the glass surfaces genuine refraction.

    Each one displaces the backdrop per pixel using a pre-baked map whose red
    and green channels encode the offset (see tools/make_glass_maps.py), so
    content behind a glass panel bends at the rim instead of merely blurring.
    Referenced from CSS as `backdrop-filter: ... url(#eh-glass-bar)`.
    """
    def one(name, image, scale):
        return (
            '<filter id="eh-glass-{n}" filterUnits="objectBoundingBox" '
            'primitiveUnits="objectBoundingBox" x="0" y="0" width="1" '
            'height="1" color-interpolation-filters="sRGB">'
            '<feImage href="{r}assets/img/{img}" x="0" y="0" width="1" '
            'height="1" preserveAspectRatio="none" result="map"/>'
            '<feDisplacementMap in="SourceGraphic" in2="map" scale="{s}" '
            'xChannelSelector="R" yChannelSelector="G"/>'
            "</filter>"
        ).format(n=name, r=r, img=image, s=scale)

    return (
        '<svg class="visually-hidden" aria-hidden="true" focusable="false" '
        'width="0" height="0"><defs>{bar}{card}</defs></svg>'
    ).format(bar=one("bar", "glass-bar.png", "0.045"),
             card=one("card", "glass-card.png", "0.06"))


def crumbs(r: str, trail: list[tuple[str, str]]) -> str:
    if not trail:
        return ""
    items = ['<li><a href="{r}index.html">Home</a></li>'.format(r=r)]
    for i, (label, path) in enumerate(trail):
        last = i == len(trail) - 1
        if last or not path:
            items.append("<li>{}</li>".format(e(label)))
        else:
            items.append('<li><a href="{r}{p}">{l}</a></li>'.format(
                r=r, p=path, l=e(label)))
    return ('<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">'
            "<ol>{}</ol></div></nav>".format("".join(items)))


def cta_band(r: str, title: str, text: str) -> str:
    return (
        '<section class="section section--ink"><div class="wrap">'
        '<h2>{t}</h2><p style="max-width:44em">{x}</p>'
        '<div class="btn-row">'
        '<a class="btn btn--primary" href="tel:{tel}">{p}Call {phone}</a>'
        '<a class="btn btn--on-dark" href="{r}contact/">Request a free quote</a>'
        "</div></div></section>"
    ).format(t=e(title), x=e(text), tel=C.BUSINESS["phone_e164"],
             p=icon("phone"), phone=e(C.BUSINESS["phone"]), r=r)


def photo(r: str, filename: str, alt: str, caption: str = "",
          wide: bool = False) -> str:
    """Render a supplied photograph, or a branded panel where none exists yet.

    Never substitutes stock imagery for EcoHeat's own work.
    """
    path = os.path.join(ROOT, "assets", "img", "photos", filename)
    if os.path.exists(path):
        cap = ('<figcaption>%s</figcaption>' % e(caption)) if caption else ""
        return (
            '<figure class="figure">'
            '<img src="{r}assets/img/photos/{f}" alt="{a}" loading="lazy" '
            'decoding="async">{cap}</figure>'
        ).format(r=r, f=e(filename), a=e(alt), cap=cap)
    return (
        '<div class="photo-slot{w}" role="img" aria-label="{a}">'
        "{i}<b>Photograph to follow</b><span>{a}</span></div>"
    ).format(w=" photo-slot--wide" if wide else "", a=e(alt),
             i=icon("camera"))


def ticks(items, cross: bool = False) -> str:
    if not items:
        return ""
    li = "".join("<li>{i}<span>{t}</span></li>".format(
        i=icon("check" if not cross else "alert"), t=e(t)) for t in items)
    return '<ul class="ticks{c}">{li}</ul>'.format(
        c=" crosses" if cross else "", li=li)


def faq_block(slugs) -> str:
    rows = []
    for slug in slugs:
        q, a = C.FAQ_INDEX[slug]
        rows.append(
            "<details><summary>{q}</summary>"
            '<div class="faq__a"><p>{a}</p></div></details>'.format(
                q=e(q), a=e(a))
        )
    return '<div class="faq">{}</div>'.format("".join(rows))


# --------------------------------------------------------------------------
# structured data
# --------------------------------------------------------------------------

def local_business_schema() -> str:
    b = C.BUSINESS
    hours = ", ".join(
        '{{"@type":"OpeningHoursSpecification","dayOfWeek":[{d}],'
        '"opens":"{o}","closes":"{c}"}}'.format(
            d=",".join('"%s"' % x for x in h["days"]), o=h["opens"],
            c=h["closes"])
        for h in b["opening_schema"]
    )
    return (
        '{{"@context":"https://schema.org","@type":"Plumber",'
        '"@id":"{url}/#business","name":"{name}","legalName":"{legal}",'
        '"url":"{url}/","telephone":"{tel}","email":"{mail}",'
        '"image":"{url}/assets/img/og-image.jpg",'
        '"logo":"{url}/assets/img/ecoheat-logo.png",'
        '"priceRange":"££","currenciesAccepted":"GBP",'
        '"paymentAccepted":"Bank transfer, Card, Cash, Finance",'
        '"address":{{"@type":"PostalAddress","streetAddress":"{street}",'
        '"addressLocality":"{town}","addressRegion":"{county}",'
        '"postalCode":"{pc}","addressCountry":"GB"}},'
        '"geo":{{"@type":"GeoCoordinates","latitude":"{lat}",'
        '"longitude":"{lon}"}},'
        '"openingHoursSpecification":[{hours}],'
        '"areaServed":[{areas}],'
        '"sameAs":["{fb}"],'
        '"identifier":[{{"@type":"PropertyValue","name":"Gas Safe register",'
        '"value":"{gs}"}},{{"@type":"PropertyValue",'
        '"name":"Companies House","value":"{cno}"}}],'
        '"hasOfferCatalog":{{"@type":"OfferCatalog","name":"Services",'
        '"itemListElement":[{cat}]}}}}'
    ).format(
        url=C.SITE_URL, name=b["name"], legal=b["legal_name"],
        tel=b["phone_e164"], mail=b["email"], street=b["street"],
        town=b["town"], county=b["county"], pc=b["postcode"],
        lat=b["lat"], lon=b["lon"], hours=hours,
        areas=",".join('{"@type":"Place","name":"%s"}' % a for a in C.AREAS),
        fb=b["facebook"], gs=b["gas_safe_number"], cno=b["company_number"],
        cat=",".join(
            '{{"@type":"Offer","itemOffered":{{"@type":"Service","name":"{n}",'
            '"url":"{u}/services/{s}/"}}}}'.format(
                n=s["nav"], u=C.SITE_URL, s=s["slug"])
            for s in C.SERVICES),
    )


def breadcrumb_schema(path: str, trail) -> str:
    items = [('{{"@type":"ListItem","position":1,"name":"Home",'
              '"item":"{}/"}}').format(C.SITE_URL)]
    for i, (label, p) in enumerate(trail, start=2):
        items.append(
            '{{"@type":"ListItem","position":{i},"name":"{n}",'
            '"item":"{u}/{p}"}}'.format(i=i, n=label, u=C.SITE_URL,
                                        p=p or path))
    return ('{{"@context":"https://schema.org","@type":"BreadcrumbList",'
            '"itemListElement":[{}]}}').format(",".join(items))


def service_schema(s) -> str:
    return (
        '{{"@context":"https://schema.org","@type":"Service",'
        '"name":"{n}","serviceType":"{n}",'
        '"url":"{u}/services/{slug}/","description":"{d}",'
        '"provider":{{"@id":"{u}/#business"}},'
        '"areaServed":[{areas}]}}'
    ).format(n=s["nav"], u=C.SITE_URL, slug=s["slug"],
             d=s["meta"].replace('"', "'"),
             areas=",".join('{"@type":"Place","name":"%s"}' % a
                            for a in C.AREAS[:10]))


def faq_schema() -> str:
    qs = []
    for _title, items in C.FAQ_GROUPS:
        for _slug, q, a in items:
            qs.append(
                '{{"@type":"Question","name":"{q}",'
                '"acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}'.format(
                    q=q.replace('"', "'"), a=a.replace('"', "'")))
    return ('{{"@context":"https://schema.org","@type":"FAQPage",'
            '"mainEntity":[{}]}}').format(",".join(qs))


# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------

PAGES = []  # populated by page() -- drives the sitemap and the link checker

# Non-HTML files the build also emits; the link checker treats these as valid
# targets even on a clean checkout where they do not exist yet.
EXTRA_OUTPUT = {"sitemap.xml", "robots.txt", "llms.txt"}


def page(path, title, meta, body, trail=None, schema=None, priority="0.6",
         changefreq="monthly", noindex=False, in_sitemap=True):
    """Assemble one HTML document. ``path`` is like 'services/index.html'."""
    depth = path.count("/")
    r = rel(depth)
    canonical = C.SITE_URL + "/" + (
        "" if path == "index.html" else path.replace("index.html", ""))
    current = "" if path == "index.html" else path.replace("index.html", "")

    blocks = [local_business_schema()]
    if trail:
        blocks.append(breadcrumb_schema(current, trail))
    if schema:
        blocks.append(schema)
    if path == "index.html":
        blocks.append(
            '{{"@context":"https://schema.org","@type":"WebSite",'
            '"name":"{n}","url":"{u}/"}}'.format(n=C.BUSINESS["name"],
                                                 u=C.SITE_URL))
    ld = "".join(
        '<script type="application/ld+json">%s</script>' % b for b in blocks)

    doc = """<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="{canonical}">
{robots}<meta name="theme-color" content="#14171a">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/img/og-image.jpg">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<link rel="stylesheet" href="{r}assets/css/main.css">
{ld}
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
{defs}
<div class="progress" aria-hidden="true"><div class="progress__bar"></div></div>
{header}
<main id="main">
{crumbs}
{body}
</main>
{footer}
<script src="{r}assets/js/site.js" defer></script>
<script src="{r}assets/js/motion.js" defer></script>
{gl}</body>
</html>
""".format(
        defs=glass_defs(r),
        gl=("".join('<script src="%sassets/js/%s" defer></script>\n' % (r, f)
                    for f in ("particles.js", "audio.js", "physics.js"))
            if path == "index.html" else ""),
        title=e(title), meta=e(meta), canonical=canonical, name=e(C.BUSINESS["name"]),
        site=C.SITE_URL, r=r, ld=ld, header=header(r, current),
        crumbs=crumbs(r, trail or []), body=body, footer=footer(r),
        robots='<meta name="robots" content="noindex, follow">\n' if noindex else "",
    )

    PAGES.append({"path": path, "title": title, "meta": meta, "html": doc,
                  "priority": priority, "changefreq": changefreq,
                  "canonical": canonical, "in_sitemap": in_sitemap and not noindex})
    return doc


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_home():
    r = ""

    # Three services on the home page, not six. The rest are one click away.
    lead = ["boiler-installation", "air-source-heat-pumps",
            "plumbing-and-bathrooms"]
    cards = "".join(
        '<a class="card card--link" href="services/{s}/">'
        '<div class="card__icon">{i}</div><h3>{n}</h3><p>{d}</p>'
        '<span class="card__more">Read more</span></a>'.format(
            s=x["slug"], i=icon(x["icon"]), n=e(x["nav"]), d=e(x["summary"]))
        for x in (SERVICE_BY_SLUG[k] for k in lead)
    )

    body = """
<section class="hero">
<div class="hero__canvas" aria-hidden="true"><canvas id="hero-gl"></canvas></div>
<div class="hero__scrim" aria-hidden="true"></div>
<div class="wrap"><div class="hero__inner">
<span class="eyebrow">Gas Safe registered &middot; Somerset</span>
<h1>Warm homes,<br>done properly</h1>
<p class="hero__lede">Boilers, air source heat pumps and bathrooms across
Somerset and North Somerset. Fixed prices in writing, and the engineer who
quotes the job is the engineer who does it.</p>
<div class="btn-row">
<a class="btn btn--primary" href="contact/">Book a free survey</a>
<a class="btn btn--on-dark" href="tel:{tel}">{ph}{phone}</a>
</div>
</div></div>
</section>

<section class="section" id="what-we-do"><div class="wrap">
<div class="sechead">
<span class="sechead__no">01</span>
<div><span class="eyebrow">What we do</span><h2>Three things, done well</h2></div>
</div>
<div class="grid grid-3">{cards}</div>
<p class="sechead__more"><a href="services/">Every service we offer</a></p>
</div></section>

<section class="section section--ink" id="renewables"><div class="wrap">
<div class="sechead">
<span class="sechead__no">02</span>
<div><span class="eyebrow">Renewables</span>
<h2>The grant pays {grant}. We do the paperwork.</h2></div>
</div>
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div>
<p>The Boiler Upgrade Scheme pays {grant} towards an air source heat pump on
eligible properties. We apply on your behalf and take it straight off your
quote &mdash; you never fund it yourself and claim it back.</p>
<p>Everything starts with a room-by-room heat loss survey, because that is what
decides whether a heat pump will heat your home cheaply. Free, and yours to keep
either way.</p>
<div class="btn-row" style="margin-top:1.5rem">
<a class="btn btn--primary" href="grants/">How the grant works</a>
<a class="btn btn--on-dark" href="services/air-source-heat-pumps/">Heat pumps</a>
</div>
</div>
<dl class="figures">
<div><dt>Grant available</dt><dd data-count="7500" data-prefix="£">{grant}</dd></div>
<div><dt>Survey cost</dt><dd>Free</dd></div>
<div><dt>Typical flow temp we design to</dt><dd>45&deg;C</dd></div>
<div><dt>VAT on heat pumps</dt><dd>0%</dd></div>
</dl>
</div>
</div></section>

<section class="section" id="how-we-work"><div class="wrap">
<div class="sechead">
<span class="sechead__no">03</span>
<div><span class="eyebrow">How we work</span><h2>No salespeople. Ever.</h2></div>
</div>
<ol class="steps">
<li><h3>You speak to an engineer</h3><p>Not a call centre. You get a straight
answer about whether it is something we do and what is involved.</p></li>
<li><h3>We survey, free of charge</h3><p>Heat loss room by room for heat pumps,
gas rate and system condition for boilers. Measured, not guessed.</p></li>
<li><h3>One fixed written price</h3><p>Itemised, valid 30 days, with any grant
already deducted. Extras only ever with your agreement first.</p></li>
<li><h3>The same engineer fits it</h3><p>On the agreed dates, property
protected, cleared up each day, commissioned and handed over before we
invoice.</p></li>
</ol>
</div></section>

<section class="section section--ink yard" id="the-yard" hidden><div class="wrap">
<div class="sechead">
<span class="sechead__no">04</span>
<div><span class="eyebrow">The yard</span><h2>Have a drive around</h2></div>
</div>
<p class="yard__intro">Our stock, our van, and a physics engine written for this
page. Drive with the arrow keys, hop with up, hold shift to boost, and click
anywhere to send it all flying.</p>
<div class="yard__stage">
<canvas id="yard" width="1200" height="440" role="img"
 aria-label="An illustration of the EcoHeat yard: a branded van beside a stack
 of cylinders, radiators, boilers and heat pump units resting on the ground.
 Interactive when started."></canvas>
<button class="yard__start btn btn--primary" type="button" data-yard-start>
Start the yard</button>
</div>
<div class="yard__bar">
<p class="yard__keys"><kbd>&larr;</kbd><kbd>&rarr;</kbd> drive
&middot; <kbd>&uarr;</kbd> hop &middot; <kbd>shift</kbd> boost
&middot; <kbd>esc</kbd> stop</p>
<div class="yard__btns">
<button class="btn btn--on-dark btn--sm" type="button" data-yard-sound
 aria-pressed="false">{spk}<span data-label>Sound off</span></button>
<button class="btn btn--on-dark btn--sm" type="button" data-yard-reset>
Reset</button>
</div>
</div>
<p class="visually-hidden" role="status" data-yard-live></p>
<p class="yard__note">A toy, but an honest one: every crate has a mass, so the
heavy stock barely moves and the light stock goes flying. Same arithmetic we use
to size a heat pump &mdash; just with worse consequences.</p>
</div></section>

<section class="section" id="contact"><div class="wrap">
<div class="sechead">
<span class="sechead__no">05</span>
<div><span class="eyebrow">Get in touch</span><h2>Tell us what you need</h2></div>
</div>
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div>
<p>Free surveys and fixed written quotes across Somerset and North Somerset.
No pressure, no obligation, no charge.</p>
<div class="btn-row" style="margin-top:1.5rem">
<a class="btn btn--primary" href="contact/">Request a survey</a>
<a class="btn btn--ghost" href="tel:{tel}">{ph}{phone}</a>
</div>
</div>
<dl class="figures figures--light">
<div><dt>Gas Safe register</dt><dd>{gs}</dd></div>
<div><dt>Based at</dt><dd>Edingworth</dd></div>
<div><dt>Company number</dt><dd>{cno}</dd></div>
<div><dt>Quotes valid for</dt><dd>30 days</dd></div>
</dl>
</div>
</div></section>
""".format(
        tel=C.BUSINESS["phone_e164"], ph=icon("phone"),
        phone=e(C.BUSINESS["phone"]), cards=cards, grant=C.BUS_GRANT,
        gs=e(C.BUSINESS["gas_safe_number"]),
        cno=e(C.BUSINESS["company_number"]),
        spk=icon("sound"),
    )

    page("index.html",
         "Plumbing, Heating & Heat Pumps in Somerset | EcoHeat",
         "Gas Safe registered plumbing, heating and air source heat pumps "
         "across Somerset and North Somerset. Free surveys, fixed prices and "
         "the {} heat pump grant handled for you.".format(C.BUS_GRANT),
         body, priority="1.0", changefreq="weekly")


def build_services_index():
    r = "../"
    cards = "".join(
        '<a class="card card--link" href="{s}/">'
        '<div class="card__icon">{i}</div><h3>{n}</h3><p>{d}</p>'
        '<span class="card__more">Read more</span></a>'.format(
            s=s["slug"], i=icon(s["icon"]), n=e(s["h1"]), d=e(s["summary"]))
        for s in C.SERVICES
    )
    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Services</span>
<h1>Plumbing, heating and renewable energy services</h1>
<p class="lede">Everything EcoHeat does, from a leaking tap in Burnham-on-Sea to
a full air source heat pump conversion in Taunton — carried out by Gas Safe
registered engineers and quoted at a fixed price before we start.</p>
</div></div>

<section class="section"><div class="wrap">
<h2>Choose a service</h2>
<div class="grid grid-3" style="margin-top:1.5rem">{cards}</div>
</div></section>

<section class="section section--surface"><div class="wrap narrow">
<h2>What is always included</h2>
{inc}
</div></section>
""".format(cards=cards,
           inc=ticks([
               "A free survey before any installation quote",
               "A fixed written price, itemised, valid 30 days",
               "Gas Safe registered engineers on every gas job",
               "Building Regulations notification where required",
               "Manufacturer warranty registered on your behalf",
               "Full clear-up and a handover before we invoice",
           ]))
    body += cta_band(r, "Tell us what you need",
                     "Free surveys across Somerset and North Somerset, with a "
                     "fixed written quote before any work starts.")

    page("services/index.html",
         "Our Services | Plumbing, Heating & Renewables | EcoHeat Somerset",
         "Boiler installation, servicing and repair, air source heat pumps, "
         "bathrooms, general plumbing and emergency call-outs across Somerset "
         "and North Somerset.",
         body, trail=[("Services", "services/")], priority="0.9",
         changefreq="monthly")


def build_service(s):
    r = "../../"
    sections = "".join(
        "<h2>{t}</h2><p>{b}</p>".format(t=e(t), b=e(b)) for t, b in s["body"])

    related = []
    for slug in s["related"]:
        if slug in SERVICE_BY_SLUG:
            o = SERVICE_BY_SLUG[slug]
            related.append((o["nav"], "../%s/" % slug, o["summary"],
                            o["icon"]))
        else:
            name, desc = EXTRA_LINKS[slug]
            related.append((name, "../../%s/" % slug, desc, "pound"))
    rel_cards = "".join(
        '<a class="card card--link" href="{p}">'
        '<div class="card__icon">{i}</div><h3>{n}</h3><p>{d}</p>'
        '<span class="card__more">Read more</span></a>'.format(
            p=p, i=icon(ic), n=e(n), d=e(d)) for n, p, d, ic in related)

    plans_html = ""
    if s["slug"] == "annual-service-plans":
        plans_html = (
            '<section class="section section--surface"><div class="wrap">'
            "<h2>Compare the plans</h2>"
            '<p style="max-width:44em;color:var(--text-soft)">All three plans '
            "can be paid monthly by Direct Debit or annually in one payment. "
            "Annual payment saves the equivalent of one monthly instalment.</p>"
            '<div class="plans" style="margin-top:2rem">{}</div>'
            '<p class="form__note" style="margin-top:1.5rem">Plans run for 12 '
            "months and renew only with your agreement. Cancel any time with 30 "
            "days' notice — no exit fee. Full terms are in our "
            '<a href="../../legal/terms-of-service/">terms of service</a>.</p>'
            "</div></section>"
        ).format(plan_cards())

    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">{eyebrow}</span>
<h1>{h1}</h1>
<p class="lede">{intro}</p>
</div></div>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div class="prose">{sections}</div>
<div>
{pic}
{blist}
<div class="callout"><h3>Free survey, fixed price</h3>
<p>Call <a href="tel:{tel}">{phone}</a> or
<a href="../../contact/">send an enquiry</a> and we will arrange a visit at a
time that suits you.</p></div>
</div>
</div>
</div></section>
{plans}
<section class="section{surface}"><div class="wrap narrow">
<h2>Questions about {lower}</h2>
{faqs}
<p style="margin-top:1.5rem"><a href="../../faq/">See all frequently asked questions</a></p>
</div></section>

<section class="section section--surface"><div class="wrap">
<h2>Related services</h2>
<div class="grid grid-3" style="margin-top:1.5rem">{related}</div>
</div></section>
""".format(
        eyebrow=e(s["nav"]), h1=e(s["h1"]), intro=e(s["intro"]),
        sections=sections,
        pic=photo(r, "%s.jpg" % s["slug"],
                  "EcoHeat engineer carrying out %s work at a Somerset property"
                  % s["nav"].lower()),
        blist=("<h3 style=\"margin-top:1.75rem\">What we cover</h3>%s"
               % ticks(s["bullets"])) if s["bullets"] else "",
        tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]),
        plans=plans_html, surface="" if plans_html else " section--surface",
        lower=e(s["nav"].lower()), faqs=faq_block(s["faq_slugs"]),
        related=rel_cards,
    )
    body += cta_band(r, "Book a free survey",
                     "Somerset and North Somerset covered, seven days a week "
                     "for emergencies.")

    page("services/%s/index.html" % s["slug"], s["title"], s["meta"], body,
         trail=[("Services", "services/"), (s["nav"], "services/%s/" % s["slug"])],
         schema=service_schema(s), priority="0.8")


def plan_cards() -> str:
    out = []
    for p in C.PLANS:
        if p["monthly"] is not None:
            price = ('<b>£{m}</b><span class="per">/month</span>'
                     '<span class="alt">or £{a} a year, paid in one payment'
                     "</span>").format(m=p["monthly"], a=p["annual"])
        else:
            # No figure is published until EcoHeat has approved one.
            price = ('<span class="tbc">Call for price</span>'
                     '<span class="alt">Monthly by Direct Debit or annually '
                     "in one payment</span>")
        out.append(
            '<div class="plan{f}">{flag}'
            "<h3>{n}</h3>"
            '<p class="plan__for">{for_}</p>'
            '<div class="plan__price">{price}</div>'
            "<h4>What is included</h4>{inc}"
            "<h4>What is not included</h4>{exc}"
            '<a class="btn btn--{btn}" href="../../contact/?enquiry=service-plan">'
            "Ask about {n}</a></div>".format(
                f=" plan--featured" if p["featured"] else "",
                flag='<span class="plan__flag">Most popular</span>'
                     if p["featured"] else "",
                n=e(p["name"]), for_=e(p["for"]), price=price,
                inc=ticks(p["includes"]), exc=ticks(p["excludes"], cross=True),
                btn="primary" if p["featured"] else "ghost"))
    return "".join(out)


def build_grants():
    r = "../"
    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Grants &amp; funding</span>
<h1>The {grant} Boiler Upgrade Scheme grant explained</h1>
<p class="lede">The government pays {grant} towards an air source heat pump on
eligible properties in England and Wales. We check whether you qualify, apply on
your behalf, and take the grant off your quote.</p>
</div></div>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div class="prose">
<h2>What the grant is worth</h2>
<p>The Boiler Upgrade Scheme (BUS) is administered by Ofgem. It currently pays
<strong>{grant}</strong> towards an air source heat pump and the same amount
towards a ground source heat pump. It is a grant, not a loan: there is nothing
to repay.</p>
<p>Crucially, the money is claimed by the installer, not the householder. That
means you never have to find {grant} up front and wait to be reimbursed — it is
deducted from your quotation, and you pay the balance.</p>

<h2>Who is eligible</h2>
<p>Your property normally qualifies if all of the following are true:</p>
<ul>
<li>It is a domestic property in England or Wales.</li>
<li>It has a valid Energy Performance Certificate with no outstanding
recommendations for loft or cavity wall insulation.</li>
<li>You are replacing a fossil fuel system — mains gas, oil, LPG or electric
heating.</li>
<li>The property is not a new build (with limited exceptions for self-builds).</li>
<li>The installation is carried out to MCS standards by an MCS-certified
installer.</li>
</ul>
<p>We check your EPC and confirm eligibility in writing before you commit to
anything. If you do not qualify, we will tell you at that point rather than
after the survey.</p>

<h2>How we handle the application</h2>
<ol>
<li><strong>Eligibility check.</strong> We look up your EPC and confirm the
property qualifies.</li>
<li><strong>Heat loss survey.</strong> Room by room, free of charge, producing
the design flow temperature and the emitter schedule.</li>
<li><strong>Quotation.</strong> Fixed price, itemised, with the {grant} already
deducted.</li>
<li><strong>Voucher application.</strong> We apply to Ofgem and you confirm the
application by email — this is the only step that needs you.</li>
<li><strong>Installation and commissioning.</strong> Certified to MCS standards
and registered on the MCS database.</li>
<li><strong>Redemption.</strong> We redeem the voucher. You have already had the
benefit, so nothing further is due from you.</li>
</ol>

<h2>{mcs_head}</h2>
<p>{mcs}</p>

<h2>Other funding worth checking</h2>
<p>The Boiler Upgrade Scheme is the main one, but depending on your
circumstances you may also be eligible for:</p>
<ul>
<li><strong>ECO4</strong> — support for households on qualifying benefits or in
low-EPC properties, delivered through energy suppliers.</li>
<li><strong>Great British Insulation Scheme</strong> — insulation measures that
can also bring an EPC up to the standard the heat pump grant requires.</li>
<li><strong>0% VAT</strong> — heat pumps, solar thermal and related energy
saving materials currently attract zero-rated VAT on installation in domestic
properties.</li>
</ul>
<p>If a grant will not cover it, <a href="../finance/">finance is available</a>
on qualifying installations.</p>
</div>
<div>
{pic}
<div class="callout" style="margin-top:1.5rem"><h3>Free eligibility check</h3>
<p>Send us your postcode and we will look up your EPC and tell you where you
stand — no visit required, no obligation.</p>
<p><a class="btn btn--primary" href="../contact/?enquiry=heat-pump">Check my eligibility</a></p>
</div>
<div class="callout callout--amber"><h3>Grant rules change</h3>
<p>Scheme values and eligibility criteria are set by government and can be
revised. We confirm the current position in writing with your quotation. The
authoritative source is Ofgem's Boiler Upgrade Scheme guidance.</p></div>
</div>
</div>
</div></section>

<section class="section section--surface"><div class="wrap narrow">
<h2>Grant questions</h2>
{faqs}
</div></section>
""".format(
        grant=C.BUS_GRANT,
        mcs_head="Our MCS certification" if C.MCS_STATUS == "own"
                 else "MCS accreditation and your grant",
        mcs=e(C.MCS_ANSWER),
        pic=photo(r, "heat-pump-survey.jpg",
                  "EcoHeat engineer carrying out a room-by-room heat loss "
                  "survey before a heat pump installation"),
        faqs=faq_block(["heat-pump-grant", "heat-pump-eligible",
                        "heat-pump-cost", "mcs", "heat-pump-cold"]),
    )
    body += cta_band(r, "Find out what you would pay",
                     "A free survey and a fixed written price with the grant "
                     "already deducted.")

    page("grants/index.html",
         "£7,500 Heat Pump Grant Somerset | Boiler Upgrade Scheme | EcoHeat",
         "How the {} Boiler Upgrade Scheme grant works, who is eligible, and "
         "how EcoHeat applies on your behalf so the grant comes straight off "
         "your quote.".format(C.BUS_GRANT),
         body, trail=[("Grants", "grants/")], priority="0.9")


def build_finance():
    r = "../"
    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Finance</span>
<h1>Finance options for boilers, heat pumps and bathrooms</h1>
<p class="lede">Nobody plans for a boiler to fail. Finance lets you spread the
cost of an installation over a term that suits you, with a fixed monthly payment
agreed before any work starts.</p>
</div></div>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div class="prose">
<h2>What we offer</h2>
<p>Finance is available on qualifying installations — typically boiler
replacements, heat pump installations and full bathroom refits — through an
FCA-authorised finance provider. Depending on the value of the work and the term
you choose, options normally include:</p>
<div class="table-scroll">
<table>
<thead><tr><th>Option</th><th>Typical term</th><th>How it works</th></tr></thead>
<tbody>
<tr><td>Interest-free credit</td><td>12–24 months</td>
<td>Deposit plus equal monthly payments. Nothing to pay in interest if the
balance is cleared within the term.</td></tr>
<tr><td>Buy now, pay later</td><td>Deferred 6–12 months</td>
<td>Settle in full within the deferral period and pay no interest; otherwise
the balance converts to an interest-bearing plan.</td></tr>
<tr><td>Extended credit</td><td>3–10 years</td>
<td>Fixed monthly payments over a longer term at the provider's standard rate.
Useful for heat pump installations where the monthly payment is offset against
running-cost savings.</td></tr>
</tbody>
</table>
</div>
<p>All applications are subject to status and affordability checks, and the
credit agreement is between you and the finance provider, not EcoHeat.</p>

<h2>How to apply</h2>
<ol>
<li>We survey the property and issue a fixed written quotation.</li>
<li>You choose a deposit and a term; we show you the exact monthly payment and
the total amount repayable before you decide.</li>
<li>You apply online with the provider. A decision usually takes minutes.</li>
<li>Once approved, we book the installation. The provider pays us on completion,
after you have confirmed you are happy with the work.</li>
</ol>

<h2>Finance and the heat pump grant</h2>
<p>The two work together. The <a href="../grants/">{grant} Boiler Upgrade Scheme
grant</a> is deducted from the quotation first, and finance is arranged on the
balance — so you are only ever financing what you actually have to pay.</p>

<h2>Before you commit</h2>
<p>Credit is not right for everyone. Borrowing over a long term costs more
overall than paying up front, missed payments can affect your credit file, and
the goods are not security for the loan but the debt is still enforceable. We
will always show you the total amount repayable alongside the monthly figure so
you are comparing like with like. If paying outright is better for you, we will
say so.</p>
</div>
<div>
<div class="callout"><h3>Talk it through first</h3>
<p>Ring <a href="tel:{tel}">{phone}</a> and we will tell you whether the job
qualifies for finance and what the realistic monthly figure looks like, before
you apply for anything.</p>
<p><a class="btn btn--primary" href="../contact/?enquiry=finance">Ask about finance</a></p>
</div>
{req}
</div>
</div>
</div></section>
""".format(
        grant=C.BUS_GRANT, tel=C.BUSINESS["phone_e164"],
        phone=e(C.BUSINESS["phone"]),
        req=('<div class="callout callout--amber"><h3>Credit information</h3>'
             "<p>Finance is provided by an FCA-authorised third-party lender "
             "and is subject to status, affordability and a minimum spend. "
             "Representative APR, deposit requirements and the total amount "
             "repayable are shown on your written quotation and on the "
             "provider's credit agreement before you sign anything.</p>"
             "<p><strong>Before launch:</strong> once the finance provider is "
             "appointed, add their name, FCA firm reference number, EcoHeat's "
             "own credit broker permission or exemption, and the representative "
             "example here. Consumer credit promotions must comply with FCA "
             "CONC 3.</p></div>"),
    )
    body += cta_band(r, "Get a quote with finance figures",
                     "Fixed price, monthly payment and total repayable, all in "
                     "writing before you commit.")

    page("finance/index.html",
         "Boiler & Heat Pump Finance Options | EcoHeat Somerset",
         "Spread the cost of a boiler, heat pump or bathroom installation with "
         "finance from an FCA-authorised provider. Interest-free and extended "
         "terms, subject to status.",
         body, trail=[("Finance", "finance/")], priority="0.7")


def build_projects():
    r = "../"
    blocks = []
    for cs in C.CASE_STUDIES:
        # Photo lists are ordered before, then after.
        labels = ["Before", "After"]
        pics = "".join(
            '<div><p class="eyebrow">{lab}</p>{img}</div>'.format(
                lab=e(labels[i] if i < len(labels) else "Detail"),
                img=photo(r, f, alt))
            for i, (f, alt) in enumerate(cs["photos"]))
        blocks.append("""
<article class="section" id="{slug}" style="border-bottom:1px solid var(--line)">
<div class="wrap">
<span class="eyebrow">{type} · {loc}</span>
<h2>{title}</h2>
<p style="max-width:44em;font-size:1.1rem"><strong>{summary}</strong></p>
<div class="grid grid-2" style="gap:1.5rem;margin:1.75rem 0">{pics}</div>
<div class="grid grid-3" style="gap:2rem">
<div><h3>The challenge</h3><p>{challenge}</p></div>
<div><h3>What we did</h3><p>{solution}</p></div>
<div><h3>The outcome</h3><p>{outcome}</p></div>
</div>
</div>
</article>""".format(
            slug=cs["slug"], type=e(cs["type"]), loc=e(cs["location"]),
            title=e(cs["title"]), summary=e(cs["summary"]),
            challenge=e(cs["challenge"]), solution=e(cs["solution"]),
            outcome=e(cs["outcome"]), pics=pics))

    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Our work</span>
<h1>Projects and case studies</h1>
<p class="lede">Installations we have carried out across Somerset and North
Somerset, written up honestly — including the problems we found along the way and
how they were solved.</p>
</div></div>
{blocks}
<section class="section section--surface"><div class="wrap narrow" style="text-align:center">
<h2>Your project could be next</h2>
<p>Every job on this page started with a free survey and a fixed written price.
Photographs are published only with the customer's permission.</p>
<div class="btn-row" style="justify-content:center">
<a class="btn btn--primary" href="../contact/">Request a free survey</a>
<a class="btn btn--ghost" href="{fb}" rel="noopener">See more on Facebook</a>
</div>
</div></section>
""".format(blocks="".join(blocks), fb=e(C.BUSINESS["facebook"]))

    page("projects/index.html",
         "Projects & Case Studies | EcoHeat Somerset",
         "Real EcoHeat installations across Somerset — oil to heat pump "
         "conversions, back boiler removals and bathroom refits, with the "
         "challenge, the fix and the outcome.",
         body, trail=[("Projects", "projects/")], priority="0.8")


def build_reviews():
    r = "../"
    if C.REVIEWS:
        items = "".join(
            '<figure class="card"><div class="card__icon">{st}</div>'
            "<blockquote><p>{t}</p></blockquote>"
            "<figcaption><strong>{n}</strong><br>{l} · {s}</figcaption>"
            "</figure>".format(st=icon("star"), t=e(rv["text"]),
                               n=e(rv["name"]), l=e(rv["location"]),
                               s=e(rv["source"]))
            for rv in C.REVIEWS)
        reviews_block = '<div class="grid grid-3">%s</div>' % items
    else:
        reviews_block = """
<div class="callout"><h3>Reviews are published here as they come in</h3>
<p>EcoHeat is a young company and we would rather show you nothing than show you
testimonials we have written ourselves. Genuine reviews from customers appear on
our Facebook page today, and will be published here — with the customer's
permission — as they are received.</p>
<p><a class="btn btn--primary" href="{fb}" rel="noopener">Read reviews on Facebook</a></p>
</div>""".format(fb=e(C.BUSINESS["facebook"]))

    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Reviews</span>
<h1>What our customers say</h1>
<p class="lede">Honest feedback from households across Somerset and North
Somerset.</p>
</div></div>

<section class="section"><div class="wrap">
<h2>Reviews</h2>
<div style="margin-top:1.5rem">{reviews}</div>
</div></section>

<section class="section section--surface"><div class="wrap">
<div class="grid grid-2" style="gap:3rem">
<div>
<h2>Leave us a review</h2>
<p>If we have worked for you, a few lines makes a real difference to a small
local firm — and it helps the next person in your village decide who to trust
with their heating.</p>
<p>You can review us on our
<a href="{fb}" rel="noopener">Facebook page</a>. We never offer incentives in
exchange for reviews and we never write them ourselves.</p>
</div>
<div>
<h2>Something not right?</h2>
<p>Tell us before you tell the internet and we will put it right. Call
<a href="tel:{tel}">{phone}</a> or email
<a href="mailto:{mail}">{mail}</a> and it goes straight to the person who ran
your job. Our full complaints procedure is in our
<a href="../legal/terms-of-service/#complaints">terms of service</a>.</p>
</div>
</div>
</div></section>
""".format(reviews=reviews_block, fb=e(C.BUSINESS["facebook"]),
           tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]),
           mail=e(C.BUSINESS["email"]))
    body += cta_band(r, "Join them", "Free surveys and fixed written quotes "
                                     "across Somerset and North Somerset.")

    page("reviews/index.html",
         "Customer Reviews | EcoHeat Plumbing and Renewables Somerset",
         "Genuine customer reviews for EcoHeat Plumbing and Renewables, "
         "covering Weston-super-Mare, Taunton, Bridgwater and the surrounding "
         "Somerset area.",
         body, trail=[("Reviews", "reviews/")], priority="0.6")


def build_about():
    r = "../"
    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">About us</span>
<h1>About EcoHeat Plumbing and Renewables</h1>
<p class="lede">A small, independent Somerset firm doing plumbing, heating and
renewables properly — with the same engineer from first phone call to final
handover.</p>
</div></div>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div class="prose">
<h2>Who we are</h2>
<p>EcoHeat Plumbing and Renewables Limited was incorporated in 2024 and works
out of Brent House Farm at Edingworth, between Weston-super-Mare and
Burnham-on-Sea. The company is new; the trade experience behind it is not.</p>
<p>We deliberately stayed small. There is no call centre, no sales team on
commission and no target to shift a particular manufacturer's boiler. When you
ring, you get an engineer. When you get a quote, it comes from the person who
will be standing in your airing cupboard.</p>

<h2>What we believe about heating</h2>
<p>Two things, mainly. First, that most heating systems in Somerset are running
badly rather than broken — wrong flow temperature, no balancing, an oversized
boiler short-cycling itself to death. Fixing that is usually cheaper than
replacing anything.</p>
<p>Second, that renewables only work when they are designed. A heat pump sized
off a rule of thumb will be noisy, expensive and disappointing, and it will put
the next three households off. We do the heat loss survey properly because the
alternative damages the technology's reputation as well as the customer.</p>

<h2>Credentials</h2>
<p>We are Gas Safe registered under register number
<strong>{gs}</strong>, which you can verify at gassaferegister.co.uk. The
company is registered in England and Wales, number
<strong>{cno}</strong>, and we hold public liability insurance.</p>
<p>{mcs}</p>

<h2>How we price</h2>
<p>Surveys are free. Quotations are fixed, written and itemised, and valid for
30 days. On installations we take a deposit that covers materials, with the
balance due on completion and commissioning — never before the system is
finished and working. If we find something genuinely hidden once we start, we
stop, explain it and re-quote rather than adding it to the invoice.</p>
</div>
<div>
{team}
<h3 style="margin-top:1.5rem">At a glance</h3>
<div class="stats" style="grid-template-columns:1fr 1fr;margin-bottom:1.5rem">
<div class="stat"><b>2024</b><span>Incorporated in Somerset</span></div>
<div class="stat"><b>{gs}</b><span>Gas Safe register number</span></div>
<div class="stat"><b data-count="7500" data-prefix="£">{grant}</b><span>Heat pump grant handled for you</span></div>
<div class="stat"><b>Free</b><span>Surveys and quotations</span></div>
</div>
{van}
</div>
</div>
</div></section>

<section class="section section--ink"><div class="wrap">
<h2>How we work</h2>
<div class="grid grid-3" style="margin-top:1.5rem">
<div><h3>You deal with the engineer</h3><p>No account managers, no handovers
between departments. The person who surveys the job carries it through.</p></div>
<div><h3>The price is the price</h3><p>Fixed, written and itemised before we
start. Extras only ever with your agreement, in writing, first.</p></div>
<div><h3>We say no when it is right</h3><p>If a repair is more sensible than a
replacement, or your property is a poor candidate for a heat pump, you will hear
that from us.</p></div>
</div>
</div></section>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem">
<div>
<h2>Where to find us</h2>
<p><strong>Trading address</strong><br>{street}<br>{town}, {county}, {pc}</p>
<p><strong>Registered office</strong><br>{office}</p>
<p><strong>Telephone</strong> <a href="tel:{tel}">{phone}</a><br>
<strong>Email</strong> <a href="mailto:{mail}">{mail}</a></p>
<p><a href="../areas-we-cover/">See all the areas we cover</a></p>
</div>
<div>
<h2>Opening hours</h2>
<div class="table-scroll"><table>{hours}</table></div>
<p class="form__note">Outside these hours, emergency call-outs are available for
burst pipes, leaks and total loss of heating or hot water. If you smell gas,
call the National Gas Emergency Service on 0800 111 999 first.</p>
</div>
</div>
</div></section>
""".format(
        gs=e(C.BUSINESS["gas_safe_number"]), cno=e(C.BUSINESS["company_number"]),
        mcs=e(C.MCS_ANSWER), grant=C.BUS_GRANT,
        team=photo(r, "team.jpg",
                   "The EcoHeat Plumbing and Renewables engineering team at "
                   "their Edingworth base near Weston-super-Mare"),
        van=photo(r, "van.jpg",
                  "EcoHeat Plumbing and Renewables branded van parked at a "
                  "customer's property in Somerset"),
        street=e(C.BUSINESS["street"]), town=e(C.BUSINESS["town"]),
        county=e(C.BUSINESS["county"]), pc=e(C.BUSINESS["postcode"]),
        office=e(C.BUSINESS["registered_office"]),
        tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]),
        mail=e(C.BUSINESS["email"]),
        hours="".join("<tr><th>{d}</th><td>{h}</td></tr>".format(d=e(d), h=e(h))
                      for d, h in C.BUSINESS["opening"]),
    )
    body += cta_band(r, "Come and talk to us",
                     "Free surveys and straight answers, across Somerset and "
                     "North Somerset.")

    page("about/index.html",
         "About EcoHeat | Gas Safe Plumbers in Somerset",
         "EcoHeat Plumbing and Renewables is an independent Gas Safe registered "
         "firm based at Edingworth near Weston-super-Mare, covering Somerset "
         "and North Somerset.",
         body, trail=[("About", "about/")], priority="0.7")


def build_areas():
    r = "../"
    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Coverage</span>
<h1>Areas we cover across Somerset and North Somerset</h1>
<p class="lede">We are based at Edingworth, between Weston-super-Mare and
Burnham-on-Sea, and work across Somerset and North Somerset — roughly a 30 mile
radius, with the M5 corridor covered daily.</p>
</div></div>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem;align-items:start">
<div>
<h2>Towns and villages we work in</h2>
<ul class="areas-list">{areas}</ul>
<p style="margin-top:1.5rem">Not on the list? Ring <a href="tel:{tel}">{phone}</a>
and ask. We would rather give you a straight no than quote for a job we cannot
service properly afterwards — an annual boiler service is not much use if the
engineer is an hour and a half away.</p>
</div>
<div>
<h2>Response times</h2>
<p>Distance matters most when something has gone wrong, so we are honest about
it:</p>
<div class="table-scroll"><table>
<thead><tr><th>Area</th><th>Typical emergency response</th></tr></thead>
<tbody>
<tr><td>Weston-super-Mare, Burnham-on-Sea, Highbridge, Brent Knoll, Bleadon,
Banwell</td><td>Same day, usually within hours</td></tr>
<tr><td>Bridgwater, Cheddar, Axbridge, Wedmore, Congresbury, Yatton</td>
<td>Same day where possible</td></tr>
<tr><td>Taunton, Wells, Clevedon, Nailsea, Street, Glastonbury</td>
<td>Same or next working day</td></tr>
</tbody>
</table></div>
<div class="callout"><h3>Booked work travels further</h3>
<p>For installations and surveys we cover a wider area than for emergency
call-outs. If you are on the edge of the map and planning a boiler or heat pump
replacement, it is worth asking.</p></div>
</div>
</div>
</div></section>

<section class="section section--surface"><div class="wrap">
<h2>What we can do in your area</h2>
<div class="grid grid-3" style="margin-top:1.5rem">{cards}</div>
</div></section>
""".format(
        areas="".join("<li>%s</li>" % e(a) for a in C.AREAS),
        tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]),
        cards="".join(
            '<a class="card card--link" href="../services/{s}/">'
            '<div class="card__icon">{i}</div><h3>{n}</h3><p>{d}</p>'
            '<span class="card__more">Read more</span></a>'.format(
                s=s["slug"], i=icon(s["icon"]), n=e(s["nav"]),
                d=e(s["summary"])) for s in C.SERVICES),
    )
    body += cta_band(r, "Check we cover you",
                     "One phone call and we will tell you straight away.")

    page("areas-we-cover/index.html",
         "Areas We Cover | Plumbers in Weston-super-Mare & Taunton",
         "EcoHeat covers Weston-super-Mare, Burnham-on-Sea, Bridgwater, "
         "Taunton, Cheddar, Wells, Clevedon, Nailsea and the surrounding "
         "Somerset and North Somerset area.",
         body, trail=[("Areas we cover", "areas-we-cover/")], priority="0.7")


def build_faq():
    groups = []
    for title, items in C.FAQ_GROUPS:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        groups.append(
            '<section class="section" id="{s}"><div class="wrap narrow">'
            "<h2>{t}</h2>{f}</div></section>".format(
                s=slug, t=e(title),
                f=faq_block([x[0] for x in items])))

    toc = "".join(
        '<li><a href="#{s}">{t}</a></li>'.format(
            s=re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-"), t=e(t))
        for t, _ in C.FAQ_GROUPS)

    body = """
<div class="pagehead"><div class="wrap narrow">
<span class="eyebrow">Help</span>
<h1>Frequently asked questions</h1>
<p class="lede">Straight answers to what customers in Somerset actually ask us —
about grants, boilers, bathrooms, service plans and how we charge.</p>
<ul class="ticks" style="margin-top:1.5rem;columns:2 220px">{toc}</ul>
</div></div>
{groups}
""".format(toc=toc, groups="".join(groups))

    body += cta_band("../", "Still not sure?",
                     "Ring us and ask. We would rather spend five minutes on "
                     "the phone than have you book the wrong thing.")

    page("faq/index.html",
         "FAQs | Heat Pump Grants, Boilers & Plans | EcoHeat",
         "Answers to common questions about the {} heat pump grant, boiler "
         "installation, bathroom fitting, emergency call-outs and EcoHeat's "
         "service plans in Somerset.".format(C.BUS_GRANT),
         body, trail=[("FAQs", "faq/")], schema=faq_schema(), priority="0.8")


def build_contact():
    r = "../"
    action = FORM_ENDPOINT or ("mailto:%s" % C.BUSINESS["email"])
    enctype = "" if FORM_ENDPOINT else ' enctype="text/plain"'
    options = "".join(
        '<option value="{v}">{l}</option>'.format(v=s["slug"], l=e(s["nav"]))
        for s in C.SERVICES)

    body = """
<div class="pagehead"><div class="wrap">
<span class="eyebrow">Contact</span>
<h1>Contact EcoHeat Plumbing and Renewables</h1>
<p class="lede">Call for anything urgent. For quotes and surveys, the form below
reaches the same engineers — we aim to reply the same working day.</p>
</div></div>

<section class="section"><div class="wrap">
<div class="grid grid-2" style="gap:3rem;align-items:start">

<div>
<h2>Request a quote or a survey</h2>
<form class="form" data-contact-form action="{action}" method="post"{enctype}>
<div class="form__status" aria-live="polite"></div>

<div class="field--row">
<div class="field">
<label for="name">Your name <span class="hint">(required)</span></label>
<input id="name" name="name" type="text" autocomplete="name" required>
</div>
<div class="field">
<label for="phone">Telephone <span class="hint">(required)</span></label>
<input id="phone" name="phone" type="tel" autocomplete="tel" required>
</div>
</div>

<div class="field--row">
<div class="field">
<label for="email">Email</label>
<input id="email" name="email" type="email" autocomplete="email">
</div>
<div class="field">
<label for="postcode">Postcode <span class="hint">(required)</span></label>
<input id="postcode" name="postcode" type="text" autocomplete="postal-code"
 required>
</div>
</div>

<div class="field">
<label for="enquiry">What do you need?</label>
<select id="enquiry" name="enquiry">
<option value="">Please choose…</option>
{options}
<option value="service-plan">Annual service plan</option>
<option value="finance">Finance options</option>
<option value="other">Something else</option>
</select>
</div>

<div class="field">
<label for="message">Tell us about the job <span class="hint">(the more detail,
the more accurate our answer)</span></label>
<textarea id="message" name="message"
 placeholder="For example: 18-year-old Worcester combi in the kitchen, losing pressure weekly, three-bed semi."></textarea>
</div>

<div class="field hp" aria-hidden="true">
<label for="company_website">Leave this field empty</label>
<input id="company_website" name="company_website" type="text" tabindex="-1"
 autocomplete="off">
</div>

<div class="consent">
<input id="consent" name="consent" type="checkbox" value="yes" required>
<label for="consent">I agree that EcoHeat may use the details above to respond
to this enquiry, and I have read the
<a href="../legal/privacy-policy/">privacy policy</a>. <span class="hint">
(Required. We will not add you to a mailing list or pass your details to anyone
else without asking you first.)</span></label>
</div>

<button class="btn btn--primary" type="submit">Send enquiry</button>
<p class="form__note">We use what you send only to answer your enquiry and, if
you go ahead, to carry out the work. Enquiries that do not lead to a job are
deleted within 24 months. See the
<a href="../legal/privacy-policy/">privacy policy</a> for your rights, including
how to ask us to delete your data.{fallback}</p>
</form>
</div>

<div>
<h2>Call or email</h2>
<div class="card" style="margin-bottom:1.25rem">
<div class="card__icon">{ph}</div>
<h3><a href="tel:{tel}">{phone}</a></h3>
<p>Fastest for emergencies and anything urgent. You will get an engineer, not a
call centre.</p>
</div>
<div class="card" style="margin-bottom:1.25rem">
<div class="card__icon">{ml}</div>
<h3><a href="mailto:{mail}">Email us</a></h3>
<p>{mail}</p>
</div>
<div class="card" style="margin-bottom:1.25rem">
<div class="card__icon">{ch}</div>
<h3><a href="https://wa.me/{wa}" rel="noopener">WhatsApp</a></h3>
<p>Send a photo of the boiler, the leak or the error code — it often saves a
visit.</p>
</div>

<h3>Trading address</h3>
<p>{street}<br>{town}, {county}, {pc}</p>
<h3>Opening hours</h3>
<div class="table-scroll"><table>{hours}</table></div>

<div class="callout callout--amber" style="margin-top:1.5rem">
<h3>Smell gas?</h3>
<p>Leave the property, do not touch light switches, and call the National Gas
Emergency Service on <a href="tel:+448001119999">0800 111 999</a> before you
call us.</p>
</div>
</div>

</div>
</div></section>
""".format(
        action=e(action), enctype=enctype, options=options,
        fallback=("" if FORM_ENDPOINT else
                  " This form opens your own email application to send the "
                  "message, so nothing is stored on this website and no "
                  "third-party form processor receives your details."),
        ph=icon("phone"), ml=icon("mail"), ch=icon("chat"),
        tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]),
        mail=e(C.BUSINESS["email"]), wa=e(C.BUSINESS["whatsapp"]),
        street=e(C.BUSINESS["street"]), town=e(C.BUSINESS["town"]),
        county=e(C.BUSINESS["county"]), pc=e(C.BUSINESS["postcode"]),
        hours="".join("<tr><th>{d}</th><td>{h}</td></tr>".format(d=e(d), h=e(h))
                      for d, h in C.BUSINESS["opening"]),
    )

    schema = ('{{"@context":"https://schema.org","@type":"ContactPage",'
              '"name":"Contact EcoHeat","url":"{u}/contact/",'
              '"mainEntity":{{"@id":"{u}/#business"}}}}').format(u=C.SITE_URL)

    page("contact/index.html",
         "Contact EcoHeat | Plumbers in Weston-super-Mare | 01934 440290",
         "Contact EcoHeat Plumbing and Renewables for a free survey or a quote. "
         "Call 01934 440290, email us or send an enquiry — Somerset and North "
         "Somerset covered.",
         body, trail=[("Contact", "contact/")], schema=schema, priority="0.9")


# --------------------------------------------------------------------------
# legal pages
# --------------------------------------------------------------------------

def legal_page(slug, title, meta, h1, lede, sections, priority="0.3"):
    r = "../../"
    html_parts = []
    for heading, para_list in sections:
        anchor = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        html_parts.append('<h2 id="{a}">{h}</h2>'.format(a=anchor, h=e(heading)))
        html_parts.extend(para_list)

    body = """
<div class="pagehead"><div class="wrap narrow">
<span class="eyebrow">Legal</span>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
<p class="form__note" style="margin-top:1rem">Last updated {date}</p>
</div></div>
<section class="section"><div class="wrap narrow"><div class="prose">{body}</div></div></section>
""".format(h1=e(h1), lede=e(lede), date=BUILD_DATE, body="".join(html_parts))

    page("legal/%s/index.html" % slug, title, meta, body,
         trail=[("Legal", ""), (h1, "legal/%s/" % slug)], priority=priority)


def build_privacy():
    b = C.BUSINESS
    processor_note = (
        "<p>Enquiries submitted through the website form are sent to us by a "
        "third-party form processor acting as our data processor under a "
        "written agreement. <strong>Before launch:</strong> name the provider "
        "here, together with the country its servers are in and, if outside "
        "the UK, the transfer safeguard relied upon.</p>"
        if FORM_ENDPOINT else
        "<p>Our website contact form opens your own email application and "
        "sends the message directly to us. It is not submitted to this website "
        "and no third-party form processor receives your details.</p>"
    )

    sections = [
        ("Who we are", [
            "<p>{legal} (&ldquo;EcoHeat&rdquo;, &ldquo;we&rdquo;, "
            "&ldquo;us&rdquo;) is the data controller for the personal data "
            "described in this policy. We are registered in England and Wales "
            "under company number {cno}, with a registered office at "
            "{office} and a trading address at {street}, {town}, {pc}.</p>"
            .format(legal=e(b["legal_name"]), cno=e(b["company_number"]),
                    office=e(b["registered_office"]), street=e(b["street"]),
                    town=e(b["town"]), pc=e(b["postcode"])),
            "<p>For anything to do with your personal data, contact us at "
            '<a href="mailto:{m}">{m}</a> or on '
            '<a href="tel:{t}">{p}</a>.</p>'.format(
                m=e(b["email"]), t=b["phone_e164"], p=e(b["phone"])),
        ]),
        ("What personal data we collect", [
            "<p>We collect only what we need to answer your enquiry and carry "
            "out work you ask us to do:</p>",
            "<ul>"
            "<li><strong>Contact details</strong> — your name, telephone "
            "number, email address and the postcode or address of the "
            "property.</li>"
            "<li><strong>Enquiry details</strong> — what you tell us about the "
            "job, including any photographs you send us.</li>"
            "<li><strong>Job records</strong> — surveys, quotations, "
            "certificates, invoices and service history for work we carry "
            "out.</li>"
            "<li><strong>Correspondence</strong> — emails, WhatsApp messages "
            "and notes of telephone calls.</li>"
            "</ul>",
            "<p>We do not collect special category data, and we do not ask for "
            "payment card details through this website.</p>",
        ]),
        ("How we use it, and our lawful basis", [
            '<div class="table-scroll"><table>'
            "<thead><tr><th>What we do</th><th>Why</th><th>Lawful basis "
            "(UK GDPR Article 6)</th></tr></thead><tbody>"
            "<tr><td>Reply to your enquiry and provide a quotation</td>"
            "<td>You have asked us to</td>"
            "<td>Steps taken at your request prior to entering a contract "
            "(Art. 6(1)(b))</td></tr>"
            "<tr><td>Carry out work, order materials and invoice</td>"
            "<td>To deliver what you have engaged us to do</td>"
            "<td>Performance of a contract (Art. 6(1)(b))</td></tr>"
            "<tr><td>Issue gas safety and commissioning certificates, notify "
            "Building Regulations, register warranties</td>"
            "<td>We are required to</td>"
            "<td>Legal obligation (Art. 6(1)(c))</td></tr>"
            "<tr><td>Apply for the Boiler Upgrade Scheme grant on your "
            "behalf</td><td>To obtain the grant you have asked us to claim</td>"
            "<td>Performance of a contract (Art. 6(1)(b))</td></tr>"
            "<tr><td>Keep accounting records</td><td>Tax and company law</td>"
            "<td>Legal obligation (Art. 6(1)(c))</td></tr>"
            "<tr><td>Send service reminders to existing customers</td>"
            "<td>So your warranty is not invalidated by a missed service</td>"
            "<td>Legitimate interests (Art. 6(1)(f)) — you can opt out at any "
            "time</td></tr>"
            "<tr><td>Publish a photograph or review of your job</td>"
            "<td>To show our work</td><td>Consent (Art. 6(1)(a)) — we ask "
            "first, and you can withdraw it</td></tr>"
            "</tbody></table></div>",
            "<p>We do not send marketing email or SMS to people who have "
            "simply made an enquiry, and we never sell or rent your details to "
            "anyone.</p>",
        ]),
        ("Who we share it with", [
            processor_note,
            "<p>Beyond that, we share personal data only where it is necessary:"
            "</p>",
            "<ul>"
            "<li><strong>Gas Safe Register and Building Control</strong> — "
            "notification of notifiable gas work, as required by law.</li>"
            "<li><strong>Manufacturers</strong> — to register your warranty in "
            "your name.</li>"
            "<li><strong>Ofgem and MCS</strong> — where we apply for a Boiler "
            "Upgrade Scheme voucher on your behalf, and to register the "
            "installation.</li>"
            "<li><strong>Our MCS-accredited installation partner</strong> — "
            "where a heat pump installation is certified through them.</li>"
            "<li><strong>Finance providers</strong> — only if you ask us to "
            "arrange finance, and only with your knowledge.</li>"
            "<li><strong>Our accountant and IT providers</strong> — under "
            "confidentiality obligations.</li>"
            "<li><strong>Insurers and legal advisers</strong> — if a claim or "
            "dispute arises.</li>"
            "</ul>",
        ]),
        ("How long we keep it", [
            "<ul>"
            "<li><strong>Enquiries that do not become jobs</strong> — deleted "
            "within 24 months.</li>"
            "<li><strong>Job and installation records</strong> — kept for the "
            "life of the installation plus 6 years, because gas safety records, "
            "warranty claims and liability all depend on them.</li>"
            "<li><strong>Accounting records</strong> — 6 years plus the current "
            "financial year, as required by HMRC.</li>"
            "<li><strong>Gas safety certificates</strong> — at least 2 years, "
            "and normally for the life of the appliance record.</li>"
            "</ul>",
        ]),
        ("Your rights", [
            "<p>Under UK data protection law you have the right to:</p>",
            "<ul>"
            "<li>ask for a copy of the personal data we hold about you;</li>"
            "<li>have inaccurate data corrected;</li>"
            "<li>ask us to delete data we no longer need (this does not "
            "override records we must keep by law);</li>"
            "<li>object to, or ask us to restrict, processing based on our "
            "legitimate interests;</li>"
            "<li>withdraw consent at any time where we rely on it, such as for "
            "photographs of your installation;</li>"
            "<li>ask for your data in a portable format.</li>"
            "</ul>",
            "<p>Email <a href=\"mailto:{m}\">{m}</a> and we will respond within "
            "one month. There is no charge.</p>".format(m=e(b["email"])),
            "<p>If you are unhappy with how we have handled your data you can "
            "complain to the Information Commissioner's Office at ico.org.uk or "
            "on 0303 123 1113. We would appreciate the chance to put it right "
            "first.</p>",
        ]),
        ("Cookies and analytics", [
            "<p>This website sets no advertising or tracking cookies, and does "
            "not profile visitors. See our "
            '<a href="../cookie-policy/">cookie policy</a> for the detail.</p>',
        ]),
        ("Security", [
            "<p>Enquiries and job records are held in access-controlled "
            "accounts protected by strong passwords and two-factor "
            "authentication where the provider supports it. This website is "
            "served over HTTPS. No system is perfectly secure, but we take "
            "reasonable technical and organisational measures appropriate to a "
            "business of our size.</p>",
        ]),
        ("Changes to this policy", [
            "<p>If we change how we use personal data we will update this page "
            "and change the date at the top. Material changes affecting "
            "existing customers will be notified directly.</p>",
        ]),
    ]

    legal_page(
        "privacy-policy",
        "Privacy Policy | EcoHeat Plumbing and Renewables",
        "How EcoHeat Plumbing and Renewables collects, uses, shares and stores "
        "personal data, the lawful basis for each purpose, how long we keep it "
        "and your rights under UK GDPR.",
        "Privacy policy",
        "What we do with your personal data, why we are allowed to, how long we "
        "keep it and how to get it back or have it deleted.",
        sections, priority="0.3")


def build_cookies():
    sections = [
        ("The short version", [
            "<p>This website sets no cookies of its own, uses no analytics or "
            "advertising trackers, and does not profile you. There is nothing "
            "to consent to, which is why you are not being asked to dismiss a "
            "banner.</p>",
        ]),
        ("What that means in practice", [
            "<ul>"
            "<li>No Google Analytics, Meta Pixel or similar tracking.</li>"
            "<li>No advertising or re-marketing cookies.</li>"
            "<li>No third-party fonts, maps or embedded video loading from "
            "external servers on page load.</li>"
            "<li>No cross-site tracking of any kind.</li>"
            "</ul>",
            "<p>Your browser may store ordinary technical information such as "
            "its own cache. That is not something this site controls or can "
            "read.</p>",
        ]),
        ("Server logs", [
            "<p>Our hosting provider keeps standard access logs — IP address, "
            "timestamp, page requested and browser type — for security and to "
            "keep the site running. These are ordinary server logs, not "
            "cookies, and they are not used to build a profile of you.</p>",
        ]),
        ("If this changes", [
            "<p>If we ever add analytics or any non-essential cookie, we will "
            "ask for your consent before it is set, and this page will be "
            "updated first. Under the Privacy and Electronic Communications "
            "Regulations, non-essential cookies require opt-in consent, and we "
            "will treat it that way.</p>",
            '<p>See also our <a href="../privacy-policy/">privacy policy</a>.'
            "</p>",
        ]),
    ]
    legal_page(
        "cookie-policy",
        "Cookie Policy | EcoHeat Plumbing and Renewables",
        "This website sets no advertising or analytics cookies. What that "
        "means, what our host logs, and what we would do before adding any "
        "non-essential cookie.",
        "Cookie policy",
        "A short page, because there is very little to declare.",
        sections, priority="0.2")


def build_terms():
    b = C.BUSINESS
    sections = [
        ("About these terms", [
            "<p>These terms apply to work carried out by {legal} "
            "(&ldquo;EcoHeat&rdquo;) for consumers and to the use of this "
            "website. They do not affect your statutory rights under the "
            "Consumer Rights Act 2015. Where we have issued a separate written "
            "contract or quotation, and it conflicts with these terms, the "
            "quotation takes precedence.</p>".format(legal=e(b["legal_name"])),
        ]),
        ("Quotations and pricing", [
            "<p>Surveys are free and carry no obligation. Quotations are fixed, "
            "itemised and valid for 30 days from issue unless stated otherwise "
            "on the quotation itself.</p>",
            "<p>A fixed price covers the work described in the quotation. If we "
            "encounter something that could not reasonably have been "
            "identified at survey — concealed asbestos, a failed component "
            "found once panels are removed, non-compliant existing pipework — "
            "we will stop, explain the position and provide a revised price for "
            "your approval before continuing. You are never charged for "
            "additional work you have not agreed to in writing.</p>",
            "<p>Prices shown anywhere on this website are indicative unless "
            "they appear on a written quotation addressed to you.</p>",
        ]),
        ("Deposits and payment", [
            "<p>On installations we take a deposit to cover materials, with the "
            "balance due on completion and commissioning of the work. On "
            "repairs and call-outs, payment is due on completion. We accept "
            "bank transfer, card and cash.</p>",
            "<p>Invoices are payable within 14 days. We reserve the right to "
            "charge statutory interest on overdue commercial accounts under the "
            "Late Payment of Commercial Debts (Interest) Act 1998. Goods "
            "supplied remain our property until paid for in full.</p>",
        ]),
        ("Your right to cancel", [
            "<p>Where you enter into a contract with us away from our business "
            "premises — which covers most surveys carried out at your home — "
            "you have the right under the Consumer Contracts (Information, "
            "Cancellation and Additional Charges) Regulations 2013 to cancel "
            "within <strong>14 days</strong> without giving a reason.</p>",
            "<p>To cancel, tell us in writing at "
            '<a href="mailto:{m}">{m}</a> or by post to our trading address '
            "before the 14 days expire. We will refund any deposit within 14 "
            "days of being told.</p>".format(m=e(b["email"])),
            "<p>If you ask us in writing to begin work inside the 14-day "
            "cancellation period — as customers with no heating usually do — "
            "and you then cancel, we may charge for the work already carried "
            "out and materials already supplied, in proportion to what has been "
            "done.</p>",
        ]),
        ("Access, and things outside our control", [
            "<p>You agree to provide safe access to the property and to the "
            "areas we need to work in, along with a supply of electricity and "
            "water. Please tell us in advance about asbestos, structural "
            "problems or anything else that affects safe working.</p>",
            "<p>If we attend at an agreed appointment and cannot gain access, "
            "we may charge a reasonable call-out fee. We will always try to "
            "contact you before doing so.</p>",
        ]),
        ("Workmanship, guarantees and warranties", [
            "<p>All work is carried out with reasonable care and skill by "
            "suitably qualified engineers. Gas work is carried out by Gas Safe "
            "registered engineers under register number {gs}.</p>".format(
                gs=e(b["gas_safe_number"])),
            "<p>Our workmanship is guaranteed for 12 months from completion. "
            "Manufacturer warranties on appliances are provided by the "
            "manufacturer, typically run from 5 to 12 years, and are stated on "
            "your quotation. Manufacturer warranties normally require an annual "
            "service by a qualified engineer; if that service is missed, the "
            "manufacturer may decline a claim, and that is outside our "
            "control.</p>",
            "<p>Guarantees do not cover fair wear and tear, damage caused by "
            "third parties, misuse, freezing, system water quality problems "
            "where we advised treatment that was declined, or faults in parts "
            "of the system we did not install or were not asked to work on.</p>",
        ]),
        ("Service plans", [
            "<p>Service plans run for 12 months from the start date and renew "
            "only with your agreement. They can be paid monthly by Direct Debit "
            "or annually in advance.</p>",
            "<p>You may cancel at any time on 30 days' written notice. Where "
            "you have paid monthly and a service has already been carried out "
            "in the plan year, we may charge the difference between the "
            "instalments paid and our standard price for the work "
            "delivered. There is no exit fee beyond that.</p>",
            "<p>Plans cover the appliances and components listed on the plan "
            "and exclude faults that already existed at the first service, "
            "appliances beyond economic repair, and systems that have not been "
            "installed or commissioned to the relevant standards. Full "
            "inclusions and exclusions for each plan are set out on the "
            '<a href="../../services/annual-service-plans/">service plans '
            "page</a>.</p>",
        ]),
        ("Grants and finance", [
            "<p>Where we apply for a Boiler Upgrade Scheme grant on your "
            "behalf, the grant is awarded by Ofgem under scheme rules set by "
            "government. We will confirm eligibility in writing before you "
            "commit, but we cannot guarantee an award, and scheme values and "
            "criteria may change. If a voucher is refused for reasons outside "
            "our control, you may cancel the contract and we will refund your "
            "deposit less the cost of any work already carried out at your "
            "request.</p>",
            "<p>Finance, where arranged, is a credit agreement between you and "
            "an FCA-authorised finance provider. EcoHeat is not the lender. "
            "Applications are subject to status and affordability checks.</p>",
        ]),
        ("Complaints", [
            "<p>If something is not right, tell us first — most problems are "
            "solved with a phone call. Contact us on "
            '<a href="tel:{t}">{p}</a> or at <a href="mailto:{m}">{m}</a>.</p>'
            .format(t=b["phone_e164"], p=e(b["phone"]), m=e(b["email"])),
            "<p>We will acknowledge a written complaint within 5 working days "
            "and give you a substantive response within 28 days. If we cannot "
            "resolve it between us, you may refer a gas-related complaint to "
            "the Gas Safe Register, and you retain your rights under the "
            "Consumer Rights Act 2015.</p>",
        ]),
        ("Liability", [
            "<p>We hold public liability insurance and we are responsible for "
            "loss or damage you suffer that is a foreseeable result of our "
            "breaking this contract or failing to use reasonable care and "
            "skill.</p>",
            "<p>We do not limit our liability in any way where it would be "
            "unlawful to do so — including for death or personal injury caused "
            "by our negligence, for fraud, or for any breach of your statutory "
            "rights. We are not liable for losses that were not foreseeable, or "
            "for business losses, as our services are supplied for domestic and "
            "private use.</p>",
        ]),
        ("Website content", [
            "<p>The content of this website is provided for general information "
            "about our services. Guidance on grants, regulations and heating "
            "technology is given in good faith and correct to the best of our "
            "knowledge at the date shown, but it is not a substitute for a "
            "survey of your property or for the official scheme rules. Always "
            "check the current position with us before relying on it.</p>",
            "<p>Text, images and design on this site belong to EcoHeat unless "
            "stated otherwise, and may not be reproduced without permission.</p>",
        ]),
        ("Governing law", [
            "<p>These terms are governed by the law of England and Wales, and "
            "any dispute may be brought in the courts of England and Wales.</p>",
        ]),
    ]
    legal_page(
        "terms-of-service",
        "Terms of Service | EcoHeat Plumbing and Renewables",
        "EcoHeat's terms of service: quotations and fixed pricing, deposits and "
        "payment, your 14-day right to cancel, guarantees, service plans, "
        "grants, complaints and liability.",
        "Terms of service",
        "The terms on which we quote, carry out work and run service plans — "
        "including your right to cancel and how to complain.",
        sections, priority="0.3")


def build_404():
    body = """
<div class="pagehead"><div class="wrap narrow">
<span class="eyebrow">404</span>
<h1>That page has moved or never existed</h1>
<p class="lede">Sorry about that. Here is where most people are heading.</p>
</div></div>
<section class="section"><div class="wrap">
<h2>Popular pages</h2>
<div class="grid grid-3" style="margin-top:1.5rem">{cards}</div>
<p style="margin-top:2rem">Or just ring us on <a href="tel:{tel}">{phone}</a> —
usually quicker than clicking about.</p>
</div></section>
""".format(
        cards="".join(
            '<a class="card card--link" href="{p}"><div class="card__icon">{i}'
            "</div><h3>{n}</h3><p>{d}</p></a>".format(p=p, i=icon(ic), n=e(n),
                                                      d=e(d))
            for n, p, d, ic in [
                ("Services", "services/", "Boilers, heat pumps, bathrooms and "
                 "emergency call-outs.", "spanner"),
                ("Heat pump grants", "grants/",
                 "How the %s Boiler Upgrade Scheme grant works." % C.BUS_GRANT,
                 "pound"),
                ("Contact", "contact/", "Request a free survey or a quote.",
                 "mail"),
            ]),
        tel=C.BUSINESS["phone_e164"], phone=e(C.BUSINESS["phone"]))

    page("404.html", "Page not found | EcoHeat Plumbing and Renewables",
         "The page you were looking for could not be found. Browse EcoHeat's "
         "plumbing, heating and renewable energy services for Somerset.",
         body, noindex=True, in_sitemap=False)


# --------------------------------------------------------------------------
# non-HTML output
# --------------------------------------------------------------------------

def sitemap_xml() -> str:
    rows = []
    for p in PAGES:
        if not p["in_sitemap"]:
            continue
        rows.append(
            "  <url>\n    <loc>{loc}</loc>\n    <lastmod>{d}</lastmod>\n"
            "    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>\n"
            "  </url>".format(loc=p["canonical"], d=BUILD_DATE,
                              c=p["changefreq"], pr=p["priority"]))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "{}\n</urlset>\n".format("\n".join(rows)))


def robots_txt() -> str:
    return """# EcoHeat Plumbing and Renewables
# Somerset & North Somerset plumbing, heating and renewables.

User-agent: *
Allow: /

# Query strings on the contact form pre-select a subject; they are not
# separate pages and should not be indexed as duplicates.
Disallow: /contact/?

Sitemap: {site}/sitemap.xml
""".format(site=C.SITE_URL)


def llms_txt() -> str:
    services = "\n".join(
        "- [{n}]({u}/services/{s}/): {d}".format(
            n=s["nav"], u=C.SITE_URL, s=s["slug"], d=s["summary"])
        for s in C.SERVICES)
    return """# {name}

> Gas Safe registered plumbing, heating and renewable energy installer based at
> Edingworth near Weston-super-Mare, covering Somerset and North Somerset.

- Legal entity: {legal}, company number {cno} (England & Wales)
- Gas Safe register number: {gs}
- Telephone: {phone}
- Email: {mail}
- Trading address: {street}, {town}, {county}, {pc}
- Heat pump accreditation: {mcs}

## Services

{services}

## Key pages

- [Boiler Upgrade Scheme grants]({u}/grants/): how the {grant} heat pump grant works
- [Finance options]({u}/finance/)
- [Projects and case studies]({u}/projects/)
- [Areas we cover]({u}/areas-we-cover/)
- [FAQs]({u}/faq/)
- [Contact]({u}/contact/)
""".format(name=C.BUSINESS["name"], legal=C.BUSINESS["legal_name"],
           cno=C.BUSINESS["company_number"], gs=C.BUSINESS["gas_safe_number"],
           phone=C.BUSINESS["phone"], mail=C.BUSINESS["email"],
           street=C.BUSINESS["street"], town=C.BUSINESS["town"],
           county=C.BUSINESS["county"], pc=C.BUSINESS["postcode"],
           mcs=C.MCS_BADGE, services=services, u=C.SITE_URL,
           grant=C.BUS_GRANT)


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------

def validate() -> list[str]:
    problems = []
    titles, metas = {}, {}
    paths = {p["path"] for p in PAGES}

    for p in PAGES:
        doc, path = p["html"], p["path"]

        h1s = re.findall(r"<h1[ >]", doc)
        if len(h1s) != 1:
            problems.append("%s: expected exactly one <h1>, found %d"
                            % (path, len(h1s)))

        # Heading hierarchy: no level may be skipped on the way down.
        prev = 1
        for lv in [int(m) for m in re.findall(r"<h([1-4])[ >]", doc)]:
            if lv > prev + 1:
                problems.append("%s: heading jumps from h%d to h%d"
                                % (path, prev, lv))
                break
            prev = lv

        if len(p["title"]) > 65:
            problems.append("%s: title is %d chars (aim for <= 65)"
                            % (path, len(p["title"])))
        if not (110 <= len(p["meta"]) <= 175):
            problems.append("%s: meta description is %d chars (aim 110-175)"
                            % (path, len(p["meta"])))
        titles.setdefault(p["title"], []).append(path)
        metas.setdefault(p["meta"], []).append(path)

        # Relative internal links must resolve to a real output file.
        base = os.path.dirname(path)
        for raw in re.findall(r'href="([^"]+)"', doc):
            if raw.startswith(("http://", "https://", "mailto:", "tel:", "//",
                               "#")):
                continue
            href = raw.split("#")[0].split("?")[0]
            if not href:
                continue
            target = os.path.normpath(os.path.join(base, href))
            if href.endswith("/") or "." not in os.path.basename(target):
                target = os.path.join(target, "index.html")
            target = target.replace(os.sep, "/")
            if target in paths or target in EXTRA_OUTPUT:
                continue
            if os.path.exists(os.path.join(ROOT, target)):
                continue
            problems.append("%s: broken internal link -> %s" % (path, href))

    for title, where in titles.items():
        if len(where) > 1:
            problems.append("duplicate <title> %r on %s" % (title, where))
    for meta, where in metas.items():
        if len(where) > 1:
            problems.append("duplicate meta description on %s" % where)

    return problems


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def build_all():
    build_home()
    build_services_index()
    for s in C.SERVICES:
        build_service(s)
    build_grants()
    build_finance()
    build_projects()
    build_reviews()
    build_about()
    build_areas()
    build_faq()
    build_contact()
    build_privacy()
    build_cookies()
    build_terms()
    build_404()


def write(target_dir: str):
    for p in PAGES:
        dest = os.path.join(target_dir, p["path"])
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(p["html"])
    for name, text in (("sitemap.xml", sitemap_xml()),
                       ("robots.txt", robots_txt()),
                       ("llms.txt", llms_txt())):
        with open(os.path.join(target_dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)


def main() -> int:
    build_all()

    problems = validate()
    for problem in problems:
        sys.stderr.write("  ! %s\n" % problem)

    if "--check" in sys.argv:
        tmp = tempfile.mkdtemp()
        try:
            write(tmp)
            drift = []
            for p in PAGES:
                new = os.path.join(tmp, p["path"])
                old = os.path.join(ROOT, p["path"])
                if not os.path.exists(old):
                    drift.append(p["path"] + " (missing)")
                    continue
                with open(new, encoding="utf-8") as a, \
                        open(old, encoding="utf-8") as b:
                    if a.read() != b.read():
                        drift.append(p["path"])
            for name in ("sitemap.xml", "robots.txt", "llms.txt"):
                with open(os.path.join(tmp, name), encoding="utf-8") as a:
                    new_text = a.read()
                old_path = os.path.join(ROOT, name)
                old_text = (open(old_path, encoding="utf-8").read()
                            if os.path.exists(old_path) else None)
                # The sitemap carries a build date; compare ignoring lastmod.
                if name == "sitemap.xml" and old_text is not None:
                    strip = lambda t: re.sub(r"<lastmod>[^<]+</lastmod>", "", t)
                    if strip(new_text) != strip(old_text):
                        drift.append(name)
                elif new_text != old_text:
                    drift.append(name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        if drift:
            sys.stderr.write(
                "\nOut of date, re-run `python3 build.py`:\n  %s\n"
                % "\n  ".join(drift))
            return 1
        if problems:
            return 1
        print("check: %d pages up to date, no problems" % len(PAGES))
        return 0

    write(ROOT)
    print("built %d pages into %s" % (len(PAGES), ROOT))
    if problems:
        print("%d problem(s) reported above" % len(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
