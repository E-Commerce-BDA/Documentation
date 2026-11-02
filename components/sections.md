# Section blocks — the CMS home vocabulary

> Scope: `frontend/storefront/components/sections/*` (blocks + registry +
> carousel island), `lib/sections/*` (view models, resolver, marquee/present
> helpers), and the `CMS home sections` block in `app/globals.css`.
> Status: Active | Version 2.0 | Date: 2026-11-02
> Parent: `components/README.md` §1 · `pages/home.md` §3 (section spec) ·
> `design-system/storefront.md` §4/§8 · `pages/routing.md` §2
> Implements: sf-051 (single hero) and **sf-060** (CMS-composed home: six
> blocks, the resolver, the registry, the degraded faces).

---

## 0. The pipeline — one page, four layers (normative)

| Layer | File | Owns | Never does |
|---|---|---|---|
| Route | `app/(shop)/page.tsx` | fetch `getSections(homepage)`, pick a face, `revalidate = 300` | any copy, any order, any layout |
| Resolver | `lib/sections/resolveSections.ts` | fan-out to catalog/cms, skip rules, order, knob defaults | any JSX, any pixel |
| Registry | `components/sections/SectionRenderer.tsx` | type → block dispatch, single- vs multi-slide hero | fetching, sorting, inventing defaults |
| Block | `components/sections/*Section.tsx` | paint the view model exactly | fetching, deciding, state (the one exception is the hero island, §1.2) |

Five resolver rules, enforced in `resolveSections` and nowhere else:

1. **Order is the CMS `sortOrder`.** Nothing downstream re-sorts, so an admin
   drag in the (future) panel is the page.
2. **Inactive and empty are both skips.** A hero with no usable slide or a
   strip whose brands all vanished paints *nothing* — an empty box is theatre.
3. **A dead service costs one section.** `null` from a dep (catalog down,
   blogs down) skips that section only; an empty-but-successful answer skips it
   too, and the two cases look identical to the shopper and different in the
   console.
4. **Curated order survives the round trip.** `ids` is pinned by
   `array_position` in catalog-svc, and the resolver re-orders anyway
   (`orderByIds`) — a manual "Most Popular" row that silently became "whatever
   the DB returned" would be a CMS lie.
5. **Sparse style keys stay sparse.** `gutter`/`ratio`/`bgColor`/`maxItems`
   reach the block only when the admin set them; `undefined` is never written as
   `undefined`, because absent is what keeps the CSS-var token fallback alive
   (the same rule `fromCatalog.toCardSettings` follows for cards).

`banner` is refused in the resolver (`sf-061` scope), so no `banner` model can
ever reach the registry — the registry's `default` branch is a compile-time
statement, not a runtime fallback.

## 1. Look per state (normative)

### 1.1 HeroSection (v2 — one slide, CMS-resolved)

Text panel + image panel on the full-bleed shell (`padding-inline
var(--sf-page-pad)`, ≤50px gutter — no page `max-width`; the text column may
hold its own measure). Desktop is two columns; below 768 px the panels stack
text-first and the column order never changes.

| State | Look |
|---|---|
| default (`align="left"`) | text panel left, image panel right, `--color-surface` fill |
| `align="center"` | text panel centred, image panel below full width; CTAs centred |
| no image | single column — text panel takes the grid, no reserved media box |
| no CTAs (`ctas: []`) | no CTA row at all (never an empty flex row) |
| `height="viewport"` | `min-height: min(88vh, 820px)` — a CMS knob, capped so a short slide leaves no wall of colour |
| `bgColor` / `textColor` set | `--hero-bg` / `--hero-text` on the section root; absent keeps the token |
| hover / focus-visible on a CTA | shared ring; `--color-ink` fill, `--color-surface` label |

Eyebrow is 12 px small caps in `--text-muted`; title is `<h1>` (it *is* the page
header on `/`); body is 16 px `--color-ink` at the muted tone. Image is a plain
`<img>` (LCP `eager`, carousel followers `lazy`) inside a
`--color-accent-soft` backing box — no `next/image`, matching the `ProductCard`
precedent for arbitrary admin hosts. `data-height` is the state hook; the block
is a pure painter and holds no state.

### 1.2 HeroCarousel (client island — only when a hero has >1 slide)

`.sf-slideshow` renders **one `HeroSection` per slide** and owns nothing but the
index, so the paint contract stays in one stylesheet block and the page keeps
exactly one visible `<h1>`.

| State | Look / behaviour |
|---|---|
| inactive slide | `hidden` attribute — out of layout *and* the a11y tree, no second class vocabulary |
| slide change | `sf-slide-in` fade (`--slideshow-fade`, 260 ms); decoration only |
| hover / focus / hidden tab | auto-advance stops (`HERO_SLIDE_MS` 6000 ms timer skips ticks) |
| `prefers-reduced-motion: reduce` | timer never fires, fade off — the dots stay, because navigation is not motion |
| dots | `role="tablist"` + `role="tab"[aria-selected]`, label "Slide n of m" |
| first paint | slide 1 `eager` (LCP), the rest `lazy` — no paying for a photo nobody has seen |

### 1.3 ProductCollectionSection (`featured_products`)

The listing's own `ProductGridIsland` inside `.sf-collection` — one client
boundary, so quick-add behaves identically here and on `/products`.

| State | Look |
|---|---|
| `layout: "grid"` | the shared `.sf-grid` responsive columns |
| `layout: "carousel"` | same cells as a native scroll row: `overflow-x: auto`, `scroll-snap-type: x mandatory`, `--collection-cell-w` (260 px) — a row you can actually scroll, no JS carousel |
| `gutter` set | `--grid-gap` in px (a value the stylesheet can still theme, not a class) |
| section card knobs | merged **under** the product's `cardSettings` (precedence flat prop → styleConfig → product → theme), so "the section sets the ratio, the product may disagree" is literal |
| no cards resolved | the resolver skips the section — no empty grid, no skeleton |

### 1.4 CategoryShowcaseSection

Tiles are links (`/products?category=<slug>` — routing.md §1), not pictures with
a label. 2 columns on phones, `--showcase-cols` (3) from 640 px.

| State | Look |
|---|---|
| `showPhotos: true` + a category image | 4/3 media box above the name |
| tile with no image | name-only tile inside the same box (never a grey placeholder standing in for art) |
| `showPhotos: false` | every tile keeps its size and centres its name (`--showcase-nameonly-h` 88 px) — the admin asked for less artwork, not a broken layout |

### 1.5 BrandStripSection (the logo row, optionally a marquee)

Server-rendered; motion is CSS alone. The track is the same cells painted twice
and the stylesheet translates `-50%`, so one loop is exactly one copy wide.

| State | Look |
|---|---|
| `motion: "static"` | one track, `flex-wrap: wrap`, no duplicate cells |
| `motion: "marquee"` | `flex-wrap: nowrap; width: max-content; animation: sf-marquee var(--marquee-duration) linear infinite` |
| `direction: "right"` | `animation-direction: reverse` — one keyframe, no second animation |
| `pauseOnHover` (`data-pause="true"`) | `animation-play-state: paused` on `:hover` **and** `:focus-within` |
| reduced motion | `animation: none`, track wraps, and the `[aria-hidden="true"]` loop copy is `display: none` — every brand paints exactly once |
| logo present | `<img class="sf-strip__logo">` with the brand name as `alt` |
| logo absent | `.sf-strip__wordmark` — a logoless brand is never an empty cell |
| `items[].label` present | `.sf-strip__label` beside the logo, `data-named="true"` spacing it (the admin's per-brand choice, not a global toggle) |

Duration is computed in `lib/sections/marquee.ts`:
`cells × (cell + gap) ÷ speed(px/s)`, clamped to 4–240 s, with the strip's
metrics (180 + 32) and the quote row's (340 + 20) stated as constants mirrored by
the stylesheet's fallbacks — a block inventing its own constant would drift from
the CSS silently.

### 1.6 TestimonialSection

Every row is a CMS `testimonial.items[]` entry: quote, name, optional
role/avatar/rating/verified/date. Nothing is synthesised — no fake average, no
star the CMS did not say.

| State | Look |
|---|---|
| `layout: "grid"` | `.sf-testimonials__grid`, 1 column on phones, `--quote-cols` (3) from 640 px |
| `layout: "marquee"` | the strip's mechanism reused: duplicated `aria-hidden` track, same `sf-marquee` keyframes, same pause and reduced-motion rules |
| `rating` 1..5 | five `.sf-stars__star` cells with `data-on`, wrapped in `role="img" aria-label="Rated n out of 5"`; out of range paints no star row |
| `verified: true` | `.sf-pill` "Verified" |
| `date` | `formatMonthYear` → `<time datetime>` ("Nov 2026"); an unparseable date renders nothing, never "Invalid Date" |
| no rating / no role / no avatar | the element is absent, not empty |

### 1.7 BlogTeaserSection

Cards only — the post body belongs to `/blog/[slug]` (sf-063). Date, cover,
title, excerpt, and a real link; an excerpt the CMS did not write is not invented
here, and a coverless post is a text card, not a grey box.

### 1.8 SectionRenderer

`models.map` + a `switch` on `model.type` (a table of components would need a
cast per row, and a cast in the one file that dispatches every CMS feature is
where a wrong type hides). `key` is the section key. Order is the resolver's
order, untouched. An empty model list renders nothing at all.

## 2. Customizable fields (CMS knob → var → default)

| Type | Knob (contracts 1.12.0) | Reaches CSS as | Resolver default |
|---|---|---|---|
| `hero` | `height` | `data-height` | `"auto"` |
| `hero` | `bgColor`, per-slide `bgColor`/`textColor` | `--hero-bg` / `--hero-text` (slide outranks section) | absent |
| `hero` | `ratio` / `customRatio` | `--hero-ratio` | `HERO_DEFAULT_RATIO` = `"4 / 3"` (CSS-space, colon-free) |
| `hero` | `ctas` (max 3, blank text/href dropped) | `Button` flat props | variant by index: primary, light, ghost-ink |
| `featured_products` | `content.source` `"manual"`/`"newest"` | — | manual when `productIds` present, else newest |
| `featured_products` | `maxItems` / `content.layout` / `gutter` / `ratio` / `blendMode` / `bgColor` | `cards.slice`, `data-layout`, `--grid-gap`, `cardOverrides`, `--section-bg` | 8, `"grid"`, absent, absent, absent, absent |
| `category_showcase` | `categoryIds` / `maxItems` / `showPhotos` / `gutter` / `bgColor` | order pin, slice, `data-photos`, `--grid-gap`, `--section-bg` | active-first 12, `true` |
| `brand_strip` | `items[{brandId,label}]` (wins) / `brandIds` / `maxItems` / `motion` / `speed` / `direction` / `pauseOnHover` / `bgColor` | order + `data-named`, slice, `data-motion`/`data-direction`/`data-pause`, `--marquee-duration`, `--section-bg` | 12, `"static"`, 60 px/s, `"left"`, `true` |
| `testimonial` | `items[]` / `maxItems` / `layout` / `speed` / `pauseOnHover` / `bgColor` | slice, `data-layout`/`data-pause`, `--marquee-duration`, `--section-bg` | 12, `"grid"`, 60, `true` |
| `blog_teaser` | `postIds` / `count` / `maxItems` / `gutter` / `bgColor` | order pin, slice (≤12), `--grid-gap`, `--section-bg` | 3 |

`DEFAULT_HERO` is gone: there is no built-in home copy, so an empty CMS is an
empty page (§3), not a scaffold.

## 3. Degradation faces (the `/` route's three states)

| Condition | Face |
|---|---|
| `getSections` → `null` (cms-svc unreachable) | 200 + `.sf-degraded`: "The shop is up, the content service is not" and a real `Browse products → /products` link |
| sections answered, every one skipped | `.sf-degraded`: "Nothing is published on the home page yet" + the same link |
| sections resolved | `<SectionRenderer>` and nothing else — no page-level wrapper copy |

Both degraded faces are one section, no hero, no strip: honest absence, never a
placeholder that looks like content.

## 4. How to change (scopes — where a value lives)

| Value | Home | Override |
|---|---|---|
| Section list, order, copy, active flag | cms-svc `sections` rows (`pageKey: "homepage"`) | admin API (`PATCH /cms/admin/sections/…`), never a deploy |
| CTA cap, ratio fallback, knob defaults, skip rules | `lib/sections/resolveSections.ts` + `lib/sections/hero.ts` | per-instance props on the block (showcase routes only) |
| Marquee speed arithmetic and cell metrics | `lib/sections/marquee.ts` | `--strip-cell` / `--quote-cell` / `--grid-gap` theme vars (the constants must move with them) |
| Paint (fills, type scale, easing, motion) | `.sf-*` block in `app/globals.css` + house tokens | theme tokens and the admin's `bgColor` — no per-section palette beyond that |
| Multi-slide navigation | `components/sections/HeroCarousel.tsx` | — (the painter stays stateless) |
| Image host | the CMS row's `image`/`logoUrl`/`coverUrl` | — (`<img>` accepts arbitrary hosts) |

## 5. Global rules (inherited)

1. **`props → JSX`.** No block fetches. The route resolves, the registry
   dispatches, the block paints.
2. **State reaches CSS only through `data-*`** (`data-motion`, `data-direction`,
   `data-pause`, `data-photos`, `data-named`, `data-layout`, `data-height`,
   `data-on`, `aria-selected`, `hidden`). The markup sets attrs; the stylesheet
   does the painting.
3. **Paint only through `var()` over a token** — a hardcoded hex in this
   vocabulary is a bug, and `sections-style.test.ts` fails on it. Per-section
   admin values arrive as inline custom properties (`--section-bg`,
   `--grid-gap`, `--marquee-duration`, `--hero-*`), never as inline colours.
4. **No page-level `max-width`.** The shell owns `--sf-page-pad`
   (`clamp(16px, 4vw, 50px)`); sections pad themselves only vertically
   (`--section-pad-x: 0`), or the gutter doubles. A `ch` measure on a *text*
   element is the one allowed exception (`design-system/storefront.md` §4).
5. **Motion always has a static face**: marquee tracks pause and stop under
   reduced motion, the slideshow timer is suppressed, the fade is dropped.
   Navigation survives; animation does not.
6. **Sparse props.** `{ x: undefined }` is a lie the CSS can no longer correct;
   keys the admin did not set stay absent.
7. **Trio tests per block** — contract (behaviour), style (paint through vars),
   and the resolver/lib unit that owns the rule.

## 6. Apply-to-all (the per-type bulk switch)

The CMS section row *is* the switch: one `PUT` per row changes one instance, and
the seed/panel's "apply to all" writes the same field to every row of that type.
There is no storefront-side bulk flag — a section type that needs one gets it in
contracts first, because a knob the contract cannot express cannot be audited.

---

## Appendix — file references

- Contracts: `@ecom/contracts` 1.12.0 `section.ts`, `section-content.ts`,
  `section-settings.ts`, `section-catalog.ts`, `footer.ts`
- Models: `lib/sections/viewModels.ts` · Resolver:
  `lib/sections/resolveSections.ts` · `test/lib/sections/resolveSections.test.ts`
- Helpers: `lib/sections/hero.ts` · `lib/sections/marquee.ts` ·
  `lib/sections/present.ts` (+ their `test/lib/sections/*` units)
- Blocks: `components/sections/{HeroSection,HeroCarousel,toHeroFields,ProductCollectionSection,CategoryShowcaseSection,BrandStripSection,TestimonialSection,BlogTeaserSection,SectionRenderer,index}.ts(x)`
- Tests: `test/components/{hero,hero-carousel,product-collection,showcase-journal,brand-strip,testimonial,section-renderer}.test.tsx`,
  `test/components/{hero,sections}-style.test.ts`, `test/app/(shop)/home.test.tsx`
- Paint: `app/globals.css` — the `CMS home sections` block (`.sf-section`,
  `.sf-hero*`, `.sf-slideshow*`, `.sf-collection`, `.sf-showcase*`,
  `.sf-strip*`, `.sf-testimonials*`, `.sf-quote*`, `.sf-stars*`, `.sf-blog*`,
  `.sf-degraded*`) + `@keyframes sf-marquee` / `sf-slide-in`
- Data: `lib/cms/client.ts` (`getSections`), `lib/catalog/client.ts`
  (`listProducts` with `ids`, `listBrands`), `lib/cms/tags.ts`
  (`cms:sections:{pageKey}`)
- Deferred: `banner` (sf-061), footer shell + blog/legal routes (sf-062/sf-063),
  admin panel UI (adm-001 — wiring it is an API-only change by design)
