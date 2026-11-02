# Routing — Universal Routes, Page Headers, URLs & SEO

> Scope: every storefront route, the shared page-header contract, query
> rules, PDP variant URLs, and canonical/SEO discipline. Single authority —
> page docs and implementations reference this file, never re-decide it.
> Status: Active | Version 1.2 | Date: 2026-11-02
> Parent: `0.Project-Overview.md` §14 (Docs Index) · `5.Features.md` (acceptance)

---

## 1. Route map (locked)

| Route | Page | Notes |
|---|---|---|
| `/` | Homepage (`pages/home.md`) | hero is the header; no H1/breadcrumb |
| `/products?category=` | Listing + category | ONE canonical listing route (§4); category is a filter, never a path |
| `/products/[slug]` | PDP | slug only — never ids (`/p?id=` banned) |
| `/compare?ids=a,b` | Compare (max 4) | unordered set → query, not path |
| `/cart` | Cart | top-level, title only |
| `/checkout` | Checkout | auth-required; title only |
| `/checkout/confirmation/[orderId]` | Order confirmation | auth-required; bookmarkable — order number is the identity (A5.8) |
| `/account/*` | Account (orders/addresses/wishlist) | auth-required; sub-routes, bookmarkable |
| `/blog`, `/blog/[slug]` | Blog surfaces (shipped sf-063, CMS-fed) | index is title-only; article gets breadcrumb + `<h1>` from the post |
| `/blog/category/[slug]` | Blog category (spec — not yet built) | `listBlogs({category})` exists client-side; a route is deferred until a category exists |
| `/about`, `/privacy`, `/terms` | Company/legal pages (shipped sf-063, CMS-fed) | each renders one cms-svc page document's blocks; no copy in the route |
| `/signin`, `/signup`, `/forgot` | Auth (`(auth)` group) | NOT `/login`; conversion chrome (minimal nav, footer suppressed) |

The `/blog`, `/about`, `/privacy`, `/terms` routes render CMS documents
(`lib/cms/client.ts` → blogs/pages reads). A missing/unpublished document is
`notFound()`; a long policy renders inside the prose *measure* (`max-width` on
the text block), never a capped page (§2, design-system §4 / decision §10.2).

Auth rule (from Features A11): unauthenticated `/account` or `/checkout`
→ `/signin?next=<original>` (resume the interrupted task).

## 2. PageHeader contract (one shell, all pages)

`PageHeader({ eyebrow?, title, breadcrumb?, actions? })` on the shared
full-bleed shell (`padding-inline var(--sf-page-pad)`,
`clamp(16px, 4vw, 50px)`, no page `max-width`). Slots filled per page type — never copy-pasted:

| Page type | H1 top-left | Breadcrumb | Rationale |
|---|---|---|---|
| Listing, account, cart, checkout, compare, blog index | ✅ | ❌ | top-level — `Home / Cart` trails are noise |
| PDP, blog article | ✅ (product/post name) | ✅ (`Home / Shoes / Running X`) | deep pages need an upward escape path |
| Auth | configurable centered/split, no H1 (see `pages/auth-design.md`) | ❌ | conversion focus, minimal chrome |
| Home | ❌ (hero is the header) | ❌ | |

## 3. Query rules — path = identity, query = short-lived data representing the current condition of a UI (Ephemeral View State)

**Allowed in query:** filters/sort (`?category=&sort=`), search `?q=`,
compare `?ids=`, pagination cursor, `?preview=1`, auth `?next=`, PDP
variant keys (§4).
**Banned from query:** quantity, form contents, tokens, PII/secrets
(anything that leaks via history, logs, or referers).

## 4. PDP variant URLs

* Format `/products/[slug]?color=&size=` — slugs (never ids), fixed key
  order (`color` before `size`; order variants are duplicate URLs).
* Server-validated on load; invalid/out-of-stock → nearest in-stock valid
  variant + quiet notice + URL rewrite (never 404, never silent wrongness).
* Shared links land on the exact variant; committed selections push history
  (back steps through tried variants); refresh preserves selection.

## 5. SEO discipline (variant + filter sprawl)

1. **Canonical is always the bare slug** (default = first in-stock variant);
   every variant URL emits `rel=canonical` to it.
2. **Internal links always bare** — sitemaps, grids, related items,
   breadcrumbs. Canonical is a hint; unanimous internal linking makes it
   near-deterministic. Sitemap = canonicals only.
3. **Same discipline covers listing filters** (the bigger sprawl risk):
   filtered URLs canonicalize to the unfiltered listing.
4. **JSON-LD `Product` with per-variant `offers`** (price, availability,
   sku, image) on the canonical page — variant richness for rich results
   with zero URL sprawl.
5. Acceptance (extends Features A2/A9 shareability): every variant/filter
   URL reproduces its result set; every variant URL emits the bare-slug
   canonical. Per-variant indexing (long-tail color queries) is deferred
   until Search Console shows demand worth chasing.

---

## Appendix — file references

- Page specs: `pages/home.md` (more per §6 of the docs plan)
- Acceptance: `5.Features.md` A2/A3/A9/A11 · `9.Testing.md` (URL SLOs)
- Implementation: `PageHeader` + `Breadcrumbs` shell (`shell-cart.md` §3/§5),
  blog routes `app/(shop)/blog/{page,[slug]/page}.tsx` +
  `lib/blog/present.ts` (sf-063), legal routes
  `app/(shop)/{about,privacy,terms}/page.tsx` via
  `_components/cmsPageRoute.tsx` → `components/pages/{CmsPage,PageBlocks}.tsx`
  + `lib/pages/richText.ts` sanitizer (sf-063), return-path/mint logic in
  `proxy.ts` (shipped sf-051)
- `useVariantFromURL` query sync: to build with PDP depth (sf-055)
