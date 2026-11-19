# DigitalTalha on Cloudflare Pages

The production website is https://digitaltalha.com/. Its Direct Upload project
is `digitaltalha-migration`, with `cloudflare-production` as its production branch.
The CMS review branch deploys to https://pages-cms.digitaltalha-migration.pages.dev/.

## Build, verify and publish

See [Editing and publishing](../CMS.md) for the GitHub workflow. The production
job runs after a successful push build on `main`, or by manual dispatch on
`main` with the production target. The preview job builds with noindex, omits
tracking, uses the separate preview D1 binding and disables enquiry delivery under
the normal preview configuration.

To build and deploy a preview locally with authorised Wrangler access:

```sh
SITE_NOINDEX=1 npm run build:cloudflare
npm exec --yes --package wrangler@4.162.0 -- wrangler pages deploy dist --project-name digitaltalha-migration --branch pages-cms --commit-dirty=true
python3 cloudflare/check_runtime.py https://pages-cms.digitaltalha-migration.pages.dev/
```

Use `wrangler pages deployment list --project-name digitaltalha-migration
--environment production` to identify the current production deployment.
Keep production and preview artifacts separate. The preview Worker returns 503
on the public custom domain as a safeguard against publishing the wrong artifact.

## SEO and public files

`prepare.py` wraps the checked static build in Pages advanced mode. It removes
PHP and Apache configuration, generates Worker routing/security headers and
copies only reviewed public files from `legacy-public` into the final artifact.
Keep that directory when updating: it preserves 44 public dated WordPress media
files and the updated root llms.txt. Do not copy a full WordPress uploads archive;
private form attachments and plugin/server files are deliberately excluded.

The Worker preserves 13 exact aliases, five old sitemap filenames, nine WordPress
IDs through both p/page_id query parameters, unrelated campaign parameters,
HTTPS/non-www canonicalisation, index.html/slash redirects and the actual hospital
project page. `/projects/` now serves the portfolio. Legacy category routes and
WordPress shortlink 504 lead there. `/resources/` redirects to the dedicated
blog at `/blog/`. Unknown public routes remain 404. All non-custom-domain hosts get
noindex and an empty sitemap. The 13 production canonical pages remain indexable.
Cloudflare may append its analytics beacon; original page content and GTM markup
were checked against the source. Analytics reporting itself was not verified.

## Enquiries and incoming mail

The original `/api/enquiry.php` address is handled by `worker.mjs`; raw PHP is not
published. Valid enquiries use Resend's HTTPS API and the verified sender
`website@notify.digitaltalha.com`. Replies address the visitor's supplied email.
Cloudflare separately forwards incoming hello@ mail to the configured Gmail inbox.
This forwarding does not configure a Gmail "send as hello@" identity.

Keep these server settings private:

| Setting | Storage |
| --- | --- |
| RESEND_API_KEY | Cloudflare secret, sending-only key |
| ENQUIRY_TO | Cloudflare secret, confirmed Gmail destination |
| RATE_LIMIT_SECRET | Cloudflare secret, random value of at least 32 characters |
| ENQUIRY_FROM | website@notify.digitaltalha.com |
| ENQUIRY_PREVIEW_HOST | Empty in production and normal previews |

Production D1 binding ENQUIRY_DB points to `digitaltalha-enquiry-production`,
`9b7b939b-116d-4b26-a8aa-6a5223f28dab`. Preview uses its own database.
Both schemas are applied. D1 stores only keyed IP digests and expiry timestamps,
not enquiry content. Atomic SQL limits attempts to one per IP per 60 seconds.

The backend checks origin, size, content type, required fields, consent, service,
phone, website and honeypot. It rejects duplicates/header injection and fails
closed on missing configuration, storage or provider failure. A provider message
ID is required before reporting accepted delivery. The November 2026 cutover verified two live enquiries in Gmail with SPF, DKIM and DMARC passing.

## Validation and recovery

Ten Worker test groups and a real SQLite test passed. Existing build, metadata,
service and interaction checks passed. The final public audit passed 13 pages,
83 redirects, 45 preserved public files, HTTPS, robots/sitemap, missing/private
paths and preview noindex. See the archived cutover verification in the original migration workspace.

Keep the November 12 hosting/files and seven-database backup, original DNS exports
and the saved production/source archives. Full WordPress restore was not tested.
Recover a defective update using the last verified Pages deployment and existing
production bindings, rather than assuming the expired Hostinger origin works.
No old hosting, mailbox or backups were deleted. Old message recovery was waived.
