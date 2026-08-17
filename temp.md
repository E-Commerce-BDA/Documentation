# temp.md — Database Table Inventory (Working Scratch Doc)

> Temporary working document for discussing the full data model before writing `3.Database-Schema.md`.
> Status: Working | Last Updated: 2026-08-15

---

## A. How We Define the Database

### A.1 Data Placement Rule
| Store | Holds |
|---|---|
| **PostgreSQL (RDS)** | Every record needing ACID + referential integrity: users, orders, inventory, carts, payments, outbox |
| **MongoDB (Atlas M0)** | Flexible/JSON-shaped data where schema varies per record: CMS sections/settings, blogs, analytics events |
| **Redis (EC2)** | Ephemeral/transient data: sessions, cache, rate limits, idempotency keys, compare list |

### A.2 ACID + Normalization Policy
- Each service owns a separate Postgres **schema** (`auth`, `catalog`, `cart`, `order`, `notify`, `import`) → clean ownership boundaries, no cross-service table sharing.
- **1NF:** atomic columns, no repeating groups (variants/images/attributes split into child tables).
- **2NF:** no partial key dependencies (child tables reference `product_id`/`order_id`, never inherit parent-only fields).
- **3NF:** no transitive dependencies (prices stored in dedicated price columns, not derived from other fields).
- **Deliberate denormalization exception:** `order_items` snapshots product name/SKU/price at purchase time — intentional so order history survives later catalog changes (audit requirement). Kept out of 3NF by design.
- **ACID enforcement:** foreign keys + transactions + **transactional outbox** (order row + outbox row committed in the same transaction → no order without its event).

---

## B. PostgreSQL Tables Inventory (by owning service)

### B.1 `auth` schema — auth-svc
| Table | Purpose | Short description |
|---|---|---|
| `users` | Accounts | id, email, password_hash, first/last name, phone, avatar, status, timestamps |
| `addresses` | Address book | user_id, type (shipping/billing), line1/2, city, state, postal_code, country, is_default |
| `refresh_tokens` | Token rotation | user_id, token_hash, expires_at, revoked_at, created_at |
| `roles` | RBAC — role defs | id, name, slug (admin/customer), description |
| `permissions` | RBAC — permission defs | id, name, slug (product.create, order.read...), description |
| `role_permissions` | RBAC — join | role_id ↔ permission_id |
| `user_roles` | RBAC — join (multi-role) | user_id ↔ role_id |

### B.2 `catalog` schema — catalog-svc
| Table | Purpose | Short description |
|---|---|---|
| `categories` | Category tree | id, parent_id (self-FK for tree), name, slug, image, is_active, sort_order, navbar/megamenu flags, JSONB settings |
| `brands` | Brand directory | name, slug, logo, description, is_active |
| `products` | Core catalog | sku, name, slug, description, category_id, brand_id, price, compare_at_price, stock (running balance), status, tags, attributes JSONB, photo_settings JSONB, source (local/shopify/bigcommerce/odoo), external_id |
| `product_variants` | Variant rows (no inline options) | product_id, sku, price, stock, image, is_active |
| `product_images` | Media gallery | product_id, url (S3), alt, sort_order, is_primary |
| `product_options` | Option definitions (stored once) | product_id, name (Size/Color), position |
| `product_option_values` | Option values (stored once) | option_id, value, position |
| `product_variant_option_values` | Variant↔option↔value junction | variant_id, option_id, option_value_id |
| `product_attributes` | Compare engine — defs | attribute name, slug, type |
| `product_attribute_values` | Compare engine — values | product_id, attribute_id, value |
| `stock_movements` | Stock ledger (audit) | product_id/variant_id, qty_change, reason (sale, admin_adjustment, import...), order_id, created_at. `products.stock` = running balance, updated in the SAME transaction as the movement insert (balance + ledger pattern) |
| `product_discounts` | Scheduled product discounts | product_id, discount_type (percent/fixed), value, starts_at, ends_at, is_active. Supports multiple discounts over time + automation-ready |
| `reviews` **[optional]** | Ratings | product_id, user_id, rating, title, body, is_approved |

### B.3 `cart` schema — cart-svc
| Table | Purpose | Short description |
|---|---|---|
| `carts` | Cart | user_id (nullable) or session_id, status (active/abandoned/converted), last_activity_at, timestamps |
| `cart_items` | Line items | cart_id, product_id, variant_id, qty, unit_price snapshot, added_at |
| `wishlists` | Wishlist | user_id |
| `wishlist_items` | Wishlist entries | wishlist_id, product_id, added_at |

> **Compare products:** NOT a table — stored in Redis (`compare:{sessionId}`) only. Ephemeral by design, does not survive sessions. Decided 2026-08-15.

### B.4 `order` schema — order-svc
| Table | Purpose | Short description |
|---|---|---|
| `orders` | Order header | user_id, order_number, status, subtotal/shipping/tax/discount/grand_total, currency, address snapshots JSONB, payment_status, timestamps |
| `order_items` | Order lines (snapshot) | order_id, product/variant id, name/SKU/price snapshots, qty, line_total |
| `order_status_history` | State audit | order_id, from, to, note, actor, created_at |
| `payments` | Payment records | order_id, provider, amount, status, transaction_id, paid_at (mock v1) |
| `outbox` | Event guarantee | aggregate_type/id, event_type, payload JSONB, status, attempts, published_at |
| `shipments` **[optional]** | Fulfillment | order_id, carrier, tracking_number, status, shipped_at |
| `discount_codes` | Coupons/promotions | code, type, amount, min_order, starts_at, ends_at, usage_limit. Expiry presets (24h / 2 days / 5 days / 1 week) are UI shortcuts that set `ends_at` — no schema change |

### B.5 `notify` schema — notify-svc
| Table | Purpose | Short description |
|---|---|---|
| `email_logs` | Delivery audit | recipient, subject, template, status, sent_at, error |
| `notification_templates` **[optional]** | Template store | key, subject, body, variables JSONB |

### B.6 `import` schema — import-svc
| Table | Purpose | Short description |
|---|---|---|
| `import_jobs` | Import runs (core) | file ref, source, status, totals, errors JSONB, created_by, created_at |

---

## C. MongoDB Collections (cms-svc + analytics-svc)

| Collection | Owner | Purpose |
|---|---|---|
| `cms_sections` | cms-svc | Homepage/section blocks (hero, banner, featured products, blog teaser, brands) with content + settings JSON |
| `cms_settings` | cms-svc | **Global** theme: colors, border radius, image ratios, blend mode (multiply/normal), typography |
| `navigation_settings` | cms-svc | Navbar/megamenu config (which categories, images on/off, columns, order) |
| `pages` | cms-svc | Static pages (about, contact) with content blocks |
| `blogs` | cms-svc | Blog posts (title, slug, cover, content blocks, status) |
| `blog_categories` | cms-svc | Blog taxonomy |
| `media` | cms-svc | S3 asset registry (url, alt, dimensions, usage) |
| `page_views` | analytics-svc | Raw page-view + heartbeat events |
| `sessions` | analytics-svc | Session timeline (start/end, pages visited, exit page) |
| `cart_events` | analytics-svc | Cart activity stream (from cart.updated) |
| `abandoned_carts` | analytics-svc | Detected abandoned carts + status (reminded/converted) |
| `daily_stats` | analytics-svc | Aggregated daily metrics (views, exits, conversions) |

---

## D. Redis Keyspaces (ephemeral, not tables)

| Key pattern | Purpose |
|---|---|
| `compare:{sessionId}` | Compare-products list (session-scoped) |
| `sess:{tokenId}` | Session store (sliding TTL) |
| `rate:{ip}` | Rate-limit counters |
| `idem:{eventId}` | Idempotency dedupe set |
| `cat:product:{id}` | Catalog cache-aside |
| `cms:section:{key}` | CMS section cache |
| `cms:settings:global` | Global CMS settings cache |

---

## E. Decision Flags

| Item | Decision |
|---|---|
| Optional/likely-future tables | Included in temp.md, marked `[optional]` (reviews, shipments, notification_templates) |
| RBAC | Full tables: roles, permissions, role_permissions, user_roles (multi-role supported) |
| Compare storage | Redis only — no table |
| users.role column | Removed — role resolved via `user_roles` join |
| Product discounts | New `product_discounts` table (decided 2026-08-15) — scheduled, multiple over time, automation-ready |
| Discount coupons | `discount_codes` promoted from optional to **core** (decided 2026-08-15) |
| Admin stock adjustments | Supported via `stock_movements` with reason=`admin_adjustment` |
| Variant model | Normalized junction model (decided 2026-08-16): `product_options` + `product_option_values` + `product_variants` (no JSONB) + `product_variant_option_values`. Every value stored once; combination via joins |
| Stock model | Balance + ledger (decided 2026-08-16): `products.stock` running balance updated in same transaction as `stock_movements` insert |
| Source tracking | `products.source` + `products.external_id` added now (decided 2026-08-16) — idempotent Shopify/BigCommerce/Odoo re-syncs later |
| import_jobs | Promoted from optional to **core** (decided 2026-08-16) — batch status/totals/errors needed by import UI |

---

## F. Admin Feature → Table Mapping

| Admin feature | Table(s) | Notes |
|---|---|---|
| Increase product stock | `products.stock` + `stock_movements` | Audited via reason=`admin_adjustment` |
| Apply product discounts | `product_discounts` | Scheduled; multiple allowed over time; active row drives display price |
| Create discount coupons + expiry presets | `discount_codes` | Presets (24h/2d/5d/1w) just set `ends_at` |
| View all orders | `orders`, `order_items`, `order_status_history` | Read-only listing + filters; endpoints in `4.API-Design.md`, UI in `6.Admin-Panel.md` |

---

## Next Step
After review, this inventory becomes `3.Database-Schema.md` with:
- Full column definitions per table (data types with **reason** per column)
- Indexes with **reason** per index (primary, FK, unique, partial, GIN for JSONB/full-text)
- Postgres/Mongo ownership map
