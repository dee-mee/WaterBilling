from django.db import migrations, models


def backfill_account_numbers(apps, schema_editor):
    """Backfill account numbers for existing clients."""
    Client = apps.get_model("main", "Client")
    used = set()
    next_seq = 1000000001
    clients = list(Client.objects.all().order_by("id"))
    for client in clients:
        assigned = None
        if client.meter_number is not None:
            candidate = str(client.meter_number).strip()
            if candidate and candidate not in used:
                assigned = candidate
        if assigned is None:
            while str(next_seq) in used:
                next_seq += 1
            assigned = str(next_seq)
            next_seq += 1
        client.account_number = assigned
        used.add(assigned)
    if clients:
        Client.objects.bulk_update(clients, ["account_number"], batch_size=500)


def noop_reverse(apps, schema_editor):
    """No-op for reverse migration."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_alter_metric_consump_amount"),
    ]

    operations = [
        # Add account_number field (nullable initially for backfill)
        migrations.AddField(
            model_name="client",
            name="account_number",
            field=models.CharField(
                db_index=True,
                help_text="M-Pesa Paybill account reference (BillRefNumber).",
                max_length=20,
                null=True,
            ),
        ),
        # Add credit_balance field
        migrations.AddField(
            model_name="client",
            name="credit_balance",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        # Add amount_paid field
        migrations.AddField(
            model_name="waterbill",
            name="amount_paid",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        # Update meter_number field
        migrations.AlterField(
            model_name="client",
            name="meter_number",
            field=models.BigIntegerField(db_index=True, null=True),
        ),
        # Update payment_status field
        migrations.AlterField(
            model_name="waterbill",
            name="payment_status",
            field=models.TextField(
                choices=[("Paid", "Paid"), ("Pending", "Pending"), ("Partial", "Partial")],
                null=True,
            ),
        ),
        # Backfill account numbers for existing records
        migrations.RunPython(backfill_account_numbers, noop_reverse),
        # Make account_number unique and not nullable after backfill
        migrations.AlterField(
            model_name="client",
            name="account_number",
            field=models.CharField(
                db_index=True,
                help_text="M-Pesa Paybill account reference (BillRefNumber).",
                max_length=20,
                unique=True,
            ),
        ),
    ]
