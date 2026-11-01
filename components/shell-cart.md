# Shell + cart blocks — purpose, mount rule, residents

> Scope: `frontend/storefront/components/shell/*` (production composed-dumb chrome) + the cart blocks that mount alongside it.
> Status: Active | Version 1.2 | Date: 2026-11-01
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
| Navbar | `components/shell/Navbar.tsx` | Regions-gated composition; --nb-* inline; `cart: { count, onOpen }` prop, zero local state |
| PageHeader | `components/shell/PageHeader.tsx` | `{ eyebrow?, title, breadcrumb?, actions? }` — the `pages/routing.md` §2 contract |
| CartLineItem | `components/shell/CartLineItem.tsx` | `{ line, pending?, onQty, onRemove }`; thumb + name + variant + stepper + line total |
| MiniCartDrawer | `components/shell/MiniCartDrawer.tsx` | `{ open, onClose, items, totals, status, onQty, onRemove, onCheckout }`; Esc + overlay close + focus restore |
| NavbarMount | `app/_components/NavbarMount.tsx` | Owns disclosure/dismiss/slides/scroll-hide/autoplay; auth self-suppress |
| SearchMount | `components/shell/SearchMount.tsx` | Registry's first caller; lazy variant + own search state (absorbed sf-026) |
| demoNavInput | `lib/shell/demoNavInput.ts` | Shared demo seam; cms-svc swaps one line per site |

Hook homes: shared islands in `app/hooks/` (`useSearch`); shell-local hooks beside their component; `lib/` stays pure (no hooks — state violates purity). Pure presentation maps (`tagTone`-style tag→tone tables) live in `lib/<domain>/`, never in components — one home, both variants read it.

## 4. Cart blocks (live)

`CartLineItem`, `MiniCartDrawer` and `PageHeader` live here with the same shape:
props→JSX, settings-driven, trio-tested, indexed here + README §1 +
`0.Project-Overview.md` §14 same-commit. `Footer` still lands with the launch
slice.

`CartProvider` (`app/_components/CartProvider.tsx`) is the *island* half: it owns
the cart store, renders `<MiniCartDrawer>` and feeds `NavbarMount` the
`cart={{ count, onOpen }}` prop. It is indexed here because the drawer and the
provider are one unit — the drawer never mounts anywhere else.

`NavCartButton.tsx` is now **wired**: the disabled "coming soon" trigger is gone
and the button renders `count` from the provider. The e2e loop is
NavCartButton → `onOpen` → drawer → `CartLineItem` → `onCheckout` → `/checkout`.

Cart state rules (why the provider exists):

- Optimistic mutation → BFF → revert + `Toast` on failure. A quantity change is
  debounced per line before it leaves the island.
- The drawer reads the **same** store as `/cart`; two surfaces, one reducer
  (`lib/cart/state.ts`), so a quantity changed in the drawer is already correct
  when the cart page paints.
- Guest identity is the `sf_cid` cookie (`proxy.ts` mints it); the drawer never
  needs a sign-in to show lines, and sign-in merges the guest cart server-side
  (A4.6).
