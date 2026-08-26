from decimal import Decimal

from django.db import models

from main.models import Client, WaterBill


class Payment(models.Model):
    class Method(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        BANK = "bank", "Bank"
        STRIPE = "stripe", "Stripe"
        CASH = "cash", "Cash"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        MATCHED = "matched", "Matched"
        UNMATCHED = "unmatched", "Unmatched"
        FAILED = "failed", "Failed"

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.MPESA)
    reference_code = models.CharField(
        max_length=64,
        unique=True,
        help_text="M-Pesa TransID or bank/stripe reference (idempotency key).",
    )
    account_reference = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text="Raw BillRefNumber / account number typed by the payer.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"], name="payments_pa_status_created_idx"),
            models.Index(fields=["client", "created_at"], name="payments_pa_client_created_idx"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference_code} ({self.get_status_display()})"


class PaymentAllocation(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="allocations")
    water_bill = models.ForeignKey(
        WaterBill,
        on_delete=models.CASCADE,
        related_name="payment_allocations",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_due_at_match = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Bill payable() snapshot when this allocation was applied.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.payment.reference_code} -> bill {self.water_bill_id}: {self.amount}"
