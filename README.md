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

## Noch offen vor dem Livegang

- Impressum: Postadresse ergänzen
- Datenschutz: Hoster ergänzen
- Testen auf einer Subdomain (z.B. neu.marcscheidegger.ch), erst danach auf marcscheidegger.ch umstellen
