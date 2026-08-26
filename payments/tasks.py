from celery import shared_task

from payments.services import reconcile_payment


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def reconcile_payment_task(self, payment_id):
    try:
        return reconcile_payment(payment_id).pk
    except Exception as exc:
        raise self.retry(exc=exc)
