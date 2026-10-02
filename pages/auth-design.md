# Auth Design — Layouts, Customization Model & Storefront Demo

> Scope: auth page UI (signin/signup/forgot) — layout choice, per-knob
> customization, content rules, and the storefront demo that proves them.
> Backend (tokens, endpoints, edge cases) lives in `services/auth.md` and is
> NOT repeated here. Frontend behavior companion (`pages/auth.md`) to create
> with the real build.
> Status: Active | Version 1.0 | Date: 2026-09-27
> Parent: `0.Project-Overview.md` §14 · `pages/routing.md` (routes, headers)
> Related: `services/auth.md` (backend) · `5.Features.md` A11 (acceptance)

---

## 1. Decisions (locked)

1. **Sanitized HTML for panel content** — max customization (headings,
   bold/italic, lists, links, alignment, inline colors) with a strict
   allowlist (`h1–h4/p/strong/em/ul/ol/li/a/span/br` + `href/style/text-align`;
   `script/style/on*` stripped) + CSP. Structured blocks were safer but less
   customizable; HTML-with-allowlist wins per review.
2. **Shared set for signin+signup, separate set for forgot** — one style/
   content object covers both auth doors; forgot owns its own full set.
3. **Per-page layout + panel side** — each of signin/signup/forgot
   independently picks `centered | split`, and in split mode its own panel
   side (`left | right`).
4. **Storefront demo first, no admin UI** — knobs ship as a working demo in
   the showcase (`E:\E-Commerce\index.html` `#/auth` + knobs drawer);
   persistence arrives with cms-svc; the admin editor screen is out of scope.
5. **Buttons stay solid** — gradients apply to the split panel only, never to
   submit buttons (`design-system/storefront.md` §7.1 stands).

## 2. Settings shape (single object, three scopes)

```json
{
  "shared": { "layout": {}, "form": {}, "button": {}, "inputs": {},
              "panel": {}, "typography": {}, "media": {}, "behavior": {} },
  "pages": {
    "signin": { "mode": "split", "panelSide": "left" },
    "signup": { "mode": "split", "panelSide": "right" },
    "forgot": { "mode": "centered", "panelSide": "left",
                "style": { "form": {}, "panel": {}, "typography": {}, "media": {} } }
  }
}
```

Precedence (sparse/absent = inherit, same convention as Button/Tooltip):
`page > shared-auth > global theme > builtins`. Forgot's `style` replaces
the shared style groups wholesale when present; its `mode/panelSide` always
resolve per page.

## 3. Knob groups (controls + defaults)

| Group | Knobs | Control | Default |
|---|---|---|---|
| Layout | `mode` per page | segmented centered/split | split (signin/signup), centered (forgot) |
| | `panelSide` per page | segmented left/right | signin left, signup right, forgot left |
| | `ratio` | select 50-50/60-40/40-60 | 50-50 |
| | `mobile` | select stacked/hidden-panel <640px | stacked |
| Form card | `surface` | select white/tinted/transparent | white |
| | `radius` 0–24, `width` 360–480 | sliders | 12 / 400 |
| | `elevation` | select flat/border/floating | border |
| Button | full Button knob set | (existing model) | primary defaults; solids only |
| Inputs | `bg/border/radius/text/placeholder` | pickers + slider | white / `--border` / 10 / ink / muted |
| | `focusBorder/focusRing/focusRingWidth` | pickers + slider | accent / `#0077B633` / 3 |
| | `errorBorder` | picker | error red |
| Panel bg | `mode` | select solid/gradient/image/pattern/none | gradient |
| | gradient `type/angle/stops[]` | select + 0–360 slider + 2–4 stops | linear 135°, `#023E8A→#0077B6→#48CAE4` |
| | image `url/fit/position/overlay 0–80` | upload + selects + slider | cover / center / 0 |
| Typography | `family` | select Outfit/Fraunces/system | Outfit (Fraunces panel headline) |
| | per element (headline/sub/bullets/quote/form-title/labels): `size/weight/color/align` | sliders + selects + pickers | see demo defaults |
| Content (HTML) | `headline/sub/bullets/quote/microcopy` | rich textarea (allowlist §1.1) | season/member copy (demo) |
| Media | `logoUrl/logoHeight` | upload + slider | brand mark / 28 |
| Behavior | `rememberDefault` | toggle | on |
| | `postLoginRedirect` | text (`?next=` default) | `?next=` resume |
| | notice texts (rate-limit/session-expired) | text inputs | envelope-safe copy |
| Social | providers + order | toggles + drag order | off (mock in demo; real OAuth later) |
| Errors | `style` banner/inline | select | banner |
| Motion | page fade 150–300ms | slider (reduced-motion forces off) | 200 |
| SEO | per-page `title/description` | text inputs | route defaults |

## 4. Guards (warn, don't block — button-override philosophy)

* Contrast < 4.5:1 panel text vs background → warning badge in demo.
* Gradient stops outside 2–4, angle outside 0–360 → clamped.
* Image upload: type allowlist (png/jpg/webp/svg), size cap (to set with cms-svc).
* HTML outside allowlist → stripped, never rejected (editor shows what survived).

## 5. Fixed by design (never customizable)

Token mechanics, envelope codes/messages shape, rate limits, `?next=` flow,
HttpOnly storage, 15m/30d lifetimes, reuse-detection response. Customization
changes presentation only — security behavior is not themable.

## 6. Storefront demo (`E:\E-Commerce\index.html` `#/auth` + knobs drawer)

Status: **implemented** (demo-grade: resets on reload; persistence with
cms-svc). Drawer controls: layout filter (both/centered/split), panel side
flip, gradient stops + angle → panels live, button bg/text → submits live,
input focus color, card radius slider, plain-text headline editor
(textContent-only, matching the allowlist rule). Forgot's separate set is
proven in code (`resolveSettings.ts` isolate path + unit test), not yet
exposed as a drawer control — deferred with font selects, image/overlay
controls, and per-page side segmentation.

Implemented against: `lib/auth/settings.ts` (vocabulary + builtins) ·
`lib/auth/resolveSettings.ts` (cascade + sanitizer) · `lib/auth/cssVars.ts`
(var map) · `components/auth/*` (composed dumb) · `app/(auth)/*/page.tsx`
(smart routes, chromeless — no header/footer until finalized).

## 7. Open items

* Image size cap + font-list final approval with cms-svc schema.
* Social OAuth providers/scope (real wiring, post-v1).
* Admin editor screen design (explicitly later).
