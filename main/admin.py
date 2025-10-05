from django.contrib import admin
from .models import *


class WaterBillAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing_date', 'previous_reading', 'present_reading', 'meter_consumption', 'payment_status', 'approval_status', 'duedate', 'penaltydate')
    fields = ('name', 'billing_date', 'previous_reading', 'present_reading', 'meter_consumption', 'payment_status', 'approval_status', 'duedate', 'penaltydate')

admin.site.register(WaterBill, WaterBillAdmin)
admin.site.register(Client)
admin.site.register(Metric)