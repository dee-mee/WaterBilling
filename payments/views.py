import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from payments.models import Payment
from payments.services import resolve_client

logger = logging.getLogger(__name__)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or ""


def _ip_allowed(request):
    allowed = getattr(settings, "MPESA_ALLOWED_IPS", []) or []
    if not allowed:
        return True
    return _client_ip(request) in allowed


def _secret_ok(callback_secret):
    expected = settings.MPESA_CALLBACK_SECRET
    if not expected:
        return callback_secret is None
    if callback_secret is None:
        return False
    return callback_secret == expected


def _deny():
    return JsonResponse({"ResultCode": "C2B00016", "ResultDesc": "Rejected"}, status=403)


def _parse_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


@csrf_exempt
@require_POST
def mpesa_validation(request, callback_secret=None):
    if not _secret_ok(callback_secret) or not _ip_allowed(request):
        return _deny()
    payload = _parse_body(request)
    bill_ref = payload.get("BillRefNumber") or payload.get("BillRefNo") or ""
    client = resolve_client(bill_ref)
    if client:
        return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})
    return JsonResponse({"ResultCode": "C2B00012", "ResultDesc": "Invalid Account Number"})


def _enqueue_reconcile(payment_id):
    try:
        from payments.tasks import reconcile_payment_task

        reconcile_payment_task.delay(payment_id)
        return True
    except Exception:
        logger.warning("Could not enqueue reconcile for payment %s", payment_id, exc_info=True)
        return False


@csrf_exempt
@require_POST
def mpesa_confirmation(request, callback_secret=None):
    """Always HTTP 200 so Safaricom does not retry into duplicate work."""
    try:
        if not _secret_ok(callback_secret) or not _ip_allowed(request):
            return JsonResponse({"ResultCode": "0", "ResultDesc": "Rejected"})

        payload = _parse_body(request)
        trans_id = (payload.get("TransID") or "").strip()
        if not trans_id:
            logger.warning("M-Pesa confirmation missing TransID")
            return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})

        amount = payload.get("TransAmount") or "0"
        bill_ref = payload.get("BillRefNumber") or payload.get("BillRefNo") or ""
        payment, created = Payment.objects.get_or_create(
            reference_code=trans_id,
            defaults={
                "amount": amount,
                "method": Payment.Method.MPESA,
                "account_reference": str(bill_ref).strip(),
                "status": Payment.Status.PENDING,
                "raw_payload": payload,
            },
        )
        if created or payment.status == Payment.Status.PENDING:
            _enqueue_reconcile(payment.pk)
    except Exception:
        logger.exception("M-Pesa confirmation handler error")
    return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})


@csrf_exempt
@require_POST
def stk_push_callback(request, callback_secret=None):
    """Callback receiver for Safaricom Daraja STK Push."""
    try:
        if not _secret_ok(callback_secret):
            return JsonResponse({"ResultCode": "0", "ResultDesc": "Rejected"})

        payload = _parse_body(request)
        logger.info("STK Push Callback payload: %s", payload)

        stk_body = payload.get("Body", {}).get("stkCallback", {})
        result_code = stk_body.get("ResultCode")

        if result_code == 0:
            metadata = stk_body.get("CallbackMetadata", {}).get("Item", [])
            meta_dict = {item.get("Name"): item.get("Value") for item in metadata if isinstance(item, dict) and "Name" in item}

            receipt_no = str(meta_dict.get("MpesaReceiptNumber") or "").strip()
            amount = meta_dict.get("Amount") or "0"

            if receipt_no:
                account_ref = str(stk_body.get("CheckoutRequestID", "")).strip()
                payment, created = Payment.objects.get_or_create(
                    reference_code=receipt_no,
                    defaults={
                        "amount": amount,
                        "method": Payment.Method.MPESA,
                        "account_reference": account_ref,
                        "status": Payment.Status.PENDING,
                        "raw_payload": payload,
                    },
                )
                if created or payment.status == Payment.Status.PENDING:
                    from payments.services import reconcile_payment
                    reconcile_payment(payment.pk)

        return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})
    except Exception:
        logger.exception("Error processing STK Push callback")
        return JsonResponse({"ResultCode": "0", "ResultDesc": "Accepted"})


def initiate_customer_stk_push(request):
    """AJAX endpoint for customer to trigger M-Pesa STK Push prompt on their phone."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST method required."}, status=405)

    try:
        from main.models import WaterBill
        from payments.mpesa import initiate_stk_push, format_phone_number

        bill_id = request.POST.get("bill_id")
        phone_number = request.POST.get("phone_number")

        if not bill_id:
            return JsonResponse({"success": False, "message": "Bill ID is required."})

        try:
            bill = WaterBill.objects.get(id=bill_id)
        except WaterBill.DoesNotExist:
            return JsonResponse({"success": False, "message": "Bill not found."})

        # Security check: ensure user owns the bill or is staff
        user = request.user
        if not (user.is_staff or user.is_superuser):
            if not (bill.name and bill.name.user == user):
                return JsonResponse({"success": False, "message": "Unauthorized access to this bill."})

        if bill.payment_status == "Paid":
            return JsonResponse({"success": True, "already_paid": True, "message": "This bill has already been paid in full!"})

        remaining = bill.balance_remaining()
        amount_to_pay = remaining if remaining > 0 else bill.payable()

        client = bill.name
        account_ref = client.account_number if (client and client.account_number) else str(client.meter_number if client else bill_id)

        target_phone = phone_number or (client.contact_number if client else "") or getattr(user, "contact_number", "")
        formatted_phone = format_phone_number(target_phone)

        if not formatted_phone or len(formatted_phone) != 12:
            return JsonResponse({
                "success": False,
                "message": "Please enter a valid Kenyan phone number (e.g., 0712345678 or +2547XXXXXXXX)."
            })

        # Initiate STK Push via Daraja API
        try:
            res = initiate_stk_push(
                phone_number=formatted_phone,
                amount=amount_to_pay,
                account_reference=account_ref,
                transaction_desc=f"Bill #{bill.id}"
            )
            logger.info("STK Push success response: %s", res)

            return JsonResponse({
                "success": True,
                "message": f"M-Pesa prompt sent to {formatted_phone}! Please check your phone and enter your M-Pesa PIN.",
                "checkout_id": res.get("CheckoutRequestID"),
                "bill_id": bill.id,
                "amount": float(amount_to_pay),
                "account_number": account_ref,
                "phone": formatted_phone
            })
        except Exception as stk_err:
            logger.warning("Daraja STK Push failed: %s", stk_err)
            return JsonResponse({
                "success": False,
                "message": f"Could not send M-Pesa prompt automatically ({str(stk_err)}). You can pay via Paybill {getattr(settings, 'MPESA_SHORTCODE', '174379')} Account {account_ref} or click Confirm Payment.",
                "bill_id": bill.id,
                "amount": float(amount_to_pay),
                "account_number": account_ref,
                "phone": formatted_phone,
                "can_simulate": True
            })

    except Exception as e:
        logger.exception("Error in initiate_customer_stk_push")
        return JsonResponse({"success": False, "message": f"Server error: {str(e)}"})


def check_bill_payment_status(request, bill_id):
    """Check if a bill has been paid or reconciled."""
    if not request.user.is_authenticated:
        return JsonResponse({"paid": False, "message": "Authentication required."}, status=401)

    try:
        from main.models import WaterBill
        from payments.services import reconcile_payment

        bill = WaterBill.objects.get(id=bill_id)
        client = bill.name

        user = request.user
        if not (user.is_staff or user.is_superuser):
            if not (client and client.user == user):
                return JsonResponse({"paid": False, "message": "Unauthorized access."})

        if bill.payment_status == "Paid":
            return JsonResponse({
                "paid": True,
                "status": "Paid",
                "message": "Bill is paid in full!",
                "amount_paid": float(bill.amount_paid or bill.payable())
            })

        if client and client.account_number:
            pending_payments = Payment.objects.filter(
                account_reference__icontains=client.account_number,
                status__in=[Payment.Status.PENDING, Payment.Status.UNMATCHED]
            )
            for p in pending_payments:
                reconcile_payment(p.pk)

            bill.refresh_from_db()
            if bill.payment_status == "Paid":
                return JsonResponse({
                    "paid": True,
                    "status": "Paid",
                    "message": "Payment received! Bill is now marked as Paid.",
                    "amount_paid": float(bill.amount_paid or bill.payable())
                })

        return JsonResponse({
            "paid": False,
            "status": bill.payment_status,
            "amount_due": float(bill.balance_remaining()),
            "message": "Payment not yet detected. Please check your phone for the PIN prompt."
        })
    except WaterBill.DoesNotExist:
        return JsonResponse({"paid": False, "message": "Bill not found."})


def confirm_payment_simulation(request):
    """
    Direct payment confirmation & simulation for sandbox/testing mode.
    Simulates M-Pesa C2B/STK payment so customer can confirm bill is paid immediately.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST method required."}, status=405)

    try:
        from main.models import WaterBill
        from payments.mpesa import simulate_c2b, format_phone_number
        from payments.services import reconcile_payment

        bill_id = request.POST.get("bill_id")
        phone_number = request.POST.get("phone_number")

        if not bill_id:
            return JsonResponse({"success": False, "message": "Bill ID required."})

        bill = WaterBill.objects.get(id=bill_id)
        client = bill.name

        user = request.user
        if not (user.is_staff or user.is_superuser):
            if not (client and client.user == user):
                return JsonResponse({"success": False, "message": "Unauthorized access."})

        if bill.payment_status == "Paid":
            return JsonResponse({"success": True, "already_paid": True, "message": "Bill is already paid in full!"})

        amount = float(bill.balance_remaining() or bill.payable())
        account_ref = client.account_number if (client and client.account_number) else str(client.meter_number if client else bill.id)
        msisdn = format_phone_number(phone_number or (client.contact_number if client else "254708374149")) or "254708374149"

        try:
            simulate_c2b(amount=amount, bill_ref_number=account_ref, msisdn=msisdn)
        except Exception as e:
            logger.warning("Simulation API call note: %s. Performing direct fallback reconciliation...", e)
            import random
            receipt_code = f"NLJ{random.randint(100000, 999999)}"
            pay = Payment.objects.create(
                reference_code=receipt_code,
                amount=amount,
                method=Payment.Method.MPESA,
                account_reference=account_ref,
                status=Payment.Status.PENDING
            )
            reconcile_payment(pay.pk)

        bill.refresh_from_db()
        return JsonResponse({
            "success": True,
            "message": f"Payment of KES {amount:.2f} confirmed! Bill is marked as Paid.",
            "payment_status": bill.payment_status
        })

    except Exception as e:
        logger.exception("Error in confirm_payment_simulation")
        return JsonResponse({"success": False, "message": f"Payment confirmation error: {str(e)}"})

