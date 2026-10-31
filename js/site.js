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

    // kontakt.php leitet mit ?gesendet=1 oder ?fehler=1 zurück
    const params = new URLSearchParams(location.search);
    const show = id => { const el = document.getElementById(id); if (el) el.hidden = false; };
    if (params.has('gesendet')) show('msg-ok');
    if (params.has('fehler')) show('msg-err');
});
