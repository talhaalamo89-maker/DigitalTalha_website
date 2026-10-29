# SEO implementation — 29 October 2026

Each service has a dedicated, statically generated page: `/google-ads/`, `/meta-ads/`, `/website-creation/` and `/seo/`. Existing canonical routes and WordPress-era redirects are retained. The sitemap now contains 12 indexable URLs.

Service pages explain the offer, intended customer, included work, deliverables, required inputs, limitations and common questions. Important content and links are rendered directly in HTML. The About page gives the named marketer’s real background and working approach; the existing practice project is clearly labelled as hypothetical.

Page-specific titles/descriptions, canonical URLs, Open Graph/Twitter metadata, descriptive image alternatives and linked Person, WebSite, WebPage, Service, BreadcrumbList and article entities are included where relevant. Service social previews use the new matching artwork. Only actual hero imagery is preloaded; below-fold images are lazy loaded and include dimensions.

The implementation follows the [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide). Keyword choices describe the offered services. No local search-volume research, ranking improvement, indexing result or live speed measurement is claimed.

Before launch, check the production host’s indexing headers, HTTPS, redirects and 404 behavior. Verify Search Console ownership, inspect representative pages and submit `/sitemap.xml`. Test live mobile performance and real enquiry delivery. A public staging build should use `SITE_NOINDEX=1`; rebuild normally before production deployment.
