from django.core.management.base import BaseCommand

from payments.models import Payment
from payments.services import reconcile_payment


class Command(BaseCommand):
    help = "Reconcile pending M-Pesa/bank payments (cPanel cron fallback when Celery is unavailable)."

    def handle(self, *args, **options):
        pending = Payment.objects.filter(status=Payment.Status.PENDING).order_by("created_at")
        count = 0
        errors = 0
        for payment in pending:
            try:
                reconcile_payment(payment.pk)
                count += 1
            except Exception as exc:
                errors += 1
                self.stderr.write(f"Payment {payment.pk} failed: {exc}")
        self.stdout.write(self.style.SUCCESS(f"Processed {count} pending payment(s); {errors} error(s)."))
