from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('purchase-ticket/', views.purchase_ticket, name='purchase_ticket'),
    path('check_in', views.check_in, name='check_in'),

    
    path('payment-options/<int:order_id>/', views.payment_options, name='payment_options'),
    path('pay-ticket/yoomoney/<int:order_id>/', views.pay_ticket_yoomoney, name='pay_ticket_yoomoney'),
    path('pay-ticket/status/<int:order_id>/', views.pay_ticket_status, name='pay_ticket_status'),
    path('pay-ticket/test/<int:order_id>/', views.pay_ticket_test, name='pay_ticket_test'),
]
