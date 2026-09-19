# Button — Component Rules (template for all components)

> Scope: `frontend/storefront/components/ui/Button.tsx` + `app/globals.css` `.sf-btn`
> + `lib/cms/buttonAnimation.ts` (types, defaults, P>S>G resolver — the only
> `??` allowed near buttons).
> Status: Active | Version 1.1 | Date: 2026-09-17
> Parent: `design-system/storefront.md` §7.1 (palettes) · `9.Testing.md` §base
> Implements: 5 faces (default / hover / focus-visible / pressed / disabled+loading)

This is the **template every component doc copies**: §1 look per type, §2
customizable fields, §3 how to change (scopes), §4 global rules, §5 apply-to-all.

---

## 1. Look per type (what each state looks like — normative)

| Type | Face | Text | Border | Motion |
|---|---|---|---|---|
| **Default** | variant palette (§7.1 table) | variant text | variant border | none at rest |
| **Hover** | travelling wave layer (`--wave-bg`) to full cover | swaps to `--wave-text` after `0.2s` delay | swaps to `--wave-border` after `0.2s` delay | `wave-rise 360ms cubic-bezier(.32,.72,.32,1)` (or `animationKind`) |
| **Focus-visible** | unchanged | unchanged | unchanged | `2px accent outline + offset 2` — **fixed, not customizable** (a11y requirement) |
| **Pressed** | unchanged (effect OFF by default) | unchanged | unchanged | none, unless admin enables `pressed.*` |
| **Disabled + Loading (shared face)** | `#DCE8EE` solid | `#0A2540` solid (≈12:1) | `#DCE8EE` | **none — no wave, no swap, `transition: none`**; loading adds spinner + `aria-busy` |

Rules baked into CSS and guarded by `test/components/button-states.test.ts`:
- **No hover effect on disabled/loading, ever, by default.** `:hover`
  matches disabled elements, so every hover selector carries
  `:not([disabled]):not([aria-disabled="true"])`. A bare `.sf-btn:hover`
  is a bug and fails CI.
- **Disabled face is explicit solids, never `opacity`.** Fading text and
  face together destroys contrast (white on faded blue ≈ 1.5:1 — the
  shipped bug). `opacity: 0.5` on `.sf-btn[disabled]` fails CI.
- **Loading = disabled face + spinner.** Loading is non-interactive
  (double-submit protection), so it can never have its own look. The
  spinner uses `currentColor` and inherits the readable ink text color.

## 2. Customizable fields (what admin can change)

All fields optional everywhere (absent = inherit); `Reset` deletes the key,
never writes `null`. Numeric knobs clamp to the listed ranges.

| Group | Field | Control | Default |
|---|---|---|---|
| Look | `bg / textColor / borderColor / borderWidth 0–4 / radius 0–24·pill` | color pickers + sliders | variant palette, `1px`, `8px` |
| Hover | `animationKind` (wave-rise/fade*/linear/none), `waveOrigin`, `peaks 1–3`, `peakHeight 4–24px`, `durationMs 0–1000`, `textDelayMs 0–500`, `easing`, `hoverBg/hoverText/hoverBorderColor` | selects + sliders + pickers | wave-rise bottom 2-peak `360/200ms` smooth, per-variant wave colors |
| Pressed | `pressed.enabled`, `pressed.scale 0.9–1`, `pressed.translateY 0–8px`, `pressed.shadow` | toggle + sliders + shadow input | **all off** (`enabled: false` reproduces today — no `:active` rule ever existed) |
| Disabled+Loading | `disabled.bg/textColor/borderColor/borderWidth 0–4`, `disabled.hoverEnabled` | pickers + slider + toggle | `#DCE8EE / #0A2540 / #DCE8EE / 1px`, hover **off** |
| Visibility | `showIcon?`, `showLoader?`, `fullWidth?`, `size sm/md/lg` | toggles + select | on / on / off / `md 44px` |

`disabled.hoverEnabled: true` opts into a **palette-only** swap on disabled
hover — the travelling wave stays `display: none` regardless. Focus ring is
intentionally absent from this table.

## 3. How to change (scopes — where a value lives)

Precedence: **instance (`ctas[].animation`) ?? section settings ?? global
theme ?? DEFAULT** (`resolveButtonAnimation`, tested in
`test/components/button-animation.test.ts`).

- **One button:** set fields on that CTA's `animation` object (flat
  component props like `disabledBg` win over keys inside `animation` —
  same object, convenience layer only).
- **One section:** `section.settings.buttonAnimation` (or `.disabled` /
  `.pressed` subgroup) — every button in the section inherits unless it
  overrides that key.
- **Everywhere:** `theme.buttonAnimation` — the global default.
- Prefill rule (admin UX): the form always shows **resolved** values (what
  the button looks like now) but stores only **edited** keys (sparse).

## 4. Global rules (what holds for every component, not just Button)

1. **One shared geometry per component.** Variants/sizes differ by CSS
   vars only. A second copy of a `::before`/layout rule is a bug — sizes
   scale by `%`, never by duplicated rules.
2. **Parked layers keep a px buffer.** Any layer parked outside the box
   rests at `100% + ≥8px`, never a bare `%` — subpixel rounding eats
   ~0.5px margins at some zooms (the wave-bleed bug). Guarded by
   `test/components/wave-park.test.ts`.
3. **Dead elements never animate by default.** Disabled/loading get no
   hover, no travel, no transition. Opt-ins are explicit data attrs
   defaulting to off, and CI asserts the default.
4. **No hex literals, no `??`, no fallbacks in components.** Vars flow
   server → inline `style` → bare `var(--x)` in CSS. The resolver is the
   only place defaults live.
5. **Dumb contract:** `props → JSX`. No fetch, no store, no CMS import in
   `components/ui`.

## 5. Apply-to-all (the per-type bulk switch)

Each customizable **group** (look / hover / pressed / disabled) gets an
`Apply to all buttons of this scope` switch in the admin form:

- Target scope picker: `this button | this section | all sections (global)`.
- Writes the edited group at the chosen scope; display name shows where
  each value currently resolves from (instance/section/global/default).
- Clearing a group at a scope deletes its keys (inherit downward again).

---

## Appendix — file references

- Component: `frontend/storefront/components/ui/Button.tsx`
- Styles: `frontend/storefront/app/globals.css` (`.sf-btn`, wave, states)
- Model: `frontend/storefront/lib/cms/buttonAnimation.ts`
- Tests: `frontend/storefront/test/components/` (`wave-park`, `button-states`,
  `button-animation`, `button`)
- Tokens: `design-system/storefront.md` §3 (never hex in components)
