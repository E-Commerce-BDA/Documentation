# Launch — deletion checklist, preview gating, runbook

> Scope: everything that must happen exactly once when the storefront launches (demo-surface deletion, preview-route gating, bundle verification).
> Status: Active | Version 1.0 | Date: 2026-10-11
> Parent: `0.Project-Overview.md` (Docs Index §14)

---

## 1. `/components` showcase deletion (owner: launch captain)

**Rule:** `frontend/storefront/app/components/` (route `/components`, file `page.tsx`) is deleted at homepage launch. It is scaffolding with an expiry date — not a product surface, never linked from shop chrome.

**Why it exists at all:** dumb components need a driven surface before their production mount points exist. The showcase is that surface; the file header says so (`TEMPORARY living showcase — DELETE at homepage launch`).

**Checklist (in order):**
1. Confirm every showcase section has a production mount: §13 feel-test retired (verdicts in `components/search-overlays.md` §6), §14 sheet + §16 editorial mounted via SearchMount (sf-026).
2. Delete `app/components/` entirely (one commit, no stragglers — grep `components/page` repo-wide after).
3. Remove the `Component showcase` link from `app/page.tsx:52`.
4. Run the merge gate (`pnpm test` + `tsc --noEmit` + `next build --webpack`) — all green.
5. Run the bundle proof: unselected overlay chunk markers absent from served JS (the sf-026 test covers this; on launch day read its output, don't assume).

**What breaks without it:** demo routes ship to shoppers (crawlable, confusing, a second unmaintained UI); static showcase imports keep unselected variants in the bundle, silently voiding the selection model.

## 2. Preview-route gating (`/preview/search?variant=…`, lands with admin preview)

**Rule:** the preview route is `noindex, nofollow` + auth-gated (admin session). It reads *draft* CMS JSON, resolves server-side, renders the variant — so admin sees unsaved knob changes instantly through the same code shoppers get.

**Why gating:** an ungated preview is a crawlable duplicate storefront and a settings oracle (attackers read knob values). Two checklist lines prevent both; duplication of components into the admin app is rejected (see `1.Architecture.md` §16 — single codebase wins).

## 3. CSS revisit budget

**Rule:** variant CSS stays global (`globals.css`) until measured variant CSS passes 50KB. The trigger is a number from `next build` output, not a feeling.

**Why:** ~3KB gzip per variant buys zero flash-risk on variant switch, zero new machinery, and keeps style-contract tests reading one file (see `components/search-overlays.md` §5).

## 4. Launch-day runbook order

1. CMS settings frozen + snapshotted (rollback copy).
2. Showcase deletion (§1 checklist).
3. Preview route gated (§2 verification: curl without session → 401/redirect; response headers carry `noindex`).
4. Merge gate + bundle proof green.
5. Deploy per `7.Deployment.md` (when it exists); verify `/` first paint carries zero overlay bytes.
