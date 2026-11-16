# DigitalTalha website

[DigitalTalha](https://digitaltalha.com/) is a static website built with Python and deployed to Cloudflare Pages. Pages CMS provides the content editor using the existing GitHub repository. See [Editing and publishing](CMS.md) for the setup and daily workflow and [Cloudflare Pages](cloudflare/README.md) for hosting and recovery.

## Build and check

Python 3.13 and Node.js 24 or later are used in CI.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm run test:cloudflare
npm run build:cloudflare
```

Run `SITE_NOINDEX=1 npm run build:cloudflare` for review, then open the generated `DigitalTalha-preview.html` or run `npm run dev` and visit `http://127.0.0.1:4173`. The local form cannot deliver mail. The build recreates `dist/` from source, so drafts, removed pages and older generated files cannot persist across builds.

| Source | Purpose |
| --- | --- |
| `.pages.yml` | Pages CMS fields and media settings |
| `content/pages/`, `content/services/` | Website copy, headings, illustrations and FAQs |
| `content/hospital-project.json` | Case study details and screenshots |
| `content/posts/`, `content/seo/` | Blog posts, titles, descriptions and social cards |
| `scripts/`, `assets/` | HTML generation, layout, images and site behavior |
| `cloudflare/` | Redirects, enquiry handler, legacy files and Pages packaging |

Earlier motion templates and Hostinger scripts remain as historical reference. Cloudflare production uses the existing static design and the Cloudflare enquiry handler.
