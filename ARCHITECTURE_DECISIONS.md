# Architecture Decisions (from the comment audit)

> Short ADRs distilled from the reasoning that currently lives in code comments.
> Each decision gets a heading, a one-line choice, the reason, and what it rules out.
> Full per-comment classification: `state-for-agents/comment-audit.csv`.

## ADR-contracts — Contracts are the shared source of truth
**Choice:** Every service and the storefront import versioned `@ecom/contracts` tarballs; no sibling imports.
**Why:** A polyrepo needs one place a payload can be right. Drift showed up as runtime parse failures, so the contract is pinned exactly, never a range.
**Rules out:** cross-repo source imports; floating `^` versions.

## ADR-events — Outbox in the same transaction
**Choice:** Producers write the finished envelope to `<schema>.outbox` inside the domain transaction; a relay publishes after commit.
**Why:** Publish-after-commit loses the event on a crash between the two; publish-before-commit announces something that may roll back. Storing the envelope means the relay re-derives nothing.
**Rules out:** fire-and-forget publishes; in-process buses.

## ADR-events — One group, one relay, key by aggregate
**Choice:** One Kafka group per service (`postfixId: ''`), one shared relay, messages keyed by aggregate id, sequential publish.
**Why:** A second group splits partitions and silently loses half the records; parallel publish breaks per-aggregate order. `FOR UPDATE SKIP LOCKED` plus a lease prevents double-claim and recovers from a crashed worker.
**Rules out:** one group per topic; parallel publish in a batch.

## ADR-events — Every topic has a DLQ twin
**Choice:** Invalid payloads go to `<topic>.dlq`; five retries with bounded backoff; a failed DLQ write stops the consumer rather than committing past a lost record.
**Why:** A lost poison message is silent data loss; an unbounded ladder outruns the Kafka session and loops forever on `UNKNOWN_MEMBER_ID`.
**Rules out:** infinite retry; committing past a failed dead-letter.

## ADR-sessions — Identity at the edge, never in JS
**Choice:** `sf_cid` is an HttpOnly guest cookie minted in `proxy.ts`; the BFF reads it as `x-session-id`; tokens never reach the browser.
**Why:** Minting on first write races two quick adds into two carts; HttpOnly keeps an XSS from stealing the basket.
**Rules out:** `localStorage`; mint-on-first-write.

## ADR-sessions — BFF is the only browser seam
**Choice:** Browser calls only this origin's `/api/**`; those routes forward over HTTP with identity headers.
**Why:** Keeps broker addresses, service URLs, and keys out of the client; one failure vocabulary on both sides of the seam.
**Rules out:** browser-side service clients; direct DB or Kafka from the edge.

## ADR-cache — Tag-based invalidation, bounded staleness
**Choice:** CMS reads use Next Data Cache tags with `revalidate: 300`; cms-svc calls `POST /api/revalidate` with an allowlisted tag and a constant-time secret compare.
**Why:** Time-based cache alone serves stale content for a full TTL; an unvalidated `revalidateTag` lets one loop flush the whole cache.
**Rules out:** open invalidation; per-request fetches with no cache handle.

## ADR-ui — Smart shell, dumb leaves
**Choice:** Route owns state and validation; `components/ui` is props → JSX; style state reaches CSS only through `data-*`.
**Why:** One place to decide, many places to paint; class toggles for state make style-contract tests impossible.
**Rules out:** fetch/store in `ui/`; class-based state flags.

## ADR-ui — Sparse overrides, resolver owns defaults
**Choice:** Flat props beat options object beats resolver defaults; absent means inherit; `null` rejects.
**Why:** Two sources of truth for a default freeze the theme out of the CSS-var chain and scatter `??` chains that are hard to test.
**Rules out:** component-level `||` fallbacks; writing `null` to reset.

## ADR-db — Raw SQL in Postgres, Mongoose for docs
**Choice:** Postgres uses parameterized hand-written SQL; Mongo uses Mongoose; no migrations in v1 (schema applied by SQL files).
**Why:** Learning goal is to understand the queries and indexes directly; document shapes suit an ODM. Migrations add moving parts while the schema is still settling.
**Rules out:** ORM/query builders; migration runners for now.

## ADR-testing — Trio per feature
**Choice:** Contract, resolver-unit, and style-contract tests; no merge without all three.
**Why:** Rendering tests alone miss wrong defaults; unit tests alone miss broken linkage; style tests catch hardcoded paint values that defeat theming.
**Rules out:** merges on a single test tier.

## ADR-comments — Why at the site only when code cannot show it
**Choice:** Keep short `// reason:` notes where AGENTS.md §5 requires them; move long decision prose into this file and leave a `// ADR-<id>: <slug>` pointer. Delete a comment only when both its claims and its reason are recoverable from the adjacent signature, control flow, types or imports. A reason naming a rejected alternative, an external constraint or a non-local invariant keeps the comment even when the action itself is obvious.
**Why:** A reader needs the local why only when the code cannot prove it. A comment that paraphrases the code is bloat by the same test AGENTS.md §3.4 applies to `??`. Blanket comment banning would break §5's reason-required rule, so the test is per-comment against its code. Pass 2 confirmed the failure mode: a mechanical first pass cut 186 storefront comments and 81 had to be restored because their reason was invisible in code.
**Rules out:** deleting a reason that records a rejected alternative, an external constraint or a non-local invariant; keeping a comment that restates the code; keyword- or length-based comment purges.

## ADR-comments-ratchet — Ratchet, not a big-bang ban
**Choice:** A comment counter records a per-repo baseline and fails only when the count increases.
**Why:** Not every comment can be removed in one pass; a hard ban would block all merges while the inventory is still being worked.
**Rules out:** a lint rule that forbids all comments immediately.

### Implementation (doc-006)
The counter is `scripts/comment-ratchet/count_comments.py` and its snapshot is
`scripts/comment-ratchet/comment-baseline.json` — one reviewable-comment count
per code repo. Run the script with no arguments from anywhere in the checkout;
it exits `1` only when a repo is above its baseline, so deleting comments can
never fail it. Generated files and the reason-required constructs of AGENTS.md
§5 (`reason:`, `ADR-*:`, lint/TS directives, `!important`/`console.`/`??`
justifications) are excluded because they are not removable by choice.

An addition is approved by judging it against ADR-comments and regenerating the
baseline with `--update-baseline` in the same commit, with the reason in the
commit body. `--repo` scopes a check and `--json` feeds another tool. The full
command list and the four-case acceptance test are in
`scripts/comment-ratchet/README.md`; the test proves that one added comment
fails and that removals pass.

No CI hook is configured here. This file documents the pre-merge check and the
script implements it; a job may call the same command later without editing it.

## ADR-media — Containment lives in one path resolver
**Choice:** All media reads go through `resolvePath`; the storage port takes a `read` function, not a path, and the local adapter reads through `resolvePath`.
**Why:** A symlink planted under the root must be rejected identically on upload, worker read, and delivery. A path-taking port would make each adapter invent its own containment rule.
**Rules out:** per-adapter path checks; trusting resolved paths from storage.

## ADR-privacy — Never echo rejected input
**Choice:** Body validation returns field names and a fixed message; the rejected value is never included in a 400 or a log.
**Why:** A beacon carries a page URL, which can contain a token in its query string. Echoing it would leak a credential into an error body or log.
**Rules out:** default Zod issue messages on public endpoints.

## ADR-testing — HTTP tests never join a consumer group
**Choice:** The Kafka consumer starts in a separate bootstrap (`startConsumer`) guarded by `KAFKA_CONSUMER_ENABLED`, and e2e suites call only `configureApp`.
**Why:** Every suite calls `app.init()`; if the consumer were wired into the HTTP module, an HTTP test would join the real group and steal offsets. The switch is a checked flag, not "is the module imported".
**Rules out:** consumers started by `configureApp`; module-presence detection.

## ADR-events — Closed DLQ reasons, deterministic failures
**Choice:** An import has exactly four repairable rejection reasons; a deterministic failure throws to roll back the `processed_events` claim and dead-letters immediately. `translateError` lets a service map a domain failure to a terminal reason.
**Why:** Redelivery cannot change a dangling reference or a conflicting sku, so burning the 31-second ladder on it is pure waste; a thrown exception is the only thing that rolls back the claim.
**Rules out:** retrying human-repairable failures; returning instead of throwing inside a claimed transaction.

## ADR-tokens — Six-layer paint architecture, admin chrome separate
**Choice:** Paint resolves in six layers — code-only primitives, admin-editable semantic storefront tokens (`--sf-*`), resolver-derived component tokens, AA-locked state tokens, scoped section/product overrides, and static admin chrome tokens (`--adm-*`). Merchant config writes only validated global palette pairs; reset deletes a key (inherits) and never writes `null`; status/focus/disabled/shell faces stay global; the admin tool never consumes merchant tokens.
**Why:** Admin must restyle the storefront without a code deploy, but merchant input cannot be trusted as CSS: numbers need declared clamps, fg/on pairs need AA contrast floors, names and values need sanitizing so a setting cannot inject arbitrary declarations, and the editor's preview must be the same surface production renders or WYSIWYG is a lie. A separate locked layer gives style-contract tests one place to assert those floors, and lets `--adm-*` chrome stay ink-based while the preview underneath shows ocean.
**Rules out:** raw admin-authored CSS variables; `null`-as-reset; merchant re-skin of `--adm-*` chrome; per-section override of status/focus/disabled/shell faces.

### Implementation (doc-008)
| Layer | Namespace | Who may write it | What it holds |
|---|---|---|---|
| 1. Primitives | `--sf-p-*` (code only) | code, never CMS | raw ramp samples; no hex literal in `components/` |
| 2. Semantic storefront | `--sf-*` | admin palette editor, global scope, validated + clamped | meaning: brand / ink / surface / status-bg pairs |
| 3. Derived component | `--sf-<component>-*` | resolver only | e.g. `--sf-button-bg` ← `--sf-brand`; not a direct admin knob |
| 4. Locked state | `--sf-focus*`, `--sf-disabled*`, `--sf-*-fg`/`--sf-*-on`, shell | resolver only, AA-clamped, global only | status foregrounds, focus + halo, disabled face, shell chrome |
| 5. Scoped overrides | inline `--sf-section-bg` / `--sf-section-fg`; product/slide flat props | per section or product | bg+fg pair and that section's own content knobs only |
| 6. Admin chrome | `--adm-*` | admin code only | static tool chrome; never merchant config |

Inheritance, highest to lowest (one default source — `lib/<domain>/` resolvers):

```text
product/slide flat prop
  → component theme (theme.button.*, theme.input.*, …)
  → section settings (bg + fg pair, plus that section's own content knobs)
  → global palette (--sf-* semantic tokens)
  → builtin (DEFAULT_* in lib)
```

`reset` deletes keys so the layer below shows through; it never writes `null`.
A section or product override accepts only the bg+fg pair and its own content
knobs — status faces, focus, disabled and shell tokens are global and cannot be
scoped. Legacy `--color-*` names remain aliases of `--sf-*` for one release
(sf-084); new code uses `--sf-*` only and no component-level `??` fallback may
bypass the var chain.

Rebuilt islands add **no new `useState`**: state lives in pure machines and
`useReducer` only, with timers/pointer ids/listeners in `useRef` + `useEffect`.
Reason: a reducer is a pure, testable transition table and keeps the
controlled-only rule intact; a local `useState` is a second, untested state
source. Rejected: ad-hoc `useState` per island and local boolean flags — full
rule in ADR-ui below.

Exact names/defaults: `design-system/storefront.md` §3.0. Admin separation:
`design-system/admin.md` §3.0. Planned artifacts: `components/customization.md`.

## ADR-ui — Pure machines use `useReducer`; side effects are not state
**Choice:** Every rebuilt island keeps behavioural state in a pure transition
machine driven by `useReducer`, with `open`/selection owned by the parent as
controlled props. Timers, pointer ids, abort controllers and listeners live in
`useRef` and are attached and removed in `useEffect`.
**Why:** A reducer is a pure, trio-testable transition table, so a state is
reachable only through a named event and the controlled-only rule stays intact.
A side-effect handle stored in state adds renders without adding meaning, and a
set of local boolean flags (`isOpen`, `isDragging`, `isLoading`) silently admits
impossible combinations — exactly how the prototype produced undefined states.
**Rules out:** new `useState` in rebuilt islands; local boolean flags as a
substitute for a machine; side-effect handles in state; generic machine
factories and XState (only the named states and events are ported).
**Does not rule out:** the `Select` custom-branch disclosure (sf-033,
AGENTS.md §3 rule 2) — the browser owns a native select's popup internally, so
the drop-in replacement may own that one disclosure when the parent does not;
the *value* stays controlled either way. An island needs no ADR for the
`useRef`/`useEffect` side-effect seam; any `useState` addition still needs one
with a documented reason at the site (AGENTS.md §5).

Indexed manifests: `components/README.md` §3 ·
`components/customization.md` §No-new-`useState` rule ·
`components/sections.md` §7.2 (rail machine).
