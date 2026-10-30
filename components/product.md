# ProductCard (+ Gallery / VariantSelector stubs) — commerce face

> Scope: `frontend/storefront/components/commerce/ProductCard.tsx` + `.sf-productcard` (media, badges, options/swatches/pills, info, hover actions, CTA bar variants, stock/wishlist states, ports, theme group).
> Status: Active | Version 2.0 | Date: 2026-10-30
> Parent: `components/README.md` (index + conventions)

---

## 1. Anatomy (look)

`<article>` root: media block (image + hover image + badges list + overlay CTA layer) → CTA bar (when `ctaVariant` is `below`) → info (category eyebrow, name 2-line clamp, price + compare-at sale, rating, inline CTA when `ctaVariant="inline"`, color swatches & size pills) → footer CTA (when `ctaVariant="footer"`). Card never knows siblings — grid columns live at the listing level (owner passes `columns` to the grid, not the card).

Media ratios (union, default `4:5` — editorial precedent): `3:4 / 4:3 / 4:5 / 1:1 / 16:9`. Ratio is a prop today, theme knob at build.
Card types: `standard`, `minimal`, `compact`, `overlay`, `horizontal`.

## 2. Media (cover + hover swap)

`image` + optional `hoverImage` (admin picks which is cover, which is hover — both settable independently): hover transitions cover→hover per `swapAnimation` (default `fade` 160ms; reduced-motion always instant-swap, no transition). Absent hover = static cover. `loading="lazy"`, placeholder image-bg, `alt=""` — the card's open control already announces name+price (palette-row pattern, no double-announce).

Swap animation set (`swapAnimation` + `swapDurationMs` 0–500): `fade` (crossfade) / `slide` (hover slides in over cover) / `zoom` (hover scales 1.06→1.0 over cover) / `none` (instant swap). Preset→concrete in the resolver (motion-shape precedent); CSS reads vars, keyframes per member.

Image blend modes (`imageBlendMode`): `normal / multiply / darken / overlay / screen` (CSS `mix-blend-mode` on the image with `--pc-media-bg` as the canvas backing).

## 3. Centralized Badges (single source of truth)

Badges **cannot** be created or deleted via the product card. All badges live in `catalog.badges` and are assigned to products via `catalog.product_badges`.
- **Entity**: `key`, `label`, `bg`, `text_color`, `border_color`, `border_style` (`solid`, `dashed`, `dotted`, `none`), `priority`, `is_active`, `starts_at`, `ends_at`.
- **Rendering**: ProductCard displays up to 3 active badges in priority order in a stack (`.sf-productcard__badge-list`) positioned via `badgePosition: "left" | "right"`.
- Deprecates local freeform `theme.badges.custom` in favor of the platform registry.

## 4. Options, Swatches & Pills

Products can expose selectable options on the card face without N+1 query penalty:
- Backed by `catalog.product_options` (`display_type: "swatch" | "pill" | "dropdown"`, `show_on_card: boolean`) and `catalog.product_option_values` (`swatch_hex: string | null`, `swatch_image_url: string | null`).
- Product list endpoint (`GET /products`) projects options using lateral subquery aggregation (`jsonb_agg`) when `show_on_card = true`.
- Storefront displays color swatches (32px circles with accessible high-contrast border and active ring) and size pills (`role="radiogroup"` with `aria-label`).
- Controlled interaction via `selectedOptions` and `onSelectOption(name, value)`.

## 5. CTA Action Bar Variants & Styles

Configurable action bar placements and button formats:
- `ctaVariant`:
  - `overlay`: Floating bar on top of the image (revealed on hover or always on touch).
  - `below`: Rendered directly underneath the media block.
  - `inline`: Embedded beside the price block inside info.
  - `footer`: Pinned to the bottom of the card with an accent dividing border.
  - `none`: Completely hidden.
- `ctaStyle`:
  - `icon`: Circular icon action buttons.
  - `label`: Text button (e.g., "Add to Bag").
  - `icon-label`: Icon + label combination button.
- `ctaSet`: Max 3 actions from `['quick-view', 'wishlist', 'add-to-cart', 'share']`.

## 6. Contrast-Safe Admin Colors

Admins can configure arbitrary hex colors via the Admin Panel color picker:
- `cardBg`, `hoverCardBg`, `borderColor`, `hoverBorderColor`, `mediaBg`.
- Automatic Contrast Safety: If an admin selects a dark background (`isDarkHex(cardBg) === true`), `resolveProductCardStyles()` automatically populates high-contrast fallback tokens (`--pc-text`, `--pc-muted`, `--pc-price`) unless explicitly overridden, preventing unreadable dark text on dark surfaces.
- CSS uses strictly CSS variables (`var(--pc-card-bg)`, etc.); zero hardcoded hex values outside variables.

## 7. Info (each with a show toggle)

Name (2-line clamp, `nameSize`), price + optional `compareAt` strikethrough with auto sale face (`priceSize`), rating + count (palette pattern, `showRatings`), category eyebrow (`showDept`). Defaults mirror palette row faces.

## 8. Stock + wishlist states

`stock: "in" | "low" | "out"` (default `in`): `low` shows a low-stock face; `out` disables all actions + dims media via explicit solids (never opacity — contrast ban) + "Sold out" face. `wishlisted: boolean` flips the heart (palette `addedIds` pattern; `useWishlist` hook lands with the wishlist slice — prop today, hook later). The heart is product-level, not variant-level. Guests are prompted to sign in; the pending product id survives via `?next=` or a short-lived cookie (never `localStorage`) and is POSTed after login. A duplicate add is a no-op; admin-only tokens are rejected (403).

## 9. Card-as-link rule (dumbness boundary)

Root is `<article>`, never a button/link: media + name navigate via `onOpen(product)` (owner routes to PDP); actions are **sibling** buttons (nested-`<button>` ban — palette-row precedent). Whole-card click never swallows action clicks (stopPropagation at the action, stated). Actions sit in tab order; Esc closes nothing (no popup); focus-visible ring fixed.

Touch: hover layer is hover-only; on `(hover: none)` actions hide unless `showActionsOnTouch` (admin toggle, default false). Tap = `onOpen` (navigate) — no first-tap-reveal (locked: reveal-on-tap traps touch users in a mode with no exit affordance).

## 10. Data (ports, additive — `SearchResult` extends, never forks)

`ProductCardData extends SearchResult`: `hoverImage? / url? / compareAt? / stock? / wishlisted? / badges? / options? / cardSettings?` (all optional — absent renders the base face). Cart reuses `QuickAddPort`; wishlist gets `WishlistPort { toggle(id, signal) }` where `id` is the **product id** (no variant id); share is owner-handled (no port — Web Share API is browser, not service). CMS/product-svc replaces demo rows at the call site (one line), callers never change.

## 11. Theme group sketch (`theme.productCard` — build task wires)

`cardBg / hoverCardBg / borderColor / hoverBorderColor / mediaBg / textColor / mutedTextColor / priceColor / comparePriceColor / borderRadius` 0–24, `mediaRatio` union, `cardType`, `badgePosition`, `showBadge/Ratings/Dept/Swatches/Pills`, `hoverMode` (`none/image/actions/image-and-actions/zoom`), `swapAnimation` (`fade/slide/zoom/none`) + `swapDurationMs` 0–500, `ctaVariant` (`overlay/below/inline/footer/none`), `ctaStyle` (`icon/label/icon-label`), `ctaSet` (max 3) + `ctaPosition`, `showActionsOnTouch`, `nameSize / priceSize`, listing columns desktop 3/4/5 – tablet 2/3 (**cap 3** — 4-up below 1024px squeezes cards under ~220px and thumb + two text lines stop being legible) – phone 1/2, `cardWidth / cardHeight` caps (listing-level, clamped). Hover paint resolves through CSS `:hover` on vars (never class toggles; `:not([disabled])`-style guards; `out`-of-stock cards get no hover faces). Every knob gets a flat per-instance twin (trio rule: explicit override always wins over theme). Resolver: same nested-merge + clean/clamp/union discipline. Matrix records rows same-commit.

## 12. Deferred, reserved (props land now, slices later)

- Quick-view modal slice (reserved `onQuickView(product)`; modal carries PDP data needs — own slice).
- Compare (`onCompare?` + `compareBehavior: "page" | "modal"` — admin selects destination; both land in the compare slice).
- Skeleton face (loading shimmer — lands with listing slice, not per-card).

## 13. Gallery / VariantSelector (stubs — one line each, no placeholders)

- **Gallery**: PDP media rail (thumbs + zoom contract) — lands with PDP slice.
- **VariantSelector**: size/color pickers feeding `selectedAttribute` — lands with the attribute-thinking task.
