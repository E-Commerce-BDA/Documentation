# Toast — bottom-center notification

> Scope: `frontend/storefront/components/ui/Toast.tsx` + `.sf-toast` (quick-add confirmations first, cart/auth notices later).
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## 1. Look

White card, bottom-center, above overlays (z-60): optional leading glyph slot, bold title + muted message, X dismiss. Fade + 8px rise, killed under reduced-motion.

## 2. Customizable fields

None on the Toast itself: `open/title/message/icon/onClose` arrive as props; paint rides Oceanic tokens. Per-surface tinting (if ever needed) arrives as a parent-passed `className`, never as Toast knobs.

## 3. Scopes

Dumb and timerless: renders nothing when closed, fires `onClose` only from the X. Auto-dismiss timing belongs to the owner (showcase demo effect, production assembler) — a Toast that dismisses itself would hide state the owner must own. `role="status"` announces politely; never `alert` (confirmations don't interrupt).

## 4. Global rules (apply-to-all)

- Owner-triggered: quick-add confirmations surface only when the surface's `notifyOnQuickAdd` knob is on (palette default on, locked).
- One Toast at a time per surface (latest message wins; no stacking — stacking needs a queue design, filed when a second producer arrives).
- New notice UI uses Toast — no second toast implementation.

## 5. Apply-to-all

Cart/auth/future notices reuse this primitive with their own copy + icon. If notices need severity faces, extend via `data-*` attrs, never a sibling component.
