# Admin Design System — Oceanic Blue v1.0 (Admin Console)

> Platform: Next.js 16 (App Router) + React 19 + Tailwind CSS 4 + TypeScript 5 + shadcn/ui + Radix (optional)
> Theme: Oceanic Blue — aligned with storefront tokens; **admin primary buttons stay black & white (ink + white)**
> Status: Active | Version 1.0 | Date: 2026-08-24
> Parent: `docs/6.Admin-Panel.md` (screens §3, registry §4, patterns §7) | `docs/5.Features.md` Part B | `docs/2.Tech-Stack.md` §4
> Implements: `frontend/admin/app/*` + `components/*` + `lib/api-client/*` + `store/*`
> Figma: (add file URL when created)

---

## 1. Design Principles — Admin

| Principle | Statement | Rationale |
|---|---|---|
| **Density without clutter** | 320px sidebar + 64px topbar + cards at 12px radius, generous `16-24px` inner padding, `12px` grid gaps. | Admin lives in tables/forms for hours; dense saves scroll, cramped kills scan. |
| **Clarity over decoration** | `#F5FAFC` mist page, white cards, `#DCE8EE` 1px borders, no gradients. | Numbers, stock, orders must be scannable; flat keeps focus on data. |
| **Black & white actions** | Admin primary buttons are **ink `#0A2540` + white** — deliberately NOT the storefront ocean `#0077B6`. Ocean is reserved for links, focus, and active states. | Admin is a work tool: monochrome actions read as neutral/serious and never compete with the storefront brand the admin is previewing. |
| **Trust through consistency** | Shared neutrals/borders/status colors with storefront (`#0A2540`, `#DCE8EE`, success/warning/error trio) so `?preview=1` is WYSIWYG. | Admin creates what storefront shows; shared tokens guarantee preview fidelity (`6.Admin-Panel.md` §7.1). |
| **Data first, safe actions** | Status badges, KPI numbers, destructive `ConfirmDialog` visually distinct; `409 DUPLICATE_SKU` is a blocking banner. | Inventory, orders, discounts are money-critical. |

---

## 2. Typography — Admin

Admin keeps **Outfit** for everything (body + labels + numbers) to maximize legibility in tables; **Fraunces** optional for page titles only. `Geist Mono` retained for code/ids.

| Category | Font | Weight | Size | Line-height | Letter-spacing | Usage in Admin |
|---|---|---|---|---|---|---|
| **H1 (Page)** | Outfit | 600 | 24 | 1.20 | -0.015em | `Dashboard`, `Products`, `Orders` titles |
| **H2 (Section)** | Outfit | 600 | 18 | 1.30 | -0.01em | Panel titles (`KPI Cards`, `Section list`) |
| **H3 (Group)** | Outfit | 600 | 14 | 1.20 | 0 | Form group heads (`Content`, `Appearance`, `CTAs`) |
| **Body** | Outfit | 400 | 14 | 1.50 | 0 | Table cells, form help |
| **Body Small** | Outfit | 400 | 13 | 1.40 | 0 | Slide-row meta, hints |
| **Label** | Outfit | 500-600 | 12-14 | 1.20 | 0.01-0.02em | `field label 12px 600 0.02em`, navlinks 500 |
| **Caption** | Outfit | 400 | 12 | 1.40 | 0 | `err 12px`, helper text |
| **KPI Large** | Outfit | 700 | 28-32 | 1.10 | -0.02em | Dashboard KPI numbers |
| **Data Small** | Outfit | 600 | 13 | 1.20 | 0 | `uses_count`, `SKU`, prices; badge `11px 700` |
| **CTA** | Outfit | 600 | 14 | 1.00 | 0.01em | Admin buttons (Save, Add Slide, Add CTA) |

Rules: single family (Outfit) for scan speed; numbers use `600` not body `400`; no Fraunces in tables/forms.

---

## 3. Color System — Oceanic Blue Admin (Which Color Where)

Admin shares storefront neutrals/status but surfaces are `#F5FAFC` page + white cards, and **actions are monochrome ink**. Every token has hex + usage.

### 3.1 Primitives

**Ocean ramp (accents only):** `50 #E6F7FB` · `100 #CAF0F8` · `200 #ADE8F4` · `300 #90E0EF` · `400 #48CAE4` · `500 #00B4D8` · `600 #0096C7` · `700 #0077B6` · `800 #023E8A` · `900 #03045E`

**Neutrals (workhorse):** Ink `#0A2540` · Mist `#F5FAFC` · Surface `#FFFFFF` · Border `#DCE8EE` · Muted `#5B7286`

**Status trio:** Success `#0E9F6E` / bg `#ECFDF3` / border `#ABEFC6` · Warning `#F79009` / bg `#FFFAEB` / border `#FEDF89` · Error `#D92D20` / bg `#FEF3F2` / border `#FECDCA`

### 3.2 Semantic Tokens — Admin Alias (Where Used)

| Semantic Token | Hex | Where Used — Admin (Exact) | Contrast |
|---|---|---|---|
| `--color-navbar-bg` / sidebar bg | `#FFFFFF` | `Topbar 64px` + `Sidebar 320px` bg, `border 1px solid --border` | — |
| `--color-page-bg` | `#F5FAFC` | `body` canvas, `group-head`, `add-slide`, table header bg | — |
| `--color-card-bg` | `#FFFFFF` | Panels, cards, tables, KPI cards, forms, `slide-row`, `cta-item` | — |
| `--color-ink` (text.primary) | `#0A2540` | Page H1, table primary cells, **primary buttons bg**, topbar text | 15.9:1 on white |
| `--color-accent` | `#0077B6` | Links, active nav text, chart line, focus **border** (buttons stay ink) | 4.6:1 AA |
| `--color-accent-50` | `#E6F7FB` | Sidebar active bg, hover washes, chart area | — |
| `--color-button-bg` (admin primary) | **`#0A2540` ink** | `Save`, `Add Slide`, `Add CTA`, destructive-adjacent primaries — **black & white, not ocean** | 15.9:1 AAA |
| `--color-button-text` | `#FFFFFF` | Primary button label | — |
| `--border` | `#DCE8EE` | Every admin border: panels, inputs, tables, chips, dialogs | — |
| `--text-muted` | `#5B7286` | `panel h3 13px 0.08em uppercase`, `field label 12px 600`, hints | 4.7:1 AA |
| `--focus-ring` | `#0077B633` | Input focus `0 0 0 3px`, `slide-row.active` ring | — |
| Status | `#0E9F6E`/`#F79009`/`#D92D20` | Badges `active/completed` · `pending/partial/low stock` · `failed/expired` with bg/border trios | — |

**Admin vs storefront delta:** Storefront primary CTA = ocean `#0077B6`; **admin primary button = ink `#0A2540` + white** (black & white policy). Ocean in admin is limited to links, focus borders, active-nav, and charts. `imageBg #CAF0F8` appears only inside hero previews, not as an admin surface. Storefront hero is a gradient; admin stays flat mist.

### 3.3 Component Tokens — Semantic → Admin Component

| Component | Token | Value | Note |
|---|---|---|---|
| **Sidebar 320px** | bg `#FFFFFF`, border `#DCE8EE`, active `bg #E6F7FB + text #023E8A + border-left 3px #0077B6` | groups Overview/Catalog/Content/Sales/Customers/System | `navlink 14px 500`, group label `12px 600 0.08em uppercase muted` |
| **Topbar 64px** | bg `#FFFFFF`, text `#0A2540` | logo 20px 700; search `36px 999px`; icon-btn hover `border #0077B6` | |
| **KPI Card** | bg `#FFFFFF`, radius 12, number `28-32 700 ink`, label `12px 600 muted` | delta success/warning/error | |
| **Table** | header `bg #F5FAFC 12px 600 uppercase muted`, row hover `#F5FAFC`, cells 14px | offset pagination | |
| **Form inputs** | `40px radius 10 border #DCE8EE`, focus `border #0077B6 + ring #0077B633`, error `border #D92D20 + .err 12px #D92D20` | | |
| **Primary button** | **`bg #0A2540 + text #FFFFFF`** (black & white) | hover `#1A3A5C`; secondary = white + `border #0A2540` + ink text | **not ocean** |
| **ColorPicker** | `40px swatch radius 10 + hex input` | | |
| **Slider** | track `#DCE8EE`, thumb `#0077B6` | `0-24 / 0-48 / 0-4` ranges | |
| **Toggle** | off `#DCE8EE`, on `#0077B6`, knob white | | |
| **ThreeState (Inherit\|Override)** | active `#0077B6`; Reset = delete JSONB key, never `null` | | |
| **Slide row** | border default, active `border #0077B6 + ring #0077B633`, img `48×36 r6` | | |
| **CTA item (ctas 0-3)** | `z.array(ctaSchema).max(3)`; Add CTA dashed 36px disabled@3 opacity .5 | per-CTA `text/link` required + hex styles + radius 0-24 | |
| **Dialog/Confirm** | overlay `rgba(10,37,64,.5)`; destructive `#D92D20` + white | | |
| **SortableList** | ghost opacity .5, dragging shadow-lg, optimistic revert | | |
| **Badge** | `11px 700`: success/warning/error trios | | |
| **Chart** | line `#0077B6`, area `#E6F7FB`, grid `#F5FAFC` | | |
| **Tabs** | active `text #0A2540 + 2px bottom border #0077B6` | | |

---

## 4. Spacing — Admin

Base `4px`: `4 · 8 · 12 · 16 · 20 · 24 · 32`. Controls grid `320px 1fr gap 20`; panel padding `14px`; group-body `12px`; sections `28px 24px`.

---

## 5. Border Radius — Admin

`sm 6` (slide-img) · `md 8` (mini, button) · `lg 10` (group, slide-row, inputs) · `card 12` (panel, card) · `peek 14` (storefront only) · `pill/circle 9999`.

---

## 6. Shadows & Motion — Admin

| Token | Value |
|---|---|
| `shadow-card` | `0 4px 16px rgba(10,37,64,.08)` |
| `shadow-lg` | `0 8px 32px rgba(10,37,64,.12)` |
| `focus-ring` | `0 0 0 3px #0077B633` |
| `duration-fast` | `180ms ease` |
| `duration-base` | `320ms cubic-bezier(.32,.72,.32,1)` |
| wave (preview CTAs only) | `360ms` rise + `0.2s` text delay |

`prefers-reduced-motion` → transitions off.

---

## 7. Components — Admin

### 7.1 Layout Shell — Topbar 64px + Sidebar 320px (values in §3.3); controls grid `320px 1fr gap 20` → `1fr` at 900px.

### 7.2 Tables — header `#F5FAFC 12px 600 uppercase muted`, row hover mist, offset pagination `?page&perPage=25`.

### 7.3 Forms — inputs per §3.3; validation inline `.err 12px #D92D20`; 409 conflicts as blocking banners.

### 7.4 CTAs Editor — `hero.slides[].ctas` + `banner.ctas`: `z.array(ctaSchema).max(3)`, per-CTA `text(1-50)/link(internal)/bg/textColor/borderColor/borderWidth 0-4/borderRadius 0-24 (default 8)`; live preview `?preview=1` renders storefront `HeroSection` (ocean primary `#0077B6`) — admin chrome stays ink.

### 7.5 Media Picker — modal grid, usage filter `product/section/blog`, multi-select, S3 upload.

### 7.6 SortableList — unified drag for sections/gallery/navbar/blocks; `sort_order` optimistic revert.

---

## 8. Layout — Admin

`Announcement 36px → Topbar 64px → Sidebar 320px | Content max 1280px pad 24 → Footer`. Breakpoints: 640 / 700 / 900 / 1280.

---

## 9. Tailwind CSS Configuration — Admin

```css
@import "tailwindcss";
:root { --color-page-bg:#F5FAFC; --color-card:#FFFFFF; --color-ink:#0A2540; --color-accent:#0077B6; --border:#DCE8EE; }
@theme inline {
  --color-card: var(--color-card);
  --color-muted: #5B7286;
  --radius-card: 12px;
  --font-sans: var(--font-outfit);
}
```

`layout.tsx`: `Outfit 400-700` (+ Geist Mono for ids). **Admin primary = `bg #0A2540 text #FFFFFF`.**

---

## 10. Figma Variable Collections — Admin

| Collection | Variables |
|---|---|
| `Colors` | `pageBg #F5FAFC`, `card #FFFFFF`, `border #DCE8EE`, `ink #0A2540`, `accent #0077B6`, `success #0E9F6E`, `warning #F79009`, `error #D92D20`, `muted #5B7286` |
| `Radii` | `button 8, card 12, peek 14, circle` |
| `Shadows` | `card, dialog, focus-ring` |
| `Typography` | `Outfit` (+ Geist Mono) |

---

## 11. Component Inventory — Admin

`Button (ink primary)`, `Input`, `Select`, `Badge 11px 700`, `Card`, `ColorPicker 40px`, `Slider`, `Toggle`, `ThreeState`, `DateRangePicker 7/30/90d`, `Tabs`, `TreeView`, `MediaPickerModal`, `SortableList`, `Dialog`, `Table`, `Pagination (offset)`, `Chart`, `Timeline`, `PermissionCheckboxTree`, `BlockEditor`.

---

## 12. Accessibility — Admin

- **Contrast:** ink on white `15.9:1` AAA; muted `4.7:1` AA; error `#D92D20` on white `4.6:1` AA; **ink button + white text `15.9:1`**.
- **Keyboard:** full tab order; `Enter` on Add CTA; `←/→` on hero preview; labelled controls.
- **Focus:** ring `#0077B633` on every input/select; `2px #0077B6` outline on links.

---

## Appendix — File References (Admin)

- `docs/6.Admin-Panel.md` §2 shell, §3.1-3.20 screens, §4 registry, §7.1 live preview
- `docs/5.Features.md` Part B acceptance
- `docs/3.Database-Schema.md` §4.1 `cms_*`, §3.2 `photo_settings`
- Prototype: `E:\E-Commerce\index.html` — Oceanic Blue v1.0 (admin chrome ink; storefront preview ocean)
- `frontend/admin/app/globals.css`, `layout.tsx`, `lib/api-client/*`, `components/*`
