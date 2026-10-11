# Search overlays — variant matrix, selection model, registry contract

> Scope: every search overlay variant in `frontend/storefront` (look per variant, shared selection + motion + theme rules, what ships over the network).
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `components/README.md` (index + conventions)

---

## 1. Variant matrix (look per variant)

| Variant | File | Look | Status |
|---|---|---|---|
| Classic | Showcase `§13` feel-test only (no production file) | Centered dialog, trap vs light tested | Fallback behavior; trap won, kept as fallback |
| Palette | *(to build, sf-024)* | Centered modal: filters, trending + recent, quick-add, keyboard hints | Coming |
| Sheet | `components/shell/SearchSheet.tsx` + `.sf-searchsheet` | Top slide-down panel, dept pills, cards | ✅ live (showcase §14) |
| Editorial | `components/shell/SearchEditorial.tsx` + `.sf-editorial` | Scrollable full-screen takeover, serif input, curated grid | ✅ live (showcase §16) |
| Inspect | *Removed (sf-022)* | Split modal, hover preview, size select | Built sf-019→021, removed: photo mismatch. History preserved in log, never rewritten |

New variants add a row here, a settings instance, a component + CSS block, a registry line, and a showcase section — never an edit to a sibling variant.

## 2. Selection ≠ build-time (the core rule)

**Rule:** admin selection never changes what's in the build. The build ships all variant chunks; selection happens per request: server resolves CMS settings → passes `variant + resolved theme` as props → client island loads only that chunk. One build, infinite admin combinations, zero rebuilds.

**Why:** builds are slow and global; admin decisions are fast and per-shop. Tying selection to the build would mean a deploy per knob change and one build per variant. Per-request resolution keeps customization instant (new prop values, no new code).

**What breaks without it:** a build-time-selected variant bakes one shop's choice into every deploy; multi-shop CMS becomes impossible; previewing a variant requires a rebuild.

**Proof:** build-output test asserts unselected chunk markers absent from served JS (sf-026 assembler wires this; until then the registry's single-importer discipline holds by review).

## 3. Network inventory (what travels, why only this)

| When | Travels | Why |
|---|---|---|
| First paint | Server HTML + page JS. Overlay code: zero bytes (closed overlay mounts nothing) | Overlay content depends on interaction state; hidden dialog HTML wastes bytes |
| Near search | Selected variant chunk only (hover/focus preload on the trigger) | `next/dynamic` static import map; unselected variants unreferenced by any production path |
| Typing | Suggest JSON only (`q → results`, 300ms debounce, min-2 gate, stale-kill) | Port boundary: `useSearch` never knows endpoints (`lib/search/source.ts`) |
| Always | Settings as inlined `--ed-*`/`--searchsheet-*` vars + tiny props (bytes, not code) | Resolver runs server-side; client receives concrete values, never knob names |

Admin customization strengthens this model: knobs are JSON/vars, not code, so customized overlays need no new chunks — only fresh prop values resolved on every request.

## 4. Registry contract (`components/shell/searchRegistry.ts`)

**Rule:** one static dynamic-import per built variant; unbuilt variants resolve to `null` (caller falls back to classic), never to a wrong variant. The registry is the *only* production importer — static overlay imports are banned outside `app/components/` (showcase) and the registry itself.

**Why:** bundlers can only split what they can statically see. A variable `import(path)` would defeat analysis and ship everything; one literal import per variant keeps each chunk addressable and the rest droppable.

**What breaks without it:** a single static import in a production path pulls every variant into the page bundle — the whole selection model silently stops working.

**Proof:** CI lint rule banning static overlay imports in production paths + build-output chunk-absence test (both land with sf-026; until then review-enforced).

## 5. Shared variant rules (apply-to-all)

- **Motion per-variant instances:** shared `OverlayMotionField` shape, one resolved instance per variant (`sheetAnimation`, `editorialAnimation`, …). Preset → concrete ms+easing in the resolver; components inline vars and never see preset names. Reason: a sheet slides, a takeover fades — neither setting may leak into the other.
- **Theme object, not flat props:** variants with 10+ paint knobs take one resolved `theme` object (flat copy wins for the 2–3 most A/B-tested text knobs only). Reason: fifteen flat color props is prop explosion; the object stays controlled (parent-owned) with the trio precedence intact.
- **Curated-before-typing:** empty query shows a `curated` grid; 2+ chars switch to live results. Reason: the overlay must read as a destination on open, not an empty box waiting for input.
- **Trap wins:** every overlay traps Tab, closes on Esc, returns focus. Locked feel-test verdict (§13); full-screen scroll still traps.
- **SEO:** overlay mounts only when open (closed = zero DOM, no duplicate content for crawlers); headings inside capped below the page's single `h1`; card buttons carry `name, $price` labels so card images stay `alt=""` (no double-announce).
- **Paint/state/motion → `.sf-*` CSS (var-only); layout → utilities or block CSS per file precedent.** Global `globals.css` keeps all variant CSS (~3KB gzip per variant) — no flash-risk on variant switch, style-contract tests read one file. Revisit trigger: variant CSS past 50KB (see `pages/launch.md`).

## 6. Feel-test verdicts (assembled — rationale, not just outcomes)

- **Trap over light dismiss** (§13, sf-016): no keyboard user left behind the overlay.
- **Oceanic arrival for takeovers** (sf-018/023): full-screen = fade + small rise; sheet = pure slide, zero opacity by variant decision.
- **Per-visit recent memory, never `localStorage`** (locked): tokens and history stay out of JS persistence.
- **Inspect removed, not fixed** (sf-022): photo mismatch at the concept level — forward deletion over revert, history preserved as record.

## 7. Service ports (swap map — microservice coupling without rewrites)

| Need | Port (`lib/`) | Demo today | Real service later | Owner |
|---|---|---|---|---|
| Ranked suggest | `search/source.ts` `SearchSource` | `demoSource.ts` (+ `DEMO_CATALOG`, `DEMO_TRENDING`) | search-svc | `useSearch` |
| Trending terms | `search/trending.ts` `TrendingSource` | `DEMO_TRENDING` | search-svc / CMS | palette (prop) |
| Quick add | `cart/quickAdd.ts` `QuickAddPort` | `createDemoQuickAdd` (120ms, always ok) | cart-svc | `useQuickAdd` |
| Recent terms | *No port* — visit memory only | `useRecentSearches` | — (ban forbids persistence) | palette (props) |

**Swap rule:** one line at the call site (hook construction / showcase wiring). Contract tests stub the port, never the network — proven before the backend exists. Demo files are throwaway-by-replacement: the service replaces the file, callers never change. Shared interactive faces converge on `pill.md` (one Pill, all variants); shared tag faces converge on the `tagTone` lib map.
