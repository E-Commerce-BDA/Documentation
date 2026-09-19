# Tooltip — Component Rules

> Scope: `frontend/storefront/components/ui/Tooltip.tsx` + `app/globals.css`
> `.sf-tip` (pure CSS positioning — no library, no measuring, no flip).
> Status: Active | Version 1.0 | Date: 2026-09-18
> Parent: `design-system/storefront.md` §3 (tokens — ink bubble)

This doc follows the `components/button.md` template, minus interactive
states (a tooltip is shown/hidden only).

---

## 1. Look (single spec, all placements)

Ink bubble (`--color-ink`) + white text, `12px/500`, `6px 10px` padding,
radius `8`, arrow nub, `max-width 240px`, `200ms` show delay, 4px drift on
entry. Readable on page surfaces **and** product images — the bubble never
adapts, so it never mismatches. One deliberate limitation: **no viewport
flip** (pure CSS cannot measure collisions). Mitigated by per-element
default placements + max-width clamp; if edge-clipping ever manifests
inside `MiniCartDrawer`/`Dialog`, floating-ui is the named scoped fallback
— for those containers only, never global.

## 2. Customizable fields (what admin can change)

All fields optional (absent = inherit/today); numerics clamp. Flat props
(`tipBg`, …) win over the `styleOverrides` object (future CMS payload —
same shape, no component change).

| Field | Control | Default | Notes |
|---|---|---|---|
| `mode` | select: custom / product-name / position | custom | content source (§3) |
| `text` (custom) | text input, 1–2 lines | — | enforced short; no paragraphs |
| `tipBg` / `tipTextColor` | color pickers | ink `#0A2540` / `#FFFFFF` | low-contrast pairs allowed but documented with a contrast warning |
| `tipBorderColor` / `tipBorderWidth 0–2` | picker + slider | transparent / `0` (today's borderless look) | |
| `tipRadius 0–16` | slider | `8` | button/card radius language |
| `tipFontSize 11–14` | slider | `12` | keeps tooltips subordinate to body |
| `tipFontWeight` | select 400–700 | `500` | |
| `tipAnimation` | select: slide / fade / none | slide (4px drift + fade) | `none` = instant (reduced-motion forces this too) |
| `tipDurationMs 0–500` | slider | `160` | travel/fade time (`delayMs` = wait before showing, separate) |
| `tipOffset 4–16` | slider | `8` | gap between trigger edge and bubble |
| `placement` | select: top / bottom / left / right | per element (dots → bottom) | no auto-flip (see §1) |
| `delayMs` | slider 0–500 | 200 | 0 for controlled/tour use |
| `maxWidth` | slider 120–320 | 240 | long product names wrap |
| `showArrow` | toggle | on | off inside dense dot rows |
| `enabled` | toggle | on | off (or empty text) → bare trigger, zero tooltip DOM |

Fixed by design decision (not exposed): `z-index` (systemic), `line-height`/
`padding` (derived from font size), `text-align` (center; paragraphs are
banned by §4), arrow size (8px).

## 3. How to change (scopes — eligibility first)

Tooltips are **opt-in per element**, never global. Only the 7 eligible
types accept a `tooltip` slot (enforced in code — other components have no
slot to fill): product/gallery images, carousel + pagination dots,
homepage section headers, navbar items, icon-only buttons, form-field
hints, disabled buttons (reason text).

Precedence for an eligible element: **instance `tooltip` ?? section
default ?? global default ?? off**. Prefill shows the resolved text;
reset deletes the key (sparse, never `null`). Bulk follows the standard
apply-to-all pattern ("all navbar items", "all dots in this carousel").

## 4. Global rules

1. **Where:** eligible 7 only (§3). Never on primary CTAs, never paragraphs
   inside, never as a substitute for visible labels or error text.
2. **Zero-JS positioning.** No measuring library in the tooltip path;
   `role="tooltip"` + `aria-describedby` on the trigger, `aria-hidden`
   nothing (bubble is real DOM when shown).
3. **Decorative triggers keep their names.** `IconButton`'s `label`, dots'
   `aria-label`, links' text stay the accessible name; the tooltip is
   supplemental description only.
4. **Keyboard parity.** `:focus-within` shows what `:hover` shows;
   `prefers-reduced-motion` kills the drift/fade.
5. **No hex, no `??` in the component** (global dumb-component rules);
   vars flow inline → bare `var(--tip-*)`, defaults live in CSS fallbacks.

## 5. Apply-to-all

Per eligible group ("dots in this carousel", "navbar items",
"gallery images"): one switch writes the edited `tooltip` group at the
chosen scope (element / section / global); display shows where each value
resolves from. Clearing deletes keys (inherit downward again).

---

## Appendix — file references

- Component: `frontend/storefront/components/ui/Tooltip.tsx`
- Styles: `app/globals.css` (`.sf-tip`, placements, arrow, reduced-motion)
- Showcase: `app/page.tsx` §12 (image hover, dots-below "2 of 3",
  disabled reason, navbar icon)
- Tests: `test/components/tooltip.test.tsx` (3 modes, bare render,
  linkage, data contract)
