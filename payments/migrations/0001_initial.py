import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("main", "0012_client_payment_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("mpesa", "M-Pesa"),
                            ("bank", "Bank"),
                            ("stripe", "Stripe"),
                            ("cash", "Cash"),
                        ],
                        default="mpesa",
                        max_length=20,
                    ),
                ),
                (
                    "reference_code",
                    models.CharField(
                        help_text="M-Pesa TransID or bank/stripe reference (idempotency key).",
                        max_length=64,
                        unique=True,
                    ),
                ),
                (
                    "account_reference",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="Raw BillRefNumber / account number typed by the payer.",
                        max_length=64,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("matched", "Matched"),
                            ("unmatched", "Unmatched"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payments",
                        to="main.client",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PaymentAllocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "amount_due_at_match",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Bill payable() snapshot when this allocation was applied.",
                        max_digits=12,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="allocations",
                        to="payments.payment",
                    ),
                ),
                (
                    "water_bill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_allocations",
                        to="main.waterbill",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["status", "created_at"], name="payments_pa_status_created_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["client", "created_at"], name="payments_pa_client_created_idx"),
        ),
    ]
