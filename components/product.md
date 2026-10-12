# ProductCard (+ Gallery / VariantSelector stubs) — commerce face

> Scope: `frontend/storefront/components/commerce/ProductCard.tsx` + `.sf-productcard` (media, badge, info, hover actions, stock/wishlist states, ports, theme group sketch).
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## 1. Anatomy (look)

`<article>` root: media block (image + hover image + badge + hover CTA layer) → info (category eyebrow, name 2-line clamp, price + compare-at sale, rating). Card never knows siblings — grid columns live at the listing level (owner passes `columns` to the grid, not the card).

Media ratios (union, default `4:5` — editorial precedent): `3:4 / 4:3 / 4:5 / 1:1 / 16:9`. Ratio is a prop today, theme knob at build.

## 2. Media (cover + hover swap)

`image` + optional `hoverImage` (admin sets both): hover crossfades cover→hover in 160ms (reduced-motion: instant swap, no fade). Absent hover = static cover. `loading="lazy"`, placeholder image-bg, `alt=""` — the card's open control already announces name+price (palette-row pattern, no double-announce).

## 3. Badge (tag → face + position)

`showBadge` gate + per-product `tag` → `tagTone` map + owner-passed custom-badm map (sf-032 `tones` prop, same lookup order). `badgePosition: "left" | "right"` (default left). Shape rides Badge/Pill — no card-level badge paint, ever.

## 4. Info (each with a show toggle)

Name (2-line clamp, `nameSize`), price + optional `compareAt` strikethrough with auto sale face (`priceSize`), rating + count (palette pattern, `showRatings`), category eyebrow (`showDept`). Defaults mirror palette row faces.

## 5. Hover layer (admin picks ONE)

`hoverMode: "image" | "actions"` (default `actions`): image-swap (see §2) vs CTA bar with **max 3** of `quick-view / wishlist / add-to-cart / share` (`ctaSet` array, order = display order). CTA position `left / center / right` (default center); icons from the Icon set (glyph-only v1 — upload deferred with reason: icon-color theming breaks on arbitrary uploads). `onQuickView / onWishlist / onQuickAdd / onShare` callbacks (owner-owned; share falls back to clipboard when `navigator.share` is absent).

## 6. Stock + wishlist states

`stock: "in" | "low" | "out"` (default `in`): `low` shows a low-stock face; `out` disables all actions + dims media via explicit solids (never opacity — contrast ban) + "Sold out" face. `wishlisted: boolean` flips the heart (palette `addedIds` pattern; `useWishlist` hook lands with the wishlist slice — prop today, hook later).

## 7. Card-as-link rule (dumbness boundary)

Root is `<article>`, never a button/link: media + name navigate via `onOpen(product)` (owner routes to PDP); actions are **sibling** buttons (nested-`<button>` ban — palette-row precedent). Whole-card click never swallows action clicks (stopPropagation at the action, stated). Actions sit in tab order; Esc closes nothing (no popup); focus-visible ring fixed.

Touch: hover layer is hover-only; on `(hover: none)` actions hide unless `showActionsOnTouch` (admin toggle, default false). Tap = `onOpen` (navigate) — no first-tap-reveal (locked: reveal-on-tap traps touch users in a mode with no exit affordance).

## 8. Data (ports, additive — `SearchResult` extends, never forks)

`ProductCardData extends SearchResult`: `hoverImage? / url? / compareAt? / stock? / wishlisted?` (all optional — absent renders the base face). Cart reuses `QuickAddPort`; wishlist gets `WishlistPort { toggle(id, signal) }` (same shape); share is owner-handled (no port — Web Share API is browser, not service). CMS/product-svc replaces demo rows at the call site (one line), callers never change.

## 9. Theme group sketch (`theme.productCard` — build task wires)

`cardBg / borderColor / borderRadius` 0–24, `mediaRatio` union, `badgePosition`, `showBadge/Ratings/Dept`, `hoverMode`, `ctaSet` (max 3) + `ctaPosition`, `showActionsOnTouch`, `nameSize / priceSize`, listing columns desktop 3/4/5 – tablet 2/3 – phone 1/2 (listing-level, clamped). Resolver: same nested-merge + clean/clamp/union discipline. Matrix records rows same-commit.

## 10. Deferred, reserved (props land now, slices later)

- Single-attribute quick-pick (`selectedAttribute?` + `onAttribute?` — needs variant-inventory thinking; reserved, never stubbed UI).
- Quick-view modal slice (reserved `onQuickView(product)`; modal carries PDP data needs — own slice).
- Compare (`onCompare?` + `compareBehavior: "page" | "modal"` — admin selects destination; both land in the compare slice).
- Skeleton face (loading shimmer — lands with listing slice, not per-card).

## 11. Gallery / VariantSelector (stubs — one line each, no placeholders)

- **Gallery**: PDP media rail (thumbs + zoom contract) — lands with PDP slice.
- **VariantSelector**: size/color pickers feeding `selectedAttribute` — lands with the attribute-thinking task.
