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


def check_column_exists(table_name, column_name):
    """Check if a column already exists in a table."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, [table_name, column_name])
        return cursor.fetchone() is not None


def check_column_is_unique(table_name, column_name):
    """Check if a column already has a unique constraint."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints 
            WHERE table_name = %s AND constraint_type = 'UNIQUE'
        """, [table_name])
        constraints = cursor.fetchall()
        for constraint in constraints:
            cursor.execute("""
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE constraint_name = %s AND table_name = %s
            """, [constraint[0], table_name])
            columns = cursor.fetchall()
            if any(col[0] == column_name for col in columns):
                return True
        return False


def add_account_number_field(apps, schema_editor):
    """Add account_number field only if it doesn't exist."""
    if not check_column_exists('main_client', 'account_number'):
        # Add the field without unique constraint first
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE main_client 
                ADD COLUMN account_number VARCHAR(20)
            """)
            cursor.execute("""
                CREATE INDEX main_client_account_number_idx 
                ON main_client(account_number)
            """)
    else:
        # Field exists, just ensure it's not unique yet
        if check_column_is_unique('main_client', 'account_number'):
            with connection.cursor() as cursor:
                cursor.execute("""
                    ALTER TABLE main_client 
                    DROP CONSTRAINT main_client_account_number_key
                """)


def add_credit_balance_field(apps, schema_editor):
    """Add credit_balance field only if it doesn't exist."""
    if not check_column_exists('main_client', 'credit_balance'):
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE main_client 
                ADD COLUMN credit_balance DECIMAL(12,2) DEFAULT 0
            """)


def add_amount_paid_field(apps, schema_editor):
    """Add amount_paid field only if it doesn't exist."""
    if not check_column_exists('main_waterbill', 'amount_paid'):
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE main_waterbill 
                ADD COLUMN amount_paid DECIMAL(12,2) DEFAULT 0
            """)


def make_account_number_unique(apps, schema_editor):
    """Make account_number unique after backfill."""
    if check_column_exists('main_client', 'account_number'):
        if not check_column_is_unique('main_client', 'account_number'):
            with connection.cursor() as cursor:
                cursor.execute("""
                    ALTER TABLE main_client 
                    ADD CONSTRAINT main_client_account_number_key 
                    UNIQUE (account_number)
                """)


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_alter_metric_consump_amount"),
    ]

    operations = [
        # Use custom SQL operations for idempotency
        migrations.RunPython(add_account_number_field, migrations.RunPython.noop),
        migrations.RunPython(add_credit_balance_field, migrations.RunPython.noop),
        migrations.RunPython(add_amount_paid_field, migrations.RunPython.noop),
        
        # Standard operations for meter_number and payment_status (should be safe)
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
        
        # Backfill account numbers
        migrations.RunPython(backfill_account_numbers, noop_reverse),
        
        # Make account_number unique
        migrations.RunPython(make_account_number_unique, migrations.RunPython.noop),
        
        # Update Django's state to match the final schema
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="client",
                    name="account_number",
                    field=models.CharField(
                        db_index=True,
                        help_text="M-Pesa Paybill account reference (BillRefNumber).",
                        max_length=20,
                        unique=True,
                    ),
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
            ],
            database_operations=[],
        ),
    ]
