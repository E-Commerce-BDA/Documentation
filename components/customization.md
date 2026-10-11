# Customization matrix — every admin knob, per surface (living doc)

> Scope: the full knob inventory from dumb primitives to shell blocks to (later) sections — what admin can change, types, defaults, since which task.
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## Progressive rule (read first)

Every settings slice appends its rows here same-commit, or the slice isn't done. Surfaces land in three states: **live** (knobs work end-to-end), **settings-only** (vocabulary resolved, component to-come), **stub** (one line, filled by its slice). No knob exists without a row; no row without a knob.

## Dumb primitives (props/vars, no CMS groups yet)

| Surface | Knob | Type | Default |
|---|---|---|---|
| Pill (`pill.md`) | `--pill-*` faces (bg/active-text/text/border/chip-bg/action-bg/action-text/added-bg/added-text/radius) | CSS vars (parent inlines) | Oceanic tokens, radius 999 |
| Toast (`toast.md`) | `open/title/message/icon/onClose` | Props only | — (no knobs by design) |
| Badge | `tone` (success/warning/error/sale/info/neutral/lilac) | Prop | `neutral` (tones fixed) |

Button (`button.md`, sf-030 — highest-reuse primitive first):

| Knob | Type | Default |
|---|---|---|
| `variant` | `primary/light/ghost-ink/sale/success/error` | `primary` |
| `size` | `sm/md/lg` (36/44/52px) | `md` |
| `bg / textColor / borderColor / borderRadius` | CMS colors + 0–24 | theme (8px radius) |
| `hoverBorderColor / waveBg` | CMS colors | theme |
| `animation` (`ButtonAnimationField`) | enabled/useWave/waveOrigin/peaks/peakHeight/animationKind/durationMs/easing | wave bottom 2-peak, 360ms |
| `disabledBg / disabledTextColor / disabledBorderColor / disabledBorderWidth / disabledHoverEnabled` | flat (win over `animation.disabled`) | explicit solids |
| `loading` | boolean (spinner face) | false |

## Search overlays (nested `search.*` groups, resolved per-key)

Sheet (`sheetAnimation` only + flat `placeholder`/`dept` props):

| Knob | Type | Default |
|---|---|---|
| `overlayVariant` | `classic/palette/sheet/editorial` | `classic` |
| `placeholder` | string | `Search products…` |
| `sheetAnimation` | motion instance | smooth 240 ease-out, full |

Editorial (`search.editorial`, sf-023):

| Knob | Type | Default |
|---|---|---|
| `bg / bgAlpha / blur / blurPx` | color / 0–100 / bool / 0–24 | `#f5fafc` / 100 / off / 8 |
| `eyebrow / eyebrowColor / archiveEyebrow / archiveColor` | strings | Atelier copy, muted/accent |
| `inputColor / placeholderColor / underlineColor` | colors | ink / `#93a3b1` / ink |
| `title / titleColor / mutedColor / closeIconColor` | string + colors | Curated copy, ink/muted/ink |
| `tabTextColor / tabActiveBg / tabActiveText / tabShape` | colors + `pill` (v1) | muted / ink / white |
| `cardType / cardRadius / deptColor / nameColor / priceColor` | `standard` (v1) / 0–24 / colors | 16, muted/ink/ink |
| `editorialAnimation` | motion instance | oceanic 320, full |

Palette (`search.palette`, sf-024 + sf-028):

| Knob | Type | Default |
|---|---|---|
| `cardBg / backdrop / backdropAlpha / blur / blurPx` | color / color / 0–100 / bool / 0–24 | white / ink / 72 / on / 8 |
| `inputColor / placeholderColor / iconColor / closeColor` | colors | ink / `#93a3b1` / accent / muted |
| `mutedColor / headingColor / nameColor / priceColor / ratingColor / deptColor` | colors | muted / ink / ink / ink / gold / muted |
| `pillActiveBg / pillActiveText / pillText / pillBorder / pillChipBg` | colors | ink / white / ink / border / white |
| `quickAddBg / quickAddText / quickAddedBg / quickAddedText` | colors | accent-50 / ink / success-bg / success |
| `pillRadius` | 0–999 (999 = stadium) | 999 |
| `cardMaxWidth / rowsMaxHeight / thumbSize / inputSize / nameSize / thumbRadius` | clamped px | 720 / 300 / 64 / 16 / 17 / 14 |
| `showFilters / showTrending / showRecent / showRatings / showTags / showDept / showFooter` | booleans | all true |
| `rowAction` | `quick-add` (v1; view/both later + onView) | `quick-add` |
| `cardType` | `row` (v1) | `row` |
| `notifyOnQuickAdd` | boolean (owner surfaces Toast) | true |
| `paletteAnimation` | motion instance | oceanic 320, full |

## Navbar + inner blocks (settings live, components mixed)

| Surface | State | Knobs (existing vocabulary) |
|---|---|---|
| Regions/logo/bar/colors | settings-only (chrome pending) | regions toggles; logo image/height/position/wordmark; bar height/sticky/shadow; colors bg/text/hover/badge/announce |
| NavLinks | **live** | items (label/href/icon/badge/highlight/schedule), maxItems 3–8 |
| AnnouncementBar | **live** | items (text/cta/countdown), arrows, autoplay, dismissible, collapseAnimation |
| Search trigger | settings-only (`search.enabled`) | enabled (+ `overlayVariant` above) |
| Account | settings-only | enabled, items (orders/addresses/wishlist/signout) |
| Cart block | settings-only (MiniCartDrawer to-come) | enabled, destination drawer/page, dedicatedPage, badgeCap 1–99 |
| Hamburger/mobile | settings-only (drawer to-come) | breakpoint 640–1024, drawerSide left/right |

## Stubs (filled by their slices — one line each, no placeholders)

- **Product card** (variants row/overlay/minimal land with card-type work; palette `cardType` union extends).
- **CMS sections** (hero/banner/featured/category/brand/blog land with sections slice).
- **Toast severity faces** (extend via `data-*` when a second producer arrives; no stacking until a queue design exists).
