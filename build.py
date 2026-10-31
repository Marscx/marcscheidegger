"""Erzeugt alle HTML-Seiten von marcscheidegger.ch.

Inhalte (Projekte, Konzerte, Texte) hier ändern, dann:  python3 build.py
"""
import html, os, re

OUT = os.path.dirname(os.path.abspath(__file__))
V = 4  # Cache-Version für CSS/JS – bei Änderungen an site.css / site.js erhöhen

NAV = [("index.html", "Home"), ("projekte.html", "Projekte"), ("chronologie.html", "Chronologie"),
       ("lernen.html", "Lernen"), ("kontakt.html", "Kontakt")]

E = html.escape
CUR = ' aria-current="page"'

def page(fname, title, desc, body, current=None):
    navlis = "\n".join(
        f'                <li><a href="{h}"{CUR if h == (current or fname) else ""}>{t}</a></li>'
        for h, t in NAV)
    full_title = "Marc Scheidegger – Gitarre & Gesang" if fname == "index.html" else f"{title} – Marc Scheidegger"
    doc = f"""<!doctype html>
<html lang="de-CH">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{E(full_title)}</title>
    <meta name="description" content="{E(desc)}">
    <meta property="og:title" content="{E(full_title)}">
    <meta property="og:description" content="{E(desc)}">
    <meta property="og:image" content="https://marcscheidegger.ch/img/hero-jvf-earlclub.jpg">
    <meta property="og:type" content="website">
    <meta name="theme-color" content="#0b1220">
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="css/site.css?v={V}">
    <script src="js/site.js?v={V}"></script>
</head>
<body>
    <a class="skip" href="#inhalt">Zum Inhalt</a>
    <header class="site-header">
        <div class="wrap">
            <a class="brand" href="index.html">Marc <span>Scheidegger</span></a>
            <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menü</button>
            <nav class="nav" id="nav" aria-label="Hauptnavigation">
                <ul>
{navlis}
                </ul>
            </nav>
        </div>
    </header>

    <main id="inhalt">
{body.rstrip()}
    </main>

    <footer class="site-footer">
        <div class="wrap">
            <p>© <span data-year>2026</span> Marc Scheidegger</p>
            <ul>
                <li><a href="https://www.instagram.com/marscx/">Instagram</a></li>
                <li><a href="https://www.youtube.com/watch?v=AC6F9rHJwL4">YouTube</a></li>
                <li><a href="https://www.linkedin.com/in/marc-scheidegger-470537ab/">LinkedIn</a></li>
                <li><a href="impressum.html">Impressum</a></li>
                <li><a href="datenschutz.html">Datenschutz</a></li>
            </ul>
        </div>
    </footer>
</body>
</html>
"""
    with open(os.path.join(OUT, fname), "w") as f:
        f.write(doc)

# ---------------------------------------------------------------- Projekte
# (slug, name, bild, zeitraum, besetzung, fakten[(jahr, text)], links[(url, text)], gruppe)
P = [
    ("julian-von-fluee", "Julian von Flüe Trio", "julian-von-fluee-trio.jpg", "seit 2014",
     "Julian von Flüe – Akkordeon · Marc Scheidegger – Gitarre · Matthias Abächerli – Bass (seit 2021)",
     [("2014 – heute", "zahlreiche Konzerte"),
      ("2018", "CD-Produktion «Drive»"),
      ("2019", "CD-Taufe"),
      ("2019", "TV Oberwallis"),
      ("2021", "Matthias Abächerli kommt am Bass dazu – das Trio in der heutigen Besetzung"),
      ("2022", "CD-Produktion «Dur D’Altstadt» abgeschlossen"),
      ("2022", "Auftritt in der SRF-Sendung Potzmusig"),
      ("2023", "CD-Taufe am 11. März, Chollerhalle Zug"),
      ("2023", "Zwei Auftritte auf der Hauptbühne des Premio Internazionale della Fisarmonica, Castelfidardo (Italien)"),
      ("2024", "CD «Alpine Folk» mit 13 neuen Kompositionen, Plattentaufe am 23. November in der Galvanik Zug"),
      ("2025", "Tournee «Alpine Folk», u. a. Stanser Musiktage und Pregny Alp Festival; Interview bei SRF Musikwelle"),
      ("2025", "SRF «Typisch Volksmusik Sessions»"),
      ("2026", "Auftritt in der SRF-Sendung Potzmusig (21. Februar)"),
      ("2026", "Landäbärg Unplugged in Sarnen und Küstenklänge auf der MS Switzerland")],
     [("https://julianvonfluee.ch/", "Band-Website"), ("https://julianvonfluee.ch/live/", "Alle Konzerte")], "aktuell"),
    ("mala-oreen", "Mala Oreen", "mala-oreen.jpg", "seit 2019",
     "Mala Oreen – Gesang, Fiddle, Gitarre · Rafael Woll – Schlagzeug, Gesang · Simon Itten – Kontrabass, Gesang · Marc Scheidegger – Gitarre, Mandoline, Gesang",
     [("2019 – heute", "zahlreiche Konzerte"),
      ("2021", "Album «AWAKE» (5. November), Plattentaufe im Chäslager Stans und Konzert in der Jazzkantine")],
     [("https://www.malaoreen.com/", "Website"), ("https://malaoreen.bandcamp.com/", "Album auf Bandcamp")], "aktuell"),

    ("boogiefox", "Boogiefox", "boogiefox.jpg", "2013 – 2024",
     "Anet Zemp – Gesang, Gitarre · Ralph Sonderegger – Kontrabass, Gesang · Marc Scheidegger – Gitarre, Gesang",
     [("2013 – 2024", "zahlreiche Konzerte")],
     [], "frueher"),
    ("mat-and-yvonne", "Mat and Yvonne with Friends", "mat-and-yvonne.jpg", "2021 – 2022",
     "Yvonne Moore – Gesang · Mat Callahan – Gesang, Gitarre, Produktion · Arno Troxler – Schlagzeug · Andre Poussaz – Kontrabass · Julian von Flüe – Akkordeon · Sibylle Fässler, Nadja Stoller, Konrad – Gesang · Marc Scheidegger – Gitarre",
     [("2021", "Konzert im Café Mokka Thun"), ("2022", "Videodreh")], [], "frueher"),
    ("moe", "Moë", "moe.jpg", "2002 – 2011",
     "Anet Zemp – Gesang · Ephrem Lüchinger – Keyboards · Manuel Rindlisbacher – Bass · Dominik Burkhalter – Schlagzeug · Marc Scheidegger – Gitarre",
     [("2002", "Luzerner Werkbeiträge"), ("2002", "Popkredit Zürich"), ("2003", "Clubtour"),
      ("2008", "CD-Produktion und Clubtour"), ("2011", "CD-Produktion und Clubtour")], [], "frueher"),
    ("kubus", "Kubus", "kubus.jpg", "1999 – 2006",
     "Rafael Woll – Schlagzeug · Marcel Stalder – Bass · Adrian Pflugshaupt – Saxofon · Peter Estermann – Piano · Fabian Stübi – Elektronik · Marc Scheidegger – Gitarre, Elektronik",
     [("1999", "Luzerner Werkbeiträge"), ("2001", "Jazzfestival Kaunas, Litauen"),
      ("2003", "Jazzfestival Willisau, Hauptbühne"), ("2006", "Anerkennungspreis der Stadt Luzern")], [], "frueher"),
    ("stimmreise", "stimmreise.ch", None, "2010 – 2014",
     "Nadja Räss – Gesang · Dani Häusler – Klarinette, Gesang · Richard Hugener – Bass, Gesang · Marc Scheidegger – Gitarre, Gesang",
     [("2010", "CD-Produktion «Stimmreise 2»"), ("2010 – 2014", "zahlreiche Konzerte in der Schweiz und in Österreich"),
      ("2014", "SRF Potzmusig")], [], "frueher"),
    ("open-mic-band", "Open Mic Band Kaufleuten", None, "2004 – 2006",
     "Michel Gsell – Bass · Arno Troxler – Schlagzeug · Ephrem Lüchinger – Keyboards · Kungfu Horns · Marc Scheidegger – musikalische Leitung, Gitarre",
     [("2004 – 2006", "einmal im Monat im Kaufleuten Zürich")], [], "frueher"),

    ("patrick-jonsson", "Patrick Jonsson", "patrick-jonsson.jpg", "2009 – 2013",
     "Patrick Jonsson – Gesang",
     [("2009", "CD-Produktion «This Is the Sky»"), ("2009 – 2010", "Konzerttour"),
      ("2011", "CD-Produktion «People Are Strange»"), ("2013", "Videoproduktion «Better Morning»")], [], "begleit"),
    ("andrew-bond", "Andrew Bond", None, "2016 – 2018",
     "Andrew Bond – Gesang, Songs · Lukas Landis – Schlagzeug · Stef Veyr – Kontrabass · Andi Pupato – Perkussion · Marc Scheidegger – Gitarre",
     [("2016", "Kinderkonzerte und Studioaufnahmen"), ("2016", "Kids on Ice, Hallenstadion Zürich"),
      ("2018", "Kids on Ice, Hallenstadion Zürich")], [], "begleit"),
    ("emel", "Emel", None, "1999 – 2017",
     "Emel – Gesang",
     [("1999", "Konzerttour"), ("2007", "Konzerte, Support für Rihanna in der St. Jakobshalle Basel"),
      ("2017", "Singleproduktion «Dragon» mit Rhani Krija, Perkussion"),
      ("2017", "Konzert an der Badenfahrt mit Rhani Krija")], [], "begleit"),
    ("yvonne-moore", "Yvonne Moore", None, "1999 · 2015 – 2018",
     "Yvonne Moore – Gesang · Arno Troxler – Schlagzeug · Andre Poussaz – Kontrabass · Mat Callahan – Gesang, Gitarre, Produktion",
     [("1999", "CD-Produktion «Nomad», zahlreiche Konzerte"),
      ("2015 – 2018", "Konzerte mit dem Programm «Bob Mose Songs»")], [], "begleit"),
    ("martina-linn", "Martina Linn", None, "2012 – 2015",
     "Martina Linn – Gesang, Gitarre · Marc Scheidegger – Gitarre, Gesang",
     [("2012", "Gastmusiker, Soundfarm Studios Obernau (Marco Jencarelli)"),
      ("2014", "Konzert im Stadtkeller Luzern"),
      ("2015", "Gastmusiker, Soundfarm Studios Obernau (Marco Jencarelli)"),
      ("2015", "CD-Taufe im Treibhaus Luzern")], [], "begleit"),
    ("guy-vincent", "Guy Vincent", None, "2010",
     "Michel Gsell – Gesang, Gitarre · Arno Troxler – Schlagzeug · Peter Estermann – Keyboards · Simon Kaufmann – Bass, Gesang · Marc Scheidegger – Gitarre",
     [("2010", "CD-Produktion «33 Minutes»")], [], "begleit"),
    ("cyrill-camenzind", "Cyrill Camenzind", None, "2013",
     "Cyrill Camenzind – Produzent",
     [("2013", "Studioaufnahmen für die Vorentscheidung des Eurovision Song Contest")], [], "begleit"),
]

INTRO = {
    "julian-von-fluee": "Alpine Folk: Julian von Flües eigene Kompositionen, verwurzelt in der Musik des Alpenraums und inspiriert von amerikanischer Country- und Folkmusik. Aktuelles Album: «Alpine Folk» (2024).",
    "mala-oreen": "«Songs for and from the heart» – Americana und Folk mit mehrstimmigem Gesang. Das Album «AWAKE» nannte Americana Highways «one of the year’s best».",
}

# ---------------------------------------------------------------- Clips
# (quelle, id, titel, jahr) – nur Clips, in denen Marc nachweislich mitspielt.
# Vorschaubilder liegen lokal in img/clips/; das Video lädt erst nach Klick (Datenschutz).
CLIPS = {
    "julian-von-fluee": [
        ("srf", "017d68a1-7ecb-4124-a484-b73eafa8a137", "SRF Typisch Volksmusik Sessions", "2025"),
        ("yt", "jCNFVanFAxY", "Neue CD «Alpine Folk»", "2024"),
        ("yt", "AC6F9rHJwL4", "On the way to Castelfidardo", "2023"),
        ("srf", "c9a96bc2-3897-4d29-911a-1cc2ea4119a6", "SRF Potzmusig aus Kaiserstuhl", "2022"),
        ("yt", "HnTExtVyzM0", "Tango Nuevo", "2022"),
        ("yt", "No2nQ4fnL_8", "Caviano", "2021"),
    ],
    "mala-oreen": [
        ("yt", "jhvhz8U2mec", "Live in der Liebhaberei Rain", "2020"),
    ],
    "boogiefox": [
        ("yt", "Pf2XysrZIS4", "Über d’Liebi", "2016"),
    ],
    "moe": [
        ("yt", "NPvAOLSUiUI", "Sehnsucht (Album «inners»)", "2012"),
    ],
    "patrick-jonsson": [
        ("yt", "4kAg4MDMOpU", "A Better Morning (Videoclip)", "2013"),
    ],
}

def clip(kind, cid, title, year):
    if kind == "yt":
        embed = f"https://www.youtube-nocookie.com/embed/{cid}?autoplay=1&rel=0"
        url, thumb, src = f"https://www.youtube.com/watch?v={cid}", f"yt-{cid}.jpg", "YouTube"
    else:
        embed = f"https://www.srf.ch/play/embed?urn=urn:srf:video:{cid}&subdivisions=false"
        url, thumb, src = f"https://www.srf.ch/play/tv/redirect/detail/{cid}", f"srf-{cid[:8]}.jpg", "SRF"
    return f"""                            <figure class="clip">
                                <a class="clip-play" href="{url}" data-embed="{embed}" data-title="{E(title)}">
                                    <img src="img/clips/{thumb}" alt="" loading="lazy" width="960" height="540">
                                    <span class="clip-src">{src}</span>
                                    <span class="clip-icon" aria-hidden="true"></span>
                                    <span class="sr">Video abspielen: </span>
                                </a>
                                <figcaption>{E(title)} <span>{year}</span></figcaption>
                            </figure>"""

def clips(slug):
    if slug not in CLIPS:
        return ""
    return f"""
                        <div class="clips">
{chr(10).join(clip(*c) for c in CLIPS[slug])}
                        </div>
                        <p class="clip-note">Videos werden erst beim Abspielen von YouTube bzw. SRF geladen.</p>"""

def facts(fs):
    return "\n".join(f"                            <li><b>{E(y)}</b><span>{E(t)}</span></li>" for y, t in fs)

def project_row(p):
    slug, name, img, years, lineup, fs, links, _ = p
    btn = ("\n                        <div class=\"btns\">" + "".join(
        f'<a class="btn ghost" href="{u}">{E(t)} ↗</a>' for u, t in links) + "</div>") if links else ""
    intro = f'\n                        <p>{E(INTRO[slug])}</p>' if slug in INTRO else ""
    return f"""                <article class="project" id="{slug}">
                    <img src="img/{img}" alt="{E(name)} live" loading="lazy" width="1200" height="900">
                    <div>
                        <p class="years">{E(years)}</p>
                        <h3>{E(name)}</h3>{intro}
                        <p class="lineup">{E(lineup)}</p>
                        <ul class="facts">
{facts(fs)}
                        </ul>{btn}
                    </div>{clips(slug)}
                </article>"""

def compact_card(p):
    slug, name, img, years, lineup, fs, links, _ = p
    im = f'\n                    <img src="img/{img}" alt="{E(name)}" loading="lazy" width="1200" height="800">' if img else ""
    return f"""                <article class="card" id="{slug}">{im}
                    <div class="body">
                        <p class="years" style="color:var(--accent);font-weight:600;font-size:.9rem;margin:0 0 4px">{E(years)}</p>
                        <h3>{E(name)}</h3>
                        <p class="lineup">{E(lineup)}</p>
                        <ul class="facts">
{facts(fs)}
                        </ul>{clips(slug)}
                    </div>
                </article>"""

grp = lambda g: [p for p in P if p[7] == g]

# ---------------------------------------------------------------- Konzerte
# (datum JJJJ-MM-TT, zeit, band-slug, ort, link) – vergangene blendet site.js automatisch aus
KONZERTE = [
    ("2026-11-21", "20:00", "julian-von-fluee", "ARTick – Schlössli Mattstetten", "https://eventfrog.ch/de/p/konzerte/folk/julian-von-fluee-trio-alpine-folk-7462512049513359337.html"),
    ("2026-12-05", "18:00", "julian-von-fluee", "Alpine Folk im Roten Doppelpfeil «Churchill», Zürich", "https://www.sbb.ch/de/freizeit-ferien/ideen/angebot.html/zuege/folkmusik-churchill"),
    ("2027-01-22", "", "julian-von-fluee", "Kulturverein Ermitage, Beckenried", ""),
    ("2027-01-23", "", "julian-von-fluee", "Jazzclub Thalwil, feat. Roland von Flüe", ""),
    ("2027-01-30", "", "julian-von-fluee", "Anna Stüssi Haus, Dänikon", ""),
    ("2027-02-12", "20:00", "mala-oreen", "Dinner-Konzert, Frohe Aussicht, Oberrieden", "https://www.frohe-aussicht-oberrieden.ch"),
    ("2027-02-26", "", "julian-von-fluee", "Theater im Pfarrhauskeller, Waldenburg", ""),
    ("2027-03-18", "20:15", "julian-von-fluee", "Kleinkunstbühne Rathus-Schüür, Baar", ""),
    ("2027-03-19", "21:00", "julian-von-fluee", "Le Singe, Biel", ""),
    ("2027-04-10", "20:00", "julian-von-fluee", "Diogenes Theater, Altstätten", "https://diogenes-theater.ch/veranstaltung/julian-von-der-fluehe-trio-alpine-folk/"),
    ("2027-04-23", "20:00", "julian-von-fluee", "Kulturhalle Rothenburg", ""),
    ("2027-04-24", "19:30", "julian-von-fluee", "Kulturschopf Feldbach", ""),
    ("2027-10-16", "20:15", "julian-von-fluee", "Gaswerk Eventbar, Seewen", "https://www.gaswerk-eventbar.ch/veranstaltungen/julian-von-fluee-trio-ch/"),
    ("2027-10-22", "19:30", "julian-von-fluee", "Schloss Schauensee, Kriens", ""),
    ("2027-10-31", "17:00", "julian-von-fluee", "Kulturraum Marabu, Gelterkinden", ""),
]
MONATE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
BAND = {p[0]: p[1] for p in P}

def konzerte(limit=None):
    items = []
    for d, t, b, ort, url in KONZERTE:
        y, m, day = d.split("-")
        link = f' <a href="{url}">Infos ↗</a>' if url else ""
        zeit = f" · {t} Uhr" if t else ""
        items.append(f"""                    <li data-date="{d}">
                        <time datetime="{d}"><b>{int(day)}.</b> {MONATE[int(m) - 1]} {y}</time>
                        <div><strong>{E(BAND[b])}</strong><span>{E(ort)}{zeit}</span>{link}</div>
                    </li>""")
    lim = f' data-limit="{limit}"' if limit else ""
    return f"""                <ul class="gigs"{lim}>
{chr(10).join(items)}
                </ul>
                <p class="gigs-empty" hidden>Zurzeit sind keine Konzerte eingetragen.</p>"""

projekte = f"""        <section class="hero small">
            <img src="img/mat-and-yvonne.jpg" alt="" width="2000" height="1330">
            <div class="wrap">
                <span class="kicker">Bands &amp; Projekte</span>
                <h1>Auf der Bühne<br>und im Studio</h1>
                <p class="lead">Aktuelle Bands, frühere Projekte und Produktionen als Begleitmusiker – mit Besetzung und den wichtigsten Stationen.</p>
                <div class="btns">
                    <a class="btn" href="#aktuell">Aktuelle Bands</a>
                    <a class="btn ghost" href="#konzerte">Konzerte</a>
                    <a class="btn ghost" href="#frueher">Frühere Bands</a>
                    <a class="btn ghost" href="#begleit">Begleitmusiker &amp; Studio</a>
                </div>
            </div>
        </section>

        <section class="section" id="aktuell">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Heute</span>
                    <h2>Aktuelle Bands</h2>
                </div>
{chr(10).join(project_row(p) for p in grp("aktuell"))}
            </div>
        </section>

        <section class="section alt" id="konzerte">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Live</span>
                    <h2>Nächste Konzerte</h2>
                </div>
{konzerte()}
            </div>
        </section>

        <section class="section" id="frueher">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">1999 – 2024</span>
                    <h2>Frühere Bands</h2>
                </div>
                <div class="compact">
{chr(10).join(compact_card(p) for p in grp("frueher"))}
                </div>
            </div>
        </section>

        <section class="section alt" id="begleit">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Gastmusiker</span>
                    <h2>Begleitmusiker &amp; Studio</h2>
                    <p>Konzerte, Tourneen und Studioaufnahmen mit Sängerinnen, Sängern und Produzenten.</p>
                </div>
                <div class="compact">
{chr(10).join(compact_card(p) for p in grp("begleit"))}
                </div>
                <div class="btns"><a class="btn ghost" href="chronologie.html">Alles nach Jahren: zur Chronologie</a></div>
            </div>
        </section>
"""
page("projekte.html", "Projekte", "Bands und Projekte von Marc Scheidegger: Julian von Flüe Trio, Mala Oreen, Boogiefox sowie frühere Bands und Produktionen als Begleitmusiker.", projekte)

# ---------------------------------------------------------------- Chronologie
by_year = {}
for p in P:
    for y, t in p[5]:
        start = int(y[:4])
        m = re.search(r"–\s*(\d{4}|heute)", y)
        suffix = f" (bis {m.group(1)})" if m else ""
        by_year.setdefault(start, []).append((p[0], p[1], t + suffix))
years = sorted(by_year, reverse=True)

def year_block(y):
    items = "\n".join(
        f'                        <li><a href="projekte.html#{s}">{E(n)}</a> <span>– {E(t)}</span></li>'
        for s, n, t in by_year[y])
    return f"""                <li class="year" id="jahr-{y}">
                    <h2>{y}</h2>
                    <ul>
{items}
                    </ul>
                </li>"""

chrono = f"""        <section class="hero small plain">
            <div class="wrap">
                <span class="kicker">Chronologie</span>
                <h1>Seit 1999<br>unterwegs</h1>
                <p class="lead">Konzerte, CD-Produktionen, Festivals und Fernsehauftritte – Jahr für Jahr. Heute spiele ich im <a href="projekte.html#julian-von-fluee">Julian von Flüe Trio</a> und bei <a href="projekte.html#mala-oreen">Mala Oreen</a>.</p>
            </div>
        </section>

        <section class="section">
            <div class="wrap">
                <nav class="years-nav" aria-label="Jahre">
{chr(10).join(f'                    <a href="#jahr-{y}">{y}</a>' for y in years)}
                </nav>
                <ol class="timeline">
{chr(10).join(year_block(y) for y in years)}
                </ol>
            </div>
        </section>
"""
page("chronologie.html", "Chronologie", "Chronologie von Marc Scheidegger: Konzerte, CD-Produktionen, Festivals und TV-Auftritte seit 1999.", chrono)

# ---------------------------------------------------------------- Home
def band_card(slug, name, img, text):
    return f"""                    <a class="card" href="projekte.html#{slug}">
                        <img src="img/{img}" alt="{E(name)}" loading="lazy" width="1200" height="800">
                        <div class="body">
                            <h3>{E(name)}</h3>
                            <p>{E(text)}</p>
                            <span class="more">Mehr erfahren</span>
                        </div>
                    </a>"""

TOOLS = [
    ("wuerfel", "Würfel", "https://zufall.marcscheidegger.ch/",
     "Zufallsgenerator für die Übezeit: Stammton, Chromatik, Akkorde, CAGED-Formen und mehr – würfeln statt immer das Gleiche üben."),
    ("uebetimer", "Übe-Timer", "https://uebetimer.marcscheidegger.ch/",
     "Mehrere Timer für ein ganzes Übeprogramm. Sie laufen nacheinander ab, mit Gong am Ende jeder Übung und einem Journal für Notizen."),
    ("instrumentengrafik", "Instrumentengrafiken", "https://caged.marcscheidegger.ch/",
     "Akkorde und Formen auf Gitarre, Ukulele und Keyboard sichtbar machen – klar dargestellt, mit hervorgehobenen Grundtönen."),
]

def tool_card(k, name, url, text, h="h3"):
    return f"""                    <a class="card" href="{url}">
                        <img class="square" src="img/tool-{k}.jpg" alt="Grafik: {E(name)}" loading="lazy" width="800" height="800">
                        <div class="body">
                            <{h}>{E(name)}</{h}>
                            <p>{E(text)}</p>
                            <span class="more">Tool öffnen</span>
                        </div>
                    </a>"""

home = f"""        <section class="hero">
            <img src="img/hero-jvf-earlclub.jpg" alt="Marc Scheidegger mit dem Julian von Flüe Trio auf der Bühne" width="2000" height="1500" fetchpriority="high">
            <div class="wrap">
                <span class="kicker">Gitarre · Gesang · Mandoline</span>
                <h1>Marc Scheidegger</h1>
                <p class="lead">Gitarrist und Sänger – live mit dem Julian von Flüe Trio und Mala Oreen, als Begleitmusiker im Studio und mit eigenen Übe-Tools für alle, die ein Instrument lernen.</p>
                <div class="btns">
                    <a class="btn" href="projekte.html">Projekte entdecken</a>
                    <a class="btn ghost" href="kontakt.html">Kontakt &amp; Booking</a>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Aktuelle Bands</span>
                    <h2>Live auf der Bühne</h2>
                </div>
                <div class="grid two">
{band_card("julian-von-fluee", "Julian von Flüe Trio", "julian-von-fluee-trio.jpg", "Alpine Folk mit Akkordeon, Gitarre und Bass. Aktuelles Album «Alpine Folk» (2024), Konzerte bis 2027 und Auftritte in der SRF-Sendung Potzmusig.")}
{band_card("mala-oreen", "Mala Oreen", "mala-oreen.jpg", "Americana und Folk mit Fiddle, Mandoline und mehrstimmigem Gesang. Album «AWAKE» (2021), seit 2019 zahlreiche Konzerte.")}
                </div>
            </div>
        </section>

        <section class="section alt">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Live</span>
                    <h2>Nächste Konzerte</h2>
                </div>
{konzerte(limit=5)}
                <div class="btns"><a class="btn ghost" href="projekte.html#konzerte">Alle Konzerte</a></div>
            </div>
        </section>

        <section class="section">
            <div class="wrap split">
                <img src="img/marc-scheidegger.jpg" alt="Porträt Marc Scheidegger" loading="lazy" width="1200" height="1200">
                <div>
                    <span class="kicker">Seit 1999</span>
                    <h2>Bühne, Studio, Festival</h2>
                    <p>Vom Jazzfestival Willisau mit Kubus über Clubtouren mit Moë und die Open Mic Band im Kaufleuten Zürich bis zu Kids on Ice im Hallenstadion mit Andrew Bond: Seit über 25 Jahren spiele ich in Bands, begleite Sängerinnen und Sänger und arbeite im Studio.</p>
                    <div class="btns">
                        <a class="btn" href="chronologie.html">Zur Chronologie</a>
                        <a class="btn ghost" href="projekte.html#frueher">Frühere Projekte</a>
                    </div>
                </div>
            </div>
        </section>

        <section class="section alt">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Lernen &amp; Üben</span>
                    <h2>Meine Übe-Tools</h2>
                    <p>Kostenlose Werkzeuge im Browser – für das tägliche Üben auf Gitarre, Ukulele und Keyboard.</p>
                </div>
                <div class="grid">
{chr(10).join(tool_card(*t) for t in TOOLS)}
                </div>
                <div class="btns"><a class="btn ghost" href="lernen.html">Alles zum Lernen</a></div>
            </div>
        </section>

        <section class="section">
            <div class="wrap section-head" style="margin-bottom:0">
                <span class="kicker">Kontakt</span>
                <h2>Konzert, Studio oder Anfrage?</h2>
                <p>Schreib mir – ich melde mich gerne.</p>
                <div class="btns"><a class="btn" href="kontakt.html">Nachricht schreiben</a></div>
            </div>
        </section>
"""
page("index.html", "Home", "Marc Scheidegger – Gitarrist und Sänger mit dem Julian von Flüe Trio, Mala Oreen und Boogiefox. Projekte, Chronologie und Übe-Tools.", home)

# ---------------------------------------------------------------- Lernen
lernen = f"""        <section class="hero small plain">
            <div class="wrap split">
                <div>
                    <span class="kicker">Lernen &amp; Üben</span>
                    <h1>Besser üben,<br>mehr Musik</h1>
                    <p class="lead">Eigene Übe-Tools im Browser, Online-Kurse und Werkzeuge zum Noten schreiben und Musik produzieren.</p>
                    <div class="btns">
                        <a class="btn" href="#tools">Zu den Übe-Tools</a>
                        <a class="btn ghost" href="https://marcscheidegger.moodlecloud.com/login/index.php">Online-Kurse ↗</a>
                    </div>
                </div>
                <img src="img/marc-scheidegger.jpg" alt="Porträt Marc Scheidegger" width="1200" height="1200" style="max-width:420px;justify-self:center">
            </div>
        </section>

        <section class="section" id="tools">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Kostenlos im Browser</span>
                    <h2>Meine Übe-Tools</h2>
                    <p>Funktionieren auf dem Computer, Tablet und Handy – ohne Anmeldung.</p>
                </div>
                <div class="grid">
{chr(10).join(tool_card(*t) for t in TOOLS)}
                </div>
            </div>
        </section>

        <section class="section alt">
            <div class="wrap grid two">
                <div class="card"><div class="body">
                    <span class="kicker">Online-Kurse</span>
                    <h2 style="font-size:1.7rem">Lernen im eigenen Tempo</h2>
                    <p>Meine Kurse auf der Lernplattform Moodle – Anmeldung über den Link.</p>
                    <div class="btns"><a class="btn" href="https://marcscheidegger.moodlecloud.com/login/index.php">Zu den Online-Kursen ↗</a></div>
                </div></div>
                <div class="card"><div class="body">
                    <span class="kicker">Werkzeuge</span>
                    <h2 style="font-size:1.7rem">Online Musik machen</h2>
                    <ul class="links">
                        <li><a href="https://marcscheidegger.sites.noteflight.com/home">Noten schreiben mit Noteflight</a></li>
                        <li><a href="https://www.soundtrap.com/">Musik produzieren mit Soundtrap</a></li>
                    </ul>
                </div></div>
            </div>
        </section>
"""
page("lernen.html", "Lernen", "Übe-Tools von Marc Scheidegger: Würfel, Übe-Timer und Instrumentengrafiken, dazu Online-Kurse und Werkzeuge zum Musik machen.", lernen)

# ---------------------------------------------------------------- Kontakt
kontakt = """        <section class="hero small plain">
            <div class="wrap">
                <span class="kicker">Kontakt</span>
                <h1>Lass uns<br>Musik machen</h1>
                <p class="lead">Konzertanfragen, Studioaufnahmen, Online-Kurse oder einfach eine Frage – ich freue mich auf deine Nachricht.</p>
            </div>
        </section>

        <section class="section">
            <div class="wrap grid two">
                <div class="card"><div class="body">
                    <h2 style="font-size:1.7rem">Nachricht schreiben</h2>
                    <p id="msg-ok" class="notice ok" hidden>Danke! Deine Nachricht ist angekommen.</p>
                    <p id="msg-err" class="notice err" hidden>Das hat leider nicht geklappt. Bitte prüfe die Angaben oder schreib direkt per E-Mail.</p>
                    <form class="form" action="kontakt.php" method="post">
                        <label>Name<input name="name" autocomplete="name" required maxlength="120"></label>
                        <label>E-Mail<input name="email" type="email" autocomplete="email" required maxlength="200"></label>
                        <label>Nachricht<textarea name="nachricht" required maxlength="5000"></textarea></label>
                        <label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
                        <button class="btn" type="submit">Senden</button>
                    </form>
                </div></div>
                <div style="display:grid;gap:24px;align-content:start">
                    <div class="card"><div class="body">
                        <h2 style="font-size:1.4rem">Direkt per E-Mail</h2>
                        <p><a href="mailto:marcscheidegger@mac.com">marcscheidegger@mac.com</a></p>
                    </div></div>
                    <div class="card"><div class="body">
                        <h2 style="font-size:1.4rem">Social Media</h2>
                        <ul class="links">
                            <li><a href="https://www.instagram.com/marscx/">Instagram</a></li>
                            <li><a href="https://www.youtube.com/watch?v=AC6F9rHJwL4">YouTube</a></li>
                            <li><a href="https://www.linkedin.com/in/marc-scheidegger-470537ab/">LinkedIn</a></li>
                            <li><a href="https://twitter.com/marscx">X</a></li>
                        </ul>
                    </div></div>
                </div>
            </div>
        </section>
"""
page("kontakt.html", "Kontakt", "Kontakt zu Marc Scheidegger für Konzertanfragen, Studioaufnahmen und Online-Kurse.", kontakt)

# ---------------------------------------------------------------- Rechtstexte
impressum = """        <section class="section">
            <div class="wrap prose">
                <span class="kicker">Rechtliches</span>
                <h1>Impressum</h1>
                <h2>Verantwortlich für den Inhalt</h2>
                <p>Marc Scheidegger<br>
                <!-- TODO: Postadresse ergänzen -->[Strasse und Nr. bitte ergänzen]<br>
                [PLZ Ort bitte ergänzen]<br>
                Schweiz</p>
                <p>E-Mail: <a href="mailto:marcscheidegger@mac.com">marcscheidegger@mac.com</a></p>
                <h2>Haftung für Links</h2>
                <p>Diese Website enthält Links zu externen Websites. Für deren Inhalte sind ausschliesslich die jeweiligen Betreiber verantwortlich.</p>
                <h2>Urheberrechte</h2>
                <p>Texte, Fotos und Grafiken auf dieser Website sind urheberrechtlich geschützt. Die Fotos stammen von den jeweiligen Bands bzw. Fotografinnen und Fotografen (z.&nbsp;B. Mala Oreen: Andrea Ebener). Eine Verwendung ist nur mit Einwilligung erlaubt.</p>
            </div>
        </section>
"""
page("impressum.html", "Impressum", "Impressum von marcscheidegger.ch", impressum, current="-")

datenschutz = """        <section class="section">
            <div class="wrap prose">
                <span class="kicker">Rechtliches</span>
                <h1>Datenschutz</h1>
                <p>Diese Website verzichtet bewusst auf Cookies, Tracking, Werbung und eingebettete Inhalte von Drittanbietern. Schriften und Skripte werden direkt von diesem Server geladen.</p>
                <h2>Verantwortlich</h2>
                <p>Marc Scheidegger, <a href="mailto:marcscheidegger@mac.com">marcscheidegger@mac.com</a> (Adresse siehe <a href="impressum.html">Impressum</a>).</p>
                <h2>Server-Logdateien</h2>
                <p>Beim Aufruf der Website speichert der Webserver technisch notwendige Daten (IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Browser). Diese Daten dienen dem sicheren Betrieb und werden nach kurzer Zeit gelöscht. <!-- TODO: Hoster und Speicherdauer ergänzen -->[Hoster bitte ergänzen]</p>
                <h2>Kontaktformular und E-Mail</h2>
                <p>Wenn du mir über das Kontaktformular oder per E-Mail schreibst, verwende ich deine Angaben (Name, E-Mail-Adresse, Nachricht) nur, um deine Anfrage zu beantworten. Die Daten werden nicht weitergegeben.</p>
                <h2>Videos</h2>
                <p>Videos von YouTube und SRF sind so eingebunden, dass beim Besuch der Seite keine Daten an diese Anbieter gehen. Erst wenn du auf ein Video klickst, wird es von YouTube (im erweiterten Datenschutzmodus, youtube-nocookie.com) bzw. von SRF geladen. Dabei erhält der Anbieter deine IP-Adresse und es gelten seine Datenschutzbestimmungen.</p>
                <h2>Externe Links</h2>
                <p>Links zu anderen Websites (z.&nbsp;B. Instagram, YouTube, Moodle, Noteflight) führen zu Angeboten mit eigenen Datenschutzbestimmungen. Beim Anklicken verlässt du diese Website.</p>
                <h2>Deine Rechte</h2>
                <p>Du kannst jederzeit Auskunft über deine gespeicherten Daten verlangen sowie deren Berichtigung oder Löschung beantragen. Es gilt das Schweizer Datenschutzgesetz (DSG).</p>
            </div>
        </section>
"""
page("datenschutz.html", "Datenschutz", "Datenschutzerklärung von marcscheidegger.ch", datenschutz, current="-")

page("404.html", "Seite nicht gefunden", "Diese Seite gibt es nicht.", """        <section class="hero small plain">
            <div class="wrap">
                <span class="kicker">Fehler 404</span>
                <h1>Falscher Ton.</h1>
                <p class="lead">Diese Seite gibt es nicht (mehr). Vielleicht findest du hier, was du suchst:</p>
                <div class="btns">
                    <a class="btn" href="/">Zur Startseite</a>
                    <a class="btn ghost" href="/projekte.html">Projekte</a>
                    <a class="btn ghost" href="/lernen.html">Lernen</a>
                </div>
            </div>
        </section>
""", current="-")

# 404 wird unter beliebigen Pfaden ausgeliefert: Links absolut machen
p404 = os.path.join(OUT, "404.html")
with open(p404) as f:
    t = re.sub(r'(href|src)="(css|js|favicon|index|img)', r'\1="/\2', f.read())
with open(p404, "w") as f:
    f.write(t)

print("ok", years)
