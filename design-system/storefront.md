# Storefront Design System — Oceanic Blue v1.0

> Platform: Next.js 16 (App Router) + React 19 + Tailwind CSS 4 + TypeScript 5
> Theme: Oceanic Blue — light gradient hero, flat solid buttons, wave hover
> Status: Active | Version 1.0 | Date: 2026-08-24
> Parent: `docs/6.Admin-Panel.md` §4, `docs/pages/home.md` §3, `docs/2.Tech-Stack.md` §4
> Implements: `E:\E-Commerce\index.html` (source of truth until globals.css is wired) → `frontend/storefront/src/app/globals.css` + `layout.tsx` + `components/*`
> Figma: (add file URL when created)

---

## 1. Design Principles

| Principle | Statement | Rationale |
|---|---|---|
| **Product first** | The product (image, price, name) is primary; UI is the frame. | Customer comes to buy, not to admire chrome. Every token serves product legibility. |
| **Light & airy** | White surfaces, ocean accents, generous whitespace, `480px` hero deck on `1280px` grid. | Bright storefront converts better for apparel; dark/heavy chrome hides product. |
| **Gradient canvas, solid actions** | Hero background is a soft ocean gradient; buttons are **solid fills** (no gradients). | The canvas sets mood; the CTA stays the highest-contrast, most predictable element on the page. |
| **Wave interaction** | On hover a wave rises inside the button and swaps it to the secondary color. | One signature affordance, flat 2D, no shadows-on-color — feels alive without animation libraries. |
| **One token source** | Single CMS `cms_settings.theme` → `:root` CSS vars → Tailwind `@theme inline` → per-slide `style` via `lib/cms/resolve.ts`. | No ad-hoc hex in `components/`; `P>S>G` inheritance is deterministic. |
| **Constraint drives consistency** | Hard cap `3 CTAs per slide` (`z.array(ctaSchema).max(3)`), `480px` hero base fixed, no autoplay/parallax. | Freedom without guardrails becomes clutter; engineering principles keep the storefront shoppable. |

---

## 2. Typography

Fonts: **Fraunces** (variable, opsz 9–144) for display/headings + **Outfit** for body/UI. Never Outfit for display; never Fraunces below 24px. Weights used: `Fraunces 500/600/700`, `Outfit 400/500/600/700`. Loaded via `next/font` (variable, `display=swap`, `subset latin`) — prototype uses `@import` for demo only.

| Category | Font | Weight | Size | Line-height | Letter-spacing | Usage |
|---|---|---|---|---|---|---|
| **Display** | Fraunces | 700 | 48 (clamp 28→48) | 1.05 | -0.025em | Hero `headline` (desktop). `max-width 12ch` |
| **H1** | Fraunces | 600 | 36 | 1.10 | -0.02em | PDP name |
| **H2** | Fraunces | 600 | 24 | 1.20 | — | Section titles (Featured, Category) |
| **H3 / Card title** | Outfit | 600 | 14 | 1.30 | — | Card titles, panel heads |
| **Body Large** | Outfit | 400 | 17 (clamp 15→17) | 1.60 | 0 | Hero `subcopy` |
| **Body Default** | Outfit | 400 | 16 | 1.50 | 0 | Product description, blog body |
| **Body Small** | Outfit | 400 | 14 | 1.50 | 0 | Card meta, filters |
| **Label Large** | Outfit | 500 | 14 | 1.20 | 0.01em | Form labels, navlinks |
| **Label Small** | Outfit | 600 | 12 | 1.20 | 0.12em uppercase | Eyebrow `NEW COLLECTION`, panel headers |
| **Caption** | Outfit | 500 | 13 | 1.40 | 0 | Helper text, prices, hints |
| **CTA** | Outfit | 600 | 15 | 1.00 | 0.01em | `ctas[].text` pill buttons |

Rules: `headline` always `Fraunces 700` at `clamp 28-48px`; `eyebrow` always `12px 600 uppercase 0.12em` in `text.muted`; price numbers use `600` not body `400`; currency format `$12.00` (USD v1).

---

## 3. Color System — Oceanic Blue (Detailed: Which Color Where)

All colors are emitted as `:root` vars (`--color-*`, ocean ramp) and consumed via Tailwind `@theme inline`. Never use a primitive hex directly in `components/` — use a semantic token.

### 3.1 Primitives — Raw Palette (Do Not Use Directly)

**Ocean ramp:**

| Primitive | Hex | Note |
|---|---|---|
| `ocean-50` | `#E6F7FB` | foam — hover wash, light button bg |
| `ocean-100` | `#CAF0F8` | image placeholder, gradient end |
| `ocean-200` | `#ADE8F4` | light accent |
| `ocean-300` | `#90E0EF` | foam text on dark |
| `ocean-400` | `#48CAE4` | bright cyan — gradient end |
| `ocean-500` | `#00B4D8` | vivid |
| `ocean-600` | `#0096C7` | mid |
| `ocean-700★` | `#0077B6` | **primary** — CTA, links, focus |
| `ocean-800` | `#023E8A` | hover / accent-hover |
| `ocean-900` | `#03045E` | abyss — gradients only |

**Neutrals:** Ink `#0A2540` · Mist `#F5FAFC` · Surface `#FFFFFF` · Border `#DCE8EE` · Muted `#5B7286`

**Brand gradients (decorative only — never on buttons):**
- Ocean bars: `linear-gradient(90deg,#0077B6,#48CAE4)` (700→400)
- Deep: `linear-gradient(90deg,#023E8A,#0096C7)` (800→600)
- Hero canvas: `linear-gradient(90deg,#F5FAFC 0%,#E6F7FB 48%,#CAF0F8 100%)`

> Hero-carousel slide background gradients are documented in **§7.7** — they are slide-level styling, not primitives or themes.

### 3.2 Semantic Tokens — Meaning Layer (Alias Primitives → Where Used)

| Semantic Token (`--color-*`) | Value | Where Used — Storefront (Exact) | Contrast |
|---|---|---|---|
| `--color-navbar-bg` | `#FFFFFF` | Navbar background (sticky, `height 64px`, `border-bottom 1px solid --border`) | — |
| `--color-navbar-text` | `#0A2540` | `.brand` (20px 700), `.navlinks` (14px 500), search text | 15.9:1 on white — AAA |
| `--color-ink` | `#0A2540` | headline, body text, announcement bar bg, dots/arrows `currentColor` | 15.9:1 |
| `--color-accent` | `#0077B6` | `.brand span`, `navlinks a:hover`, `icon-btn/slide-arrow/mini:hover`, `slide-row.active` border, `.pill` bg, `cta:focus-visible` outline, input focus border | 4.6:1 on white — **AA, usable as text** |
| `--color-accent-hover` | `#023E8A` | accent hover/active | 10.9:1 |
| `--color-accent-50` | `#E6F7FB` | `.add-slide:hover`, `.slide-arrow:hover` wash | — |
| `--color-button-bg` | `#0077B6` | **Primary CTA** `ctas[0].bg` fallback, banner CTA | 4.6:1 AA |
| `--color-button-text` | `#FFFFFF` | Primary CTA text | on `buttonBg` 4.6:1 AA |
| `--color-button-light-bg` | `#FFFFFF` | Light CTA background | — |
| `--color-button-light-text` | `#0077B6` | Light CTA text + `border-color` | — |
| `--color-section-bg` | `#F5FAFC` | `body` bg, section bg | — |
| `--color-image-bg` | `#CAF0F8` | Hero `imageBgColor` fallback, card `ph` gradient end | — |
| `--color-sale` | `#FF6B4A` | Sale badge `SALE −30%`, sale CTA — **ink `#0A2540` text** (4.6:1 AA); white text FAILS (2.8:1) | — |
| `--color-sale-soft` | `#FFEDE6` | Sale wave bg, sale-soft chips | — |
| `--color-success` (+bg/border) | `#0E9F6E` / `#ECFDF3` / `#ABEFC6` | Order confirmed, in stock, delivered | — |
| `--color-warning` (+bg/border) | `#F79009` / `#FFFAEB` / `#FEDF89` | Low stock, pending, abandoned cart | — |
| `--color-error` (+bg/border) | `#D92D20` / `#FEF3F2` / `#FECDCA` | `COUPON_EXPIRED`, `STOCK_INSUFFICIENT`, `VALIDATION_FAILED` | — |
| `--border` | `#DCE8EE` | All 1px borders, dividers | — |
| `--text-muted` | `#5B7286` | Eyebrow, hints, prices, labels, footer | 4.7:1 on white — AA |
| `--focus-ring` | `#0077B633` | Input focus `0 0 0 3px`, `slide-row.active` ring | — |

**Contrast quick check:** Ink `#0A2540` on card `#FFFFFF` ≈ `15.9:1` AAA; muted `#5B7286` `4.7:1` AA; primary `#0077B6` `4.6:1` AA — **usable as text and button fill** (this replaces the old "accent is badge-only" rule). Sale `#FF6B4A` requires ink text, never white.

### 3.3 Component Tokens — Semantic → Component (Concrete Mapping to Code)

| Component | Token | Semantic | Value | Note |
|---|---|---|---|---|
| **Navbar** | `bg` / `text` / `hover` | `bg.card` / `text.primary` / `text.accent` | `#FFFFFF` / `#0A2540` / `#0077B6` | `height 64px` sticky, search `36px 999px min-300` |
| **Announcement** | `bg` / `text` | `bg.inverse (ink)` / `text.inverse` | `#0A2540` / `#FFFFFF` | `height 36px` |
| **Hero — Slide bg** | fixed gradient | — | `linear-gradient(90deg,#F5FAFC 0%,#E6F7FB 48%,#CAF0F8 100%)` | Per-slide `bgColor`/`bgGradient` demoted to placeholder/future use; text panel colors stay per-slide |
| **Hero — Peek** | `current` / `next` | — | `translate(-50%,-50%) 0deg 1 z3 shadow-lg` / `translate(-47.5%,-48.8%) rotate(2deg) scale(.92) opacity .62 z1` | `480px` fixed, `overflow:visible` |
| **Hero — CTAs 0-3** | `bg`/`text`/`border` | `button.bg/text` or per-CTA | `#0077B6`/`#FFFFFF`/`#0077B6` | `z.array(ctaSchema).max(3)`; `0` = no row; `flex wrap gap 12` |
| **Slide Arrows** | column below CTA | — | `40px` circle, hover `border accent + bg accent-50` | desktop vertical, `<900px` row |
| **Product Card** | `bg`/`border`/`ph` | `bg.card`/`border.default`/gradient | `#FFFFFF` / `#DCE8EE` / `#E6F7FB→#CAF0F8` | `radius 12`, sale badge `#FF6B4A`+ink |
| **Sale Card** | badge | `color.sale + ink` | `#FF6B4A` + `#0A2540` | pill `9999px`, top-left `8px` inset, strike price + coral sale price |
| **Banner / Strip / Blog / Footer** | `bg.card` / `border.default` / `text.muted` | — | `#FFFFFF` / `#DCE8EE` / `#5B7286` | unchanged structure |

---

## 4. Spacing System

Base `4px`: `4 · 8 · 12 · 16 · 20 · 24 · 32 · 56 · 72`. Hero `padding 72px 24px`, `gap 56px`, `min-height 540px`; sections `max-width 1280px`, `padding 28px 24px`; card `bd` `12px`.

---

## 5. Border Radius

`button 8` (CMS 0–24 slider) · `md 10` (logo, slide-row) · `card/section 12` · `peek 14` · `pill 9999` (visual; CMS stores 8) · `circle 9999` (dots, arrows, icon-btn).

---

## 6. Shadows & Motion

| Token | Value |
|---|---|
| `shadow-sm` | `0 1px 2px rgba(10,37,64,.06)` |
| `shadow-md` | `0 4px 16px rgba(10,37,64,.08)` |
| `shadow-lg` | `0 8px 32px rgba(10,37,64,.12), 0 1px 3px rgba(10,37,64,.08)` |
| `focus-ring` | `0 0 0 3px #0077B633` |
| `duration-fast` | `180ms ease` (text fade `is-fading`) |
| `duration-base` | `320ms cubic-bezier(.32,.72,.32,1)` (peek, `peekIn`, `textIn 220ms`) |
| **wave-rise** | `transform .36s cubic-bezier(.32,.72,.32,1)` on `.cta::before` |
| **wave-text** | `color/border-color .16s ease` with **`0.2s` delay** (text swaps only after wave covers) |

`prefers-reduced-motion: reduce` → transitions `none`, wave pinned down, peeks hidden.

---

## 7. Components — Storefront

### 7.1 Button / CTA (`components/ui/Button.tsx`) — 6 solid variants, wave hover

| Variant | Fill | Text | Border | Wave (`--wave-bg` / `--wave-text`) |
|---|---|---|---|---|
| **Primary** | `#0077B6` | `#FFFFFF` | `#0077B6` | `#FFFFFF` / `#0077B6` |
| **Light** | `#FFFFFF` | `#0077B6` | `#0077B6` | `#0077B6` / `#FFFFFF` |
| **Ghost ink** | `#FFFFFF` | `#0A2540` | `#0A2540` | `#0A2540` / `#FFFFFF` |
| **Sale** | `#FF6B4A` | `#0A2540` | `#FF6B4A` | `#FFEDE6` / `#0A2540` |
| **Success** | `#0E9F6E` | `#FFFFFF` | `#0E9F6E` | `#ECFDF3` / `#0E9F6E` |
| **Error** | `#D92D20` | `#FFFFFF` | `#D92D20` | `#FEF3F2` / `#D92D20` |

**Wave rule (`getWaveColors`):** luminance `< 150` → white wave + ocean text; else ocean wave + white text. Wave = `::before` ellipse rising from bottom, `0.36s cubic-bezier(.32,.72,.32,1)`, text/border swap delayed `0.2s`. **Solid fills only — no gradients on buttons.** `min-height 44px`, `padding 14px 28px`, pill `9999px`, focus-visible `2px accent offset 2`, disabled `.5`.

### 7.2 Hero Section (`components/sections/HeroSection.tsx`)

- **Props:** `{ slides: Slide[] }` resolved via `lib/cms/resolve.ts` (`P>S>G`).
- **Background:** fixed light ocean gradient (§3.3) — `slide.bgColor` feeds placeholder fallback only.
- **Layout:** `split` `50-50…30-70` inline `grid-template-columns`; `flip` desktop-only; `<900px` stacks.
- **Peek deck:** `480px` fixed; `len==1` static; `len>=2` `current + next` (no left peek).
- **Motion:** `peekIn 320ms` come-forward; text `is-fading 180ms` + `textIn 220ms`; `isHeroAnimating` lock `460ms`.
- **Nav:** dots `bottom:16px`; `slide-arrows` column below CTA; keyboard `←/→`.
- **Dark variant:** abyss `#0A2540` bg, white ink, foam `#90E0EF` secondary.

### 7.3 Banner — `image, title, ctas[0..3], bgColor`; radius 12, padding 22.

### 7.4 Featured Products — `productIds[]` ordered picker → `ProductCard` grid `4→2→1`.

### 7.5 Product Card — `radius 12`, `ph` gradient `#E6F7FB→#CAF0F8`, title 14/600, price muted, sale badge `#FF6B4A`+ink, strike price + coral sale price.

### 7.6 Gallery / Variant Selector / Cart — `photoSettings` `P>S>G`; `CartLineItem` + `MiniCartDrawer` on `store/cart.ts`.

### 7.7 Hero Carousel — Slide Background Gradients

The hero carousel supports **per-slide background gradients**. These are **slide backgrounds only** — they are not themes, not design-system primitives/tokens, and they never apply outside the hero carousel section. Global tokens (§3.2) are unaffected.

**Rules:**
- The gradient fills the slide's hero-section background only. Primary CTA stays **solid `#0077B6` + white** with wave hover on every slide.
- The accent gradient colors the **eyebrow** and headline `<em>` via `background-clip:text; color:transparent` — nothing else on the slide uses it.
- `ink` / `muted` are that slide's text colors. All inks are **≥ `11:1 AAA`** on their lightest gradient stop.
- Default (no gradient set) = hero canvas `linear-gradient(90deg,#F5FAFC,#E6F7FB 48%,#CAF0F8)`. Direction `135deg` desktop.

| Slide background (135deg) | Accent gradient (eyebrow + `<em>` clip) | Ink | Muted | Suits |
|---|---|---|---|---|
| Warm Sunrise — `#FFF8F0 → #FFEDD5 → #FFE5BF` | `#C08552 → #E85D04` | `#4B2E2B` | `#8C5A3C` | warm linen, white-tee, everyday collections |
| Sage Cloud — `#F6F4E8 → #E5EEE4 → #C0E1D2` | `#4A7C59 → #8FA28A` | `#2D3B2D` | `#5F6B5F` | eco, multicolor racks, nature drops |
| Aurora Lav-Sky — `#F0E9FF → #E0F2FE → #CAF0F8` | `#7C6FF0 → #EC4899` | `#2D2A4A` | `#5B7286` | editorial, new-collection, campaign slides |

Live reference: canvas **Frames 10–12** in `index.html` (one live carousel per gradient).

---

## 8. Layout Patterns

Shell: `Announcement 36px` → `Navbar 64px sticky` → `Hero min-height 540px (pad 72/24, gap 56)` → `Sections 1280px / 28px 24px` → `Footer`. Breakpoints: **900px** (hero stacks, peek hidden, arrows→row), **700px** (palette grid 1-col), **640px** (headline 28px, CTA flex-1). Grids `4→2→1`.

---

## 9. Tailwind CSS Configuration

```css
@import "tailwindcss";
:root { --color-accent:#0077B6; --color-button-bg:#0077B6; --color-ink:#0A2540; --color-section-bg:#F5FAFC; /* …§3.2 */ }
@theme inline {
  --color-primary: var(--color-accent);
  --color-card: #FFFFFF;
  --radius-button: 8px;
  --font-sans: var(--font-outfit);
  --font-display: var(--font-fraunces);
}
```

`layout.tsx`: `next/font` `Fraunces (500-700) + Outfit (400-700)` variable. `lib/cms/resolve.ts` emits `:root` vars.

---

## 10. Figma Variable Collections Summary

| Collection | Variables |
|---|---|
| `Colors` | `ink #0A2540`, `mist #F5FAFC`, `surface #FFFFFF`, `primary #0077B6`, `hover #023E8A`, `foam #E6F7FB`, `imageBg #CAF0F8`, `sale #FF6B4A`, `success #0E9F6E`, `warning #F79009`, `error #D92D20`, `border #DCE8EE`, `muted #5B7286` |
| `Gradients` | `ocean-bars 700→400`, `deep 800→600`, `hero-canvas` (hero-slide background gradients live in §7.7, not in Figma collections) |
| `Radii` | `button 8, card 12, peek 14, pill 9999, circle` |
| `Shadows` | `sm/md/lg/focus-ring` |
| `Typography` | `Fraunces + Outfit` scale as §2 |

---

## 11. Component Inventory

`components/ui/` (`Button`, `IconButton`, `Badge`, `Input`, `Textarea`, `Select`, `ChipInput`, `ColorPicker`, `Slider`, `Toggle`, `ThreeStateControl`, `Dialog`, `SortableList`), `components/sections/` (`HeroSection`, `BannerSection`, `FeaturedProducts`, `CategoryShowcase`, `BrandStrip`, `BlogTeaser`), `components/product/` (`ProductCard`, `Gallery`, `VariantSelector`), `components/cart/` (`CartLineItem`, `MiniCartDrawer`). All dumb `props → JSX`; hero `<2KB` JS.

---

## 12. Accessibility Guidelines

- **Contrast:** Ink on card `≈15.9:1` AAA; muted `4.7:1` AA; primary `#0077B6` `4.6:1` AA (text + fill); **sale `#FF6B4A` must use ink text** (`4.6:1`) — white fails (`2.8:1`).
- **Motion:** `prefers-reduced-motion` disables wave (`transition:none`, wave pinned), hides peeks, kills fades.
- **Keyboard:** `←/→` on hero (`tabIndex 0`), dots `aria-label="Go to slide N"`, arrows labelled, peeks `aria-hidden`, CTA `focus-visible` ring.
- **Images:** `alt` from `imageAlt`, `eager` first slide (LCP) else `lazy`, `aspect-ratio` prevents CLS.

---

## Appendix — File References

- Prototype (source of truth): `E:\E-Commerce\index.html` — Oceanic Blue v1.0 · Fraunces + Outfit · gradient hero · peek deck · wave CTAs · hero slide background gradients (Warm Sunrise / Sage Cloud / Aurora, §7.7)
- CMS: `docs/6.Admin-Panel.md` §4 · `docs/3.Database-Schema.md` §4.1 (`cms_settings.theme`, `cms_sections` `Slide{ctas[0..3]}`) · `docs/pages/home.md` §3
- Implementation: `frontend/storefront/src/app/globals.css`, `layout.tsx`, `lib/cms/resolve.ts`, `lib/api-client/cms.ts`, `shared/src/schemas/cta.schema.ts`
