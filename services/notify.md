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

In this first slice (ntf-001) the service is a scaffold: it owns its schema and
answers health probes. The Kafka consumer and the SQS worker arrive in ntf-002
and ntf-003.

## 2. What notify owns

- **Postgres `notify` schema** in the shared `ecom` database. No new container.
- **`email_logs`** — one row per attempted send, so a reminder can be audited
  and retried. Columns: `id`, `user_id`, `to_address`, `subject`, `template`,
  `status` (`pending|sent|failed`), `attempts`, `last_error`, `created_at`,
  `sent_at`. Indexes on `status`, `user_id` and `created_at`.
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
and health behaviour; no live broker or SMTP is needed for the scaffold.

## Appendix — where each fact lives

- Repo: `notify-svc/` on `master`, port 4080.
- Schema: `db/001-notify-schema.sql`.
- Service code: `src/{app.module,app.setup,main}.ts`, `src/db/`, `src/health/`.
- Shared contracts: `@ecom/contracts` 1.16.0, `@ecom/messaging` 0.5.0.
