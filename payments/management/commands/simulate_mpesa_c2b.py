from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from payments.mpesa import simulate_c2b


class Command(BaseCommand):
    help = "Simulate a sandbox C2B Paybill payment. Use test shortcode 174379 and test phone 254708374149."

    def add_arguments(self, parser):
        parser.add_argument("account_number")
        parser.add_argument("amount")
        parser.add_argument("--msisdn", default="254708374149", help="Sandbox test phone number (default: 254708374149)")

    def handle(self, *args, **options):
        if (settings.MPESA_ENV or "sandbox").lower() == "production":
            raise CommandError("Refusing to simulate C2B against production.")
        data = simulate_c2b(options["amount"], options["account_number"], options["msisdn"])
        self.stdout.write(self.style.SUCCESS(str(data)))
