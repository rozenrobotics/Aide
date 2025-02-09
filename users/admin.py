from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

from users.models import TrainTicket, TrainInfo


@admin.register(TrainTicket)
class TrainTicketAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'face_data', 'seat_number', 'created_at')
    search_fields = ('user_name', 'seat_number')


@admin.register(TrainInfo) 
class TrainInfoAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'departure_station', 'arrival_station', 
                   'departure_time', 'arrival_time')
    search_fields = ('train_number', 'departure_station', 'arrival_station')
