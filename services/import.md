# Import Service — Backend (import-svc :4070)

> What this file is: the plain-language contract for the service that turns a
> uploaded product file into catalog products. Written before the code, in the
> auth.md shape, so the port, data and transport rules are agreed first.
> Status: Active | Version 1.0 | Date: 2026-11-25
> Parent: `0.Project-Overview.md` §14 · `1.Architecture.md` §5/§9

Technical words appear only where the builder needs exact names (schema, table
and column names, ports, error codes). Everything else is explained the way
you'd explain it to a shop owner.

---

## 1. The big picture (what talks to what)

Import is the shop's loading dock. A file arrives, each row is checked on its
own, and a valid row becomes a product through an event.

```
Admin UI ──upload──► import-svc (:4070) ──writes──► Postgres import schema
                            │                     (import_jobs + import_rows)
                            │  SQS task jobs
                            ▼
                     import-process-row worker
                            │
                            ▼ Kafka product.imported ──► catalog-svc, search-svc
```

One bad row must not fail the whole file, so rows are split into tasks and
retried individually. The job record is the report an admin polls.

In this first slice (imp-001) the service owns only its schema and health
probes. The upload API and SQS producer arrive in imp-002; the worker and the
`product.imported` publisher arrive in imp-003.

## 2. What import owns

- **Postgres `import` schema** in the shared `ecom` database. No new container.
- **`import_jobs`** — one row per uploaded file. Columns and indexes are
  specified in `3.Database-Schema.md` §3.6: `id`, `source`, `file_key`,
  `status` (`pending|processing|completed|failed|partial`), `total_rows`,
  `success_count`, `failed_count`, `errors` (JSONB), `created_by`,
  `created_at`, `updated_at`. Indexes on `status` and `created_at`.
- **`import_rows`** — one row per source row, so retries and the report are
  per-row. `id`, `job_id`, `row_number`, `status` (`pending|processed|failed`),
  `payload` (JSONB), `error` (JSONB), `product_id`, `created_at`, `updated_at`.
  Unique on `(job_id, row_number)`.
- No TTL or sweeper in v1; retention is a separate infrastructure task.

## 3. House rules

1. Kafka is for domain events only; SQS is for row jobs only. Import publishes
   `product.imported` and never consumes a Kafka topic.
2. A row's identity is `(jobId, rowNumber)`, so a redelivered task updates the
   same row instead of appending another.
3. No real customer data in fixtures: tests use synthetic SKUs and names.

## 4. Endpoints (v1 scaffold)

| Probe | Happy path | When it says no | Who asks |
|---|---|---|---|
| `GET /health` | `200 {"status":"ok"}` | never while the process runs | Docker `HEALTHCHECK`, restart policy |
| `GET /health/ready` | `200 {"status":"ready","checks":{"db":"up"}}` | `503 {"status":"not_ready","checks":{"db":"down"}}` | Compose `depends_on`, ALB target group |

Health routes sit outside `/api/v1`. Liveness never touches the database;
readiness runs `SELECT 1` and returns the object verbatim so the shape does not
become Nest's default error body.

## 5. Gates

`npx tsc --noEmit`, `pnpm test`, `pnpm test:e2e` (health skip paths without a
database), `pnpm lint`, `pnpm build`. Unit tests assert the schema declaration
and health behaviour; no broker or SQS is needed for the scaffold.

## Appendix — where each fact lives

- Repo: `import-svc/` on `master`, port 4070.
- Schema: `db/001-import-schema.sql`.
- Service code: `src/{app.module,app.setup,main}.ts`, `src/db/`, `src/health/`.
- Shared contracts: `@ecom/contracts` 1.17.0, `@ecom/messaging` 0.5.0.
