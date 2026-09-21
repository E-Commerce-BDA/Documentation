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
| Input / Textarea / Select | `input.md` *(to create)* | ⬜ |
| Checkbox / Radio / Toggle / Slider | `form-controls.md` *(to create, grouped)* | ⬜ |
| Badge / Card / Dialog / IconButton | `feedback.md` *(to create, grouped)* | ⬜ |
| Tabs / Skeleton / Pagination / Breadcrumbs / Accordion | `navigation.md` *(to create, grouped)* | ⬜ |
| Rating / Price / QuantityStepper / Toast / Table / EmptyState | `commerce.md` *(to create, grouped)* | ⬜ |
| SearchAutocomplete / CheckoutSteps | `commerce.md` *(to create, grouped)* | ⬜ |
| ProductCard / Gallery / VariantSelector | `product.md` *(to create, grouped)* | ⬜ |
| HeroSection / BannerSection / FeaturedProducts / CategoryShowcase / BrandStrip / BlogTeaser | `sections.md` *(to create, grouped)* | ⬜ |
| CartLineItem / MiniCartDrawer / Announcement / Navbar / Footer | `shell-cart.md` *(to create, grouped)* | ⬜ |

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
