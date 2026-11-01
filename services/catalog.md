# Catalog Service — Event Surface (catalog-svc :4020)

> What this file is: catalog-svc's Kafka behaviour — what it consumes, what it
> produces, and the one rule that decides what an imported stock figure means.
> Status: Active | Version 1.0 | Date: 2026-11-01
> Parent: `1.Architecture.md` §6 · `8.Versioning.md` §1/§8 ·
> `3.Database-Schema.md` §3.2
> Referenced by: `4.API-Design.md` §3.2 · `9.Testing.md` §3.2/§5.2 ·
> `10.Observability.md` §3 · `services/cart.md` §6.5 · `services/search.md` §5

**Scope.** This file covers the event surface only. Catalog's HTTP API lives in
`4.API-Design.md §3.2`, its tables in `3.Database-Schema.md §3.2`, and its store
behaviour in `5.Features.md`. It exists as its own file because `cat-007` and
`cat-008` turned catalog-svc into the platform's most involved messaging
participant — five outbox-triggering mutations on one side, two consumed topics
on the other, and a stock rule that can lose money if it is written down wrong.

---

## 1. The big picture

```
catalog admin writes  ──►  products / variants / images / discounts / badges
                                    │  same transaction
                                    ▼
                           catalog.outbox  ──► relay ──► product.updated
                                                        category.updated

import-svc  ──► product.imported ─┐
order-svc   ──► order.created     ─┴─► catalog-svc consumer (group: catalog-svc)
                                             │
                                             ├── order.created   → hold or release a reservation
                                             └── product.imported → upsert product/variants/images
```

Two consequences worth stating plainly:

- **The producer half never runs during a consume.** An import does not publish
  `product.updated` (see §5.7); a reservation hold does not publish anything.
- **The consumer half is one process, one group, one commit protocol.** Both
  topics ride a single Nest strategy, so `catalog-svc` is one group id and never
  splits into a `catalog-svc-server` twin with its own offsets.

---

## 2. The consumer

| Setting | Value |
|---|---|
| Transport | `@nestjs/microservices` Kafka transport via `@ecom/messaging` `0.3.0` |
| Entry point | `src/events/catalog-consumer.controller.ts` — two `@EventPattern` methods |
| Topics | `order.created` (3 partitions, key `orderId`), `product.imported` (1 partition, key `productId`) |
| Consumer group | `catalog-svc` — exactly the service name (`postfixId: ''`) |
| Offset | manual: `autoCommit: false`, committed only after the handler's transaction commits |
| Deserializer | `value.toString()`; parsing is the handler's job, so a malformed record is dead-lettered rather than crashing the transport |
| Dedupe | `catalog.processed_events` (`event_id` PK, `topic`, `processed_at`), claimed inside the handler's transaction |
| Switch | `KAFKA_CONSUMER_ENABLED` (default `true`; `false` in the e2e suites) |
| Stats | `GET /api/v1/catalog/internal/consumer-stats`, `x-service-key`, `no-store` |

`app.connectMicroservice({ strategy: createKafkaConsumerStrategy({…}) })` plus
`startAllMicroservices()` is what subscribes; `app.listen()` does neither. The
start is **not awaited** by `main.ts` and a broker that is down is retried every
five seconds — catalog still answers HTTP reads while Kafka restarts, and the
reservations catch up afterwards.

`@Payload()` and `@Ctx()` on both methods are load-bearing: a handler that
declares no parameter decorator is called with the payload only, because Nest's
`RpcContextCreator` falls back to `DEFAULT_CALLBACK_METADATA` (one PAYLOAD at
index 0). The second positional parameter would then be `undefined` and every
commit would fail on `ctx.getMessage()`.

What the controller owns is the topic list and the mapping to the two handlers.
Parsing, the 5-attempt retry ladder (1/2/4/8/16 s), the dead letter, the
counters and the offset commit all belong to `KafkaEventHandler`, shared with
cart-svc and search-svc.

---

## 3. Route `order.created` — reserve, and nothing else

`OrderCreatedHandler` was **not** touched by the transport change (`cat-008`,
decision `R4`): it still reads the envelope, parses `order.created`, claims the
event and takes or releases the hold in one transaction. Only the plumbing
around it moved from a hand-written `kafkajs` consumer to the shared strategy,
and `test/order-created.e2e-spec.ts` passes unchanged.

| Outcome | Counter | Offset | Side effect |
|---|---|---|---|
| Held (or released) for the first time | `accepted` | committed | stock reserved, one `sale` movement, one `processed_events` row |
| This event id was already applied | `duplicate` | committed | none |
| Envelope's type is not `order.created` | `ignored` (`not-subscribed`) | committed | none |
| Nothing to reserve for this order | `ignored` (`no-reservation`) | committed | none — a committed `ignored`, never a dead letter |
| Envelope or payload fails validation | `invalid` | committed after the DLQ write | none |
| Reservation already closed / does not match | dead letter | committed after the DLQ write | none |
| Database error | — | committed **after** the DLQ write | retried 5× first, then `transient-exhausted` |

`reservation-closed` and `reservation-mismatch` are named through
`translateError` in `src/events/events.module.ts`, so they dead-letter on the
first attempt instead of burning 31 seconds on an answer that cannot change.

---

## 4. Route `product.imported` — the upsert

`src/events/product-imported/product-imported.handler.ts` +
`product-import.repository.ts`.

Classification happens **before** any transaction opens: envelope, then payload
against `product.imported`'s schema, then the money strings. Prices arrive as a
string from some producers and a number from others, so they are coerced to
numbers here — a string that is not a number at all is `invalid-payload`, not a
database error loop. `effectivePrice` from the payload is deliberately dropped:
catalog derives it from `catalog.product_discounts` everywhere else, and a feed
cannot express a discount window.

Then **one transaction** contains all of it:

1. **Claim.** `ProcessedEventsStore.claim(client, eventId, 'product.imported')`
   → `false` means this is a replay: return `duplicate` and write nothing.
2. **Category.** `categoryId` given ⇒ must exist, else `unresolved-reference`.
   Only `categorySlug` ⇒ slugify, then find-or-create (`is_active` true).
   Neither ⇒ `null`.
3. **Brand.** Same rule with `brandName`. Find-or-create is
   `INSERT … ON CONFLICT (slug) DO NOTHING` plus a re-read, so two concurrent
   imports share one row instead of racing.
4. **Product**, upserted by `id = payload.productId` — never "by sku", because
   the event carries the id and a sku held by *another* product is a collision
   for a human, not an overwrite. A new row is inserted with `source = 'import'`.
   An existing row's `source`, `external_id`, `photo_settings`, `card_settings`,
   `tags`, `attributes`, discounts, badges, options and `deleted_at` are **not**
   in the `SET` list: an import states what a product *is*, not how it looks or
   where it came from. A `sku` or `slug` already held by a different product id
   is `sku-conflict` / `slug-conflict`.
5. **Status.** `active` → `active`; anything else → `draft`, except that an
   `archived` row stays `archived`. Withdrawal is a local decision and only a
   later explicit `active` undoes it.
6. **Variants** (`variants[]`, contract `1.9.0`). Upserted by `sku`, setting
   `price`, `stock`, `image_url`, `is_active`, `updated_at`. A `sku` belonging to
   another `product_id` is `variant-sku-conflict`: rewriting its `product_id`
   would move a live cart line to another product. **Variants are never deleted
   for being absent** — absence is ambiguous ("the feed dropped it", "the array
   was omitted", "a partial import") and a deleted variant takes its stock
   movements with it.
7. **Images** — replace-set, product level only, because `imageRefSchema` is a
   bare string and a payload cannot say which variant an image belongs to. Three
   ordered steps: clear the old primary (otherwise `one_primary_per_product`
   fires), delete the urls no longer present, then upsert each remaining url with
   `sort_order` = array index and `is_primary` = `index === 0`. Duplicates in the
   payload are collapsed first-seen. `null` means "the payload said nothing" and
   leaves the set alone; `[]` clears it.
8. **No outbox row.** Search receives the change from `product.imported`
   directly, so a 10 000-row import does not become 10 000 extra
   `product.updated` events. This is deliberate (`D2`) — do not "fix" the missing
   emit.

Everything above shares the transaction, so a claim never exists without the
rows it claims, and a rejection never leaves a claim behind for the redelivery to
skip.

**One migration was needed, and it was not the one the task expected.**
`catalog.processed_events` already exists (`db/006-order-created-consumer.sql`) and
`'import'` was already a legal `stock_movements.reason` (see `001`'s CHECK), so the
plan concluded "no migration for `cat-008`". That conclusion missed a third
constraint: `db/008-product-import-source.sql` widens `products_source_check` so a
new row can be stamped `source = 'import'`. Writing `'local'` instead would make a
feed row indistinguishable from one an admin typed in, and there would be no way
to answer "what did the last import touch?". It is the only schema change in the
route, and `create-product.dto.ts` deliberately keeps its own list without
`'import'` — an admin creating a product over HTTP cannot claim the importer's
provenance.

---

## 5. The stock rule (the money rule)

`catalog.products.stock` and `catalog.product_variants.stock` are **on hand
already net of holds**: `StockReservationsRepository.reserve` decrements them the
moment a hold is taken and writes a `sale` movement. A feed, though, reports
**physical** stock — the units on the shelf, including the ones a shopper is
currently holding. So an imported figure is not written as-is:

```text
onHand = max(0, imported − openReserved)
```

- `openReserved` is the sum of `quantity` over items in every reservation with
  `status = 'held'` for that product (and that variant), **including holds past
  their expiry that the sweeper has not reached**. Those units are still
  deducted from `stock` and are about to be given back; subtracting them now is
  what stops the sweep double-counting them later.
- Only when the payload **carries** `stock`. "The feed did not say" must never
  mean "set it to zero", so an absent figure writes nothing and leaves the
  column alone (`COALESCE`).
- `imported < openReserved` clamps to `0` and logs a warning with both numbers.
  A feed that reports fewer units than live holds is wrong, but refusing the
  import would leave the product unpriced and unbuyable.
- **Exactly one `catalog.stock_movements` row per stated figure**, with
  `reason = 'import'` and `qty_after = onHand` — written even when `qty_change`
  is `0`, because what it records is "the feed asserted this number". A
  redelivery cannot add a second one: the claim dedupes the event.

Worked example: 2 units reserved, a `product.imported` record that states
`stock: 10` ⇒ `stock = 8`, one movement row with `qty_change = 8` (`0` → `8`).
Replay the same event id ⇒ no write at all.

---

## 6. Dead letters — `product.imported.dlq` / `order.created.dlq`

Every topic has a `.dlq` twin, and the `reason` is part of the operational
surface: it is what makes the DLQ queryable, so the strings are fixed.

| Reason | Meaning | Replayable? |
|---|---|---|
| `invalid-json` | Body is not JSON (`rawValue` kept on the DLQ record) | after a producer fix |
| `invalid-envelope` | Envelope failed validation (`id`, `producer`, `timestamp`, `payload`) | after a producer fix |
| `invalid-payload` | Payload failed the topic's schema, or a price is not a number | after a producer fix |
| `unresolved-reference` | `categoryId` / `brandId` names a row that does not exist | yes, after the row exists |
| `sku-conflict` | `sku` is held by a different product id | yes, after a human resolves |
| `slug-conflict` | `slug` is held by a different product id | yes, after a human resolves |
| `variant-sku-conflict` | Variant `sku` belongs to another product | yes, after a human resolves |
| `reservation-closed` | `order.created` names a reservation that is already closed | no — informational |
| `reservation-mismatch` | `order.created` does not match the reservation on record | no — informational |
| `transient-exhausted` | Infrastructure error survived the 5-attempt ladder | yes, once the dependency recovers |

A reservation that does not exist **yet** is deliberately *not* in that list: cat-007
dead-lettered it as `reservation-missing`, and `cat-008` dropped that mapping so it
retries and exhausts as `transient-exhausted` instead. A hold whose transaction has not
committed when the event arrives is worth waiting for — dead-lettering it immediately
would reject the normal race between `order.created` and the reservation's own commit.

All four import reasons are *deterministic*: redelivering the same record cannot
change the answer, which is why they are thrown (rolling the claim back) and
translated into an immediate dead letter rather than retried.

**One case does not commit.** If the DLQ write itself fails, the handler throws
`KafkaConsumerStalledError`, the run loop stops and the offset stays
uncommitted — the group stalls rather than committing past a lost record. The
health endpoint surfaces it; restarting the process resumes from the last commit.

---

## 7. Metrics

`GET /api/v1/catalog/internal/consumer-stats` (header `x-service-key`,
`Cache-Control: no-store`), process-local and reset on boot:

```json
{
  "accepted": 412, "skipped": 0, "committed": 412, "duplicate": 7,
  "ignored": 3, "invalid": 0, "dlq": 0, "commit": 419, "stalled": 0,
  "lag": { "order.created": 0, "product.imported": 0 },
  "totalLag": 0,
  "lastCommit": { "topic": "product.imported", "partition": 0, "offset": "13", "committedAt": "2026-11-01T10:00:12.000Z" },
  "sampledAt": "2026-11-01T10:00:15.000Z"
}
```

- The five counters catalog reported before `cat-008` (`committed`, `duplicate`,
  `ignored`, `invalid`, `dlq`) still mean the same thing; the rest are additive.
- `lag` is `fetchTopicOffsets − fetchOffsets({ groupId: 'catalog-svc' })` per
  topic/partition, sampled every 15 s by a separate admin client on an unref'd
  timer. A `-1` committed offset counts as **never committed**, not as lag, and
  everything but the counters is `null`/empty until the first sample.
- Lag without `lastCommit` cannot tell "behind" from "stopped", which is the
  question this endpoint exists to answer.
- External cross-check: `kafka-consumer-groups.sh --describe --group catalog-svc`
  must show exactly one group per topic and no `catalog-svc-server` group.

---

## 8. Tests

| Level | File | What it pins |
|---|---|---|
| Unit | `src/events/product-imported/product-imported.handler.spec.ts` | every branch of §4: create vs update, the preserved columns, category/brand resolution, each conflict reason, the clamp, no-outbox |
| Unit | `src/events/order-created/order-created.handler.spec.ts` | the unchanged reserve/release behaviour |
| Unit | `src/events/catalog-consumer.controller.spec.ts` | both topics on one controller, one commit protocol, both `translateError` reasons, DLQ-failure → no commit + throw |
| E2E | `test/order-created.e2e-spec.ts` | one hold per order, one order id, replay is a no-op |
| E2E | `test/product-imported.e2e-spec.ts` | product + 2 variants + 3 images + 1 `processed_events` row + **zero** `catalog.outbox` rows; replay writes nothing; dangling `categoryId` → `product.imported.dlq` with `unresolved-reference`; reserve 2 then import 10 ⇒ on-hand 8 and one `import` movement |
| Live (`RUN_KAFKA_E2E=1`) | `test/live-kafka.consumer.e2e-spec.ts` | a real broker: `order.created` commits a hold, `product.imported` with `variants[]` applies and writes no outbox row, and `describeGroups` shows `catalog-svc` `Stable` / `catalog-svc-server` `Dead` |

Commands: `pnpm lint`, `pnpm test`, `pnpm test:e2e`, `npx tsc --noEmit`,
`pnpm build`; the gated live spec is `9.Testing.md §4.4`.

---

## 9. Deferred and known limits

| Item | State |
|---|---|
| `order.status.updated` (release stock on cancel/refund) | not consumed yet — `cat-010` adds one more `@EventPattern` to this same controller. Two consumers in one group would split the partitions, so it must not be a second strategy |
| Import cannot express a discount window | `effectivePrice` in the payload is ignored; a sale price needs a `catalog.product_discounts` row, which `product.imported` has no field for |
| Variant images | untouched by an import: `imageRefSchema` is a bare string, so there is nowhere to say which variant an image belongs to |
| Variants are not removed by absence | by design (§4.6); withdrawal is a human decision |
| No import metrics beyond the counters | the log line reports created/updated, variant, image and stock-figure counts; there is no per-import success rate anywhere |
| `catalog.outbox` rows are not auto-replayed | `failed` rows are alerted and replayed by hand (`10.Observability.md §4`) |
