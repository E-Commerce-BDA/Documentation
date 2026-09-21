# Routing — Universal Routes, Page Headers, URLs & SEO

> Scope: every storefront route, the shared page-header contract, query
> rules, PDP variant URLs, and canonical/SEO discipline. Single authority —
> page docs and implementations reference this file, never re-decide it.
> Status: Active | Version 1.0 | Date: 2026-09-18
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
| `/account/*` | Account (orders/addresses/wishlist) | auth-required; sub-routes, bookmarkable |
| `/blog`, `/blog/category/[slug]`, `/blog/[slug]` | Blog surfaces | article gets breadcrumb |
| `/signin`, `/signup` | Auth (`(auth)` group) | NOT `/login`; conversion chrome (minimal nav, no footer noise) |

Auth rule (from Features A11): unauthenticated `/account` or `/checkout`
→ `/signin?next=<original>` (resume the interrupted task).

## 2. PageHeader contract (one shell, all pages)

`PageHeader({ eyebrow?, title, breadcrumb?, actions? })` on the shared
1280px / 28px-24px grid. Slots filled per page type — never copy-pasted:

| Page type | H1 top-left | Breadcrumb | Rationale |
|---|---|---|---|
| Listing, account, cart, checkout, compare, blog index | ✅ | ❌ | top-level — `Home / Cart` trails are noise |
| PDP, blog article | ✅ (product/post name) | ✅ (`Home / Shoes / Running X`) | deep pages need an upward escape path |
| Auth | ❌ centered card | ❌ | conversion focus, minimal chrome |
| Home | ❌ (hero is the header) | ❌ | |

## 3. Query rules — path = identity, query = ephemeral view state

**Allowed in query:** filters/sort (`?category=&sort=`), search `?q=`,
compare `?ids=`, pagination cursor, `?preview=1`, auth `?next=`, PDP
variant keys (§4).
**Banned from query:** quantity, form contents, tokens, PII/secrets
(anything that leaks via history, logs, or referers).

## 4. PDP variant URLs (locked decision)

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
- Implementation: `PageHeader` shell (to build), `useVariantFromURL` sync
  (to build with PDP), `middleware.ts` return-path (to build with auth)
