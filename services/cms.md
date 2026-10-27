# CMS Service — Backend (cms-svc :4050)

> What this file is: the plain-language build checklist for CMS content:
> sections, global and per-section settings, navigation/megamenu, blogs, and
> theme configuration. Phase 1 covers the service foundation only.
> Status: Active | Version 1.0 | Date: 2026-10-27
> Parent: `0.Project-Overview.md` §14 · `1.Architecture.md` §5/§9 · `3.Database-Schema.md` §4
> Referenced by: `6.Admin-Panel.md`, `pages/home.md` (to create)

Technical words appear only where the builder needs exact names (collection
names, error codes, endpoint paths, headers). Everything else is explained
the way you'd explain it to a shop owner.

---

## 1. The big picture (what talks to what)

Think of the CMS as the shop's content office:

```
Admin panel / storefront        Nginx gateway                 cms-svc (:4050)
(content editors, shoppers)     verifies identity,            owns content truth
                                stamps request id
        │                              │                              │
        │   read published content     │                              │
        └─────────────────────────────►│─────────────────────────────►│
                                       │                              │
                                       │                    ┌─────────▼─────────┐
                                       │                    │ MongoDB (Atlas)   │
                                       │                    │ sections/settings │
                                       │                    └─────────┬─────────┘
                                       │                              │
                                       │                    ┌─────────▼─────────┐
                                       │                    │ Redis             │
                                       │                    │ cache (degraded)  │
                                       │                    └───────────────────┘
```

* **MongoDB is the source of truth** for CMS documents. The service fails
  fast if Mongo is unavailable at startup, because serving stale or empty
  content is worse than refusing to start.
* **Redis is an accelerator, not the truth.** Readiness reports Redis as
  `down` while still returning `200` when Mongo is healthy. CMS reads can
  fall back to Mongo; Redis outages must not take the content office down.
* **The gateway owns identity.** `cms-svc` verifies the access token itself
  on role-sensitive routes and never trusts a raw `x-roles` header. Phase 1
  provides the guard plumbing; no CMS route is protected yet.
* **Save equals publish in v1.** There is no draft/publish workflow in the
  first CMS release. Public reads see the latest saved content. Draft
  filtering is a Phase 2 contract decision, not a Phase 1 behavior.

## 2. What Phase 1 includes

| Area | Delivered |
|---|---|
| Bootstrap | NestJS 12 on Node 24, ESM build, `/api/v1` prefix with health excluded |
| Config | Joi-validated `NODE_ENV`, `PORT`, `MONGODB_URI`, `JWT_SECRET`, `REDIS_URL` |
| Mongo | Global Mongoose connection, 5s server selection, fail-fast startup (`retryAttempts: 0`) |
| Redis | Single ioredis client, offline queue disabled, 1s connect timeout |
| Health | `GET /health` liveness and `GET /health/ready` readiness |
| Auth | Global JWT module, `JwtAuthGuard`, `RolesGuard`, `@Roles()` decorator |
| HTTP behavior | Request ID propagation, standard error envelope, cache-control, validation pipe |
| Local runtime | Dockerized Mongo 8 on `127.0.0.1:27018`, local Redis on `6379` |
| Tests | Unit and e2e suites against real Mongo + Redis |

Deliberately **not** in Phase 1: CMS collections/models, content endpoints,
Zod request/response schemas, event publishing, S3/media handling, and the
app Dockerfile. Those start in Phase 2/3 after the contract decisions in §7.

## 3. Health probes

| Probe | Happy path | When it says no | Who asks |
|---|---|---|---|
| `GET /health` | `200 {"status":"ok"}` | never while the process runs | Docker `HEALTHCHECK`, restart policy |
| `GET /health/ready` | `200 {"status":"ready","checks":{"mongo":"up","redis":"up"}}` | `503 {"status":"not_ready","checks":{"mongo":"down","redis":"up"}}` | Compose `depends_on`, ALB target group |

Redis is degraded by design:

```json
{
  "status": "ready",
  "checks": { "mongo": "up", "redis": "down" }
}
```

Mongo is critical. A readiness probe that cannot ping Mongo within two
seconds returns `503` and identifies `mongo` as `down`. Health responses are
not wrapped in the API error envelope and are always `Cache-Control:
no-store`.

## 4. Local runtime and configuration

MongoDB runs as `ecom-cms-mongo` on `127.0.0.1:27018` with the
`ecom-cms-mongo-data` volume. Local Mongo has no authentication and is bound
to loopback only. Atlas is reserved for the separate staging smoke
environment in Phase 7 and is never used by automated tests.

| Variable | Purpose | Local default |
|---|---|---|
| `NODE_ENV` | `development`, `test`, or `production` | `development` |
| `PORT` | HTTP port | `4050` |
| `MONGODB_URI` | Mongo connection string including database name | `mongodb://127.0.0.1:27018/ecom_cms` |
| `JWT_SECRET` | Shared access-token secret, minimum 32 characters | local-only value in `.env` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |

E2E tests use `ecom_cms_test`, refuse to run against a non-`_test` database,
and drop the test database when finished. The test runner is intentionally
serial (`fileParallelism: false`) because the suite owns one database.

## 5. Security and shared HTTP behavior

* **JWT verification.** Access tokens must use `HS256`, issuer `ecom-auth`,
  audience `ecom-api`, and a 30-second clock tolerance. `JwtAuthGuard`
  attaches the verified user to the request; `RolesGuard` checks
  `@Roles(...)` metadata against the verified roles only.
* **No header trust.** A caller cannot gain a role by sending `x-roles`.
  Role-sensitive routes must use both guards.
* **Error envelope.** Non-health errors return:
  ```json
  {
    "error": {
      "code": "NOT_FOUND",
      "message": "Cannot GET /api/v1/unknown"
    },
    "requestId": "9da57367-c4be-43b4-9376-264162c355da",
    "timestamp": "2026-10-27T17:30:58.950Z"
  }
  ```
* **Request tracing.** The gateway `x-request-id` is echoed in the response
  header and embedded in error responses. Missing or blank values get a fresh
  UUIDv4.
* **Cache policy.** Mutating methods (`POST`, `PATCH`, `PUT`, `DELETE`) get
  `Cache-Control: no-store`. Health responses are always `no-store`.
* **Input hygiene.** Global `ValidationPipe` uses `whitelist` and
  `forbidNonWhitelisted`; the JSON and URL-encoded body limit is 1 MB.
* **No protected CMS routes yet.** The guards are installed and tested, but
  Phase 1 exposes only health endpoints.

## 6. Verification (Phase 1)

| Gate | Result |
|---|---|
| `pnpm lint` | 0 warnings / 0 errors |
| `pnpm test` | 35 tests across 7 files passed |
| `pnpm test:e2e` | 5 tests across 2 files passed against real Mongo + Redis |
| `pnpm typecheck` | clean |
| `pnpm build` | clean; output includes `dist/main.js` |
| Production smoke | `/health` `200`; `/health/ready` `200` with both dependencies up; unknown API route `404` with envelope |
| Mongo-down smoke | `/health/ready` `503` with `mongo: "down"`, `redis: "up"` after Mongo stopped |
| Mongo-down startup | process exits after the 5s selection timeout; no retry loop |

The production smoke test caught an ESM-only issue: Mongoose’s `Connection`
type was being emitted as a runtime import because of decorator metadata.
Changing it to a type-only import fixed `node dist/main.js`; the full gate set
was then re-run.

A second startup smoke caught `@nestjs/mongoose`’s default retry loop.
`retryAttempts: 0` now makes boot fail after the selection timeout instead of
retrying for roughly 27 seconds.

## 7. Phase 2 prerequisites (open contract decisions)

Phase 2 must not start until these are settled:

1. `@ecom/contracts` package name, version, and publish workflow.
2. Sections/settings API shape: global vs per-section override payloads,
   version field, and cache-buster semantics.
3. Navigation/megamenu and theme shape shared with the storefront.
4. Media scope: S3 upload/ownership model and `media.resize-image` task
   contract.
5. Atlas backup/restore strategy for staging and production.
6. Public draft filtering: confirm save-equals-publish for v1 or introduce a
   draft state before the first public read endpoint.

Until then, the service stays a verified foundation with no CMS domain code.
