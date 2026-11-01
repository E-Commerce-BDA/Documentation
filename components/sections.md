# Section blocks — HeroSection

> Scope: `frontend/storefront/components/sections/HeroSection.tsx`,
> `lib/sections/hero.ts` (the model + `DEFAULT_HERO` resolver), and the
> `.sf-hero*` block in `app/globals.css`.
> Status: Active | Version 1.0 | Date: 2026-11-01
> Parent: `components/README.md` §1 · `pages/home.md` §3 (hero spec) ·
> `design-system/storefront.md` §5
> Implements: sf-051 (`/` hero). Sections beyond the hero land with sf-060.

---

## 1. Look per state (normative)

### HeroSection (v1 — one static slide)

Text panel + image panel on a 1280 px / 24 px grid. Desktop is two columns;
below 768 px the panels stack text-first and the column order never changes.

| State | Look |
|---|---|
| default (`align="left"`) | text panel left, image panel right, `--color-surface` fill |
| `align="center"` | text panel centred, image panel below full width; CTAs centred |
| no image | single column — text panel takes the grid, no reserved media box |
| no CTAs (`ctas: []`) | no CTA row at all (never an empty flex row) |
| hover / focus-visible on a CTA | shared ring; `--color-ink` fill, `--color-surface` label |

Eyebrow is 12 px small caps in `--text-muted`; title is `<h1>` (it *is* the page
header on `/`); body is 16 px `--color-ink` at the muted tone. Image is a plain
`<img loading="eager">` (LCP) inside a `--color-accent-soft` backing box — no
`next/image`, matching the `ProductCard` precedent.

## 2. Customizable fields (what admin can change)

| Knob | Values | Default (`DEFAULT_HERO`) |
|---|---|---|
| `eyebrow` | string | `"New season"` |
| `title` | string (required) | `"Everything for every day"` |
| `body` | string | one sentence of house copy |
| `ctas` | `Cta[0..3]` — `{ text, href, variant? }` | primary `Shop now → /products`, light `Browse categories → /products` |
| `image` | `{ src, alt, ratio? }` | `undefined` (no-image face) |
| `align` | `"left" \| "center"` | `"left"` |

`ratio` accepts `"4:3"`, `"1:1"`, `"16:9"`; absent = `"4:3"`. Cap of three CTAs
is enforced in the resolver, not in the component (`lib/sections/hero.ts`),
mirroring the CMS `z.array(ctaSchema).max(3)` rule in `pages/home.md` §3.8.

## 3. How to change (scopes — where a value lives)

| Value | Home | Override |
|---|---|---|
| CTA cap (3), ratio fallback, `DEFAULT_HERO` copy | `lib/sections/hero.ts` → `resolveHero` | per-instance flat props |
| paint (fills, type scale, easing) | `.sf-hero*` + house tokens | theme tokens only — no per-section palette |
| image host | the route that passes `image.src` | — (`<img>` accepts arbitrary admin hosts) |
| slide set | not in v1 — single object | `slides: Slide[]` arrives with sf-060 |

## 4. Global rules (inherited)

1. **`props → JSX`.** The block never fetches; the route resolves hero content
   (today `DEFAULT_HERO`, later `cms-svc`) and passes it down.
2. **Controlled-only.** No state, no autoplay, no interval. Multi-slide
   navigation (`activeIndex` + dots) is a caller-owned prop pair when sf-060
   lands — the same reason `Gallery` is controlled.
3. **State reaches CSS only through `data-*`** (`data-align`, `data-has-image`).
4. **A11y fixed.** `<section aria-label="Hero">`, `<h1>` for the title, image
   `alt` required when `image` is present, CTAs are real anchors (never
   `onClick` navigation).
5. **Trio tests** — `hero.test.tsx` (contract + resolver) and
   `hero-style.test.ts` (paint only through vars).

## 5. Apply-to-all (the per-type bulk switch)

N/A — there is no per-type switch for a section; the section *type* is the
switch, and it is a route-level choice (`pages/home.md` §2 section order).

---

## Appendix — file references

- Model + `DEFAULT_HERO`: `lib/sections/hero.ts` · `test/lib/sections/hero.test.ts`
- Block: `components/sections/HeroSection.tsx` · `test/components/hero.test.tsx`
- Paint: `app/globals.css` `.sf-hero*`
- Consumers: `app/(shop)/page.tsx` (hero + featured grid, sf-051)
- Deferred: multi-slide carousel, hero CMS content, and the BannerSection /
  FeaturedProducts / CategoryShowcase / BrandStrip / BlogTeaser siblings all
  arrive with **sf-060** (needs the contracts repin in sf-053 first —
  `@ecom/contracts` 1.7.0 ships no Section schemas).
