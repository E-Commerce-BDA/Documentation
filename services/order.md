# Order Service — Backend (order-svc :4040)

> What this file is: the plain-language build checklist and architectural specification
> for order placement, idempotent checkout, stock reservation sagas, discount redemption,
> order lifecycle management, transactional outbox dispatching, and refunds.
> Status: Active | Version 1.0 | Date: 2026-10-27
> Parent: `0.Project-Overview.md` · `1.Architecture.md` §5/§9 · `3.Database-Schema.md` §3.4
> Companion Services: `auth-svc` (:4010), `catalog-svc` (:4020), `cart-svc` (:4030)

Technical words appear only where the builder needs exact names (table and column names,
error codes, endpoint paths, headers). Everything else is explained the way you'd explain
it to a shop owner.

---

## 1. The big picture (what talks to what)

Think of order placement like a retail customer standing at a cash register with a conveyor belt:

```
Customer's Browser / BFF          Nginx API Gateway               order-svc (:4040)
(Cart items, coupon, address,      Verifies access token,         Idempotent coordinator,
 payment provider)                 stamps x-user-id & x-roles,    state machine, outbox
        │                         attaches x-request-id                  │
        │                                 │                              │
        │─── POST /checkout ─────────────►│                              │
        │    x-idempotency-key            │─── Forward ─────────────────►│
                                                                         │
                    ┌────────────────────────────────────────────────────┤
                    │ 1. Redis replay cache, then the orders row         │
                    │    (idem:{userId}:checkout:{key})                  │
                    │ 2. Pre-reserve stock via catalog-svc (:4020)       │
                    │ 3. Coupon, discount clamp, price snapshots         │
                    │ 4. TX1: orders(status=pending), items,             │
                    │    history, payments(pending), key + hash          │
                    │ 5. Capture payment (order exists now)              │
                    │ 6. TX2: payments→captured, orders→                 │
                    │    confirmed/paid, history, outbox row             │
                    │ 7. Cache + unlock + best-effort cart    │
                    │    conversion (Phase-0 bridge)          │
                    ▼                                                    ▼
              PostgreSQL :5433                                      Redis :6379
          Schema "order" (8 tables)                         Replay cache & Locks
```

* **Idempotency first**: Double-clicking the "Place Order" button never double-charges the customer or duplicates database records. The key is scoped `idem:{userId}:checkout:{key}`: a short-lived Redis lock (`:lock`, 60 s) blocks the race, the cached confirmation (`idem:…`, 24 h) replays the receipt, and a **partial unique index on `orders (user_id, idempotency_key)`** is the real authority — a crash between `COMMIT` and `REDIS SET` still replays from the order row, and another user's key can never reach this user's order. A Redis outage before the first write is a retryable `503 IDEMPOTENCY_UNAVAILABLE`; after the commit it is only a warning, because the order is already durable.
* **Pending-first payment saga**: The order row is written as `pending` *before* the provider is called, so money is never captured for an order that does not exist. A declined capture closes the attempt (`failed`, hold released, `402 PAYMENT_FAILED`); a failure after a successful capture is refunded through the provider and then closed (`503 PAYMENT_PERSIST_FAILED`); a provider that cannot be reached leaves the order `pending`, so retrying the same key resumes the saga instead of starting a second one.
* **Pre-transaction stock reservation**: `order-svc` reserves stock with `catalog-svc` *before* opening TX1, preventing external HTTP latency from holding open database connections. The hold must precede the order row, because the row is the first durable write and a pending order with no hold could be confirmed against stock that was never reserved. Any failure after the hold releases it with `POST /internal/stock/release { reservationId }`, and a terminal transition (`cancelled`, `failed`) releases it again from the order row — a retry can never inflate stock because no quantities are sent.
* **Transactional outbox guarantee**: The order row and its `order.created` event row are written inside the *exact same* SQL transaction (TX2). The Dual-Write Problem is eliminated: an order cannot exist without its event, and an event cannot exist without its order.
* **Asynchronous relay worker**: A background worker polls pending events from `order.outbox` using partial index `idx_outbox_pending`, publishes them, and marks them `published`.
* **Cart conversion bridge (Phase-0)**: after the confirmation is cached, checkout calls `POST /api/v1/cart/internal/carts/:userId/convert` on cart-svc with `x-service-key` and a 2 s timeout, fire-and-forget. `200 {cartId, convertedAt}` means the active cart became `converted`; `204` means there was nothing to convert, which also makes a retry silent. Any failure is a `warn` in the log and never fails the order — the shopper keeps a `converted` cart or, worst case, an active cart that goes to the abandoned-cart flow. The bridge disappears when cart-svc consumes `order.created` (`ca-009`).

---

## 2. Core Concepts in Plain Words

* **Idempotency Key (`x-idempotency-key`).** A unique ticket number generated by the checkout button. If network hiccups cause the customer's phone to retry the request 3 times, `order-svc` executes the checkout once, caches the result alongside a SHA-256 hash of the payload, and replays the receipt on retries. The hash lives on the order row too, so a retry that arrives after a crash (or after Redis lost the cache) still resolves to the same order; a *different* body under the same key is rejected with `409 IDEMPOTENCY_CONFLICT`.
* **Pending-first payment saga.** The order is first written as a promise (`pending`, payment `pending`), then the money is captured, then the same order is confirmed. Each step owns one compensation: a declined capture closes the attempt and releases the hold, a failure after the capture refunds it through the provider before closing the attempt, and a provider timeout leaves the order `pending` so the customer's retry resumes it (same order id, provider idempotency key = order id) instead of creating a second order.
* **Refunds ledger.** A refund is not a status flip: it is a row in `order.refunds` reserved *before* the provider is called and settled after, so the books can never claim a refund that did not happen. One refund per order (a unique `order_id` is the idempotency gate): replaying a settled refund returns the stored row without calling the provider, a failed one is retried in place with the amount it was reserved for, and only a successful provider answer moves the payment to `refunded`.
* **Saga-lite Stock Compensation.** If the customer's credit card is declined or the database connection drops after stock has been locked in the warehouse, `order-svc` executes an automated compensation call to `catalog-svc` to return the reserved stock to the shelf.
* **Immutable Item Snapshots.** In `order_items`, the shop writes down the exact product name, SKU, and unit price paid at the moment of checkout. If the merchant alters the product price or deletes the product from the catalog next month, past receipts and tax invoices remain legally pristine.
* **Finite State Machine (FSM).** Orders must advance through defined directional steps:
  `pending` &rarr; `confirmed` &rarr; `processing` &rarr; `shipped` &rarr; `delivered` &rarr; `refunded`.
  An admin cannot roll back a `delivered` parcel back to `pending`, and cancelled orders cannot be revived. `pending` is a real state now (not just a default): it means "stock held, money not captured yet".

---

## 3. Endpoints & Route Reference

Global API prefix: `/api/v1`

### 3.1 Checkout & Cart Conversion
| Method | Path | Auth / Guards | Description |
|---|---|---|---|
| `POST` | `/api/v1/checkout` | `JwtAuthGuard` | Idempotent checkout: validates stock, applies discount, captures payment, writes outbox row, returns `201 Created`. |

### 3.2 Coupons & Discounts
| Method | Path | Auth / Guards | Description |
|---|---|---|---|
| `POST` | `/api/v1/discount-codes/validate` | Public / Customer | Validates coupon active window, max uses, min order threshold, and returns calculated discount. |
| `GET` | `/api/v1/discount-codes` | `JwtAuthGuard`, `RolesGuard('admin')` | Admin paginated coupon list. |
| `POST` | `/api/v1/discount-codes` | `JwtAuthGuard`, `RolesGuard('admin')` | Admin create new discount code (percent or fixed). |
| `GET` | `/api/v1/discount-codes/:id` | `JwtAuthGuard`, `RolesGuard('admin')` | Admin retrieve coupon by ID. |
| `PATCH` | `/api/v1/discount-codes/:id` | `JwtAuthGuard`, `RolesGuard('admin')` | Admin update coupon rules. |
| `DELETE` | `/api/v1/discount-codes/:id` | `JwtAuthGuard`, `RolesGuard('admin')` | Admin delete coupon. |

### 3.3 Customer & Admin Order Lifecycle
| Method | Path | Auth / Guards | Description |
|---|---|---|---|
| `GET` | `/api/v1/me/orders` | `JwtAuthGuard` | Customer cursor-paginated order history with snapshot items, status history, and payments. |
| `GET` | `/api/v1/orders/:id` | `JwtAuthGuard` | Retrieve order by ID. Customer can view own order; admin can view any order (`403 Forbidden` on cross-tenant access). |
| `GET` | `/api/v1/orders` | `JwtAuthGuard`, `RolesGuard('admin')` | Admin order management with status, date, and order number filters. |
| `GET` | `/api/v1/orders/:id/status-history` | `JwtAuthGuard`, `RolesGuard('admin')` | Chronological audit timeline of order status transitions. |
| `PATCH` | `/api/v1/orders/:id/status` | `JwtAuthGuard`, `RolesGuard('admin')` | Advances order status according to the Finite State Machine; appends to history and writes outbox event. |
| `POST` | `/api/v1/orders/:id/refund` | `JwtAuthGuard`, `RolesGuard('admin')` | Refunds a delivered order (full or partial up to `grand_total`) through the payment provider: reserves a `refunds` row, calls `processRefund` with the stored `transaction_id`, settles the ledger + payment + order + `order.status.updated` in one transaction, and returns `{order, refund}`. |

### 3.4 Internal Service-to-Service Gateway
| Method | Path | Auth / Guards | Description |
|---|---|---|---|
| `GET` | `/api/v1/internal/orders/:id` | `ServiceKeyGuard` | Internal order lookup requiring `x-service-key` header (bypasses customer JWT). |

### 3.5 Health & Readiness Probes
| Method | Path | Auth / Guards | Description |
|---|---|---|---|
| `GET` | `/health` | Public | Kubernetes / Docker liveness probe (`{ status: 'ok' }`). |
| `GET` | `/health/ready` | Public | Readiness probe testing active PostgreSQL connection pool query and Redis PING (`503` if down). |

---

## 4. Security & Hardening Architecture

1. **Standard Error Envelope.** All non-health errors return a uniform structure:
   ```json
   {
     "error": {
       "code": "VALIDATION_FAILED",
       "message": "Validation failed",
       "details": ["status must be one of: pending, confirmed, ..."]
     },
     "requestId": "3a9e9fb5-a216-4d5d-961d-073ba7c1d671",
     "timestamp": "2026-10-27T15:38:31.000Z"
   }
   ```
2. **Request ID Propagation.** The gateway's `x-request-id` header is echoed in the response header and embedded in the JSON error payload. If missing, a fresh UUIDv4 is assigned.
3. **Cache-Control Header.** All mutating HTTP methods (`POST`, `PATCH`, `PUT`, `DELETE`) receive `Cache-Control: no-store` to prevent intermediary caching of financial mutations.
4. **Parameter Tampering & Prototype Pollution Defense.** Enforced by `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`, stripping and rejecting injected keys (`__proto__`, `constructor`, `isAdmin`).
5. **SQL Injection Immunity.** All database access in `src/orders/`, `src/discounts/`, and `src/outbox/` uses parameterized queries (`$1, $2, ...`) and UUID format regex guards before executing SQL.

---

## 5. Database Schema & Tables

PostgreSQL schema `"order"` contains 8 dedicated tables:
* `orders`: core order entity with currency, totals (subtotal, shipping, tax, discount, grand total), JSONB address snapshots, statuses, the stock reservation id, and the idempotency key + payload hash.
  * Partial unique index: `idx_orders_idem` on `(user_id, idempotency_key) WHERE idempotency_key IS NOT NULL` — one key per user, and the loser of a race gets `23505` instead of a second order.
* `order_items`: line item snapshot records with product ID, variant ID, product name, SKU, unit price, quantity, and line total.
* `order_status_history`: immutable chronological log of state changes (`from_status`, `to_status`, `note`, `actor`, `created_at`).
* `payments`: lifecycle payment records (`provider`, `amount`, `status`, `transaction_id`, `paid_at`), moving `pending` &rarr; `captured` &rarr; `refunded` (or `failed`).
* `refunds`: the refund ledger — one row per order (`UNIQUE (order_id)`), carrying `amount`, `status` (`pending`/`succeeded`/`failed`), `provider_reference`, `failure_reason`, `reason`, and `requested_by`.
  * Index: `idx_refunds_order` on `(order_id)`.
* `outbox`: transactional event queue (`event_id`, `aggregate_type`, `aggregate_id`, `event_type`, `payload`, `status`, `attempts`, `published_at`).
  * Partial index: `idx_outbox_pending` on `(created_at) WHERE status = 'pending'`.
* `discount_codes`: coupons with percent/fixed values, date windows (`starts_at`, `ends_at`), max uses, and atomic `uses_count`.
  * Partial index: `idx_discount_codes_valid` on `(ends_at) WHERE is_active = true`.
* `shipments`: fulfillment records with carrier, tracking numbers, and shipment statuses.

---

## 6. Verification & Automated Test Inventory

* **Unit Tests (77 tests across 6 test suites)**:
  * `orders.service.spec.ts` (24 tests): FSM transition rules, terminal state immutability, customer ownership RBAC, stock-hold release on cancellation, and the refund ledger (provider call, replay, in-flight guard, no-captured-payment, provider failure, retry amount).
  * `outbox.service.spec.ts` (3 tests): event polling, concurrency guard, and retry increments.
  * `checkout.service.spec.ts` (25 tests): user-scoped idempotency replay, body-hash conflicts, corrupt cache, Redis fail-closed 503, pending-first saga, capture decline, TX2 failure compensation, resume, and hold release exactly once.
  * `discounts.service.spec.ts` (17 tests): percent/fixed calculations, cart clamping, date windows, and usage thresholds.
  * `health.service.spec.ts` (4 tests): PostgreSQL and Redis ping health checks.
  * `canonical-json.spec.ts` (4 tests): stable key ordering and hashing of equivalent payloads.
* **E2E Integration Tests (77 tests across 6 test suites — 76 pass, 1 skipped)**:
  * `security.e2e-spec.ts` (12 tests): structured error envelope, `x-request-id` tracing, `Cache-Control: no-store`, `ServiceKeyGuard` enforcement, RBAC isolation, prototype pollution rejection, and SQL injection safety.
  * `orders.e2e-spec.ts` (22 tests): customer history lookup, cross-customer forbidden isolation, admin status progression (`confirmed` &rarr; `processing` &rarr; `shipped` &rarr; `delivered`), rollback rejection, status history timeline, and refunds against a ledger (provider called once with the stored transaction, replay, provider failure leaving order and payment untouched, retry on the same row, `409 NO_CAPTURED_PAYMENT`, no `order.refunded` event).
  * `checkout.e2e-spec.ts` (18 tests, 1 skipped): checkout against live PostgreSQL + Redis, cross-user key isolation, DB-authoritative replay after a cache flush, concurrent duplicates, Redis-outage drill, the payment saga (capture after the pending row, decline, TX2 failure refund, resume), and the stock/coupon failure matrix.
  * `discounts.e2e-spec.ts` (14 tests): public coupon validation, admin coupon CRUD, and usage increment verification.
  * `health.e2e-spec.ts` (2 tests): `/health` liveness and `/health/ready` readiness against live DB and Redis.
  * `schema.e2e-spec.ts` (9 tests): 8 PostgreSQL tables, the refund unique constraint, foreign key cascades, `set_updated_at()` triggers, check constraints.
* **Code Quality & Linter**:
  * `oxlint --type-aware src/ test/`: **0 warnings / 0 errors** on 70 files with 111 rules.
  * `nest build`: Clean TypeScript build exiting code `0`.
