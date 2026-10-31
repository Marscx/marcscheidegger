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

    // Clips und Hörproben: YouTube/SRF wird erst nach Klick geladen.
    // Es läuft immer nur etwas: ein Clip oder eine Hörprobe im Mini-Player.
    let aktiv = null;
    let mini = null;
    const clipStoppen = () => {
        if (aktiv) aktiv.player.replaceWith(aktiv.vorschau);
        aktiv = null;
    };
    const miniSchliessen = () => {
        if (mini) mini.remove();
        mini = null;
        document.querySelectorAll('.track.spielt').forEach(t => t.classList.remove('spielt'));
    };

    document.querySelectorAll('.track[data-embed]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();
            clipStoppen();
            miniSchliessen();
            mini = document.createElement('div');
            mini.className = 'mini-player';
            mini.innerHTML = '<div class="mp-head"><span></span><button type="button" aria-label="Hörprobe schliessen">×</button></div>';
            mini.querySelector('span').textContent = '♪ ' + a.dataset.title;
            mini.querySelector('button').addEventListener('click', miniSchliessen);
            const f = document.createElement('iframe');
            f.src = a.dataset.embed;
            f.title = 'Hörprobe: ' + a.dataset.title;
            f.allow = 'autoplay; encrypted-media';
            // Apple Music braucht eine feste Höhe statt 16:9
            if (a.dataset.h) {
                f.style.aspectRatio = 'auto';
                f.style.height = a.dataset.h + 'px';
            }
            mini.append(f);
            document.body.append(mini);
            a.classList.add('spielt');
        });
    });

    document.querySelectorAll('.clip-play[data-embed]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();
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

    // kontakt.php leitet mit ?gesendet=1 oder ?fehler=1 zurück
    const params = new URLSearchParams(location.search);
    const show = id => { const el = document.getElementById(id); if (el) el.hidden = false; };
    if (params.has('gesendet')) show('msg-ok');
    if (params.has('fehler')) show('msg-err');
});
