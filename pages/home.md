# Home — `pages/home.md`

> Storefront Homepage Plan
> Status: Draft | Last Updated: 2026-08-21
> Parent: `docs/0.Project-Overview.md` | `docs/5.Features.md` §A1 | `docs/6.Admin-Panel.md` §3.7/§4/§5/§6
> Route: `frontend/storefront/app/(shop)/page.tsx` | CMS `pageKey=homepage`

---

## 1. Purpose & Scope

The homepage is the storefront entry point. It is fully CMS-driven: the set of sections, their order, and their content are stored in `cms_sections` (Mongo) and rendered by the storefront by iterating the sections array for `pageKey=homepage`. No section is hardcoded except the shell (navbar, footer, announcement).

This file owns the **homepage layout, section inventory, and the hero section spec** (including all customization controls requested). Acceptance criteria for homepage features live in `5.Features.md` §A1; this file adds layout, component breakdown, data model, and admin editing details. It does not duplicate storage or API contracts (see `3.Database-Schema.md` §4.1, `4.API-Design.md` §3.5).

---

## 2. Page Layout (Wireframe, Text)

```
Navbar (sticky)
Announcement bar [optional, dismissible]
Hero               ← §3 (split, slides, per-slide theming)
Banner             ← full-width promo strip (optional, CMS order controls it)
Featured products  ← carousel/grid of 4-8 products (CMS picker)
Category showcase  ← 3-6 category cards (image + name → /products?category=)
Brand strip        ← logo row (optional)
Blog teaser        ← 3 latest posts (optional)
Testimonials       ← [optional, future]
Footer
```

- Sections render in `cms_sections.sort_order` order. Admin reorders via drag-drop (see `6.Admin-Panel.md` §7.2). Empty state: if a section has no content (e.g. no featured products selected), it is skipped, not rendered as an empty block.
- Page is a server component. It fetches `GET /api/v1/cms/sections?pageKey=homepage` (cached via Redis `cms:section:{key}`, invalidated by `cms.updated`) and `GET /api/v1/cms/settings/global` for theme defaults. No client fetch on first paint.

---

## 3. Hero Section — Detailed Spec

The hero is the first section on the homepage and the primary conversion surface. It follows the split-static pattern: text on one side, image on the other, rendered as a two-column grid whose proportion is configurable.

### 3.1 Structure

- Desktop: two columns — text panel + image panel. Proportion controlled by `split` (see §3.4).
- Mobile (<768px): stacked — text panel on top, image panel below. Stack order does not change with `flip`; `flip` only affects desktop column order.
- No autoplay, no auto-rotation, no video, no parallax. Simple 2D, flat colors, system font.

### 3.2 Slides

The hero holds an ordered array of slides. The admin can add, remove, duplicate, and reorder slides.

- **1 slide:** rendered as a static block. No navigation chrome (no dots, no arrows). This is the default and the simplest case.
- **>1 slide:** rendered as a manual slider. No autoplay. Navigation: dots (one per slide) centered below the hero plus prev/next arrow buttons on the left/right edges. Dots and arrows are always visible when >1 slide; they do not auto-hide. Keyboard: left/right arrows switch slides; focus stays on the hero.

Slide object shape (stored in `cms_sections.content.slides[]` for `type=hero`; Zod-validated via `shared/src/schemas/cta.schema.ts`):

```json
{
  "id": "slide_01",
  "eyebrow": "New Collection",
  "headline": "Built for everyday",
  "subcopy": "Simple, durable pieces that go with everything.",
  "image": "s3://.../hero-01.jpg",
  "imageAlt": "Model wearing overshirt",
  "bgColor": "#ffffff",
  "textColor": "#111111",
  "imageBgColor": "#f2f2f2",
  "ctas": [
    { "id": "cta_01", "text": "Shop Now", "link": "/products", "bg": "#111111", "textColor": "#ffffff", "borderColor": "#111111", "borderWidth": 1, "borderRadius": 6 }
  ],
  "split": "50-50",
  "flip": false,
  "ratio": "4:3"
}
```

`ctas` is `Cta[0..3]` — `0` = no CTA row, `1-3` = rendered as `flex flex-wrap gap-3`; `length > 3` rejected by `z.array(ctaSchema).max(3)` (400 `VALIDATION_FAILED`). Legacy flat `ctaText/ctaLink/ctaBg` docs are auto-migrated to `ctas[0]` in `lib/cms/resolve.ts`.

- `id` is a short random string, stable across reorders. Used as React key and for drag-drop.
- Any theming field absent → falls through to the next level (see §3.5).

### 3.3 Per-Slide Theming (Customization Controls)

Each slide exposes these controls in the admin editor. All are optional per slide; absence means inherit.

| Field | Control | Allowed values | Default when absent |
|---|---|---|---|
| `bgColor` | color picker + hex input | any hex | `theme.colors.sectionBg` or `#ffffff` |
| `textColor` | color picker + hex input | any hex | `#111111` |
| `image` / `imageAlt` | media picker + alt text input | S3 URL + string | required — slide invalid without image |
| `imageBgColor` | color picker + hex input | any hex | `bgColor` (so the supporting div matches the slide) |
| `headline`, `subcopy`, `eyebrow` | text inputs / textarea | string | required: `headline` (ctas optional) |
| `ctas` | repeater (0-3) — per CTA: `text` (text input, required), `link` (link input, required, internal path `/products`, `/products?category=...`, `/products/[slug]`), `bg` / `textColor` / `borderColor` (color picker + hex), `borderWidth` (0-4 px), `borderRadius` (0-24 px slider) | `Cta[0..3]` | `0` = no CTA row; each present CTA requires `text + link`; absent style fields inherit per §3.5 (`bg→theme.colors.buttonBg`, `textColor→theme.colors.buttonText`, `borderColor→bg`, `borderRadius→theme.borderRadius.button`); `length > 3` blocked by `z.array(ctaSchema).max(3)`; Add CTA disabled at 3 |

Button preview in the admin form updates live as the picker changes (per CTA).

### 3.4 Layout Controls

| Control | Values | Effect |
|---|---|---|
| `split` | `50-50`, `60-40`, `40-60`, `70-30`, `30-70` | Grid proportion text vs image. `60-40` = text 60%, image 40%. Implemented as `grid-template-columns` (e.g. `60% 40%`). |
| `flip` | `true` / `false` | Mirror the two panels on desktop. `false` = text left, image right. `true` = image left, text right. Implemented by swapping `order` / grid placement. No effect on mobile stack. |
| `ratio` | `1:1`, `4:3`, `3:4`, `16:9` | Image aspect ratio. Applied as `aspect-ratio` on the image wrapper. |
| `imageBgColor` | hex | Color of the supporting div behind the image. The image panel is a relative container: an absolutely positioned background div (inset 16px on desktop, inset 8px on mobile) filled with `imageBgColor`, with the `<img>` on top, slightly offset to create a layered card effect. If `imageBgColor` equals `bgColor`, the effect is visually flat (no visible backing). |

All layout controls are per slide, so slide 1 can be `60-40` non-flipped while slide 2 is `40-60` flipped with a different backing color.

### 3.5 Inheritance (Precedence)

```
effective value = slide field ?? section settings ?? global theme ?? builtin default
```

- Slide field present → wins. Absent → section-level `settings` (if the admin sets a default for the hero section) → global `cms_settings.theme` → builtin default from the table in §3.3.
- "Reset to global/inherit" in the admin deletes the key from the slide object; it never writes `null`.

### 3.6 Storefront Component

```
components/sections/HeroSection.tsx
  props: { slides: Slide[] }
  - 1 slide: <section> with grid, no state, no JS
  - >1 slide: client component (lightweight) with useState for activeIndex,
    dots + arrow buttons, no interval, no autoplay
```

- The text panel: eyebrow (small caps, 12px, opacity 0.7), headline (`<h1>`, 32px desktop / 24px mobile, `textColor`), subcopy (16px, `textColor` at 0.8), CTA row — `0-3` buttons in `flex flex-wrap gap-3`; each button inline style from `ctas[i].bg/textColor/borderColor/borderWidth/borderRadius` via `lib/cms/resolve.ts`; `ctas: []` renders no CTA row.
- The image panel: relative wrapper with `ratio`; background div with `imageBgColor`; `<img>` with `object-cover`, `width`/`height` from CMS, `loading="eager"` for the first slide (LCP), `loading="lazy"` for other slides.
- Split is applied via inline `gridTemplateColumns` so it is per slide and does not require CSS classes per variant.
- Accessibility: section has `aria-label="Hero"`, dots have `aria-label="Go to slide N"`, arrows have `aria-label="Previous/Next slide"`, image has `alt` from `imageAlt`.
- Performance: no JS when 1 slide; when >1 slide, JS is <2 KB (state + handlers). No carousel library.

### 3.7 Admin Editor

Route: `frontend/admin/app/cms/sections` — hero type selected.

- Left: slide list — rows show thumbnail + headline truncated + drag handle. Actions per row: duplicate, delete (confirm). "Add slide" appends a new slide with defaults (headline "New slide", placeholder image). Drag-drop reorders and writes the new order on drop (optimistic, revert on failure).
- Right: slide form — collapsible groups: Content (eyebrow/headline/subcopy/image picker/alt), Appearance (bgColor, textColor, imageBgColor), CTAs (0-3) — repeater: each CTA row shows `text` truncated + color swatch + drag handle; expand row to edit `text` (required), `link` (required, internal path), `bg`/`textColor`/`borderColor` (color pickers), `borderWidth` (0-4), `borderRadius` (0-24 slider); Add CTA disabled at 3 with tooltip "Max 3 buttons per slide"; duplicate/delete (confirm) per CTA; drag reorder within slide; per-CTA live preview swatch, Layout (split select, flip toggle, ratio select).
- Top: live preview pane — renders the real `HeroSection` against local (unsaved) state via a preview endpoint (`?preview=1`) so Redis cache is not polluted (see `6.Admin-Panel.md` §7.1). Preview has a slide switcher (dots) to inspect each slide and renders the `ctas` row per slide.
- Validation: save blocked if any slide missing `headline` or `image`, or if `ctas.length > 3`, or if any `ctas[i].text` empty or `link` not an internal path; Zod (`z.array(ctaSchema).max(3)`) errors shown inline per CTA field; `ctas: []` is valid (no CTA row).
- Save: `PUT /api/v1/cms/sections/:id` with the full `slides` array; on success publishes `cms.updated` and invalidates `cms:section:{key}`.

### 3.8 Settings Registry Entries (addition to `6.Admin-Panel.md` §4)

| Setting key | Type | Allowed values | Scope | Default | Component |
|---|---|---|---|---|---|
| `hero.slides[].bgColor` | color hex | hex | S (per slide) | `theme.colors.sectionBg` | Hero slide |
| `hero.slides[].textColor` | color hex | hex | S (per slide) | `#111111` | Hero slide |
| `hero.slides[].imageBgColor` | color hex | hex | S (per slide) | `bgColor` | Hero image backing div |
| `hero.slides[].ctas` | array(Cta) | `Cta[0..3]`, `z.array(ctaSchema).max(3)` | S (per slide) | `[]` | Hero slide CTAs (0 = no CTA row, intrinsic product-card hover buttons not counted) |
| `hero.slides[].ctas[].text` | string | 1-50 | S (per CTA) | — | CTA label (required per CTA) |
| `hero.slides[].ctas[].link` | string | internal path (`/products`, `/products?category=...`) | S (per CTA) | — | CTA link (required per CTA, Zod `refine(isInternalPath)`) |
| `hero.slides[].ctas[].bg` | color hex | hex | S (per CTA) | `theme.colors.buttonBg` | CTA background |
| `hero.slides[].ctas[].textColor` | color hex | hex | S (per CTA) | `theme.colors.buttonText` | CTA text color |
| `hero.slides[].ctas[].borderColor` | color hex | hex | S (per CTA) | `ctas[].bg` | CTA border color |
| `hero.slides[].ctas[].borderWidth` | integer px | 0–4 | S (per CTA) | 1 | CTA border width |
| `hero.slides[].ctas[].borderRadius` | integer px | 0–24 | S (per CTA) | `theme.borderRadius.button` | CTA border radius |
| `banner.ctas` | array(Cta) | `Cta[0..3]`, `z.array(ctaSchema).max(3)` | S | `[]` | Banner CTAs (0-3, same Cta shape) |
| `hero.slides[].split` | string | `50-50`/`60-40`/`40-60`/`70-30`/`30-70` | S (per slide) | `50-50` | Hero layout |
| `hero.slides[].flip` | boolean | true/false | S (per slide) | `false` | Hero layout |
| `hero.slides[].ratio` | string | `1:1`/`4:3`/`3:4`/`16:9` | S (per slide) | `4:3` | Hero image |

### 3.9 Behavior & States

- Loading: server component streams; hero renders on first paint (no skeleton needed — single image is the LCP).
- Empty: if `slides` is empty or the homepage has no hero section, the hero is skipped (no placeholder).
- Error: if an image fails to load, `alt` text is shown in the image panel's backing div; layout does not collapse.
- Single slide: static, no dots/arrows, no JS.
- Multiple slides: manual navigation only; active dot is filled (`bgColor` = `textColor`), inactive dots are `textColor` at 0.3; arrows are simple chevrons in `textColor` on transparent background with a subtle hover background.

---

## 4. Other Homepage Sections (Summary)

These sections follow the same CMS pattern as the hero (each is a `cms_sections` document with `type` and `content` + `settings` + `sort_order`). They are not detailed here beyond inventory; each will get its own subsection in future page plans if customization is needed. For now they use the generic section renderer and the global/section override model (`6.Admin-Panel.md` §5).

| Section type | Content fields | Notes |
|---|---|---|
| `banner` | `image, title, ctas[0..3] (each {text, link, bg, textColor, border*}, max 3 via Zod), bgColor` | Full-width strip, centered text |
| `featured_products` | `productIds[]` (picker, ordered), `title` | Renders product cards (uses `theme.borderRadius.card`, `photoSettings.ratio`) |
| `category_showcase` | `categoryIds[]`, `title` | Category cards → `/products?category=` |
| `brand_strip` | `brandIds[]` | Logo row, grayscale logos |
| `blog_teaser` | `postIds[]` or auto latest 3 | Post cards |

All are optional and ordered by `sort_order`. The generic section renderer applies `settings.gutter`, `settings.maxItems`, and the Product > Section > Global override for `ratio`/`blendMode` where relevant.

---

## 5. Responsive Rules

- Breakpoint: 768px (`md`).
- Hero: grid on desktop, stack on mobile (text on top). Split and flip have no effect on mobile. Image ratio is preserved on both. CTAs stack vertically full-width on mobile (each block button), wrap as `flex flex-wrap gap-3` on desktop.
- Other sections: featured/category grids go 4-col → 2-col → 1-col; brand strip wraps; banner text stays centered.

---

## 6. Data Fetching & Pipeline

```
Admin save hero → cms-svc writes Mongo (bumps version) → publishes cms.updated
  → storefront invalidates cms:section:homepage (Redis) → next SSR: Redis miss → Mongo read → cache (TTL 5 min)
```

- Homepage is ISR with `revalidate` on `cms.updated` (stale-while-revalidate 1 min). Preview mode bypasses Redis.

---

## 7. Acceptance Checklist

- [ ] Homepage renders sections in `sort_order` order; missing sections are skipped
- [ ] Hero with 1 slide renders as static split with no dots/arrows and no JS
- [ ] Hero with >1 slide shows dots + arrows, manual navigation only, no autoplay, keyboard left/right works
- [ ] Per-slide bgColor, textColor, image, headline, subcopy, and 0-3 `ctas[]` (each `bg/text/borderColor/borderWidth/borderRadius`) apply correctly; absent fields inherit per §3.5; `ctas.length > 3` rejected with `400 VALIDATION_FAILED`, `ctas: []` renders no CTA row
- [ ] Split `50-50`/`60-40`/`40-60`/`70-30`/`30-70` produces the correct grid proportion on desktop and stacks correctly on mobile
- [ ] Flip mirrors text/image on desktop only
- [ ] Image backing div uses `imageBgColor` and is visible as a layered offset
- [ ] Admin can add/remove/duplicate/reorder slides; drag-drop persists order; delete requires confirm
- [ ] Admin live preview shows each slide with the split/flip/colors applied before save
- [ ] Save publishes `cms.updated` and storefront reflects changes within cache TTL

---

## 8. Related Documents

- `docs/0.Project-Overview.md` §8 — homepage feature overview
- `docs/1.Architecture.md` §7 — `cms.updated` contract
- `docs/3.Database-Schema.md` §4.1 — `cms_sections` storage
- `docs/4.API-Design.md` §3.5 — `GET /cms/sections?pageKey=homepage`, `PUT /cms/sections/:id`
- `docs/5.Features.md` §A1 — homepage acceptance criteria
- `docs/6.Admin-Panel.md` §3.7/§4/§5/§6/§7 — CMS sections, settings registry, override model, pipeline, editor patterns
- `AGENTS.md` §5 — frontend conventions (components/sections, lib/cms resolution)
