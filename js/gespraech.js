'use strict';

// =============================================================================
// Schülergespräch und Jahres-Dashboard in der Übemappe (Seite mappe.html)
// =============================================================================
// Teil "gespraech" der Übemappe (Format: MAPPE.md in den Übe-Tools):
//   { version: 1, gespraeche: [ { datum, schuljahr, spieljahr, band, konzerte,
//       bewertung: { kriteriumId: { sus, wichtig, lp } },   // je 0–5 Sterne (0 = leer)
//       notizen: { themaId: "…" }, ueben: { ist, ziel }, handlungen: [ { ziel, massnahme, bis } ],
//       allgemein: "…", kennzahlen: { … } } ] }
// sus = «So gut kann ich es» (Schüler/in), wichtig = «So wichtig ist es mir» (Schüler/in),
// lp = Einschätzung der Lehrperson. Keine Noten: Die Sterne zeigen Stand und Schwerpunkte,
// die Lücke zwischen «wichtig» und «kann ich» zeigt mögliche Ziele.
//
// Die Kriterien stammen aus Marcs Vorlage «Schülergespräch». Neue Kriterien unten in
// KATALOG ergänzen – bestehende IDs nie umbenennen, sonst passen alte Mappen nicht mehr.

const Gespraech = (() => {
    const KATALOG = [
        { gruppe: 'Linke Hand', themen: [
            { id: 'akkordspiel', name: 'Akkordspiel', kriterien: [['minis', 'Die Minis'], ['akkorde1', 'Die Akkorde der 1. Lage'], ['barre', 'Barré Akkorde'], ['daumengriff', 'Daumengriff'], ['akkordeFinden', 'Akkorde selber finden']] },
            { id: 'melodiespiel', name: 'Melodiespiel', kriterien: [['toene1', 'Die Töne der 1. Lage'], ['tab', 'Spielen nach TAB'], ['riffs', 'Rock Riffs'], ['percussive', 'Percussive Fingerstyle']] },
            { id: 'solospiel', name: 'Solospiel', kriterien: [['improvisieren', 'Improvisieren']] },
            { id: 'technik', name: 'Technik', kriterien: [['fingersatz', 'Fingersatz']] },
        ] },
        { gruppe: 'Rechte Hand', themen: [
            { id: 'anschlagMelodie', name: 'Anschlag Melodie', kriterien: [['daumenschlag', 'Daumenschlag'], ['pickMelodie', 'Pick'], ['tirando', 'Tirando'], ['chickenPick', 'Chicken Pick'], ['fingerstyle', 'Fingerstyle']] },
            { id: 'anschlagBegleitung', name: 'Anschlag Begleitung', kriterien: [['daumen', 'Daumen'], ['pickBegleitung', 'Pick'], ['spanisch', 'Spanische Schlagmuster']] },
            { id: 'ton', name: 'Ton', kriterien: [['schoenerTon', 'Schöner Ton'], ['verstaerker', 'Verstärker-Ton einstellen'], ['ausDenHaenden', 'Aus den Händen']] },
        ] },
        { gruppe: 'Musik', themen: [
            { id: 'gestaltung', name: 'Gestaltung', kriterien: [['gestaltung', 'Gestaltung']] },
            { id: 'improvisation', name: 'Improvisation', kriterien: [['improvisation', 'Improvisation']] },
            { id: 'zusammenspiel', name: 'Zusammenspiel', kriterien: [['band', 'Band']] },
            { id: 'vorspiel', name: 'Vorspiel', kriterien: [['vorspiel', 'Vorspiel']] },
            { id: 'motivation', name: 'Motivation', kriterien: [['motivation', 'Motivation']] },
        ] },
    ];
    const THEMEN = KATALOG.flatMap((g) => g.themen);
    const KRITERIEN = THEMEN.flatMap((t) => t.kriterien.map(([id, name]) => ({ id, name, thema: t })));
    const REIHEN = [
        ['sus', 'Kann ich', 'So gut kann ich es (Schüler/in)'],
        ['wichtig', 'Wichtig', 'So wichtig ist es mir (Schüler/in)'],
        ['lp', 'Lehrperson', 'Einschätzung der Lehrperson'],
    ];
    const AKKORDE = ['C', 'A', 'G', 'E', 'F', 'D', 'Am', 'Em', 'Dm', 'C7', 'A7', 'G7', 'E7', 'D7', 'B7', 'Am7', 'Em7', 'Dm7', 'Bm7'];

    // ---------- Hilfen ----------
    const el = (tag, cls, text) => {
        const e = document.createElement(tag);
        if (cls) e.className = cls;
        if (text !== undefined) e.textContent = text;
        return e;
    };
    const tag = (d) => new Date(d).toLocaleDateString('de-CH', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
    const sterne = (n) => (n ? '★'.repeat(n) + '☆'.repeat(5 - n) : '–');
    function dauer(sec) {
        sec = Math.max(0, Math.round(sec || 0));
        const h = Math.floor(sec / 3600), m = Math.round((sec % 3600) / 60);
        return h ? `${h} h ${String(m).padStart(2, '0')} min` : `${m} min`;
    }
    const heute = () => {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    };

    // ---------- Schuljahr: 1. August bis 31. Juli ----------
    function schuljahrVon(d) {
        const x = new Date(d), y = x.getMonth() >= 7 ? x.getFullYear() : x.getFullYear() - 1;
        return `${y}/${String(y + 1).slice(2)}`;
    }
    function schuljahrGrenzen(sj) {
        const y = parseInt(sj, 10);
        return { von: new Date(y, 7, 1), bis: new Date(y + 1, 7, 1) };
    }
    function schuljahre(mappe) {
        const s = new Set([schuljahrVon(new Date())]);
        const t = mappe.tools.uebetimer, w = mappe.tools.wuerfel, g = mappe.tools.gespraech;
        ((t && t.journal) || []).forEach((e) => e && e.start && s.add(schuljahrVon(e.start)));
        ((w && w.verlauf) || []).forEach((v) => v && v.zeit && s.add(schuljahrVon(v.zeit)));
        ((g && g.gespraeche) || []).forEach((x) => x && x.schuljahr && s.add(x.schuljahr));
        return [...s].sort().reverse();
    }

    // Kennzahlen eines Schuljahres aus Übe-Timer und Würfel
    function kennzahlen(mappe, sj) {
        const { von, bis } = schuljahrGrenzen(sj);
        const imJahr = (d) => { const x = new Date(d); return x >= von && x < bis; };
        const t = mappe.tools.uebetimer, w = mappe.tools.wuerfel;
        const journal = ((t && t.journal) || []).filter((e) => e && e.start && imJahr(e.start));
        const geuebt = (e) => (e.uebungen || []).reduce((s, u) => s + (u.geuebt || 0), 0);
        const monate = new Array(12).fill(0);          // August … Juli
        const wochen = new Set(), themen = {};
        for (const e of journal) {
            const d = new Date(e.start);
            monate[(d.getMonth() + 5) % 12] += geuebt(e);
            const mo = new Date(d); mo.setHours(0, 0, 0, 0); mo.setDate(mo.getDate() - ((mo.getDay() + 6) % 7));
            wochen.add(mo.getTime());
            for (const u of e.uebungen || []) {
                const k = (u.thema || 'Ohne Thema').trim();
                themen[k] = (themen[k] || 0) + (u.geuebt || 0);
            }
        }
        const verlauf = ((w && w.verlauf) || []).filter((v) => v && v.zeit && imJahr(v.zeit));
        const lern = (w && w.lernstand) || {};
        // Akkorde, die im Schuljahr zum ersten Mal gewusst wurden
        const vorher = new Set(((w && w.verlauf) || []).filter((v) => v.gewusst && new Date(v.zeit) < von).map((v) => v.akkord));
        const neu = new Set(verlauf.filter((v) => v.gewusst && !vorher.has(v.akkord)).map((v) => v.akkord));
        return {
            schuljahr: sj,
            sessions: journal.length,
            uebezeit: journal.reduce((s, e) => s + geuebt(e), 0),
            wochenMitUeben: wochen.size,
            monate,
            themen: Object.entries(themen).sort((a, b) => b[1] - a[1]).slice(0, 6),
            antworten: verlauf.length,
            akkordeNeu: AKKORDE.filter((a) => neu.has(a)),
            akkordeGewusst: AKKORDE.filter((a) => lern[a] && lern[a].zuletzt === 'ja').length,
            hatWuerfel: !!w,
            hatTimer: !!t,
        };
    }

    // ---------- Jahres-Dashboard ----------
    let gewaehltesJahr = null;
    function jahrZeigen(mappe, box) {
        box.textContent = '';
        const jahre = schuljahre(mappe);
        if (!gewaehltesJahr || !jahre.includes(gewaehltesJahr)) gewaehltesJahr = jahre[0];
        const kopf = el('div', 'jahr-kopf');
        const wahl = el('select', 'jahr-wahl');
        wahl.setAttribute('aria-label', 'Schuljahr');
        jahre.forEach((j) => { const o = el('option', '', 'Schuljahr ' + j); o.value = j; wahl.append(o); });
        wahl.value = gewaehltesJahr;
        wahl.addEventListener('change', () => { gewaehltesJahr = wahl.value; jahrZeigen(mappe, box); });
        kopf.append(wahl);
        box.append(kopf);

        const k = kennzahlen(mappe, gewaehltesJahr);
        const zahlen = el('div', 'mappe-zahlen');
        const kachel = (wert, text) => { const d = el('div', 'mappe-zahl'); d.append(el('b', '', String(wert)), el('span', '', text)); zahlen.append(d); };
        kachel(k.sessions, 'Übesessions');
        kachel(dauer(k.uebezeit), 'Übezeit');
        kachel(k.wochenMitUeben, 'Wochen mit Üben');
        kachel(k.wochenMitUeben ? dauer(k.uebezeit / k.wochenMitUeben) : '–', 'pro Übewoche');
        if (k.hatWuerfel) {
            kachel(`${k.akkordeGewusst} / ${AKKORDE.length}`, 'Akkorde gewusst (heute)');
            kachel(k.akkordeNeu.length, 'Akkorde neu gelernt');
        }
        box.append(zahlen);

        // Übezeit pro Monat
        const MONATE = ['Aug', 'Sep', 'Okt', 'Nov', 'Dez', 'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul'];
        const max = Math.max(1, ...k.monate);
        const saeulen = el('div', 'mappe-wochen jahr-monate');
        saeulen.setAttribute('aria-label', 'Übezeit pro Monat');
        k.monate.forEach((sec, i) => {
            const sp = el('div', 'mappe-woche');
            sp.title = `${MONATE[i]}: ${dauer(sec)}`;
            const s = el('div', 'saeule'), b = el('i');
            b.style.height = Math.round((sec / max) * 100) + '%';
            s.append(b);
            sp.append(el('span', 'wert', sec ? Math.round(sec / 3600 * 10) / 10 + ' h' : ''), s, el('span', 'datum', MONATE[i]));
            saeulen.append(sp);
        });
        box.append(saeulen);

        if (k.themen.length) {
            box.append(el('h4', '', 'Am meisten geübt'));
            const ol = el('ol', 'jahr-themen');
            k.themen.forEach(([name, sec]) => { const li = el('li'); li.append(el('span', '', name), el('b', '', dauer(sec))); ol.append(li); });
            box.append(ol);
        }
        if (k.akkordeNeu.length) box.append(el('p', 'mappe-hinweis', 'Neu gelernte Akkorde: ' + k.akkordeNeu.join(', ')));
        if (!k.sessions && !k.antworten) box.append(el('p', 'mappe-hinweis', 'In diesem Schuljahr gibt es noch keine Einträge aus Übe-Timer oder Würfel.'));
    }

    // ---------- Gespräch: Daten ----------
    function teil(mappe) {
        const t = Mappe.teil(mappe, 'gespraech', () => ({ version: 1, gespraeche: [] }));
        if (!Array.isArray(t.gespraeche)) t.gespraeche = [];
        return t;
    }
    function neuesGespraech(mappe) {
        const liste = teil(mappe).gespraeche;
        const vorher = liste[liste.length - 1];
        const g = {
            datum: heute(),
            schuljahr: schuljahrVon(new Date()),
            spieljahr: vorher && vorher.spieljahr ? vorher.spieljahr + 1 : null,
            band: vorher ? vorher.band : null,
            konzerte: null,
            bewertung: {},
            notizen: {},
            ueben: { ist: 0, ziel: 0 },
            handlungen: [],
            allgemein: '',
        };
        liste.push(g);
        return g;
    }
    function bewertung(g, id) {
        if (!g.bewertung[id]) g.bewertung[id] = { sus: 0, wichtig: 0, lp: 0 };
        return g.bewertung[id];
    }
    // Durchschnitt eines Themas für eine Reihe (nur bewertete Kriterien)
    function themaWert(g, thema, reihe) {
        const w = thema.kriterien.map(([id]) => (g.bewertung[id] || {})[reihe] || 0).filter((x) => x > 0);
        return w.length ? w.reduce((a, b) => a + b, 0) / w.length : 0;
    }
    // Mögliche Ziele: grosse Lücke zwischen «wichtig» und «kann ich» (bzw. Einschätzung Lehrperson)
    function moeglicheZiele(g) {
        return KRITERIEN.map((k) => {
            const b = g.bewertung[k.id] || {};
            const kann = b.sus || b.lp || 0;
            return { k, luecke: (b.wichtig || 0) - kann, b };
        }).filter((x) => x.b.wichtig >= 3 && x.luecke > 0)
            .sort((a, b) => b.luecke - a.luecke || b.b.wichtig - a.b.wichtig).slice(0, 6);
    }

    // ---------- Spinnennetz (SVG) ----------
    function spinne(g, vorher) {
        const N = THEMEN.length, R = 120, cx = 240, cy = 160;
        const punkt = (i, w) => {
            const a = -Math.PI / 2 + (2 * Math.PI * i) / N;
            return [cx + Math.cos(a) * R * (w / 5), cy + Math.sin(a) * R * (w / 5)];
        };
        const t = [];
        for (let s = 1; s <= 5; s++) {
            t.push(`<polygon points="${THEMEN.map((_, i) => punkt(i, s).join(',')).join(' ')}" class="netz${s === 5 ? ' rand' : ''}"/>`);
        }
        THEMEN.forEach((th, i) => {
            const [x, y] = punkt(i, 5), [lx, ly] = punkt(i, 6.15);
            t.push(`<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" class="achse"/>`);
            const anker = Math.abs(lx - cx) < 8 ? 'middle' : lx < cx ? 'end' : 'start';
            t.push(`<text x="${lx.toFixed(1)}" y="${(ly + 4).toFixed(1)}" text-anchor="${anker}" class="beschriftung">${th.name}</text>`);
        });
        const linie = (gg, reihe, cls) => {
            const werte = THEMEN.map((th) => themaWert(gg, th, reihe));
            if (!werte.some((x) => x > 0)) return;
            t.push(`<polygon points="${werte.map((w, i) => punkt(i, w).map((v) => v.toFixed(1)).join(',')).join(' ')}" class="${cls}"/>`);
        };
        if (vorher) linie(vorher, 'sus', 'vorher');
        linie(g, 'wichtig', 'wichtig');
        linie(g, 'lp', 'lp');
        linie(g, 'sus', 'sus');
        return `<svg viewBox="0 0 480 330" class="spinne" role="img" aria-label="Spinnennetz: Stand und Schwerpunkte pro Thema">${t.join('')}</svg>`;
    }

    // ---------- Gespräch: Anzeige und Bearbeitung ----------
    let aktuell = 0;   // Index des angezeigten Gesprächs
    function zeigen(mappe, box) {
        box.textContent = '';
        const liste = teil(mappe).gespraeche;
        if (aktuell >= liste.length) aktuell = liste.length - 1;

        const kopf = el('div', 'gespraech-kopf');
        const reiter = el('div', 'gespraech-reiter');
        liste.forEach((g, i) => {
            const b = el('button', 'btn ghost' + (i === aktuell ? ' aktiv' : ''), tag(g.datum));
            b.type = 'button';
            b.setAttribute('aria-pressed', String(i === aktuell));
            b.addEventListener('click', () => { aktuell = i; zeigen(mappe, box); });
            reiter.append(b);
        });
        const neu = el('button', 'btn', '＋ Neues Gespräch');
        neu.type = 'button';
        neu.addEventListener('click', () => { neuesGespraech(mappe); aktuell = teil(mappe).gespraeche.length - 1; zeigen(mappe, box); });
        reiter.append(neu);
        kopf.append(reiter);
        box.append(kopf);

        if (!liste.length) {
            box.append(el('p', 'mappe-hinweis', 'Noch kein Schülergespräch in dieser Mappe. Mit «Neues Gespräch» beginnst du eines – die Sterne könnt ihr gemeinsam am iPad setzen.'));
            return;
        }
        const g = liste[aktuell];
        const vorher = aktuell > 0 ? liste[aktuell - 1] : null;
        if (!g.bewertung) g.bewertung = {};
        if (!g.notizen) g.notizen = {};
        if (!g.ueben) g.ueben = { ist: 0, ziel: 0 };
        if (!Array.isArray(g.handlungen)) g.handlungen = [];

        // Grunddaten
        const grund = el('div', 'gespraech-grund');
        const feld = (label, typ, wert, setzen, extra) => {
            const l = el('label', 'feld');
            l.append(el('span', '', label));
            const i = el('input');
            i.type = typ;
            if (wert !== null && wert !== undefined) i.value = wert;
            Object.assign(i, extra || {});
            i.addEventListener('input', () => { setzen(i.value); if (typ === 'date') reiter.querySelector('.aktiv').textContent = tag(i.value || g.datum); });
            l.append(i);
            grund.append(l);
        };
        feld('Datum', 'date', g.datum, (v) => { g.datum = v || heute(); });
        feld('Schuljahr', 'text', g.schuljahr, (v) => { g.schuljahr = v.trim(); }, { placeholder: '2026/27', maxLength: 9 });
        feld('Spieljahr', 'number', g.spieljahr, (v) => { g.spieljahr = v ? Number(v) : null; }, { min: 1, max: 30, inputMode: 'numeric' });
        feld('Jahre in einer Band', 'number', g.band, (v) => { g.band = v === '' ? null : Number(v); }, { min: 0, max: 30, inputMode: 'numeric' });
        feld('Konzerte', 'number', g.konzerte, (v) => { g.konzerte = v === '' ? null : Number(v); }, { min: 0, max: 200, inputMode: 'numeric' });
        box.append(grund);

        // Legende
        const leg = el('div', 'stern-legende');
        REIHEN.forEach(([r, kurz, lang]) => { const s = el('span', 'leg-' + r); s.append(el('i'), document.createTextNode(lang)); leg.append(s); });
        box.append(leg);

        // Spinnennetz + mögliche Ziele (werden bei jeder Änderung neu gezeichnet)
        const auswertung = el('div', 'gespraech-auswertung');
        const netz = el('div', 'spinne-box');
        const ziele = el('div', 'ziele-box');
        auswertung.append(netz, ziele);

        const handlungenBox = el('div', 'handlungen-box');
        const auffrischen = () => {
            netz.innerHTML = spinne(g, vorher) + (vorher ? '<p class="mappe-hinweis">Gestrichelt: «Kann ich» beim Gespräch vom ' + tag(vorher.datum) + '</p>' : '');
            ziele.textContent = '';
            ziele.append(el('h4', '', 'Mögliche Ziele'));
            const z = moeglicheZiele(g);
            if (!z.length) ziele.append(el('p', 'mappe-hinweis', 'Hier erscheinen Kriterien, die wichtig sind (ab 3 Sternen), aber noch nicht so gut gehen.'));
            const ol = el('ol', 'ziele');
            z.forEach(({ k, b }) => {
                const li = el('li');
                li.append(el('span', 'ziel-name', `${k.thema.name === k.name ? k.name : k.thema.name + ': ' + k.name}`),
                    el('span', 'ziel-werte', `kann ${b.sus || b.lp || 0} · wichtig ${b.wichtig}`));
                const plus = el('button', 'btn ghost klein', '＋ Handlung');
                plus.type = 'button';
                plus.addEventListener('click', () => {
                    g.handlungen.push({ ziel: k.thema.name === k.name ? k.name : `${k.thema.name}: ${k.name}`, massnahme: '', bis: '' });
                    handlungenZeigen();
                    const felder = handlungenBox.querySelectorAll('.massnahme');
                    if (felder.length) felder[felder.length - 1].focus();
                });
                li.append(plus);
                ol.append(li);
            });
            ziele.append(ol);
        };

        // Sterne-Knöpfe: nochmals auf denselben Stern tippen = leer
        const sternReihe = (wert, setzen, label, cls) => {
            const d = el('div', 'sterne ' + cls);
            d.setAttribute('role', 'group');
            d.setAttribute('aria-label', label);
            const male = () => [...d.children].forEach((b, i) => {
                const an = i < wert();
                b.classList.toggle('an', an);
                b.setAttribute('aria-pressed', String(i + 1 === wert()));
            });
            for (let n = 1; n <= 5; n++) {
                const b = el('button', 'stern', '★');
                b.type = 'button';
                b.setAttribute('aria-label', `${label}: ${n} von 5`);
                b.addEventListener('click', () => { setzen(wert() === n ? 0 : n); male(); auffrischen(); });
                d.append(b);
            }
            male();
            return d;
        };

        const tabelle = el('div', 'kriterien');
        const kopfzeile = el('div', 'kr-kopf');
        kopfzeile.append(el('span', '', ''), ...REIHEN.map(([r, kurz]) => el('span', 'leg-' + r, kurz)));
        tabelle.append(kopfzeile);
        const w = mappe.tools.wuerfel;
        for (const gruppe of KATALOG) {
            tabelle.append(el('h4', 'kr-gruppe', gruppe.gruppe));
            for (const th of gruppe.themen) {
                const einzeln = th.kriterien.length === 1 && th.kriterien[0][1] === th.name;
                if (!einzeln) tabelle.append(el('h5', 'kr-thema', th.name));
                for (const [id, name] of th.kriterien) {
                    const z = el('div', 'kr-zeile' + (einzeln ? ' einzeln' : ''));
                    const n = el('div', 'kr-name', name);
                    if (id === 'akkorde1' && w && w.lernstand) {
                        const gew = AKKORDE.filter((a) => w.lernstand[a] && w.lernstand[a].zuletzt === 'ja').length;
                        n.append(el('small', '', `Würfel: ${gew} von ${AKKORDE.length} gewusst`));
                    }
                    z.append(n);
                    const b = bewertung(g, id);
                    REIHEN.forEach(([r, kurz]) => {
                        const zelle = el('div', 'kr-zelle');
                        zelle.append(el('span', 'kr-label leg-' + r, kurz), sternReihe(() => b[r] || 0, (v) => { b[r] = v; }, `${name} – ${kurz}`, r));
                        z.append(zelle);
                    });
                    tabelle.append(z);
                }
                const notiz = el('textarea', 'kr-notiz');
                notiz.rows = 1;
                notiz.placeholder = `Notiz zu ${th.name} (z. B. Stücke, Fortschritte)`;
                notiz.value = g.notizen[th.id] || '';
                notiz.addEventListener('input', () => { g.notizen[th.id] = notiz.value; });
                tabelle.append(notiz);
            }
        }
        // Üben
        tabelle.append(el('h4', 'kr-gruppe', 'Üben'));
        [['ist', 'Wie ist es'], ['ziel', 'Was nehmen wir uns vor']].forEach(([r, name]) => {
            const z = el('div', 'kr-zeile einzeln ueben');
            z.append(el('div', 'kr-name', name), sternReihe(() => g.ueben[r] || 0, (v) => { g.ueben[r] = v; }, `Üben – ${name}`, r === 'ist' ? 'sus' : 'wichtig'));
            tabelle.append(z);
        });
        box.append(tabelle, auswertung);

        // Handlungen
        box.append(el('h4', 'kr-gruppe', 'Vereinbarte Handlungen'));
        const handlungenZeigen = () => {
            handlungenBox.textContent = '';
            g.handlungen.forEach((h, i) => {
                const z = el('div', 'handlung');
                const f = (cls, ph, key, typ) => {
                    const inp = el(typ === 'area' ? 'textarea' : 'input', cls);
                    if (typ !== 'area') inp.type = 'text';
                    else inp.rows = 1;
                    inp.placeholder = ph;
                    inp.value = h[key] || '';
                    inp.addEventListener('input', () => { h[key] = inp.value; });
                    return inp;
                };
                const weg = el('button', 'plan-weg', '✕');
                weg.type = 'button';
                weg.title = 'Handlung entfernen';
                weg.addEventListener('click', () => { g.handlungen.splice(i, 1); handlungenZeigen(); });
                z.append(f('ziel', 'Ziel', 'ziel'), f('massnahme', 'Was wir tun', 'massnahme', 'area'), f('bis', 'Bis wann', 'bis'), weg);
                handlungenBox.append(z);
            });
            if (!g.handlungen.length) handlungenBox.append(el('p', 'mappe-hinweis', 'Noch keine Handlungen – bei «Mögliche Ziele» auf «＋ Handlung» tippen oder unten selbst eine anlegen.'));
        };
        handlungenZeigen();
        const plus = el('button', 'btn ghost', '＋ Handlung');
        plus.type = 'button';
        plus.addEventListener('click', () => { g.handlungen.push({ ziel: '', massnahme: '', bis: '' }); handlungenZeigen(); });
        box.append(handlungenBox, plus);

        // Allgemeine Notizen
        const allg = el('label', 'feld breit');
        allg.append(el('span', '', 'Allgemeine Notizen zum Gespräch'));
        const ta = el('textarea');
        ta.rows = 3;
        ta.value = g.allgemein || '';
        ta.addEventListener('input', () => { g.allgemein = ta.value; });
        allg.append(ta);
        box.append(allg);

        // Kennzahlen des Schuljahres mitspeichern (damit sie auch später im Gespräch stehen)
        g.kennzahlen = (({ sessions, uebezeit, wochenMitUeben, akkordeGewusst, akkordeNeu }) =>
            ({ sessions, uebezeit, wochenMitUeben, akkordeGewusst, akkordeNeu }))(kennzahlen(mappe, g.schuljahr || schuljahrVon(g.datum)));

        const loeschen = el('button', 'btn ghost loeschen', 'Dieses Gespräch löschen');
        loeschen.type = 'button';
        loeschen.addEventListener('click', () => {
            if (!confirm(`Gespräch vom ${tag(g.datum)} aus der Mappe löschen?`)) return;
            liste.splice(aktuell, 1);
            aktuell = Math.max(0, aktuell - 1);
            zeigen(mappe, box);
        });
        box.append(loeschen);
        auffrischen();
    }

    // ---------- Text für den Download ----------
    function text(mappe) {
        const z = [];
        const g0 = mappe.tools.gespraech;
        const liste = (g0 && g0.gespraeche) || [];
        for (const g of liste.slice().reverse()) {
            const titel = `SCHÜLERGESPRÄCH ${tag(g.datum)}`;
            z.push(titel, '-'.repeat(titel.length));
            z.push(`Schuljahr: ${g.schuljahr || '–'} · Spieljahr: ${g.spieljahr || '–'} · Jahre in einer Band: ${g.band ?? '–'} · Konzerte: ${g.konzerte ?? '–'}`);
            if (g.kennzahlen) {
                const k = g.kennzahlen;
                z.push(`Im Schuljahr: ${k.sessions} Übesessions, ${dauer(k.uebezeit)} geübt in ${k.wochenMitUeben} Wochen · Akkorde gewusst: ${k.akkordeGewusst}/19` +
                    (k.akkordeNeu && k.akkordeNeu.length ? ` (neu: ${k.akkordeNeu.join(', ')})` : ''));
            }
            z.push('', 'Sterne: Kann ich | Wichtig | Lehrperson');
            for (const gruppe of KATALOG) {
                z.push('', gruppe.gruppe.toUpperCase());
                for (const th of gruppe.themen) {
                    const einzeln = th.kriterien.length === 1 && th.kriterien[0][1] === th.name;
                    if (!einzeln) z.push(`  ${th.name}`);
                    for (const [id, name] of th.kriterien) {
                        const b = (g.bewertung || {})[id] || {};
                        z.push(`  ${einzeln ? '' : '  '}${name.padEnd(einzeln ? 28 : 26)} ${sterne(b.sus)} | ${sterne(b.wichtig)} | ${sterne(b.lp)}`);
                    }
                    const n = (g.notizen || {})[th.id];
                    if (n && n.trim()) n.trim().split('\n').forEach((l) => z.push(`      > ${l}`));
                }
            }
            const u = g.ueben || {};
            z.push('', 'ÜBEN', `  Wie ist es:              ${sterne(u.ist)}`, `  Was nehmen wir uns vor:  ${sterne(u.ziel)}`);
            const ziele = moeglicheZiele({ bewertung: g.bewertung || {} });
            if (ziele.length) {
                z.push('', 'MÖGLICHE ZIELE (wichtig, aber noch nicht so weit)');
                ziele.forEach(({ k, b }) => z.push(`  - ${k.thema.name === k.name ? k.name : k.thema.name + ': ' + k.name} (kann ${b.sus || b.lp || 0}, wichtig ${b.wichtig})`));
            }
            if ((g.handlungen || []).length) {
                z.push('', 'VEREINBARTE HANDLUNGEN');
                g.handlungen.forEach((h, i) => z.push(`  ${i + 1}. ${h.ziel || 'Ziel'}: ${h.massnahme || '–'}${h.bis ? ' (bis ' + h.bis + ')' : ''}`));
            }
            if (g.allgemein && g.allgemein.trim()) z.push('', 'NOTIZEN', ...g.allgemein.trim().split('\n').map((l) => '  ' + l));
            z.push('');
        }
        return z.join('\n');
    }

    // Jahres-Dashboard als Text
    function jahrText(mappe, sj) {
        const k = kennzahlen(mappe, sj || gewaehltesJahr || schuljahrVon(new Date()));
        const MONATE = ['Aug', 'Sep', 'Okt', 'Nov', 'Dez', 'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul'];
        const z = [`SCHULJAHR ${k.schuljahr} IM ÜBERBLICK`, '-'.repeat(`SCHULJAHR ${k.schuljahr} IM ÜBERBLICK`.length)];
        z.push(`${k.sessions} Übesessions, ${dauer(k.uebezeit)} geübt, in ${k.wochenMitUeben} Wochen` +
            (k.wochenMitUeben ? ` (Ø ${dauer(k.uebezeit / k.wochenMitUeben)} pro Übewoche)` : ''));
        z.push('Übezeit pro Monat: ' + k.monate.map((s, i) => `${MONATE[i]} ${Math.round(s / 60)}'`).join(' · '));
        if (k.themen.length) z.push('Am meisten geübt: ' + k.themen.map(([n, s]) => `${n} (${dauer(s)})`).join(', '));
        if (k.hatWuerfel) z.push(`Akkorde gewusst: ${k.akkordeGewusst}/19` + (k.akkordeNeu.length ? ` · neu gelernt: ${k.akkordeNeu.join(', ')}` : ''));
        z.push('');
        return z.join('\n');
    }

    return { jahrZeigen, zeigen, text, jahrText, schuljahrVon, KATALOG };
})();
