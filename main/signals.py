from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Metric

@receiver(post_migrate)
def create_default_metric(sender, **kwargs):
    """
    Create a default Metric object if none exists, or update if it has incorrect default.
    This runs after migrations complete.
    """
    metric = Metric.objects.first()
    if not metric:
        Metric.objects.create(
            consump_amount=200.0,  # Default consumption amount
            penalty_amount=100.0  # Default penalty amount
        )
        print("Created default Metric object")
    elif metric.consump_amount == 1.0:
        metric.consump_amount = 200.0
        metric.save()
        print("Updated existing Metric object from 1.0 to 200.0")
