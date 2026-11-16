/* BUILD_CONFIG */

const APEX = 'digitaltalha.com';
const UNAVAILABLE = 'The enquiry form is temporarily unavailable. Please try again later.';
const SECURITY = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'X-Frame-Options': 'SAMEORIGIN',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
};
const ALIASES = {
  '/about-us/': '/about/', '/contact-us/': '/contact/', '/service/': '/services/',
  '/projects/': '/blog/', '/resources/': '/blog/',
  '/category/meta-ads/': '/blog/', '/category/uncategorized/': '/blog/',
  '/about-me/': '/about/', '/contact-me/': '/contact/',
  '/wordpress/': '/seo/', '/site-map/': '/sitemap.xml',
  '/google-ads-services/': '/google-ads/', '/terms-and-conditions/': '/terms-conditions/',
};
const SHORTLINKS = {
  454: '/about/', 456: '/contact/', 458: '/terms-conditions/', 460: '/privacy-policy/',
  484: '/services/', 504: '/blog/', 605: '/google-ads/', 607: '/meta-ads/',
  782: '/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/',
};
const SERVICES = ['Google Ads', 'Meta Ads', 'Website Creation', 'SEO', 'Not sure yet'];

function json(status, ok, message, headers = {}) {
  return Response.json({ ok, message }, { status, headers: { 'Cache-Control': 'no-store', ...headers } });
}

export function redirectTarget(url) {
  const next = new URL(url);
  const original = next.href;
  if (next.hostname === 'www.' + APEX || (next.hostname === APEX && next.protocol !== 'https:')) {
    next.hostname = APEX;
    next.protocol = 'https:';
    next.port = '';
  }
  const path = next.pathname.replace(/\/index\.html$/, '/');
  if (path === '/') {
    for (const [key, value] of next.searchParams) {
      if ((key === 'p' || key === 'page_id') && Object.hasOwn(SHORTLINKS, value)) {
        next.pathname = SHORTLINKS[value];
        next.searchParams.delete(key, value);
        return next.href;
      }
    }
  }
  const slashPath = path.endsWith('/') ? path : path + '/';
  if (Object.hasOwn(ALIASES, slashPath)) next.pathname = ALIASES[slashPath];
  else if (/^\/(sitemap_index|wp-sitemap|post-sitemap|page-sitemap|category-sitemap)\.xml$/.test(path)) next.pathname = '/sitemap.xml';
  else if (path === '/404.html') next.pathname = '/404/';
  else if (PAGE_ROUTES.has(slashPath)) next.pathname = slashPath;
  return next.href === original ? null : next.href;
}

async function limitedBody(request) {
  if (Number(request.headers.get('Content-Length')) > 24000) throw new RangeError();
  const reader = request.body?.getReader();
  if (!reader) return new Uint8Array();
  const chunks = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 24000) { await reader.cancel(); throw new RangeError(); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return bytes;
}

const emailValid = value => value.length <= 250 && /^[A-Za-z0-9.!#$%&'*+\/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$/.test(value) && !/[\r\n]/.test(value);

export async function enquiry(request, env, send = fetch) {
  if (request.method !== 'POST') return json(405, false, 'Please use the enquiry form.', { Allow: 'POST' });
  const url = new URL(request.url);
  // Browser submissions must be same-origin; no cross-site or missing-origin sends.
  if (request.headers.get('Origin') !== url.origin || request.headers.get('Sec-Fetch-Site') === 'cross-site') {
    return json(403, false, 'Please send your enquiry from this website.');
  }
  const contentType = request.headers.get('Content-Type') || '';
  if (!/^(multipart\/form-data|application\/x-www-form-urlencoded)(?:;|$)/i.test(contentType)) {
    return json(415, false, 'Please use the enquiry form.');
  }
  let form;
  try {
    const body = await limitedBody(request);
    form = await new Response(body, { headers: { 'Content-Type': contentType } }).formData();
  } catch (error) {
    return json(error instanceof RangeError ? 413 : 400, false, 'Please check your details and try again.');
  }
  const data = {};
  const limits = { name: 400, business: 600, email: 250, phone: 30, website: 1000, service: 100, budget: 150, message: 15000, consent: 10, company_url: 1000 };
  for (const [key, max] of Object.entries(limits)) {
    const values = form.getAll(key);
    const value = values[0] ?? '';
    if (values.length > 1 || typeof value !== 'string' || new TextEncoder().encode(value).length > max) {
      return json(422, false, 'Please check your details and try again.');
    }
    data[key] = value.replaceAll('\0', '').trim();
  }
  if (data.company_url) return json(400, false, 'Your enquiry could not be sent.');
  if (!data.name || !data.business || data.message.length < 10 || !emailValid(data.email)) {
    return json(422, false, 'Please enter your name, business, valid email, and a short message.');
  }
  if (!SERVICES.includes(data.service)) return json(422, false, 'Please choose a service.');
  if (data.consent !== 'yes') return json(422, false, 'Please agree to the Privacy Policy so I can contact you.');
  if (data.phone && !/^[+0-9() .-]{7,25}$/.test(data.phone)) return json(422, false, 'Please check your phone number.');
  if (data.website) {
    try { if (!['http:', 'https:'].includes(new URL(data.website).protocol)) throw new Error(); }
    catch { return json(422, false, 'Please enter a valid website address.'); }
  }
  const production = url.hostname === APEX && !BUILD_PREVIEW;
  const testHost = env.ENQUIRY_PREVIEW_HOST;
  const previewAllowed = testHost && url.hostname === testHost && testHost.endsWith('.pages.dev');
  if ((!production && !previewAllowed) || !env.RESEND_API_KEY || !emailValid(env.ENQUIRY_TO || '') ||
      !emailValid(env.ENQUIRY_FROM || '') || !env.ENQUIRY_DB || (env.RATE_LIMIT_SECRET || '').length < 32) {
    return json(503, false, UNAVAILABLE);
  }
  try {
    const ip = request.headers.get('CF-Connecting-IP');
    if (!ip) return json(503, false, UNAVAILABLE);
    const encoder = new TextEncoder();
    const secret = await crypto.subtle.importKey('raw', encoder.encode(env.RATE_LIMIT_SECRET), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const digest = await crypto.subtle.sign('HMAC', secret, encoder.encode(ip));
    const key = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
    const now = Math.floor(Date.now() / 1000);
    await env.ENQUIRY_DB.prepare('DELETE FROM enquiry_limits WHERE expires < ?').bind(now - 86400).run();
    // One atomic claim prevents parallel requests at different edge locations.
    const claim = await env.ENQUIRY_DB.prepare(`INSERT INTO enquiry_limits (key, expires) VALUES (?, ?)
      ON CONFLICT(key) DO UPDATE SET expires=excluded.expires WHERE enquiry_limits.expires <= ? RETURNING expires`)
      .bind(key, now + 60, now).first();
    if (!claim) return json(429, false, 'Please wait a minute before sending another enquiry.', { 'Retry-After': '60' });
    const budgetLabel = ['Website Creation', 'SEO'].includes(data.service) ? 'Project budget' : 'Monthly ad budget';
    const text = `New website enquiry\n\nName: ${data.name}\nBusiness: ${data.business}\nEmail: ${data.email}\nPhone: ${data.phone}\nWebsite: ${data.website}\nService: ${data.service}\n${budgetLabel}: ${data.budget}\n\nMessage:\n${data.message}\n\nConsent to contact: Yes\n`;
    const response = await send('https://api.resend.com/emails', {
      method: 'POST', signal: AbortSignal.timeout(10000),
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: `DigitalTalha Website <${env.ENQUIRY_FROM}>`, to: [env.ENQUIRY_TO], reply_to: data.email,
        subject: `${production ? '' : '[PREVIEW TEST] '}DigitalTalha website enquiry: ${data.service}`, text }),
    });
    if (!response.ok) return json(503, false, UNAVAILABLE);
    const receipt = await response.json();
    if (!receipt.id || typeof receipt.id !== 'string') return json(503, false, UNAVAILABLE);
    return json(200, true, 'Your enquiry was accepted for delivery.');
  } catch { return json(503, false, UNAVAILABLE); }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isPublicHost = url.hostname === APEX || url.hostname === 'www.' + APEX;
    const noindex = !isPublicHost || BUILD_PREVIEW;
    let response;
    if (BUILD_PREVIEW && isPublicHost) response = new Response('Preview build: production deployment is disabled.', { status: 503 });
    else if (isPublicHost && (url.hostname !== APEX || url.protocol !== 'https:')) {
      response = new Response(null, { status: 301, headers: { Location: redirectTarget(url) } });
    }
    else if (url.pathname === '/api/enquiry.php') response = await enquiry(request, env);
    else if (!['GET', 'HEAD'].includes(request.method)) response = json(405, false, 'Method not allowed.', { Allow: 'GET, HEAD' });
    else {
      const target = redirectTarget(url);
      if (target) response = new Response(null, { status: 301, headers: { Location: target } });
      else if (noindex && url.pathname === '/sitemap.xml') response = new Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>', { headers: { 'Content-Type': 'application/xml' } });
      else response = await env.ASSETS.fetch(request);
    }
    const headers = new Headers(response.headers);
    for (const [key, value] of Object.entries(SECURITY)) headers.set(key, value);
    if (noindex || url.pathname === '/DigitalTalha-preview.html') headers.set('X-Robots-Tag', 'noindex, follow');
    const status = url.pathname === '/404/' && response.ok ? 404 : response.status;
    return new Response(request.method === 'HEAD' ? null : response.body, {
      status, statusText: status === response.status ? response.statusText : 'Not Found', headers,
    });
  },
};
