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
**Choice:** Keep short `// reason:` notes where AGENTS.md §5 requires them; move long decision prose into this file and leave a `// ADR-<id>: <slug>` pointer. Delete Tautology, Stale and Excuse comments, including any "why" comment that only restates what the signature, control flow or imports already show.
**Why:** A reader needs the local why only when the code cannot prove it. A comment that paraphrases the code is bloat by the same test AGENTS.md §3.4 applies to `??`. Blanket comment banning would break §5's reason-required rule, so the test is per-comment against its code.
**Rules out:** deleting a reason that records a rejected alternative, an external constraint or a non-local invariant; keeping a comment that restates the code.

## ADR-comments — Ratchet, not a big-bang ban
**Choice:** A comment counter records a per-repo baseline and fails only when the count increases.
**Why:** Not every comment can be removed in one pass; a hard ban would block all merges while the inventory is still being worked.
**Rules out:** a lint rule that forbids all comments immediately.

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
