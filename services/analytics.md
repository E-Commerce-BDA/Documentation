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

## HTTP (planned — anl-002)

`POST /api/v1/analytics/track` accepts `pageViewedPayloadSchema` and returns
**202** after validation and an outbox write. It never leaks PII and is called
by the storefront's Next route `/api/track`, which is the only component that
talks to this service. The browser never sees a Kafka client.

## Kafka ownership

- `page.viewed`: produced by anl-002 from HTTP ingest, keyed by `sessionId`,
  via a Mongo outbox row written in the same transaction as validation.
- `cart.abandoned`: produced by anl-004 from the idle-cart detector, once per
  cart per idle window.
- Four topics consumed by anl-003 with `processed_events` claimed in the same
  Mongo transaction as the fact write; invalid payloads go to the topic DLQ.

## Gates

`pnpm typecheck`, `pnpm test`, `pnpm test:e2e` (skips without Mongo),
`pnpm lint`, `pnpm build`.
