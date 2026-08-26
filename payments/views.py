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
