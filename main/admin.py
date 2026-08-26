from django.contrib import admin
from .models import *


class WaterBillAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing_date', 'previous_reading', 'present_reading', 'meter_consumption', 'payment_status', 'approval_status', 'amount_paid', 'duedate', 'penaltydate')
    fields = ('name', 'billing_date', 'previous_reading', 'present_reading', 'meter_consumption', 'payment_status', 'approval_status', 'amount_paid', 'duedate', 'penaltydate')
    list_per_page = 50


class ClientAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'meter_number', 'first_name', 'last_name', 'contact_number', 'status', 'credit_balance')
    search_fields = ('account_number', 'meter_number', 'first_name', 'last_name', 'contact_number')
    list_per_page = 50


admin.site.register(WaterBill, WaterBillAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Metric)