from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from account.models import *
import datetime
import string, secrets
from django.utils import timezone


def money(value):
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Client(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    meter_number = models.BigIntegerField(null=True, db_index=True)
    account_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="M-Pesa Paybill account reference (BillRefNumber).",
    )
    first_name = models.CharField(max_length=30) 
    last_name = models.CharField(max_length=30) 
    middle_name = models.CharField(max_length=30, null=True, blank=True) 
    contact_number = models.CharField(null=True, unique=True, max_length=13)
    address = models.CharField(max_length=250)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude coordinate for map location")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude coordinate for map location")
    status = models.TextField(choices=(('Connected', 'Connected'), ('Disconnected', 'Disconnected'), ('Pending', 'Pending')))
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def save(self, *args, **kwargs):
        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
            # Assuming middle_name is not a field in the Account model
            # self.middle_name = self.user.middle_name
        if not self.account_number:
            self.account_number = Client.allocate_account_number(self.meter_number)
        super().save(*args, **kwargs)

    @classmethod
    def allocate_account_number(cls, meter_number=None):
        """Prefer unused meter number; otherwise the next sequential 10-digit id."""
        used = set(cls.objects.exclude(account_number="").values_list("account_number", flat=True))
        if meter_number is not None:
            candidate = str(meter_number).strip()
            if candidate and candidate not in used:
                return candidate
        next_seq = 1000000001
        numeric = [int(a) for a in used if str(a).isdigit()]
        if numeric:
            next_seq = max(max(numeric) + 1, next_seq)
        while str(next_seq) in used:
            next_seq += 1
        return str(next_seq)


    def __str__(self):
        if self.middle_name:
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        else:
            return f"{self.last_name}, {self.first_name}"


class WaterBill(models.Model):
    UNPAID_STATUSES = ("Pending", "Partial")

    name = models.ForeignKey(Client, on_delete=models.CASCADE)
    previous_reading = models.BigIntegerField(null=True)
    present_reading = models.BigIntegerField(null=True)
    meter_consumption = models.BigIntegerField(null=True)
    payment_status = models.TextField(
        choices=(("Paid", "Paid"), ("Pending", "Pending"), ("Partial", "Partial")),
        null=True,
    )
    approval_status = models.TextField(choices=(('Pending Approval', 'Pending Approval'), ('Approved', 'Approved'), ('Rejected', 'Rejected')), default='Pending Approval')
    billing_date = models.DateField(null=True)
    duedate = models.DateField(null=True)
    penaltydate = models.DateField(null=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    
    def compute_bill(self):
        try:
            metric = Metric.objects.first()
            if not metric:
                # If no metric exists, create one with default values
                metric = Metric.objects.create(
                    consump_amount=200.0,
                    penalty_amount=100.0
                )
            consump_amount = metric.consump_amount
            # Ensure rate is at least 200 (treat 1 as legacy invalid value)
            if not consump_amount or consump_amount <= 1:
                consump_amount = 200.0
            return self.meter_consumption * consump_amount if self.meter_consumption else 0
        except Exception as e:
            # Fallback in case of any error
            print(f"Error computing bill: {str(e)}")
            return self.meter_consumption * 200.0 if self.meter_consumption else 0

    def penalty(self):
        today = timezone.localdate()
        if self.penaltydate and today >= self.penaltydate:
            try:
                # Calculate number of days from penalty date to today
                days_passed = (today - self.penaltydate).days
                
                # Return only the daily increment: 5 KSH per day
                daily_penalty = days_passed * 5.0
                
                return daily_penalty
            except Exception as e:
                # Fallback in case of any error
                print(f"Error calculating penalty: {str(e)}")
                # Calculate days even in fallback
                try:
                    days_passed = (today - self.penaltydate).days
                    return days_passed * 5.0  # Only daily increment
                except:
                    return 0  # Ultimate fallback
        return 0

    
    def payable(self):
        today = timezone.localdate()
        if self.penaltydate and today >= self.penaltydate:
            return self.compute_bill() + self.penalty()
        return self.compute_bill()

    def balance_remaining(self):
        if self.payment_status == "Paid":
            return Decimal("0.00")
        due = money(self.payable())
        paid = money(self.amount_paid)
        remaining = due - paid
        return remaining if remaining > 0 else Decimal("0.00")

    def save(self, *args, **kwargs):
        if self.meter_consumption is None and self.present_reading is not None and self.previous_reading is not None:
            self.meter_consumption = self.present_reading - self.previous_reading
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.name}'


class Metric(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    consump_amount = models.FloatField(default=200, null=True)
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