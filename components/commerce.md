# Commerce blocks — QuantityStepper · EmptyState

> Scope: `frontend/storefront/components/ui/QuantityStepper.tsx`,
> `components/ui/EmptyState.tsx`, `lib/commerce/quantity.ts` (the clamp), and the
> `.sf-qty` / `.sf-empty` blocks in `app/globals.css`.
> Status: Active | Version 1.0 | Date: 2026-11-01
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

## 6. Reuse/gap map (commerce slice — doc-009, planned)

The canonical map from the standalone-prototype research (`sf-082`, `sf-083`)
lives in [shell.md](shell.md) §2–§3. The commerce surfaces (cart, checkout,
confirmation, products/PDP, account, compare) reuse the same ten pieces; they
are listed here so a route never rebuilds one locally.

| Prototype piece | Existing Next home | Reuse rule |
|---|---|---|
| Navbar | `components/shell/Navbar.tsx` + `NavbarMount.tsx` | one chrome on every commerce route |
| AccountMenu | `NavAccountButton.tsx` + planned Dropdown/Menu | trigger stays; the menu is a new primitive |
| Search overlays | `SearchSheet` / `SearchEditorial` / `SearchPalette` + `searchRegistry` | registry variants, never a page-local overlay |
| Drawers | `MobileDrawer.tsx`, `MiniCartDrawer.tsx` | cart and filter panels share `.sf-drawer`/`.sf-scrim` |
| Product card / grid | `ProductCard.tsx`, `ProductGrid.tsx`, `.sf-grid` | one painter across listing, PDP, cart and account |
| Filter rail | desktop `/products` sidebar | FilterDrawer reuses the same controls on mobile |
| Sort select | `Select.tsx` (`native`) + `theme.select` | composed by ShopToolbar, not re-implemented |
| Brand strip | `BrandStripSection.tsx` (`sf-marquee`) | unchanged; rail is a separate engine |
| Compare table | 4-column table + drag surface (`sf-081`) | reused as-is; no paginated comparison |
| Footer | `Footer.tsx` + `FooterMount.tsx` (`sf-062`) | CMS faces, unchanged |

The nine gaps are indexed in [README.md](README.md) §3 and
[0.Project-Overview.md](../0.Project-Overview.md) §14; the commerce-owned ones
are:

| Artifact | Reuse boundary | State contract |
|---|---|---|
| OrderSummaryCard (sf-088, ⬜ planned) | replaces repeated totals markup on checkout, confirmation and cart; reads the same `lib/commerce/totals.ts` resolver | props only, no state |
| Timeline (sf-088, ⬜ planned) | replaces the order-status step markup on confirmation and account order detail | props only, no state |
| ShopToolbar / FilterDrawer / GridModeToggle (sf-087, ⬜ planned) | compose the existing sort select, filter rail and grid on `/products` | pure machines + `useReducer`; parent owns `open`/selection |

Planned files: `lib/commerce/totals.ts` and `lib/commerce/timeline.ts` (pure
resolvers), `.sf-ordersummary` / `.sf-timeline` blocks in `app/globals.css`,
trios `test/lib/commerce/{totals,timeline}.test.ts` +
`test/components/{order-summary-card,timeline}.test.tsx` +
`test/components/{order-summary-card,timeline}-style.test.ts`. No new
`useState`: ADR-ui in
[ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md).

---

## Appendix — file references

- Clamp + tests: `lib/commerce/quantity.ts` · `test/lib/commerce/quantity.test.ts`
- Blocks: `components/ui/QuantityStepper.tsx` · `components/ui/EmptyState.tsx`
- Paint: `app/globals.css` `.sf-qty*`, `.sf-empty*`
- Consumers: `app/(shop)/products/page.tsx` (empty), `cart/_components/CartView.tsx`,
  `products/[slug]/_components/PurchasePanel.tsx`
