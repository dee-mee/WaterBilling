from django.urls import path

from payments import staff_views, views

urlpatterns = [
    path("mpesa/validation/", views.mpesa_validation, name="mpesa_validation"),
    path("mpesa/confirmation/", views.mpesa_confirmation, name="mpesa_confirmation"),
    path(
        "mpesa/<str:callback_secret>/validation/",
        views.mpesa_validation,
        name="mpesa_validation_secret",
    ),
    path(
        "mpesa/<str:callback_secret>/confirmation/",
        views.mpesa_confirmation,
        name="mpesa_confirmation_secret",
    ),
    path("mpesa/stkpush/callback/", views.stk_push_callback, name="stk_push_callback"),
    path(
        "mpesa/stkpush/<str:callback_secret>/callback/",
        views.stk_push_callback,
        name="stk_push_callback_secret",
    ),
    path("stkpush/initiate/", views.initiate_customer_stk_push, name="initiate_customer_stk_push"),
    path("check-status/<int:bill_id>/", views.check_bill_payment_status, name="check_bill_payment_status"),
    path("confirm-simulation/", views.confirm_payment_simulation, name="confirm_payment_simulation"),
    path("unmatched/", staff_views.unmatched_payments, name="unmatched_payments"),
    path(
        "unmatched/<int:pk>/assign/",
        staff_views.assign_unmatched_payment,
        name="assign_unmatched_payment",
    ),
    path("unmatched/<int:pk>/retry/", staff_views.retry_payment, name="retry_payment"),
]
