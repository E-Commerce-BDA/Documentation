# Shell — reuse/gap map for the Wave 1 rebuild

> Scope: `frontend/storefront/components/shell/*`, `app/_components/*` and the
> shell-side Wave 1 artifacts (Dropdown/Menu, FilterDrawer, ShopToolbar,
> MegaMenu) — the canonical reuse/gap map distilled from the standalone-prototype
> research (`sf-082`, `sf-083`).
> Status: Active | Version 1.1 | Date: 2026-11-27
> Parent: [README.md](README.md) §1/§3 · [shell-cart.md](shell-cart.md) (live residents)
> Implements: doc-009 indexing; the nine artifacts in `components/README.md` §3 — all shipped (sf-087/sf-088) and wired in sf-089–sf-093

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
| AccountMenu | `components/shell/NavAccountButton.tsx` + shipped `components/ui/Menu.tsx` | reused the trigger; the menu is one new primitive, not a second navbar | [shell-cart.md](shell-cart.md) §3 · `components/navigation.md` *(to create)* |
| Search overlays (sheet / editorial / palette) | `components/shell/SearchSheet.tsx`, `SearchEditorial.tsx`, `SearchPalette.tsx` + `searchRegistry.ts` | variants come from the registry; never a page-local overlay | [search-overlays.md](search-overlays.md) §2–§4 |
| Drawers (hamburger / cart) | `components/shell/MobileDrawer.tsx`, `MiniCartDrawer.tsx` + `.sf-drawer`/`.sf-scrim` | shipped `FilterDrawer.tsx` reparents into the same drawer face; no new panel | [shell-cart.md](shell-cart.md) §3–§4 |
| Product card / grid | `components/commerce/ProductCard.tsx`, `ProductGrid.tsx` + `.sf-grid` | one painter; shipped `GridModeToggle.tsx` only switches `data-layout`, it never clones grid rules | [product.md](product.md) §1–§10, §15 |
| Filter rail | `components/commerce/FilterRail.tsx` in `app/(shop)/products/_components/ListingShell.tsx` | shipped `FilterDrawer.tsx` reuses the same controls in a left drawer below 1024px; desktop stays sticky | `components/navigation.md` *(to create)* · [customization.md](customization.md) §Navbar + inner blocks |
| Sort select | `components/ui/Select.tsx` (`native` branch) + `theme.select` | shipped `ShopToolbar.tsx` composes the existing select; no second sort control | [customization.md](customization.md) §Select |
| Brand strip | `components/sections/BrandStripSection.tsx` (`sf-marquee`) | unchanged; PaginatedRail is a separate engine for card rows, not a second marquee | [sections.md](sections.md) §1.5 |
| Compare table | the 4-column compare table + drag surface (`sf-081`) | reuse the table; no infinite-loop pagination — a comparison table has no repeated pages | [customization.md](customization.md) §CMS sections |
| Footer | `components/shell/Footer.tsx` + `app/_components/FooterMount.tsx` | CMS document faces (`data-face="cms"`/`"minimal"`); unchanged by the rebuild | [shell-cart.md](shell-cart.md) §5 |

The primitives Button, Pill, Badge, Input and Toast are reused the same way —
they already carry model / `.sf-*` CSS / doc / barrel, so the rebuild adds no
new row for them.

## 3. Gap map — final outcome for the nine doc-009 artifacts

Each row is one §1 row, one
[0.Project-Overview.md](../0.Project-Overview.md) §14 row and one five-section
manifest in [README.md](README.md) §3, added in the same commit. All nine rows
are ✅ shipped (sf-087/sf-088) and wired into routes by sf-089–sf-093; Palette
(sf-084) is the separate doc-008 foundation gap, also shipped.

| Artifact | Gap it closed | Shipped file(s) + state contract | Owner doc / outcome |
|---|---|---|---|
| SegmentedToggle (sf-087) | no controlled 2–3 way selector existed | `components/ui/SegmentedToggle.tsx` + `lib/shop/models.ts`; `value`/`onChange` parent-owned, props only | `components/form-controls.md` *(to create)*; shipped rule in `frontend/storefront/components/README.md` |
| Dropdown/Menu (sf-087) | NavAccountButton had a trigger but no menu primitive | `components/ui/Menu.tsx` + `lib/shop/models.ts`; `open`/`onOpenChange` parent-owned, trap in the route island | `components/navigation.md` *(to create)*; reused by `NavAccountButton.tsx` |
| FilterDrawer (sf-087, wired sf-092) | desktop filters had no mobile disclosure | `components/ui/FilterDrawer.tsx` + `lib/shop/machine.ts`; pure machine + `useReducer` in `ListingShell.tsx` | `components/navigation.md` *(to create)*; reuses `FilterRail.tsx`, no second drawer face |
| ShopToolbar (sf-087, wired sf-092) | sort, filter button and grid mode were composed per page | `components/ui/ShopToolbar.tsx` + `lib/shop/models.ts`; composed dumb, every value a prop | `components/navigation.md` *(to create)*; one row on `/products` |
| GridModeToggle (sf-087, wired sf-092) | mobile 2↔1 columns existed only in the prototype | `components/ui/GridModeToggle.tsx` + `lib/shop/machine.ts`; `data-layout` on the shared grid | [product.md](product.md) §grid mode *(to append)*; mobile-only gate |
| PaginatedRail (sf-088, wired sf-091) | per-section carousel copies needed one engine | `components/shell/PaginatedRail.tsx` + `lib/sections/railModel.ts` + `lib/sections/machine.ts`; index wrap, not cloned DOM | [sections.md](sections.md) §7.2; CMS carousel via `ProductRailIsland.tsx` |
| MegaMenu (sf-088, wired sf-089) | contracts 2.2.0 nav groups had no dumb renderer | `components/shell/MegaMenu.tsx` + `lib/shell/megaMenuModel.ts` + `lib/shell/resolveNav.ts`; disclosure route-owned, `data-*` only | `components/navigation.md` *(to create)* · [sections.md](sections.md) §7.1; live CMS has no groups configured, so verified by contract/CSSOM probe |
| OrderSummaryCard (sf-088, wired sf-093) | checkout and order pages repeated totals markup | `components/commerce/OrderSummaryCard.tsx` + `lib/order/summaryModel.ts`; props only | [commerce.md](commerce.md) §6; cart + checkout + confirmation share one painter |
| Timeline (sf-088, wired sf-093) | order status had no shared step painter | `components/commerce/Timeline.tsx` + `lib/order/timeline.ts`; props only | [commerce.md](commerce.md) §6; confirmation + account order detail |

No row was added for a second implementation of an existing block: where the
prototype piece already had a Next home, that home was reused unchanged.

## 4. Mount and state rule for shell-side gaps

Shell mounts once at the root layout ([shell-cart.md](shell-cart.md) §2); pages
inherit it and pass settings, never conditional markup. Shipped mounts are
`app/_components/NavbarMount.tsx` (Menu + MegaMenu) and
`app/(shop)/products/_components/ListingShell.tsx` (FilterDrawer + ShopToolbar +
GridModeToggle). Dropdown/Menu, FilterDrawer and MegaMenu are **controlled dumb
blocks**: the route island owns `open`/selection in a pure machine with
`useReducer`, and the block only paints `data-*` faces. Escape and overlay clicks
*call* the parent callback — they are not a state exit. Timers, pointer ids and
listeners live in `useRef` and are cleaned in `useEffect`; no new `useState`, no
local boolean flags
(ADR-ui in [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md),
[customization.md](customization.md) §No-new-`useState` rule).

## Appendix — file references

- Live chrome: [shell-cart.md](shell-cart.md) · overlays:
  [search-overlays.md](search-overlays.md)
- Live blocks and knobs: [product.md](product.md) ·
  [sections.md](sections.md) §7 · [customization.md](customization.md) ·
  [commerce.md](commerce.md) §6
- Shipped gap files: `components/ui/{SegmentedToggle,Menu,FilterDrawer,ShopToolbar,GridModeToggle}.tsx`,
  `components/shell/{MegaMenu,PaginatedRail}.tsx`,
  `components/commerce/{OrderSummaryCard,Timeline,ProductRailIsland}.tsx`;
  models `lib/shop/{models,machine}.ts`, `lib/shell/{megaMenuModel,resolveNav}.ts`,
  `lib/sections/{railModel,machine}.ts`, `lib/order/{summaryModel,timeline}.ts`;
  trios `test/lib/shop/models.test.ts`, `test/lib/shop/machine.test.ts`,
  `test/lib/composed-models.test.ts`, `test/lib/sections/railMachine.test.ts`,
  `test/lib/nav-group-normalization.test.ts` and the `test/components/` suites
  `foundational-components`, `foundational-style`, `composed-components`,
  `composed-style`, `listing-controls`, `listing-chrome-style`,
  `shell-mega-contract`, `shell-mega-style`, `collection-rail`,
  `collection-rail-style`, `money-chrome`, `money-chrome-style`
- Index and conventions: [README.md](README.md) §1–§3 ·
  [0.Project-Overview.md](../0.Project-Overview.md) §14
- Decisions: [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md) ADR-ui,
  ADR-tokens
