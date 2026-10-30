# Cart Service — Backend (cart-svc :4030)

> What this file is: the plain-language build checklist for guest/user carts,
> wishlists, guest-to-account merge, and the cart behavior settings document.
> Status: Active | Version 1.1 | Date: 2026-10-27
> Parent: `0.Project-Overview.md` §14 · `1.Architecture.md` §5/§9 ·
> `3.Database-Schema.md` §3.3
> Referenced by: `4.API-Design.md` §3.3/§4.12/§4.13 · `6.Admin-Panel.md` §3.21 ·
> `5.Features.md` A3.6/A4.6/A6.5 · `services/auth.md` §6

Technical words appear only where the builder needs exact names (tables,
columns, endpoint paths, error codes). Everything else is explained the way
you would explain it to a shop owner.

**Current build status (2026-10-26):** Phase 1 is live — Nest scaffold,
crash-proof Postgres pool, `/health` + `/health/ready`, and
`db/001-cart-schema.sql` (four cart tables, seven indexes, two triggers).
Cart CRUD, settings, merge, wishlist, and hardening are specified here and
tracked as `ca-002`–`ca-006` in `state-for-agents/tasks.json`.

---

## 1. The big picture

```
Shopper / admin browser
        │
        ▼
Nginx gateway  ── strips forged x-user-id / x-roles / service keys
        │         verifies the JWT and writes trusted identity headers
        ▼
cart-svc :4030  ── owns cart + wishlist + cart.settings
        │         re-verifies JWT + role for wishlist/admin routes
        │
        ├── Postgres `cart` schema   (carts, cart_items, wishlists, settings, audit)
        ├── Redis                    (idempotency keys, 24h TTL)
        └── Kafka                    (`cart.updated`, fire-and-forget adapter)
```

- The storefront owns the guest cookie (`x-session-id`) and calls cart-svc
  through the gateway.
- Wishlist and admin settings are role-sensitive: cart-svc verifies the JWT
  itself and enforces `customer` or `admin`. Identity-only cart routes may
  use the gateway's trusted `x-user-id` on the private path.
- cart-svc never reads `catalog` tables. Product name, slug, image, variant
  label, and unit price are **snapshots** taken when the line is added.
- `cart.updated` is published **after commit** and never awaited in the
  response path.
- Cart behavior settings are **runtime data**. Saving them is a database
  write, not a build or redeploy.

### Why cart-svc owns the merge policy

The merge policy decides what happens to the shopper's goods at sign-in. It
belongs to the service that owns both carts, not to the CMS theme document.
The CMS may render the admin screen later, but the policy, validation,
versioning, and audit live here.

Rejected alternative: put `guestMergeStrategy` in `cms_settings` — wrong
ownership, cross-service read on every login, and CMS downtime would change
cart behavior.

---

## 2. Identity and ownership

| Caller | Identity | Rule |
|---|---|---|
| Logged-in shopper | verified `Authorization: Bearer` JWT | `user_id = JWT.sub`; gateway may also set `x-user-id` on the private network |
| Guest | `x-session-id` cookie | one active cart per session; never accept a body `session_id` |
| Wishlist | verified JWT + `customer` role | own wishlist only; no guest wishlist; cart-svc verifies the JWT itself |
| Admin settings | verified JWT + `admin` role | cart-svc verifies the JWT itself; `x-roles` alone is never enough |
| Service-to-service | `x-service-key` (v1) | private network only; certificates later |

- The gateway deletes client-supplied `x-user-id`, `x-roles`, and service
  keys before forwarding. cart-svc trusts those headers only on the private
  path for identity-only routes.
- Role-sensitive routes do not rely on gateway trust. Wishlist verifies the
  JWT signature, expiry, issuer/audience (`iss: ecom-auth`,
  `aud: ecom-api`), and `customer` role locally; admin settings verify
  `admin`. `x-roles` alone is never enough.
- Ownership is enforced in SQL (`user_id = JWT.sub`), not only in a
  controller check. A role is not ownership.
- A guest cart is identified by `session_id`, not by a client-provided
  `user_id`. A logged-in cart is identified by `user_id`, not by a body
  field.
- On merge, the storefront sends the user JWT **and** `x-session-id`; after
  success it clears the guest session cookie.
- Future granular permissions: `cart.write`, `wishlist.write`. Until the
  permission catalogue is seeded, wishlist enforces `customer` and admin
  settings enforce `admin`.

Rejected alternative: trust `x-roles` on role-sensitive routes because the
gateway sets it — a direct service call or a gateway misconfiguration would
become privilege escalation. Defense in depth wins.

---

## 3. Data model

Exact columns and indexes: `3.Database-Schema.md` §3.3. The rules that
matter to the service:

### carts

- `status` is `active | abandoned | converted`.
- `one_active_cart_per_user` and `one_active_cart_per_session` are partial
  unique indexes. A concurrent `GET /cart` must retry the insert on `23505`
  and select the winner, not return a 500.
- `last_activity_at` is the TTL input. An idle active cart becomes
  `abandoned` after 24h via a later worker; v1 exposes the timestamp and
  keeps the statuses.
- A merged guest cart becomes `converted`, never deleted. Analytics keeps
  the history.
- A cart must have `user_id` or `session_id` (CHECK constraint).

### cart_items

- One line per `(cart_id, product_id, variant_id)`; the unique index uses
  `NULLS NOT DISTINCT`, so a null variant counts as one line.
- `qty > 0`; `unit_price >= 0`; `product_name` is required.
- Display fields are snapshots. They are refreshed only by a future
  `product.updated` consumer; reads never join the catalog schema.
- `product_slug` mirrors `catalog.products.slug` length (280).
- `image_url` is a snapshot, not a media join.

### wishlists / wishlist_items

- One wishlist per user (`user_id` unique).
- One row per `(wishlist_id, product_id)`.
- Product-level by design: no `variant_id`; variant choice happens at
  add-to-cart.
- Add/remove touches `wishlists.updated_at` in the same transaction; it is
  not exposed in the API. The existing trigger covers direct wishlist-row
  updates only.
- No guest session column; guests use the sign-in prompt + pending product
  id flow in §4.8.
- Wishlist mutations do **not** emit `cart.updated`; they are not cart
  changes.

### cart.settings / cart.settings_audit

- `setting_values` JSONB stores **overrides only**; defaults live in the
  code registry.
- `version` increments on every save; the API requires the expected version.
- Audit is append-only, written in the same transaction as the save.
- No secrets. API keys, passwords, and payment credentials belong in a
  secret manager, not this table.

### Totals

`cartTotals` is computed from the cart rows, never from a catalog call:

```json
{ "subtotal": 159.98, "itemCount": 2, "lineCount": 1 }
```

- `subtotal = sum(qty * unit_price)`.
- `itemCount = sum(qty)`.
- `lineCount = number of cart_items rows`.
- Currency is a store-level setting later; do not invent a per-cart currency
  column in v1.

---

## 4. Cart flows

All endpoints are under `/api/v1/cart`. Cart mutations require
`x-idempotency-key`; admin settings use `version`; wishlist uses the unique
`(wishlist_id, product_id)` constraint instead.

### 4.1 Get / ensure the active cart

`GET /cart` with a user JWT or a guest session:

1. Resolve identity (user or session). Neither → `401`.
2. Select the active cart by the partial unique index.
3. If none, insert one; on `23505`, select the existing winner.
4. Load items and compute totals.
5. Return `{cart, items[], totals}`.

`GET` is safe to retry and does not emit an event.

### 4.2 Add an item

`POST /cart/items` body `{productId, variantId?, qty}`:

1. Validate `qty > 0` (integer).
2. Ask the `CatalogClient` adapter for the product/variant snapshot. In v1
   the adapter is a local fixture because `catalog-svc` is absent; production
   swaps in the HTTP client.
3. Product missing/inactive → `422 CART_PRODUCT_UNAVAILABLE`.
4. Ensure the active cart.
5. Insert or update the matching line:
   - existing line: `qty = qty + requested`;
   - new line: copy name/slug/image/variant label/unit price from the
     catalog snapshot.
6. Commit, recompute totals, return `201 {item, cartTotals}`.
7. Publish one `cart.updated` after commit.

Stock caps are a catalog responsibility; cart-svc stores the requested
quantity and lets checkout revalidate. If a future catalog stock field is
available, the add path may clamp and return a warning — do not silently
reduce quantity without telling the shopper.

### 4.3 Update quantity

`PATCH /cart/items/:id` body `{qty}`:

- `qty > 0`; `qty = 0` is a removal, not an update (use DELETE).
- Ownership check: the item must belong to the caller's active cart; a
  different cart's item → `404 CART_ITEM_NOT_FOUND` (never reveal another
  shopper's cart).
- Update, recompute, return `{item, cartTotals}`, one event.

### 4.4 Remove one item / batch remove / clear

- `DELETE /cart/items/:id` → `204`, one event.
- `DELETE /cart/items` body `{ids[]}` → `204`, one event for the batch.
- `DELETE /cart` → `204`, one event.

Ownership is checked before any delete. A missing id in a batch is ignored
for idempotent retries; a completely foreign id set returns `404`.

### 4.5 Idempotency

- `x-idempotency-key` is required on every cart mutation and on merge.
- Redis stores `key → response` for 24h. A replay returns the stored
  response; a different body under the same key → `409
  IDEMPOTENCY_CONFLICT`.
- If Redis is unavailable, keyed mutations fail with `503
  SERVICE_UNAVAILABLE` rather than applying twice. Reads still work.
- `POST /cart/merge` is naturally idempotent because the guest cart is
  consumed; the key still gives exact response replay.
- Admin settings writes do not use an idempotency key; `version` is the
  concurrency guard.

Rejected alternative: best-effort idempotency that silently applies twice
when Redis is down — a double-add is worse than a short 503.

### 4.6 Events

- Exactly one `cart.updated` per successful mutation, after commit.
- Payload: cart id, user id or session id, status, items, totals, updated
  timestamp.
- Publish is fire-and-forget; a broker failure is logged, never returned to
  the shopper.
- Merge emits one event for the resulting cart; the converted guest cart is
  visible in the database/audit trail, not as a second event.

### 4.7 Catalog adapter

`CatalogClient` is a port with two adapters:

- `FixtureCatalogClient` for local tests (no catalog-svc).
- `HttpCatalogClient` for production (`catalog-svc:4020`).

The cart service stores snapshots and never imports catalog code or queries
the catalog schema. This keeps the repo independent and makes the future
service swap a wiring change.

### 4.8 Wishlist

Wishlist is a product-level “save for later” list for signed-in customers.
It is not a cart and never emits `cart.updated`.

- `GET /wishlist` → `200 {items[]}`; an empty list is valid when the user
  has no wishlist row, and `GET` does not create one. Each item is
  `{id, productId, addedAt}`. No product snapshot is stored; the storefront
  hydrates name/price/image from catalog by `productId`.
- `POST /wishlist/items` body `{productId}` → `201 {item}`; creates the
  wishlist row lazily. The unique
  `(wishlist_id, product_id)` makes the add idempotent: a duplicate returns
  the existing item with the same `id` and `addedAt`.
- `DELETE /wishlist/items/:id` → `204`. A missing or foreign item returns
  `404 WISHLIST_ITEM_NOT_FOUND`.
- Auth: verified JWT + `customer`; no server-side guest wishlist. A guest
  click prompts sign-in. The storefront preserves the pending `productId`
  through the auth redirect (`?next=` or a short-lived cookie; never
  `localStorage`) and calls `POST /wishlist/items` after login. Duplicates
  are a no-op.
- Product-based, not variant-based: `variant_id` is deliberately absent;
  the shopper chooses a variant when adding to cart.
- One wishlist per user (`user_id` unique). Add/remove touches
  `wishlists.updated_at` in the same transaction; it is not exposed in the
  API. The existing trigger covers direct wishlist-row updates only.
- No `x-idempotency-key`; uniqueness is the idempotency mechanism.

---

### 4.9 Internal conversion (Phase-0 bridge)

`POST /api/v1/cart/internal/carts/:userId/convert` — service-to-service only,
guarded by `x-service-key` (`401 SERVICE_KEY_INVALID` otherwise).

- One statement: `UPDATE cart.carts SET status='converted', last_activity_at=now()
  WHERE user_id=$1 AND status='active' RETURNING …`. The partial unique index
  `one_active_cart_per_user` guarantees at most one row, so no transaction and no
  `FOR UPDATE`.
- `200 {cartId, convertedAt}` when a cart was converted, `204` when the user has
  no active cart — so a replay is a silent no-op — and `400 VALIDATION_FAILED`
  for a non-uuid user id.
- Items are **not** deleted: `converted` is history for analytics and support.
- One `cart.updated` with `status: 'converted'` is published after the update
  (no-op adapter until ca-008).
- `INTERNAL_SERVICE_KEY` is mandatory when `NODE_ENV=production`; the app refuses
  to boot without it, so the development fallback cannot reach a deployment.
- Why it exists: checkout confirms the order before any `order.created` consumer
  exists (ca-009). order-svc calls this route fire-and-forget; a failure costs an
  abandoned-cart email, never the order. The route is removed in ca-009.

## 5. Settings subsystem

### 5.1 Why a registry, not a column per setting

The first setting is `guestMergeStrategy`, but the next ones may be
`cart.maxLines`, `cart.reservationMinutes`, or a future checkout hint.
Adding a database column for each one would require DDL for every product
decision. Instead:

- `cart.settings.setting_values` stores a JSONB **override document**.
- `src/settings/settings.registry.ts` is the single source of truth for
  keys, types, defaults, validation, admin labels, UI control, visibility,
  and permission.
- The API resolves `defaults + overrides`; a missing key means "inherit the
  default".

Adding a setting later = one registry entry + tests + a code deploy. **No
database migration, no seed row, no new table.**

Rejected alternatives:

- One typed column per setting — strong DB checks, but DDL per setting and a
  schema deploy every time.
- Arbitrary admin-defined keys — flexible, but no validation, no safe UI,
  and a much larger attack surface.
- A separate settings service now — premature for one service; extract the
  pattern if a second service needs it.

### 5.2 Registry entry

Each setting is declared in one place:

```ts
guestMergeStrategy: {
  key: 'guestMergeStrategy',
  group: 'guestCart',
  label: 'Guest-to-account cart behavior',
  description: 'What happens when a guest signs in with items in both carts.',
  schema: z.enum(['merge', 'guest_wins', 'user_wins']),
  defaultValue: 'merge',
  control: 'select',
  options: [
    { value: 'merge', label: 'Merge carts' },
    { value: 'guest_wins', label: 'Guest cart wins' },
    { value: 'user_wins', label: 'Account cart wins' },
  ],
  visibility: 'admin',       // admin | public | secret
  permission: 'cart.write',  // future granular permission
}
```

- The registry is pure TypeScript: no Nest, no SQL, no React.
- `visibility: 'admin'` is returned only by the admin API.
- `visibility: 'public'` may be projected by a future safe read endpoint;
  there is no public settings document.
- `visibility: 'secret'` is read from a secret manager and returned only as
  configured/not-configured. It is never stored in `cart.settings`.

### 5.3 Storage and resolution

- One row per scope; v1 `scope = 'global'`.
- `setting_values` holds overrides; `version` starts at 0.
- Resolution: `{ ...registryDefaults, ...storedOverrides }`.
- Unknown keys are rejected before SQL; a stored key that was removed from
  the registry is ignored by the resolver and reported in logs.
- `null` is not a valid setting value. Reset deletes the key from the
  override document; it never writes `null`.
- A save updates the document and inserts one audit row in the same
  transaction. If either fails, both roll back.
- `updated_at` is kept by `trg_cart_settings_updated_at` (same
  `cart.set_updated_at()` function).

### 5.4 Admin API

`GET /api/v1/cart/settings` (admin only) returns:

```json
{
  "scope": "global",
  "version": 4,
  "values": { "guestMergeStrategy": "merge" },
  "overrides": {},
  "definitions": [
    {
      "key": "guestMergeStrategy",
      "group": "guestCart",
      "label": "Guest-to-account cart behavior",
      "type": "select",
      "options": ["merge", "guest_wins", "user_wins"],
      "defaultValue": "merge",
      "visibility": "admin"
    }
  ],
  "updatedAt": "2026-10-26T10:00:00Z",
  "updatedBy": "uuid"
}
```

`PATCH /api/v1/cart/settings` (admin only):

```json
{ "version": 4, "values": { "guestMergeStrategy": "guest_wins" } }
```

Reset:

```json
{ "version": 4, "reset": ["guestMergeStrategy"] }
```

Rules:

- `version` is required; stale version → `409 SETTINGS_VERSION_CONFLICT`
  with the current version in `details`.
- Unknown key → `400 UNKNOWN_SETTING`; invalid value → `400
  INVALID_SETTING_VALUE`; no partial update.
- `values` is shallow-merged; `reset` deletes keys in the same transaction.
- `Cache-Control: no-store`; `Vary: Authorization`.
- Response mirrors the GET without `definitions`.
- `GET /api/v1/cart/settings/audit` is an optional admin-only feed
  (`?cursor=&limit=`) added in the hardening phase.

### 5.5 Security of the settings route

- Verified JWT + `admin` role, checked in cart-svc. Gateway headers alone
  are not enough.
- No public settings endpoint. The storefront never receives `updatedBy`,
  `definitions`, overrides, or audit.
- The merge policy is not a secret; if you want it hidden from customers,
  omit it from merge responses. The resulting cart is enough.
- Rate limit at Nginx: 5 req/s per IP (writes 2/s); CORS allowlist for the
  admin origin; body limit (16 KB); no wildcard credentials.
- Input allowlist: registry keys only; reject `__proto__`, `constructor`,
  and `prototype`; parameterized SQL; no raw JSON SQL interpolation.
- Output projection: no secrets, no actor email, no audit in public
  responses.
- Audit is append-only; the app DB role gets `INSERT` + `SELECT`, not
  `UPDATE`/`DELETE`.
- Logs record key/version/request id, not full values; redact
  `Authorization` and cookies.

### 5.6 Build, deploy, and cache behavior

- An admin save is a database write. **No build, no redeploy, no restart.**
- The admin app fetches settings at runtime after login; the values are not
  baked into its build or `NEXT_PUBLIC_*`.
- A cart-svc deploy does not reset settings. `002-cart-settings.sql` uses
  `INSERT ... ON CONFLICT DO NOTHING` and never truncates.
- The storefront does not read settings; it only calls cart endpoints. No
  SSG rebuild is needed.
- Rollback is safe: old code ignores unknown JSONB keys; the data stays.
- v1 has no cache. If merge traffic later justifies one, use
  `cart:settings:{scope}:v{version}` so a version bump invalidates it; do not
  add a cache without that key.

### 5.7 Adding a future setting

1. Add one registry entry (key, group, label, type, Zod schema, default,
   control, visibility, permission).
2. Add a unit test for default/validation and, if it changes behavior, a
   consumer test.
3. Deploy cart-svc code.
4. The admin `GET /settings` automatically includes the definition; a
   generic admin screen renders the new control.
5. No SQL migration, no seed row.
6. If secret: wire the secret manager; never store the value in
   `cart.settings`. If per-scope: add a scope row and registry rule.
7. To retire a setting: stop exposing it, remove the consumer, keep stored
   values until cleanup, then delete in a later migration. Never repurpose a
   key.

### 5.8 Deferred policies

`ask_customer` is deliberately not in v1. It needs a preview endpoint, a
storefront modal, and a choice token. Adding the enum value without that
flow would create a policy the UI cannot honor. The three v1 values are
complete.

---

## 6. Guest-to-account merge

Trigger: the storefront calls `POST /api/v1/cart/merge` after sign-in with
the user JWT, the guest `x-session-id`, and `x-idempotency-key`.

### 6.1 Policies

| Policy | Both sides have items | Only one side has items |
|---|---|---|
| `merge` (default) | Keep the user cart; matching `(product_id, variant_id)` lines sum quantities; guest-only lines append; guest cart `converted`. | If only guest: adopt the guest cart as the user cart. If only user: keep it. |
| `guest_wins` | Guest cart becomes the user's active cart (`user_id` set, `session_id` null); old user cart `converted`. | Adopt guest if it has items; otherwise keep user. |
| `user_wins` | Keep user cart; guest cart `converted`. | If user cart is empty, adopt guest rather than discard the only items; otherwise keep user. |

### 6.2 Algorithm

1. Resolve the user from the verified JWT; require `x-session-id`.
2. In one transaction, lock the active user cart and active guest cart
   `FOR UPDATE` in deterministic id order (avoid deadlocks).
3. If there is no active guest cart, return the user cart (`200`); the retry
   is a no-op. No event.
4. Apply the selected policy.
5. Ensure the resulting cart is the single active cart for the user; mark
   the losing cart `converted`.
6. Update `last_activity_at`; commit.
7. Publish one `cart.updated` after commit.

### 6.3 Edge rules

- **Never lose the only non-empty cart.** This overrides a literal
  `user_wins`: if the user cart is empty, the guest cart is adopted.
- Matching lines use the unique `(cart_id, product_id, variant_id)` key with
  `NULLS NOT DISTINCT`; a null variant matches a null variant.
- Existing user lines keep the user's price/name snapshot; guest-only lines
  keep the guest snapshot. Do not re-price during merge.
- Both carts empty: keep/create the user cart, mark the guest cart
  `converted`.
- No guest cart: return the user cart; no second event.
- `guest_wins` must convert the old user cart before reassigning the guest
  cart, or the partial unique index will reject two active user carts.
- The guest cart row is never deleted; `converted` preserves history.
- Merge is idempotent: after the first success the guest cart is no longer
  active, so a retry returns the user cart without double-adding.

### 6.4 Event

One `cart.updated` for the resulting cart, after commit. A broker outage is
logged; the merge remains successful. A future `cart.merged` event would be
a contract change, not a v1 addition.

---

## 7. Security

### 7.1 Route matrix

| Route | Access | Rule |
|---|---|---|
| `GET /cart` | JWT or guest session | own cart only |
| `POST/PATCH/DELETE /cart/items*` | JWT or guest session | own active cart only; idempotency key required |
| `DELETE /cart` | JWT or guest session | own cart only |
| `POST /cart/merge` | JWT + guest session | own carts only; idempotency key required |
| `GET/PATCH /cart/settings` | verified JWT + `admin` | no public route; version required on PATCH |
| `GET /cart/settings/audit` | verified JWT + `admin` | optional hardening endpoint |
| `GET /wishlist` | verified JWT + `customer` | own wishlist only; no guest wishlist |
| `POST /wishlist/items` | verified JWT + `customer` | own wishlist only; duplicate add returns the existing item |
| `DELETE /wishlist/items/:id` | verified JWT + `customer` | own wishlist only; missing/foreign → 404 |
| `POST /cart/internal/carts/:userId/convert` | `x-service-key` | service-to-service only; no JWT; 204 on replay; not exposed through Nginx |

Wishlist is the first customer-role route to verify the JWT in cart-svc.
Guests are prompted to sign in; the storefront carries the pending product
id and posts it after login.

### 7.2 Authentication and authorization

- Verify JWT signature, expiry, issuer/audience (`iss: ecom-auth`,
  `aud: ecom-api`), and required role/permission in cart-svc for every
  role-sensitive route. Wishlist requires `customer`; admin settings require
  `admin`. Do not rely on `x-roles` alone.
- `@Roles('customer')` is intentional: an admin-only token gets `403` on
  wishlist. An admin who shops must also hold `customer`; `RolesGuard`
  requires every listed role.
- The gateway strips forged identity headers; cart-svc trusts them only on
  the private path for identity-only routes. Role-sensitive routes
  re-verify and never use `x-roles` as authorization.
- Enforce ownership in SQL (`user_id = JWT.sub`), not only in a controller
  check. A role is not ownership.
- Admin/customer roles now; `cart.write`/`wishlist.write` later. A removed
  role stays valid until the access token expires (15m); document this
  window.
- Direct service calls require `x-service-key` and the private network.
- Never accept `user_id`, `session_id`, `role`, or `updated_by` from a
  request body.

### 7.3 Input/output

- Registry allowlist for settings; Zod validation for values; unknown keys
  rejected.
- DTO validation for cart bodies; `qty` integer > 0; body size limit.
- Ownership checks return `404`, not `403`, for another shopper's item.
- Parameterized SQL only.
- Reject prototype-pollution keys.
- No stack traces, DSNs, or internal ids in error messages.
- Public cart responses contain cart data only; no settings, audit, or actor
  metadata.

### 7.4 Transport and abuse

- TLS at Nginx; cart-svc is not publicly exposed.
- Rate limits: cart settings 5 req/s (writes 2/s); cart reads/writes follow
  the global 30 req/s per route unless a stricter rule is added.
- CORS allowlist for the admin origin; no wildcard with credentials.
- `Cache-Control: no-store` on admin settings; `Vary: Authorization`.
- Structured logs with `x-request-id`; redact tokens/cookies.
- Audit every settings save with actor, version, request id, old/new values.

### 7.5 Secrets and data access

- `JWT_SECRET`, `DATABASE_URL`, and `REDIS_URL` come from env/secret
  manager, never from Git or build args.
- The cart DB role has access only to the `cart` schema; no `auth` or
  `catalog` table reads.
- `cart.settings` is not a secret store. If a future setting is sensitive,
  mark it `visibility: 'secret'` and read it from the secret manager.
- Audit values may contain cart behavior only; never secrets. If a secret
  setting is ever audited, store `[redacted]`, not the value.

### 7.6 Admin app

- The admin app is a separate Next.js repo. Use a BFF/HttpOnly session or a
  memory-only Bearer token; never `localStorage`.
- If cookies are used, add CSRF protection and `SameSite=Strict`.
- The settings screen is gated by the server; hiding the sidebar item is not
  security.
- CSP; no settings values in the build; fetch after authentication.

---

## 8. Errors

All errors use the shared envelope (`4.API-Design.md` §1.5). Cart-specific
codes:

| Status | Code | When |
|---|---|---|
| 400 | `VALIDATION_FAILED` | bad body/query, `qty <= 0` |
| 401 | `UNAUTHENTICATED` | no/invalid JWT; guest session is valid only for cart routes |
| 403 | `FORBIDDEN` | valid token without `customer` on wishlist, or customer on an admin route |
| 404 | `CART_ITEM_NOT_FOUND` | item not in the caller's active cart |
| 404 | `WISHLIST_ITEM_NOT_FOUND` | item not in the caller's wishlist |
| 409 | `IDEMPOTENCY_CONFLICT` | same key, different body |
| 409 | `SETTINGS_VERSION_CONFLICT` | stale settings `version` |
| 400 | `UNKNOWN_SETTING` | key not in the registry |
| 400 | `INVALID_SETTING_VALUE` | value fails the registry schema |
| 422 | `CART_PRODUCT_UNAVAILABLE` | catalog snapshot missing/inactive |
| 503 | `SERVICE_UNAVAILABLE` | Redis required for idempotency is down |
| 500 | `INTERNAL_ERROR` | unexpected; no internals leaked |

---

## 9. Build and deployment behavior

### Admin saves a setting

1. Admin app sends `PATCH /cart/settings` with `version` and values.
2. cart-svc verifies JWT + `admin`.
3. Registry validates keys/values.
4. Transaction: `UPDATE ... WHERE scope='global' AND version=$expected`,
   insert audit, commit.
5. Response returns the new version.
6. The next merge reads the new value from Postgres.

**No build, no redeploy, no restart.** Settings are runtime data.

### Admin app rebuild/deploy

- Build contains code only, not settings values.
- The page fetches `GET /cart/settings` after login.
- Rebuilding the admin app does not reset settings.
- Do not use `NEXT_PUBLIC_*` for admin secrets or values.

### cart-svc rebuild/deploy

- Schema scripts are additive and idempotent.
- `001-cart-schema.sql` recreates the four live tables; `002` adds settings
  and audit. The settings seed uses `ON CONFLICT DO NOTHING`.
- A deploy or schema re-run preserves admin values.
- Old code ignores unknown JSONB keys, so rollback is safe.
- No migration runner in v1; apply the numbered SQL manually in order.
- No `DROP`, `TRUNCATE`, or destructive seed in deploy scripts.

### Storefront build

- The storefront does not read cart settings.
- cart-svc reads the policy at merge time; the storefront only calls
  `POST /cart/merge`.
- Do not bake the policy into a static build. If a public setting is ever
  needed, fetch it at runtime or revalidate; never a build-time constant.

### Git push / CI

- Settings are not committed to Git. Admin saves are database records, not
  code changes.
- Admin users must not have repository write access or deploy credentials.
- CI builds code and runs tests; it does not inject production settings.
- Schema application is a separate controlled step with a restricted DB
  role and a backup.

---

## 10. Tests

### Unit

- Settings registry defaults, override merge, reset, unknown key, invalid
  value, version conflict, audit payload, prototype-pollution rejection.
- Totals (`subtotal`, `itemCount`, `lineCount`) and snapshot mapping.
- Merge policy selection and edge rules (only guest, only user, both empty,
  null variant, matching line, guest-wins reassignment).
- Idempotency replay/conflict logic.
- Wishlist: duplicate add returns the existing item; foreign/missing delete;
  product-level uniqueness; `updated_at` touch.

### E2E / contract

- Guest cart persists across requests via `x-session-id`; one active cart
  per session under concurrent create.
- Add/update/remove/clear; ownership returns 404; totals match rows.
- Every mutation emits exactly one `cart.updated` after commit.
- Merge: all three policies, never-lose-only-cart, no duplicate lines,
  guest cart `converted`, old user cart `converted` on guest-wins, one event,
  retry is a no-op.
- Settings: admin GET/PATCH, 401/403, unknown key, invalid value, reset,
  stale version 409, audit row, `no-store`, no public route.
- Wishlist: customer 200; admin-only/no-role 403; guest 401; empty list;
  add; duplicate 201 same item and one row; product-level uniqueness across
  variants; foreign/missing delete 404; remove 204; no `cart.updated`; no
  snapshot; `updated_at` touched.
- Header spoofing: `x-user-id`/`x-roles` without a valid JWT → 401/403;
  role-sensitive routes re-verify the JWT.
- Idempotency: same key returns the stored response; different body → 409;
  Redis down → 503 for mutations.
- Schema: six tables, indexes, triggers, seed idempotency; re-running
  `002` preserves an existing settings document.

### Style/quality gates

- `pnpm test`, `pnpm test:e2e`, `tsc --noEmit`, `oxlint`, `nest build`.
- No secrets in fixtures or logs.
- P99 cart read/removal targets from `3.Database-Schema.md` §6.

---

## 11. Deferred and known limits

| Item | Why deferred | Unblock |
|---|---|---|
| `catalog-svc` HTTP adapter | repo absent | fixture adapter now; swap wiring later |
| Redis idempotency | container stopped/commented | start `ecom-redis`; readiness includes Redis |
| Kafka publisher | broker absent | no-op `IEventBus` adapter; log event; swap later |
| `@ecom/contracts` DTOs/events | package absent | local DTOs; move when package lands |
| Admin settings screen | `frontend/admin` empty | admin-app phase (not a cart-svc task); API works with a test admin JWT |
| `ask_customer` policy | needs preview + choice UI | later phase; not in the v1 enum |
| Audit read endpoint | write audit now; read later | hardening phase |
| Settings cache | merge traffic is low | versioned cache key later |
| `cart.write` / `wishlist.write` permissions | auth permission catalogue empty | seed permissions + guards later |
| Server-side guest wishlist | needs session-scoped rows, merge, TTL; guests use sign-in prompt + pending product id | separate feature |
| Wishlist catalog validation | catalog-svc absent; current phase validates `productId` shape only | validate/hydrate when catalog adapter lands |
| Cart merge role alignment | `POST /cart/merge` accepts any verified JWT; wishlist requires `customer` | align in a separate auth task |
| Abandonment worker | TTL scan is a separate job | `last_activity_at` is ready |
| Currency | store-level setting later | do not add a cart column |

---

## Appendix — where each fact lives

- Tables, indexes, triggers: `3.Database-Schema.md` §3.3.
- Endpoints, envelopes, idempotency, rate limits: `4.API-Design.md` §1.5–
  1.7, §3.3, §4.7, §4.12, §4.13.
- Admin route and screen: `6.Admin-Panel.md` §2.2, §3.21.
- Shopper acceptance: `5.Features.md` A3.6, A4.6–A4.7, A6.5.
- Auth identity, token delivery, merge hand-off: `services/auth.md` §1–6.
- Test gates: `9.Testing.md` §3.3.
- Tracker: `state-for-agents/tasks.json` (`ca-002`–`ca-006`) and
  `TASKS/todo/`.
