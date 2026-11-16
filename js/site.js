// =============================================================================
// marcscheidegger.ch – kleine Funktionen im Browser
// =============================================================================
// Die Website funktioniert auch ohne JavaScript (alle Inhalte stehen im HTML).
// Dieses Skript ergänzt nur Komfort:
//   1. Handy-Menü auf- und zuklappen
//   2. Jahreszahl in der Fusszeile aktuell halten
//   3. Konzertlisten: vergangene Termine ausblenden
//   4. Videos und Hörproben erst nach Klick laden (Datenschutz)
// Nach Änderungen in dieser Datei in build.py die Zahl V erhöhen.

// Markiert die Seite als "JavaScript aktiv". Das CSS versteckt das Handy-Menü nur,
// wenn diese Klasse da ist – ohne JavaScript bleibt die Navigation sichtbar.
document.documentElement.classList.add('js');

// Alles Weitere erst, wenn die Seite fertig geladen ist
document.addEventListener('DOMContentLoaded', () => {

    // ---------- 1. Handy-Menü ----------
    // Klick auf "Menü" klappt die Navigation auf bzw. zu (CSS-Klasse "open").
    // aria-expanded sagt Screenreadern, ob das Menü offen ist.
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.getElementById('nav');
    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            const open = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', open);
        });
    }

    // ---------- 2. Jahreszahl ----------
    // Ersetzt "© 2026" in der Fusszeile durch das aktuelle Jahr.
    document.querySelectorAll('[data-year]').forEach(el => {
        el.textContent = new Date().getFullYear();
    });

    // ---------- 3. Konzertlisten ----------
    // Jede Zeile trägt ihr Datum (data-date="2027-03-18"). Ist es vor heute, wird die
    // Zeile ausgeblendet. Die Startseite hat data-limit="5" und zeigt nur die nächsten 5.
    // Sind keine Termine mehr übrig, erscheint stattdessen der Hinweis "gigs-empty".
    const heute = new Date().toISOString().slice(0, 10);   // z. B. "2026-11-01"
    document.querySelectorAll('.gigs').forEach(list => {
        const limit = Number(list.dataset.limit) || Infinity;
        let shown = 0;
        list.querySelectorAll('li[data-date]').forEach(li => {
            li.hidden = li.dataset.date < heute || shown++ >= limit;
        });
        if (!shown) {
            list.hidden = true;
            const empty = list.nextElementSibling;
            if (empty && empty.classList.contains('gigs-empty')) empty.hidden = false;
        }
    });

    // ---------- 4. Videos und Hörproben ----------
    // Beim Seitenaufruf sind nur lokale Vorschaubilder bzw. Textzeilen zu sehen.
    // Erst ein Klick lädt den Player von YouTube, SRF oder Apple Music.
    // Es läuft immer nur eines: entweder ein Video oder eine Hörprobe im Mini-Player.
    let aktiv = null;   // gerade laufendes Video: { player: iframe, vorschau: ursprünglicher Link }
    let mini = null;    // gerade offener Mini-Player (Hörprobe)

    // Laufendes Video stoppen: Player wieder durch das Vorschaubild ersetzen
    const clipStoppen = () => {
        if (aktiv) aktiv.player.replaceWith(aktiv.vorschau);
        aktiv = null;
    };
    // Mini-Player schliessen und die Markierung "spielt" entfernen
    const miniSchliessen = () => {
        if (mini) mini.remove();
        mini = null;
        document.querySelectorAll('.spielt').forEach(t => t.classList.remove('spielt'));   // Hörprobe-Zeile oder Plattenspieler
    };

    // Mini-Player unten rechts öffnen und den Auslöser (Zeile oder Logo) als "spielt" markieren
    const miniOeffnen = (ausloeser) => {
        clipStoppen();
        miniSchliessen();
        mini = document.createElement('div');
        mini.className = 'mini-player';
        mini.innerHTML = '<div class="mp-head"><span></span><button type="button" aria-label="Hörprobe schliessen">×</button></div>';
        mini.querySelector('span').textContent = '♪ ' + ausloeser.dataset.title;
        mini.querySelector('button').addEventListener('click', miniSchliessen);
        const f = document.createElement('iframe');
        f.src = ausloeser.dataset.embed;
        f.title = 'Hörprobe: ' + ausloeser.dataset.title;
        f.allow = 'autoplay; encrypted-media';
        mini.append(f);
        document.body.append(mini);
        ausloeser.classList.add('spielt');
    };

    // Hörproben: Klick öffnet unten rechts den Mini-Player mit dem Apple-Music-Player.
    // Die Player-Adresse steht im HTML in data-embed (erzeugt von build.py).
    document.querySelectorAll('.track[data-embed]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();          // nicht zu Apple Music wechseln, sondern hier abspielen
            miniOeffnen(a);
        });
    });

    // Plattenspieler im Logo (nur Startseite, dort hat das Logo data-jukebox):
    // Klick auf den Plattenspieler öffnet bzw. schliesst die Jukebox mit allen Hörproben.
    // Die Musik läuft weiter, auch wenn die Jukebox zugeht; solange sie läuft, dreht sich die Platte.
    const logo = document.querySelector('.logo[data-jukebox]');
    const jukebox = document.getElementById('jukebox');
    if (logo && jukebox) {
        logo.setAttribute('aria-expanded', 'false');
        const jukeboxZeigen = (zeigen) => {
            jukebox.hidden = !zeigen;
            logo.setAttribute('aria-expanded', String(zeigen));
            if (zeigen) jukebox.querySelector('.track')?.focus({ preventScroll: true });
        };
        logo.addEventListener('click', e => {
            if (!e.target.closest('.logo-zeichen')) return;   // Klick auf den Namen: normaler Link
            e.preventDefault();
            jukeboxZeigen(jukebox.hidden);
        });
        jukebox.querySelector('.jb-kopf button').addEventListener('click', () => jukeboxZeigen(false));
        document.addEventListener('keydown', e => { if (e.key === 'Escape' && !jukebox.hidden) jukeboxZeigen(false); });
        // Platte dreht sich, solange eine Hörprobe läuft (egal ob aus der Jukebox oder von einer Bandseite)
        new MutationObserver(() => logo.classList.toggle('spielt', !!mini))
            .observe(document.body, { childList: true });
    }

    // Videos: Klick ersetzt das Vorschaubild an Ort und Stelle durch den echten Player.
    document.querySelectorAll('.clip-play[data-embed]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();          // nicht zu YouTube/SRF wechseln, sondern hier abspielen
            clipStoppen();
            miniSchliessen();
            const f = document.createElement('iframe');
            aktiv = { player: f, vorschau: a };
            f.src = a.dataset.embed;
            f.title = a.dataset.title;
            f.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
            f.allowFullscreen = true;
            a.replaceWith(f);
        });
    });
});
