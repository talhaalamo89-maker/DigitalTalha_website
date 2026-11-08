# Verification — 8 November 2026

## Passed

- Production build: 13 primary pages, legacy aliases and error documents, for 21 HTML files in total.
- Local links, asset targets, fragment targets, unique IDs, one H1 per page and ordered heading levels.
- Complete retained campaign article text. Legal content remains sourced from the original retained snapshots.
- Metadata, canonical URLs, linked JSON-LD, breadcrumb agreement, image alt/dimensions, sitemap membership and preview noindex on all 13 primary pages. Production sitemap contains 12 indexable URLs.
- Four static service pages contain their full scope, FAQs, preparation details, related-service links and matching artwork. Images are 1536 × 1024 WebP files, each below 40 KB.
- Service pages and other pages contain no repeated enquiry form. The single Contact form offers all four services and the backend accepts SEO.
- The About page contains the recovered journey and training details rather than only a short introduction.
- Original logo retained, with a dark CSS background behind the white mark.
- Existing enquiry success/failure, submission recovery, no false lead events, navigation Escape handling and project-search tests pass.
- Standalone preview and site JavaScript syntax checks pass.
- Local Apache: 31 normal-layout checks and 49 packaged versioned-routing checks passed.
- Hosted noindex staging: 42 checks passed, including the nested LiteSpeed error-document path, shortlinks, PHP execution and invalid submission rejection.
- Live production: 68 checks passed at 11:55:40 IST on 8 November 2026. Pages, asset hashes, canonical metadata, indexing headers, the 12-URL sitemap, legacy redirects, nine WordPress shortlinks, retained tracking parameters, HTTP/www redirects, a true 404, internal-release access denial and PHP validation were checked.
- Both main-domain and www certificates validated. DNS before/after matched across all 23 records; existing mail records were preserved.
- Three existing WordPress subdomains, `/shop/` and an original upload URL remained successful. The portrait's bytes were unchanged. Six existing application folders and original WordPress files/database remain in place.
- Representative staging desktop/mobile screenshots and 22 layout profiles were reviewed. The live desktop homepage, mobile homepage, Contact layout and mobile menu navigation were reviewed with no horizontal overflow in those measurements.
- Fresh files/database backups were downloaded and independently checked for matching hashes and archive/SQL integrity. The temporary migration key was revoked and a new connection was rejected.

Full evidence is retained privately in the local migration handoff: `audit/live-verification.json`, `audit/live-browser-review.json`, `audit/backup-verification.json` and `audit/access-cleanup.json`. These records and private backups are excluded from this repository. Production used the approved versioned-release switch; no rollback was required. The user subsequently authorized committing and pushing the deployed migration fixes to GitHub.

## Not verified

Valid enquiry sending/inbox delivery and successful-send rate limiting were not tested because the user declined email tests. Frontend success behavior was tested with simulated responses. PHP `mail()` acceptance is not inbox delivery.

Analytics reporting/conversions remain unverified: existing public GTM container version 7 has only a link-click listener, with its GA4 ID stored as a variable rather than an active measurement tag. Search Console, real-device performance/Core Web Vitals, a full WordPress restore and an actual rollback were not tested. No continuous availability monitoring or zero-downtime guarantee is claimed.
