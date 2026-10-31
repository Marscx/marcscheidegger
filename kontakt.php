<?php
// Kontaktformular: schickt die Nachricht per mail() und leitet zurück auf kontakt.html.

const EMPFAENGER = 'marcscheidegger@mac.com';
const ABSENDER   = 'website@marcscheidegger.ch'; // Adresse auf der eigenen Domain, sonst landet die Mail im Spam

function zurueck(string $status): void {
    header('Location: kontakt.html?' . $status . '=1', true, 303);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    zurueck('fehler');
}

// Honeypot: Menschen sehen dieses Feld nicht, Bots füllen es aus
if (!empty($_POST['website'])) {
    zurueck('gesendet');
}

$name      = trim((string)($_POST['name'] ?? ''));
$email     = trim((string)($_POST['email'] ?? ''));
$nachricht = trim((string)($_POST['nachricht'] ?? ''));

// Zeilenumbrüche in Name/E-Mail würden zusätzliche Mail-Header erlauben
$name = str_replace(["\r", "\n"], ' ', $name);

if ($name === '' || $nachricht === ''
    || mb_strlen($name) > 120 || mb_strlen($nachricht) > 5000
    || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    zurueck('fehler');
}

$betreff = '=?UTF-8?B?' . base64_encode('Kontakt über marcscheidegger.ch: ' . $name) . '?=';
$text    = "Name: $name\nE-Mail: $email\n\n$nachricht\n";
$header  = implode("\r\n", [
    'From: marcscheidegger.ch <' . ABSENDER . '>',
    'Reply-To: ' . $email,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

zurueck(mail(EMPFAENGER, $betreff, $text, $header, '-f' . ABSENDER) ? 'gesendet' : 'fehler');
