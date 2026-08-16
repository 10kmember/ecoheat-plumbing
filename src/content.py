# -*- coding: utf-8 -*-
"""Single source of truth for every fact, page and piece of copy on the site.

Nothing in the generated HTML is written by hand; edit this file and re-run
``python3 build.py`` from the repository root.

Anything marked ``NEEDS SIGN-OFF`` is a commercial or regulatory claim that must
be confirmed by EcoHeat before the site goes live. See README.md.
"""

# ---------------------------------------------------------------------------
# Business facts
# ---------------------------------------------------------------------------

BUSINESS = {
    "name": "EcoHeat Plumbing and Renewables",
    "legal_name": "Ecoheat Plumbing and Renewables Limited",
    "company_number": "15532701",
    "gas_safe_number": "952210",
    "phone": "01934 440290",
    "phone_e164": "+441934440290",
    "email": "info@ecoheatplumbingandrenewables.co.uk",
    "whatsapp": "441934440290",
    "facebook": "https://www.facebook.com/share/18zvEXzBF4/",
    # Trading address (Gas Safe registered premises)
    "street": "Brent House Farm, Edingworth Road, Edingworth",
    "town": "Weston-super-Mare",
    "county": "Somerset",
    "postcode": "BS24 0JA",
    "lat": "51.2846",
    "lon": "-2.9210",
    # Registered office (Companies House)
    "registered_office": (
        "Suite 106, Viney Court, Viney Street, Taunton, Somerset, TA1 3FB"
    ),
    "opening": [
        ("Monday to Friday", "07:30 - 17:30"),
        ("Saturday", "08:00 - 13:00"),
        ("Sunday", "Emergency call-outs only"),
    ],
    "opening_schema": [
        {"days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
         "opens": "07:30", "closes": "17:30"},
        {"days": ["Saturday"], "opens": "08:00", "closes": "13:00"},
    ],
}

# Production domain. Canonical tags, the sitemap and structured data use this.
# Internal links are always relative, so the build also works unchanged on a
# GitHub Pages project path such as /Ava/.
SITE_URL = "https://www.ecoheatplumbingandrenewables.co.uk"

# NEEDS SIGN-OFF -- heat pump accreditation.
#   "partner" : installations delivered with an MCS-accredited partner.
#   "own"     : EcoHeat holds its own MCS certificate; set MCS_NUMBER below.
# The Boiler Upgrade Scheme is only payable where the installer is MCS
# certified, so this must be accurate before launch.
MCS_STATUS = "partner"
MCS_NUMBER = ""  # e.g. "NAP-12345" -- only used when MCS_STATUS == "own"

BUS_GRANT = "£7,500"

AREAS = [
    "Weston-super-Mare", "Taunton", "Bridgwater", "Burnham-on-Sea",
    "Highbridge", "Cheddar", "Wedmore", "Axbridge", "Banwell", "Bleadon",
    "Brent Knoll", "Congresbury", "Yatton", "Clevedon", "Nailsea",
    "Wells", "Street", "Glastonbury", "North Petherton", "Wellington",
]

# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------
# Each service becomes /services/<slug>/ with its own H1, meta description,
# Service schema and internal links.

SERVICES = [
    {
        "slug": "boiler-installation",
        "nav": "Boiler installation",
        "h1": "Boiler installation in Somerset & North Somerset",
        "title": "Boiler Installation Weston-super-Mare & Taunton",
        "meta": (
            "Gas Safe registered boiler installation across Somerset and North "
            "Somerset. Fixed-price quotes, gas, LPG and oil, and the engineer "
            "who quotes is the engineer who fits."
        ),
        "summary": (
            "Fixed-price gas, LPG and oil boiler installations, fitted by the "
            "engineer who surveyed the job."
        ),
        "icon": "boiler",
        "intro": (
            "A new boiler is the single biggest heating decision most "
            "households make, and it is usually made in a hurry after an old "
            "one fails. We survey properly, quote a fixed price in writing, "
            "and fit to manufacturer specification so the warranty stands up."
        ),
        "body": [
            ("What we install",
             "Gas, LPG and oil boilers from the mainstream manufacturers: "
             "combination, system and conventional. We size the boiler to "
             "the property using a room-by-room heat loss calculation rather "
             "than replacing like for like, because an oversized boiler "
             "cycles, wastes fuel and wears out early."),
            ("What a fixed price includes",
             "The boiler and flue, all controls, a magnetic system filter, a "
             "chemical flush or power flush where the system needs it, "
             "Building Regulations notification, the Benchmark commissioning "
             "record and the manufacturer warranty registration. No day-rate "
             "surprises once the old boiler is off the wall."),
            ("Warranties",
             "Manufacturer warranties run from 5 to 12 years depending on the "
             "boiler and the controls fitted. We tell you at quote stage "
             "exactly which warranty applies and what you have to do to keep "
             "it valid: normally an annual service on time, every year."),
        ],
        "bullets": [
            "Combi, system and conventional boiler swaps",
            "Back boiler and warm-air system replacements",
            "Full system upgrades including pipework and radiators",
            "Smart controls and weather compensation",
            "Landlord and letting-agent installations",
            "Building Regulations notification handled for you",
        ],
        "faq_slugs": ["boiler-install-time", "boiler-brands", "fixed-price"],
        "related": ["boiler-servicing-and-repairs", "air-source-heat-pumps",
                    "annual-service-plans"],
    },
    {
        "slug": "boiler-servicing-and-repairs",
        "nav": "Servicing & repairs",
        "h1": "Boiler servicing, repairs and gas safety certificates",
        "title": "Boiler Service & Repair Weston-super-Mare | Gas Safe",
        "meta": (
            "Annual boiler servicing, breakdown repairs, power flushing and "
            "landlord gas safety certificates (CP12) across Somerset. Gas Safe "
            "registered engineers, register number 952210."
        ),
        "summary": (
            "Annual services, breakdown repairs, power flushing and landlord "
            "gas safety certificates."
        ),
        "icon": "spanner",
        "intro": (
            "Most boiler breakdowns are preventable, and most of the "
            "expensive ones announce themselves months in advance. A proper "
            "annual service catches them; a fifteen-minute look at the front "
            "panel does not."
        ),
        "body": [
            ("What an annual service covers",
             "Flue gas analysis against the manufacturer's figures, seals and "
             "combustion chamber inspection, gas rate and working pressure "
             "check, safety device testing, condensate and pressure vessel "
             "check, and a written record. If the reading is out we tell you "
             "what it means rather than ticking a box."),
            ("Repairs and diagnostics",
             "Pressure loss, lockouts, cold radiators, noisy pumps, leaking "
             "cylinders and failed diverter valves. We diagnose before we "
             "quote, and if a repair is not economic on an old appliance we "
             "will say so plainly instead of replacing parts one at a time."),
            ("Landlord gas safety certificates",
             "CP12 certificates for landlords and letting agents across "
             "Somerset and North Somerset, with reminders before the renewal "
             "date so a portfolio never lapses. Multi-property visits can be "
             "booked in one appointment."),
        ],
        "bullets": [
            "Annual boiler services with a written record",
            "Breakdown diagnosis and repair",
            "Landlord gas safety certificates (CP12)",
            "Power flushing and magnetic filter fitting",
            "Radiator, valve and thermostat replacement",
            "Unvented cylinder servicing (G3 qualified)",
        ],
        "faq_slugs": ["service-frequency", "cp12", "pressure-loss"],
        "related": ["annual-service-plans", "boiler-installation",
                    "emergency-plumbing"],
    },
    {
        "slug": "air-source-heat-pumps",
        "nav": "Air source heat pumps",
        "h1": "Air source heat pump installation in Somerset",
        "title": "Air Source Heat Pump Installation Somerset | £7,500 Grant",
        "meta": (
            "Air source heat pump design, installation and servicing across "
            "Somerset. We handle the {grant} Boiler Upgrade Scheme paperwork "
            "and size the system on a full heat loss survey."
        ).format(grant=BUS_GRANT),
        "summary": (
            "Heat pump design, installation and servicing, with the {grant} "
            "grant paperwork handled for you."
        ).format(grant=BUS_GRANT),
        "icon": "heatpump",
        "intro": (
            "A heat pump that has been designed properly is quiet, cheap to "
            "run and heats the house to temperature in a Somerset winter. One "
            "that has been guessed at is none of those things. The difference "
            "is the survey, not the badge on the unit."
        ),
        "body": [
            ("We start with a heat loss survey",
             "Every room is measured and calculated against its fabric, "
             "glazing and exposure. That produces the flow temperature the "
             "system has to run at, which in turn tells us which radiators "
             "need changing and what size unit the property actually needs. "
             "We give you those numbers before you commit to anything."),
            ("Designed for low flow temperatures",
             "Heat pumps are efficient when they run cool. We design to the "
             "lowest flow temperature the house will tolerate, upsize the "
             "emitters that need it, and set the weather compensation curve "
             "on commissioning so the system modulates instead of cycling."),
            ("Grants and paperwork",
             "The Boiler Upgrade Scheme pays {grant} towards an air source "
             "heat pump on eligible properties in England and Wales. We check "
             "eligibility, apply on your behalf and deduct the grant from your "
             "quote, so you never pay it out and claim it back."
             .format(grant=BUS_GRANT)),
        ],
        "bullets": [
            "Room-by-room heat loss surveys",
            "Air source heat pump supply and installation",
            "Radiator and emitter upgrades for low flow temperatures",
            "Hot water cylinder replacement and G3 unvented work",
            "Annual heat pump servicing and maintenance",
            "Boiler Upgrade Scheme applications handled end to end",
        ],
        "faq_slugs": ["heat-pump-grant", "heat-pump-cost", "heat-pump-radiators",
                      "mcs"],
        "related": ["grants", "finance", "boiler-installation"],
    },
    {
        "slug": "plumbing-and-bathrooms",
        "nav": "Plumbing & bathrooms",
        "h1": "Plumbing and bathroom installation",
        "title": "Plumber Weston-super-Mare & Taunton | Bathroom Fitting",
        "meta": (
            "General plumbing and full bathroom installations across Somerset: "
            "taps, showers, cylinders, underfloor heating and bathroom "
            "fit-outs by one team from strip-out to snagging."
        ),
        "summary": (
            "Everyday plumbing and complete bathroom installations, managed by "
            "one team start to finish."
        ),
        "icon": "tap",
        "intro": (
            "The small jobs matter as much as the big ones; they are how most "
            "customers meet us. We turn up when we said we would, protect the "
            "floors, and clear up before we leave."
        ),
        "body": [
            ("Everyday plumbing",
             "Taps, ball valves, stop taps, waste and soil pipework, outside "
             "taps, immersion heaters, pumps, water softeners and mains "
             "pressure problems. If it carries water in a domestic property, "
             "we work on it."),
            ("Bathroom installations",
             "Full bathrooms, en-suites, shower rooms and accessible "
             "wet rooms. We handle strip-out, first fix, tiling, second fix, "
             "electrics through our qualified partner and the final snagging "
             "list, one point of contact rather than four trades to chase."),
            ("Cylinders and underfloor heating",
             "Unvented cylinder installation and servicing to G3, vented "
             "cylinder replacement, and wet underfloor heating for extensions "
             "and renovations, zoned and balanced on commissioning."),
        ],
        "bullets": [
            "Complete bathroom and en-suite installations",
            "Wet rooms and accessible bathing",
            "Taps, showers, toilets, basins and waste",
            "Unvented hot water cylinders (G3)",
            "Wet underfloor heating",
            "Outside taps, stop taps and mains pressure work",
        ],
        "faq_slugs": ["bathroom-time", "bathroom-supply"],
        "related": ["emergency-plumbing", "boiler-installation", "finance"],
    },
    {
        "slug": "emergency-plumbing",
        "nav": "Emergency call-outs",
        "h1": "Emergency plumbing and heating call-outs",
        "title": "Emergency Plumber Weston-super-Mare | Leaks & No Heating",
        "meta": (
            "Emergency plumber covering Weston-super-Mare, Taunton and "
            "surrounding Somerset. Burst pipes, leaks, no hot water and boiler "
            "breakdowns. Call 01934 440290."
        ),
        "summary": (
            "Burst pipes, leaks, no heating and no hot water: same-day where "
            "we can get to you."
        ),
        "icon": "alert",
        "intro": (
            "Water where it should not be does damage by the minute. If you "
            "have a burst, turn the water off at the stop tap first, then "
            "call us."
        ),
        "body": [
            ("What counts as an emergency",
             "A burst or leaking pipe, water coming through a ceiling, no "
             "heating or hot water in cold weather, a boiler leaking water, a "
             "blocked or overflowing soil stack, or any smell of gas. If you "
             "smell gas, leave the property and call the National Gas "
             "Emergency Service on 0800 111 999 before you call us."),
            ("How we prioritise",
             "Service-plan customers are seen first, then vulnerable "
             "households and properties with active water damage. We will tell "
             "you honestly on the phone when we can be with you rather than "
             "promising an hour and arriving at six."),
            ("What it costs",
             "You are told the call-out charge and the hourly rate before we "
             "set off, and we confirm the repair cost before starting work. "
             "Nothing is invoiced that you have not already agreed."),
        ],
        "bullets": [
            "Burst and leaking pipes",
            "No heating or no hot water",
            "Boiler breakdowns and lockouts",
            "Overflowing tanks and cisterns",
            "Blocked soil and waste pipes",
            "Leak detection and pipe repair",
        ],
        "faq_slugs": ["emergency-hours", "emergency-cost", "stop-tap"],
        "related": ["annual-service-plans", "boiler-servicing-and-repairs",
                    "plumbing-and-bathrooms"],
    },
    {
        "slug": "annual-service-plans",
        "nav": "Annual service plans",
        "h1": "Annual service plans",
        "title": "Boiler & Heat Pump Service Plans | EcoHeat Somerset",
        "meta": (
            "Spread the cost of your annual service and get priority "
            "call-outs. Monthly or annual payment, no exit fee, and every plan "
            "includes a full manufacturer-specification service."
        ),
        "summary": (
            "Spread the cost of your annual service and jump the queue when "
            "something goes wrong."
        ),
        "icon": "shield",
        "intro": (
            "A service plan does two things: it keeps your warranty valid by "
            "making sure the annual service actually happens, and it puts you "
            "at the front of the queue in the week when everyone's heating "
            "fails at once."
        ),
        "body": [
            ("How payment works",
             "Every plan can be paid monthly by Direct Debit or annually in "
             "one payment. Annual payment saves the equivalent of one monthly "
             "instalment. Plans run for twelve months, renew only with your "
             "agreement, and carry no exit fee: cancel with 30 days' notice "
             "and you pay for the cover you have used."),
            ("What every plan includes",
             "A full annual service to manufacturer specification with a "
             "written record, a service reminder before your renewal date so "
             "the warranty never lapses, priority booking ahead of non-plan "
             "customers, and no call-out charge during working hours."),
            ("What is not included",
             "Parts and labour on repairs are quoted separately unless your "
             "plan states otherwise, and pre-existing faults found at the "
             "first service are excluded. We tell you what is wrong and what "
             "it costs to put right; you decide."),
        ],
        "bullets": [],
        "faq_slugs": ["plan-cancel", "plan-parts", "plan-price"],
        "related": ["boiler-servicing-and-repairs", "emergency-plumbing",
                    "air-source-heat-pumps"],
    },
]

# ---------------------------------------------------------------------------
# Service plans
# ---------------------------------------------------------------------------
# NEEDS SIGN-OFF -- prices.
#   ``monthly`` and ``annual`` are published to the public site verbatim.
#   Leave a value as None and the card shows "Call for price" instead of a
#   figure, so the site can go live before pricing is agreed without ever
#   advertising a number EcoHeat has not approved.
# Recommended opening prices are in README.md; enter them here to publish.

PLANS = [
    {
        "slug": "essential",
        "name": "Essential",
        "for": "Gas or LPG boiler, owner-occupied",
        "monthly": None,
        "annual": None,
        "featured": False,
        "includes": [
            "Full annual boiler service to manufacturer specification",
            "Written service record and Benchmark update",
            "Annual service reminder so your warranty stays valid",
            "Priority booking ahead of non-plan customers",
            "No call-out charge, Mon-Fri 07:30-17:30",
            "10% off any parts fitted during the plan year",
        ],
        "excludes": [
            "Parts and repair labour (quoted before any work starts)",
            "Faults already present at the first service",
        ],
    },
    {
        "slug": "complete",
        "name": "Complete",
        "for": "Boiler, controls and full heating system",
        "monthly": None,
        "annual": None,
        "featured": True,
        "includes": [
            "Everything in Essential",
            "Unlimited breakdown call-outs, labour included",
            "Cover for boiler, controls, pump, valves and radiators",
            "Emergency response outside working hours at no extra call-out",
            "Annual system health check: pressure, inhibitor and filter",
            "Magnetic filter cleaned and re-dosed each year",
        ],
        "excludes": [
            "Replacement parts (10% discount applies)",
            "Boilers over 15 years old or beyond economic repair",
        ],
    },
    {
        "slug": "renewables",
        "name": "Renewables",
        "for": "Air source heat pump and hot water cylinder",
        "monthly": None,
        "annual": None,
        "featured": False,
        "includes": [
            "Full annual heat pump service to manufacturer specification",
            "Unvented cylinder safety check (G3)",
            "Refrigerant circuit and F-Gas leak check",
            "Weather compensation curve reviewed and re-optimised",
            "Efficiency report: actual seasonal performance vs design",
            "Priority booking and no working-hours call-out charge",
        ],
        "excludes": [
            "Parts and repair labour (quoted before any work starts)",
            "Systems not commissioned to MCS standards",
        ],
    },
]

# ---------------------------------------------------------------------------
# FAQs -- rendered on /faq/ with FAQPage schema, and surfaced on the relevant
# service pages via ``faq_slugs`` above.
# ---------------------------------------------------------------------------

FAQ_GROUPS = [
    ("Heat pumps and grants", [
        ("heat-pump-grant",
         "How much is the heat pump grant and do I have to claim it back?",
         "The Boiler Upgrade Scheme pays {grant} towards an air source heat "
         "pump on eligible properties in England and Wales. You never pay it "
         "out and claim it back: we apply on your behalf and the grant is "
         "deducted from your quote, so you only ever pay the balance."
         .format(grant=BUS_GRANT)),
        ("heat-pump-eligible",
         "Which properties are eligible for the Boiler Upgrade Scheme?",
         "Domestic properties in England and Wales with a valid EPC that has "
         "no outstanding loft or cavity wall insulation recommendations. The "
         "property must be replacing a fossil fuel system (gas, oil, LPG or "
         "electric), and new build properties are generally excluded. We check "
         "your EPC before quoting and tell you where you stand."),
        ("heat-pump-cost",
         "What does an air source heat pump cost to install?",
         "The honest answer is that it depends on the heat loss of your "
         "property and how many radiators need upsizing, which is exactly what "
         "the survey establishes. We give you a fixed written price after the "
         "heat loss survey, with the {grant} grant already deducted, and there "
         "is no charge for the survey.".format(grant=BUS_GRANT)),
        ("heat-pump-radiators",
         "Do I need to replace all my radiators for a heat pump?",
         "Usually not all of them. Heat pumps run at lower flow temperatures "
         "than a boiler, so each radiator has to give out the same heat at a "
         "cooler water temperature. In a typical Somerset home a handful need "
         "upsizing and the rest are fine. The heat loss survey tells us "
         "room by room, and that list forms part of your quote."),
        ("heat-pump-cold",
         "Do heat pumps work in cold weather?",
         "Yes. Air source heat pumps extract heat from outside air well below "
         "freezing, and they are the standard heating system in Scandinavia. "
         "Efficiency falls as it gets colder, which is why the system is sized "
         "against the coldest design temperature for the region rather than an "
         "average day."),
        ("mcs",
         "Are you MCS certified?",
         None),  # filled in below from MCS_STATUS
    ]),
    ("Boilers", [
        ("boiler-install-time",
         "How long does a boiler installation take?",
         "A straight combi swap in the same position is usually one day. "
         "Moving the boiler, converting from a conventional system to a combi, "
         "or replacing a back boiler typically takes two to three days. We "
         "give you the number of days in writing with the quote, and you will "
         "not be left without hot water overnight without being told first."),
        ("boiler-brands",
         "Which boiler brands do you fit?",
         "We fit the mainstream manufacturers (Worcester Bosch, Vaillant, "
         "Ideal, Baxi and Viessmann among others) and we are not tied to any "
         "one of them. That means we can recommend on the merits of the "
         "appliance and the warranty rather than on a supplier target."),
        ("fixed-price",
         "Is the quote a fixed price?",
         "Yes. Once we have surveyed the property the written quote is the "
         "price you pay. The only thing that changes it is you asking for "
         "additional work, or something genuinely hidden (an asbestos flue "
         "seal, for instance), in which case we stop, explain and re-quote "
         "before carrying on."),
        ("pressure-loss",
         "Why does my boiler keep losing pressure?",
         "Almost always a leak somewhere in the system or a failed expansion "
         "vessel. If the pressure drops over weeks it is usually a small leak "
         "on pipework or a radiator valve; over hours it is usually the "
         "pressure relief valve or the vessel. Both are diagnosable in one "
         "visit and neither should be topped up and ignored."),
        ("service-frequency",
         "How often does a boiler need servicing?",
         "Every twelve months, and manufacturers make it a warranty condition: "
         "miss a service and a 10-year warranty can be void when you need "
         "it. Our service plans include a reminder before the anniversary "
         "date for exactly this reason."),
        ("cp12",
         "How quickly can I get a landlord gas safety certificate?",
         "Usually within a few working days, and we can book multiple "
         "properties into one visit for portfolio landlords and letting "
         "agents. We also diary your renewal date and remind you before the "
         "certificate expires."),
    ]),
    ("Bathrooms and plumbing", [
        ("bathroom-time",
         "How long does a bathroom installation take?",
         "A typical family bathroom is 5 to 10 working days from strip-out to "
         "snagging, depending on tiling and whether anything needs moving. You "
         "get a day-by-day schedule before we start so you know which days you "
         "are without the room."),
        ("bathroom-supply",
         "Can I supply my own bathroom suite?",
         "Yes, and plenty of customers do. We will check what you have chosen "
         "before you order it: the most common problem is a shower or tap "
         "that the property's water pressure cannot run properly, which is far "
         "cheaper to catch before delivery than after tiling."),
        ("stop-tap",
         "Where is my stop tap and why does it matter?",
         "Most commonly under the kitchen sink, sometimes in a downstairs "
         "cloakroom or under the stairs. Find it now and check it turns: in a "
         "burst, the thirty seconds it takes to shut the water off is the "
         "difference between a wet floor and a replacement ceiling."),
    ]),
    ("Booking, plans and payment", [
        ("emergency-hours",
         "Do you offer emergency call-outs?",
         "Yes, for burst pipes, leaks, and no heating or hot water. Ring "
         "{phone} and you will get an honest answer about when we can be with "
         "you. Service-plan customers are prioritised. If you smell gas, leave "
         "the property and call the National Gas Emergency Service on 0800 111 "
         "999 first.".format(phone=BUSINESS["phone"])),
        ("emergency-cost",
         "What does an emergency call-out cost?",
         "You are told the call-out charge and hourly rate on the phone before "
         "we set off, and the repair cost is confirmed before work starts. "
         "Nothing appears on the invoice that you have not already agreed."),
        ("plan-price",
         "How much is a service plan and can I pay annually?",
         "Every plan can be paid monthly by Direct Debit or annually in one "
         "payment, and paying annually saves the equivalent of one monthly "
         "instalment. Current prices and exactly what each plan covers are set "
         "out on the service plans page."),
        ("plan-cancel",
         "Can I cancel a service plan?",
         "Yes. Plans run for twelve months and renew only with your agreement. "
         "Cancel at any time with 30 days' notice and you pay only for the "
         "cover you have used; there is no exit fee."),
        ("plan-parts",
         "Are parts included in a service plan?",
         "On the Essential and Renewables plans, parts and repair labour are "
         "quoted separately and plan customers get 10% off parts. The Complete "
         "plan includes breakdown labour; replacement parts are still charged, "
         "with the same discount."),
        ("areas",
         "Which areas do you cover?",
         "We are based at Edingworth between Weston-super-Mare and "
         "Burnham-on-Sea, and cover Somerset and North Somerset, including "
         "Taunton, Bridgwater, Cheddar, Wells, Clevedon and Nailsea. If you "
         "are just outside, ring and ask; we will give you a straight yes or "
         "no rather than quote and cancel."),
        ("finance-q",
         "Do you offer finance?",
         "Yes, on installations over a qualifying value, through an "
         "FCA-authorised finance provider. Options include interest-free "
         "periods and longer terms with interest. Full details, including "
         "representative APR, are on the finance page."),
        ("payment",
         "How do I pay and do you take a deposit?",
         "Bank transfer, card or cash. On installations we take a deposit to "
         "cover materials, with the balance due on completion and "
         "commissioning, never before the job is finished and working."),
    ]),
]

# Resolve the accreditation answer from the flag at the top of the file.
_MCS_ANSWERS = {
    "own": (
        "Yes. EcoHeat is MCS certified under registration {num}, which is what "
        "allows us to apply for the {grant} Boiler Upgrade Scheme grant on "
        "your behalf. You can verify our certification on the MCS register at "
        "mcscertified.com."
    ),
    "partner": (
        "Our air source heat pump installations are designed, commissioned and "
        "certified with our MCS-accredited installation partner. That "
        "accreditation is what makes your installation eligible for the "
        "{grant} Boiler Upgrade Scheme grant, and the certificate is issued in "
        "your name on completion. Day to day you deal with EcoHeat: we survey "
        "the property, carry out the work and look after it afterwards."
    ),
}


def _resolve_mcs_answer():
    text = _MCS_ANSWERS[MCS_STATUS].format(num=MCS_NUMBER, grant=BUS_GRANT)
    for _title, items in FAQ_GROUPS:
        for i, (slug, q, a) in enumerate(items):
            if slug == "mcs" and a is None:
                items[i] = (slug, q, text)
    return text


MCS_ANSWER = _resolve_mcs_answer()

MCS_BADGE = (
    "MCS certified, reg. {num}".format(num=MCS_NUMBER) if MCS_STATUS == "own"
    else "Heat pumps installed with our MCS-accredited partner"
)

FAQ_INDEX = {slug: (q, a) for _t, items in FAQ_GROUPS for slug, q, a in items}

# ---------------------------------------------------------------------------
# Case studies -- shown on /projects/.
# Photographs are supplied by EcoHeat; see assets/img/photos/README.md.
# Every entry's ``photos`` list holds (filename, alt-text) pairs. Where the file
# is not present the build renders a labelled brand panel instead of a gap, and
# never a stock photograph.
# ---------------------------------------------------------------------------

CASE_STUDIES = [
    {
        "slug": "heat-pump-edingworth",
        "title": "Oil boiler to air source heat pump, Edingworth",
        "type": "Air source heat pump",
        "location": "Edingworth, North Somerset",
        "summary": (
            "A four-bedroom farmhouse running on an ageing oil boiler, "
            "converted to an air source heat pump with the Boiler Upgrade "
            "Scheme grant deducted from the quote."
        ),
        "challenge": (
            "Solid stone walls and a large hot water demand meant a "
            "like-for-like swap would have run at too high a flow temperature "
            "to be efficient."
        ),
        "solution": (
            "A room-by-room heat loss survey identified six radiators to "
            "upsize and a new unvented cylinder. The system was designed "
            "around a low flow temperature with weather compensation set on "
            "commissioning."
        ),
        "outcome": (
            "The property came off oil entirely, and the grant was applied "
            "before invoice so the customer never had to fund it up front."
        ),
        "photos": [
            ("heat-pump-edingworth-before.jpg",
             "Ageing oil boiler and pipework in a Somerset farmhouse utility "
             "room before EcoHeat replaced it with a heat pump"),
            ("heat-pump-edingworth-after.jpg",
             "Air source heat pump unit installed on an exterior wall of a "
             "farmhouse near Edingworth by EcoHeat"),
        ],
    },
    {
        "slug": "combi-swap-weston",
        "title": "Back boiler removal and combi installation, Weston-super-Mare",
        "type": "Boiler installation",
        "location": "Weston-super-Mare, North Somerset",
        "summary": (
            "A 1970s back boiler and gravity hot water system replaced with a "
            "modern combination boiler and smart controls in two days."
        ),
        "challenge": (
            "Removing a back boiler means taking out the fireplace unit, "
            "sealing the chimney and re-routing gas and water, a job that is "
            "routinely under-quoted as a straight swap."
        ),
        "solution": (
            "Back boiler and tanks removed, chimney safely capped and "
            "ventilated, new gas run and condensate route installed, system "
            "power flushed and a magnetic filter fitted."
        ),
        "outcome": (
            "Loft and airing cupboard freed up, hot water on demand, and the "
            "manufacturer's extended warranty registered on completion."
        ),
        "photos": [
            ("combi-swap-weston-before.jpg",
             "Original 1970s back boiler behind a fireplace in a "
             "Weston-super-Mare home before removal"),
            ("combi-swap-weston-after.jpg",
             "Newly installed combination boiler with magnetic filter and "
             "tidy pipework fitted by EcoHeat"),
        ],
    },
    {
        "slug": "bathroom-burnham",
        "title": "Full bathroom refit, Burnham-on-Sea",
        "type": "Bathroom installation",
        "location": "Burnham-on-Sea, Somerset",
        "summary": (
            "A dated family bathroom stripped and refitted as a walk-in shower "
            "room, completed in eight working days by one team."
        ),
        "challenge": (
            "Low mains pressure meant the customer's chosen shower would never "
            "have performed, and the existing waste run had inadequate fall."
        ),
        "solution": (
            "Pressure tested before ordering, specification changed to a "
            "suitable shower, waste re-run to correct fall, and the room "
            "re-boarded, tiled and second-fixed by the same team."
        ),
        "outcome": (
            "Delivered on the day-by-day schedule agreed at the start, with "
            "the snagging list cleared before final invoice."
        ),
        "photos": [
            ("bathroom-burnham-before.jpg",
             "Dated bathroom with over-bath shower in a Burnham-on-Sea home "
             "before EcoHeat's refit"),
            ("bathroom-burnham-after.jpg",
             "Completed walk-in shower room with tiled walls installed by "
             "EcoHeat in Burnham-on-Sea"),
        ],
    },
]

# ---------------------------------------------------------------------------
# Reviews.
# Genuine customer reviews only. Add entries here as they are received on
# Google or Facebook, with the reviewer's consent to be quoted. Until then the
# reviews page links to the Facebook page rather than showing invented quotes,
# and no AggregateRating schema is emitted (publishing fabricated review markup
# is a manual-action risk with Google and a CMA compliance risk).
# ---------------------------------------------------------------------------

REVIEWS = []  # {"name":, "location":, "date": "2026-05-01", "rating": 5, "text":, "source": "Google"}
