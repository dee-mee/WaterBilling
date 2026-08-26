from django.core.management.base import BaseCommand

from main.models import Client


class Command(BaseCommand):
    help = "Create synthetic Client rows to exercise account_number indexes at scale."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=5000)

    def handle(self, *args, **options):
        n = options["count"]
        existing = Client.objects.count()
        batch = []
        start = 2000000001
        for i in range(n):
            seq = start + existing + i
            batch.append(
                Client(
                    meter_number=seq,
                    account_number=str(seq),
                    first_name="Scale",
                    last_name=f"Client{seq}",
                    address="Load test",
                    status="Connected",
                    contact_number=None,
                )
            )
            if len(batch) >= 500:
                Client.objects.bulk_create(batch)
                batch = []
        if batch:
            Client.objects.bulk_create(batch)
        self.stdout.write(self.style.SUCCESS(f"Created {n} clients (bulk)."))
