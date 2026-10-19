<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function respond(int $code, bool $ok, string $message): never {
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'message' => $message]);
    exit;
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    respond(405, false, 'Please use the enquiry form.');
}
if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 24000) respond(413, false, 'Your enquiry is too long.');
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
$expectedHost = strtolower(explode(':', $_SERVER['HTTP_HOST'] ?? '')[0]);
$originHost = strtolower((string)parse_url($origin, PHP_URL_HOST));
if ($origin !== '' && ($originHost === '' || $originHost !== $expectedHost)) respond(403, false, 'Please send your enquiry from this website.');
if (($_POST['company_url'] ?? '') !== '') respond(400, false, 'Your enquiry could not be sent.');

function field(string $name, int $max): string {
    $value = $_POST[$name] ?? '';
    if (!is_string($value) || strlen($value) > $max) respond(422, false, 'Please check your details and try again.');
    return trim(str_replace("\0", '', $value));
}
$name = field('name', 400);
$business = field('business', 600);
$email = field('email', 250);
$phone = field('phone', 30);
$website = field('website', 1000);
$service = field('service', 100);
$budget = field('budget', 150);
$message = field('message', 15000);
if ($name === '' || $business === '' || strlen($message) < 10 || !filter_var($email, FILTER_VALIDATE_EMAIL)) respond(422, false, 'Please enter your name, business, valid email, and a short message.');
if (!in_array($service, ['Google Ads','Meta Ads','Website Creation','Not sure yet'], true)) respond(422, false, 'Please choose a service.');
if (($_POST['consent'] ?? '') !== 'yes') respond(422, false, 'Please agree to the Privacy Policy so I can contact you.');
if ($phone !== '' && !preg_match('/^[+0-9() .-]{7,25}$/', $phone)) respond(422, false, 'Please check your phone number.');
if ($website !== '' && (!filter_var($website, FILTER_VALIDATE_URL) || !in_array(strtolower((string)parse_url($website,PHP_URL_SCHEME)),['http','https'],true))) respond(422, false, 'Please enter a valid website address.');
if (preg_match('/[\r\n]/', $email)) respond(422, false, 'Please check your email address.');

// Keep the rate-limit files outside the public document root. No enquiry content is stored.
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rateFile = sys_get_temp_dir() . '/digitaltalha-rate-' . hash('sha256', $ip);
$rateHandle = @fopen($rateFile, 'c+');
if (!$rateHandle || !flock($rateHandle, LOCK_EX)) respond(503, false, 'Enquiry delivery is temporarily unavailable. Please use WhatsApp or email.');
$last = (int)stream_get_contents($rateHandle);
if ($last > time() - 60) { flock($rateHandle, LOCK_UN); fclose($rateHandle); respond(429, false, 'Please wait a minute before sending another enquiry.'); }

$recipient = 'talhaalamo89@gmail.com';
$subject = 'DigitalTalha website enquiry: ' . $service;
$budgetLabel = $service === 'Website Creation' ? 'Project budget' : 'Monthly ad budget';
$body = "New website enquiry\n\nName: $name\nBusiness: $business\nEmail: $email\nPhone: $phone\nWebsite: $website\nService: $service\n$budgetLabel: $budget\n\nMessage:\n$message\n\nConsent to contact: Yes\n";
$headers = ['From' => 'DigitalTalha Website <website@digitaltalha.com>', 'Reply-To' => $email, 'Content-Type' => 'text/plain; charset=UTF-8', 'MIME-Version' => '1.0'];
if (!function_exists('mail')) { flock($rateHandle, LOCK_UN); fclose($rateHandle); respond(503, false, 'Please contact me directly by WhatsApp or email.'); }
$sent = @mail($recipient, $subject, $body, $headers);
if ($sent) { rewind($rateHandle); ftruncate($rateHandle, 0); fwrite($rateHandle, (string)time()); fflush($rateHandle); }
flock($rateHandle, LOCK_UN); fclose($rateHandle);
if (!$sent) respond(503, false, 'Your enquiry could not be sent. Please use WhatsApp or email.');
respond(200, true, 'Your enquiry was accepted for delivery.');
