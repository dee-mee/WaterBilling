from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from payments.mpesa import register_c2b_urls


class Command(BaseCommand):
    help = "Register C2B validation/confirmation URLs with Safaricom Daraja."

    def handle(self, *args, **options):
        if not settings.MPESA_CONSUMER_KEY or not settings.MPESA_SHORTCODE:
            raise CommandError("MPESA_CONSUMER_KEY and MPESA_SHORTCODE must be set.")
        if not settings.MPESA_CALLBACK_BASE_URL:
            raise CommandError("MPESA_CALLBACK_BASE_URL must be set (public HTTPS origin).")
        data = register_c2b_urls()
        self.stdout.write(self.style.SUCCESS(str(data)))
