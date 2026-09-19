# Icons — Component Rules

> Scope: `frontend/storefront/components/ui/icons/Icon.tsx` (thin wrapper over
> `lucide-react`) + consumers (`IconButton`, `Button`/`Input` adornments,
> `Checkbox` tick).
> Status: Active | Version 1.0 | Date: 2026-09-18
> Parent: `design-system/storefront.md` §3 (tokens — icons use text color)

This doc follows the `components/button.md` template, minus states (icons
have no interactive states of their own).

---

## 1. Look (one rule, not per-icon specs)

All icons: **24×24 viewBox, `stroke="currentColor"`, `fill="none"`,
2px stroke, round caps/joins** (lucide defaults, locked in `Icon`).
Color is inherited from the parent text color — dark on white surfaces,
white on dark surfaces. **There are no color props and no per-background
variants.** `filled` switches to `fill="currentColor"` for active states
only (wishlisted heart, rated star).

`size` default **20** (optical fit in the 40px `IconButton` circle);
`16/24` used for inline/meta contexts. Exception: `Checkbox` tick renders
at `2.5px` stroke — legibility floor at ~12px boxes.

## 2. Customizable fields (what admin can change)

| Field | Control | Default | Notes |
|---|---|---|---|
| `size` | slider 12–32 | 20 | per-instance (adornment size follows its input) |
| `filled` | toggle | false | heart/star active states |
| `title` | text (optional) | absent | standalone meaning only; renders `<title>` + `role="img"` |
| color | inherited | parent text | admin recolors via parent `style={{ color }}` — no icon-level knob |

`strokeWidth` is fixed at 2 by design decision (not exposed) to keep the
set optically uniform. `name` accepts the 26 mapped keys (`ICON_NAMES`);
unknown CMS-driven strings fail closed (render nothing + dev warning).

## 3. How to change (scopes)

Icons carry no theme of their own — they resolve color from context:
instance `style` ?? parent text color ?? global ink. No resolver, no P>S>G
merge, no section/global icon settings. "Apply to all" does not apply;
change the parent's color once and every icon inside follows.

## 4. Global rules

1. **Never import `lucide-react` outside `icons/Icon.tsx`.** Call sites use
   `<Icon name>` or the barrel export — a future library swap touches one
   map. (`grep -r "lucide-react" components` must hit only `icons/`.)
2. **No emoji/unicode glyphs as icons.** They render inconsistently across
   platforms and cannot inherit theme color (the ⌕🛒✕ they replaced).
3. **Decorative by default.** `aria-hidden` unless `title` is set;
   `IconButton`'s required `label` stays the accessible name.
4. **No hex in icon code** (follows the global rule — `currentColor` only,
   `tickColor`-style props pass through `style`, never into paths).

## 5. Set (26, grouped by surface)

Navbar/actions: `search, shopping-bag, user, menu, x` · Navigation:
`arrow-left/right/up/down, chevron-left/right/up/down` · Commerce:
`heart (+filled), store, star (+filled), truck, shield-check, returns,
share, eye` · Forms/editing: `check, minus, plus, trash, filter`.

Deferred: payment-brand and social logos (own fill rules + legal
constraints — separate decision when needed).

---

## Appendix — file references

- Wrapper: `frontend/storefront/components/ui/icons/Icon.tsx`
- Consumers: `IconButton.tsx`, `Button.tsx` (`leftIcon/rightIcon`),
  `Input.tsx`, `Checkbox.tsx` (tick + indeterminate)
- Showcase: `app/page.tsx` §7 (white + ink chips prove the color flip)
- Tests: `frontend/storefront/test/components/icon.test.tsx`
- Dep: `lucide-react` (tree-shakeable — only imported icons ship)
