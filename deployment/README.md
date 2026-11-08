# Hostinger deployment and recovery

The custom site went live at https://digitaltalha.com/ on 8 November 2026 after explicit approval. This repository records its source and generated files. **A GitHub push does not deploy the site.** No auto-deploy is configured.

## Preserve the existing layout

The live document root contains original WordPress files and nested websites. Do not use an archive deployment that replaces or clears that root. Keep the `demo`, `gtmpractice`, `shop`, `marketing`, `ecommerce` and `practice` folders, original uploads, `.well-known`, `llms.txt` and existing DNS/email records.

Production consists of:

- `public_html/.digitaltalha-release-20261108/`: the complete 42-file release.
- `public_html/.htaccess`: the root dispatcher recorded exactly in `deployment/root.htaccess`. It preserves child hosts/folders, old media and nine WordPress shortlinks, then routes the main site into the release.
- A release-level `.htaccess` built from `dist/.htaccess`, with its 404 error-document path adapted to the nested directory. Direct access to the hidden release URL is denied.

Original WordPress files/database were retained for rollback; WordPress admin no longer edits the main site. Private file/database backups, keys, account audit records and the complete migration history remain in the local handoff outside this Git repository. The temporary migration key was revoked. Use your own verified SSH/SFTP access for future work.

## Build and package

From the repository root, run:

```sh
npm run build
npm run check
python3 deployment/package-release.py --release .digitaltalha-release-20261108
```

The last command creates an ignored ZIP under `deployment/packages/`, adapting the nested error-document path without modifying `dist/`. It creates an archive only; it does not connect to or change Hostinger. An archive's SHA may differ due to ZIP timestamps; compare extracted file bytes when checking against the original release.

The dated release is already live. For a new deployment, choose a new directory name, replace every occurrence of the old release name in a copy of the root dispatcher, and package with the matching `--release` value. Never overwrite the active release. The saved dispatcher contains the production domain and should not be installed unchanged on another hostname.

For a separate public staging website, build with `SITE_NOINDEX=1`, check with `python3 scripts/check-seo.py --staging`, and retain noindex metadata/headers, no tracking and an empty sitemap. Adapt its dispatcher hostname and error-document directory. Rebuild production without `SITE_NOINDEX` afterward. Do not install a staging build on the main domain.

## Manual deployment sequence

1. In Hostinger, confirm the exact domain, account, document root and nested subdomain roots. Check SSL, PHP support and the current DNS/email records. Establish SSH/SFTP access and compare the server fingerprint with hPanel before trusting it.
2. Create fresh private backups of the full document root, including dotfiles and child folders, and the correct database identified from `wp-config.php`. Store them outside the public root, download them, compare hashes, and inspect archive/SQL integrity. Keep the current active root dispatcher separately. Do not commit these backups or credentials.
3. Build, check and review the new candidate on a separate staging site. Verify routes, redirect targets, unknown-page 404s, PHP execution, mobile navigation and intended indexing. A valid enquiry sends mail; test that only when authorized and verify receipt independently.
4. Create a new private preparation directory beside `public_html`. Upload the release ZIP and matching root dispatcher there. Compare their local/server SHA-256 hashes. Extract the ZIP into a new private `release/` folder; check file count, `index.html`, `api/enquiry.php`, production indexing and nested ErrorDocument path. Set directories to 755 and files to 644. Ensure the new public release destination does not exist.
5. Record the precise overwrite and rollback plan and obtain approval before replacing a live site's routing. Recheck the current root dispatcher's hash for drift. Clear only the main site's old caches as appropriate.
6. Save another private copy of the active root `.htaccess`. Move the complete prepared `release/` directory to the new hidden path under `public_html`. Atomically rename the prepared dispatcher over `public_html/.htaccess` on the same filesystem. Do not remove the old routing file first. Leave WordPress files, databases, child folders, DNS and mail records in place.
7. Clear the main website's provider cache. Verify actual served content, not merely the upload acknowledgement. Test the main domain and www SSL/redirect chains, all primary pages/assets, 12 sitemap URLs, canonical/indexing metadata, legacy paths/shortlinks with tracking parameters, true 404s, internal-release denial and PHP validation. Compare the DNS zone and preserved subdomains/uploads with the baseline.
8. Review the live desktop/mobile layout. Confirm enquiry inbox delivery and Analytics reporting separately when authorized and configured. Retain the old release, original dispatcher and verified backups until the new release is accepted. Remove temporary access keys and record the result.

## Rollback

For a later custom-site update, restore the dispatcher saved immediately before that update. Copy it to a private temporary file, verify its hash, then atomically rename it over `public_html/.htaccess`. Clear the main-site cache and verify the previous custom release returns.

To return to the original WordPress site from this migration, use the privately saved original WordPress `.htaccess` instead. No SQL import or original WordPress file replacement was needed for this migration's planned routing rollback. Its execution and a full restore were not tested. Establish your own verified access first; the migration key was removed. Do not restore the entire hosting account or overwrite child websites.

## Verification limits

The migration passed 68 production checks plus five preserved successful application/media URLs, 42 staging checks and 49 local versioned-routing checks. Representative desktop/mobile browser checks also passed. The retained GTM container `GTM-NMMW3MLB` lacks an active GA4 measurement/lead tag, so reporting/conversions remain unverified. Valid email sends were declined; actual enquiry delivery remains unverified. No Search Console action, measured Core Web Vitals, full restore or continuous downtime monitoring was performed.
