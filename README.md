# DigitalTalha website

A portable redesign of digitaltalha.com, built around shorter copy, original character illustrations, visual service journeys and useful interactions. Colours: orange #EB5729, warm white and black. Poppins has a system-font fallback.

## Review the website

Open `DigitalTalha-preview.html` in a browser. This self-contained file contains all pages and images, including the favicon. Enquiries are intentionally disabled in the preview; direct WhatsApp and email links remain available. Reopen the updated file to see the latest version.

For an HTTP preview, run from this folder:

```sh
python3 scripts/build.py
python3 scripts/preview.py
python3 scripts/serve.py
```

Then open http://127.0.0.1:4173. The preview server never serves PHP source or sends mail. This authoring environment could not run the local HTTP/browser preview, so desktop/mobile visual verification remains pending.

## What is included

- Home, About, Services, Google Ads, Meta Ads, Website Creation, Projects, Contact, Privacy Policy, Terms and the full campaign article, plus a custom 404 page.
- Distinct search analyst, social creative and website builder illustrations, each with its own subtle motion.
- Selectable service journeys, a goal-based service picker and clickable process steps.
- Scope and FAQs that open when needed, rather than long default page sections.
- A sticky Pause motion control, saved motion preference, system reduced-motion support, and animation pausing when scenes leave the viewport or the page is in the background.
- Locally bundled brand assets and artwork. Only the optional Google Font needs an external visual resource.
- PHP enquiry handling, form validation, spam controls, error feedback and a successful-enquiry data-layer event.

Original source snapshots remain in `content/original-pages.json`. Marketing copy is intentionally condensed under the latest brief; the original public routes, complete 22-section article and policy text are retained. No client results, testimonials, revenue figures or turnaround guarantees were invented. Character artwork is an illustration of the services; DigitalTalha remains a solo freelance business.

## Edit and rebuild

Requires Python 3.10+ and Node.js for interaction checks. No package installation is needed.

- `scripts/motion_pages.py`: active visual page layouts and concise marketing copy.
- `scripts/build.py`: shared header, footer, forms, SEO, article, policies and route generation.
- `assets/motion.css` and `assets/motion.js`: illustrations, motion, selectors and controls.
- `assets/site.css` and `assets/site.js`: shared styles, navigation, search and form submission.
- `content/website-service.json`: full Website Creation scope and FAQs.
- `server/enquiry.php`: server-side enquiry validation and mail transport.

```sh
npm run build
npm run check
```

The build generates `dist/` for hosting and refreshes `DigitalTalha-preview.html`. The preview stores each image only once to keep the file small. It does not use a third-party animation library.

## Production routes

| Page | URL |
| --- | --- |
| Home | `/` |
| About | `/about/` |
| All services | `/services/` |
| Google Ads | `/google-ads/` |
| Meta Ads | `/meta-ads/` |
| Website Creation | `/website-creation/` |
| Projects / blog | `/blog/` |
| Contact | `/contact/` |
| Privacy | `/privacy-policy/` |
| Terms | `/terms-conditions/` |
| Full article | `/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/` |

Legacy `/service/`, `/about-us/`, `/contact-us/` and `/projects/` addresses have Apache 301 redirects and static fallback pages. Other unknown paths use `404.html`. Existing subdomains are outside this migration.

## Hostinger deployment

1. Download both the existing WordPress files and database as a complete backup.
2. Test the replacement separately while the existing site stays live.
3. Use a Custom PHP/HTML site with PHP 8.1+.
4. Upload the **contents** of `dist/` into the domain’s `public_html`, including `.htaccess`. Keep source snapshots and documentation outside the document root.
5. During the planned switch, remove old WordPress routing/index files that would override the new site, keeping the backup for rollback.
6. Preserve DNS and email records, confirm HTTPS and www/non-www behavior, and check redirects and 404 responses.
7. Test desktop/mobile rendering, interactions, pause/reduced motion and real email delivery before launch.
8. Reconcile existing analytics and consent settings; submit `/sitemap.xml` after launch. Public staging copies need noindex. Production robots/sitemap allow indexing.

The source and generated hosting files are maintained in https://github.com/talhaalamo89-maker/DigitalTalha_website. Hostinger deployment remains a separate step; the live WordPress site has not been replaced.

## Enquiry delivery

`server/enquiry.php` is copied to `dist/api/enquiry.php`. It validates fields, service selection, consent and request origin; rejects the spam honeypot; and rate limits by IP using temporary timestamp files outside the document root. Message content is emailed, not saved in public files.

Recipient: `talhaalamo89@gmail.com`. Sender: `website@digitaltalha.com`. Provision a valid sender and confirm Hostinger mail transport and SPF/DKIM before launch. PHP accepting a message does not prove inbox delivery; send a real test after hosting is connected. If authenticated SMTP is required, keep credentials in server settings, outside the repository and browser code.

Website Creation enquiries use a project budget, while advertising forms use monthly ad budget. A `generate_lead` data-layer event is emitted only after the server accepts the enquiry. Existing GA4/GTM/Meta IDs were not supplied, so no provider IDs or tracking setup were fabricated. PHP runtime and inbox delivery remain unverified in this environment.
