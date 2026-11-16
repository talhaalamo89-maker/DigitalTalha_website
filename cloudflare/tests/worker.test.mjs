import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { DatabaseSync } from 'node:sqlite';

const source = await readFile(new URL('../worker.mjs', import.meta.url), 'utf8');
const routes = ['/', '/about/', '/contact/', '/services/', '/blog/', '/google-ads/', '/meta-ads/', '/seo/', '/website-creation/', '/projects/glisan-akbari-hospital/', '/terms-conditions/', '/404/'];
async function load(preview = false) {
  const code = source.replace('/* BUILD_CONFIG */', `const BUILD_PREVIEW=${preview};const PAGE_ROUTES=new Set(${JSON.stringify(routes)});`);
  return import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
}
const { default: worker, enquiry, redirectTarget } = await load();
const valid = { name: 'Test Visitor', business: 'Migration test', email: 'visitor@example.com', phone: '+91 9999999999', website: 'https://example.com', service: 'SEO', budget: 'Testing', message: 'Synthetic migration test enquiry.', consent: 'yes', company_url: '' };
function request(fields = {}, options = {}) {
  const url = options.url || 'https://digitaltalha.com/api/enquiry.php';
  return new Request(url, { method: 'POST', headers: { Origin: new URL(url).origin, 'CF-Connecting-IP': '192.0.2.10', ...options.headers }, body: new URLSearchParams({ ...valid, ...fields }) });
}
function environment() {
  const db = new DatabaseSync(':memory:');
  db.exec('CREATE TABLE enquiry_limits (key TEXT PRIMARY KEY, expires INTEGER NOT NULL)');
  const binding = { prepare(sql) { return { bind(...args) { return { async run() { return db.prepare(sql).run(...args); }, async first() { return db.prepare(sql).get(...args) || null; } }; } }; } };
  return { RESEND_API_KEY: 'synthetic-test-key', ENQUIRY_TO: 'owner@example.com', ENQUIRY_FROM: 'website@digitaltalha.com', RATE_LIMIT_SECRET: 'synthetic-test-hmac-secret-over-32-characters', ENQUIRY_DB: binding, db };
}
const accepted = async () => Response.json({ id: 'synthetic-receipt' });

test('all WordPress shortlinks retain campaign parameters', () => {
  const ids = { 454: '/about/', 456: '/contact/', 458: '/terms-conditions/', 460: '/privacy-policy/', 484: '/services/', 504: '/blog/', 605: '/google-ads/', 607: '/meta-ads/', 782: '/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/' };
  for (const [id, path] of Object.entries(ids)) for (const key of ['p', 'page_id']) {
    const target = new URL(redirectTarget(`https://digitaltalha.com/?utm_source=a&${key}=${id}&utm_term=x%20y`));
    assert.equal(target.pathname, path);
    assert.equal(target.searchParams.get('utm_source'), 'a');
    assert.equal(target.searchParams.get('utm_term'), 'x y');
    assert.equal(target.searchParams.has(key), false);
  }
  assert.equal(redirectTarget('https://digitaltalha.com/?p=999'), null);
  assert.equal(redirectTarget('https://www.digitaltalha.com/index.html?p=605&utm_source=legacy'), 'https://digitaltalha.com/google-ads/?utm_source=legacy');
});
test('aliases, sitemap, index and slash redirects avoid the real project page', () => {
  for (const [alias, target] of Object.entries({ 'about-me': '/about/', 'contact-me': '/contact/', wordpress: '/seo/', 'site-map': '/sitemap.xml' })) {
    assert.equal(redirectTarget(`https://digitaltalha.com/${alias}/?utm_source=legacy`), `https://digitaltalha.com${target}?utm_source=legacy`);
  }
  for (const [alias, target] of Object.entries({ 'about-us': '/about/', 'contact-us': '/contact/', service: '/services/', projects: '/blog/', resources: '/blog/', 'category/meta-ads': '/blog/', 'category/uncategorized': '/blog/', 'google-ads-services': '/google-ads/', 'terms-and-conditions': '/terms-conditions/' })) {
    for (const suffix of ['', '/', '/index.html']) {
      assert.equal(redirectTarget(`https://digitaltalha.com/${alias}${suffix}?utm_source=test`), `https://digitaltalha.com${target}?utm_source=test`);
    }
  }
  for (const name of ['sitemap_index', 'wp-sitemap', 'post-sitemap', 'page-sitemap', 'category-sitemap']) assert.equal(redirectTarget(`https://digitaltalha.com/${name}.xml`), 'https://digitaltalha.com/sitemap.xml');
  assert.equal(redirectTarget('https://digitaltalha.com/projects/glisan-akbari-hospital/'), null);
  assert.equal(redirectTarget('https://digitaltalha.com/unknown'), null);
  assert.equal(redirectTarget('https://digitaltalha.com/unknown/index.html'), null);
  assert.equal(redirectTarget('https://digitaltalha.com/about'), 'https://digitaltalha.com/about/');
  assert.equal(redirectTarget('https://digitaltalha.com/about/index.html?a=1'), 'https://digitaltalha.com/about/?a=1');
  assert.equal(redirectTarget('http://www.digitaltalha.com/about/?a=1'), 'https://digitaltalha.com/about/?a=1');
  assert.equal(redirectTarget('https://www.digitaltalha.com/about-us/index.html?a=1'), 'https://digitaltalha.com/about/?a=1');
  assert.equal(redirectTarget('https://digitaltalha.com/404.html'), 'https://digitaltalha.com/404/');
});
test('methods, origins, content types, size and malformed form rejected before sending', async () => {
  let sends = 0; const send = async () => { sends++; return accepted(); };
  const cases = [
    [new Request('https://digitaltalha.com/api/enquiry.php'), 405],
    [request({}, { headers: { Origin: 'https://evil.example' } }), 403],
    [request({}, { headers: { Origin: 'null' } }), 403],
    [request({}, { headers: { 'Sec-Fetch-Site': 'cross-site' } }), 403],
    [request({}, { headers: { 'Content-Type': 'application/json' } }), 415],
    [request({}, { headers: { 'Content-Length': '24001' } }), 413],
    [request({ message: 'x'.repeat(25000) }), 413],
    [request({}, { headers: { 'Content-Type': 'multipart/form-data; boundary=invalid' } }), 400],
  ];
  for (const [req, status] of cases) assert.equal((await enquiry(req, environment(), send)).status, status);
  assert.equal(sends, 0);
});
test('required fields, consent, honeypot, service, header injection and URLs rejected', async () => {
  const cases = [{name:''}, {business:''}, {email:'bad'}, {email:'x@example.com\r\nBcc: spam@example.com'}, {service:'unknown'}, {consent:''}, {message:'short'}, {phone:'not a phone'}, {website:'javascript:alert(1)'}, {website:'https://'}, {company_url:'spam'}, {name:'x'.repeat(401)}];
  for (const fields of cases) {
    const response = await enquiry(request(fields), environment(), () => { throw new Error('Must not send'); });
    assert.equal(response.status, fields.company_url ? 400 : 422, JSON.stringify(fields));
  }
  const duplicate = new URLSearchParams(valid); duplicate.append('email', 'another@example.com');
  const req = new Request('https://digitaltalha.com/api/enquiry.php', {method:'POST',headers:{Origin:'https://digitaltalha.com'},body:duplicate});
  assert.equal((await enquiry(req, environment())).status, 422);
});
test('accepted provider response alone enables success; outgoing payload uses configured recipient', async () => {
  const env = environment(); let payload;
  const response = await enquiry(request(), env, async (url, init) => {
    assert.equal(url, 'https://api.resend.com/emails'); payload = JSON.parse(init.body); return accepted();
  });
  assert.equal(response.status, 200); assert.equal((await response.json()).ok, true);
  assert.deepEqual(payload.to, ['owner@example.com']); assert.equal(payload.reply_to, valid.email);
  assert.match(payload.text, /Consent to contact: Yes/); assert.match(payload.text, /Project budget/);
  const row = env.db.prepare('SELECT * FROM enquiry_limits').get();
  assert.match(row.key, /^[a-f0-9]{64}$/); assert.equal(JSON.stringify(row).includes('192.0.2.10'), false);
});
test('provider failure, timeout, malformed response and absent configuration never report success', async () => {
  for (const send of [async () => new Response('', {status:500}), async () => {throw new Error('timeout');}, async () => Response.json({}), async () => new Response('invalid')]) {
    const response = await enquiry(request(), environment(), send); assert.equal(response.status,503); assert.equal((await response.json()).ok,false);
  }
  for (const key of ['RESEND_API_KEY','ENQUIRY_TO','ENQUIRY_FROM','RATE_LIMIT_SECRET','ENQUIRY_DB']) {
    const env=environment(); delete env[key]; assert.equal((await enquiry(request(),env)).status,503);
  }
});
test('atomic SQLite claim permits one concurrent send, then retries after expiry', async () => {
  const env=environment(); let sends=0;
  const send=async()=>{sends++;return accepted();};
  const responses=await Promise.all([enquiry(request(),env,send),enquiry(request(),env,send)]);
  assert.deepEqual(responses.map(r=>r.status).sort(),[200,429]);assert.equal(sends,1);
  env.db.prepare('UPDATE enquiry_limits SET expires=0').run();
  assert.equal((await enquiry(request(),env,send)).status,200);
});
test('previews default to no sends and require one exact authorised test hostname', async () => {
  const env=environment(); const url='https://test.digitaltalha-migration.pages.dev/api/enquiry.php';
  assert.equal((await enquiry(request({}, {url}),env,accepted)).status,503);
  env.ENQUIRY_PREVIEW_HOST='test.digitaltalha-migration.pages.dev';
  assert.equal((await enquiry(request({}, {url}),env,accepted)).status,200);
  assert.equal((await enquiry(request({}, {url:'https://another.pages.dev/api/enquiry.php'}),env,accepted)).status,503);
});
test('preview has noindex and empty sitemap; production keeps indexing and true unknown 404', async () => {
  const env={ASSETS:{fetch: async()=>new Response('Page not found',{status:404})}};
  for (const host of ['digitaltalha-migration.pages.dev','branch.digitaltalha-migration.pages.dev']) {
    const response=await worker.fetch(new Request(`https://${host}/unknown/`),env);
    assert.equal(response.status,404);assert.equal(response.headers.get('X-Robots-Tag'),'noindex, follow');
    const sitemap=await worker.fetch(new Request(`https://${host}/sitemap.xml`),env);assert.equal((await sitemap.text()).includes('<loc>'),false);
  }
  const response=await worker.fetch(new Request('https://digitaltalha.com/unknown/'),env);
  assert.equal(response.status,404);assert.equal(response.headers.get('X-Robots-Tag'),null);assert.equal(response.headers.get('X-Content-Type-Options'),'nosniff');
  const errorPage = { ASSETS: { fetch: async () => new Response('<h1>Page not found</h1>', { headers: { 'Content-Type': 'text/html' } }) } };
  const directError = await worker.fetch(new Request('https://digitaltalha.com/404/'), errorPage);
  assert.equal(directError.status, 404);
  assert.equal(await directError.text(), '<h1>Page not found</h1>');
  const headError = await worker.fetch(new Request('https://digitaltalha.com/404/', { method: 'HEAD' }), errorPage);
  assert.equal(headError.status, 404);
  assert.equal(await headError.text(), '');
  const preview=await load(true);
  assert.equal((await preview.default.fetch(new Request('https://digitaltalha.com/'),env)).status,503);
});
test('API requests also use the canonical production origin', async () => {
  const response=await worker.fetch(new Request('http://www.digitaltalha.com/api/enquiry.php?test=1'),{});
  assert.equal(response.status,301);
  assert.equal(response.headers.get('Location'),'https://digitaltalha.com/api/enquiry.php?test=1');
});
