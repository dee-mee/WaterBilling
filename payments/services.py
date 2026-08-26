from django.db import transaction
from django.db.models import F

from main.models import Client, WaterBill, money
from payments.account_refs import normalize_account_reference
from payments.models import Payment, PaymentAllocation
from payments.notifications import notify_payment_received


def resolve_client(account_reference):
    raw = "".join(str(account_reference or "").split())
    if not raw:
        return None
    seen = set()
    candidates = [raw, normalize_account_reference(raw)]
    normalized = normalize_account_reference(raw)
    if normalized.isdigit():
        for width in range(len(normalized), 13):
            candidates.append(normalized.zfill(width))
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        client = Client.objects.filter(account_number=candidate).first()
        if client:
            return client
    return None


def reconcile_payment(payment_id):
    """Apply a pending payment to oldest unpaid approved bills (FIFO)."""
    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment_id)
        if payment.status == Payment.Status.MATCHED:
            return payment

        client = payment.client or resolve_client(payment.account_reference)
        if not client:
            payment.status = Payment.Status.UNMATCHED
            payment.save(update_fields=["status"])
            return payment

        client = Client.objects.select_for_update().get(pk=client.pk)
        remaining = money(payment.amount) + money(client.credit_balance)
        client.credit_balance = money(0)

        bills = (
            WaterBill.objects.select_for_update()
            .filter(
                name=client,
                approval_status="Approved",
                payment_status__in=WaterBill.UNPAID_STATUSES,
            )
            .order_by(F("billing_date").asc(nulls_last=True), "id")
        )

        for bill in bills:
            if remaining <= 0:
                break
            due = money(bill.payable())
            already_paid = money(bill.amount_paid)
            need = due - already_paid
            if need <= 0:
                bill.payment_status = "Paid"
                bill.save(update_fields=["payment_status"])
                continue
            apply_amt = min(remaining, need)
            PaymentAllocation.objects.create(
                payment=payment,
                water_bill=bill,
                amount=apply_amt,
                amount_due_at_match=due,
            )
            bill.amount_paid = already_paid + apply_amt
            bill.payment_status = "Paid" if bill.amount_paid >= due else "Partial"
            bill.save(update_fields=["amount_paid", "payment_status"])
            remaining -= apply_amt

        client.credit_balance = remaining
        client.save(update_fields=["credit_balance"])
        payment.client = client
        payment.status = Payment.Status.MATCHED
        payment.save(update_fields=["client", "status"])

    notify_payment_received(payment)
    return payment
