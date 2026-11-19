import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { setTimeout as delay } from 'node:timers/promises';

const origin = 'https://digitaltalha.com';
const release = 'f08cb408d38f36655110b9a0a0da9e94d27b4db5';
const routes = new Set([
  '/', '/about/', '/services/', '/website-creation/', '/google-ads/', '/meta-ads/', '/seo/',
  '/projects/', '/blog/', '/projects/glisan-akbari-hospital/', '/contact/', '/privacy-policy/',
  '/terms-conditions/', '/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/'
]);
const get = async (route, options = {}) => fetch(origin + route, {
  headers: { 'cache-control': 'no-cache' }, signal: AbortSignal.timeout(8000), ...options
});

try {
  const workflowURL = 'https://api.github.com/repos/talhaalamo89-maker/DigitalTalha_website/actions/runs?branch=main&head_sha=' + release;
  const response = await fetch(workflowURL, { signal: AbortSignal.timeout(8000) });
  if (response.ok) {
    const { workflow_runs } = await response.json();
    for (const run of workflow_runs ?? []) {
      console.log('Production workflow: ' + run.html_url + ' ' + run.status + ' ' + (run.conclusion ?? ''));
    }
  }
} catch {
  // The published site is checked independently.
}

let homepage;
for (let attempt = 1; attempt <= 8; attempt++) {
  try {
    const response = await get('/?release=' + release.slice(0, 8));
    const body = await response.text();
    if (response.ok && body.includes('Book a free consultation') && body.includes('id="selected-work"')) {
      homepage = body;
      break;
    }
  } catch {
    // Allow for deployment propagation and transient connection failures.
  }
  if (attempt < 8) await delay(4000);
}
assert(homepage, 'The redesigned homepage has not appeared on the public domain.');
assert(homepage.indexOf('id="selected-work"') < homepage.indexOf('id="services"'));
assert(homepage.includes('Glisan Akbari'));
const css = await get('/assets/site.css?release=' + release.slice(0, 8));
assert(css.ok);
assert.equal(await css.text(), readFileSync(new URL('../assets/site.css', import.meta.url), 'utf8'),
  'Public CSS should match the tested release.');
console.log('PASS: the redesigned homepage, featured hospital project and exact stylesheet are live.');

const sitemap = await get('/sitemap.xml');
assert(sitemap.ok, 'Production sitemap status');
const entries = [...(await sitemap.text()).matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
assert.equal(entries.length, routes.size);
assert.deepEqual(new Set(entries), new Set([...routes].map(route => origin + route)));
await Promise.all([...routes].map(async route => {
  const response = await get(route);
  const html = await response.text();
  assert(response.ok, 'Public page failed: ' + route);
  assert(html.includes('<link rel="canonical" href="' + origin + route + '">'), 'Canonical mismatch: ' + route);
  assert(!/noindex/i.test(response.headers.get('x-robots-tag') ?? ''), 'Production header noindex: ' + route);
  assert(!/<meta name="robots" content="[^"]*noindex/i.test(html), 'Production HTML noindex: ' + route);
  if (['/google-ads/', '/meta-ads/', '/website-creation/', '/seo/'].includes(route)) {
    assert(html.includes('in India | DigitalTalha</title>'), 'New service title: ' + route);
  }
  if (route === '/blog/') assert(html.includes('Digital marketing blog'), 'Dedicated blog listing');
  if (route === '/contact/') {
    assert(html.includes('action="/api/enquiry.php"') && html.includes('Send enquiry'), 'Public enquiry form');
  }
}));
const oldSitemap = await get('/sitemap_index.xml', { redirect: 'manual' });
assert([301, 308].includes(oldSitemap.status), 'Legacy sitemap redirect status');
assert.equal(new URL(oldSitemap.headers.get('location'), origin).pathname, '/sitemap.xml');
const enquiry = await get('/api/enquiry.php');
assert.equal(enquiry.status, 405);
assert.equal(enquiry.headers.get('allow'), 'POST');
assert.equal((await enquiry.json()).ok, false);
console.log('PASS: all 14 live pages, titles, canonical URLs, sitemap, legacy redirect, blog and enquiry routing.');
