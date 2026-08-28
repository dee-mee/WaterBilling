"""
Management command: generate synthetic data for load testing.

Usage:
    python3 manage.py generate_test_data --clients 5000
    python3 manage.py generate_test_data --clients 5000 --clear   # wipe first

Place this file at: main/management/commands/generate_test_data.py
(create main/management/__init__.py and main/management/commands/__init__.py
as empty files if they don't already exist)

Requires Faker: pip install faker --break-system-packages
"""
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import Client, WaterBill, Metric
from payments.models import Payment

try:
    from faker import Faker
except ImportError:
    Faker = None


class Command(BaseCommand):
    help = "Generate synthetic clients, bills, and payments for load testing."

    def add_arguments(self, parser):
        parser.add_argument("--clients", type=int, default=5000)
        parser.add_argument("--bills-per-client", type=int, default=3)
        parser.add_argument("--payment-rate", type=float, default=0.6,
                             help="Fraction of unpaid bills that get a matching Payment (0.0-1.0)")
        parser.add_argument("--clear", action="store_true",
                             help="Delete existing synthetic data first (account_number starting TEST-)")
        parser.add_argument("--batch-size", type=int, default=500)

    def handle(self, *args, **options):
        if Faker is None:
            self.stderr.write(self.style.ERROR(
                "Faker is not installed. Run: pip install faker --break-system-packages"
            ))
            return

        fake = Faker()
        n_clients = options["clients"]
        n_bills = options["bills_per_client"]
        payment_rate = options["payment_rate"]
        batch_size = options["batch_size"]

        if options["clear"]:
            self.stdout.write("Deleting existing synthetic data (account_number starting TEST-)...")
            deleted, _ = Client.objects.filter(account_number__startswith="TEST-").delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} synthetic records (cascade)."))

        # Ensure a Metric exists so compute_bill() has a real rate to use later
        metric, _ = Metric.objects.get_or_create(pk=1, defaults={"consump_amount": 200.0, "penalty_amount": 100.0})
        rate = Decimal(str(metric.consump_amount or 200.0))

        self.stdout.write(f"Generating {n_clients} clients, ~{n_bills} bills each...")

        created_clients = 0
        clients_batch = []
        base_meter = 900000000  # stays clear of any real meter numbers

        for i in range(n_clients):
            clients_batch.append(Client(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                meter_number=base_meter + i,
                account_number=f"TEST-{100000 + i}",
                contact_number=f"+2547{10000000 + i:08d}",  # deterministic -> guaranteed unique
                address=fake.address().replace("\n", ", "),
                latitude=Decimal(str(round(random.uniform(-1.5, -1.1), 6))),
                longitude=Decimal(str(round(random.uniform(36.6, 37.0), 6))),
                status=random.choice(["Connected", "Connected", "Connected", "Disconnected", "Pending"]),
            ))

            if len(clients_batch) >= batch_size:
                Client.objects.bulk_create(clients_batch, ignore_conflicts=True)
                created_clients += len(clients_batch)
                self.stdout.write(f"  ...{created_clients} clients created")
                clients_batch = []

        if clients_batch:
            Client.objects.bulk_create(clients_batch, ignore_conflicts=True)
            created_clients += len(clients_batch)

        self.stdout.write(self.style.SUCCESS(f"Created {created_clients} clients."))

        # Bills
        test_clients = list(Client.objects.filter(account_number__startswith="TEST-"))
        self.stdout.write(f"Generating bills for {len(test_clients)} clients...")

        bills_batch = []
        created_bills = 0
        today = timezone.now().date()

        for client in test_clients:
            for m in range(n_bills):
                consumption = random.randint(5, 60)
                total = Decimal(consumption) * rate
                status = random.choice(["Pending", "Pending", "Paid", "Partial"])
                amount_paid = total if status == "Paid" else (total / 2 if status == "Partial" else Decimal("0.00"))
                bills_batch.append(WaterBill(
                    name=client,
                    previous_reading=0,
                    present_reading=consumption,
                    meter_consumption=consumption,
                    payment_status=status,
                    approval_status="Approved",
                    billing_date=today,
                    duedate=today,
                    penaltydate=today,
                    amount_paid=amount_paid,
                ))
            if len(bills_batch) >= batch_size:
                WaterBill.objects.bulk_create(bills_batch, ignore_conflicts=True)
                created_bills += len(bills_batch)
                self.stdout.write(f"  ...{created_bills} bills created")
                bills_batch = []

        if bills_batch:
            WaterBill.objects.bulk_create(bills_batch, ignore_conflicts=True)
            created_bills += len(bills_batch)

        self.stdout.write(self.style.SUCCESS(f"Created {created_bills} bills."))

        # Payments — unreconciled, matched to a subset of unpaid/partial bills' clients
        unpaid_bills = list(WaterBill.objects.filter(
            name__account_number__startswith="TEST-",
            payment_status__in=list(WaterBill.UNPAID_STATUSES),
        ))
        sample_size = int(len(unpaid_bills) * payment_rate)
        sampled = random.sample(unpaid_bills, min(sample_size, len(unpaid_bills)))

        payments_batch = []
        created_payments = 0
        for idx, bill in enumerate(sampled):
            payments_batch.append(Payment(
                account_reference=bill.name.account_number,
                reference_code=f"TESTTX{idx:08d}",
                amount=bill.compute_bill() or Decimal("100.00"),
                method="mpesa",
                status="pending",
                raw_payload={"synthetic": True},
            ))
            if len(payments_batch) >= batch_size:
                Payment.objects.bulk_create(payments_batch, ignore_conflicts=True)
                created_payments += len(payments_batch)
                payments_batch = []

        if payments_batch:
            Payment.objects.bulk_create(payments_batch, ignore_conflicts=True)
            created_payments += len(payments_batch)

        self.stdout.write(self.style.SUCCESS(
            f"Done. {created_clients} clients, {created_bills} bills, {created_payments} unreconciled payments."
        ))
