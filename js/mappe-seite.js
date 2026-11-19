'use strict';

// =============================================================================
// Übersicht einer Übemappe (Seite mappe.html)
// =============================================================================
// Liest eine Übemappe-Datei (Format: MAPPE.md in Übe-Timer und Würfel, Code: mappe.js)
// und zeigt Übe-Journal (Teil "uebetimer") und Lernstand (Teil "wuerfel").
// Der Übeplan lässt sich bearbeiten und in die Mappe zurückschreiben.
// Alles passiert nur im Browser; die Mappe wird hier absichtlich NICHT gemerkt
// (gemeinsam genutzte Geräte, z. B. das Unterrichts-iPad).

document.addEventListener('DOMContentLoaded', () => {
    const $ = (sel) => document.querySelector(sel);
    const el = (tag, cls, text) => {
        const e = document.createElement(tag);
        if (cls) e.className = cls;
        if (text !== undefined) e.textContent = text;
        return e;
    };

    // Akkorde der 1. Lage in der Reihenfolge des Würfels (akkorde.js)
    const AKKORDE = ['C', 'A', 'G', 'E', 'F', 'D', 'Am', 'Em', 'Dm', 'C7', 'A7', 'G7', 'E7', 'D7', 'B7', 'Am7', 'Em7', 'Dm7', 'Bm7'];
    const TOOL_NAMEN = { uebetimer: 'Übe-Timer', wuerfel: 'Würfel' };

    let mappe = null;

    // ---------- Zeit und Datum ----------
    function dauer(sec) {
        sec = Math.max(0, Math.round(sec || 0));
        const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
        if (h) return `${h} h ${String(m).padStart(2, '0')} min`;
        if (m) return s ? `${m} min ${s} s` : `${m} min`;
        return `${s} s`;
    }
    const tag = (d) => new Date(d).toLocaleDateString('de-CH', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
    const tagKurz = (d) => new Date(d).toLocaleDateString('de-CH', { day: 'numeric', month: 'numeric' });
    const uhr = (d) => new Date(d).toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit' });
    // Montag 00:00 der Woche eines Datums
    function wochenAnfang(d) {
        const x = new Date(d);
        x.setHours(0, 0, 0, 0);
        x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
        return x;
    }

    // ---------- Übe-Timer ----------
    function timerZeigen(t) {
        const journal = Array.isArray(t && t.journal) ? t.journal.filter((e) => e && e.start) : [];
        $('#blockTimer').hidden = false;
        const geuebt = (e) => (e.uebungen || []).reduce((s, u) => s + (u.geuebt || 0), 0);
        const total = journal.reduce((s, e) => s + geuebt(e), 0);
        const vor7 = Date.now() - 7 * 864e5;
        const woche = journal.filter((e) => new Date(e.start) >= vor7).reduce((s, e) => s + geuebt(e), 0);

        const zahlen = $('#timerZahlen');
        zahlen.textContent = '';
        [
            [journal.length, journal.length === 1 ? 'Übesession' : 'Übesessions'],
            [dauer(total), 'geübt insgesamt'],
            [dauer(woche), 'in den letzten 7 Tagen'],
            [journal.length ? dauer(total / journal.length) : '–', 'pro Session'],
        ].forEach(([wert, text]) => {
            const d = el('div', 'mappe-zahl');
            d.append(el('b', '', String(wert)), el('span', '', text));
            zahlen.append(d);
        });

        // Übezeit pro Woche, die letzten 8 Wochen
        const wochen = $('#timerWochen');
        wochen.textContent = '';
        const jetzt = wochenAnfang(new Date());
        const summen = [];
        for (let i = 7; i >= 0; i--) {
            const von = new Date(jetzt); von.setDate(von.getDate() - 7 * i);
            const bis = new Date(von); bis.setDate(bis.getDate() + 7);
            summen.push({ von, sec: journal.filter((e) => { const d = new Date(e.start); return d >= von && d < bis; }).reduce((s, e) => s + geuebt(e), 0) });
        }
        const max = Math.max(1, ...summen.map((w) => w.sec));
        for (const w of summen) {
            const spalte = el('div', 'mappe-woche');
            spalte.title = `Woche ab ${tag(w.von)}: ${dauer(w.sec)}`;
            const balken = el('i');
            balken.style.height = Math.round((w.sec / max) * 100) + '%';
            spalte.append(el('span', 'wert', w.sec ? Math.round(w.sec / 60) + "'" : ''), el('div', 'saeule'), el('span', 'datum', tagKurz(w.von)));
            spalte.querySelector('.saeule').append(balken);
            wochen.append(spalte);
        }

        // Sessions, neueste zuerst
        const box = $('#timerSessions');
        box.textContent = '';
        if (!journal.length) {
            box.append(el('p', 'mappe-hinweis', 'Noch keine Übesessions in dieser Mappe.'));
            return;
        }
        for (const e of journal.slice().reverse()) {
            const sec = el('article', 'mappe-session');
            const planned = (e.uebungen || []).reduce((s, u) => s + (u.geplant || 0), 0);
            sec.append(el('h4', '', `${tag(e.start)}, ${uhr(e.start)}${e.ende ? '–' + uhr(e.ende) : ''}`));
            sec.append(el('p', 'mappe-info', `geübt ${dauer(geuebt(e))} von ${dauer(planned)}`));
            const ol = el('ol', 'mappe-uebungen');
            for (const u of e.uebungen || []) {
                const li = el('li');
                const zeile = el('div', 'zeile');
                zeile.append(el('span', 'thema', u.thema || 'Ohne Thema'),
                    el('span', 'zeit', `${dauer(u.geuebt)} / ${dauer(u.geplant)}`),
                    el('span', 'status' + (u.status === 'erledigt' ? ' ok' : ''), u.status || ''));
                li.append(zeile);
                if (u.notiz) li.append(el('p', 'notiz', u.notiz));
                ol.append(li);
            }
            sec.append(ol);
            if (e.notizen) sec.append(el('p', 'notiz allgemein', e.notizen));
            box.append(sec);
        }
    }

    // ---------- Würfel ----------
    function wuerfelZeigen(t) {
        const lern = (t && t.lernstand) || {};
        const verlauf = Array.isArray(t && t.verlauf) ? t.verlauf : [];
        $('#blockWuerfel').hidden = false;
        let gewusst = 0, geuebt = 0;
        AKKORDE.forEach((n) => { const e = lern[n]; if (e) { geuebt++; if (e.zuletzt === 'ja') gewusst++; } });

        const zahlen = $('#wuerfelZahlen');
        zahlen.textContent = '';
        [
            [`${gewusst} / ${AKKORDE.length}`, 'zuletzt gewusst'],
            [geuebt, 'Akkorde geübt'],
            [verlauf.length, 'Antworten im Verlauf'],
            [verlauf.length ? new Date(verlauf[verlauf.length - 1].zeit).toLocaleDateString('de-CH') : '–', 'zuletzt geübt'],
        ].forEach(([wert, text]) => {
            const d = el('div', 'mappe-zahl');
            d.append(el('b', '', String(wert)), el('span', '', text));
            zahlen.append(d);
        });

        const raster = $('#wuerfelAkkorde');
        raster.textContent = '';
        for (const n of AKKORDE) {
            const e = lern[n];
            const k = el('div', 'mappe-akkord' + (e ? (e.zuletzt === 'ja' ? ' ja' : ' nein') : ''));
            k.append(el('b', '', n), el('span', 'marke', e ? (e.zuletzt === 'ja' ? '✓' : '✗') : '·'),
                el('span', 'zaehler', e ? `${e.ja || 0} ✓ · ${e.nein || 0} ✗` : 'nicht geübt'));
            k.title = e ? (e.zuletzt === 'ja' ? 'Zuletzt gewusst' : 'Zuletzt nicht gewusst') : 'Noch nicht geübt';
            raster.append(k);
        }

        const ol = $('#wuerfelVerlauf');
        ol.textContent = '';
        if (!verlauf.length) ol.append(el('li', 'mappe-hinweis', 'Noch keine Antworten.'));
        for (const v of verlauf.slice(-20).reverse()) {
            const li = el('li', v.gewusst ? 'ja' : 'nein');
            li.append(el('span', 'zeit', `${tag(v.zeit)} ${uhr(v.zeit)}`), el('b', '', v.akkord),
                el('span', '', v.gewusst ? '✓ gewusst' : '✗ nicht gewusst'));
            ol.append(li);
        }
    }

    // ---------- Übeplan bearbeiten ----------
    function planZeile(thema, minuten) {
        const li = el('li', 'plan-zeile');
        const t = el('input'); t.type = 'text'; t.className = 'thema'; t.maxLength = 80; t.value = thema || '';
        t.placeholder = 'Thema, z. B. Akkordwechsel C–G'; t.setAttribute('aria-label', 'Thema');
        const m = el('input'); m.type = 'number'; m.className = 'minuten'; m.min = 1; m.max = 600; m.value = minuten || 5;
        m.inputMode = 'numeric'; m.setAttribute('aria-label', 'Minuten');
        const weg = el('button', 'plan-weg', '✕'); weg.type = 'button'; weg.title = 'Übung entfernen';
        weg.addEventListener('click', () => li.remove());
        li.append(t, m, el('span', 'einheit', 'min'), weg);
        return li;
    }
    function planZeigen(t) {
        const ol = $('#planZeilen');
        ol.textContent = '';
        const plan = Array.isArray(t && t.plan) ? t.plan : [];
        if (plan.length) plan.forEach((p) => ol.append(planZeile(p.thema, Math.max(1, Math.round((p.sekunden || 0) / 60)))));
        else ol.append(planZeile('', 5));
        $('#planMeldung').textContent = '';
    }
    $('#planNeu').addEventListener('click', () => {
        const z = planZeile('', 5);
        $('#planZeilen').append(z);
        z.querySelector('.thema').focus();
    });
    $('#planUebernehmen').addEventListener('click', () => {
        if (!mappe) return;
        const plan = [...document.querySelectorAll('#planZeilen .plan-zeile')].map((z) => ({
            thema: z.querySelector('.thema').value.trim() || 'Ohne Thema',
            sekunden: Math.max(1, Math.round(Number(z.querySelector('.minuten').value) || 0)) * 60,
        }));
        const t = Mappe.teil(mappe, 'uebetimer', () => ({ version: 1, plan: [], journal: [] }));
        if (!Array.isArray(t.journal)) t.journal = [];
        t.plan = plan;
        const summe = plan.reduce((s, p) => s + p.sekunden, 0);
        $('#planMeldung').textContent = `Übernommen: ${plan.length} ${plan.length === 1 ? 'Übung' : 'Übungen'}, ${dauer(summe)}. Jetzt die Mappe teilen oder speichern.`;
        timerZeigen(t);
    });

    // ---------- Mappe öffnen, anzeigen, weitergeben ----------
    function titelZeigen() {
        $('#mappeTitel').textContent = mappe.name ? `Übemappe von ${mappe.name}` : 'Übemappe';
    }
    function anzeigen() {
        $('#mappeInhalt').hidden = false;
        titelZeigen();
        $('#mappeName').value = mappe.name || '';
        const teile = Object.keys(mappe.tools).map((k) => TOOL_NAMEN[k] || k);
        $('#mappeInfo').textContent = `angelegt ${tag(mappe.erstellt)}` +
            (mappe.geaendert ? ` · zuletzt geändert ${tag(mappe.geaendert)}, ${uhr(mappe.geaendert)}` : '') +
            (teile.length ? ` · enthält: ${teile.join(', ')}` : ' · noch leer');
        $('#blockTimer').hidden = true;
        $('#blockWuerfel').hidden = true;
        if (mappe.tools.uebetimer) timerZeigen(mappe.tools.uebetimer);
        if (mappe.tools.wuerfel) wuerfelZeigen(mappe.tools.wuerfel);
        planZeigen(mappe.tools.uebetimer);
        $('#mappeInhalt').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    $('#mappeDatei').addEventListener('change', (e) => {
        const datei = e.target.files[0];
        e.target.value = '';
        if (!datei) return;
        Mappe.oeffnen(datei).then((m) => {
            mappe = m;
            $('#mappeMeldung').textContent = '';
            anzeigen();
        }).catch((err) => { $('#mappeMeldung').textContent = err.message; });
    });

    const teilen = Mappe.kannTeilen();
    const knopf = $('#mappeWeitergeben');
    knopf.textContent = teilen ? '↗ Mappe teilen' : '⬇ Mappe speichern';
    knopf.addEventListener('click', () => {
        if (!mappe) return;
        const gespeichert = () => {
            const alt = knopf.textContent;
            knopf.textContent = 'Gespeichert ✓';
            setTimeout(() => { knopf.textContent = alt; }, 1800);
        };
        // Kann der Browser die Datei doch nicht teilen, wird sie heruntergeladen
        if (teilen) { Mappe.teilen(mappe).then((r) => { if (r === 'heruntergeladen') gespeichert(); }); return; }
        Mappe.herunterladen(mappe);
        gespeichert();
    });

    // ---------- Mappe als Textdatei (lesbar, z. B. für Mail oder Notizen) ----------
    function mappeText() {
        const z = [];
        const strich = (t) => { z.push(t, '='.repeat(t.length), ''); };
        const titel = (t) => { z.push(t, '-'.repeat(t.length)); };
        strich(mappe.name ? `ÜBEMAPPE VON ${mappe.name.toUpperCase()}` : 'ÜBEMAPPE');
        z.push(`Angelegt:  ${tag(mappe.erstellt)}`);
        if (mappe.geaendert) z.push(`Geändert:  ${tag(mappe.geaendert)}, ${uhr(mappe.geaendert)}`);
        z.push(`Erstellt:  ${tag(new Date())}, ${uhr(new Date())} – marcscheidegger.ch/mappe.html`, '');

        const t = mappe.tools.uebetimer;
        const plan = Array.isArray(t && t.plan) ? t.plan : [];
        if (plan.length) {
            titel('ÜBEPLAN');
            plan.forEach((p, i) => z.push(`${i + 1}. ${p.thema} – ${dauer(p.sekunden)}`));
            z.push(`   Total ${dauer(plan.reduce((s, p) => s + (p.sekunden || 0), 0))}`, '');
        }
        if (t) {
            const journal = Array.isArray(t.journal) ? t.journal.filter((e) => e && e.start) : [];
            const geuebt = (e) => (e.uebungen || []).reduce((s, u) => s + (u.geuebt || 0), 0);
            titel('ÜBE-JOURNAL (Übe-Timer)');
            z.push(`${journal.length} ${journal.length === 1 ? 'Übesession' : 'Übesessions'}, geübt ${dauer(journal.reduce((s, e) => s + geuebt(e), 0))}`, '');
            for (const e of journal.slice().reverse()) {
                const geplant = (e.uebungen || []).reduce((s, u) => s + (u.geplant || 0), 0);
                z.push(`${tag(e.start)}, ${uhr(e.start)}${e.ende ? '–' + uhr(e.ende) : ''} · geübt ${dauer(geuebt(e))} von ${dauer(geplant)}`);
                (e.uebungen || []).forEach((u) => {
                    z.push(`  - ${u.thema}: ${dauer(u.geuebt)} von ${dauer(u.geplant)} · ${u.status}`);
                    if (u.notiz) u.notiz.split('\n').forEach((l) => z.push(`      > ${l}`));
                });
                if (e.notizen) e.notizen.split('\n').forEach((l) => z.push(`  Notiz: ${l}`));
                z.push('');
            }
        }
        const w = mappe.tools.wuerfel;
        if (w) {
            const lern = w.lernstand || {};
            const verlauf = Array.isArray(w.verlauf) ? w.verlauf : [];
            const gewusst = AKKORDE.filter((n) => lern[n] && lern[n].zuletzt === 'ja');
            const nicht = AKKORDE.filter((n) => lern[n] && lern[n].zuletzt !== 'ja');
            const offen = AKKORDE.filter((n) => !lern[n]);
            titel('AKKORDE DER 1. LAGE (Würfel)');
            z.push(`Gewusst (${gewusst.length}):        ${gewusst.join(', ') || '–'}`);
            z.push(`Nicht gewusst (${nicht.length}):  ${nicht.join(', ') || '–'}`);
            z.push(`Noch nicht geübt (${offen.length}): ${offen.join(', ') || '–'}`, '');
            const geuebte = AKKORDE.filter((n) => lern[n]);
            if (geuebte.length) {
                z.push('Pro Akkord (gewusst / nicht gewusst):');
                geuebte.forEach((n) => z.push(`  ${n.padEnd(4)} ${lern[n].ja || 0} ✓  ${lern[n].nein || 0} ✗`));
                z.push('');
            }
            if (verlauf.length) {
                z.push('Letzte Antworten:');
                verlauf.slice(-20).reverse().forEach((v) => z.push(`  ${tag(v.zeit)} ${uhr(v.zeit)}  ${v.akkord.padEnd(4)} ${v.gewusst ? '✓ gewusst' : '✗ nicht gewusst'}`));
                z.push('');
            }
        }
        return z.join('\n');
    }
    $('#mappeText').addEventListener('click', () => {
        if (!mappe) return;
        const name = Mappe.dateiname(mappe).replace(/\.json$/, '.txt');
        const blob = new Blob(['\ufeff' + mappeText()], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = name;
        document.body.append(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    });

    // Name ändern (steht nur in der Datei)
    $('#mappeName').addEventListener('input', (e) => {
        if (!mappe) return;
        mappe.name = e.target.value.trim();
        titelZeigen();
    });

    // Neue, leere Mappe – z. B. für eine neue Schülerin mit dem ersten Übeplan
    $('#mappeNeu').addEventListener('click', () => {
        if (mappe && !confirm('Die geöffnete Mappe schliessen und eine neue beginnen? Nicht geteilte Änderungen gehen verloren.')) return;
        mappe = Mappe.neu();
        $('#mappeMeldung').textContent = '';
        anzeigen();
        $('#planMeldung').textContent = 'Neue Mappe: Name eintragen, Übeplan zusammenstellen, «In die Mappe übernehmen» und dann teilen.';
        $('#mappeName').focus({ preventScroll: true });
    });

    $('#mappeDrucken').addEventListener('click', () => window.print());
    $('#mappeSchliessen').addEventListener('click', () => {
        mappe = null;
        $('#mappeInhalt').hidden = true;
        $('#mappeMeldung').textContent = 'Mappe geschlossen.';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
