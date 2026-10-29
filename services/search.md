# Search Service — Backend (search-svc :4090)

> What this file is: the plain-language build checklist and operational guide for the unified search engine:
> typeahead suggest, ranked search, event-driven index synchronization, and backfill pipelines.
> Status: Active | Version 1.0 | Date: 2026-10-28
> Parent: `0.Project-Overview.md` §14 · `1.Architecture.md` §5/§6/§7/§9 · `3.Database-Schema.md` §3.7 · `4.API-Design.md` §3.9
> Referenced by: `search-svc` (:4090), `catalog-svc` (:4010), `cms-svc` (:4050), `storefront`

Technical words appear only where the builder needs exact names (table and column names, error codes, endpoint paths, headers). Everything else is explained the way you'd explain it to a shop owner.

---

## 1. The big picture (what talks to what)

Think of search as the shop's catalog information desk:

```
Storefront shopper           Nginx gateway                   search-svc (:4090)
(searching products,        public rate limiting,           fast reading index,
 blogs, categories)          stamps request id               answers questions
        │                           │                               │
        │   GET /suggest, /search   │                               │
        └──────────────────────────►│──────────────────────────────►│
                                    │                               │
                                    │                     ┌─────────▼─────────┐
                                    │                     │ PostgreSQL        │
                                    │                     │ search_documents  │
                                    │                     │ (FTS + GIN index) │
                                    │                     └─────────┬─────────┘
                                    │                               │
                                    │                     ┌─────────▼─────────┐
                                    │                     │ Redis             │
                                    │                     │ suggest cache     │
                                    │                     └───────────────────┘
                                                                    ▲
                                                                    │
Kafka event spine ──────────────────────────────────────────────────┘
(product.updated, category.updated, blog.updated, product.imported)
```

* **The source services own the truth:** `catalog-svc` owns products/categories; `cms-svc` owns blogs. They write to their own databases and publish domain events to Kafka.
* **`search_documents` is a denormalized read model:** Search owns no primary business entities. It consumes events, flattens them into searchable text, and indexes them in PostgreSQL.
* **PostgreSQL full-text search powers v1:** Using native PostgreSQL `tsvector`, `tsquery`, and GIN indexes. No additional external search daemons (like Elasticsearch/Typesense) are needed for learning scale.
* **Dual Ingestion Architecture:**
  1. **Primary path (real-time):** Kafka consumer group `search-svc` processes events asynchronously as changes happen.
  2. **Internal path (backfill/tests):** `POST /api/v1/search/internal/documents` (guarded by `x-service-key`) allows seeding, disaster recovery backfills, and hermetic integration tests without broker dependencies.
* **Redis accelerates typeahead only:** `GET /suggest` is cached in Redis for 10 minutes. Full `GET /search` results are not cached due to high filter and cursor cardinality. If Redis is down, search continues serving directly from PostgreSQL.

---

## 2. Core Principles & Boundaries

1. **Denormalized, never source-authoritative:**
   If the search database is dropped, the entire index can be rebuilt from Kafka replay or source database backfills without data loss.
2. **Eventual consistency by design:**
   A product or blog update takes milliseconds to appear in search after the event is processed. Eventual consistency is completely acceptable for search; it is not acceptable for checkout.
3. **Idempotent upsert & stale-event guard:**
   Events may arrive out of order or be re-delivered. The indexer enforces idempotency on `(document_type, id)` and drops updates where the incoming `source_updated_at` is older than the stored row.
4. **Resilient degraded modes:**
   - PostgreSQL down: `GET /health/ready` returns `503 Service Unavailable`.
   - Redis down: `GET /health/ready` returns `200 OK` with `redis: "down"`. Typeahead continues via PostgreSQL.
   - Kafka down: `GET /health/ready` returns `200 OK` with `kafka: "down"`. Queries continue to serve existing data; index updates pause until Kafka reconnects.
5. **No PII:**
   Only public catalog and blog content is indexed. Customer information, orders, and credentials never enter `search-svc`.

---

## 3. Data Model

### 3.1 DDL (`db/001-search-schema.sql`)

```sql
CREATE SCHEMA IF NOT EXISTS search;

CREATE TABLE IF NOT EXISTS search.search_documents (
  id varchar(64) PRIMARY KEY,
  document_type varchar(20) NOT NULL
    CHECK (document_type IN ('product', 'category', 'blog')),
  title varchar(255) NOT NULL,
  slug varchar(280) NOT NULL,
  content text NOT NULL,
  image_url varchar(2048),
  price numeric(12,2) CHECK (price >= 0),
  effective_price numeric(12,2) CHECK (effective_price >= 0),
  category_id uuid,
  popularity integer NOT NULL DEFAULT 0,
  status varchar(20) NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'inactive')),
  search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('english', title || ' ' || content)
  ) STORED,
  source_updated_at timestamptz NOT NULL,
  synced_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS search_documents_type_id_key
  ON search.search_documents (document_type, id);

CREATE INDEX IF NOT EXISTS idx_search_documents_vector
  ON search.search_documents USING GIN (search_vector);

CREATE INDEX IF NOT EXISTS idx_search_documents_active
  ON search.search_documents (status) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_search_documents_popularity
  ON search.search_documents (popularity);

CREATE INDEX IF NOT EXISTS idx_search_documents_category
  ON search.search_documents (document_type, category_id)
  WHERE document_type = 'product';
```

### 3.2 Upsert Semantics

```sql
INSERT INTO search.search_documents (
  id, document_type, title, slug, content, image_url,
  price, effective_price, category_id, popularity, status,
  source_updated_at, synced_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, now())
ON CONFLICT (document_type, id) DO UPDATE SET
  title = EXCLUDED.title,
  slug = EXCLUDED.slug,
  content = EXCLUDED.content,
  image_url = EXCLUDED.image_url,
  price = EXCLUDED.price,
  effective_price = EXCLUDED.effective_price,
  category_id = EXCLUDED.category_id,
  popularity = EXCLUDED.popularity,
  status = EXCLUDED.status,
  source_updated_at = EXCLUDED.source_updated_at,
  synced_at = now()
WHERE EXCLUDED.source_updated_at >= search.search_documents.source_updated_at
RETURNING id;
```

---

## 4. API Contracts

Base path: `/api/v1/search`

### 4.1 `GET /api/v1/search/suggest` (Public)

Typeahead endpoint for storefront search bars.

**Query Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `q` | string | Yes | Query prefix (min 2, max 100 characters). |
| `limit` | integer | No | Max items per type (1–10, default: 5). |

**Response `200 OK`:**
```json
{
  "query": "sho",
  "categories": [
    { "id": "uuid", "name": "Shoes", "slug": "shoes", "image": "https://cdn.example.com/shoes.jpg" }
  ],
  "products": [
    {
      "id": "uuid",
      "slug": "running-shoe-x",
      "name": "Running Shoe X",
      "image": "https://cdn.example.com/shoe1.jpg",
      "price": 79.99,
      "effectivePrice": 71.99
    }
  ],
  "blogs": [
    {
      "id": "uuid",
      "slug": "best-running-shoes-2026",
      "title": "Best Running Shoes 2026",
      "cover": "https://cdn.example.com/blog1.jpg"
    }
  ]
}
```

**Cache header:** `Cache-Control: public, max-age=60, stale-while-revalidate=300`

**Errors:**
- `400 QUERY_TOO_SHORT`: `q` missing, empty, or shorter than 2 characters.
- `400 QUERY_INVALID`: `q` longer than 100 characters or containing no searchable letters/digits after punctuation stripping.
- `400 INVALID_FILTER`: `limit` not an integer between 1 and 10, or unexpected query parameters provided.

---

### 4.2 `GET /api/v1/search` (Public)

Ranked search across products, categories, and blogs with facet filtering and cursor pagination.

**Query Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `q` | string | Yes | Search query (min 2, max 100 characters). |
| `type` | enum | No | `product`, `category`, or `blog`. |
| `category` | string | No | Category slug to filter products. |
| `minPrice` | number | No | Minimum price filter (implies product type). |
| `maxPrice` | number | No | Maximum price filter (implies product type). |
| `sort` | enum | No | `relevance` (default), `price.asc`, `price.desc`, `newest`, `popular`. |
| `cursor` | string | No | Opaque base64url cursor for pagination. |
| `limit` | integer | No | Items per page (1–50, default: 24). |

**Response `200 OK`:**
```json
{
  "query": "running shoes",
  "data": [
    {
      "id": "uuid",
      "type": "product",
      "title": "Running Shoe X",
      "slug": "running-shoe-x",
      "image": "https://cdn.example.com/shoe1.jpg",
      "price": 79.99,
      "effectivePrice": 71.99,
      "popularity": 12,
      "updatedAt": "2026-10-28T09:00:00.000Z"
    }
  ],
  "nextCursor": "eyJ2IjoxLCJxIjoiM2YxMG...",
  "totalHits": 42
}
```

**Cache header:** `Cache-Control: public, max-age=30, stale-while-revalidate=30`

---

### 4.3 `POST /api/v1/search/internal/documents` (Internal)

Batch ingestion endpoint for backfill, disaster recovery replay, and hermetic tests. Requires header `x-service-key`.

**Request Body:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "documentType": "product",
      "title": "Running Shoe X",
      "slug": "running-shoe-x",
      "content": "Lightweight road running shoe",
      "imageUrl": "https://cdn.example.com/shoe1.jpg",
      "price": "79.99",
      "effectivePrice": "71.99",
      "categoryId": "cat-uuid",
      "popularity": 12,
      "status": "active",
      "sourceUpdatedAt": "2026-10-28T09:00:00.000Z"
    }
  ]
}
```

**Limits:** Maximum 500 documents per batch; maximum 1 MB payload.

**Response `200 OK`:**
```json
{
  "accepted": 1,
  "skipped": 0,
  "rejected": 0
}
```

---

### 4.4 `GET /api/v1/search/internal/stats` (Internal)

Returns summary statistics for the search index. Requires header `x-service-key`.

**Response `200 OK`:**
```json
{
  "documents": 1234,
  "active": 1200,
  "byType": {
    "product": 1000,
    "category": 100,
    "blog": 100
  },
  "lastSyncedAt": "2026-10-28T09:05:00.000Z"
}
```

---

## 5. Event Ingestion Pipeline (Kafka)

`search-svc` acts as a consumer for four domain events over Kafka:

| Topic | Key | Payload Schema | Ingestion Rule |
|---|---|---|---|
| `product.imported` | `productId` | `ProductImportedPayload` | Upsert as `product`. Inactive if stock 0 or status inactive. |
| `product.updated` | `productId` | `ProductUpdatedPayload` | Upsert as `product`. Updates title, content, price, effectivePrice. |
| `category.updated` | `categoryId` | `CategoryUpdatedPayload` | Upsert as `category`. Status maps from `isActive`. |
| `blog.updated` | `blogId` | `BlogUpdatedPayload` | Upsert as `blog`. If `status == 'draft'`, sets index status to `inactive`. |

### Kafka Consumer Specifications
- **Client library:** `kafkajs`
- **Consumer Group:** `search-svc`
- **Offset management:** Manual commit (`autoCommit: false`). Offset committed only after PostgreSQL upsert transaction succeeds.
- **Retry & DLQ:** 5 attempts with exponential backoff (1s, 2s, 4s, 8s, 16s). If still failing, message is written to `<topic>.dlq` and consumer offset is committed.

---

## 6. Query Processing, Normalization & Cursor Mechanics

### 6.1 Query Normalization (`normalizeQuery`)
1. Trim leading and trailing whitespace.
2. Enforce input string type and initial length bounds (2 to 100 characters).
3. Convert to lowercase.
4. Replace punctuation and symbols (`[^\p{L}\p{N}\s]`) with spaces.
5. Collapse consecutive whitespace into single spaces.
6. Enforce post-sanitization length (reject strings that reduce to empty or < 2 characters with `QUERY_INVALID`).

### 6.2 Prefix Query Builder (`toPrefixTsQuery`)
Transforms `"run shoe"` into `"run:* & shoe:*"`. This allows typeahead prefix matching while avoiding raw user string injection into PostgreSQL's query parser.

### 6.3 Opaque Cursor
Cursors are base64url-encoded JSON envelopes:
```json
{
  "v": 1,
  "q": "sha256-hash-of-normalized-query-and-filters",
  "sort": "relevance",
  "rank": 0.423,
  "popularity": 12,
  "id": "0190..."
}
```
If a cursor generated for `"shoes"` is supplied with query `"shirts"`, the service returns `400 CURSOR_INVALID` to prevent pagination corruption.

---

## 7. Caching Strategy

- **Suggest Cache:** Redis key `search:suggest:{normalizedQ}` with 600s (10m) TTL.
  - Cached only for standard `limit=5` requests.
  - On Redis failure, the service logs a warning and queries PostgreSQL directly.
- **Search Query Cache:** None in v1. High combinatorial cardinality of filters, sorting, and pagination makes caching inefficient. PostgreSQL FTS with GIN indexes satisfies P99 < 250ms target.

---

## 8. Health & Operations

### Health Probes
- `GET /health`: Liveness probe. Returns `200 {"status":"ok"}` without external dependencies.
- `GET /health/ready`: Readiness probe. Checks PostgreSQL, Redis, and Kafka:
  - PostgreSQL down: `503 Service Unavailable`.
  - Redis down: `200 OK` with `checks.redis = "down"`.
  - Kafka down: `200 OK` with `checks.kafka = "down"`.

### Standard Error Codes
- `QUERY_TOO_SHORT` (400)
- `QUERY_INVALID` (400)
- `CURSOR_INVALID` (400)
- `INVALID_FILTER` (400)
- `INDEX_BATCH_TOO_LARGE` (400)
- `SERVICE_KEY_INVALID` (401 / 403)
- `SEARCH_UNAVAILABLE` (503)

