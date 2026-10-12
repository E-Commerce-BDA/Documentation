# Product card (+ gallery / variant stubs) — anatomy, media, badge, hover, ports

> Scope: `ProductCard` (anatomy, media swap, badge, info, hover actions, stock, ports, theme sketch) + Gallery/VariantSelector stubs §11.
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## 1. Anatomy (look)

Card root is `<article>` (listing item, never a link or button itself):
media block (image + hover layer + badge) → info block (category eyebrow,
name, price row, rating row). Columns live at the **listing level** —
the card never knows siblings; the grid tells it its width.

Media ratios (admin picks one, default **4:5** — editorial precedent):

| Ratio | Use |
|---|---|
| `1:1` | Square tiles, dense grids |
| `3:4` | Portrait standard |
| `4:5` | Portrait tall (default) |
| `4:3` | Landscape |
| `16:9` | Wide editorial |

Row/column counts (listing-level, admin-picked): desktop 3 / 4 / 5,
tablet 2 / 3 (**cap 3** — 4-up below 1024px squeezes cards under ~220px
and the thumb + two text lines stop being legible), phone 1 / 2 (size
adjusts accordingly).

## 2. Media (cover + hover swap)

`image` (cover) + optional `hoverImage`. Hover crossfades cover→hover
(160ms fade, instant under reduced-motion); absent hover = static card.
Both lazy-load with a placeholder wash behind; `alt=name` only when the
media is NOT inside a labelled button (palette-row rule: labelled
wrapper implies empty alt, no double-announce). Admin sets cover and
hover independently; hover never required.

## 3. Badge (show, map, position)

`showBadge` toggle + per-product `tag` → the shared `tagTone` lib map +
the admin's custom-badges map (see `customization.md` — one map home,
card never switches on tag strings). `badgePosition: left | right`
(default left). Badge shape rides Pill/Badge — **no card-level badge
paint knobs** (faces stay system-wide by design).

## 4. Info (name, price, rating — each gated)

- Category eyebrow (`showDept`, muted, uppercase).
- Name, 2-line clamp (`nameSize` admin-tunable; overflow ellipsizes,
  never wraps the card taller).
- Price + optional `compareAt` strikethrough (auto-sale face when
  `compareAt > price`; sale keeps ink text — contrast law).
- Rating + count (palette pattern: gold star, muted count, absent when
  no rating). `showRatings` toggle.

## 5. Hover layer (admin picks ONE mode)

`hoverMode: "image" | "actions"` — image-swap OR CTA bar, never both
(one hover story per card, no stacked effects).

CTA bar (max 3 of 4 — admin picks the set):

| Action | Behavior |
|---|---|
| Quick view | Fires reserved `onQuickView` (modal is its own later slice) |
| Wishlist | Toggles via `wishIds` + `onWishlist` (palette `addedIds` pattern) |
| Add to cart | Fires `onAdd` (cart-svc port, `QuickAddPort` pattern) |
| Share | `navigator.share` + clipboard fallback (hook owns, later) |

CTA position: left / center / right (admin). Icons from the Icon set,
glyph-only v1 (no upload — stated trim; uploads need fallback design,
deferred deliberately). On touch (`hover: none`): layer hidden unless
`showActionsOnTouch` (admin toggle, default off).

## 6. Stock + wishlist states (explicit, never opacity)

`stock: "in" | "low" | "out"` — `out` disables actions + shows a
sold-out face on the media (explicit solids; the opacity ban holds on
cards too). `low` shows a low-stock hint face. `wishlisted` flips the
heart filled (wishlist hook `useWishlist` lands with the slice; card
receives `wishIds`, stays controlled).

## 7. Card-as-link rule (nested-button ban)

Media + name navigate via `onOpen(product)` — the **owner** routes to
the PDP (parity with palette's `onView` rule: dumb card never imports
the router). Actions are **sibling** buttons beside the open-target,
never inside it (nested buttons are illegal HTML — palette-row
precedent). Whole-card click never swallows action clicks.

## 8. Keyboard + a11y (fixed, not customizable)

Actions sit in tab order (they're real buttons); the open-target is
keyboard-operable; Esc closes nothing (no popup on the card);
focus-visible ring fixed; touch gets actions only when admin enables
them (§5). Reduced-motion kills the media crossfade.

## 9. Ports (data in, never fetched)

Product data extends `SearchResult` with additive optionals only
(`hoverImage?`, `url?`, `compareAt?`, `stock?`) — zero breakage to
search consumers. Behaviors reuse port shapes: cart add mirrors
`QuickAddPort`; wishlist/share land as `WishlistPort`/share-hook with
the same abortable, demo-swappable contract. Demo rows serve the
showcase until catalog-svc lands (throwaway-by-replacement).

## 10. Theme group sketch (`theme.productCard`, build task)

`cardBg / borderColor / borderRadius` (0–24) · `mediaRatio` (5-member
union, default `4:5`) · `badgePosition` + `showBadge` · info toggles
(`showDept / showRatings`) + `nameSize / priceSize` · `hoverMode` +
`ctaSet` (max 3) + `ctaPosition` + `showActionsOnTouch` · listing
columns (desktop 3–5, tablet 2–3, phone 1–2) · `cardWidth / cardHeight`
caps · reserved `onQuickView / onCompare` + `compareBehavior:
"page" | "modal"` (compare button navigates or modals per admin —
locked decision) · reserved single-attribute quick-pick
(`selectedAttribute` + `onAttribute` — variant-inventory thinking
deferred).

## 11. Stubs (filled by their slices — one line each, no placeholders)

- **Gallery** (PDP media rail: thumbs, zoom, ratio sync with card) —
  lands with the PDP slice.
- **VariantSelector** (attribute pick → inventory → price; the
  single-attribute quick-pick graduates here) — lands with the
  variant-inventory design.
