// marcscheidegger.ch – Navigation (Mobil), Jahr in der Fusszeile, Rückmeldung Kontaktformular
document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.getElementById('nav');
    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            const open = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', open);
        });
    }

    document.querySelectorAll('[data-year]').forEach(el => {
        el.textContent = new Date().getFullYear();
    });

    // Konzertlisten: vergangene Daten ausblenden, auf der Startseite nur die nächsten N zeigen
    const heute = new Date().toISOString().slice(0, 10);
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

    // Clips: Vorschaubild durch den Player ersetzen – erst dann wird YouTube/SRF geladen.
    // Es läuft immer nur ein Clip: der vorherige wird wieder zum Vorschaubild.
    let aktiv = null;
    document.querySelectorAll('.clip-play[data-embed]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();
            if (aktiv) aktiv.player.replaceWith(aktiv.vorschau);
            const f = document.createElement('iframe');
            aktiv = { player: f, vorschau: a };
            f.src = a.dataset.embed;
            f.title = a.dataset.title;
            f.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
            f.allowFullscreen = true;
            a.replaceWith(f);
        });
    });

    // kontakt.php leitet mit ?gesendet=1 oder ?fehler=1 zurück
    const params = new URLSearchParams(location.search);
    const show = id => { const el = document.getElementById(id); if (el) el.hidden = false; };
    if (params.has('gesendet')) show('msg-ok');
    if (params.has('fehler')) show('msg-err');
});
