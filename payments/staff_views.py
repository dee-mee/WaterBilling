from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from main.decorators import staff_required
from main.models import Client
from payments.models import Payment
from payments.services import reconcile_payment


@staff_required
def unmatched_payments(request):
    payments = Payment.objects.filter(status=Payment.Status.UNMATCHED).select_related("client")
    context = {
        "title": "Unmatched Payments",
        "payments": payments,
        "clients": Client.objects.order_by("account_number"),
    }
    return render(request, "payments/unmatched.html", context)


@staff_required
@require_POST
def assign_unmatched_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    client_id = request.POST.get("client_id")
    client = get_object_or_404(Client, pk=client_id)
    payment.client = client
    if not payment.account_reference:
        payment.account_reference = client.account_number
    payment.status = Payment.Status.PENDING
    payment.save(update_fields=["client", "account_reference", "status"])
    reconcile_payment(payment.pk)
    return redirect(reverse("unmatched_payments"))


@staff_required
@require_POST
def retry_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if payment.status != Payment.Status.MATCHED:
        payment.status = Payment.Status.PENDING
        payment.save(update_fields=["status"])
        reconcile_payment(payment.pk)
    return redirect(reverse("unmatched_payments"))
