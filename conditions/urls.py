from django.contrib import admin
from django.urls import path, include
from conditions import views

urlpatterns = [
    path('start_talking_ajax/', views.start_talking_ajax, name='start_talking_ajax'),
    path('stop_talking_ajax/', views.stop_talking_ajax, name='stop_talking_ajax'),

    path('get_speaking_value', views.get_speaking_value),
    path('get_place_value', views.get_place_value),
    path('get_deviant_value', views.get_deviant_value),
    path('get_lidar_value', views.get_lidar_value, name='get_lidar_value'),

    path('set_lidar_value/<int:is_lidar>',views.set_lidar_value)

]
