# DigitalTalha — classic website

Updated 29 October 2026. A minimal, content-led website for Talha Alam, with the existing orange, warm-white and black palette, Poppins typography and normal scrolling.

## Review

Open `DigitalTalha-preview.html` in a browser. It includes all 13 content pages and shared images in one file. Internal navigation works; enquiries are disabled in this preview. The production website files are in `dist/`.

The current workspace is a recovered copy of the existing project. Its base source was recovered from `talhaalamo89-maker/DigitalTalha_website` and the retained project archive, then updated to the latest brief. It does not automatically update a separate Mac folder. The updated source and generated hosting files are maintained in the GitHub repository. Production deployment remains a separate step. A separate local clone must be pulled to receive repository changes.

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

Checks pass for 18 HTML files and 13 primary pages, including links, fragments, images, headings, form wiring, retained article text, metadata, schema, sitemap, service content and interaction behavior. The standalone preview also passes JavaScript syntax validation.

Browser visual review is still pending. The managed preview could not be reached through the browser route in this session. Responsive rules are implemented, but browser appearance, overflow and real browser interaction have not been verified for this version. These checks are not evidence of live rankings or Core Web Vitals.

## Production

Deploy the contents of `dist/`, including `.htaccess`, to the intended PHP-capable Hostinger document root only after backing up the existing WordPress files and database. Confirm HTTPS, redirects, a true 404, production indexing directives and email delivery before switching traffic.

The canonical origin remains `https://digitaltalha.com/`. Public staging can use:

```sh
SITE_NOINDEX=1 npm run build
python3 scripts/check-seo.py --staging
```

Rebuild without `SITE_NOINDEX` before production deployment.

The retained mail recipient is `talhaalamo89@gmail.com`, with sender `website@digitaltalha.com`. Actual inbox delivery and sender authentication require testing on the host. A lead event is sent to the data layer only after a successful backend response, and records the selected service. No analytics IDs were invented.
