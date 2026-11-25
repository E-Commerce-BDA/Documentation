# Analytics Service — behavioral facts (analytics-svc :4060)

> What this file is: analytics-svc's contract — what it owns, what it consumes,
> and where the data lives. Copy the shape of `auth.md`.
> Status: Active | Date: 2026-11-23
> Parent: `1.Architecture.md` §6 · `8.Versioning.md` §1 ·
> `3.Database-Schema.md` · `tasks.json` → repos → `analytics-svc`

## Scope

Behavioral insight for the storefront: page-view and exit funnels, cart
idle→abandoned detection, conversion and cohorts. Writes are fire-and-forget;
no shopper flow waits on analytics.

| Concern | Value |
|---|---|
| Port | 4060 |
| Database | Mongo `ecom_analytics` (local URI uses the `rs0` replica set on port 27018) |
| Kafka group | `analytics-svc` — one group for all four consumed topics |
| Produces | `page.viewed`, `cart.abandoned` |
| Consumes | `cart.updated`, `order.created`, `page.viewed`, `user.registered` |
| SQS tasks | none |

## Mongo collections (anl-001)

| Collection | Key indexes | TTL | Reason |
|---|---|---|---|
| `page_views` | `createdAt` (TTL), `sessionId + createdAt` | 30 days | append-only view facts |
| `cart_events` | `createdAt` (TTL), `cartId + createdAt` | 60 days | cart lifecycle facts |
| `processed_events` | unique `eventId` | none | dedupe must outlive the facts it protects |

Indexes are declared in `src/db/indexes.ts` and applied at boot by
`IndexesService`; the declarations are unit-tested and the live indexes have an
e2e check that skips cleanly without Mongo.

## HTTP (shipped — anl-002)

`POST /api/v1/analytics/track` accepts the `pageViewedPayloadSchema` fields.
`timestamp` is optional on the wire — the server stamps it so a wrong client
clock cannot skew funnels. The response is **202 `{ status: "accepted" }`**
with `cache-control: no-store`.

- Invalid body → **400** `VALIDATION_FAILED` with field names only. Rejected
  values are never echoed, so a page URL containing a token cannot leak into a
  response or a log.
- Over the limit → **429** `RATE_LIMITED` with `Retry-After`. The limit is a
  per-`sessionId` sliding window, 60 events / 60s by default, configurable with
  `TRACK_RATE_LIMIT_MAX` and `TRACK_RATE_LIMIT_WINDOW_MS`.
- The validated beacon becomes one `page.viewed` row in `analytics_outbox`,
  written in a Mongo transaction keyed by `sessionId`. Nothing is published
  synchronously; the relay drains after commit. `page_views` facts are written
  by the Kafka consumer, not here.

The only caller is the storefront's Next route `/api/track` (sf-052). The
browser never sees a Kafka client. Duplicate HTTP beacons are not deduped at
ingest — at-least-once delivery and `processed_events` dedupe belong to the
consumer.

## Kafka ownership

- `page.viewed`: produced by anl-002 from HTTP ingest, keyed by `sessionId`,
  via a Mongo outbox row written in the same transaction as validation.
- `cart.abandoned`: produced by a one-minute scheduled detector from the latest
  active `cart_events` fact per cart. A cart is idle after
  `CART_ABANDONED_AFTER_MS` (default 30 minutes); `ABANDONMENT_SWEEP_ENABLED`
  (default true) parks the timer and `ABANDONMENT_SWEEP_BATCH_SIZE` (default 100)
  caps a sweep. The event is keyed by `userId`, or by `sessionId`/`cartId` for a
  guest. Exactly one event is emitted per cart per idle window: a marker in
  `abandonment_windows` keyed by `<cartId>|<lastActivityAt>` is inserted with the
  outbox row in one Mongo transaction, so a repeated scan is a no-op and a newer
  `cart.updated` opens a new window. The marker has no TTL, matching
  `processed_events`.
- Four topics consumed on one group, exactly `analytics-svc`: `cart.updated` →
  `cart_events` (60d), `order.created` → `order_events` (60d), `page.viewed` →
  `page_views` (30d), `user.registered` → `user_events` (60d, id and timestamp
  only). Each fact and its `processed_events` claim are written in one Mongo
  transaction; invalid payloads go to the topic DLQ. The retry ladder is bounded
  to a 20s budget, so five attempts over 15s of sleeps fit inside the 45s broker
  session. `KAFKA_CONSUMER_ENABLED=false` parks the consumer without touching
  the HTTP beacon.

## Gates

`pnpm typecheck`, `pnpm test`, `pnpm test:e2e` (skips without Mongo),
`pnpm lint`, `pnpm build`.

## Transport ownership (canonical)

Source of truth: `state-for-agents/STATUS.md` section 5. This table must match
the shared messaging catalog; a service may not claim a producer or consumer
that the running code does not own.

| Role | Topics / queues |
|---|---|
| Publishes | page.viewed (key sessionId), cart.abandoned (key userId) |
| Consumes | cart.updated, order.created, page.viewed, user.registered |
| SQS tasks | none |
| Must not | No SQS tasks. |
