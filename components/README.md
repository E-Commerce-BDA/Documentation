# Components — Index & Conventions

> Scope: every `components/*.md` rule doc (one per UI component).
> Status: Active | Version 1.3 | Date: 2026-11-27
> Parent: `0.Project-Overview.md` §14 (Docs Index)

---

## 1. Status matrix

| Component | Doc | Status |
|---|---|---|
| Button (+animation/disabled/pressed model) | `button.md` | ✅ done (+ template owner) |
| Icons (26, lucide wrapper) | `icons.md` | ✅ done |
| Tooltip (+style knobs) | `tooltip.md` | ✅ done |
| Pill (filter/chip/action interactive pill) | `pill.md` | ✅ done |
| Toast (bottom-center notification) | `toast.md` | ✅ done |
| Customization matrix (living knob inventory) | `customization.md` | ✅ done (progressive — slices append rows) |
| Search overlays (variant matrix + selection + registry) | `search-overlays.md` | ✅ done |
| Input / Textarea / Select | `input.md` *(to create)* | ⬜ |
| Checkbox / Radio / Toggle / Slider | `form-controls.md` *(to create, grouped)* | ⬜ |
| Badge / Card / Dialog / IconButton | `feedback.md` *(to create, grouped)* | ⬜ |
| Tabs / Skeleton / Pagination / Breadcrumbs / Accordion | `navigation.md` *(to create, grouped)* | ⬜ (Breadcrumbs meanwhile shipped as a shell block — `shell-cart.md` §3) |
| QuantityStepper / EmptyState | `commerce.md` §1–§2 | ✅ done |
| Rating / Price / Table | `commerce.md` *(same doc, later sections)* | ⬜ |
| SearchAutocomplete / CheckoutSteps | `commerce.md` *(to append, grouped)* | ⬜ |
| ProductCard / Gallery / VariantSelector / ProductGrid | `product.md` | ✅ done (§1–§10 card, §14 gallery + variant selector, §15 grid + `fromCatalog`) |
| Section blocks: Hero (+ carousel island) | `sections.md` §1.1–§1.2 | ✅ done (v2 — CMS slides, multi-slide island) |
| ProductCollection / CategoryShowcase / BrandStrip / Testimonial / BlogTeaser / SectionRenderer + PDP sections (description/details/reviews/related/trust/story/FAQ) | `sections.md` §1.3–§1.8, §2, §3.2 (contracts 1.14.0) | ✅ done (sf-060; grouped, one doc per §3 rule 4) |
| BannerSection | `sections.md` §0 (refused in the resolver) | ⬜ sf-061 |
| Shell purpose + mount rule + search overlays + cart blocks | `shell-cart.md` | ✅ done (§4 live: PageHeader, CartLineItem, MiniCartDrawer, CartProvider; §5 live: Footer + FooterMount — sf-062) |
| Footer (+ FooterMount) | `shell-cart.md` §5 | ✅ done (sf-062 — CMS document, minimal-face fallback, shared gutter) |
| BlogCard / PostBlocks / PageBlocks / CmsPage | `sections.md` §1.7 + `shell-cart.md` §3 + route tests (`test/components/{post,page}-blocks.test.tsx`, `test/app/(shop)/{blog,legal}.test.tsx`) | ✅ done (sf-063 — grouped, no standalone doc yet per §2 rule 4) |
| Palette (`--sf-*` resolver + emitter, legacy aliases) | `../design-system/storefront.md` §3.0 + `customization.md` | ✅ shipped (sf-084) — `lib/theme/palette.ts`, `lib/theme/vars.ts`, `lib/cms/themeVars.ts`, CSS mirrors in `app/globals.css` |
| SegmentedToggle (controlled 2–3 way selector) | `form-controls.md` *(to create)* | ✅ shipped (sf-087) — `components/ui/SegmentedToggle.tsx`; model `lib/shop/models.ts`; manifest in this README §3. Owner doc still deferred |
| Dropdown/Menu (controlled disclosure + keyboard trap) | `navigation.md` *(to create)* + `shell.md` §2 | ✅ shipped (sf-087) — `components/ui/Menu.tsx`; model `lib/shop/models.ts`; manifest in this README §3. Owner doc still deferred |
| FilterDrawer (mobile, reuses desktop filters) | `navigation.md` *(to create)* + `shell.md` §2 | ✅ shipped (sf-087, wired sf-092) — `components/ui/FilterDrawer.tsx`; models `lib/shop/models.ts` + `lib/shop/machine.ts`; mounted by `app/(shop)/products/_components/ListingShell.tsx`. Owner doc still deferred |
| ShopToolbar (sort + filter + grid row) | `navigation.md` *(to create)* + `shell.md` §2 | ✅ shipped (sf-087, wired sf-092) — `components/ui/ShopToolbar.tsx`; same models and listing shell. Owner doc still deferred |
| GridModeToggle (`data-layout` 2↔1, mobile-only) | `product.md` *(to append)* | ✅ shipped (sf-087, wired sf-092) — `components/ui/GridModeToggle.tsx`; `data-layout` on the shared grid; `product.md` section still deferred |
| PaginatedRail (drag, loop, dots, reduced motion) | `sections.md` §7.2 + `customization.md` | ✅ shipped (sf-088, wired sf-091) — `components/shell/PaginatedRail.tsx`, island `components/commerce/ProductRailIsland.tsx`; models `lib/sections/railModel.ts` + `lib/sections/machine.ts` |
| MegaMenu (contracts 2.2.0 nav groups/columns) | `navigation.md` *(to create)* + `sections.md` §7.1 | ✅ shipped (sf-088, wired sf-089) — `components/shell/MegaMenu.tsx`; models `lib/shell/megaMenuModel.ts` + `lib/shell/resolveNav.ts`; mounted by `app/_components/NavbarMount.tsx` + `components/shell/NavLinks.tsx`. Owner doc still deferred |
| OrderSummaryCard (totals resolver + block) | `commerce.md` §6 | ✅ shipped (sf-088, wired sf-093) — `components/commerce/OrderSummaryCard.tsx`; model `lib/order/summaryModel.ts` |
| Timeline (status → steps resolver + block) | `commerce.md` §6 | ✅ shipped (sf-088, wired sf-093) — `components/commerce/Timeline.tsx`; model `lib/order/timeline.ts` |

**Reuse/gap map (final outcome):** the canonical map from the standalone-prototype
research (`sf-082`, `sf-083`) lives in [shell.md](shell.md) §2–§3 and is mirrored
in [commerce.md](commerce.md) §6. The rebuild reuses Navbar, AccountMenu,
search overlays, drawers, ProductCard/ProductGrid, the filter rail, the sort
`Select`, BrandStrip, the compare table and Footer unchanged (same model /
`.sf-*` CSS / doc / barrel). All nine doc-009 gaps above **shipped** as real
files (sf-087/sf-088) and were wired into routes in sf-089–sf-093; Palette
(sf-084) shipped as the earlier doc-008 foundation. No second implementation of
an existing block was created: where a prototype piece was already covered it
was reused, not re-indexed. Still explicitly deferred: `form-controls.md` and
`navigation.md` owner docs, the `product.md` grid-mode section, `banner`
(sf-061), and navigation/footer draft patches repainting nav chrome
([storefront.md](../design-system/storefront.md) §3.0 Wave 4 amendment).

**Wave mapping of the rebuild:** Wave 1 = sf-087/sf-088 (the nine artifacts) plus
sf-089/sf-090 (navbar + overlays/drawers); Wave 2 = sf-091/sf-092/sf-093
(home rails, listing/PDP, cart/checkout/confirmation); Wave 3 = sf-094/sf-095
(account/compare, auth/blog/legal); Wave 4 = sf-096 (preview draft patch,
`frame-ancestors` CSP, 2.2.0 config envelope). All four waves shipped.

Small related components share one grouped doc (see §2 rule 4); Button,
Icons, and Tooltip earned standalone docs as system pioneers (first model,
first wrapper, first zero-JS positioning).

## 2. Doc conventions (enforced in review)

1. **Header block mandatory** — `Scope | Status | Version | Date | Parent`
   on every component doc.
2. **Index rule** — every new doc adds exactly one row to §1 above **and**
   one row to `0.Project-Overview.md` §14 in the same commit. Future docs
   are listed as `(to create)` rows up front so gaps stay visible.
3. **Backlinks** — every doc names its Parent; parents name children.
4. **One doc per component, small relatives grouped** — no misc catch-alls.
   (Working scratch notes stay unindexed personal files, e.g. `temp.md` —
   they graduate into numbered docs or stay out of nav.)
5. **Template** — standalone docs follow the `button.md` 5-section shape
   (look per type / customizable fields / scopes / global rules /
   apply-to-all); grouped docs repeat that shape per component inside.
6. **No new `useState`** — rebuilt islands keep state in pure machines and
   `useReducer`, with parent-owned props for `open`/selection; timers, pointer
   ids and listeners live in `useRef`/`useEffect`. A `useState` addition needs an
   ADR with a documented reason ([customization.md](customization.md)
   §No-new-`useState` rule;
   [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md) ADR-ui).

---

## 3. Wave 1 artifact entries (5-section shape)

doc-009 was docs-first; all nine entries below are now ✅ **shipped** (sf-087 /
sf-088) and wired into routes in sf-089–sf-093. Each §1 row and its
[§14 row](../0.Project-Overview.md) were recorded in the docs commit; the paths
below are the *actual* shipped files, which differ from the original planned
names (the resolver and barrel layout consolidated them). Each entry keeps the
[button.md](button.md) 5-section shape (§1 look per type, §2 customizable
fields, §3 scopes, §4 global rules, §5 apply-to-all); the five rows are the
shipped-artifact manifest of the storefront constitution (AGENTS.md §3 rule 7):
**lib model · CSS block · state contract · tests · owner doc**. Paint is
`--sf-*` only ([storefront.md](../design-system/storefront.md) §3.0); state
reaches CSS only through `data-*`. Where the Documentation owner doc is still
deferred, the repo-local five-section entry in
`frontend/storefront/components/README.md` carries the rule until it graduates.

### SegmentedToggle (sf-087 · shipped)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/shop/models.ts` — pure `resolveSegmentedToggle({ options, size, ariaLabel })`, 1–6 option clamp; defaults only here |
| CSS block | `.sf-segmented` / `.sf-segmented__option` in `app/globals.css`; fills via `--segmented-*`, focus ring fixed |
| state contract | controlled: `value` + `onChange` parent-owned; no `useState`, no hidden selection inside the block |
| tests | `test/lib/shop/models.test.ts` · `test/components/foundational-components.test.tsx` · `test/components/foundational-style.test.ts` |
| owner doc | `components/form-controls.md` *(to create)* — 5-section shape lives meanwhile in `frontend/storefront/components/README.md` §Shop chrome primitives; barrel `components/ui/index.ts` |

### Dropdown/Menu (sf-087 · shipped)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/shop/models.ts` — pure `resolveMenu({ align, ariaLabel })`; disclosure and item/link shape stay with the owner |
| CSS block | `.sf-menu` / `.sf-menu__item` in `app/globals.css`; `--menu-*` over house tokens; `data-open` hook |
| state contract | `open` / `onOpenChange` parent-owned; Escape and overlay **call** the parent callback (no state exit); trap + focus return in the route island |
| tests | `test/lib/shop/models.test.ts` · `test/components/foundational-components.test.tsx` · `test/components/foundational-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* — 5-section shape lives meanwhile in `frontend/storefront/components/README.md` §Shop chrome primitives; barrel `components/ui/index.ts`. Reused by `components/shell/NavAccountButton.tsx` |

### FilterDrawer (sf-087 · shipped, wired sf-092)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/shop/machine.ts` — pure drawer/grid modes + `lib/shop/models.ts` resolver for the reused desktop filter controls (no separate `filterDrawer.ts`) |
| CSS block | `.sf-filterdrawer` in `app/globals.css`, reusing `.sf-drawer` / `.sf-scrim` — no second drawer face |
| state contract | pure machine + `useReducer` in `app/(shop)/products/_components/ListingShell.tsx`; `open` parent-owned; pointer/focus handles in `useRef`, listeners in `useEffect` |
| tests | `test/lib/shop/machine.test.ts` · `test/components/listing-controls.test.tsx` · `test/components/listing-chrome-style.test.ts` · `test/app/(shop)/products/listing-shell.test.tsx` |
| owner doc | `components/navigation.md` *(to create)* + [shell.md](shell.md) §2 (reuse) |

### ShopToolbar (sf-087 · shipped, wired sf-092)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/shop/models.ts` + `lib/shop/machine.ts` — pure resolvers/modes; composes the existing `Select`, FilterDrawer trigger and GridModeToggle (no separate `toolbar.ts`) |
| CSS block | `.sf-toolbar` in `app/globals.css`; row geometry fixed here, paint via `--*` over house tokens; one shared gutter with the grid |
| state contract | composed dumb: every value (`sort`, `onSortChange`, `filterOpen`, `onOpenFilters`, `layout`, `onLayoutChange`, `count`) is a prop; zero local state |
| tests | `test/lib/shop/models.test.ts` · `test/components/listing-controls.test.tsx` · `test/components/listing-chrome-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* + [shell.md](shell.md) §2 |

### GridModeToggle (sf-087 · shipped, wired sf-092)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/shop/machine.ts` — pure `2` ↔ `1` mode with a mobile-only gate (`lib/shop/models.ts` re-exports `GridMode`); never writes `data-layout` itself |
| CSS block | `.sf-gridmode` in `app/globals.css`; `data-layout` on the shared `.sf-grid` (no duplicated grid rules) |
| state contract | pure machine + `useReducer`; value parent-owned; desktop keeps its theme grid |
| tests | `test/lib/shop/machine.test.ts` · `test/lib/shop/gridModeParse.test.ts` · `test/components/listing-controls.test.tsx` · `test/components/listing-chrome-style.test.ts` |
| owner doc | `components/product.md` §grid mode *(to append)* |

### PaginatedRail (sf-088 · shipped, wired sf-091)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/sections/railModel.ts` (page/dot resolver + clamp) and `lib/sections/machine.ts` (`railIndexMachine`); the prototype's idle/dragging/settling events are resolved by index wrap, not cloned DOM |
| CSS block | `.sf-rail` in `app/globals.css`; `--rail-*` over house tokens, static reduced-motion face |
| state contract | pure machine + `useReducer` in `components/shell/PaginatedRail.tsx`; drag id and timers in `useRef`, listeners/cleanup in `useEffect`; no local boolean flags |
| tests | `test/lib/composed-models.test.ts` · `test/lib/sections/railMachine.test.ts` · `test/components/composed-components.test.tsx` · `test/components/composed-style.test.ts` · `test/components/collection-rail.test.tsx` · `test/components/collection-rail-style.test.ts` |
| owner doc | [sections.md](sections.md) §7.2 + [customization.md](customization.md) §PaginatedRail drag/pagination/motion |

### MegaMenu (sf-088 · shipped, wired sf-089)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/shell/megaMenuModel.ts` — `normalizeNavGroups` + `resolveMegaMenu` over contracts 2.2.0 `navLinkSchema.groups[]` (≤6 groups, 1–12 items, `columns` 1–4, optional promo); clamps, no JSX. Trailing hrefs must be internal or http(s) |
| CSS block | `.sf-megamenu` / `.sf-megamenu__*` in `app/globals.css`; `--megamenu-cols` is clamped, never a raw admin column count |
| state contract | dumb `components/shell/MegaMenu.tsx`; disclosure owned by `app/_components/NavbarMount.tsx` + `components/shell/NavLinks.tsx`; `data-open`/`data-active` only; keyboard parity fixed |
| tests | `test/lib/composed-models.test.ts` · `test/lib/nav-group-normalization.test.ts` · `test/components/composed-components.test.tsx` · `test/components/composed-style.test.ts` · `test/components/shell-mega-contract.test.tsx` · `test/components/shell-mega-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* + [sections.md](sections.md) §7.1 |

### OrderSummaryCard (sf-088 · shipped, wired sf-093)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/order/summaryModel.ts` — pure `resolveOrderSummary` (subtotal/discount/shipping/tax/total + clamped free-ship progress); defaults live only here |
| CSS block | `.sf-ordersummary` in `app/globals.css`; `--summary-progress` over house tokens, no hardcoded paint |
| state contract | props only; no state, no fetch — the route resolves the order/cart totals and passes them in |
| tests | `test/lib/composed-models.test.ts` · `test/components/composed-components.test.tsx` · `test/components/composed-style.test.ts` · `test/components/money-chrome.test.tsx` · `test/components/money-chrome-style.test.ts` |
| owner doc | [commerce.md](commerce.md) §6 |

### Timeline (sf-088 · shipped, wired sf-093)

| Section | Shipped artifact |
|---|---|
| lib model | `lib/order/timeline.ts` — pure status → steps resolver (completed/current/upcoming), one default source |
| CSS block | `.sf-timeline` in `app/globals.css`; `--sf-timeline-*` over house tokens; `data-state` drives every state face |
| state contract | props only; no state — the status comes from the order view model |
| tests | `test/lib/composed-models.test.ts` · `test/components/composed-components.test.tsx` · `test/components/composed-style.test.ts` · `test/components/money-chrome.test.tsx` · `test/components/money-chrome-style.test.ts` |
| owner doc | [commerce.md](commerce.md) §6 |
