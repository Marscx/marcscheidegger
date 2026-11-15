# marcscheidegger.ch

Website von Marc Scheidegger – reines HTML/CSS/JS, ohne CMS und ohne Abhängigkeiten.
Ersetzt die bisherige WordPress-Seite.

## Aufbau

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite |
| `projekte.html` | Aktuelle Bands, frühere Bands, Begleitmusiker & Studio |
| `chronologie.html` | Alle Stationen nach Jahren |
| `lernen.html` | Übe-Tools, Online-Kurse, Links |
| `kontakt.html` | E-Mail und Social Media |
| `impressum.html`, `datenschutz.html`, `404.html` | Rechtliches, Fehlerseite |
| `css/site.css`, `js/site.js` | Gemeinsames Design, Mobil-Menü |
| `.htaccess` | HTTPS, 301-Weiterleitungen der alten WordPress-Adressen, Caching |
| `img/` | Fotos (JPG, max. 2000 px) und Übe-Tool-Grafiken (`tool-grafiken-quelle.html` ist die Vorlage) |

## Inhalte ändern

Alle HTML-Seiten werden von `build.py` erzeugt (Kopf- und Fusszeile, Projekte, Konzerte,
Chronologie). Inhalte dort ändern und danach neu erzeugen:

```bash
python3 build.py
```

- **Konzerte:** Liste `KONZERTE` – vergangene Daten blendet `site.js` automatisch aus,
  die Startseite zeigt die nächsten fünf.
- **Projekte:** Liste `P` – Gruppe `aktuell`, `frueher` oder `begleit`. Die Chronologie
  entsteht automatisch aus den Fakten der Projekte.
- Bei Änderungen an `site.css` / `site.js` die Zahl `V` in `build.py` erhöhen.

## Lokal ansehen

```bash
php -S localhost:8090
```

Dann http://localhost:8090 öffnen.

## Konzerte aktualisieren (einmal pro Woche)

```
python3 konzerte.py && python3 build.py
```

`konzerte.py` liest die Termine von julianvonfluee.ch/live und vom Optune-Kalender von
Mala Oreen und schreibt sie nach `konzerte.json`; `build.py` baut daraus die Seiten.
Danach committen und pushen. Ist eine Band-Website nicht erreichbar, bleiben deren
bisherige Termine stehen. Schreibweisen korrigieren: `KORREKTUREN` in `konzerte.py`.
Konzerte, die auf keiner Band-Website stehen: `KONZERTE_VON_HAND` in `build.py`.

## Veröffentlichen (Plesk)

1. **Test:** Subdomain `neu.marcscheidegger.ch` → Git → Repository
   `https://github.com/Marscx/marcscheidegger.git`, Branch `main`, automatische Bereitstellung
   bei Push, Bereitstellungspfad = Dokumentenstamm der Subdomain.
   SSL/TLS (Let's Encrypt) für die Subdomain aktivieren – `.htaccess` leitet auf HTTPS um.
   Auf `neu.` sendet der Server `noindex`, damit Google die Testseite nicht aufnimmt.
2. **Livegang:** Die Website wird direkt in `httpdocs` von `marcscheidegger.ch` bereitgestellt
   (Git-Bereitstellungspfad in Plesk = `httpdocs`). So bleiben die verlinkten Unterordner in
   `httpdocs` (moodle, MarcBuch …) unter ihren Adressen erreichbar. Die WordPress-Dateien bleiben
   liegen, sind aber durch `.htaccess` gesperrt (Abschnitt 4); die Startseite ist `index.html`.
   Die Subdomain `neu.` zeigt danach ebenfalls auf `httpdocs` – `.htaccess` (Abschnitt 1b)
   leitet jede Adresse dort per 301 auf `marcscheidegger.ch` um.
   Vorher in Plesk eine vollständige Sicherung erstellen.

## Urheberrecht

Texte, Fotos und Grafiken: © Marc Scheidegger bzw. die jeweiligen Bands und Fotografinnen und
Fotografen. Alle Rechte vorbehalten – keine Weiterverwendung ohne Einwilligung.

## Design-Variante mit Tailwind CSS (Branch `design-tailwind`)

Auf diesem Branch wird das Aussehen mit [Tailwind CSS](https://tailwindcss.com) v4 erzeugt.

- **Quelle:** `src/site.tailwind.css` – Farben (Nachtblau `night-*`, Koralle `akzent-*`) und alle Bausteine.
- **Ergebnis:** `css/site.css` – wird erzeugt, nie direkt bearbeiten. Es enthält nur die Klassen,
  die in `build.py` und `js/site.js` vorkommen, und kommt mit Git auf den Server (Plesk baut nichts).
- **Programm:** `tools/tailwindcss-macos-arm64` (Tailwind v4.3.3, offizieller Download von GitHub,
  Prüfsumme kontrolliert). Liegt nicht in Git. Neu holen:
  `gh release download v4.3.3 -R tailwindlabs/tailwindcss -p tailwindcss-macos-arm64 -D tools && chmod +x tools/tailwindcss-macos-arm64`
- `python3 build.py` erzeugt die HTML-Seiten und danach automatisch `css/site.css`.
- Kopf- und Fusszeile sowie der Seitenkopf der Startseite sind direkt in `build.py` mit
  Tailwind-Klassen gestaltet; alle übrigen Bausteine (Karten, Konzerte, Hörproben, Zeitleiste …)
  behalten ihre Namen und sind in der Quelle aus Tailwind-Werkzeugen zusammengesetzt.
- Es werden keine Schriften oder Dateien von fremden Servern geladen.
- **Logo-Schrift:** `fonts/marc-versalien.ttf` ist Marcs Handschrift, aber nur mit den Grossbuchstaben
  des Namens (A C D E G H I M R S) und dem Leerzeichen – alle anderen Zeichen sind entfernt, damit sich
  aus der Datei keine Unterschrift nachbauen lässt. Die volle Schrift kommt nie in dieses Repo.
