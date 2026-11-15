"""Holt die aktuellen Konzerttermine der Bands und schreibt sie nach konzerte.json.

Einmal pro Woche von Hand starten:

    python3 konzerte.py      → schreibt konzerte.json
    python3 build.py         → baut die Seiten mit den neuen Terminen

Quellen
    Julian von Flüe Trio   https://julianvonfluee.ch/live/   (WordPress-Seite: Jahr als Überschrift,
                            darunter je Konzert "Wochentag, Tag. Monat", Zeit, Ort, Links)
    Mala Oreen             Optune-Kalender (dieselben Daten wie auf malaoreen.com), als JSON

Sicherheit: Schlägt eine Quelle fehl oder liefert sie nichts Brauchbares, bleiben deren
bisherige Termine aus konzerte.json erhalten – die Website verliert nie Termine wegen
eines Netzwerkfehlers. Nur Standardbibliothek, keine Zusatzpakete.
"""
import datetime, html, json, os, re, sys, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
DATEI = os.path.join(HIER, "konzerte.json")
AGENT = "Mozilla/5.0 (compatible; marcscheidegger.ch Konzertabgleich)"

# Schreibweisen, die auf marcscheidegger.ch anders stehen sollen als auf der Band-Website
KORREKTUREN = {
    "Schlösser Mattstetten": "Schlössli Mattstetten",
    "Chilehus Hedigen": "Chilehus Hedingen",          # Tippfehler auf der Band-Website
}

MONATE = {m: i + 1 for i, m in enumerate(
    ["januar", "februar", "märz", "april", "mai", "juni", "juli", "august",
     "september", "oktober", "november", "dezember"])}


def laden(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def korrigieren(text):
    for alt, neu in KORREKTUREN.items():
        text = text.replace(alt, neu)
    return text.replace(" - ", " – ")          # Bindestrich mit Leerzeichen → Gedankenstrich


def text_von(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


# ---------------------------------------------------------------- Julian von Flüe Trio
def julian_von_fluee():
    s = laden("https://julianvonfluee.ch/live/")
    termine = []
    jahr = None
    # Überschriften (Jahr in h1/h2, Datum in h4) und Absätze der Reihe nach durchgehen
    for tag, inhalt in re.findall(r"<(h[1-4]|p)[^>]*>(.*?)</\1>", s, flags=re.S):
        t = text_von(inhalt)
        if tag in ("h1", "h2") and re.fullmatch(r"20\d\d", t):
            jahr = int(t)
            continue
        if tag == "h4":
            m = re.fullmatch(r"\w+,\s*(\d{1,2})\.\s*([A-Za-zäÄ]+)", t)
            if jahr and m and m.group(2).lower() in MONATE:
                termine.append({"datum": datetime.date(jahr, MONATE[m.group(2).lower()], int(m.group(1))).isoformat(),
                                "zeit": "", "band": "julian-von-fluee", "ort": "", "link": "", "_zeilen": []})
            continue
        if tag == "p" and termine and not termine[-1]["ort"]:
            # Zeilen des Absatzes (getrennt durch <br>), mit ihren Links
            for zeile in re.split(r"<br\s*/?>", inhalt):
                text = text_von(zeile)
                href = re.search(r'href="([^"]+)"', zeile)
                if not text:
                    continue
                k = termine[-1]
                z = re.fullmatch(r"(\d{1,2}):(\d\d)\s*Uhr", text)
                if z:
                    k["zeit"] = f"{int(z.group(1)):02d}:{z.group(2)}"
                elif re.search(r"tickets|infos|informationen", text, re.I) and href:
                    k["link"] = href.group(1)            # Ticket-Link hat Vorrang
                elif re.match(r"vorverkauf", text, re.I):
                    continue
                else:
                    k["_zeilen"].append(text)
                    if href and not k["link"]:
                        k["link"] = href.group(1)
            k = termine[-1]
            k["ort"] = korrigieren(", ".join(k.pop("_zeilen")))
    for k in termine:
        k.pop("_zeilen", None)
    return [k for k in termine if k["ort"]]


# ---------------------------------------------------------------- Mala Oreen
def mala_oreen():
    daten = json.loads(laden("https://api-calendar.optune.me/v4/artist/events/Mala-Oreen"))
    termine = []
    for e in daten:
        v = e.get("venue") or {}
        ort = ", ".join(x for x in [e.get("title", "").strip(), v.get("name", "").strip(), v.get("city", "").strip()] if x)
        termine.append({
            "datum": e["playDate"][:10],
            "zeit": e.get("playTime") or e.get("startTime") or "",
            "band": "mala-oreen",
            "ort": korrigieren(ort),
            "link": e.get("ticketLink") or v.get("website") or "",
        })
    return termine


# ---------------------------------------------------------------- Zusammenführen
def main():
    alt = []
    if os.path.exists(DATEI):
        with open(DATEI) as f:
            alt = json.load(f)
    neu, meldungen = [], []
    for band, holen in (("julian-von-fluee", julian_von_fluee), ("mala-oreen", mala_oreen)):
        try:
            termine = holen()
            # Plausibilität: gültige Daten, und eine Band-Seite mit Konzerten liefert nicht plötzlich 0
            for k in termine:
                datetime.date.fromisoformat(k["datum"])
            bisher = [k for k in alt if k["band"] == band]
            if not termine and bisher:
                raise ValueError("keine Termine gefunden – bisherige bleiben")
            neu += termine
            meldungen.append(f"{band}: {len(termine)} Termine")
        except Exception as e:                     # Quelle nicht erreichbar oder verändert
            neu += [k for k in alt if k["band"] == band]
            meldungen.append(f"{band}: FEHLER ({e}) – bisherige Termine behalten")
    neu.sort(key=lambda k: (k["datum"], k["zeit"]))
    with open(DATEI, "w") as f:
        json.dump(neu, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n".join(meldungen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
