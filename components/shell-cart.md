# Shell + cart blocks — purpose, mount rule, residents

> Scope: `frontend/storefront/components/shell/*` (production composed-dumb chrome) + cart blocks when the cart slice lands.
> Status: Active | Version 1.1 | Date: 2026-10-27
> Parent: `components/README.md` (index + conventions)

---

## 1. Purpose (what "shell" means — and what it is not)

**Rule:** `components/shell/` holds production composed-dumb chrome: domain-arranged props→JSX blocks (navbar pieces, drawers, search overlays) with no fetch/store/state. It mounts from the root layout; every page inherits it.

**Why a separate folder from `components/ui/`:** ui holds type-pure primitives (button, badge, input); shell holds *composed* blocks wired from several primitives + settings (e.g. SearchSheet = input + dept pills + cards + motion vars). Depth rule (AGENTS.md §2): everything gets dumber with depth — shell is the last dumb layer before routes.

**What it is not:** the `/components` showcase (`app/components/page.tsx`) is a temporary demo surface, deleted at homepage launch (see `pages/launch.md`). Shell components are the product; the showcase merely renders them. Never delete shell with the showcase; never import showcase code into shell.

**What breaks without this distinction:** launch day deletes the demo route and — without the boundary written down — takes production chrome with it, or leaves demo helpers imported by production files.

## 2. Mount rule

**Rule:** shell mounts once at the root layout. Pages inherit it; per-page differences travel as *settings*, never as conditional markup in the shell. Server resolves settings → passes variant + theme props → client islands load behavior (see `search-overlays.md` §2–4 for the overlay instance of this rule).

**Why:** one mount means one focus scope, one trap contract, one place where chrome can break. Per-page `if` trees in the shell become untestable within weeks.

## 3. Current residents

| Block | File | Contract (one line) |
|---|---|---|
| NavLinks | `components/shell/NavLinks.tsx` | Dumb link row; active/highlight/badge via props |
| AnnouncementBar | `components/shell/AnnouncementBar.tsx` | Dismissible bar; two-phase collapse, reduced-motion instant |
| SearchSheet | `components/shell/SearchSheet.tsx` | Sheet variant (see `search-overlays.md`) |
| SearchEditorial | `components/shell/SearchEditorial.tsx` | Editorial variant (see `search-overlays.md`) |
| SearchPalette | `components/shell/SearchPalette.tsx` | Palette variant (see `search-overlays.md`) |
| searchRegistry | `components/shell/searchRegistry.ts` | Variant → dynamic import; null over wrong (see `search-overlays.md` §4) |
| NavLogo | `components/shell/NavLogo.tsx` | Image or wordmark; anchor announces it |
| NavSearchTrigger | `components/shell/NavSearchTrigger.tsx` | Search glyph; hover/focus preloads the overlay chunk |
| NavAccountButton | `components/shell/NavAccountButton.tsx` | User glyph; menu deferred (no menu primitive) |
| NavWishlistButton | `components/shell/NavWishlistButton.tsx` | Heart + capped count badge; guest click prompts sign-in (no guest wishlist) |
| MobileDrawer | `components/shell/MobileDrawer.tsx` | Slide panel + NavLinks; trap + Esc (parent owns open) |
| Navbar | `components/shell/Navbar.tsx` | Regions-gated composition; --nb-* inline; zero state |
| NavbarMount | `app/_components/NavbarMount.tsx` | Owns disclosure/dismiss/slides/scroll-hide/autoplay; auth self-suppress |
| SearchMount | `components/shell/SearchMount.tsx` | Registry's first caller; lazy variant + own search state (absorbed sf-026) |
| demoNavInput | `lib/shell/demoNavInput.ts` | Shared demo seam; cms-svc swaps one line per site |

Hook homes: shared islands in `app/hooks/` (`useSearch`); shell-local hooks beside their component; `lib/` stays pure (no hooks — state violates purity). Pure presentation maps (`tagTone`-style tag→tone tables) live in `lib/<domain>/`, never in components — one home, both variants read it.

## 4. Cart blocks (to-come at cart slice)

`CartLineItem`, `MiniCartDrawer`, `Footer` land here with the same shape: props→JSX, settings-driven, showcase-demoed, trio-tested, indexed here + README §1 + `0.Project-Overview.md` §14 same-commit. This section stays a stub until then — no placeholder components that get deleted later (AGENTS.md route-chrome rule, applied to shell).

`NavCartButton.tsx` already exists on disk but stays **unmounted and unwired** until this slice — a trigger with no drawer is dead UI, and dead UI is worse than absent UI. It mounts here with the drawer, not before.
