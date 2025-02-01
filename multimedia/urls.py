from django.urls import path
from multimedia import views

urlpatterns = [
    path('', views.multimedia_index, name='multimedia_index'),
    path('shop', views.product_list, name='shop'),
    path('films', views.films, name='films'),
    path('music', views.music, name='music'),

    path('create-payment/<int:product>', views.create_payment, name='create_payment'),
    path('test-payment/<int:product>', views.test_payment, name='test_payment'),
    path('check-payment-status/', views.check_payment_status, name='check_payment_status'),

    path('gpt', views.gpt, name='gpt'),
    path('process_question_ajax/', views.process_question_ajax, name='process_question_ajax'),
]
