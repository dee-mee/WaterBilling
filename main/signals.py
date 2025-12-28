from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Metric

@receiver(post_migrate)
def create_default_metric(sender, **kwargs):
    """
    Create a default Metric object if none exists.
    This runs after migrations complete.
    """
    if not Metric.objects.exists():
        Metric.objects.create(
            consump_amount=1.0,  # Default consumption amount
            penalty_amount=100.0  # Default penalty amount
        )
        print("Created default Metric object")
