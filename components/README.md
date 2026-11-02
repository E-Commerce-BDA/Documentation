# Components — Index & Conventions

> Scope: every `components/*.md` rule doc (one per UI component).
> Status: Active | Version 1.0 | Date: 2026-09-18
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
| Tabs / Skeleton / Pagination / Breadcrumbs / Accordion | `navigation.md` *(to create, grouped)* | ⬜ |
| QuantityStepper / EmptyState | `commerce.md` §1–§2 | ✅ done |
| Rating / Price / Table | `commerce.md` *(same doc, later sections)* | ⬜ |
| SearchAutocomplete / CheckoutSteps | `commerce.md` *(to append, grouped)* | ⬜ |
| ProductCard / Gallery / VariantSelector / ProductGrid | `product.md` | ✅ done (§1–§10 card, §14 gallery + variant selector, §15 grid + `fromCatalog`) |
| Section blocks: Hero (+ carousel island) | `sections.md` §1.1–§1.2 | ✅ done (v2 — CMS slides, multi-slide island) |
| ProductCollection / CategoryShowcase / BrandStrip / Testimonial / BlogTeaser / SectionRenderer | `sections.md` §1.3–§1.8, §2 | ✅ done (sf-060; grouped, one doc per §3 rule 4) |
| BannerSection | `sections.md` §0 (refused in the resolver) | ⬜ sf-061 |
| Shell purpose + mount rule + search overlays + cart blocks | `shell-cart.md` | ✅ done (§4 live: PageHeader, CartLineItem, MiniCartDrawer, CartProvider) |

Small related components share one grouped doc (see §3 rule 4); Button,
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
