# Pill — the one interactive pill

> Scope: `frontend/storefront/components/ui/Pill.tsx` + `.sf-pill` (filter dept pills, trending chips, quick-add actions across overlay variants).
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## 1. Look per variant

| Variant | Face | Use |
|---|---|---|
| `filter` | Ink fill when `active`, bordered text when not | Dept rails (sheet, editorial, palette) |
| `chip` | Bordered pill + trailing icon slot | Trending terms (palette ↗) |
| `action` | Tinted fill; `data-state="added"` flips to success face | Quick Add (palette) |

`kbd` hints (`ESC`, `↵`) are display `<kbd>`, never Pills — not interactive, no button semantics.

## 2. Customizable fields

None on the Pill itself: theming rides `--pill-*` vars inlined by the parent overlay (which resolves them from CMS settings). Fallbacks mirror Oceanic tokens. The Pill knows no knobs — same precedent as sheet motion vars (presentation via props, no lib module).

## 3. Scopes

Renders a native `<button>` and forwards `className`/`aria-pressed`/handlers, so existing `.sf-* button` selectors and role queries keep matching. Retrofit rule: adopting Pill in a live overlay must change zero tests — the suite is the proof.

## 4. Global rules (apply-to-all)

- State reaches CSS only through `data-variant`/`data-active`/`data-state` — never class toggles.
- `:hover` stays off the active face and off `[disabled]` (bare `:hover` matches both; repainting active ink-on-ink or dimming disabled destroys the face).
- Disabled faces are explicit solids (contrast ban on `opacity`), focus-visible ring fixed.
- No transitions: instant state swap, nothing for reduced-motion to kill.

## 5. Apply-to-all

New selectable pill UI uses Pill — no second pill implementation. If a design needs a face Pill lacks, extend `PillVariant` (additive union), never a sibling component.
