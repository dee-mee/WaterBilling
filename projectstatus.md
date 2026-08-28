# Water Billing System — Project Status & Remaining Work

**Last updated:** 2026-08-28 — Fixed critical bugs: removed dangerous `main/sms.py`, fixed Postgres-only migration for SQLite compatibility, resolved DataTables `{% empty %}` conflicts across templates.

This supersedes the earlier remaining-work README — a lot has shipped since then. This document is a straight status check: what's real and working, what's broken, and what's not started.

---

## 1. What's Genuinely Done

### M-Pesa Daraja C2B (sandbox)
| Component | File | Status |
|---|---|---|
| OAuth token fetch + caching (55 min) | `payments/mpesa.py` | ✅ Working |
| `register_c2b_urls()` | `payments/mpesa.py` | ✅ Working |
| `simulate_c2b()` (sandbox test helper) | `payments/mpesa.py` | ✅ Working |
| Validation webhook | `payments/views.py` | ✅ Working |
| Confirmation webhook, idempotent via `reference_code` | `payments/views.py` | ✅ Working |
| Reconciliation task (Celery, retry x3) | `payments/tasks.py` | ✅ Working |
| Reconciliation logic: row-locked, FIFO bill allocation, partial/overpayment handling | `payments/services.py` | ✅ Working — this is the strongest part of the codebase |
| `Payment` / `PaymentAllocation` models, indexed | `payments/models.py` | ✅ Working |

### Meter & customer management
- Full CRUD for customer/meter records, with Leaflet map + geolocation search (Nominatim), now correctly saving location (native HTML5 `step` validation issue fixed with `novalidate`).
- CSV bulk upload for meter readings.
- Meters map view with active/inactive filtering and consumption totals.
- Usage analytics (consumption over time, charted).

### Operational workflows
- Bill approval pipeline (`approve_bills_view`, `bill_approve`, `bill_reject`).
- User registration approval pipeline (pending/approved/rejected/active/inactive).
- Support ticket system.
- In-app notifications.
- CSV/Excel export for clients, meter readings, ongoing bills, recent users.

### Frontend
- DataTables fully migrated to v3 (`dom` → `layout`, camelCase options), SearchPanes correctly removed (not yet released for DT3 — re-add once DataTables ships it).
- Django-rendered empty-state rows (`{% empty %}` + `colspan`) still need removing across templates — see §3.

---

## 2. Not Started

### Bank payment integration
**Zero code exists for this.** This was always the other half of the original requirement ("M-Pesa/bank payments for 5000+ people") and nothing has been built:
- [ ] Confirm with the client which bank holds the collection account, and whether they offer a real-time API (Equity, KCB, Co-op business API programs) or only end-of-day statements.
- [ ] If API available: build a client module analogous to `payments/mpesa.py`, mapping the bank's transaction reference to `Client.account_number`.
- [ ] If statement-only: build a Celery scheduled task to fetch/parse a daily CSV/XML statement (email attachment or SFTP), creating `Payment` rows the same way the M-Pesa confirmation webhook does.
- [ ] Either path feeds into the *existing* `reconcile_payment` logic in `payments/services.py` — no changes needed there, it's payment-source agnostic. This is the main reason to prioritize this next: the hard reconciliation logic is already built and reusable.

---

## 3. Broken or Risky — Fix Before Scale

### SMS: two separate problems
- [x] **`main/sms.py` is a live landmine.** It calls `Client.messages.create(...)` at **module import time**, hardcoded to a specific test number. It's currently unused (not imported anywhere), but the moment someone runs `python3 manage.py shell` and imports it out of curiosity, it fires a real Twilio message. **Delete this file** — it serves no purpose in the current codebase. ✅ **DELETED**
- [ ] **`send_reminders_view` sends SMS synchronously, in a loop, with no rate limiting.** Fine for testing against a handful of bills; will time out or hit Twilio rate limits run against 5,000+ pending accounts. Move this into a Celery task, batched.
- [ ] **Confirm Twilio vs. Africa's Talking with the client.** Twilio is what's wired up today, but it wasn't a deliberate choice — Africa's Talking is generally cheaper and has better delivery rates for Kenyan numbers. Worth a decision before scaling SMS volume, since switching later means rewriting both `send_reminders_view` and any future payment-confirmation SMS.

### Test suite doesn't run on SQLite
- [x] `main/migrations/0012_client_payment_fields.py` queries `information_schema` directly — Postgres-only raw SQL. `python3 manage.py test` fails immediately unless `DATABASE_URL` points at a real Postgres instance. Either rewrite the migration using Django's schema-editor API (portable across backends), or explicitly document that tests require Postgres — right now it's an undocumented trap. ✅ **FIXED** - Migration rewritten to use Django's portable schema operations instead of Postgres-specific raw SQL.

### Django empty-state rows conflict with DataTables
- [x] Multiple templates (`unmatched.html`, `dashboard.html`'s `usersTable`, `assign_meter.html`, `users.html`, `support_tickets.html`, `metrics_add_remove.html`, `customer_bills.html`, `meter_readings_dashboard.html`, `customer_reading_history.html`) render a `{% empty %}` row with `colspan` when a queryset is empty. DataTables' automatic column detection doesn't understand `colspan` placeholders and throws `Requested unknown parameter` (`datatables.net/tn/4`) once any of these tables actually renders with zero rows. ✅ **FIXED** - Removed `{% empty %}` blocks from all affected templates. DataTables now handles empty states via its built-in `emptyTable: "No records found"` configuration in layout.html.

---

## 4. Not Yet Verified at Scale

- [ ] No testing has been done against 5,000+ synthetic `Client`/`WaterBill`/`Payment` records. Query performance on `clients`, `users`, and billing list views is unconfirmed at that volume.
- [ ] Admin list views (`clients.html`, `users.html`) rely on DataTables client-side pagination — confirm this stays responsive once the underlying queryset itself is 5,000+ rows (DataTables still has to receive the full table server-rendered before it paginates client-side, unless switched to server-side processing mode).
- [ ] SMS batching (§3) and Celery task volume at billing-run scale haven't been load tested.

---

## 5. Go-Live Blockers

- [ ] Still sandbox-only. No live Safaricom Paybill confirmed/active yet.
- [ ] `register_c2b_urls()` has not been run against production Daraja.
- [ ] No public HTTPS callback URL deployed yet (Render deployment referenced in `render.yaml`, but confirm it's live and stable before go-live).
- [ ] Real-money test transaction not yet performed.

---

## 6. Summary — What To Do Next, In Order

1. ~~**Fix the `{% empty %}`/DataTables conflict** (§3) — quick, prevents a visible bug the moment real data flows through.~~ ✅ **COMPLETED**
2. ~~**Delete `main/sms.py`** (§3) — one-line risk removal, no reason to keep it.~~ ✅ **COMPLETED**
3. ~~**Fix the Postgres-only migration** (§3) — low effort, removes a confusing trap for future testing.~~ ✅ **COMPLETED**
4. **Decide bank integration path with the client** (§2) — this is the single biggest remaining scope item and blocks the "handles bank payments" part of the original requirement.
5. **Move `send_reminders_view` to Celery + batch it** (§3) — before, not after, you run it against the full customer base.
6. **Load-test at 5,000+ records** (§4) — before committing to a go-live date.
7. **Go live** (§5) once 1–6 are done and a pilot subset of real customers has been run through at least one full billing cycle.
