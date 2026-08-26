from django.db import migrations, models, connection


def backfill_account_numbers(apps, schema_editor):
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
    pass


def drop_existing_index(apps, schema_editor):
    """Drop existing account_number index if it exists (for idempotency)."""
    try:
        with connection.cursor() as cursor:
            # Try to drop any existing account_number indexes
            cursor.execute("DROP INDEX IF EXISTS main_client_account_number_48e25570_like")
            cursor.execute("DROP INDEX IF EXISTS main_client_account_number_key")
            cursor.execute("DROP INDEX IF EXISTS main_client_account_number_idx")
    except Exception:
        # If any drop fails, continue - the index might not exist
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_alter_metric_consump_amount"),
    ]

    operations = [
        # Drop any existing indexes first (for redeploy scenarios)
        migrations.RunPython(drop_existing_index, migrations.RunPython.noop),
        
        migrations.AddField(
            model_name="client",
            name="account_number",
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="credit_balance",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="waterbill",
            name="amount_paid",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name="client",
            name="meter_number",
            field=models.BigIntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="waterbill",
            name="payment_status",
            field=models.TextField(
                choices=[("Paid", "Paid"), ("Pending", "Pending"), ("Partial", "Partial")],
                null=True,
            ),
        ),
        migrations.RunPython(backfill_account_numbers, noop_reverse),
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
