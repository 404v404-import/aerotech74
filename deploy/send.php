<?php
/**
 * Обработчик заявок с сайта «АэроТех 74».
 * Принимает JSON или обычный POST, проверяет данные и отправляет письмо.
 * Персональные данные не сохраняются на сервере (минимизация по 152-ФЗ).
 *
 * Настройки ниже нужно заполнить перед загрузкой на хостинг.
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

const TO_EMAIL   = 'zakaz@aerotech74.ru';   // куда приходят заявки
const FROM_EMAIL = 'site@aerotech74.ru';    // существующий ящик на домене
const SITE_NAME  = 'АэроТех 74';
const TG_TOKEN   = '';                       // токен бота, если нужен Telegram
const TG_CHAT    = '';                       // chat_id получателя

function respond(bool $ok, string $error = '', int $code = 200): void
{
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

function clean(string $value, int $limit = 200): string
{
    $value = strip_tags($value);
    $value = str_replace(["\r", "\n", "\0"], ' ', $value);
    $value = trim($value);
    if (function_exists('mb_substr')) {
        $value = mb_substr($value, 0, $limit);
    } else {
        $value = substr($value, 0, $limit);
    }
    return $value;
}

function textLength(string $value): int
{
    return function_exists('mb_strlen') ? mb_strlen($value) : strlen($value);
}

function notifyTelegram(string $text): void
{
    if (TG_TOKEN === '' || TG_CHAT === '') {
        return;
    }
    $url = 'https://api.telegram.org/bot' . TG_TOKEN . '/sendMessage';
    $payload = http_build_query([
        'chat_id' => TG_CHAT,
        'text' => $text,
        'parse_mode' => 'HTML',
        'disable_web_page_preview' => 'true',
    ]);
    $context = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => "Content-Type: application/x-www-form-urlencoded\r\n",
            'content' => $payload,
            'timeout' => 5,
        ],
    ]);
    @file_get_contents($url, false, $context);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    respond(false, 'method', 405);
}

$raw = file_get_contents('php://input');
$data = json_decode($raw !== false ? $raw : '', true);
if (!is_array($data)) {
    $data = $_POST;
}

// Honeypot: скрытое поле, которое заполняют только боты
if (!empty($data['company'])) {
    respond(true);
}

$name    = clean((string)($data['name'] ?? ''), 60);
$phone   = (string)($data['phone'] ?? '');
$type    = clean((string)($data['type'] ?? ''), 100);
$comment = clean((string)($data['comment'] ?? ''), 1000);
$consent = !empty($data['consent']);
$page    = clean((string)($_SERVER['HTTP_REFERER'] ?? ''), 300);

$digits = preg_replace('/\D+/', '', $phone);
if (strlen($digits) === 10 && $digits[0] === '9') {
    $digits = '7' . $digits;
} elseif (strlen($digits) === 11 && $digits[0] === '8') {
    $digits = '7' . substr($digits, 1);
}

if (textLength($name) < 2) {
    respond(false, 'name', 422);
}
if (strlen($digits) !== 11) {
    respond(false, 'phone', 422);
}
if (!$consent) {
    respond(false, 'consent', 422);
}

// Простая защита от повторных отправок: не чаще одного раза в 20 секунд с IP
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$throttle = sys_get_temp_dir() . '/aerotech_lead_' . md5($ip);
if (is_file($throttle) && (time() - filemtime($throttle)) < 20) {
    respond(false, 'too_many', 429);
}
@touch($throttle);

$subject = 'Заявка с сайта — ' . ($type !== '' ? $type : 'консультация');

$lines = [
    'Новая заявка с сайта ' . SITE_NAME,
    '',
    'Имя: ' . $name,
    'Телефон: +' . $digits,
    'Что нужно: ' . ($type !== '' ? $type : 'не указано'),
    'Комментарий: ' . ($comment !== '' ? $comment : '—'),
    'Страница: ' . ($page !== '' ? $page : '—'),
    'IP: ' . $ip,
    'Дата: ' . date('d.m.Y H:i'),
];
$body = implode("\n", $lines);

$headers = implode("\r\n", [
    'From: ' . SITE_NAME . ' <' . FROM_EMAIL . '>',
    'Reply-To: ' . FROM_EMAIL,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
$sent = @mail(TO_EMAIL, $encodedSubject, $body, $headers);

$telegramText = "<b>Заявка с сайта</b>\n"
    . 'Имя: ' . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . "\n"
    . 'Телефон: +' . $digits . "\n"
    . 'Что нужно: ' . htmlspecialchars($type !== '' ? $type : 'не указано', ENT_QUOTES, 'UTF-8') . "\n"
    . 'Комментарий: ' . htmlspecialchars($comment !== '' ? $comment : '—', ENT_QUOTES, 'UTF-8');
notifyTelegram($telegramText);

if (!$sent) {
    error_log('Aerotech lead: mail() failed for ' . $digits);
    respond(false, 'mail', 500);
}

respond(true);
