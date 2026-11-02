"""Erzeugt alle HTML-Seiten von marcscheidegger.ch.

SO FUNKTIONIERT DIE WEBSITE
---------------------------
Die Website besteht aus fertigen HTML-Dateien (index.html, projekte.html …), die der
Webserver einfach ausliefert – ohne Datenbank, ohne WordPress. Damit Kopf- und
Fusszeile auf allen Seiten gleich sind und Inhalte nur an einer Stelle stehen,
werden die HTML-Dateien von diesem Skript erzeugt.

    build.py  ──erzeugt──▶  index.html, projekte.html, chronologie.html, lernen.html,
                            kontakt.html, impressum.html, datenschutz.html, 404.html

Die HTML-Dateien deshalb NIE direkt bearbeiten – Änderungen gehen beim nächsten
Durchlauf verloren. Immer hier ändern und dann im Terminal ausführen:

    python3 build.py

Weitere Dateien:
    css/site.css   Aussehen (Farben, Abstände, Layout)
    js/site.js     Kleine Funktionen im Browser (Handy-Menü, Konzerte, Videos, Hörproben)
    .htaccess      Regeln für den Webserver (Weiterleitungen, HTTPS, Sperren)
    img/           Bilder

AUFBAU DIESER DATEI
-------------------
1. Grundeinstellungen und Bausteine (Navigation, Icons, Seitenrahmen)
2. Inhalte als Listen: Projekte, Clips, Hörproben, Konzerte
3. Funktionen, die aus den Listen HTML machen
4. Die einzelnen Seiten (Projekte, Chronologie, Home, Lernen, Kontakt, Rechtliches, 404)

Was du am häufigsten änderst:
    neues Konzert          → Liste KONZERTE
    neue Station / Band    → Liste P (Projekte)
    neues Video            → Liste CLIPS
    neue Hörprobe          → Liste TRACKS
    Texte einer Seite      → Abschnitt der jeweiligen Seite weiter unten
"""
import html, os, re

# =============================================================================
# 1. GRUNDEINSTELLUNGEN UND BAUSTEINE
# =============================================================================

# Ordner, in den die HTML-Dateien geschrieben werden (= Ordner dieser Datei)
OUT = os.path.dirname(os.path.abspath(__file__))

# Cache-Version: Browser merken sich CSS/JS lange. Wird diese Zahl erhöht, hängt an
# den Links ein neues "?v=…" und alle Besucher laden die geänderte Datei neu.
# → Nach jeder Änderung an site.css oder site.js um 1 erhöhen.
V = 9

# Hauptnavigation oben: (Datei, Beschriftung) – Reihenfolge = Reihenfolge im Menü
NAV = [("index.html", "Home"), ("projekte.html", "Projekte"), ("chronologie.html", "Chronologie"),
       ("lernen.html", "Lernen"), ("kontakt.html", "Kontakt")]

# E() macht Text HTML-sicher: aus "&" wird "&amp;", aus "<" wird "&lt;" usw.
E = html.escape
# Markiert im Menü die Seite, auf der man gerade ist (wird per CSS hervorgehoben)
CUR = ' aria-current="page"'

# --- Icons -------------------------------------------------------------------
# Alle Icons sind kleine SVG-Grafiken direkt im Code (keine externen Icon-Dienste,
# damit beim Seitenaufruf keine Daten an Dritte gehen). "currentColor" bedeutet:
# das Icon nimmt die Textfarbe an, die im CSS festgelegt ist.
MAIL_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>')

def icon(inner):
    """Verpackt die Zeichnung eines Icons in einen einheitlichen SVG-Rahmen (24×24, Strichstärke 1.8)."""
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')

ICONS = {
    "instagram": icon('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
                      '<circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>'),
    "youtube": icon('<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3z" fill="currentColor"/>'),
    "linkedin": icon('<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 11v6M8 7.5v.01M12 17v-6M12 13.5a2.5 2.5 0 0 1 5 0V17"/>'),
    "x": icon('<path d="M4 4h4.5L20 20h-4.5z"/><path d="M19.5 4l-6.6 7.5M11.1 12.5 4.5 20"/>'),
    "mail": MAIL_ICON,
}

# --- Social Media ------------------------------------------------------------
# (Icon-Name, Beschriftung, Link). Erscheint als Icon-Reihe in der Fusszeile jeder
# Seite und als Liste auf der Kontaktseite (dort ohne E-Mail, die hat eine eigene Karte).
# Neuen Kanal hinzufügen: Zeile ergänzen und oben in ICONS ein passendes Icon anlegen.
SOCIAL = [
    ("instagram", "Instagram", "https://www.instagram.com/marscx/"),
    ("youtube", "YouTube", "https://www.youtube.com/watch?v=AC6F9rHJwL4"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/marc-scheidegger-470537ab/"),
    ("x", "X", "https://twitter.com/marscx"),
    ("mail", "E-Mail", "mailto:marcscheidegger@mac.com"),
]

def social_icons(indent):
    """Runde Icons ohne Text für die Fusszeile (Beschriftung nur als Tooltip / für Screenreader)."""
    return "\n".join(f'{indent}<li><a href="{u}" aria-label="{t}" title="{t}">{ICONS[k]}</a></li>' for k, t, u in SOCIAL)

def social_links(indent):
    """Liste mit Icon + Name für die Kontaktseite (E-Mail ausgelassen)."""
    return "\n".join(f'{indent}<li><a href="{u}"><span class="ico">{ICONS[k]}</span>{t}</a></li>' for k, t, u in SOCIAL if k != "mail")

# --- Seitenrahmen ------------------------------------------------------------
def page(fname, title, desc, body, current=None):
    """Schreibt eine komplette HTML-Seite: gemeinsamer Rahmen + der Inhalt "body".

    fname    Dateiname, z. B. "projekte.html"
    title    Seitentitel im Browser-Tab ("Projekte – Marc Scheidegger")
    desc     Kurzbeschreibung für Google und für Vorschauen beim Teilen (WhatsApp usw.)
    body     der eigentliche Seiteninhalt (HTML-Abschnitte, siehe weiter unten)
    current  welcher Menüpunkt hervorgehoben wird; "-" = keiner (Impressum usw.)
    """
    navlis = "\n".join(
        f'                <li><a href="{h}"{CUR if h == (current or fname) else ""}>{t}</a></li>'
        for h, t in NAV)
    full_title = "Marc Scheidegger – Gitarre & Gesang" if fname == "index.html" else f"{title} – Marc Scheidegger"
    doc = f"""<!doctype html>
<!-- Diese Datei wird von build.py erzeugt – Änderungen bitte dort machen. -->
<html lang="de-CH">
<head>
    <!-- Unsichtbarer Kopf: Zeichensatz, Handy-Darstellung, Titel, Beschreibung
         für Google (description) und für Link-Vorschauen (og:…), Icon, CSS und JS -->
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
    <!-- Unsichtbarer Sprunglink für Tastatur- und Screenreader-Nutzer -->
    <a class="skip" href="#inhalt">Zum Inhalt</a>

    <!-- ===== KOPFZEILE: Name links, Navigation rechts (bleibt beim Scrollen oben).
         Auf dem Handy wird die Navigation hinter dem Knopf "Menü" versteckt. ===== -->
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

    <!-- ===== HAUPTINHALT der Seite ===== -->
    <main id="inhalt">
{body.rstrip()}
    </main>

    <!-- ===== FUSSZEILE: Copyright, Social-Media-Icons, Impressum/Datenschutz.
         Die Jahreszahl wird von site.js automatisch aktualisiert. ===== -->
    <footer class="site-footer">
        <div class="wrap">
            <p>© <span data-year>2026</span> Marc Scheidegger</p>
            <ul class="social" aria-label="Social Media">
{social_icons("                ")}
            </ul>
            <ul>
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

# =============================================================================
# 2. INHALTE
# =============================================================================

# ---------------------------------------------------------------- Projekte
# Alle Bands und Projekte. Daraus entstehen die Seite "Projekte" UND die
# "Chronologie" (die Jahreszahlen der Fakten werden dort automatisch sortiert).
#
# Jeder Eintrag hat 8 Felder in dieser Reihenfolge:
#   1 slug       kurzer Kennname ohne Leerzeichen/Umlaute; wird zur Sprungmarke
#                projekte.html#slug und verbindet CLIPS, TRACKS und KONZERTE
#   2 name       Name der Band, wie er auf der Seite steht
#   3 bild       Dateiname in img/ – oder None für "kein Bild"
#   4 zeitraum   Text oben in Gelb, z. B. "seit 2014" oder "2002 – 2011"
#   5 besetzung  Musiker mit Instrumenten, durch " · " getrennt
#   6 fakten     Liste von ("Jahr", "Text"). Jahr darf ein Zeitraum sein
#                ("2010 – 2014"); in der Chronologie erscheint der Eintrag beim Startjahr.
#   7 links      Buttons zu externen Seiten: [("https://…", "Beschriftung")] oder []
#   8 gruppe     "aktuell" = grosse Darstellung oben, "frueher" = Frühere Bands,
#                "begleit" = Begleitmusiker & Studio
#
# Beispiel für eine neue Station bei einer bestehenden Band: in deren Fakten-Liste
#   ("2027", "Auftritt am Festival XY"),
# ergänzen. Band wechselt zu "früher": Feld 8 von "aktuell" auf "frueher" ändern.
P = [
    ("julian-von-fluee", "Julian von Flüe Trio", "julian-von-fluee-trio-treppe.jpg", "seit 2014",
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
     [("2002", "Luzerner Werkbeiträge"), ("2002", "Popkredit Zürich"), ("2003", "Album «Reflections» und Clubtour"),
      ("2008", "CD-Produktion und Clubtour"), ("2011", "CD-Produktion und Clubtour")], [], "frueher"),
    ("kubus", "Kubus", "kubus.jpg", "1999 – 2006",
     "Rafael Woll – Schlagzeug · Marcel Stalder – Bass · Adrian Pflugshaupt – Saxofon · Peter Estermann – Piano · Fabian Stübi – Elektronik · Marc Scheidegger – Gitarre, Elektronik",
     [("1999", "Luzerner Werkbeiträge"), ("2001", "Jazzfestival Kaunas, Litauen"), ("2002", "Album «Kubus» (SeeHear Recordings)"),
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

# Optionaler Einleitungstext unter dem Bandnamen (nur für die grossen "aktuell"-Einträge)
INTRO = {
    "julian-von-fluee": "Alpine Folk: Julian von Flües eigene Kompositionen, verwurzelt in der Musik des Alpenraums und inspiriert von amerikanischer Country- und Folkmusik. Aktuelles Album: «Alpine Folk» (2024).",
    "mala-oreen": "«Songs for and from the heart» – Americana und Folk mit mehrstimmigem Gesang. Das Album «AWAKE» nannte Americana Highways «one of the year’s best».",
}

# ---------------------------------------------------------------- Clips (Videos)
# Videos pro Band, geordnet nach slug (siehe Projekte). Ein Eintrag:
#   (quelle, id, titel, jahr)
#   quelle  "yt" = YouTube, "srf" = SRF Play
#   id      YouTube: die 11 Zeichen nach "watch?v=" in der Adresse
#           SRF:     die lange ID aus der SRF-Play-Adresse (urn:srf:video:…)
# Nur Clips, in denen Marc nachweislich mitspielt.
#
# Das Vorschaubild muss lokal in img/clips/ liegen: "yt-<id>.jpg" bzw.
# "srf-<erste 8 Zeichen der id>.jpg". Das Video selbst lädt erst nach einem Klick –
# vorher gehen keine Daten an YouTube/SRF (Datenschutz).
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

# ---------------------------------------------------------------- Hörproben
# Hörproben von Apple Music pro Band (slug). Ein Eintrag:
#   (album-id?i=track-id, titel, album, jahr)
# Die IDs findest du in der Adresse eines Songs bei music.apple.com, z. B.
#   https://music.apple.com/ch/album/alpine-folk/1779697391?i=1779698068
#                                                └ album-id ┘   └ track-id ┘
# Beim Klick öffnet sich der Apple-Player unten rechts (ohne Abo: 30 Sekunden).
# Nur Aufnahmen, auf denen Marc spielt (eigene Liste der CD-Produktionen bzw. Credits).
TRACKS = {
    "julian-von-fluee": [
        ("1779697391?i=1779698068", "Wie Zyt verstricht", "Alpine Folk", "2024"),
        ("1779697391?i=1779697648", "E glungne Abig", "Alpine Folk", "2024"),
        ("1690417968?i=1690418716", "Dur d’Altstadt", "Dur d’Altstadt", "2023"),
        ("1690406111?i=1690406557", "Uf um Stoos ob Schwyz", "Drive", "2019"),
        ("1690406111?i=1690406337", "Nachtspaziergang", "Drive", "2019"),
    ],
    "kubus": [
        ("1435500427?i=1435500429", "Hürfel", "Kubus", "2002"),
        ("1435500427?i=1435500703", "Pilzkultur", "Kubus", "2002"),
    ],
    "moe": [
        ("487607869?i=487608450", "The Same Old Story", "Reflections", "2003"),
    ],
    "stimmreise": [
        ("1635556489?i=1635557122", "Oldbox", "stimmreise.ch, Vol. 2", "2010"),
        ("1635556489?i=1635556510", "Riiwäiwel", "stimmreise.ch, Vol. 2", "2010"),
    ],
    "patrick-jonsson": [
        ("375345689?i=375345741", "This Is the Sky", "This Is the Sky", "2009"),
        ("1292581091?i=1292581099", "People Are Strange", "People Are Strange", "2013"),
    ],
    "emel": [
        ("1305231429?i=1305231649", "Dragon", "Single", "2017"),
    ],
    "yvonne-moore": [
        ("163232224?i=163232718", "Closer to You", "Nomad", "2002"),
        ("163232224?i=163232902", "Come On Yvonne", "Nomad", "2002"),
    ],
    "guy-vincent": [
        ("693996856?i=693996860", "Expectations", "Expectations", "2013"),
        ("693996856?i=693996891", "We Live", "Expectations", "2013"),
    ],
}

# =============================================================================
# 3. FUNKTIONEN: aus den Listen oben wird HTML
# =============================================================================
# Diese Funktionen musst du normalerweise nicht ändern. Sie bauen die immer
# gleichen Bausteine (Hörprobe, Video, Fakten-Liste, Band-Karte) zusammen.

def track(tid, t, alb, y):
    """Eine Zeile in der Hörproben-Liste. Der Link führt zu Apple Music; site.js
    fängt den Klick ab und öffnet stattdessen den Mini-Player (data-embed)."""
    return (f"""                            <li><a class="track" href="https://music.apple.com/ch/album/{tid}" """
            f"""data-embed="https://embed.music.apple.com/ch/album/{tid}" data-title="{E(t)}">"""
            f"""<b>{E(t)}</b> <span>{E(alb)} · {y}</span></a></li>""")

def tracks(slug):
    """Block "Hörproben" einer Band – leer, wenn die Band keine Hörproben hat."""
    if slug not in TRACKS:
        return ""
    return f"""
                        <div class="tracks">
                            <p class="tracks-head">Hörproben <span>Apple Music</span></p>
                            <ul>
{chr(10).join(track(*t) for t in TRACKS[slug])}
                            </ul>
                        </div>"""

def clip(kind, cid, title, year):
    """Ein Video als Vorschaubild mit Abspielknopf. Erst der Klick ersetzt das Bild
    durch den echten Player (siehe site.js). Ohne JavaScript führt der Link zum Video."""
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
    """Alle Videos einer Band als Raster – leer, wenn die Band keine Videos hat."""
    if slug not in CLIPS:
        return ""
    return f"""
                        <div class="clips">
{chr(10).join(clip(*c) for c in CLIPS[slug])}
                        </div>
                        <p class="clip-note">Videos werden erst beim Abspielen von YouTube bzw. SRF geladen.</p>"""

def facts(fs):
    """Die Liste "Jahr – Text" einer Band."""
    return "\n".join(f"                            <li><b>{E(y)}</b><span>{E(t)}</span></li>" for y, t in fs)

def project_row(p):
    """Grosse Darstellung für aktuelle Bands: Bild links, Text rechts, Videos darunter."""
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
                        </ul>{tracks(slug)}{btn}
                    </div>{clips(slug)}
                </article>"""

def compact_card(p):
    """Kompakte Karte für frühere Bands und Begleitmusiker (Bild oben, falls vorhanden)."""
    slug, name, img, years, lineup, fs, links, _ = p
    im = f'\n                    <img src="img/{img}" alt="{E(name)}" loading="lazy" width="1200" height="800">' if img else ""
    return f"""                <article class="card" id="{slug}">{im}
                    <div class="body">
                        <p class="years" style="color:var(--accent);font-weight:600;font-size:.9rem;margin:0 0 4px">{E(years)}</p>
                        <h3>{E(name)}</h3>
                        <p class="lineup">{E(lineup)}</p>
                        <ul class="facts">
{facts(fs)}
                        </ul>{tracks(slug)}{clips(slug)}
                    </div>
                </article>"""

# Alle Projekte einer Gruppe ("aktuell", "frueher" oder "begleit")
grp = lambda g: [p for p in P if p[7] == g]

# ---------------------------------------------------------------- Konzerte
# Kommende Konzerte, nach Datum sortiert eintragen. Ein Eintrag:
#   (datum, zeit, band-slug, ort, link)
#   datum      immer im Format JJJJ-MM-TT, z. B. "2027-03-18"
#   zeit       "20:15" oder "" wenn unbekannt
#   band-slug  slug aus der Projektliste, z. B. "julian-von-fluee"
#   ort        Veranstalter und Ort
#   link       Ticket-/Info-Link oder ""
# Vergangene Konzerte musst du nicht löschen: site.js blendet sie im Browser
# automatisch aus. Die Startseite zeigt die nächsten 5, die Projekte-Seite alle.
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
BAND = {p[0]: p[1] for p in P}   # slug → Bandname, z. B. "mala-oreen" → "Mala Oreen"

def konzerte(limit=None):
    """Konzertliste. limit = wie viele höchstens sichtbar sind (Startseite: 5)."""
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

# =============================================================================
# 4. DIE SEITEN
# =============================================================================
# Jede Seite ist ein Text mit HTML-Abschnitten (<section>). Die {…} in geschweiften
# Klammern werden beim Erzeugen durch die Bausteine von oben ersetzt.
# Häufige CSS-Klassen (Aussehen in site.css):
#   hero          grosser Seitenkopf (mit Bild; "small" = niedriger, "plain" = ohne Bild)
#   section       normaler Abschnitt; "alt" = leicht anderer Hintergrund zur Abwechslung
#   wrap          begrenzt die Breite und zentriert den Inhalt
#   kicker        kleine Überschrift in Grossbuchstaben über dem Titel
#   btn / ghost   gelber Button / umrandeter Button
#   grid / two    Raster für Karten (automatisch so viele Spalten wie Platz hat / max. 2)

# ---------------------------------------------------------------- Seite: Projekte
projekte = f"""        <!-- ===== SEITENKOPF mit Bandfoto und Sprung-Buttons zu den Abschnitten ===== -->
        <section class="hero small">
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

        <!-- ===== AKTUELLE BANDS: grosse Darstellung (Liste P, gruppe "aktuell") ===== -->
        <section class="section" id="aktuell">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Heute</span>
                    <h2>Aktuelle Bands</h2>
                </div>
{chr(10).join(project_row(p) for p in grp("aktuell"))}
            </div>
        </section>

        <!-- ===== KONZERTE: alle kommenden Termine (Liste KONZERTE) ===== -->
        <section class="section alt" id="konzerte">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Live</span>
                    <h2>Nächste Konzerte</h2>
                </div>
{konzerte()}
            </div>
        </section>

        <!-- ===== FRÜHERE BANDS: kompakte Karten (gruppe "frueher") ===== -->
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

        <!-- ===== BEGLEITMUSIKER & STUDIO: kompakte Karten (gruppe "begleit") ===== -->
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

# ---------------------------------------------------------------- Seite: Chronologie
# Die Chronologie wird automatisch aus den Fakten aller Projekte gebaut:
# jeder Fakt landet beim Startjahr; bei Zeiträumen wird "(bis …)" angehängt.
by_year = {}
for p in P:
    for y, t in p[5]:
        start = int(y[:4])
        m = re.search(r"–\s*(\d{4}|heute)", y)
        suffix = f" (bis {m.group(1)})" if m else ""
        by_year.setdefault(start, []).append((p[0], p[1], t + suffix))
years = sorted(by_year, reverse=True)

def year_block(y):
    """Ein Jahr auf der Zeitleiste mit allen Einträgen aus diesem Jahr."""
    items = "\n".join(
        f'                        <li><a href="projekte.html#{s}">{E(n)}</a> <span>– {E(t)}</span></li>'
        for s, n, t in by_year[y])
    return f"""                <li class="year" id="jahr-{y}">
                    <h2>{y}</h2>
                    <ul>
{items}
                    </ul>
                </li>"""

chrono = f"""        <!-- ===== SEITENKOPF ===== -->
        <section class="hero small plain">
            <div class="wrap">
                <span class="kicker">Chronologie</span>
                <h1>Seit 1999<br>unterwegs</h1>
                <p class="lead">Konzerte, CD-Produktionen, Festivals und Fernsehauftritte – Jahr für Jahr. Heute spiele ich im <a href="projekte.html#julian-von-fluee">Julian von Flüe Trio</a> und bei <a href="projekte.html#mala-oreen">Mala Oreen</a>.</p>
            </div>
        </section>

        <!-- ===== ZEITLEISTE: oben Sprungmarken zu den Jahren, darunter alle Jahre ===== -->
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

# ---------------------------------------------------------------- Seite: Home (Startseite)
def band_card(slug, name, img, text):
    """Karte einer aktuellen Band auf der Startseite; führt zur Band auf der Projekte-Seite."""
    return f"""                    <a class="card" href="projekte.html#{slug}">
                        <img src="img/{img}" alt="{E(name)}" loading="lazy" width="1200" height="800">
                        <div class="body">
                            <h3>{E(name)}</h3>
                            <p>{E(text)}</p>
                            <span class="more">Mehr erfahren</span>
                        </div>
                    </a>"""

# Die Übe-Tools (eigene Subdomains). (Bild-Kürzel, Name, Link, Text);
# das Bild heisst img/tool-<Kürzel>.jpg. Wird auf Home und Lernen verwendet.
TOOLS = [
    ("wuerfel", "Würfel", "https://zufall.marcscheidegger.ch/",
     "Zufallsgenerator für die Übezeit: Stammton, Chromatik, Akkorde, CAGED-Formen und mehr – würfeln statt immer das Gleiche üben."),
    ("uebetimer", "Übe-Timer", "https://uebetimer.marcscheidegger.ch/",
     "Mehrere Timer für ein ganzes Übeprogramm. Sie laufen nacheinander ab, mit Gong am Ende jeder Übung und einem Journal für Notizen."),
    ("instrumentengrafik", "Instrumentengrafiken", "https://caged.marcscheidegger.ch/",
     "Akkorde und Formen auf Gitarre, Ukulele und Keyboard sichtbar machen – klar dargestellt, mit hervorgehobenen Grundtönen."),
]

def tool_card(k, name, url, text, h="h3"):
    """Karte für ein Übe-Tool mit quadratischer Grafik."""
    return f"""                    <a class="card" href="{url}">
                        <img class="square" src="img/tool-{k}.jpg" alt="Grafik: {E(name)}" loading="lazy" width="800" height="800">
                        <div class="body">
                            <{h}>{E(name)}</{h}>
                            <p>{E(text)}</p>
                            <span class="more">Tool öffnen</span>
                        </div>
                    </a>"""

home = f"""        <!-- ===== SEITENKOPF: grosses Bühnenfoto, Name, Kurzbeschreibung ===== -->
        <section class="hero">
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

        <!-- ===== AKTUELLE BANDS: zwei Karten (Text hier direkt im band_card-Aufruf) ===== -->
        <section class="section">
            <div class="wrap">
                <div class="section-head">
                    <span class="kicker">Aktuelle Bands</span>
                    <h2>Live auf der Bühne</h2>
                </div>
                <div class="grid two">
{band_card("julian-von-fluee", "Julian von Flüe Trio", "julian-von-fluee-trio-treppe.jpg", "Alpine Folk mit Akkordeon, Gitarre und Bass. Aktuelles Album «Alpine Folk» (2024), Konzerte bis 2027 und Auftritte in der SRF-Sendung Potzmusig.")}
{band_card("mala-oreen", "Mala Oreen", "mala-oreen.jpg", "Americana und Folk mit Fiddle, Mandoline und mehrstimmigem Gesang. Album «AWAKE» (2021), seit 2019 zahlreiche Konzerte.")}
                </div>
            </div>
        </section>

        <!-- ===== NÄCHSTE KONZERTE: die nächsten 5 aus der Liste KONZERTE ===== -->
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

        <!-- ===== ÜBER MICH: Porträt links, Text rechts ("split" = zwei Spalten) ===== -->
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

        <!-- ===== ÜBE-TOOLS: drei Karten (Liste TOOLS) ===== -->
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

        <!-- ===== KONTAKT-AUFRUF mit E-Mail-Button ===== -->
        <section class="section">
            <div class="wrap section-head" style="margin-bottom:0">
                <span class="kicker">Kontakt</span>
                <h2>Konzert, Studio oder Anfrage?</h2>
                <p>Schreib mir – ich melde mich gerne.</p>
                <div class="btns"><a class="btn" href="mailto:marcscheidegger@mac.com">{MAIL_ICON} E-Mail schreiben</a></div>
            </div>
        </section>
"""
page("index.html", "Home", "Marc Scheidegger – Gitarrist und Sänger mit dem Julian von Flüe Trio, Mala Oreen und Boogiefox. Projekte, Chronologie und Übe-Tools.", home)

# ---------------------------------------------------------------- Seite: Lernen
lernen = f"""        <!-- ===== SEITENKOPF: Text links, Porträt rechts ===== -->
        <section class="hero small plain">
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

        <!-- ===== ÜBE-TOOLS: dieselben Karten wie auf der Startseite (Liste TOOLS) ===== -->
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

        <!-- ===== ONLINE-KURSE (Moodle) und weitere Werkzeuge ===== -->
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

# ---------------------------------------------------------------- Seite: Kontakt
kontakt = f"""        <!-- ===== SEITENKOPF ===== -->
        <section class="hero small plain">
            <div class="wrap">
                <span class="kicker">Kontakt</span>
                <h1>Lass uns<br>Musik machen</h1>
                <p class="lead">Konzertanfragen, Studioaufnahmen, Online-Kurse oder einfach eine Frage – ich freue mich auf deine Nachricht.</p>
            </div>
        </section>

        <!-- ===== E-MAIL-KARTE (links) und SOCIAL MEDIA (rechts, Liste SOCIAL) ===== -->
        <section class="section">
            <div class="wrap grid two">
                <a class="card mail-card" href="mailto:marcscheidegger@mac.com">
                    <span class="mail-icon">{MAIL_ICON}</span>
                    <span class="kicker">E-Mail</span>
                    <strong>marcscheidegger@mac.com</strong>
                    <span class="more">Nachricht schreiben</span>
                </a>
                <div style="display:grid;gap:24px;align-content:start">
                    <div class="card"><div class="body">
                        <h2 style="font-size:1.4rem">Social Media</h2>
                        <ul class="links">
{social_links("                            ")}
                        </ul>
                    </div></div>
                </div>
            </div>
        </section>
"""
page("kontakt.html", "Kontakt", "Kontakt zu Marc Scheidegger für Konzertanfragen, Studioaufnahmen und Online-Kurse.", kontakt)

# ---------------------------------------------------------------- Seiten: Impressum und Datenschutz
# Reiner Text ("prose" = gut lesbare Textbreite). current="-" → kein Menüpunkt hervorgehoben.
impressum = """        <!-- ===== IMPRESSUM ===== -->
        <section class="section">
            <div class="wrap prose">
                <span class="kicker">Rechtliches</span>
                <h1>Impressum</h1>
                <h2>Verantwortlich für den Inhalt</h2>
                <p>Marc Scheidegger<br>
                Rüsseckstrasse 5<br>
                4800 Zofingen<br>
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

datenschutz = """        <!-- ===== DATENSCHUTZERKLÄRUNG ===== -->
        <section class="section">
            <div class="wrap prose">
                <span class="kicker">Rechtliches</span>
                <h1>Datenschutz</h1>
                <p>Diese Website verzichtet bewusst auf Cookies, Tracking und Werbung. Schriften und Skripte werden direkt von diesem Server geladen. Inhalte von Drittanbietern (Videos, Hörproben) werden erst nach einem Klick geladen, siehe unten.</p>
                <h2>Verantwortlich</h2>
                <p>Marc Scheidegger, <a href="mailto:marcscheidegger@mac.com">marcscheidegger@mac.com</a> (Adresse siehe <a href="impressum.html">Impressum</a>).</p>
                <h2>Server-Logdateien</h2>
                <p>Beim Aufruf der Website speichert der Webserver technisch notwendige Daten (IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Browser). Diese Daten dienen dem sicheren Betrieb und werden nach kurzer Zeit gelöscht. Die Website wird bei der Metanet AG in Zürich (Schweiz) gehostet; die Daten bleiben auf deren Servern in der Schweiz.</p>
                <h2>E-Mail</h2>
                <p>Wenn du mir per E-Mail schreibst, verwende ich deine Angaben nur, um deine Anfrage zu beantworten. Die Daten werden nicht weitergegeben.</p>
                <h2>Übe-Tools</h2>
                <p>Die Übe-Tools auf zufall.marcscheidegger.ch (Würfel), uebetimer.marcscheidegger.ch (Übe-Timer) und caged.marcscheidegger.ch (Instrumentengrafiken) laufen vollständig in deinem Browser. Der Übe-Timer speichert dein Übeprogramm und deine Einstellungen, der Würfel deinen Lernstand bei den Akkorden (gewusst / nicht gewusst). Diese Daten liegen nur im Speicher deines Browsers auf deinem Gerät (localStorage) und werden weder an mich noch an Dritte übertragen. Es werden dafür keine Cookies verwendet.</p>
                <p>Löschen kannst du diese Daten jederzeit in den Tools selbst (z.&nbsp;B. „Lernstand löschen“) oder in den Einstellungen deines Browsers (Websitedaten löschen). Griffbilder, PNG- und PDF-Dateien werden ebenfalls direkt in deinem Browser erstellt.</p>
                <h2>Videos</h2>
                <p>Videos und Hörproben von YouTube, SRF und Apple Music sind so eingebunden, dass beim Besuch der Seite keine Daten an diese Anbieter gehen. Erst wenn du auf ein Video oder eine Hörprobe klickst, wird der Player des Anbieters geladen (YouTube im erweiterten Datenschutzmodus, youtube-nocookie.com). Dabei erhält der Anbieter deine IP-Adresse und es gelten seine Datenschutzbestimmungen.</p>
                <h2>Externe Links</h2>
                <p>Links zu anderen Websites (z.&nbsp;B. Instagram, YouTube, Moodle, Noteflight) führen zu Angeboten mit eigenen Datenschutzbestimmungen. Beim Anklicken verlässt du diese Website.</p>
                <h2>Deine Rechte</h2>
                <p>Du kannst jederzeit Auskunft über deine gespeicherten Daten verlangen sowie deren Berichtigung oder Löschung beantragen. Es gilt das Schweizer Datenschutzgesetz (DSG).</p>
            </div>
        </section>
"""
page("datenschutz.html", "Datenschutz", "Datenschutzerklärung von marcscheidegger.ch", datenschutz, current="-")

# ---------------------------------------------------------------- Seite: 404 (Fehlerseite)
# Erscheint bei jeder Adresse, die es nicht gibt (eingestellt in .htaccess).
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

# Die 404-Seite kann unter jeder Adresse erscheinen (z. B. /alt/seite). Damit CSS und
# Bilder trotzdem gefunden werden, bekommen ihre Links ein "/" davor (= ab Hauptordner). ausgeliefert: Links absolut machen
p404 = os.path.join(OUT, "404.html")
with open(p404) as f:
    t = re.sub(r'(href|src)="(css|js|favicon|index|img)', r'\1="/\2', f.read())
with open(p404, "w") as f:
    f.write(t)

# Kurze Bestätigung im Terminal mit allen Jahren der Chronologie
print("ok", years)
