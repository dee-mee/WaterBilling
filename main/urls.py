from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile/<str:pk>', views.profile, name='profile'),

    path('clients', views.clients, name="clients"),
    path('client/update/<str:pk>', views.client_update, name="clientupdate"),
    path('client/delete/<str:pk>', views.client_delete, name="clientdelete"),

    path('export-clients-csv/', views.export_clients_csv, name='export_clients_csv'),

    path('bills/ongoing', views.ongoing_bills, name="ongoingbills"),
    path('bills/history', views.history_bills, name="billshistory"),
    path('bill/update/<str:pk>', views.update_bills, name="billupdate"),
    path('bill/delete/<str:pk>', views.delete_bills, name="billdelete"),
    path('bill/invoice/<str:pk>', views.download_invoice, name="download_invoice"),

    path('users', views.users, name="users"),
    path('user/update/<str:pk>', views.update_user, name="updateuser"),
    path('user/delete/<str:pk>', views.delete_user, name="deleteuser"),
    path('user/add/', views.add_user, name='adduser'),

    path('metrics', views.metrics, name="metrics"),
    path('metrics/update/<str:pk>', views.metrics_update, name="metricsupdate"),
    path('customer/add/', views.add_customer, name="add_customer"),
    path('customer/edit/<str:pk>', views.edit_customer, name="edit_customer"),
    path('bulk-upload/', views.bulk_upload_view, name='bulk_upload'),
    path('send-reminders/', views.send_reminders_view, name='send_reminders'),
    path('approve-bills/', views.approve_bills_view, name='approve_bills'),
    path('bill-approve/<int:pk>', views.bill_approve, name='bill_approve'),
    path('bill-reject/<int:pk>', views.bill_reject, name='bill_reject'),
    path('usage-analytics/', views.usage_analytics_view, name='usage_analytics'),
    path('create-checkout-session/<int:pk>', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/<int:pk>', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('my-meter/', views.user_dashboard, name='user_dashboard')

    
]
