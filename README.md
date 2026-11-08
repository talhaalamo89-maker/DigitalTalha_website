# DigitalTalha — classic website

Updated 8 November 2026. Live at [digitaltalha.com](https://digitaltalha.com/). A minimal, content-led website for Talha Alam, with the existing orange, warm-white and black palette, Poppins typography and normal scrolling.

## Review

Open `DigitalTalha-preview.html` in a browser. It includes all 13 content pages and shared images in one file. Internal navigation works; enquiries are disabled in this preview. The production website files are in `dist/`.

This repository includes the migration fixes deployed after explicit approval on 8 November 2026, based on commit `92b59181ba898963b5a607823a2003c12d408925`. **Updates pushed to `main` now build, test on the separate test website, and publish to Hostinger automatically after passing checks.** See [automatic updates](deployment/AUTOMATION.md) and [GitHub Actions](https://github.com/talhaalamo89-maker/DigitalTalha_website/actions/workflows/website.yml). Pull requests run checks without publishing. Sensitive backend and deployment-control changes stop for review.

## What changed

- The original logo sits on a dark badge so its white details remain visible in the light header and dark footer.
- Four services: Google Ads, Meta Ads, Website Creation and SEO. Each has a dedicated static page, an original service illustration, useful scope, fit, deliverables, preparation notes and FAQs.
- Service images are WebP, approximately 26–37 KB each. The original generated images are retained separately from the website deliverable; the web versions are in `assets/`.
- About content follows Talha’s supplied public About page: Class 12 curiosity, marketing reading, the UT Digital Media course, BBA studies, hands-on practice and direct working style. The outdated two-service framing was revised without inventing qualifications, results or testimonials.
- Enquiry forms appear only on `/contact/`. Header, footer and service contact links lead there. SEO is included in the form and accepted by the PHP handler.
- Existing page addresses remain unchanged. New SEO page: `/seo/`. All pages are emitted as static HTML directories. Page content and service links are available in the initial HTML.
- Unique metadata, canonical URLs, service-specific social images, linked structured data, image alternatives, breadcrumbs, sitemap and legacy redirects are included.

## Source

| File | Purpose |
| --- | --- |
| `content/services.json` | Four service descriptions, scope, FAQs and artwork mapping |
| `scripts/classic_pages.py` | Current page layouts and About content |
| `scripts/build.py` | Header, footer, forms, article, legal content and static routes |
| `content/seo.json` and `scripts/seo.py` | Search metadata and structured data |
| `assets/site.css` | Current responsive layout and brand styling |
| `assets/site.js` | Menu, search, FAQ and enquiry behavior |
| `server/enquiry.php` | Production enquiry validation and mail handling |

Earlier motion sources remain as reference. They are excluded from delivery, and the active layout does not use animation libraries.

## Build and check

Requires Python 3.10+ and Node.js; no package installation is needed.

```sh
npm run build
npm run check
npm run dev
```

The local preview normally uses `http://127.0.0.1:4173`. Managed preview environments bind to the container interface and support `PORT`. This is preview configuration only.

Checks pass for 21 HTML files and 13 primary pages, including links, fragments, images, headings, form wiring, retained article text, metadata, schema, sitemap, service content and interaction behavior. The production sitemap contains 12 indexable URLs. The standalone preview also passes JavaScript syntax validation.

Representative desktop/mobile browser review passed on staging; the live homepage, mobile navigation and Contact layout were also checked. Hosted staging passed 42 checks, local versioned routing passed 49 checks, and production passed 68 checks plus five preserved application/media URLs. See `VERIFICATION.md` and the migration audit records. These checks do not establish live rankings, Core Web Vitals, inbox delivery or Analytics receipt.

## Production

**Do not upload an overwriting archive or copy `dist/` over this account's main document root.** Existing subdomain websites are nested inside it. Production uses `public_html/.digitaltalha-release-20261108/` and one root `.htaccess` dispatcher. The packaged release also adapts its nested 404 error-document path. WordPress files and its database remain in place for rollback.

Normal updates use [the automatic workflow](deployment/AUTOMATION.md). [deployment/README.md](deployment/README.md) retains the manual packaging and recovery procedure. `deployment/root.htaccess` preserves the approved initial dispatcher template; the restricted service selects a new release for each update. `.hostinger/site.json` records the target. The complete private action record and backups remain in the local migration handoff, outside this repository. The temporary migration SSH key was revoked; a separate permanent key now permits only the reviewed deployment commands. General server changes require separately authorized access.

The canonical origin remains `https://digitaltalha.com/`. Public staging can use:

```sh
SITE_NOINDEX=1 npm run build
python3 scripts/check-seo.py --staging
```

Rebuild without `SITE_NOINDEX` before production deployment.

The retained mail recipient is `talhaalamo89@gmail.com`, with sender `website@digitaltalha.com`. PHP execution and rejected invalid submissions passed on the live host. No valid enquiry was sent, per the user's instruction; inbox delivery remains unverified. A lead event is pushed to the data layer only after a successful backend response and records the selected service without enquiry personal fields. Existing GTM `GTM-NMMW3MLB` is retained, but its published container has no active GA4 measurement/lead tag; reporting and conversions remain unverified.
