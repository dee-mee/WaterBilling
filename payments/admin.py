from django.contrib import admin

from payments.models import Payment, PaymentAllocation


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 0
    readonly_fields = ("water_bill", "amount", "amount_due_at_match", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "account_reference",
        "client",
        "amount",
        "method",
        "status",
        "created_at",
    )
    list_filter = ("status", "method")
    search_fields = ("reference_code", "account_reference")
    list_per_page = 50
    inlines = [PaymentAllocationInline]
    readonly_fields = ("created_at", "raw_payload")


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ("payment", "water_bill", "amount", "amount_due_at_match", "created_at")
    list_per_page = 50
