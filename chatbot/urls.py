from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_owner, name='register_owner'),
    path('login/', views.login_owner, name='login_owner'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login_owner'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/message/', views.whatsapp, name='whatsapp' ),
    path('homes/', views.homes, name='homes'),
    path('homes/add/', views.add_homes, name='add_homes'),
    path('homes/update/', views.update_homes, name='update_homes'),
    path('homes/<int:house_id>/', views.get_house_details, name='get_house_details'),
    path('tenants/', views.tenants, name='tenants'),
    path('tenants/add/', views.add_customer, name='add_customer'),
    path('tenants/update/', views.update_Customer, name='update_customer'),
    path('tenants/<int:customer_id>/', views.get_tenant_details, name='get_tenant_details')
]
