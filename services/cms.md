# CMS Service — Backend (cms-svc :4050)

> What this file is: the plain-language build checklist for CMS content:
> sections, global and per-section settings, navigation/megamenu, blogs, and
> theme configuration. Phase 1 covers the service foundation; Phase 2 starts
> with the settled contracts and section catalog below.
> Status: Active | Version 1.1 | Date: 2026-10-28
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
* **Save equals publish in v1, except blogs.** Sections, global and
  per-section settings, navigation/theme, and pages publish on save.
  `isActive` is a visibility/publish switch, not a separate draft copy.
  Blogs keep a real `status: draft | published` workflow. Public reads filter
  inactive sections/pages and draft blogs in the Mongo query, never after
  fetching.

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
app Dockerfile. Those start in Phase 2 after the settled decisions in §7 and
the section catalog in §8.

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

## 7. Phase 2 decisions (settled 2026-10-28)

| # | Decision | Locked outcome |
|---|---|---|
| 1 | `@ecom/contracts` | New `ecom-contracts` repo; package `@ecom/contracts@1.0.0`; exact pin; GitHub Release tarball on `v*` tag; ESM + `.d.ts`; Zod 4 peer. |
| 2 | Sections/settings API | Sparse overrides only; storefront resolver remains the merge authority. Public reads return `{sections, version}`, `{theme, version}`, `{navbar, version}`, `{settings, version}`. `version` is the global CMS revision. Admin section reads use `/admin/sections`. Page-scoped auth settings use `/settings/page/:pageKey`. |
| 3 | Nav/theme shape | Contracts own admin payload types based on the storefront `NavSettings` + `shared.megamenu`; theme is `tokens` (colors/radii/photo/typography) plus the existing storefront component groups. Storefront imports payload types; resolved types stay local. |
| 4 | Media | One shared bucket per env (`ecom-media-{env}`); cms-svc owns the `media` collection and `media/` prefix. Backend multipart upload; PNG/JPEG/WebP/AVIF only; 10 MB; no SVG in v1. `media.resize-image` job writes width/format variants. Product images remain catalog-owned URLs. |
| 5 | Atlas backup | Staging M0: nightly `mongodump` to S3, 7-day retention. Production M0: hourly dumps, 30-day retention, RPO ≤1h/RTO ≤30m. Upgrade to M10 + PITR at >350 MB (70% of M0) or when RPO <1h is required. |
| 6 | Draft filtering | Save = publish for sections/settings/nav/theme and pages (`isActive` is the publish switch). Blogs keep `status: draft/published`. Public reads filter in Mongo; admin reads are separate and role-guarded. |

Exact schemas and the section governance catalog live in
`E:/E-Commerce/ecom-contracts/README.md`. `Documentation/8.Versioning.md` is
created with the contracts release.

## 8. CMS section catalog v1

A **CMS section** is a page-body block stored in `cms_sections`, rendered in
`sort_order`. It is not the shell, not a navigation entry, and not a
product/category/brand record.

### 8.1 Types and admin-editable content

| Type | Admin-editable content | Allowed `settings` overrides |
|---|---|---|
| `hero` | `slides[]` (0–12): `id`, `headline`, `image`, `imageAlt?`, `eyebrow?`, `subcopy?`, `bgColor?`, `textColor?`, `imageBgColor?`, `ctas?`, `split?`, `flip?`, `ratio?` | `bgColor`, `blendMode`, `ratio`, `customRatio` |
| `banner` | `title?`, `subcopy?`, `image`, `imageAlt?`, `bgColor?`, `align?`, `ctas?` | `bgColor`, `blendMode` |
| `featured_products` | `title?`, `productIds?` (ordered, max 24), `layout?` (`grid`/`carousel`) | `bgColor`, `blendMode`, `ratio`, `customRatio`, `gutter`, `showPhotos`, `maxItems` |
| `category_showcase` | `title?`, `categoryIds?` (ordered, max 12) | `bgColor`, `blendMode`, `ratio`, `customRatio`, `gutter`, `showPhotos`, `maxItems` |
| `brand_strip` | `title?`, `brandIds?` (ordered, max 24) | `bgColor`, `blendMode`, `gutter`, `maxItems` |
| `blog_teaser` | `title?`, `postIds?` (ordered, max 12), `count?` (1–12) | `bgColor`, `blendMode`, `gutter`, `maxItems` |
| `testimonial` | `title?`, `items?` (max 12): `id`, `quote`, `name`, `role?`, `avatar?` | `bgColor`, `blendMode`, `gutter`, `maxItems` |

`brand_strip` is canonical; the older `brands` value is a legacy alias
normalized before validation. Empty content is valid but skipped by the
storefront. Unknown section types are rejected on write and skipped on read.

### 8.2 What the admin can and cannot modify

| Field / action | Rule |
|---|---|
| Create, delete, reorder, activate/deactivate | Allowed for the seven types. Creates append; reorder is its own endpoint. |
| `key`, `pageKey`, `type` | Create-only and immutable afterwards. A move/type change = create + delete. |
| `title` | Editable; admin-facing label only. |
| `content` | Editable per the type schema above. |
| `settings` | Editable only within the type allowlist; omit a key to inherit; `null` is rejected. |
| `sortOrder` | Not directly editable; only via reorder. |
| `isActive` | Editable visibility toggle; public reads filter it. |
| `createdAt`, `updatedAt`, `version` | Server-managed, read-only. |

Explicitly **not** CMS-managed inside a section: raw HTML/CSS/JS/iframes,
new section types, arbitrary settings keys, product/category/brand/blog
records, prices/stock/availability, page routing/SEO/blocks, navbar/footer
shell, auth/checkout/cart behavior, and media binary lifecycle. Sections store
ordered references and media keys/URLs only.

### 8.3 Public filtering

- Public `GET /sections?pageKey=` returns `isActive: true` only, sorted by
  `sortOrder`.
- Admin `GET /admin/sections?pageKey=` returns all sections.
- Removing all sections is valid; the homepage renders its minimal shell.
- Inactive sections remain in Mongo and are visible to admin only.

## 9. Phase 2 build order

1. **2.0 Contracts** — create `ecom-contracts`, add section/CTA schemas and
   catalog, build/test/pack, release `1.0.0`.
2. **2.1 cms-svc foundation** — models, Zod pipe, revision service, cache
   service, event port, error codes.
3. **2.2 Sections/settings/nav/theme** — public reads, admin CRUD/reorder,
   page-scoped auth settings, cache invalidation, `cms.updated`.
4. **2.3 Pages/blogs** — active/published filters, cursor pagination,
   `blog.updated`.
5. **2.4 Media** — StoragePort interface + local disk adapter, upload/list/delete,
   in-use guard, `media.resize-image` worker.
6. **2.5 Storefront wiring** — contracts types, nav/theme fetch, auth settings
   endpoint, fallback-to-builtins.
7. **2.6 Docs/tests** — API/schema docs, backup runbook, unit/e2e/smoke gates.

## 10. Page blocks, blog blocks, and media governance

### 10.1 Page blocks v1 (locked union)
A page document in `cms_pages` renders structured blocks. Raw HTML/CSS/iframes/scripts are forbidden.
- `rich_text`: `{ id: string, body: string }`
- `image`: `{ id: string, url: string, alt?: string, caption?: string }`
- `cta`: `{ id: string, title: string, ctas: Cta[0..3] }`
- `faq`: `{ id: string, items: { question: string, answer: string }[] }`

### 10.2 Blog blocks v1 (locked union)
A blog post in `cms_blogs` renders an editorial article:
- `heading`: `{ id: string, text: string, level: 1 | 2 | 3 | 4 }`
- `paragraph`: `{ id: string, text: string }`
- `image`: `{ id: string, url: string, alt?: string, caption?: string }`
- `quote`: `{ id: string, quote: string, cite?: string }`
- Blog lifecycle: `status: 'draft' | 'published'`. Public reads strictly filter `status: 'published'`. `blog.updated` emits on publish and update.

### 10.3 Media governance
- **Allowed MIME types:** `image/png`, `image/jpeg`, `image/webp`, `image/avif`. SVG and executables are rejected.
- **Max file size:** 10 MB.
- **Storage key format:** `media/{yyyy}/{mm}/{uuid}.{ext}`.
- **Usage enum:** `section`, `blog`, `page`, `brand`, `category`, `other`. Product images stay catalog-owned.
- **In-use guard:** `DELETE /admin/media/:id` queries `cms_sections`, `cms_pages`, and `cms_blogs`. If the image URL or key is referenced anywhere, deletion is rejected with `409 MEDIA_IN_USE`.
- **Visibility:** `public` (default) or `private`. `private` assets are reachable only through the admin file route. A document written before `cms-003` has no field and is public.

### 10.4 Media delivery and containment

`cms-003` closed two defects: the file route built a path with
`path.resolve(baseDir, key)` and served any key that existed on disk, and
nothing distinguished an editorial asset from a public one.

| Route | Auth | Serves | `Cache-Control` |
|---|---|---|---|
| `GET /cms/media/file/*` | none | `public` rows only | `public, max-age=60, must-revalidate` |
| `GET /cms/admin/media/:id/file` | 👑 admin, Mongo `ObjectId` | any visibility | `private, no-store` |

**Rules**

- **One path builder.** The storage port exposes `resolvePath(key)`; the local
  adapter validates every key in one private method before it touches the disk:
  a null byte is rejected outright, the key is percent-decoded exactly once, the
  `mediaKeySchema` regex decides the shape, and `path.relative(base, abs)` must
  not escape. `save`, `delete`, `exists`, and `resolvePath` all go through it, so
  there is no second way to reach a file.
- **Symlinks.** `resolvePath` re-checks containment after `fs.realpath` on both
  the storage root and the target, so a link planted inside `storage/` cannot
  read outside it.
- **A row is required.** The route resolves a `cms_media` document first, so an
  orphan file on disk is `404` instead of being served.
- **No existence oracle.** A private row and a missing row answer identically
  (`404 MEDIA_NOT_FOUND`, `File not found`) and the body never carries a key, a
  path, or a separator. The public route answers `404` by design; `401`/`403`
  belong to the admin route.
- **Why 60 seconds and not `immutable`.** Visibility is mutable: the same URL can
  be privatised after it was public, so an `immutable` directive would keep the
  bytes publicly cacheable long after the decision. `must-revalidate` plus a
  short TTL bounds that window; a versioned URL (`?v=<updatedAt>`) is the way to
  earn `immutable` later. The admin route is `private, no-store` because it may
  return a private asset.
- **Headers.** Both routes set `Content-Type` from the stored MIME type,
  `X-Content-Type-Options: nosniff`, and `Content-Disposition: inline`. The file
  is `stat`ed before the first header, so a miss stays a JSON error.

## 11. MongoDB Atlas backup & restore runbook

### 11.1 Backup policies & tiers

- **Staging M0 (Free Tier):** Nightly `mongodump` archived and encrypted to S3; 7-day retention policy.
- **Production M0 (Free Tier):** Hourly `mongodump` archived and encrypted to S3; 30-day retention policy; RPO ≤ 1h, RTO ≤ 30m.
- **Upgrade threshold:** When total database storage exceeds 350 MB (70% of the 512 MB M0 quota) or when compliance/business requires RPO < 1h, upgrade cluster to **M10 Dedicated** with native Atlas Continuous Cloud Backups (Point-in-Time Recovery / PITR).

### 11.2 Operational commands

#### A. Automated backup execution
```bash
#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date -u +"%Y%m%d_%H%M%SZ")
BACKUP_FILE="cms_backup_${TIMESTAMP}.gz"

echo "Starting cms-svc backup: ${BACKUP_FILE}"
mongodump --uri="${MONGODB_URI}" --archive="${BACKUP_FILE}" --gzip

echo "Uploading to S3..."
aws s3 cp "${BACKUP_FILE}" "s3://${BACKUP_S3_BUCKET}/cms/hourly/${BACKUP_FILE}" --sse AES256

rm -f "${BACKUP_FILE}"
echo "Backup complete: s3://${BACKUP_S3_BUCKET}/cms/hourly/${BACKUP_FILE}"
```

#### B. Disaster recovery & restore drill
```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="$1" # e.g. cms_backup_20261028_120000Z.gz

echo "Downloading backup from S3: ${BACKUP_FILE}..."
aws s3 cp "s3://${BACKUP_S3_BUCKET}/cms/hourly/${BACKUP_FILE}" "${BACKUP_FILE}"

echo "Restoring database (with --drop to wipe corrupted collections)..."
mongorestore --uri="${TARGET_MONGODB_URI}" --archive="${BACKUP_FILE}" --gzip --drop

rm -f "${BACKUP_FILE}"
echo "Restore complete and verified."
```

### 11.3 Verification & drill schedule

1. **Monthly Restore Drill:** Once a month, the DevOps/Platform agent downloads the latest production archive and restores it into an isolated test cluster (`ecom_cms_drill`), verifying:
   - `cms_meta` singleton document exists and revision counter matches.
   - `cms_sections`, `cms_settings`, `cms_page_settings`, `cms_navigation`, `cms_pages`, `cms_blogs`, `cms_blog_categories`, and `cms_media` record counts match source.
   - Unique and compound indexes are restored without corruption.
2. **Log Alerting:** Any failed backup cron triggers a high-priority PagerDuty / Slack alert (`cms.backup.failed`).

