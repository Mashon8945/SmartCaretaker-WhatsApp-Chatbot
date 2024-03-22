from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_owner, name='register_owner'),
    path('login/', views.login_owner, name='login_owner'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login_owner'), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/webhook/', views.whatsapp_webhook, name='whatsapp-webhook' ),

    path('homes/', views.homes, name='homes'),
    path('homes/add/', views.add_homes, name='add_homes'),
    path('homes/update/', views.update_homes, name='update_homes'),
    path('homes/<int:house_id>/', views.get_house_details, name='get_house_details'),
    path('unassign-house/<int:assignment_id>/', views.unassign_house, name="unassign_house"),
    path('delete-house/<int:house_id>/', views.delete_house, name="delete_house"),

    path('tenants/', views.tenants, name='tenants'),
    path('tenants/add/', views.add_customer, name='add_customer'),
    path('tenants/update/', views.update_Customer, name='update_customer'),
    path('tenants/<int:customer_id>/', views.get_tenant_details, name='get_tenant_details'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),

    path('notice/', views.notice, name='notice'),
    path('payment-success/<int:transaction_id>', views.payment_success, name='payment_success'),

    # path('edit-invoice/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('transactions/', views.transactions, name="transactions"),
    path('payment-form/<uuid:payment_uuid>/', views.payment_form, name='payment_form'),
    path('generate-payment-link/<int:invoice_id>/', views.generate_payment_link, name='generate_payment_link'),
    path('send-invoices/', views.generate_invoices, name='send_invoices'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    # path('process-payment/<int:invoice_id>/', views.process_payment, name='process_payment'),
]
