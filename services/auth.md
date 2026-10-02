# Auth Service — Backend (auth-svc :4010)

> What this file is: the plain-language build checklist for login, signup,
> sessions, and logout. First per-service backend doc — the other 8
> services copy this shape later.
> Status: Active | Version 1.0 | Date: 2026-09-18
> Parent: `0.Project-Overview.md` §14 · `1.Architecture.md` §5/§9
> Referenced by: `pages/auth.md` (frontend companion, to create)

Technical words appear only where the builder needs exact names (table and
column names, error codes, endpoint paths). Everything else is explained
the way you'd explain it to a shop owner.

---

## 1. The big picture (what talks to what)

Think of the shop's security like a mall with one main entrance:

```
Shopper's browser          Main entrance (Nginx gateway)         Shops inside (services)
(cookies in a               Checks the stamp, hands out           Trust the entrance's
 locked box the              a fresh name badge, sends            word — they never
 page can't open)            you to the right shop               check IDs themselves
        │                             │                                    │
        │   locked box (login)        │  ┌──────────────┐                  │
        └────────────────────────────►│  │  auth-svc    │                  │
                                      │  │  ID office   │                  │
                                      │  └──────┬───────┘                  │
                                      │         │ writes/reads             │
                                      │  ┌──────▼───────┐    ┌───────────┐ │
                                      │  │  Postgres    │◄───│   Redis   │ │
                                      │  │  filing      │    │  sticky   │ │
                                      │  │  cabinet     │    │  notes    │ │
                                      │  └──────────────┘    └───────────┘ │
```

* The **browser** keeps two cookies in a locked box JavaScript cannot open
  (HttpOnly). One is a short permission slip, one is a coat-check ticket.
* The **gateway (Nginx)** is the only one that checks stamps. It throws
  away any name badge a visitor made themselves, verifies the real stamp,
  and writes a fresh trusted badge (`x-user-id`, `x-roles`) for the shops
  inside. It also stamps every visit with a tracking number
  (`x-request-id`) so any complaint can be traced.
* **auth-svc** is the ID office: it makes the stamps, keeps the filing
  cabinet (Postgres), and answers "is this ticket still good?".
* The other shops (cart, order, cms) **never check IDs** — they trust the
  entrance's badge. They sit behind a staff-only door (service key now,
  certificates later) on a private corridor no shopper can enter.

## 2. The two tokens, in plain words

* **Permission slip (access token, lives 15 minutes).** A folded note that
  says "Ana, customer, until 8:15" plus a wax seal only the ID office can
  make. Checking it means re-pressing the seal and comparing — no filing
  cabinet visit, no phone calls. Anyone who changes one letter breaks the
  seal. Nothing about it is ever stored anywhere.
* **Coat-check ticket (refresh token, lives up to 30 days).** A random
  number that means nothing by itself. The office keeps a matching stub
  in the filing cabinet: whose ticket, when it expires, and whether it
  was already used or cancelled. Showing the ticket gets you a fresh
  permission slip.

Why two instead of one: the slip is shown on *every* request (so it must
be checkable for free and die fast if stolen), while the ticket is shown
rarely (so it can afford a cabinet lookup and can be cancelled on demand).

## 3. House rules (security policies P1–P6)

* **P1 — Homemade badges go in the bin.** The entrance deletes any
  `x-user-id`, `x-roles`, or service key arriving from outside before
  doing anything else. Forged headers die at the door.
* **P2 — Check stamps properly.** Re-press the seal (pinned HS256
  algorithm — never trust the note's own claim about how it was sealed),
  allow 30 seconds of clock disagreement between machines, confirm it was
  issued by auth-svc.
* **P3 — Mind the entrance.** Fresh badges only after a passed check;
  scrub upstream error pages into a plain envelope + tracking number;
  speed limits: login/refresh 10 per second, checkout 5, normal reads 30.
* **P4 — Shops trust the entrance, not visitors.** Staff-only door key
  today (long random string, locked file permissions), certificates
  between shops later. Shops bind to the private corridor only.
* **P5 — Keys live in safes, not notebooks.** Secrets in locked files on
  the server (later a secret manager). Nothing secret in git, in logs,
  or in error messages shown to shoppers.
* **P6 — Everything traceable.** Every log line carries the visit's
  tracking number; alarms fire on break-in patterns (reused tickets,
  ban waves, rate-limit storms). Token values never appear in logs —
  fingerprints only.

## 4. The counters (endpoints)

| Counter | Speed limit | Happy path | When it says no |
|---|---|---|---|
| Sign up | 10/s | `201` + account created + signed in + `user.registered` announced | `409` email taken (plain words) · `400` weak password (with guidance) |
| Sign in | 10/s | `200` + both cookies set | `401` "invalid email or password" — identical whether the email or the password was wrong, so strangers can't probe which accounts exist |
| Refresh (fresh slip please) | 10/s | `200` + new pair, old ticket cancelled | `401` ticket expired → sign in again · `401` ticket already used → whole family cancelled + "signed out for safety" notice |
| Sign out | — | `204`, always, even if already signed out (safe to retry) | never errors |
| My profile | 30/s | `200` your details | `401` not signed in · `403` signed in but asking for someone else's |
| Change password | 5/s | `204` + all other sessions cancelled | `401` current password wrong (generic) |
| Forgot / reset | 5/s | `202` accepted — same reply whether the email exists or not | single-use expiring reset link by mail |

## 5. Changing the locks (rotation, step by step)

1. Ticket arrives → check the sticky note (Redis). Found and fresh: proceed.
   Missing: check the filing cabinet (Postgres row by ticket fingerprint).
   Gone or cancelled: refuse.
2. In one indivisible step: file a new stub, stamp the old stub
   "cancelled" (never delete it — a used-up stub is the proof of theft),
   swap the sticky note, sign a fresh slip, set both cookies.
3. **The 10-second grace:** two browser tabs refreshing at once can both
   show the same ticket. A just-cancelled ticket re-shown within 10
   seconds gets the already-made pair, not a theft alarm.
4. Remember-me unchecked → ticket dies with the browser (24h cap);
   checked → 30-day hard cap, never extended by use.

## 6. Awkward situations (edge cases)

* **Not signed in, asking for a profile** → `401` ("who are you?").
  Signed in, asking for *someone else's* → `403` ("I know you, answer's
  no"). Never swapped, never disguised as "not found".
* **Slip expired mid-shop** → fresh pair issued silently, request
  continues. Ana notices nothing.
* **Account switched off (banned)** → sign-in refused, all live sessions
  cancelled, and the checkout counter double-checks status on every order.
* **Stolen ticket used by a thief** → the real user's next refresh shows
  an already-cancelled stub: proof of theft. Cancel everything of that
  user, log a security event, ask them to sign in again.
* **Redis asleep** → look in the filing cabinet instead (a few
  milliseconds slower, fully correct). The shop stays open.
* **Too many knocks** → `429` + "try again in N seconds".
* **Guest basket at sign-in** → the shop merges it into the user's basket
  on the server (same goods add up, different goods append). Baskets are
  never merged by the browser.
* **Clocks disagree** → 30 seconds of forgiveness on expiry times.

## 7. Receipts (errors + traceability)

Every "no" comes as the same receipt shape: `{code, message, requestId,
status}`. The `code` is a fixed machine word from the shared contracts
package (screens switch on it: sign-in redirect vs security notice vs
support page). The `message` is safe to show a shopper — never table
names, never stack traces. The `requestId` is the visit's tracking number
from the entrance: one number pasted to support replays the whole story
across gateway, ID office, and cache.

## 8. Proving it works (blocks frontend wiring)

Green before any page connects: register → sign in → silent refresh →
sign out kills the session; wrong credentials give the generic 401;
rate limits answer 429; switched-off accounts stay out; guest basket
merges; password change kills other sessions; two tabs refreshing at
once don't trigger theft alarms.

## Appendix — where each fact lives (related files)

* Tables and columns (`users`, `refresh_tokens`, RBAC):
  `3.Database-Schema.md` §3.1 (lines ~72–140); table inventory:
  `temp.md` §A–B.
* Endpoint shapes, rates, envelopes, error codes: `4.API-Design.md`
  §3–4 (auth §4.1–4.2, codes table, `requestId` envelope).
* Service map, gateway routes, transports, Redis keyspaces and the
  degrade-to-DB rule: `1.Architecture.md` §5–6, §9, §13
  (auth row, Nginx locations, `sess:{tokenId}` cache, Kafka/SQS notes).
* What shoppers must experience (acceptance boxes): `5.Features.md`
  A11.1–A11.4 (signup, signin, protected routes, forgot password).
* Test rows that gate this module: `9.Testing.md` (auth flows, 401/429,
  disabled-user, guest-merge).
* Log format and debug path: `10.Observability.md` (requestId tracing).
* Repo/tech context (ports, JWT library, Redis client, polyrepo model):
  `0.Project-Overview.md`, `2.Tech-Stack.md`.
* Frontend companion (to create): `pages/auth.md` — cookie handling in
  Next.js, guards, forms; points back here for everything server-side.
