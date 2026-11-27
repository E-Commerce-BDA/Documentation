# Shell — reuse/gap map for the Wave 1 rebuild

> Scope: `frontend/storefront/components/shell/*`, `app/_components/*` and the
> shell-side Wave 1 artifacts (Dropdown/Menu, FilterDrawer, ShopToolbar,
> MegaMenu) — the canonical reuse/gap map distilled from the standalone-prototype
> research (`sf-082`, `sf-083`).
> Status: Active (docs-first — planned rows, no code landed) | Version 1.0 | Date: 2026-11-27
> Parent: [README.md](README.md) §1/§3 · [shell-cart.md](shell-cart.md) (live residents)
> Implements: doc-009 indexing; the nine planned artifacts in `components/README.md` §3

---

## 1. Reuse before build (normative)

The standalone HTML prototype was rebuilt to match the Next surfaces
(`sf-082`) and then gained mobile filters, a marquee and one draggable rail
engine (`sf-083`). The rebuild ports the *language*, not the prototype's markup:
a prototype piece that already has a Next home is reused unchanged — same
model, same `.sf-*` CSS block, same rule doc, same barrel export. A new artifact
is indexed only where no current doc covers the piece. Reason: per-surface
copies are the drift source the consistency wave (`sf-081`) already removed.
Rejected: pasting prototype HTML into a route, or re-indexing an existing block
under a second name.

The live resident list stays authoritative in [shell-cart.md](shell-cart.md) §3;
this doc owns the *decision* of what is reused versus newly built, and the
mount/state rules that decision implies.

## 2. Reuse map — prototype piece → existing Next home

| Prototype piece | Existing Next home | Reuse rule | Owner doc |
|---|---|---|---|
| Navbar | `components/shell/Navbar.tsx` + `app/_components/NavbarMount.tsx` | one chrome for every route; no per-page nav overrides | [shell-cart.md](shell-cart.md) §3–§4 |
| AccountMenu | `components/shell/NavAccountButton.tsx` + the planned Dropdown/Menu primitive | reuse the trigger; the menu is the missing primitive, not a second navbar | [shell-cart.md](shell-cart.md) §3 · `components/navigation.md` *(to create)* |
| Search overlays (sheet / editorial / palette) | `components/shell/SearchSheet.tsx`, `SearchEditorial.tsx`, `SearchPalette.tsx` + `searchRegistry.ts` | variants come from the registry; never a page-local overlay | [search-overlays.md](search-overlays.md) §2–§4 |
| Drawers (hamburger / cart) | `components/shell/MobileDrawer.tsx`, `MiniCartDrawer.tsx` + `.sf-drawer`/`.sf-scrim` | FilterDrawer reparents into the same shell drawer face; no new panel | [shell-cart.md](shell-cart.md) §3–§4 |
| Product card / grid | `components/ui/ProductCard.tsx`, `ProductGrid.tsx` + `.sf-grid` | one painter; GridModeToggle only switches `data-layout`, it never clones grid rules | [product.md](product.md) §1–§10, §15 |
| Filter rail | the desktop sticky filter sidebar on `/products` | FilterDrawer moves the *same* controls into a left drawer below 1024px; desktop stays sticky | `components/navigation.md` *(to create)* · [customization.md](customization.md) §Navbar + inner blocks |
| Sort select | `components/ui/Select.tsx` (`native` branch) + `theme.select` | ShopToolbar composes the existing select; no second sort control | [customization.md](customization.md) §Select |
| Brand strip | `components/sections/BrandStripSection.tsx` (`sf-marquee`) | unchanged; PaginatedRail is a separate engine for card rows, not a second marquee | [sections.md](sections.md) §1.5 |
| Compare table | the 4-column compare table + drag surface (`sf-081`) | reuse the table; no infinite-loop pagination — a comparison table has no repeated pages | [customization.md](customization.md) §CMS sections |
| Footer | `components/shell/Footer.tsx` + `app/_components/FooterMount.tsx` | CMS document faces (`data-face="cms"`/`"minimal"`); unchanged by the rebuild | [shell-cart.md](shell-cart.md) §5 |

The primitives Button, Pill, Badge, Input and Toast are reused the same way —
they already carry model / `.sf-*` CSS / doc / barrel, so the rebuild adds no
new row for them.

## 3. Gap map — the nine planned artifacts

Each row is one §1 row, one
[0.Project-Overview.md](../0.Project-Overview.md) §14 row and one five-section
manifest in [README.md](README.md) §3, added in the same commit. All rows are ⬜
planned (docs-first); Palette (sf-084) is the separate doc-008 foundation gap.

| Artifact | Why it is a gap | State contract | Owner doc |
|---|---|---|---|
| SegmentedToggle (sf-087) | no controlled 2–3 way selector exists | `value`/`onChange` parent-owned; props only | `components/form-controls.md` *(to create)* |
| Dropdown/Menu (sf-087) | NavAccountButton has a trigger but no menu primitive | `open`/`onOpenChange` parent-owned; trap in the route island | `components/navigation.md` *(to create)* |
| FilterDrawer (sf-087) | desktop filters have no mobile disclosure | pure `filterDrawer` machine + `useReducer`; `open` parent-owned | `components/navigation.md` *(to create)* |
| ShopToolbar (sf-087) | sort, filter button and grid mode were composed per page | composed dumb; every value a prop | `components/navigation.md` *(to create)* |
| GridModeToggle (sf-087) | mobile 2↔1 columns existed only in the prototype | `gridMode` machine + `useReducer`; `data-layout` on the shared grid | [product.md](product.md) §grid mode |
| PaginatedRail (sf-088) | per-section carousel copies need one engine | `rail` machine + `useReducer`; `useRef`/`useEffect` for drag/timers | [sections.md](sections.md) §7.2 |
| MegaMenu (sf-088) | contracts 2.2.0 nav groups have no dumb renderer | disclosure route-owned; `data-*` only | `components/navigation.md` *(to create)* · [sections.md](sections.md) §7.1 |
| OrderSummaryCard (sf-088) | checkout and order pages repeated totals markup | pure totals resolver; props only | [commerce.md](commerce.md) §6 |
| Timeline (sf-088) | order status had no shared step painter | pure status → steps resolver; props only | [commerce.md](commerce.md) §6 |

## 4. Mount and state rule for shell-side gaps

Shell mounts once at the root layout ([shell-cart.md](shell-cart.md) §2); pages
inherit it and pass settings, never conditional markup. Dropdown/Menu,
FilterDrawer and MegaMenu are **controlled dumb blocks**: the route island owns
`open`/selection in a pure machine with `useReducer`, and the block only paints
`data-*` faces. Escape and overlay clicks *call* the parent callback — they are
not a state exit. Timers, pointer ids and listeners live in `useRef` and are
cleaned in `useEffect`; no new `useState`, no local boolean flags
(ADR-ui in [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md),
[customization.md](customization.md) §No-new-`useState` rule).

## Appendix — file references

- Live chrome: [shell-cart.md](shell-cart.md) · overlays:
  [search-overlays.md](search-overlays.md)
- Live blocks and knobs: [product.md](product.md) ·
  [sections.md](sections.md) · [customization.md](customization.md) ·
  [commerce.md](commerce.md)
- Index and conventions: [README.md](README.md) §1–§3 ·
  [0.Project-Overview.md](../0.Project-Overview.md) §14
- Decisions: [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md) ADR-ui,
  ADR-tokens
