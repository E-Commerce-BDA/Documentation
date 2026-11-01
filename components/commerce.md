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

## Appendix — file references

- Clamp + tests: `lib/commerce/quantity.ts` · `test/lib/commerce/quantity.test.ts`
- Blocks: `components/ui/QuantityStepper.tsx` · `components/ui/EmptyState.tsx`
- Paint: `app/globals.css` `.sf-qty*`, `.sf-empty*`
- Consumers: `app/(shop)/products/page.tsx` (empty), `cart/_components/CartView.tsx`,
  `products/[slug]/_components/PurchasePanel.tsx`
