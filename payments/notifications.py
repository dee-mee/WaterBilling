def notify_payment_received(payment):
    """In-app notice after a match. SMS is intentionally not sent here."""
    client = payment.client
    if not client or not client.user_id:
        return
    from main.models import UserNotification

    UserNotification.objects.create(
        user=client.user,
        notification_type="bill",
        title="Payment received",
        message=(
            f"Payment of KSH {payment.amount} (ref {payment.reference_code}) "
            f"has been applied to your account."
        ),
    )
