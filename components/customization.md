# Customization matrix — every admin knob, per surface (living doc)

> Scope: the full knob inventory from dumb primitives to shell blocks to (later) sections — what admin can change, types, defaults, since which task.
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## Progressive rule (read first)

Every settings slice appends its rows here same-commit, or the slice isn't done. Surfaces land in three states: **live** (knobs work end-to-end), **settings-only** (vocabulary resolved, component to-come), **stub** (one line, filled by its slice). No knob exists without a row; no row without a knob.

## Dumb primitives (one row per variable — sf-042 schema)

Schema: **Variable** (admin knob path) | **Description** (what it changes)
| **Values** (type/range) | **Default** | **Paints via** (CSS var or prop).
Names verified against code (step-0 grep); tables bend to code, never
the reverse. Batches land per component; grouped rows below migrate as
their batch lands.

### Pill (`pill.md`, sf-042 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `--pill-bg` | To change background of the active filter pill | color | ink `#0a2540` | `.sf-pill` active background |
| `--pill-active-text` | To change text color of the active filter pill | color | white `#ffffff` | active pill color |
| `--pill-text` | To change text color of inactive pills and chips | color | ink `#0a2540` | base `.sf-pill` color |
| `--pill-border` | To change border color of inactive pills and chips | color | `--border` | base border |
| `--pill-chip-bg` | To change background of trending chips | color | white `#ffffff` | chip background |
| `--pill-action-bg` | To change background of the Quick Add button | color | `accent-50` | action background |
| `--pill-action-text` | To change text color of the Quick Add button | color | ink `#0a2540` | action color |
| `--pill-added-bg` | To change background of the Added (done) state | color | `success-bg` | added background |
| `--pill-added-text` | To change text color of the Added (done) state | color | `success` | added color |
| `--pill-radius` | To change corner roundness of all pills | 0–999px | 999 (stadium) | `border-radius` |

### Toast (`toast.md`, sf-042 — verified; zero-knob surface by design)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `open` | To show or hide the notification | boolean | — (owner-owned) | conditional render (prop) |
| `title` | To change the bold headline of the notification | string | — | headline text (prop) |
| `message` | To change the muted detail line under the headline | string | — (optional) | detail text (prop) |
| `icon` | To change the leading glyph of the notification | ReactNode | — (optional) | icon slot (prop) |
| `onClose` | To run when the user dismisses the notification | callback | — | X button (prop) |

### Badge (`Badge`, sf-042 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `tone` | To change which face the badge shows (builtin or custom id) | 7 builtins + custom ids | `neutral` | face lookup (prop) |
| `tones` | To pass the resolved custom-badge map into the badge | `Record<id, CustomBadgeTone>` | — (owner passes) | lookup map (prop) |
| `theme.badges.custom[].id` | To name a new admin-created badge | unique string (required) | — | custom face id |
| `theme.badges.custom[].label` | To change the text shown on the custom badge | string | falls back to id | badge children |
| `theme.badges.custom[].bg` | To change background of the custom badge | color (required) | — | face bg |
| `theme.badges.custom[].textColor` | To change text color of the custom badge | color (required) | — | face text |
| `theme.badges.custom[].borderColor` | To change border color of the custom badge | color | falls back to bg | face border |
| `theme.badges.custom[].borderStyle` | To change border line style of the custom badge | `solid` / `dashed` / `dotted` | `solid` | face border-style |

### Icon (`Icon`, sf-043 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `name` | To choose which glyph the icon shows | IconName union (kebab-case, from `ICON_NAMES`) | — (required) | glyph map (prop) |
| `size` | To change the pixel box of the icon | any px (house 16–32) | 20 | svg width/height |
| `strokeWidth` | To change the stroke weight of the icon | any (house 1–3, float allowed) | 2 | svg `stroke-width` |
| `filled` | To show the icon as a filled silhouette instead of outline | boolean | false (outline) | svg `fill` |
| `color` | To change the stroke ink of the icon | color ("" = currentColor behavior) | `currentColor` | CSS `color` on svg (prop) |
| `title` | To give a standalone icon an accessible name | string | — (decorative, aria-hidden) | `<title>` + role=img |
| `theme.icon.size` | To set the house default icon size | 16–32 | 20 | owner feeds `size` |
| `theme.icon.strokeWidth` | To set the house default stroke weight | 1–3 | 2 | owner feeds `strokeWidth` |
| `theme.icon.filled` | To default all icons to filled silhouettes | boolean | false | owner feeds `filled` |
| `theme.icon.color` | To set the house default stroke ink | color ("" = currentColor) | "" | owner feeds `color` |

### Textarea (`Textarea`, sf-043 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `value` | To set the text content of the field | string | — (controlled, required) | textarea value (prop) |
| `label` | To change the caption above the field | string | — (optional) | `<label>` text |
| `helper` | To change the hint line under the field | string | — (optional) | helper text (prop) |
| `error` | To show a validation message and the invalid face | string | — (optional) | alert text + error border |
| `rows` | To change the visible height of the field in text rows | 2–12 (house) | 4 | `rows` attr |
| `radius` | To change corner roundness of the field | 0–24 (house) | 10 | `borderRadius` style |
| `borderColor` | To change border color of the field | color | `--border` token | border style |
| `bg` | To change background of the field | color | white surface token | background style |
| `textColor` | To change text color inside the field | color | ink token | color style |
| `focusBorderColor` | To change border color while the field is focused | color | accent token | `--ta-focus` var |
| `theme.textarea.*` | To set house defaults for the six paint/size knobs above | same ranges | builtins (10 / 4) | owner feeds flat props |

### Button (`Button`, sf-043 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `variant` | To change the button's color family | 6 variants | `primary` (house: `theme.defaultVariant`) | variant map → `--btn-*` |
| `size` | To change the button's height scale | `sm` / `md` / `lg` (36/44/52px) | `md` (house: `theme.defaultSize`) | minHeight/padding/fontSize |
| `bg` | To change background of the button | color ("" = variant) | variant face | `--btn-bg` |
| `textColor` | To change text color of the button | color ("" = variant) | variant face | `--btn-text` |
| `borderColor` | To change border color of the button | color ("" = variant) | variant face | `--btn-border` |
| `borderWidth` | To change border thickness of the button | 0–4px | 1 | `--btn-bw` |
| `borderRadius` | To change corner roundness of the button | 0–24 (999+ = full stadium) | 8 (house) | `--btn-radius` |
| `waveBg / waveText` | To change the hover wave wash and the text color riding it | colors | per-variant faces | `--wave-bg` / `--wave-text` |
| `hoverBorderColor` | To change border color while hovering | color (`"auto"` = waveBg) | variant | `--wave-border` |
| `waveOrigin / peaks / peakHeight` | To change where the wave rises from, crest count, crest depth | 4 edges / 1–3 / 4–24px | bottom / 2 / 12 | wave mask + `--wave-peak` |
| `durationMs / textDelayMs / easing` | To change wave travel time, text-swap delay, timing curve | 0–1000 / 0–500 / easing | 360 / 200 / smooth | `--wave-duration` / `--wave-delay` / `--wave-easing` |
| `animationKind` | To change the interaction model of the button | wave-rise / fade×4 / linear / none | `wave-rise` | `data-anim-kind` |
| `useWave / animationEnabled` | To turn the travelling wave layer on or off | boolean | true | wave layer render |
| `disabledBg / disabledTextColor / disabledBorderColor / disabledBorderWidth / disabledHoverEnabled` | To change the dead-button face (explicit solids, never dimmed) | colors + 0–4 + bool | ink-on-mist set | disabled face vars |
| `pressedScale / pressedTranslateY / pressedShadow / pressedEnabled` | To change the press-depth effect of the button | 0.9–1 / 0–8px / shadow / bool | off (1 / 0 / none) | `--pressed-scale` / `--pressed-translate` / `--pressed-shadow` |
| `theme.button.*` | To set house defaults for variant/size/paint/animation | same ranges | builtins | `theme` object prop (trio-lowest) |


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

Theme house defaults (`theme.button`, sf-031 — per-instance flat props still win):

| Knob | Type | Default |
|---|---|---|
| `defaultVariant / defaultSize` | house style | `primary` / `md` |
| `bg / textColor / borderColor` | colors ("" = variant applies) | "" (no override) |
| `borderRadius` | 0–24 | 8 |
| `animation` | global layer for `resolveButtonAnimation` | {} (pure defaults) |

Wiring (sf-038 — `theme` object prop, trio-lowest: flat > theme > variant/defaults; animation global fills the pre-built slot): AuthForm submit (first production site) + §1 house-style demo row. All other demos stay explicit (variant showcase intent). Remaining primitives wire one per turn.

Input (`theme.input`, sf-031 — flat `bg/textColor/borderColor/radius` props win):

| Knob | Type | Default |
|---|---|---|
| `bg / textColor / borderColor / focusBorderColor` | colors ("" = component tokens) | "" (no override) |
| `borderRadius` | 0–24 | 10 |

Checkbox (`theme.checkbox`, sf-031 — flat `boxBg/tickColor/borderColor/borderRadius/size` win):

| Knob | Type | Default |
|---|---|---|
| `size` | 16–28px | 20 |
| `boxBg / tickColor / borderColor` | colors ("" = accent/white/border tokens) | "" / `#FFFFFF` / "" |
| `borderRadius` | 0–12 | 6 |

Toggle (`theme.toggle`, sf-031 — flat `onColor/offColor/knobColor/width/height` win):

| Knob | Type | Default |
|---|---|---|
| `width / height` | 32–64 / 20–32px | 44 / 24 |
| `onColor / offColor / knobColor` | colors ("" = accent/border tokens) | "" / "" / `#FFFFFF` |

Select (`theme.select`, sf-033 — `variant` branch + native extension):

| Knob | Applies to | Type | Default |
|---|---|---|---|
| `variant` | both (branch) | `native` / `custom` | `native` |
| `bg / textColor / borderColor / focusBorderColor / borderRadius` | both (button face) | colors + 0–24 | "" / "" / "" / "" / 10 |
| `arrowPadding` | both (arrow offset) | 4–24px | 12 |
| `arrowIconUrl` | both (upload; glyph fallback) | URL string | "" (chevron) |
| `selectedBg / selectedText` | **custom only** (OS chrome law) | colors | "" (accent-50 / ink tokens) |
| `hoverBg / hoverText` | **custom only** | colors | "" (section-bg / ink tokens) |
| `optionPaddingY` | **custom only** | 4–16px | 8 |
| `dropdownAnimation` | **custom only** | motion instance (any preset + custom + off) | fast fade 180ms |

Data pattern (sf-035 — third `useSearch` instance): `lib/select/options.ts`
`OptionsSource.list(signal)` port → `lib/select/demoOptions.ts` demo
(8 countries, 150ms) → `app/hooks/useSelectOptions.ts` (`options/status/
reload`, mount-load, stale-kill) → §9 async + themed demos (own hook
instances; CMS/service swaps one line).

Tooltip (`theme.tooltip`, sf-037 — feeds the existing `style` object prop,
zero component change; keeps its own slide/fade/none micro-motion, never
shared presets):

| Knob | Type | Default |
|---|---|---|
| `bg / textColor / borderColor / borderWidth` | colors + 0–2 | ink / white / transparent / 0 |
| `radius / fontSize / fontWeight / offset` | 0–16 / 11–14 / 400–700 / 4–16 | 8 / 12 / 500 / 8 |
| `animation / durationMs` | `slide` / `fade` / `none` + 0–500 | `slide` / 160 |

Dialog (`theme.dialog`, sf-037 — additive paint props, Textarea precedent):

| Knob | Type | Default |
|---|---|---|
| `overlayColor / overlayAlpha` | color / 0–100 | ink / 50 |
| `panelBg / borderColor / borderRadius / maxWidth` | color / color / 0–24 / 320–720 | white / border / 12 / 448 |
| `titleColor / titleSize` | color / 14–24 | ink / 18 |
| `bodySize / bodyWeight / bodyColor` | inherited panel defaults (owner direct styles win) | 14 / 400 / ink |
| action buttons | — (no knob: `theme.button.defaultVariant` already sets the house button; Dialog never retints owner's children) | — |

## Search overlays (nested `search.*` groups, resolved per-key)

Why overlays differ (one line each — different jobs, different knobs):

| Overlay | Job | Therefore customizes |
|---|---|---|
| Sheet | Transient top panel | Motion + placeholder only (thin by design) |
| Editorial | Brand takeover | Copy + paint (24 knobs: voice and look) |
| Palette | Dense tool | Geometry + visibility + actions (40 knobs: behavior) |
| Classic | Fallback | Nothing by design (zero-knob fallback must stay trivial) |

Shared across all three live variants: motion-instance shape (preset→concrete,
per-variant instances), theme-object→vars paint, trap+Esc+return, curated-
before-typing, OS-chrome honesty (knobs mark applicability like Select).

### Sheet (`search.*`, sf-017 — thin by design)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `search.overlayVariant` | To choose which overlay the island loads | `classic` / `palette` / `sheet` / `editorial` | `classic` | registry id (prop) |
| `search.placeholder` | To change the hint text inside the search field | string | `Search products…` | input placeholder |
| `search.sheetAnimation` | To change the arrival animation of the sheet | motion preset + custom + off | smooth 240 ease-out, full travel | `--searchsheet-duration` / `--searchsheet-easing` |
| `dept` (flat prop) | To set the active department filter (owner-driven) | department string | `All` | active pill (prop) |

Sheet paint reuses navbar tokens (`--nb-bg` panel, `--nb-text` ink) — no sheet-owned paint knobs by design.

### Editorial (`search.editorial`, sf-023 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `search.editorial.bg` | To change background wash of the takeover | color | `#f5fafc` | `--ed-bg` (+ `--ed-alpha` mix) |
| `search.editorial.bgAlpha` | To change opacity of the background wash | 0–100 | 100 | `--ed-alpha` |
| `search.editorial.blur` | To turn backdrop blur on or off behind the wash | boolean | false | `data-blur` hook |
| `search.editorial.blurPx` | To change blur radius behind the wash | 0–24px | 8 | `--ed-blur-px` |
| `search.editorial.eyebrow` | To change the header eyebrow text | string | Atelier copy | rendered text (prop) |
| `search.editorial.eyebrowColor` | To change text color of the header eyebrow | color | muted | `--ed-eyebrow` |
| `search.editorial.archiveEyebrow` | To change the archive eyebrow text above the input | string | archive copy | rendered text (prop) |
| `search.editorial.archiveColor` | To change text color of the archive eyebrow | color | accent | `--ed-archive` |
| `search.editorial.inputColor` | To change text color inside the giant input | color | ink | `--ed-input` |
| `search.editorial.placeholderColor` | To change hint text color inside the giant input | color | `#93a3b1` | `--ed-placeholder` |
| `search.editorial.underlineColor` | To change color of the input underline rule | color | ink | `--ed-underline` |
| `search.editorial.title` | To change the curated-grid heading text | string | Curated copy | rendered text (prop) |
| `search.editorial.titleColor` | To change text color of the curated-grid heading | color | ink | `--ed-title` |
| `search.editorial.mutedColor` | To change the muted support text across the takeover | color | muted | `--ed-muted` |
| `search.editorial.closeIconColor` | To change color of the close X icon | color | ink | `--ed-close` |
| `search.editorial.tabTextColor` | To change text color of inactive department tabs | color | muted | `--ed-tab` |
| `search.editorial.tabActiveBg` | To change background of the active department tab | color | ink | `--ed-tab-bg` |
| `search.editorial.tabActiveText` | To change text color of the active department tab | color | white | `--ed-tab-text` |
| `search.editorial.tabShape` | To change shape language of the department tabs | `pill` (v1; underline/segmented later) | `pill` | `data-tabshape` hook |
| `search.editorial.cardType` | To change card skin of the curated grid | `standard` (v1) | `standard` | `data-card` hook |
| `search.editorial.cardRadius` | To change corner roundness of curated card images | 0–24px | 16 | `--ed-radius` |
| `search.editorial.deptColor` | To change text color of the card department eyebrow | color | muted | `--ed-dept` |
| `search.editorial.nameColor` | To change text color of the card product name | color | ink | `--ed-name` |
| `search.editorial.priceColor` | To change text color of the card price | color | ink | `--ed-price` |
| `search.editorial.editorialAnimation` | To change the arrival animation of the takeover | motion preset + custom + off | oceanic 320 | `--ed-duration` / `--ed-easing` |

### Palette (`search.palette`, sf-024 + sf-028 — verified)

| Variable | Description | Values | Default | Paints via |
|---|---|---|---|---|
| `search.palette.cardBg` | To change background of the modal card | color | white | `--pl-card` |
| `search.palette.backdrop` | To change color of the dim wash behind the card | color | ink | `--pl-backdrop` |
| `search.palette.backdropAlpha` | To change opacity of the dim wash | 0–100 | 72 | `--pl-backdrop-alpha` |
| `search.palette.blur` | To turn backdrop blur on or off behind the wash | boolean | true | `data-blur` hook |
| `search.palette.blurPx` | To change blur radius behind the wash | 0–24px | 8 | `--pl-blur-px` |
| `search.palette.cardMaxWidth` | To change width cap of the modal card | 480–960px | 720 | `--pl-maxw` |
| `search.palette.inputColor` | To change text color inside the search field | color | ink | `--pl-input` |
| `search.palette.inputSize` | To change font size inside the search field | 14–24px | 16 | `--pl-input-size` |
| `search.palette.placeholderColor` | To change hint text color inside the search field | color | `#93a3b1` | `--pl-placeholder` |
| `search.palette.iconColor` | To change color of the search glyph | color | accent | `--pl-icon` |
| `search.palette.closeColor` | To change color of the close X | color | muted | `--pl-close` |
| `search.palette.mutedColor` | To change the muted support text across the modal | color | muted | `--pl-muted` |
| `search.palette.headingColor` | To change text color of section headings in the modal | color | ink | `--pl-heading` |
| `search.palette.nameColor` | To change text color of product names in rows | color | ink | `--pl-name` |
| `search.palette.nameSize` | To change font size of product names in rows | 14–22px | 17 | `--pl-name-size` |
| `search.palette.priceColor` | To change text color of prices in rows | color | ink | `--pl-price` |
| `search.palette.ratingColor` | To change color of the rating star | color | gold | `--pl-rating` |
| `search.palette.deptColor` | To change text color of the row department label | color | muted | `--pl-dept` |
| `search.palette.rowsMaxHeight` | To change height cap of the scrollable rows region | 160–600px | 300 | `--pl-rows-max` |
| `search.palette.thumbSize` | To change size of the square row thumbnail | 48–96px | 64 | `--pl-thumb-size` |
| `search.palette.thumbRadius` | To change corner roundness of the row thumbnail | 0–24px | 14 | `--pl-thumb` |
| `search.palette.showFilters` | To show or hide the department filter row | boolean | true | region gate (prop) |
| `search.palette.showTrending` | To show or hide the trending column | boolean | true | region gate (prop) |
| `search.palette.showRecent` | To show or hide the recent-searches column | boolean | true | region gate (prop) |
| `search.palette.showRatings` | To show or hide ratings in rows | boolean | true | region gate (prop) |
| `search.palette.showTags` | To show or hide tag badges in rows | boolean | true | region gate (prop) |
| `search.palette.showDept` | To show or hide department labels in rows | boolean | true | region gate (prop) |
| `search.palette.showFooter` | To show or hide the keyboard-hint footer | boolean | true | region gate (prop) |
| `search.palette.rowAction` | To change which action rows offer | `quick-add` (v1; view/both later + onView) | `quick-add` | action branch (prop) |
| `search.palette.cardType` | To change card skin of the rows | `row` (v1) | `row` | `data-card` hook |
| `search.palette.notifyOnQuickAdd` | To notify the shopper on quick-add (owner surfaces Toast) | boolean | true | owner effect gate |
| `search.palette.paletteAnimation` | To change the arrival animation of the modal | motion preset + custom + off | oceanic 320 | `--pl-duration` / `--pl-easing` |
| Pill faces (`pillActiveBg` … `pillRadius`, 10 knobs) | To change filter/trending/quick-add faces (see Pill section) | colors + 0–999 | ink / white / 999 | `--pill-*` (not repeated here) |

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
