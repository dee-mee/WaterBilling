from django.db import models
from account.models import *
import datetime
import string, secrets
from django.utils import timezone


class Client(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    meter_number = models.BigIntegerField(null=True)
    first_name = models.CharField(max_length=30) 
    last_name = models.CharField(max_length=30) 
    middle_name = models.CharField(max_length=30, null=True, blank=True) 
    contact_number = models.CharField(null=True, unique=True, max_length=13)
    address = models.CharField(max_length=250)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude coordinate for map location")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude coordinate for map location")
    status = models.TextField(choices=(('Connected', 'Connected'), ('Disconnected', 'Disconnected'), ('Pending', 'Pending')))

    def save(self, *args, **kwargs):
        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
            # Assuming middle_name is not a field in the Account model
            # self.middle_name = self.user.middle_name 
        super().save(*args, **kwargs)


    def __str__(self):
        if self.middle_name:
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        else:
            return f"{self.last_name}, {self.first_name}"


class WaterBill(models.Model):
    name = models.ForeignKey(Client, on_delete=models.CASCADE)
    previous_reading = models.BigIntegerField(null=True)
    present_reading = models.BigIntegerField(null=True)
    meter_consumption = models.BigIntegerField(null=True)
    payment_status = models.TextField(choices=(('Paid','Paid'),('Pending', 'Pending')), null=True)
    approval_status = models.TextField(choices=(('Pending Approval', 'Pending Approval'), ('Approved', 'Approved'), ('Rejected', 'Rejected')), default='Pending Approval')
    billing_date = models.DateField(null=True)
    duedate = models.DateField(null=True)
    penaltydate = models.DateField(null=True)

    
    def compute_bill(self):
        try:
            metric = Metric.objects.first()
            if not metric:
                # If no metric exists, create one with default values
                metric = Metric.objects.create(
                    consump_amount=1.0,
                    penalty_amount=100.0
                )
            consump_amount = metric.consump_amount
            return self.meter_consumption * consump_amount if self.meter_consumption else 0
        except Exception as e:
            # Fallback in case of any error
            print(f"Error computing bill: {str(e)}")
            return self.meter_consumption * 1.0 if self.meter_consumption else 0

    def penalty(self):
        today = timezone.localdate()
        if self.penaltydate and today >= self.penaltydate:
            try:
                metric = Metric.objects.first()
                if not metric:
                    # If no metric exists, create one with default values
                    metric = Metric.objects.create(
                        consump_amount=1.0,
                        penalty_amount=100.0
                    )
                return metric.penalty_amount
            except Exception as e:
                # Fallback in case of any error
                print(f"Error calculating penalty: {str(e)}")
                return 100.0  # Default penalty amount
        return 0

    
    def payable(self):
        today = timezone.localdate()
        if self.penaltydate and today >= self.penaltydate:
            return self.compute_bill() + self.penalty()
        return self.compute_bill()


    def __str__(self):
        return f'{self.name}'


class Metric(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    consump_amount = models.FloatField(default=1, null=True)
    penalty_amount = models.FloatField(default=1, null=True)


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    admin_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} by {self.user.email}"


class UserNotification(models.Model):
    TYPE_CHOICES = [
        ('rejection', 'Account Rejection'),
        ('approval', 'Account Approval'),
        ('general', 'General Notification'),
        ('bill', 'Bill Notification'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()