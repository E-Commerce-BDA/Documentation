# ProductCard (+ Gallery / VariantSelector stubs) — commerce face

> Scope: `frontend/storefront/components/commerce/ProductCard.tsx` + `.sf-productcard` (media, badges, options/swatches/pills, placements, carousel, selection effects, info, hover actions, CTA bar variants, stock/wishlist states, ports, theme group).
> Status: Active | Version 3.0 | Date: 2026-10-30
> Parent: `components/README.md` (index + conventions)

---

## 1. Anatomy (look)

`<article>` root: media block (image carousel + hover image + badges list + overlay CTA layer + media option placements) → CTA bar (when `ctaVariant` is `below`) → info (eyebrow / brand-hover swap, name 2-line clamp, info options, price + compare-at sale, rating, inline CTA when `ctaVariant="inline"`) → footer CTA (when `ctaVariant="footer"`). Card never knows siblings — grid columns live at the listing level (owner passes `columns` to the grid, not the card).

Media ratios (union, default `4:5` — editorial precedent): `3:4 / 4:3 / 4:5 / 1:1 / 16:9`. Ratio is a prop today, theme knob at build.
Card types: `standard`, `minimal`, `compact`, `overlay`, `horizontal`.

## 2. Media (cover, hover swap & multi-image carousel)

- **Cover & Secondary Swap**: `image` + optional `hoverImage`: hover transitions cover→hover when `hoverMode="image"`. Absent hover = static cover. `loading="lazy"`, placeholder image-bg, `alt=""` — the card's open control already announces name+price (palette-row pattern, no double-announce).
- **Multi-Image Carousel**:
  - Controlled via `activeImageIndex` and `onImageIndexChange(newIndex)`.
  - Bounded by `imageLimit` (clamped 1..10, default 5).
  - Arrow Navigation: Prev / Next buttons rendered as **siblings** of the open button (never nested). Controlled via `imageNav`: `"hover"` (revealed on card hover/focus), `"always"`, `"touch"`, or `"none"`. Loop behavior governed by `imageLoop` (default true).
  - Indicator Styles: Controlled via `imageIndicator`: `"dots"`, `"bars"`, `"count"` (e.g. `1 / 4`), or `"none"`. Positioned via `imageIndicatorPosition: "bottom" | "top"`.
  - Touch Swiping: Touch gestures (`onTouchStart` / `onTouchEnd` with 40px delta threshold) enable natural carousel swiping on mobile devices.
- **Image Blend Modes** (`imageBlendMode`): `normal / multiply / darken / overlay / screen` (CSS `mix-blend-mode` on the image with `--pc-media-bg` as the canvas backing).

## 3. Centralized Badges (single source of truth)

Badges **cannot** be created or deleted via the product card. All badges live in `catalog.badges` and are assigned to products via `catalog.product_badges`.
- **Entity**: `key`, `label`, `bg`, `text_color`, `border_color`, `border_style` (`solid`, `dashed`, `dotted`, `none`), `priority`, `is_active`, `starts_at`, `ends_at`.
- **Rendering**: ProductCard displays up to 3 active badges in priority order in a stack (`.sf-productcard__badge-list`) positioned via `badgePosition: "left" | "right"`.
- Deprecates local freeform `theme.badges.custom` in favor of the platform registry.

## 4. Options, Swatches, Pills & Placements

Products expose selectable options on the card face without N+1 query penalty:
- Backed by `catalog.product_options` (`display_type: "swatch" | "pill" | "dropdown"`, `show_on_card: boolean`, `card_placement: "info" | "media" | "brand-hover" | "media-hover-top" | "hidden"`) and `catalog.product_option_values` (`swatch_hex: string | null`, `swatch_image_url: string | null`).
- Product list endpoint (`GET /products`) projects options using lateral subquery aggregation (`jsonb_agg`).
- **Configurable Placements**:
  - `info`: Placed inside the product details container underneath the title (default).
  - `media`: Pinned horizontally over the bottom of the image container.
  - `brand-hover`: Positioned in the eyebrow slot. Renders the brand/category at rest, and seamlessly reveals the option swatches on hover or keyboard focus.
  - `media-hover-top`: Floats option pills over the top of the image container on hover or keyboard focus.
  - `hidden`: Excluded from the card face.
- **Accessibility & Keyboard Navigation**:
  - Roving `tabIndex` (`tabIndex={isSelected ? 0 : -1}`) ensures single tab-stop per group.
  - WAI-ARIA `role="radiogroup"` with individual `role="radio"` and `aria-checked`.
  - `onKeyDown` handlers support ArrowRight / ArrowDown (next), ArrowLeft / ArrowUp (prev), Home (first), End (last).
  - Controlled callbacks: `selectedOptions`, `previewedOptions`, `onSelectOption(name, val)`, `onPreviewOption(name, val | null)`.

## 5. Selection Effects on Catalog Grids

- Powered by pure resolver `resolveSelectedVariant(product, selectedOptions, previewedOptions, activeImageIdx, effects)`:
  - `selectionMode`: `"preview"` (hover previews swatch, click commits selection), `"commit-only"` (click only), or `"visual"` (visual indicator only).
  - `selectionEffects`: Whitelist array of `["image", "price", "stock"]`.
    - `"image"`: Swaps display image to the matched variant's `imageUrl`.
    - `"price"`: Updates card price and compare-at strikethrough to the matched variant's pricing.
    - `"stock"`: Reflects real-time variant stock level (out-of-stock disables buttons and applies "Sold out" badge; stock < 5 reveals "Low stock").
  - Preview overrides active selection during hover preview and clears on mouse leave / blur.
  - Search results remain visual-only; selection effects run on catalog browsing grids.

## 6. CTA Action Bar Variants & Styles

Configurable action bar placements and button formats:
- `ctaVariant`:
  - `overlay`: Floating bar on top of the image (revealed on hover or always on touch). Decoupled from `hoverMode` — renders whenever `ctaVariant="overlay"`.
  - `below`: Rendered directly underneath the media block.
  - `inline`: Embedded beside the price block inside info.
  - `footer`: Pinned to the bottom of the card with an accent dividing border.
  - `none`: Completely hidden.
- `ctaStyle`:
  - `icon`: Circular icon action buttons.
  - `label`: Text button (e.g., "Add to Bag").
  - `icon-label`: Icon + label combination button.
- `ctaSet`: Max 3 actions from `['quick-view', 'wishlist', 'add-to-cart', 'share']`.
- **Focus Safety**: When unrevealed, overlay CTAs have `visibility: hidden; pointer-events: none;` so browsers remove them from the tab order, preventing invisible focus traps.

## 7. Contrast-Safe Admin Colors

Admins can configure arbitrary hex colors via the Admin Panel color picker:
- `cardBg`, `hoverCardBg`, `borderColor`, `hoverBorderColor`, `mediaBg`.
- Automatic Contrast Safety: If an admin selects a dark background (`isDarkHex(cardBg) === true`), `resolveProductCardStyles()` automatically populates high-contrast fallback tokens (`--pc-text`, `--pc-muted`, `--pc-price`) unless explicitly overridden, preventing unreadable dark text on dark surfaces.
- CSS uses strictly CSS variables (`var(--pc-card-bg)`, etc.); zero hardcoded hex values outside variables.

## 8. Info & Eyebrow Configuration

- Eyebrow Mode (`eyebrow`): `"category"` (default), `"brand"` (shows `brand.name`), or `"none"`.
- Name (2-line clamp, `nameSize`), price + optional `compareAt` strikethrough with auto sale face (`priceSize`), rating + count (palette pattern, `showRatings`), category/brand eyebrow (`showDept`). Defaults mirror palette row faces.

## 9. Stock + wishlist states

`stock: "in" | "low" | "out"` (default `in`): `low` shows a low-stock face; `out` disables all actions + dims media via explicit solids (never opacity — contrast ban) + "Sold out" face. `wishlisted: boolean` flips the heart (palette `addedIds` pattern; `useWishlist` hook lands with the wishlist slice — prop today, hook later). The heart is product-level, not variant-level. Guests are prompted to sign in; the pending product id survives via `?next=` or a short-lived cookie (never `localStorage`) and is POSTed after login. A duplicate add is a no-op; admin-only tokens are rejected (403).

## 10. Card-as-link rule (dumbness boundary)

Root is `<article>`, never a button/link: media + name navigate via `onOpen(product)` (owner routes to PDP); actions are **sibling** buttons (nested-`<button>` ban — palette-row precedent). Whole-card click never swallows action clicks (stopPropagation at the action, stated). Actions sit in tab order; Esc closes nothing (no popup); focus-visible ring fixed. Carousel arrows and indicators are strictly siblings to the media open button.

Touch: hover layer is hover-only; on `(hover: none)` actions hide unless `showActionsOnTouch` (admin toggle, default false). Tap = `onOpen` (navigate) — no first-tap-reveal (locked: reveal-on-tap traps touch users in a mode with no exit affordance).

## 11. Data (ports, additive — `SearchResult` extends, never forks)

`ProductCardData extends SearchResult`: `hoverImage? / url? / compareAt? / stock? / wishlisted? / badges? / options? / images? / brand? / cardVariants? / cardSettings?` (all optional — absent renders the base face). Cart reuses `QuickAddPort`; wishlist gets `WishlistPort { toggle(id, signal) }` where `id` is the **product id** (no variant id); share is owner-handled (no port — Web Share API is browser, not service). CMS/product-svc replaces demo rows at the call site (one line), callers never change.

## 12. Theme group sketch (`theme.productCard`)

`cardBg / hoverCardBg / borderColor / hoverBorderColor / mediaBg / textColor / mutedTextColor / priceColor / comparePriceColor / borderRadius` 0–24, `mediaRatio` union, `cardType`, `badgePosition`, `showBadge/Ratings/Dept/Swatches/Pills`, `hoverMode` (`none/image/actions/image-and-actions/zoom`), `swapAnimation` (`fade/slide/zoom/none`) + `swapDurationMs` 0–500, `ctaVariant` (`overlay/below/inline/footer/none`), `ctaStyle` (`icon/label/icon-label`), `ctaSet` (max 3) + `ctaPosition`, `showActionsOnTouch`, `nameSize / priceSize`, `eyebrow`, `imageNav`, `imageIndicator`, `imageIndicatorPosition`, `imageLoop`, `imageLimit`, `selectionMode`, `selectionEffects`, listing columns desktop 3/4/5 – tablet 2/3 (**cap 3**) – phone 1/2. Every knob gets a flat per-instance twin (explicit override always wins over theme).

## 13. Deferred, reserved (props land now, slices later)

- Quick-view modal slice (reserved `onQuickView(product)`; modal carries PDP data needs — own slice).
- Compare (`onCompare?` + `compareBehavior: "page" | "modal"` — admin selects destination; both land in the compare slice).
- Skeleton face (loading shimmer — lands with listing slice, not per-card).

## 14. Gallery / VariantSelector (stubs — one line each, no placeholders)

- **Gallery**: PDP media rail (thumbs + zoom contract) — lands with PDP slice.
- **VariantSelector**: size/color pickers feeding `selectedAttribute` — lands with the attribute-thinking task.
