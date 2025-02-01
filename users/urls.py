from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views
from users.views import *

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('django.contrib.auth.urls')),
    path('api/get_train_data/<str:train_number>/', views.get_train_data, name='get_train_data'),
]

# urls.py
from django.urls import path, include
