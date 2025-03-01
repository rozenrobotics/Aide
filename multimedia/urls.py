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

    path('get_all_orders', views.get_all_orders),
    path('end_order/<int:seat>', views.end_order),
    path('take_order_in_robot/<int:order_id>', views.take_order_in_robot, name="take_order_in_robot"),
    path('stuart', views.stuart),

    path('get_data', views.get_data, name='get_data'),


]
