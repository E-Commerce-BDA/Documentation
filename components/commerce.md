# Commerce blocks — QuantityStepper · EmptyState

> Scope: `frontend/storefront/components/ui/QuantityStepper.tsx`,
> `components/ui/EmptyState.tsx`, `lib/commerce/quantity.ts` (the clamp), and the
> `.sf-qty` / `.sf-empty` blocks in `app/globals.css`.
> Status: Active | Version 1.1 | Date: 2026-11-27
> Parent: `components/README.md` §1 · `design-system/storefront.md` §5 (form controls)
> Implements: sf-051 (`/cart`, `/products/[slug]`, `/products` empty state)

---

## 1. Look per state (normative)

### QuantityStepper

Minus button · numeric input · plus button, on one 40 px row. It appears on the
PDP (1–stock) and on every cart line (1–stock, debounced by the caller).

| State | Look |
|---|---|
| default | `--qty-border` over `--border` hairline, `--qty-bg` over white surface, `--qty-text` over `--color-ink` digits |
| hover / focus-within | shared ring — `:focus-within` shows what `:hover` shows (`--qty-accent`) |
| min reached | minus button disabled solid (`--qty-disabled-bg`/`--qty-disabled-text`), never opacity |
| max reached | plus button disabled solid |
| pending (caller-owned) | `data-pending="true"` dims the digits only (`--qty-pending-text`); freezing the buttons is the caller's `disabled` |

### EmptyState

Centred icon, title, one line of body, one action. Used by the listing (no
matches), the cart (A4.7) and the account order history.

| State | Look |
|---|---|
| default | `--empty-body` over `--text-muted`, `--empty-title` over `--color-ink`, 44 px glyph on `--empty-glyph-bg` over `--color-accent-50` |
| with action | one `Button` variant `light` under the body |

## 2. Customizable fields (what admin can change)

Neither block takes paintable admin knobs. Both read house tokens only
(`--color-ink`, `--text-muted`, `--border`, `--color-accent-50`,
`--color-accent`, `--radius-button`) through their own `--qty-*` / `--empty-*`
vars, whose fallbacks are those tokens. Reason: a quantity stepper that
matches one section's palette and not another's is a bug, not a feature.

## 3. How to change (scopes — where a value lives)

| Value | Home | Override |
|---|---|---|
| clamp (`min`, `max`, integer) | `lib/commerce/quantity.ts` → `clampQty` | flat props on the block |
| disabled faces | `data-disabled` / the buttons' `disabled` attribute, never a class toggle | — |
| icon pair (minus / plus) | `Icon` names `minus` / `plus` | — |
| empty-state copy | the route that renders it | `title` / `body` props |

## 4. Global rules (inherited)

The four `components/ui` rules hold unchanged: props → JSX, controlled-only (the
caller owns `value` for the stepper, `open` never appears here), state reaches
CSS only through `data-*`, and both blocks ship trio tests (`quantity-stepper`
contract + `quantity-stepper-style` for paint, `empty-state` contract +
`empty-state-style`).

## 5. Apply-to-all (the per-type bulk switch)

N/A — no per-type switch exists for either block; they are fixed house faces.

## 6. Reuse/gap map (commerce slice — doc-009, final outcome)

The canonical map from the standalone-prototype research (`sf-082`, `sf-083`)
lives in [shell.md](shell.md) §2–§3. The commerce surfaces (cart, checkout,
confirmation, products/PDP, account, compare) reuse the same ten pieces; they
are listed here so a route never rebuilds one locally. Every row below is now
backed by shipped code — none is a planned artifact.

| Prototype piece | Existing Next home | Reuse rule |
|---|---|---|
| Navbar | `components/shell/Navbar.tsx` + `NavbarMount.tsx` | one chrome on every commerce route |
| AccountMenu | `components/shell/NavAccountButton.tsx` + shipped `components/ui/Menu.tsx` | trigger stays; one new menu primitive (no second navbar) |
| Search overlays | `SearchSheet` / `SearchEditorial` / `SearchPalette` + `searchRegistry` | registry variants, never a page-local overlay |
| Drawers | `MobileDrawer.tsx`, `MiniCartDrawer.tsx` | cart and filter panels share `.sf-drawer`/`.sf-scrim` |
| Product card / grid | `ProductCard.tsx`, `ProductGrid.tsx`, `.sf-grid` | one painter across listing, PDP, cart and account |
| Filter rail | `components/commerce/FilterRail.tsx` in `ListingShell.tsx` | shipped `FilterDrawer.tsx` reuses the same controls on mobile |
| Sort select | `components/ui/Select.tsx` (`native`) + `theme.select` | composed by shipped `ShopToolbar.tsx`, not re-implemented |
| Brand strip | `BrandStripSection.tsx` (`sf-marquee`) | unchanged; rail is a separate engine |
| Compare table | 4-column table + drag surface (`sf-081`) | reused as-is; no paginated comparison |
| Footer | `Footer.tsx` + `FooterMount.tsx` (`sf-062`) | CMS faces, unchanged |

The nine gaps are indexed in [README.md](README.md) §3 and
[0.Project-Overview.md](../0.Project-Overview.md) §14; the commerce-owned ones
all shipped:

| Artifact | Reuse boundary (shipped) | State contract |
|---|---|---|
| OrderSummaryCard (sf-088, wired sf-093) | `components/commerce/OrderSummaryCard.tsx` replaces repeated totals markup on cart, checkout and confirmation; reads `lib/order/summaryModel.ts` | props only, no state |
| Timeline (sf-088, wired sf-093) | `components/commerce/Timeline.tsx` replaces the order-status step markup on confirmation and account order detail; reads `lib/order/timeline.ts` | props only, no state |
| ShopToolbar / FilterDrawer / GridModeToggle (sf-087, wired sf-092) | `components/ui/{ShopToolbar,FilterDrawer,GridModeToggle}.tsx` compose the existing sort select, `FilterRail` and grid in `app/(shop)/products/_components/ListingShell.tsx` | pure machines in `lib/shop/machine.ts` + `useReducer`; parent owns `open`/selection |

Shipped files: `lib/order/summaryModel.ts` and `lib/order/timeline.ts` (the pure
resolvers — the earlier planned resolver names under `lib/commerce/` were never
created), `.sf-ordersummary` / `.sf-timeline` blocks in `app/globals.css`, and the trios
`test/lib/composed-models.test.ts`,
`test/components/composed-components.test.tsx`,
`test/components/composed-style.test.ts`,
`test/components/money-chrome.test.tsx`,
`test/components/money-chrome-style.test.ts`. No new `useState`: ADR-ui in
[ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md).

---

## Appendix — file references

- Clamp + tests: `lib/commerce/quantity.ts` · `test/lib/commerce/quantity.test.ts`
- Blocks: `components/ui/QuantityStepper.tsx` · `components/ui/EmptyState.tsx`
- Wave 1 commerce blocks: `components/commerce/OrderSummaryCard.tsx` +
  `lib/order/summaryModel.ts`; `components/commerce/Timeline.tsx` +
  `lib/order/timeline.ts`; tests `test/lib/composed-models.test.ts`,
  `test/components/composed-components.test.tsx`, `test/components/composed-style.test.ts`,
  `test/components/money-chrome.test.tsx`, `test/components/money-chrome-style.test.ts`
- Paint: `app/globals.css` `.sf-qty*`, `.sf-empty*`, `.sf-ordersummary*`, `.sf-timeline*`
- Consumers: `app/(shop)/products/page.tsx` (empty), `cart/_components/CartView.tsx`,
  `products/[slug]/_components/PurchasePanel.tsx`
