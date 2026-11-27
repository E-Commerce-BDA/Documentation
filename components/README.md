# Components — Index & Conventions

> Scope: every `components/*.md` rule doc (one per UI component).
> Status: Active | Version 1.2 | Date: 2026-11-08
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
| Palette (`--sf-*` resolver + emitter, legacy aliases) | `../design-system/storefront.md` §3.0 + `customization.md` | ⬜ planned (sf-084, doc-008) |
| SegmentedToggle (controlled 2–3 way selector) | `form-controls.md` *(to create)* | ⬜ planned (sf-087, doc-009) |
| Dropdown/Menu (controlled disclosure + keyboard trap) | `navigation.md` *(to create)* + `shell.md` §2 | ⬜ planned (sf-087, doc-009) |
| FilterDrawer (mobile, reuses desktop filters) | `navigation.md` *(to create)* + `shell.md` §2 | ⬜ planned (sf-087, doc-009) |
| ShopToolbar (sort + filter + grid row) | `navigation.md` *(to create)* + `shell.md` §2 | ⬜ planned (sf-087, doc-009) |
| GridModeToggle (`data-layout` 2↔1, mobile-only) | `product.md` *(to append)* | ⬜ planned (sf-087, doc-009) |
| PaginatedRail (drag, loop, dots, reduced motion) | `sections.md` §7.2 | ⬜ planned (sf-088, doc-009) |
| MegaMenu (contracts 2.2.0 nav groups/columns) | `navigation.md` *(to create)* + `sections.md` §7.1 | ⬜ planned (sf-088, doc-009) |
| OrderSummaryCard (totals resolver + block) | `commerce.md` §6 | ⬜ planned (sf-088, doc-009) |
| Timeline (status → steps resolver + block) | `commerce.md` §6 | ⬜ planned (sf-088, doc-009) |

**Reuse/gap map:** the canonical map from the standalone-prototype research
(`sf-082`, `sf-083`) lives in [shell.md](shell.md) §2–§3 and is mirrored in
[commerce.md](commerce.md) §6. The rebuild reuses Navbar, AccountMenu, search
overlays, drawers, ProductCard/ProductGrid, the filter rail, the sort `Select`,
BrandStrip, the compare table and Footer unchanged (same model / `.sf-*` CSS /
doc / barrel). The nine doc-009 rows above are new artifacts only where no
current doc covers the piece; Palette (sf-084) is the earlier doc-008 foundation
gap. No second implementation of an existing block: if a prototype piece is
already covered, it is reused, not re-indexed.

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

Docs-first (doc-009): none of the source paths below exists yet — every entry
is ⬜ **planned**, each backed by the §1 row and the
[§14 row](../0.Project-Overview.md) recorded in the same commit. Each owner doc
will use the [button.md](button.md) 5-section shape (§1 look per type, §2
customizable fields, §3 scopes, §4 global rules, §5 apply-to-all); the five rows
in each entry are the shipped-artifact manifest of the storefront constitution
(AGENTS.md §3 rule 7): **lib model · CSS block · state contract · tests · owner
doc**. Paint is `--sf-*` only
([storefront.md](../design-system/storefront.md) §3.0); state reaches CSS only
through `data-*`.

### SegmentedToggle (sf-087 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/ui/segmented.ts` — pure `resolveSegmented({ options, value, size })` → `SegmentedModel` with `data-selected`; defaults only here |
| CSS block | `.sf-segmented` / `.sf-segmented__option` in `app/globals.css`; fills via `--sf-segmented-*`, focus ring fixed |
| state contract | controlled: `value` + `onChange` parent-owned; no `useState`, no hidden selection inside the block |
| tests | `test/lib/ui/segmented.test.ts` · `test/components/segmented-toggle.test.tsx` · `test/components/segmented-toggle-style.test.ts` |
| owner doc | `components/form-controls.md` *(to create)* — 5-section shape; barrel `components/ui/index.ts` |

### Dropdown/Menu (sf-087 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/ui/menu.ts` — pure `resolveMenu({ placement, items, maxItems })`; item/link shape resolved once |
| CSS block | `.sf-menu` / `.sf-menu__item` in `app/globals.css`; `--sf-menu-*` over house tokens; `data-open` hook |
| state contract | `open` / `onOpenChange` parent-owned; Escape and overlay **call** the parent callback (no state exit); trap + focus return in the route island |
| tests | `test/lib/ui/menu.test.ts` · `test/components/menu.test.tsx` · `test/components/menu-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* — 5-section shape; barrel `components/ui/index.ts` |

### FilterDrawer (sf-087 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/shop/filterDrawer.ts` — pure `filterDrawer` machine (`closed`/`open`, `OPEN`/`CLOSE`/`TOGGLE`/`RESET`/`APPLY`) + resolver for the reused desktop filter controls |
| CSS block | `.sf-filterdrawer` in `app/globals.css`, reusing `.sf-drawer` / `.sf-scrim` — no second drawer face |
| state contract | pure machine + `useReducer` in the route island; `open` parent-owned; pointer/focus handles in `useRef`, listeners in `useEffect` |
| tests | `test/lib/shop/filterDrawer.test.ts` · `test/components/filter-drawer.test.tsx` · `test/components/filter-drawer-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* + [shell.md](shell.md) §2 (reuse) |

### ShopToolbar (sf-087 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/shop/toolbar.ts` — pure `resolveToolbar({ sortOptions, count, regions })`; composes the existing `Select`, FilterDrawer trigger and GridModeToggle |
| CSS block | `.sf-toolbar` in `app/globals.css`; row geometry fixed here, paint via `--sf-*`; one shared gutter with the grid |
| state contract | composed dumb: every value (`sort`, `onSortChange`, `filterOpen`, `onOpenFilters`, `layout`, `onLayoutChange`, `count`) is a prop; zero local state |
| tests | `test/lib/shop/toolbar.test.ts` · `test/components/shop-toolbar.test.tsx` · `test/components/shop-toolbar-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* + [shell.md](shell.md) §2 |

### GridModeToggle (sf-087 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/shop/gridMode.ts` — pure `gridMode` machine (`2` ↔ `1`) with a mobile-only gate; never writes `data-layout` itself |
| CSS block | `.sf-gridmode` in `app/globals.css`; `data-layout` on the shared `.sf-grid` (no duplicated grid rules) |
| state contract | pure machine + `useReducer`; value parent-owned; desktop keeps its theme grid |
| tests | `test/lib/shop/gridMode.test.ts` · `test/components/grid-mode-toggle.test.tsx` · `test/components/grid-mode-toggle-style.test.ts` |
| owner doc | `components/product.md` §grid mode *(to append)* |

### PaginatedRail (sf-088 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/sections/rail.ts` — pure `rail` machine (`idle`/`dragging`/`settling`; `POINTER_*`, `NEXT`, `PREV`, `SNAP_DONE`, `WRAP`) + page/dot resolver |
| CSS block | `.sf-rail` in `app/globals.css`; `--rail-*` over house tokens, one `@keyframes`, static reduced-motion face |
| state contract | pure machine + `useReducer`; drag id and timers in `useRef`, listeners/cleanup in `useEffect`; no local boolean flags |
| tests | `test/lib/sections/rail.test.ts` · `test/components/paginated-rail.test.tsx` · `test/components/paginated-rail-style.test.ts` |
| owner doc | [sections.md](sections.md) §7.2 + [customization.md](customization.md) §PaginatedRail drag/pagination/motion |

### MegaMenu (sf-088 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/nav/megaMenu.ts` — pure `resolveMegaMenu` over contracts 2.2.0 `navLinkSchema.groups[]` (≤6 groups, 1–12 items, `columns` 1–4, optional promo); clamps, no JSX |
| CSS block | `.sf-megamenu` / `.sf-megamenu__*` in `app/globals.css`; `--megamenu-cols` is clamped, never a raw admin column count |
| state contract | dumb `MegaMenu` / `MegaMenuColumn`; disclosure owned by the route; `data-open` state only; keyboard parity fixed |
| tests | `test/lib/nav/megaMenu.test.ts` · `test/components/mega-menu.test.tsx` · `test/components/mega-menu-style.test.ts` |
| owner doc | `components/navigation.md` *(to create)* + [sections.md](sections.md) §7.1 |

### OrderSummaryCard (sf-088 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/commerce/totals.ts` — pure subtotal/discount/shipping/tax/total resolver over contracts `moneySchema`; defaults live only here |
| CSS block | `.sf-ordersummary` in `app/globals.css`; `--sf-ordersummary-*` over house tokens, no hardcoded paint |
| state contract | props only; no state, no fetch — the route resolves the order/cart totals and passes them in |
| tests | `test/lib/commerce/totals.test.ts` · `test/components/order-summary-card.test.tsx` · `test/components/order-summary-card-style.test.ts` |
| owner doc | [commerce.md](commerce.md) §6 |

### Timeline (sf-088 · planned)

| Section | Contract |
|---|---|
| lib model | `lib/commerce/timeline.ts` — pure order-status → steps resolver (completed/current/upcoming), one default source |
| CSS block | `.sf-timeline` in `app/globals.css`; `--sf-timeline-*` over house tokens; `data-step` drives every state face |
| state contract | props only; no state — the status comes from the order view model |
| tests | `test/lib/commerce/timeline.test.ts` · `test/components/timeline.test.tsx` · `test/components/timeline-style.test.ts` |
| owner doc | [commerce.md](commerce.md) §6 |
