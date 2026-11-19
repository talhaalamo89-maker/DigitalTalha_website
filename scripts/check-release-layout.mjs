import assert from 'node:assert/strict';
import { execFileSync, spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const dependencyDir = mkdtempSync(join(tmpdir(), 'digitaltalha-chrome-'));
const preview = 'http://127.0.0.1:4173';
const routes = [
  '/', '/services/', '/google-ads/', '/meta-ads/', '/website-creation/', '/seo/',
  '/projects/', '/projects/glisan-akbari-hospital/', '/blog/', '/about/', '/contact/'
];
let server;
let browser;

async function waitForPreview() {
  for (let attempt = 0; attempt < 40; attempt++) {
    if (server.exitCode !== null) throw new Error('The preview server exited.');
    try {
      if ((await fetch(preview)).ok) return;
    } catch {
      // The port opens shortly after the server process starts.
    }
    await delay(250);
  }
  throw new Error('The preview server did not respond.');
}

try {
  execFileSync('npm', ['install', '--prefix', dependencyDir, '--ignore-scripts', '--no-audit',
    '--no-fund', 'playwright-core@1.56.1'], { stdio: 'inherit', timeout: 90000 });
  const entry = join(dependencyDir, 'node_modules', 'playwright-core', 'index.mjs');
  const { chromium } = await import(pathToFileURL(entry).href);
  server = spawn('python3', ['scripts/serve.py'], {
    cwd: root, env: { ...process.env, PORT: '4173' }, stdio: ['ignore', 'ignore', 'inherit']
  });
  await waitForPreview();
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  for (const width of [320, 390, 430, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 850 }, reducedMotion: 'reduce' });
    page.setDefaultTimeout(6000);
    for (const route of routes) {
      const response = await page.goto(preview + route, { waitUntil: 'domcontentloaded', timeout: 12000 });
      assert(response?.ok(), 'Page failed at ' + route);
      assert.equal(await page.locator('main h1').count(), 1, route);
      const sizes = await page.evaluate(() => {
        const root = document.documentElement;
        return { viewport: root.clientWidth, content: root.scrollWidth };
      });
      assert(sizes.content <= sizes.viewport + 1,
        route + ' overflows at ' + width + 'px: ' + sizes.content + 'px wide.');
    }
    console.log('PASS: ' + routes.length + ' pages fit a ' + width + 'px viewport.');

    if (width === 390) {
      await page.goto(preview + '/');
      const toggle = page.getByRole('button', { name: 'Toggle navigation' });
      await toggle.click();
      assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
      await toggle.press('Escape');
      assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
      await toggle.click();
      await page.getByRole('navigation', { name: 'Main navigation' })
        .getByRole('link', { name: 'Services', exact: true }).click();
      await page.waitForURL('**/services/');
      await page.locator('main .service-card-link[href="/seo/"]').click();
      await page.waitForURL('**/seo/');
      const question = page.locator('.faq summary').first();
      await question.click();
      assert.equal(await page.locator('.faq details[open]').count(), 1);

      await page.locator('main').getByRole('link', { name: 'Book a free consultation', exact: true }).click();
      await page.waitForURL('**/contact/');
      const form = page.locator('#enquiry');
      assert.equal(await form.getAttribute('action'), '/api/enquiry.php');
      assert.equal(await form.evaluate(element => element.checkValidity()), false);
      await form.locator('#name').fill('Website QA');
      await form.locator('#business').fill('DigitalTalha Preview');
      await form.locator('#email').fill('qa@example.com');
      await form.locator('#service').selectOption({ label: 'SEO' });
      await form.locator('#message').fill('Local preview form validation.');
      await form.locator('[name="consent"]').check();
      assert.equal(await form.evaluate(element => element.checkValidity()), true);
      await form.getByRole('button', { name: 'Send enquiry' }).click();
      const status = form.getByRole('status');
      await status.waitFor({ state: 'visible' });
      assert.match(await status.textContent(), /Enquiries can be sent on the live website/);
      console.log('PASS: mobile menu, service link, FAQ, consultation button and enquiry validation.');
    }
    await page.close();
  }
} finally {
  await browser?.close();
  server?.kill();
  rmSync(dependencyDir, { recursive: true, force: true });
}
