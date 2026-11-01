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

## Veröffentlichen (Plesk)

1. **Test:** Subdomain `neu.marcscheidegger.ch` → Git → Repository
   `https://github.com/Marscx/marcscheidegger.git`, Branch `main`, automatische Bereitstellung
   bei Push, Bereitstellungspfad = Dokumentenstamm der Subdomain.
   SSL/TLS (Let's Encrypt) für die Subdomain aktivieren – `.htaccess` leitet auf HTTPS um.
   Auf `neu.` sendet der Server `noindex`, damit Google die Testseite nicht aufnimmt.
2. **Livegang:** bei `marcscheidegger.ch` unter Hosting-Einstellungen den Dokumentenstamm auf den
   Ordner von `neu.marcscheidegger.ch` stellen. Die WordPress-Dateien in `httpdocs` bleiben
   unverändert; zurück geht es, indem man den Dokumentenstamm wieder auf `httpdocs` stellt.

Noch offen vor dem Livegang:

- Impressum: Postadresse ergänzen
- Datenschutz: Hoster ergänzen

## Urheberrecht

Texte, Fotos und Grafiken: © Marc Scheidegger bzw. die jeweiligen Bands und Fotografinnen und
Fotografen. Alle Rechte vorbehalten – keine Weiterverwendung ohne Einwilligung.
