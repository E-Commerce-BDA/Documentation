# Notify Service — Backend (notify-svc :4080)

> What this file is: the plain-language contract for the service that sends
> customer email. It is written before the code, in the same shape as auth.md,
> so the port, the data and the transport rules are agreed before they are built.
> Status: Active | Version 1.0 | Date: 2026-11-25
> Parent: `0.Project-Overview.md` §14 · `1.Architecture.md` §5/§9

Technical words appear only where the builder needs exact names (schema, table
and column names, ports, error codes). Everything else is explained the way
you'd explain it to a shop owner.

---

## 1. The big picture (what talks to what)

Notify is the shop's mailbox. Other services do not write email themselves;
they leave a note in a durable place, and notify turns that note into a message.

```
order-svc / auth-svc / analytics-svc
        │  Kafka domain events (no email addresses in them)
        ▼
   notify-svc (:4080) ──writes──► Postgres notify schema
        │                         (email_logs + processed_events)
        │  SQS task jobs
        ▼
   send-email worker ──► SMTP / Mailpit
```

The events carry a user **id**, never an address. To address a message, notify
asks auth-svc's internal endpoint `GET /internal/users/:id/email` with its
service key (`au-005`). That keeps personal information off the event bus.

The Kafka consumer is in place (ntf-002): it maps four events to SQS email
jobs. The worker that actually resolves the address and sends SMTP arrives in
ntf-003. Until then the SQS module is producer-only, with no poller.

## 2. What notify owns

- **Postgres `notify` schema** in the shared `ecom` database. No new container.
- **`email_logs`** — one row per email job, so a reminder can be audited and
  retried. Columns: `id`, `user_id` (nullable for guests), `aggregate_id`,
  `to_address` (nullable until the worker resolves it), `subject`, `template`,
  `idempotency_key`, `status` (`pending|sent|failed`), `attempts`, `last_error`,
  `created_at`, `sent_at`. Indexes on `status`, `user_id`, `created_at` and a
  unique index on `idempotency_key` so a repeated delivery cannot send twice.
- **`processed_events`** — `event_id`, `topic`, `processed_at`. The claim is
  written in the same transaction as the email log row, so an at-least-once
  redelivery cannot send the same message twice.
- No TTL or sweeper in v1; retention belongs to a separate infrastructure task.

## 3. House rules

1. Kafka is for domain events only. SQS is for task jobs only. Notify consumes
   events and enqueues email jobs; it never publishes a domain event.
2. No email address ever appears in an event payload. The internal lookup is
   the only path from a user id to an address.
3. `reminder.dispatch` does not exist. An idle cart becomes `cart.abandoned`,
   and the send-email queue covers the reminder.
4. The API has no shopper-facing routes. Internal routes use a service key.

### 3.1 Event-to-job mapping

One consumer group, exactly `notify-svc`, subscribes to four topics:

| Event | Job template | Aggregate key |
|---|---|---|
| `order.created` | `order-confirmation` | `orderId` |
| `cart.abandoned` | `cart-abandoned` | `cartId` (`userId` when present) |
| `user.registered` | `welcome` | `userId` |
| `order.status.updated` | `order-confirmation` | `orderId` |

`status-update` was added in contracts 1.17.0. The job carries no status field,
so the rendered notice is deliberately generic; a richer notice needs a new job
field, which would be another contracts change.

Each event is claimed in `notify.processed_events` and gets one `email_logs`
row in the same Postgres transaction. The `notify-send-email` job is enqueued
after commit with the same `idempotencyKey` (`event:<event id>`). If SQS refuses
the job, the claim and log are compensated so a redelivery can retry; if a
commit fails after an enqueue, the worker's unique key drops the duplicate.
The retry ladder is bounded to 20s so five attempts fit inside the 45s broker
session. `KAFKA_CONSUMER_ENABLED=false` parks the consumer.

### 3.2 Send-email worker

The `notify-send-email` worker long-polls 20s in batches of 10. SQS owns the
retries (5 receives) and the `notify-send-email-dlq` dead letter; there is no
Kafka involvement. Set `SQS_TASKS_ENABLED=true` to start the poller — it is off
by default so a local run without LocalStack stays quiet. SMTP points at
Mailpit on port 1025 by default (`SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`).

For each job the worker resolves the address through auth-svc's internal
lookup using `x-service-key: NOTIFY_INTERNAL_SERVICE_KEY`, then sends and
records the provider message id in `email_logs`. A job whose idempotency key is
already `sent` is a no-op. An SMTP or lookup failure is recorded as `failed`
and the error is rethrown so the message is redelivered. A guest cart has no
user id and therefore no address: the job is acknowledged, recorded as failed
with that reason, and not retried.

### 3.3 Templates and support endpoint

Four renderers live in `src/templates/`: `welcome`, `order-confirmation`,
`cart-abandoned` and `status-update`. Each declares the variables it needs. A
missing variable throws in tests and, in production, renders a short generic
body while logging only the template id and the missing key names — never their
values, so an address cannot leak into a log line. Bodies carry identifiers,
never email addresses.

`POST /api/v1/admin/test-email` enqueues one test job through the same SQS path
as a real event and answers `202`. It requires `x-service-key` and accepts a
template plus the aggregate it is about; it never accepts an address.

## 4. Endpoints (v1 scaffold)

| Probe | Happy path | When it says no | Who asks |
|---|---|---|---|
| `GET /health` | `200 {"status":"ok"}` | never while the process runs | Docker `HEALTHCHECK`, restart policy |
| `GET /health/ready` | `200 {"status":"ready","checks":{"db":"up"}}` | `503 {"status":"not_ready","checks":{"db":"down"}}` | Compose `depends_on`, ALB target group |

Health routes sit outside `/api/v1`. Liveness never touches the database: a DB
outage must not trigger a restart loop. Readiness runs `SELECT 1` and returns
the object verbatim so the shape does not become Nest's default error body.

## 5. Gates

`npx tsc --noEmit`, `pnpm test`, `pnpm test:e2e` (health skip paths without a
database), `pnpm lint`, `pnpm build`. Unit tests assert the schema declaration
and health behaviour; unit tests use a fake mailer, so no SMTP or broker is needed.

## Appendix — where each fact lives

- Repo: `notify-svc/` on `master`, port 4080.
- Schema: `db/001-notify-schema.sql`.
- Service code: `src/{app.module,app.setup,main}.ts`, `src/db/`, `src/health/`, `src/consumer/`, `src/tasks/`, `src/templates/`, `src/admin/`.
- Shared contracts: `@ecom/contracts` 1.17.0, `@ecom/messaging` 0.5.0.

## Transport ownership (canonical)

Source of truth: `state-for-agents/STATUS.md` section 5. This table must match
the shared messaging catalog; a service may not claim a producer or consumer
that the running code does not own.

| Role | Topics / queues |
|---|---|
| Publishes | none |
| Consumes | order.created, cart.abandoned, user.registered, order.status.updated |
| SQS tasks | notify-send-email (producer + worker) |
| Must not | No Kafka producer. |
