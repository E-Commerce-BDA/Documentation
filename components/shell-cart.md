# Shell + cart blocks — purpose, mount rule, residents

> Scope: `frontend/storefront/components/shell/*` (production composed-dumb chrome) + the cart blocks that mount alongside it.
> Status: Active | Version 1.3 | Date: 2026-11-02
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
| Footer | `components/shell/Footer.tsx` | CMS footer document → two faces (`data-face="cms"`/`"minimal"`); fetches nothing (§5) |
| PageHeader | `components/shell/PageHeader.tsx` | `{ eyebrow?, title, breadcrumb?, actions? }` — the `pages/routing.md` §2 contract |
| Breadcrumbs | `components/shell/Breadcrumbs.tsx` | Crumb nav without a title — for documents that own their `<h1>` (blog article, CMS page) |
| CartLineItem | `components/shell/CartLineItem.tsx` | `{ line, pending?, onQty, onRemove }`; thumb + name + variant + stepper + line total |
| MiniCartDrawer | `components/shell/MiniCartDrawer.tsx` | `{ open, onClose, items, totals, status, onQty, onRemove, onCheckout }`; Esc + overlay close + focus restore |
| NavbarMount | `app/_components/NavbarMount.tsx` | Owns disclosure/dismiss/slides/scroll-hide/autoplay; auth self-suppress |
| FooterMount | `app/_components/FooterMount.tsx` | Server-resolved footer props; auth self-suppress (`AUTH_PATHS` duplicated per §5) |
| SearchMount | `components/shell/SearchMount.tsx` | Registry's first caller; lazy variant + own search state (absorbed sf-026) |
| demoNavInput | `lib/shell/demoNavInput.ts` | Shared demo seam; cms-svc swaps one line per site |

Hook homes: shared islands in `app/hooks/` (`useSearch`); shell-local hooks beside their component; `lib/` stays pure (no hooks — state violates purity). Pure presentation maps (`tagTone`-style tag→tone tables) live in `lib/<domain>/`, never in components — one home, both variants read it.

## 4. Cart blocks (live)

`CartLineItem`, `MiniCartDrawer` and `PageHeader` live here with the same shape:
props→JSX, settings-driven, trio-tested, indexed here + README §1 +
`0.Project-Overview.md` §14 same-commit.

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

## 5. Footer block (live — sf-062)

`components/shell/Footer.tsx` is the global link shell, painted from the cms-svc
footer document (contracts 1.12.0 `footerSchema` — columns ≤6, social, legal,
contact, logo/wordmark/tagline, copyright, payment chips). Dumb like everything
here: it fetches nothing, so "the footer changed" is never a deploy.

**Two faces, decided upstream — the block never chooses:**

| `footer` prop | Face | Who produced it |
|---|---|---|
| document | `data-face="cms"` — every row is admin data | `lib/cms/footer.ts` `fetchFooter()` cascade: source → in-process stale cache → `null` |
| `null` (cms-svc unreachable *and* nothing cached/saved) | `data-face="minimal"` — `FALLBACK_FOOTER_LINKS`: the four real routes `/products`, `/about`, `/privacy`, `/terms` | same loader; the footer's fallback is `null`, never an invented document (navigation falls back to demo input; a footer's columns *are* content) |

A footer that vanishes on an outage takes the site's navigation with it; a
footer that invents columns is a lie. Four true links is the honest middle.

**Rules:**
- Mount: `app/layout.tsx` resolves server-side (`Promise.all` with nav) and
  renders `<FooterMount footer={…}>` **after `{children}`** — the footer is the
  document's endfoot, so DOM order matches paint order (deliberate deviation
  from "directly after NavbarMount"). FooterMount is the client island and
  self-suppresses on `AUTH_PATHS` (`/signin`, `/signup`, `/forgot`) exactly like
  NavbarMount; the literal is duplicated on purpose — nav and footer may differ
  per surface, and one shared const would couple two independent decisions.
- Internal hrefs are plain `<a>` strings, never `next/link`: the shape is
  validated admin data, we never prefetch it, and a client router adds nothing
  to a server-only shell. Anything absolute is external by definition →
  `rel="noopener noreferrer"` + `target="_blank"`.
- `social[].platform` becomes `data-platform` and nothing else — an icon sprite
  is a stylesheet decision, and drawing a fake glyph for a network we have no
  artwork for is invented content. `paymentIcons` are display-only labels
  (no payment-brand asset pipeline exists yet).
- Paint: `.sf-footer*` block in `app/globals.css`; geometry fixed there, every
  fill/size through `--footer-*` vars with token fallbacks (`--footer-bg`,
  `--footer-link`, `--footer-focus`, `--footer-col-min`, `--footer-measure`…).
  The inner container pads with the shared `--sf-page-pad` gutter, so shell and
  pages align on one edge; columns are `auto-fit` so an admin-authored 1..6
  count never looks broken.
- Tests: `test/components/footer.test.tsx` (behaviour + layout-wiring guards),
  `test/components/footer-style.test.ts` (paint-through-vars contract),
  `test/lib/cms/footer.test.ts` (cascade).
