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
    path("unmatched/", staff_views.unmatched_payments, name="unmatched_payments"),
    path(
        "unmatched/<int:pk>/assign/",
        staff_views.assign_unmatched_payment,
        name="assign_unmatched_payment",
    ),
    path("unmatched/<int:pk>/retry/", staff_views.retry_payment, name="retry_payment"),
]
